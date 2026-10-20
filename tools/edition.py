"""The one place an edition is named. Every builder imports from here.

Validation figures are computed in the OSRM_Server repo (eu117_criterion.py,
the mode-share check) and copied here with their source; everything else is
read from the results directory.
"""
import os

EDITION = "EU-300"
DATA_STEM = "eu300"                       # data/eu300_city_index.csv, ...
OSRM_REPO = os.environ.get("OSRM_REPO", r"C:\dev\OSRM_Server")
RESULTS = os.environ.get("EDITION_RESULTS",
                         os.path.join(OSRM_REPO, "ccri_pilot", "results300s_nb"))
BOUNDARIES = os.path.join(os.path.dirname(RESULTS), "data")   # the ccri_pilot the results came from

# from results300s_nb/criterion.log and the mode-share check (EU300_INDEX_PLAN.md gate log)
CRITERION_RR = 0.78                       # KSI rate ratio per +10 index points
CRITERION_CI = (0.70, 0.87)
MODESHARE_RHO = 0.54                      # Spearman vs Eurostat TT1007V
MODESHARE_N = 220
