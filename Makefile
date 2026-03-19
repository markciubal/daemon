.PHONY: kharg csg all clean

# Generate all 30 Kharg Island assault scenarios → output/scenarios/kharg_island_*.kmz
kharg:
	python -m persian_gulf_simulation.runner

# Generate all 30 CSG naval engagement scenarios → output/scenarios/scenario_*.kmz
csg:
	python -m persian_gulf_simulation.generate_wargame_kml

# Generate everything
all: kharg csg

# Remove all generated output
clean:
	rm -rf output/scenarios/*
	rm -f output/wargame_master.kml output/wargame_summary.kmz
