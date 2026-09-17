# Site builders

The website is generated, never hand-edited:

1. `build_linkedin_report.py` — builds the shared page (`streets_not_reputations.html`)
   from `ccri_pilot/results200s_sens/index117.json` in the OSRM_Server repo.
   Same file is published as the claude.ai artifact.
2. `build_site.py` — wraps it as `index.html` (head/OG tags), injects the
   interactive map (reads `map_cities.json`), regenerates `social-card.png`.
3. `map_cities.json` — per-city map data (coordinates from boundary
   representative points + popup stats + tier-shade colours); regenerate from
   the index results when the ranking changes.

Run 1 then 2 from this directory's parent layout (paths inside assume the
OSRM_Server repo at C:\dev\OSRM_Server), commit `../index.html`,
`../social-card.png` and push — GitHub Pages serves from main.
