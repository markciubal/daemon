.PHONY: kharg csg all clean

# Generate all 30 Kharg Island assault scenarios → output/scenarios/kharg_island_*.kmz
kharg:
	python -m daemon.KHARG_ISLAND

# Generate all 30 CSG naval engagement scenarios → output/scenarios/scenario_*.kmz
csg:
	python -m daemon.CSG_SIM

# Generate everything (Kharg + CSG)
all:
	python -m daemon.ALL

# Remove all generated output
clean:
	rm -rf output/scenarios/*
	rm -f output/wargame_master.kml output/wargame_summary.kmz
