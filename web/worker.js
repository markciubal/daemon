// DAEMON — Pyodide Web Worker
// Loads CPython via WebAssembly, fetches simulation source from the server,
// and runs Kharg Island / CSG scenarios entirely in the browser.
//
// Message protocol
//   Main → Worker:  { type:'init' }
//                   { type:'run', which:'csg'|'kharg', id, params }
//   Worker → Main:  { type:'status', msg }
//                   { type:'log',    which, line }
//                   { type:'ready',  scenarios }
//                   { type:'done',   which, result, kmzBytes }   (Transferable)
//                   { type:'error',  which, msg }

importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js');

// Python source files to fetch from the server and write to the virtual FS.
const PYTHON_FILES = [
  'persian_gulf_simulation/__init__.py',
  'persian_gulf_simulation/__main__.py',
  'persian_gulf_simulation/config.py',
  'persian_gulf_simulation/geography.py',
  'persian_gulf_simulation/runner.py',
  'persian_gulf_simulation/generate_wargame_kml.py',
  'persian_gulf_simulation/agents/__init__.py',
  'persian_gulf_simulation/agents/base.py',
  'persian_gulf_simulation/agents/factory.py',
  'persian_gulf_simulation/simulation/__init__.py',
  'persian_gulf_simulation/simulation/engine.py',
  'persian_gulf_simulation/simulation/spatial.py',
  'persian_gulf_simulation/kml/__init__.py',
  'persian_gulf_simulation/kml/captions.py',
  'persian_gulf_simulation/kml/descriptions.py',
  'persian_gulf_simulation/kml/document.py',
  'persian_gulf_simulation/kml/narration.py',
  'persian_gulf_simulation/kml/placemarks.py',
  'persian_gulf_simulation/kml/styles.py',
  'persian_gulf_simulation/kml/tour.py',
];

// Base URL: directory containing this worker script (same as web/)
const BASE_URL = self.location.href.replace(/[^/]+$/, '');

let pyodide = null;
let currentWhich = null;  // routes stdout to the correct log panel

// ─── helpers ────────────────────────────────────────────────────────────────

function post(type, extra = {}) {
  self.postMessage({ type, ...extra });
}

// ─── init ───────────────────────────────────────────────────────────────────

async function init() {
  try {
    post('status', { msg: 'Loading Python runtime (~10 MB, cached after first load)…' });
    pyodide = await loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/',
    });

    // Redirect Python stdout/stderr to the log panel
    pyodide.setStdout({
      batched: (line) => post('log', { which: currentWhich, line }),
    });
    pyodide.setStderr({
      batched: (line) => post('log', { which: currentWhich, line: '[!] ' + line }),
    });

    post('status', { msg: 'Loading Pillow image library…' });
    await pyodide.loadPackage(['Pillow']);

    post('status', { msg: 'Fetching simulation source files…' });

    // Create package directories in the WASM virtual FS
    pyodide.runPython(`
import os
for d in [
    '/sim/persian_gulf_simulation/agents',
    '/sim/persian_gulf_simulation/simulation',
    '/sim/persian_gulf_simulation/kml',
]:
    os.makedirs(d, exist_ok=True)
`);

    // Fetch each Python source file and write it into the virtual FS
    for (const relPath of PYTHON_FILES) {
      const resp = await fetch(BASE_URL + relPath);
      if (!resp.ok) throw new Error(`Failed to fetch ${relPath}: HTTP ${resp.status}`);
      const text = await resp.text();
      pyodide.FS.writeFile('/sim/' + relPath, text, { encoding: 'utf8' });
    }

    // Add /sim to Python's module search path
    pyodide.runPython(`
import sys
if '/sim' not in sys.path:
    sys.path.insert(0, '/sim')
`);

    post('status', { msg: 'Building scenario list…' });
    const scenarios = await buildScenarios();
    post('ready', { scenarios });

  } catch (err) {
    post('error', { which: null, msg: 'Initialisation failed: ' + (err.message || String(err)) });
  }
}

// ─── build scenario list (mirrors /api/scenarios) ───────────────────────────

async function buildScenarios() {
  const resultJson = await pyodide.runPythonAsync(`
import json
from persian_gulf_simulation.runner import build_scenarios
import persian_gulf_simulation.config as cfg
from persian_gulf_simulation.generate_wargame_kml import SCENARIOS as CSG_SCENARIOS

_CSG_RANK_ORDER = [
    "realistic","one_percent_probe","depleted_drone_first","depleted_coastal",
    "one_percent_fatah2","depleted_israel_split","medium","drone_first_low",
    "hypersonic_threat","drone_first_medium","low","ballistic_barrage",
    "us_win_c2_disrupted","us_win_arsenal_attrition","usa_best","ascm_swarm",
    "us_win_ew_dominance","us_win_allied_umbrella","us_win_preemption","high",
    "shore_based_defense","strait_transit","drone_first_high","caves",
    "ballistic_surge","coordinated_strike","focused_salvo","iran_best",
]
_CSG_EXCLUDE = {
    "munitions","description","label","csg_fleet","custom_sites",
    "ballistic_targets","focus_csg","drone_focus_csg",
    "us_strike_timing","iaf_timing",
}

results = []

# ── Kharg Island scenarios ──
for rank, (label, overrides, fname, desc) in enumerate(build_scenarios(), start=1):
    sc_id = fname.replace('.kmz', '')
    params = {
        'n_irgc':                   cfg.N_SQUADS,
        'stinger_pk':               cfg.STINGER_PK,
        'stinger_hover_pk':         cfg.STINGER_HOVER_PK,
        'stinger_wez_km':           cfg.STINGER_WEZ_KM,
        'n_drone_boats':            cfg.N_DRONE_BOATS,
        'n_shahed':                 cfg.N_SHAHED,
        'n_island_shahed':          cfg.N_ISLAND_SHAHED,
        'ai_drone_fraction':        cfg.AI_DRONE_FRACTION,
        'ew_irgc_pk_mult':          cfg.EW_IRGC_PK_MULT,
        'ew_irgc_defense_mult_adj': cfg.EW_IRGC_DEFENSE_MULT_ADJ,
        'ew_manpads_pk_mult':       cfg.EW_MANPADS_PK_MULT,
        'ew_mildec_fraction':       cfg.EW_MILDEC_FRACTION,
        'ew_mildec_delay_steps':    cfg.EW_MILDEC_DELAY_STEPS,
        'ew_shahed_abort_rate':     cfg.EW_SHAHED_ABORT_RATE,
        'ew_ship_sam_pk_mult':      cfg.EW_SHIP_SAM_PK_MULT,
        'osprey_drop_steps':        cfg.OSPREY_DROP_STEPS,
        'beach_assault':            False,
        'iran_retaliation':         True,
        'pre_strike_survival_pct':  0.0,
    }
    for k, v in overrides.items():
        if isinstance(v, (int, float, bool, str)):
            params[k] = v
    results.append({'id':sc_id,'engine':'kharg','rank':rank,'label':label,'description':desc,'params':params})

# ── CSG naval scenarios ──
for rank, sc_key in enumerate(_CSG_RANK_ORDER, start=1):
    if sc_key not in CSG_SCENARIOS:
        continue
    sc = CSG_SCENARIOS[sc_key]
    params = {k:v for k,v in sc.items() if k not in _CSG_EXCLUDE and isinstance(v,(int,float,bool,str))}
    results.append({'id':sc_key,'engine':'csg','rank':rank,
                    'label':sc.get('label',sc_key),'description':sc.get('description',''),'params':params})

json.dumps(results)
`);
  return JSON.parse(resultJson);
}

// ─── run Kharg Island scenario ───────────────────────────────────────────────

async function runKharg(id, params) {
  pyodide.globals.set('_kharg_id',     id);
  pyodide.globals.set('_kharg_params', JSON.stringify(params));

  const resultJson = await pyodide.runPythonAsync(`
import json, os
from persian_gulf_simulation.runner import (
    build_scenarios, _patch_scenario, _run_scenario, _STRIP
)
import persian_gulf_simulation.config as cfg

scenario_id  = _kharg_id
user_params  = json.loads(_kharg_params)

# Find scenario entry
matched = None
for entry in build_scenarios():
    if entry[2].replace('.kmz','') == scenario_id:
        matched = entry
        break
if matched is None:
    raise ValueError(f"Kharg scenario not found: {scenario_id!r}")

label, overrides, fname, desc = matched

# Merge overrides: scenario defaults then user edits
merged = dict(overrides)
merged.update(user_params)

out_kmz = '/tmp/daemon_kharg.kmz'
if os.path.exists(out_kmz):
    os.remove(out_kmz)

pre_pct = merged.get('pre_strike_survival_pct')
if pre_pct == 0.0:
    pre_pct = None
elif merged.get('beach_assault'):
    pre_pct = 0.08

n_pre    = merged.get('n_irgc', cfg.N_SQUADS) if pre_pct else None
iran_ret = merged.get('iran_retaliation', True)
patch_args = {k: v for k, v in merged.items() if k not in _STRIP}

print(f"\\n{'='*60}")
print(f"SCENARIO: {label}")
print('='*60)

with _patch_scenario(**patch_args, beach_assault=merged.get('beach_assault', False)):
    result = _run_scenario(out_kmz, scenario_label=label,
                           pre_strike_survival_pct=pre_pct,
                           n_irgc_pre=n_pre,
                           iran_retaliation=iran_ret,
                           scenario_desc=desc)

json.dumps(result)
`);

  const result   = JSON.parse(resultJson);
  const kmzBytes = pyodide.FS.readFile('/tmp/daemon_kharg.kmz');
  return { result, kmzBytes };
}

// ─── run CSG naval scenario ──────────────────────────────────────────────────

async function runCSG(id, params) {
  pyodide.globals.set('_csg_id',     id);
  pyodide.globals.set('_csg_params', JSON.stringify(params));

  const resultJson = await pyodide.runPythonAsync(`
import json, zipfile, os
from persian_gulf_simulation.generate_wargame_kml import (
    SCENARIOS as CSG_SCENARIOS, generate_scenario
)

scenario_id = _csg_id
user_params = json.loads(_csg_params)

_CSG_EXCLUDE = {
    "munitions","description","label","csg_fleet","custom_sites",
    "ballistic_targets","focus_csg","drone_focus_csg",
    "us_strike_timing","iaf_timing",
}
_SEEDS = {
    "low":42,"medium":7,"high":13,"realistic":99,"iran_best":77,"usa_best":11,
    "drone_first_low":55,"drone_first_medium":66,"drone_first_high":88,
    "coordinated_strike":99,"focused_salvo":99,"hypersonic_threat":99,
    "ballistic_barrage":33,"ascm_swarm":44,"shore_based_defense":99,
    "strait_transit":99,"caves":99,"depleted_drone_first":42,
    "depleted_coastal":42,"depleted_israel_split":42,"us_win_preemption":42,
    "us_win_ew_dominance":42,"us_win_allied_umbrella":42,
    "us_win_c2_disrupted":42,"us_win_arsenal_attrition":42,
    "one_percent_probe":17,"one_percent_fatah2":19,"ballistic_surge":55,
}

if scenario_id not in CSG_SCENARIOS:
    raise ValueError(f"CSG scenario not found: {scenario_id!r}")

original = dict(CSG_SCENARIOS[scenario_id])
try:
    for k, v in user_params.items():
        if k not in _CSG_EXCLUDE:
            CSG_SCENARIOS[scenario_id][k] = v

    seed    = _SEEDS.get(scenario_id, 42)
    out_dir = '/tmp/csg_output'
    os.makedirs(out_dir, exist_ok=True)

    print(f"\\n{'='*60}")
    print(f"CSG SCENARIO: {scenario_id}")
    print('='*60)

    kml_content, legend_states, n_launched, n_intercepted, n_breakthrough, dur_min, costs = \\
        generate_scenario(scenario_id, seed=seed, out_dir=out_dir)

    out_kmz = '/tmp/daemon_csg.kmz'
    if os.path.exists(out_kmz):
        os.remove(out_kmz)
    with zipfile.ZipFile(out_kmz, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('doc.kml', kml_content.encode('utf-8'))
        for img_path, _, _ in legend_states:
            if os.path.exists(img_path):
                zf.write(img_path, f'images/{os.path.basename(img_path)}')

    result = {
        'n_launched':            n_launched,
        'n_intercepted':         n_intercepted,
        'n_breakthrough':        n_breakthrough,
        'intercept_rate_actual': costs.get('intercept_rate_actual', 0.0),
        'duration_min':          dur_min,
        'iran_cost_usd':         costs.get('iran_cost', 0.0),
        'us_total_cost_usd':     costs.get('total_us_cost', 0.0),
        'exchange_ratio':        costs.get('exchange_ratio', 0.0),
        'us_kia':                costs.get('us_mil_kia', 0),
        'us_wia':                costs.get('us_mil_wia', 0),
    }
finally:
    CSG_SCENARIOS[scenario_id].clear()
    CSG_SCENARIOS[scenario_id].update(original)

json.dumps(result)
`);

  const result   = JSON.parse(resultJson);
  const kmzBytes = pyodide.FS.readFile('/tmp/daemon_csg.kmz');
  return { result, kmzBytes };
}

// ─── message handler ─────────────────────────────────────────────────────────

self.onmessage = async (e) => {
  const { type, which, id, params } = e.data;

  try {
    if (type === 'init') {
      await init();

    } else if (type === 'run') {
      currentWhich = which;
      post('status', { msg: `Running ${which.toUpperCase()}: ${id}…` });

      let result, kmzBytes;
      if (which === 'kharg') {
        ({ result, kmzBytes } = await runKharg(id, params));
      } else {
        ({ result, kmzBytes } = await runCSG(id, params));
      }

      currentWhich = null;
      // Transfer the ArrayBuffer zero-copy to the main thread
      self.postMessage({ type: 'done', which, result, kmzBytes }, [kmzBytes.buffer]);
    }

  } catch (err) {
    const errWhich = currentWhich || which || null;
    currentWhich = null;
    post('error', { which: errWhich, msg: err.message || String(err) });
  }
};
