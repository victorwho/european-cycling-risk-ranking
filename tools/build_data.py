"""Generate the open data supplement and the map's city file from an edition's results.

Writes data/{stem}_city_index.csv, data/{stem}_criterion_panel.csv and
tools/map_cities.json. Column definitions follow build_academic_report.py in
OSRM_Server: access composite = mean over T42/T47/T52 of 0.7*city_a_score +
0.3*largest_component_share_km; locked share and low-stress km at T47.

Usage: python tools/build_data.py [--results DIR] [--stem eu300] [--check]
  --check writes nothing and diffs against the committed files instead.
"""
import argparse
import csv
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import edition  # noqa: E402

FLAG = {"AT": "🇦🇹", "BE": "🇧🇪", "BG": "🇧🇬", "CH": "🇨🇭", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪",
        "DK": "🇩🇰", "EE": "🇪🇪", "ES": "🇪🇸", "FI": "🇫🇮", "FR": "🇫🇷", "GB": "🇬🇧", "GR": "🇬🇷",
        "HR": "🇭🇷", "HU": "🇭🇺", "IE": "🇮🇪", "IS": "🇮🇸", "IT": "🇮🇹", "LT": "🇱🇹", "LU": "🇱🇺",
        "LV": "🇱🇻", "MT": "🇲🇹", "NL": "🇳🇱", "NO": "🇳🇴", "PL": "🇵🇱", "PT": "🇵🇹", "RO": "🇷🇴",
        "SE": "🇸🇪", "SI": "🇸🇮", "SK": "🇸🇰"}
# tier x shade (0 = safest quarter of the tier), as in the report's skyline
SHADES = {1: ["#D8EFD6", "#A5DCA9", "#66BB84", "#2E9058"],
          2: ["#FFF0BC", "#F5C93E", "#D99E0B", "#A87400"],
          3: ["#EFA28C", "#DC6A4C", "#C23A28", "#8F241A"]}
COLS = ["rank", "city", "iso2", "slug", "index", "rank_lo", "rank_hi", "tier", "tier_stability",
        "S_norm", "R_norm", "A_norm", "S_rank", "R_rank", "A_rank", "street_risk_per_km",
        "high_risk_share", "journey_risk_mean", "journey_risk_p90", "n_routed",
        "access_composite", "locked_pop_share", "low_stress_km", "street_km", "population"]


def rep_point(slug):
    from shapely.geometry import shape
    entries = json.load(open(os.path.join(edition.BOUNDARIES, f"{slug}_boundary_raw.json"),
                             encoding="utf-8"))
    p = shape(entries[0]["geojson"]).representative_point()
    return round(p.x, 4), round(p.y, 4)


def build(results):
    idx = json.load(open(os.path.join(results, "index117.json"), encoding="utf-8"))
    cities = sorted(idx["cities"], key=lambda c: c["rank"])
    ranks = {k: {c["slug"]: i for i, c in enumerate(sorted(cities, key=lambda c: c[k]), 1)}
             for k in "SRA"}
    tiers = {t: [c["slug"] for c in cities if c["tier"] == t] for t in (1, 2, 3)}
    rows, pins = [], []
    for c in cities:
        s = c["slug"]
        r = json.load(open(os.path.join(results, f"{s}.json"), encoding="utf-8"))
        ps, pr, pa = r["pillar_s"], r["pillar_r"], r["pillar_a"]
        acc = sum(0.7 * pa[t]["city_a_score"] + 0.3 * pa[t]["largest_component_share_km"]
                  for t in ("T42", "T47", "T52")) / 3
        locked = pa["T47"]["population_share_by_class"]["high_stress_locked"]
        iso = c["iso2"].upper()
        rows.append([c["rank"], c["label"], iso, s, c["index"], c["rank_lo"], c["rank_hi"],
                     c["tier"], c["tier_stability"], c["S"], c["R"], c["A"],
                     ranks["S"][s], ranks["R"][s], ranks["A"][s],
                     ps["s1_mean_risk_streets_comparable"], ps["s3_high_risk_share"],
                     pr["r1_route_risk"]["mean"], pr["r1_route_risk"]["p90"], pr["n_routed"],
                     round(acc, 4), locked, pa["T47"]["low_stress_km"], ps["street_km"],
                     r["frame"]["population"]])
        lst = tiers[c["tier"]]
        lon, lat = rep_point(s)
        pins.append({"s": s, "n": c["label"], "f": FLAG.get(iso, ""), "iso": iso,
                     "lon": lon, "lat": lat, "rank": c["rank"], "idx": c["index"],
                     "lo": c["rank_lo"], "hi": c["rank_hi"], "tier": c["tier"],
                     "stab": round(c["tier_stability"] * 100),
                     "s1": round(ps["s1_mean_risk_streets_comparable"], 1),
                     "r1": round(pr["r1_route_risk"]["mean"], 1), "locked": round(locked * 100),
                     "km": round(ps["street_km"]),
                     "col": SHADES[c["tier"]][min(3, lst.index(s) * 4 // len(lst))]})
    return rows, pins


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=edition.RESULTS)
    ap.add_argument("--stem", default=edition.DATA_STEM)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rows, pins = build(a.results)
    crit = list(csv.reader(open(os.path.join(a.results, "criterion.csv"), encoding="utf-8")))
    out = {os.path.join(ROOT, "data", f"{a.stem}_city_index.csv"): csv_text(COLS, rows),
           os.path.join(ROOT, "data", f"{a.stem}_criterion_panel.csv"): csv_text(crit[0], crit[1:]),
           os.path.join(HERE, "map_cities.json"): json.dumps(pins, ensure_ascii=False,
                                                            separators=(",", ":"))}
    for path, text in out.items():
        if a.check:
            old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            print(f"{os.path.relpath(path, ROOT)}: {'IDENTICAL' if old == text else 'DIFFERS'}")
        else:
            open(path, "w", encoding="utf-8", newline="").write(text)
            print(f"wrote {os.path.relpath(path, ROOT)} ({len(rows)} cities)")


if __name__ == "__main__":
    main()
