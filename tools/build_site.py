"""Wrap the artifact page as a standalone GitHub Pages site + social card."""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "streets_not_reputations.html")
SITE = os.path.join(HERE, "site")
os.makedirs(SITE, exist_ok=True)
BASE = "https://victorwho.github.io/european-cycling-risk-ranking/"

body = open(SRC, encoding="utf-8").read()

# ---- interactive map section (site-only: artifact CSP blocks map tiles) ------
cities_json = open(os.path.join(HERE, "map_cities.json"), encoding="utf-8").read()
MAP_SECTION = """
<h2 id="map-h">Find your city</h2>
<p class="figcap" style="margin-bottom:12px">Every dot is a ranked city, coloured by tier.
Click a dot — or search — for its rank, score and what drives it. Ctrl/⌘-scroll to zoom.</p>
<input id="cityfind" list="citylist" placeholder="Type a city…" autocomplete="off">
<datalist id="citylist"></datalist>
<div id="map" role="application" aria-label="Interactive map of 219 ranked cities"></div>
<style>
#map { height: 540px; border:1px solid var(--rule); border-radius:10px; margin-top:10px; }
@media (max-width:640px){ #map { height: 420px; } }
#cityfind { box-sizing:border-box; font-family:'Plus Jakarta Sans',sans-serif; font-size:15px; padding:9px 12px; width:min(340px,100%);
  border:1px solid var(--rule); border-radius:8px; background:var(--card); color:var(--ink); }
#cityfind:focus { outline:3px solid var(--brand); outline-offset:1px; }
.maplibregl-popup-content { background:var(--card); color:var(--ink);
  font-family:'Plus Jakarta Sans',sans-serif; border-radius:16px; padding:14px 16px 12px;
  box-shadow:0 6px 24px rgba(0,0,0,.18); min-width:230px; }
.maplibregl-popup-tip { border-top-color:var(--card) !important; border-bottom-color:var(--card) !important; }
.maplibregl-popup-close-button { color:var(--ink3); font-size:18px; padding:2px 7px; }
.pp-city { font-weight:800; font-size:17px; }
.pp-rank { font-weight:800; font-size:30px; line-height:1.05; margin:4px 0 2px;
  font-variant-numeric:tabular-nums; }
.pp-rank small { font-size:13px; font-weight:700; color:var(--ink3); }
.pp-meta { font-size:12px; color:var(--ink3); margin-bottom:8px; }
.pp-row { display:flex; justify-content:space-between; gap:14px; font-size:13px;
  border-top:1px solid var(--rule); padding:4px 0; }
.pp-row b { font-variant-numeric:tabular-nums; }
.pp-cta { display:block; margin-top:10px; padding:8px 12px; border-radius:8px;
  background:var(--navy); color:#F2C30F; font-weight:700; font-size:12.5px;
  text-decoration:none; text-align:center; }
.pp-cta:hover { background:#000; }
</style>
<script>
(function () {
  var C = __CITIES__;
  var dark = matchMedia("(prefers-color-scheme: dark)").matches;
  var map = new maplibregl.Map({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/positron",
    center: [11.5, 52.6], zoom: 3.3, minZoom: 2.6, maxZoom: 12,
    cooperativeGestures: true, attributionControl: {compact: true}
  });
  map.addControl(new maplibregl.NavigationControl({showCompass:false}));
  var gj = {type:"FeatureCollection", features: C.map(function (c) {
    return {type:"Feature", geometry:{type:"Point", coordinates:[c.lon, c.lat]}, properties:c};
  })};
  map.on("load", function () {
    map.addSource("cities", {type:"geojson", data: gj});
    map.addLayer({id:"dots", type:"circle", source:"cities", paint:{
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, 4.5, 6, 7, 9, 11],
      "circle-color": ["get", "col"],
      "circle-stroke-width": 1.4,
      "circle-stroke-color": "#FFFFFF",
      "circle-opacity": 0.92
    }});
    map.addLayer({id:"ranks", type:"symbol", source:"cities", minzoom: 5.5, layout:{
      "text-field": ["to-string", ["get","rank"]],
      "text-size": 11, "text-offset": [0, -1.35],
      "text-font": ["Noto Sans Bold"]
    }, paint:{
      "text-color": "#15151F",
      "text-halo-color": "#FFFFFF", "text-halo-width": 1.4
    }});
    map.on("mouseenter", "dots", function(){ map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "dots", function(){ map.getCanvas().style.cursor = ""; });
    map.on("click", "dots", function (e) { openPopup(e.features[0].properties, true); });
  });
  var pop = null;
  function openPopup(p, fly) {
    if (typeof p.idx === "string") { /* maplibre stringifies numbers in props sometimes */ }
    var tiern = {1:"Tier 1 · lower risk", 2:"Tier 2 · middle", 3:"Tier 3 · higher risk"}[p.tier];
    var html = '<div class="pp-city">' + p.f + " " + p.n + '</div>'
      + '<div class="pp-rank">#' + p.rank + ' <small>of ' + C.length + '</small></div>'
      + '<div class="pp-meta">index ' + p.idx + ' · interval ' + p.lo + "–" + p.hi
      + '<br>' + tiern + ' · keeps its tier in ' + p.stab + '% of re-runs</div>'
      + '<div class="pp-row"><span>Street-network risk</span><b>' + p.s1 + '</b></div>'
      + '<div class="pp-row"><span>Typical journey risk</span><b>' + p.r1 + '</b></div>'
      + '<div class="pp-row"><span>Residents locked to high-stress streets</span><b>' + p.locked + '%</b></div>'
      + '<div class="pp-row"><span>Street network</span><b>' + p.km.toLocaleString() + ' km</b></div>'
      + (p.tier == 3 ? '<a class="pp-cta" href="#forcities">Your city? Get the street-level breakdown &rarr;</a>' : '');
    if (pop) pop.remove();
    pop = new maplibregl.Popup({offset: 12, maxWidth: "300px"})
      .setLngLat([p.lon, p.lat]).setHTML(html).addTo(map);
    if (fly) map.flyTo({center:[p.lon, p.lat], zoom: Math.max(map.getZoom(), 7), speed: 1.4});
  }
  var dl = document.getElementById("citylist");
  C.forEach(function (c) {
    var o = document.createElement("option");
    o.value = c.n; o.label = "#" + c.rank + " · " + c.iso;
    dl.appendChild(o);
  });
  document.getElementById("cityfind").addEventListener("change", function (e) {
    var q = e.target.value.trim().toLowerCase();
    var c = C.find(function (x) { return x.n.toLowerCase() === q; })
         || C.find(function (x) { return x.n.toLowerCase().indexOf(q) === 0; });
    if (c) openPopup(c, true);
  });
})();
</script>
"""
MAP_SECTION = MAP_SECTION.replace("__CITIES__", cities_json)
anchor = "<h2>The top ten</h2>"
assert anchor in body
body = body.replace(anchor, MAP_SECTION + anchor, 1)
# lift the <title> and font <link>s into the head
import re
title = re.search(r"<title>.*?</title>", body).group(0)
links = re.findall(r'<link[^>]+>', body)
for frag in [title] + links:
    body = body.replace(frag, "", 1)

DESC = ("219 European cities ranked by cycling risk, measured from 67 million road "
        "segments and validated against 1,169 serious injuries. Stockholm first, "
        "Amsterdam 9th — and where the famous rankings disagree, the injury data "
        "picks a side.")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{title}
<meta name="description" content="{DESC}">
<link rel="canonical" href="{BASE}">
<meta property="og:type" content="article">
<meta property="og:title" content="Streets, Not Reputations">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{BASE}">
<meta property="og:image" content="{BASE}social-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Streets, Not Reputations">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{BASE}social-card.png">
{chr(10).join(links)}
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<style>img{{max-width:100%}}</style>
</head>
<body>
{body}
</body>
</html>
"""
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(doc)
print("site/index.html written", len(doc), "chars")

# ---- social card (1200x630) --------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

idx = json.load(open(r"C:\dev\OSRM_Server\ccri_pilot\results200s_sens\index117.json", encoding="utf-8"))
cities = sorted(idx["cities"], key=lambda c: c["rank"])
DARKM = {1: ["#E2F5E0", "#B4E4B8", "#7BCA96", "#45A56C"],
         2: ["#FFF3C7", "#F8D45C", "#E4AC24", "#BD8A10"],
         3: ["#F5B7A4", "#E67F61", "#D14C36", "#A63524"]}
tier_lists = {t: [c["slug"] for c in cities if c["tier"] == t] for t in (1, 2, 3)}
def card_col(c):
    lst = tier_lists[c["tier"]]
    return DARKM[c["tier"]][min(3, lst.index(c["slug"]) * 4 // len(lst))]

fig = plt.figure(figsize=(12, 6.3), dpi=100)
fig.patch.set_facecolor("#1A1A2E")
ax = fig.add_axes([0.045, 0.10, 0.91, 0.44])
ax.set_facecolor("#1A1A2E")
for i, c in enumerate(cities):
    ax.bar(i, c["index"], width=0.86, color=card_col(c), linewidth=0)
ax.set_xlim(-1, len(cities))
ax.set_ylim(0, 105)
ax.axis("off")
fig.text(0.045, 0.90, "STREETS, NOT REPUTATIONS", color="#FAFAF7",
         fontsize=44, fontweight="bold", family="Arial", va="top")
fig.text(0.045, 0.745, "219 European cities, ranked by cycling risk — measured, not voted.",
         color="#C9C9D6", fontsize=19, family="Arial", va="top")
fig.text(0.045, 0.66, "Defensive Pedal Research · 2026", color="#F2C30F",
         fontsize=14, family="Arial", va="top")
fig.text(0.045, 0.045, "1  Stockholm", color="#B4E4B8", fontsize=15,
         fontweight="bold", family="Arial")
fig.text(0.955, 0.045, "219  Brăila", color="#9A9AA8", fontsize=15,
         family="Arial", ha="right")
fig.savefig(os.path.join(SITE, "social-card.png"), dpi=100,
            facecolor="#1A1A2E", bbox_inches=None)
print("social-card.png written")
