"""Build the LinkedIn-shareable EU-219 ranking page from index117.json."""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
IDX = r"C:\dev\OSRM_Server\ccri_pilot\results200s_sens\index117.json"
OUT = os.path.join(HERE, "streets_not_reputations.html")

FLAG = {"AT":"🇦🇹","BE":"🇧🇪","BG":"🇧🇬","CH":"🇨🇭","CY":"🇨🇾","CZ":"🇨🇿","DE":"🇩🇪","DK":"🇩🇰",
        "EE":"🇪🇪","ES":"🇪🇸","FI":"🇫🇮","FR":"🇫🇷","GR":"🇬🇷","HR":"🇭🇷","HU":"🇭🇺","IE":"🇮🇪",
        "IS":"🇮🇸","IT":"🇮🇹","LT":"🇱🇹","LU":"🇱🇺","LV":"🇱🇻","MT":"🇲🇹","NL":"🇳🇱","NO":"🇳🇴",
        "PL":"🇵🇱","PT":"🇵🇹","RO":"🇷🇴","SE":"🇸🇪","SI":"🇸🇮","SK":"🇸🇰"}

idx = json.load(open(IDX, encoding="utf-8"))
cities = sorted(idx["cities"], key=lambda c: c["rank"])
by_slug = {c["slug"]: c for c in cities}
N = len(cities)

# ---- skyline SVG (219 bars, tier-coloured) ----------------------------------
W, H, pad_l, pad_b, pad_t = 940, 240, 8, 34, 30
bw = (W - 2 * pad_l) / N
bars, labels = [], []
# shade within tier: equal-count quartiles by score order (darker = riskier)
tier_lists = {t: [c["slug"] for c in cities if c["tier"] == t] for t in (1, 2, 3)}
def shade_of(c):
    lst = tier_lists[c["tier"]]
    return min(3, lst.index(c["slug"]) * 4 // len(lst))
LABELED = {"stockholm": "Stockholm #1", "munich": "Munich 21", "malmo": "Malmö 38",
           "madrid": "Madrid 109", "zurich": "Zurich 135", "rome": "Rome 182",
           "bucharest": "Bucharest 207", "braila": "Brăila 219"}
for i, c in enumerate(cities):
    h = (H - pad_b - pad_t) * c["index"] / 100.0
    x = pad_l + i * bw
    bars.append(
        f'<rect class="bar s{c["tier"]}-{shade_of(c)}" x="{x:.2f}" y="{H-pad_b-h:.2f}" '
        f'width="{max(bw-0.5,0.8):.2f}" height="{max(h,1.5):.2f}" '
        f'data-n="{c["rank"]}. {c["label"]}" data-v="index {c["index"]:.0f} · interval {c["rank_lo"]}–{c["rank_hi"]}"/>')
    if c["slug"] in LABELED:
        anchor = "start" if i < N * 0.12 else ("end" if i > N * 0.88 else "middle")
        labels.append(
            f'<line x1="{x+bw/2:.1f}" y1="{H-pad_b-h-4:.1f}" x2="{x+bw/2:.1f}" y2="{H-pad_b-h-12:.1f}" class="lbl-tick"/>'
            f'<text x="{x+bw/2:.1f}" y="{H-pad_b-h-17:.1f}" class="lbl" text-anchor="{anchor}">{LABELED[c["slug"]]}</text>')
skyline = (
    f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Index value for all {N} cities, ranked, coloured by tier">'
    + "".join(bars) + "".join(labels)
    + f'<line x1="{pad_l}" y1="{H-pad_b}" x2="{W-pad_l}" y2="{H-pad_b}" class="axis"/>'
    + f'<text x="{pad_l}" y="{H-10}" class="lbl axis-lbl">rank 1</text>'
    + f'<text x="{W-pad_l}" y="{H-10}" class="lbl axis-lbl" text-anchor="end">rank {N}</text>'
    + '</svg>')

# ---- top 10 plates -----------------------------------------------------------
TAGS = {"stockholm": "the upset — we audited it ourselves, and it held",
        "helsinki": "the fastest riser in Europe, by our model and everyone else's",
        "antwerp": "the most agreed-upon cycling city in Europe",
        "haarlem": "the Dutch cities the famous rankings never test",
        "leiden": "", "vantaa": "the suburbs nobody celebrates — until you measure them",
        "thehague": "", "espoo": "", "amsterdam": "the reputation, confirmed",
        "barcelona": "superblocks and 30 km/h zones, measurable from orbit"}
plates = []
for c in cities[:10]:
    tag = TAGS.get(c["slug"], "")
    plates.append(
        f'<div class="plate"><div class="plate-rank">{c["rank"]}</div>'
        f'<div class="plate-body"><div class="plate-city">{FLAG.get(c["iso2"].upper(),"")}&nbsp;{c["label"]}'
        f'<span class="plate-idx">{c["index"]:.0f}</span></div>'
        + (f'<div class="plate-tag">{tag}</div>' if tag else "")
        + f'<div class="plate-int">interval {c["rank_lo"]}–{c["rank_hi"]}</div></div></div>')
top10 = "\n".join(plates)

# ---- versus scatter: Copenhagenize 2025 (European top 30) vs us --------------
CPH = ["utrecht","copenhagen","ghent","amsterdam","paris","helsinki","muenster","antwerp",
       "bordeaux","nantes","bonn","thehague","strasbourg","lyon","malmo","munich","oslo",
       "vienna","bern","graz","zurich","rotterdam","ljubljana","bologna","stockholm",
       "vitoria","wroclaw"]
HOT = {"bordeaux": "Bordeaux — their 9th, our 116th. Worst injury rate of any French panel city.",
       "zurich": "Zurich — their 21st, our 135th. Worst injury rate in our whole outcome panel.",
       "stockholm": "Stockholm — our 1st, their 26th.", "muenster": "Münster", "utrecht": "Utrecht",
       "helsinki": "Helsinki", "antwerp": "Antwerp"}
SW, SH, SL, SR, ST, SB = 940, 430, 64, 30, 26, 52
ymax = 145
def sx(v): return SL + (v - 1) / 27.0 * (SW - SL - SR)
def sy(v): return ST + (min(v, ymax) - 1) / (ymax - 1) * (SH - ST - SB)
pts, plabels = [], []
for i, s in enumerate(CPH, 1):
    c = by_slug[s]
    hot = s in ("bordeaux", "zurich")
    cls = "pt hot" if hot else "pt"
    pts.append(f'<circle class="{cls}" cx="{sx(i):.1f}" cy="{sy(c["rank"]):.1f}" r="{7 if hot else 5.5}" '
               f'data-n="{c["label"]}" data-v="Copenhagenize #{i} · ours #{c["rank"]}"/>')
    if s in HOT:
        name = c["label"]
        dy = -11 if s not in ("utrecht", "muenster") else 18
        anch = "middle"
        if s == "stockholm": anch, dy = "start", 5
        if s == "zurich": dy = -12
        plabels.append(f'<text class="plbl{" plbl-hot" if hot else ""}" x="{sx(i):.1f}" '
                       f'y="{sy(c["rank"])+dy:.1f}" text-anchor="{anch}">{name}</text>')
grid = []
for gy in (1, 30, 60, 90, 120):
    grid.append(f'<line class="grid" x1="{SL}" y1="{sy(gy):.1f}" x2="{SW-SR}" y2="{sy(gy):.1f}"/>'
                f'<text class="lbl" x="{SL-8}" y="{sy(gy)+3.5:.1f}" text-anchor="end">{gy}</text>')
diag = f'<line class="diag" x1="{sx(1):.1f}" y1="{sy(1):.1f}" x2="{sx(27):.1f}" y2="{sy(27):.1f}"/>'
scatter = (
    f'<svg viewBox="0 0 {SW} {SH}" role="img" aria-label="Copenhagenize 2025 rank versus our rank, 27 cities">'
    + "".join(grid) + diag + "".join(pts) + "".join(plabels)
    + f'<text class="lbl" x="{(SL+SW-SR)/2:.0f}" y="{SH-12}" text-anchor="middle">Copenhagenize Index 2025 rank (their European top 30) →</text>'
    + f'<text class="lbl" x="16" y="{(ST+SH-SB)/2:.0f}" text-anchor="middle" transform="rotate(-90 16 {(ST+SH-SB)/2:.0f})">our rank →</text>'
    + f'<text class="lbl diag-lbl" x="{sx(23):.1f}" y="{sy(20):.1f}">perfect agreement</text>'
    + '</svg>')

# ---- full table --------------------------------------------------------------
TIER_NAME = {1: "Tier 1 — lower assessed risk", 2: "Tier 2 — middle", 3: "Tier 3 — higher assessed risk"}
rows = []
for t in (1, 2, 3):
    rows.append(f'<tr class="grp gt{t}"><td colspan="4">{TIER_NAME[t]}</td></tr>')
    for c in [c for c in cities if c["tier"] == t]:
        star = "" if c["placed"] else "*"
        rows.append(f'<tr><td class="r">{c["rank"]}</td>'
                    f'<td>{FLAG.get(c["iso2"].upper(),"")}&nbsp;{c["label"]}{star}</td>'
                    f'<td class="r">{c["index"]:.0f}</td>'
                    f'<td class="r ci">{c["rank_lo"]}–{c["rank_hi"]}</td></tr>')
table = "\n".join(rows)

ro = [c for c in cities if c["iso2"].upper() == "RO"]
ro_last20 = sum(1 for c in cities[-20:] if c["iso2"].upper() == "RO")

html = f"""<title>Streets, Not Reputations</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400..800;1,400..800&display=swap">
<style>
:root {{
  --paper:#FAFAF7; --ink:#15151F; --ink2:#3C3C50; --ink3:#6B6B7B;
  --rule:#E8E6DC; --card:#FFFFFF;
  --g0:#D8EFD6; --g1:#A5DCA9; --g2:#66BB84; --g3:#2E9058; --y0:#FFF0BC; --y1:#F5C93E; --y2:#D99E0B; --y3:#A87400; --r0:#EFA28C; --r1:#DC6A4C; --r2:#C23A28; --r3:#8F241A; --dot:#62679F;
  --hot:#E14848; --hot-ink:#C43B3B;
  --brand:#F2C30F; --brand-2:#FFD83D; --brand-soft:#FEF6D6;
  --navy:#1A1A2E; --plate-ink:#1A1A2E;
  --sh1:0 1px 2px rgba(20,20,30,.04), 0 2px 8px rgba(20,20,30,.04);
  --sh2:0 4px 12px rgba(20,20,30,.06), 0 8px 24px rgba(20,20,30,.06);
  --tt:240ms cubic-bezier(.2,.7,.2,1); --tt-ease:cubic-bezier(.2,.7,.2,1);
  --font:'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#1A1A2E; --ink:#F5F5FA; --ink2:#C9C9D6; --ink3:#9A9AA8;
    --rule:#2F2F4F; --card:#252542;
    --g0:#E2F5E0; --g1:#B4E4B8; --g2:#7BCA96; --g3:#45A56C; --y0:#FFF3C7; --y1:#F8D45C; --y2:#E4AC24; --y3:#BD8A10; --r0:#F5B7A4; --r1:#E67F61; --r2:#D14C36; --r3:#A63524; --dot:#8B90C4;
    --hot:#E86A6A; --hot-ink:#F08A8A;
    --brand:#F2C30F; --brand-2:#FFD83D; --brand-soft:rgba(242,195,15,.10);
    --navy:#1A1A2E; --plate-ink:#1A1A2E;
    --sh1:0 1px 2px rgba(0,0,0,.25); --sh2:0 6px 18px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="dark"] {{
  --paper:#1A1A2E; --ink:#F5F5FA; --ink2:#C9C9D6; --ink3:#9A9AA8;
  --rule:#2F2F4F; --card:#252542;
  --g0:#E2F5E0; --g1:#B4E4B8; --g2:#7BCA96; --g3:#45A56C; --y0:#FFF3C7; --y1:#F8D45C; --y2:#E4AC24; --y3:#BD8A10; --r0:#F5B7A4; --r1:#E67F61; --r2:#D14C36; --r3:#A63524; --dot:#8B90C4;
  --hot:#E86A6A; --hot-ink:#F08A8A;
  --brand:#F2C30F; --brand-2:#FFD83D; --brand-soft:rgba(242,195,15,.10);
  --navy:#1A1A2E; --plate-ink:#1A1A2E;
  --sh1:0 1px 2px rgba(0,0,0,.25); --sh2:0 6px 18px rgba(0,0,0,.35);
}}
body {{ background:var(--paper); color:var(--ink); margin:0;
  font-family:var(--font); font-size:16.5px; line-height:1.65; }}
.wrap {{ max-width:960px; margin:0 auto; padding-block:0 64px; padding-inline:20px; }}
.prose {{ max-width:680px; }}
.brandrow {{ display:flex; align-items:center; gap:12px; margin:44px 0 26px; }}
.brandrow img {{ height:44px; width:44px; }}
.brandrow .bn {{ font-weight:800; font-size:15.5px; letter-spacing:-.01em; }}
.brandrow .bt {{ font-size:12px; color:var(--ink3); }}
.eyebrow {{ font-size:12px; font-weight:700; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink3); margin:0 0 14px; }}
h1 {{ font-size:clamp(38px,6.8vw,64px); line-height:1.02; margin:0 0 18px;
  font-weight:800; letter-spacing:-.03em; text-wrap:balance; }}
h1 .hl {{ background:linear-gradient(transparent 62%, var(--brand) 62%, var(--brand) 94%, transparent 94%); }}
.dek {{ font-size:clamp(17px,2.3vw,20px); line-height:1.55; color:var(--ink2); max-width:640px; margin:0 0 8px; }}
.dek b {{ color:var(--ink); font-weight:700; }}
h2 {{ font-size:clamp(23px,3.2vw,30px); font-weight:800; letter-spacing:-.02em;
  margin:64px 0 10px; text-wrap:balance; }}
h3 {{ font-size:18px; font-weight:700; margin:34px 0 6px; }}
p {{ margin:0 0 14px; }}
.figure {{ margin:26px 0 8px; }}
.figcap {{ font-size:13px; color:var(--ink3); margin:6px 0 0; line-height:1.5; }}
.figure svg {{ width:100%; height:auto; display:block; }}
.storebtns svg {{ flex:none; }}
.bar.s1-0 {{ fill:var(--g0); }} .bar.s1-1 {{ fill:var(--g1); }} .bar.s1-2 {{ fill:var(--g2); }} .bar.s1-3 {{ fill:var(--g3); }}
.bar.s2-0 {{ fill:var(--y0); }} .bar.s2-1 {{ fill:var(--y1); }} .bar.s2-2 {{ fill:var(--y2); }} .bar.s2-3 {{ fill:var(--y3); }}
.bar.s3-0 {{ fill:var(--r0); }} .bar.s3-1 {{ fill:var(--r1); }} .bar.s3-2 {{ fill:var(--r2); }} .bar.s3-3 {{ fill:var(--r3); }}
.bar {{ transition:opacity var(--tt); }}
.bar:hover {{ opacity:.72; }}
.axis {{ stroke:var(--rule); stroke-width:1.2; }}
.grid {{ stroke:var(--rule); stroke-width:.8; }}
.lbl {{ font-family:var(--font); font-size:11.5px; fill:var(--ink3); }}
.lbl-tick {{ stroke:var(--ink3); stroke-width:1; }}
.axis-lbl {{ font-weight:700; }}
.legend {{ display:flex; flex-wrap:wrap; gap:18px; margin-top:10px;
  font-size:13px; color:var(--ink2); }}
.legend .sw.grad {{ width:34px; }}
.legend .sw {{ display:inline-block; width:11px; height:11px; border-radius:3px;
  margin-right:6px; vertical-align:-1px; }}
.plates {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:12px; margin:24px 0 4px; }}
.plate {{ display:flex; gap:14px; align-items:center; background:var(--card);
  border:1px solid var(--rule); border-radius:16px; padding:14px 16px;
  box-shadow:var(--sh1); transition:box-shadow var(--tt), transform var(--tt); }}
.plate:hover {{ box-shadow:var(--sh2); transform:translateY(-1px); }}
.plate-rank {{ font-weight:800; font-size:26px; min-width:56px; height:56px;
  border-radius:14px; display:flex; align-items:center; justify-content:center;
  color:var(--plate-ink); background:var(--brand); font-variant-numeric:tabular-nums; }}
.plate-city {{ font-weight:800; font-size:17px; display:flex; align-items:baseline; gap:8px; }}
.plate-idx {{ color:var(--ink3); font-weight:700; font-size:14px; }}
.plate-tag {{ font-size:13.5px; color:var(--ink2); line-height:1.4; }}
.plate-int {{ font-size:11.5px; color:var(--ink3); font-variant-numeric:tabular-nums; margin-top:2px; }}
.howgrid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px; margin:22px 0 26px; }}
.howcard {{ background:var(--card); border:1px solid var(--rule); border-radius:16px;
  padding:16px 16px 12px; box-shadow:var(--sh1); border-top:4px solid var(--rule); }}
.howcard.hc1 {{ border-top-color:var(--g2); }}
.howcard.hc2 {{ border-top-color:var(--y2); }}
.howcard.hc3 {{ border-top-color:var(--r2); }}
.hc-title {{ font-weight:800; font-size:16px; margin-bottom:10px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }}
.chip {{ font-size:12.5px; font-weight:600; color:var(--ink2); background:var(--paper);
  border:1px solid var(--rule); border-radius:999px; padding:3px 10px; }}
.hc-verdict {{ font-size:13.5px; line-height:1.45; color:var(--ink2); margin:0; }}
.dims {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px; margin:22px 0 26px; }}
.dimcard {{ background:var(--card); border:1px solid var(--rule); border-radius:16px;
  padding:18px 18px 12px; box-shadow:var(--sh1); }}
.dimbadge {{ display:inline-flex; align-items:center; justify-content:center;
  font-weight:800; font-size:16px; color:var(--plate-ink); background:var(--brand);
  border-radius:10px; padding:5px 12px; margin-bottom:10px;
  font-variant-numeric:tabular-nums; }}
.dim-title {{ font-weight:800; font-size:16.5px; margin-bottom:8px; line-height:1.3; }}
.dim-body {{ font-size:14px; line-height:1.55; color:var(--ink2); margin:0; }}
.arglist {{ counter-reset:arg; margin:18px 0 0; padding:0; list-style:none; }}
.arglist>li {{ position:relative; padding-left:64px; margin-bottom:26px; }}
.arglist>li::before {{ counter-increment:arg; content:counter(arg);
  position:absolute; left:0; top:2px; font-weight:800; font-size:22px;
  color:var(--plate-ink); background:var(--brand); width:42px; height:42px;
  border-radius:12px; display:flex; align-items:center; justify-content:center; }}
.arglist b {{ font-weight:800; font-size:16.5px; }}
.hotword {{ color:var(--hot-ink); font-weight:700; }}
.pt {{ fill:var(--dot); opacity:.9; transition:opacity var(--tt); }} .pt.hot {{ fill:var(--hot); opacity:1; }}
.pt:hover {{ opacity:.6; }}
.diag {{ stroke:var(--ink3); stroke-width:1; stroke-dasharray:5 5; opacity:.7; }}
.diag-lbl {{ font-style:italic; }}
.plbl {{ font-family:var(--font); font-size:12px; font-weight:700; fill:var(--ink2); }}
.plbl-hot {{ fill:var(--hot-ink); }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:24px 0; }}
.tile {{ background:var(--card); border:1px solid var(--rule); border-radius:16px;
  padding:20px 18px 16px; box-shadow:var(--sh1); }}
.tile .big {{ font-weight:800; font-size:38px; line-height:1; letter-spacing:-.02em;
  font-variant-numeric:tabular-nums; }}
.tile .what {{ font-size:13px; color:var(--ink2); margin-top:8px; line-height:1.5; }}
.caveat {{ border:1px solid var(--rule); border-left:4px solid var(--brand);
  background:var(--brand-soft); border-radius:12px; padding:14px 18px; margin:28px 0;
  color:var(--ink2); font-size:15px; }}
.caveat b {{ color:var(--ink); }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
.tblwrap {{ overflow-x:auto; margin-top:18px; }}
th,td {{ padding:6px 10px; border-bottom:1px solid var(--rule); text-align:left; }}
thead th {{ font-size:11.5px; text-transform:uppercase; letter-spacing:.08em; color:var(--ink3); }}
td.r {{ text-align:right; font-variant-numeric:tabular-nums; }}
td.ci {{ color:var(--ink3); font-size:13px; }}
tr.grp.gt1 td {{ border-bottom-color:var(--g2); }} tr.grp.gt2 td {{ border-bottom-color:var(--y2); }}
tr.grp.gt3 td {{ border-bottom-color:var(--r2); }}
tr.grp td {{ font-weight:800; padding-top:22px; border-bottom:2px solid var(--ink2); font-size:12.5px;
  text-transform:uppercase; letter-spacing:.07em; }}
.citycta {{ background:var(--navy); border-radius:16px; padding:28px 26px;
  margin:36px 0 8px; box-shadow:var(--sh2); }}
.citycta-inner {{ max-width:640px; }}
.citycta-h {{ color:#FAFAF7; margin:0 0 10px; font-size:clamp(21px,3vw,26px);
  font-weight:800; letter-spacing:-.02em; }}
.citycta-p {{ color:#C9C9D6; font-size:15px; line-height:1.6; margin:0 0 18px; }}
.citycta-p b {{ color:#FAFAF7; }}
.citycta-p a {{ color:var(--brand-2); text-underline-offset:3px; }}
.citycta-act {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
.citycta-btn {{ display:inline-flex; align-items:center; justify-content:center;
  background:var(--brand); color:#1A1A2E; font-weight:800; font-size:15px;
  text-decoration:none; padding:12px 20px; border-radius:10px; min-height:44px;
  box-sizing:border-box; transition:background var(--tt), transform var(--tt); }}
.citycta-btn:hover {{ background:var(--brand-2); }}
.citycta-btn:active {{ transform:scale(.98); }}
.citycta-addr {{ color:#9A9AA8; font-size:13px; }}
.foot {{ margin-top:56px; padding-top:18px; border-top:1px solid var(--rule);
  font-size:13.5px; color:var(--ink3); line-height:1.6; }}
.foot a, .prose a {{ color:inherit; text-underline-offset:3px; transition:color var(--tt); }}
.foot a:hover, .prose a:hover {{ color:var(--hot-ink); }}
.storebtns {{ display:flex; flex-wrap:wrap; gap:8px; }}
.storebtns a {{ display:inline-flex; align-items:center; justify-content:center; gap:8px;
  background:var(--navy); color:#FAFAF7; text-decoration:none; font-weight:700;
  font-size:14px; padding:10px 16px; border-radius:10px; min-height:44px;
  transition:background var(--tt), transform var(--tt); }}
.storebtns a:hover {{ background:#000; }}
.storebtns a:active {{ transform:scale(.98); }}
.appcta {{ display:flex; align-items:center; justify-content:space-between; gap:20px;
  flex-wrap:wrap; background:var(--brand); border-radius:16px; padding:20px 22px;
  margin:30px 0; box-shadow:var(--sh2); }}
.appcta-txt {{ max-width:520px; }}
.appcta-h {{ font-weight:800; font-size:19px; color:#15151F; margin-bottom:4px; letter-spacing:-.01em; }}
.appcta p {{ margin:0; font-size:14.5px; color:#3C3C50; line-height:1.5; }}
#cta {{ position:fixed; right:14px; bottom:max(16px, env(safe-area-inset-bottom, 0px));
  z-index:20; background:var(--brand); border-radius:12px; box-shadow:var(--sh1);
  width:min(232px, calc(100vw - 28px)); font-family:var(--font);
  transition:width var(--tt), border-radius var(--tt); }}
#cta.closed {{ width:auto; border-radius:999px; }}
#cta-head {{ display:flex; align-items:center; justify-content:space-between; width:100%;
  background:none; border:0; cursor:pointer; font:inherit; font-weight:800;
  font-size:13px; color:#15151F; padding:9px 14px; min-height:40px; }}
#cta-chev {{ font-size:11px; color:#7a6200; padding-left:8px; transition:transform var(--tt)}}
#cta.closed #cta-chev {{ transform:rotate(180deg); }}
#cta.closed #cta-body {{ display:none; }}
#cta-body {{ padding:0 13px 12px; }}
#cta-body p {{ margin:0 0 10px; font-size:12.5px; color:#1a1a1a; line-height:1.45; }}
#cta .storebtns a {{ font-size:13px; padding:8px 12px; }}
#cta .storebtns {{ flex-direction:column; }}
#cta .storebtns a {{ width:100%; box-sizing:border-box; }}
@media (max-width:640px) {{ .appcta {{ flex-direction:column; align-items:flex-start; }} }}
#tip {{ position:fixed; pointer-events:none; background:var(--navy); color:#FAFAF7;
  font-family:var(--font); font-size:12.5px; padding:7px 10px; border-radius:10px;
  line-height:1.4; opacity:0; transition:opacity .1s; z-index:9; max-width:260px;
  box-shadow:var(--sh2); }}
#tip b {{ display:block; }}
@media (max-width:520px) {{ .arglist>li {{ padding-left:0; }} .arglist>li::before {{ position:static; display:flex; margin-bottom:6px; }} }}

/* ---- motion layer: transform/opacity only, gated on html.anim (JS + no
   reduced-motion). Without JS or with reduced motion everything is static
   and fully visible. ---- */
@media (prefers-reduced-motion: no-preference) {{
  html.anim .reveal {{ opacity:0; transform:translateY(14px); }}
  html.anim .reveal.in {{ opacity:1; transform:none;
    transition:opacity 420ms var(--tt-ease), transform 420ms var(--tt-ease);
    transition-delay:var(--rd,0ms); }}
  html.anim .hl {{ background-repeat:no-repeat; background-size:0% 100%;
    animation:hlsweep 640ms cubic-bezier(.2,.7,.2,1) 300ms forwards; }}
  html.anim .bar {{ transform-box:fill-box; transform-origin:bottom;
    transform:scaleY(0);
    transition:transform 520ms cubic-bezier(.2,.7,.2,1);
    transition-delay:calc(var(--i,0)*4ms); }}
  html.anim .skyplay .bar {{ transform:scaleY(1); }}
  html.anim .pt {{ transform-box:fill-box; transform-origin:center;
    opacity:0; transform:scale(.3);
    transition:opacity 300ms cubic-bezier(.2,.7,.2,1), transform 300ms cubic-bezier(.2,.7,.2,1);
    transition-delay:calc(200ms + var(--i,0)*30ms); }}
  html.anim .scplay .pt {{ opacity:.9; transform:scale(1); }}
  html.anim .scplay .pt.hot {{ opacity:1; }}
  html.anim .diag, html.anim .plbl {{ opacity:0; transition:opacity 400ms ease-out; }}
  html.anim .scplay .diag {{ opacity:.7; }}
  html.anim .scplay .plbl {{ opacity:1; transition-delay:900ms; }}
}}
@keyframes hlsweep {{ to {{ background-size:100% 100%; }} }}
</style>

<div class="wrap">
<div class="brandrow"><img src="data:image/png;base64,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" alt="Defensive Pedal">
<div><div class="bn">Defensive Pedal</div><div class="bt">Research</div></div></div>
<p class="eyebrow">European Cycling Risk Ranking · 2026</p>
<h1>Streets, <span class="hl">Not&nbsp;Reputations</span></h1>
<p class="dek">We scored <b>67&nbsp;million road segments</b> across <b>{N} European cities</b> with a
risk model validated against 1,169 serious cycling injuries — then ranked every city, 1st to last.
No votes. No policy points. Just the streets as they are built.</p>

<div class="figure">{skyline}
<div class="legend"><span><span class="sw grad" style="background:linear-gradient(90deg,var(--g0),var(--g3))"></span>Tier 1 · safest</span>
<span><span class="sw grad" style="background:linear-gradient(90deg,var(--y0),var(--y3))"></span>Tier 2 · middle</span>
<span><span class="sw grad" style="background:linear-gradient(90deg,var(--r0),var(--r3))"></span>Tier 3 · riskiest</span></div>
<p class="figcap">All {N} cities in rank order. Bar height is the index (0–100, higher = lower
assessed risk); colour is the tier, and the shade deepens as assessed risk rises within it.
Hover any bar.</p></div>

<h2>The top ten</h2>
<div class="plates">{top10}</div>
<p class="figcap">The number beside each city is its index; the interval is where it lands in 90%
of 2,000 re-runs of the method with perturbed assumptions.</p>


<div class="prose">
<h2>How a street gets its score</h2>
<p>Underneath the city ranking is a score for every public road in 31 countries —
67&nbsp;million of them. A street is scored on how it is actually built and used:
its speed limit (including the legal default where none is signed), how much car
traffic our model estimates it carries, how many lanes it has, whether heavy trucks
are allowed, whether there is a protected bike track or just paint, how it is lit
and surfaced, and what it forces a rider to do at junctions and crossings. All of it
is read from open map data and our own data layers — no surveys, no opinions.</p>
</div>

<div class="howgrid">
<div class="howcard hc1"><div class="hc-title">The quiet side street</div>
<div class="chips"><span class="chip">30 km/h</span><span class="chip">protected track</span>
<span class="chip">calm traffic</span><span class="chip">no trucks</span></div>
<p class="hc-verdict v1">Scores at the safe end — the kind of street a network should be made of.</p></div>
<div class="howcard hc2"><div class="hc-title">The ordinary high street</div>
<div class="chips"><span class="chip">50 km/h</span><span class="chip">painted lane, at best</span>
<span class="chip">steady traffic</span><span class="chip">parked cars</span></div>
<p class="hc-verdict v2">The middle of the scale — rideable, but it depends on the rider being careful.</p></div>
<div class="howcard hc3"><div class="hc-title">The urban arterial</div>
<div class="chips"><span class="chip">2×2 lanes</span><span class="chip">heavy traffic</span>
<span class="chip">trucks allowed</span><span class="chip">nothing for bikes</span></div>
<p class="hc-verdict v3">The risky end — where the serious injuries concentrate.</p></div>
</div>

<div class="prose">
<p>Does the score mean anything? We checked it against reality: <b>4&nbsp;billion
measured bicycle passages</b> and 1,169 serious injuries across 13 European regions.
On streets our model puts at the risky extreme, riders are seriously hurt roughly
<b>twice as often per ride</b> as on the streets it calls safe. It is also not an
academic exercise — the same score plans safer routes in the Defensive Pedal app
every day.</p>
<p>The exact weights are proprietary — they are the product. The ingredients and
their directions are not: slower is safer, separation is safer, traffic and trucks
are not. And a city cannot lobby its way up the table — the score only moves when
the street does.</p>
</div>

<div class="prose">
<h2>Three questions, one rank</h2>
<p>A city's rank comes from asking the same three questions of all 219 cities —
weighted 40/30/30 — of the streets themselves.</p>
</div>

<div class="dims">
<div class="dimcard"><div class="dimbadge">40%</div>
<div class="dim-title">How risky are its streets?</div>
<p class="dim-body">Every kilometre of street, averaged — plus a separate check on
how much of the network sits in the highest-risk band, so a city cannot bury a few
terrible arterials inside a pleasant average.</p></div>
<div class="dimcard"><div class="dimbadge">30%</div>
<div class="dim-title">How risky is a typical journey?</div>
<p class="dim-body">We simulate 210 everyday trips per city — from where people
actually live to shops, schools and work — planned by the same router that guides
real riders, then score the streets those routes touch. Only what the router can
find counts; reputation cannot help a city here.</p></div>
<div class="dimcard"><div class="dimbadge">30%</div>
<div class="dim-title">Can daily life happen on calm streets?</div>
<p class="dim-body">For every populated square kilometre: what share of residents
can reach daily destinations on a <i>connected</i> low-stress network? Calm islands
that connect to nothing count for little — a network counts when it joins up.</p></div>
</div>

<div class="prose">
<p>Each question is answered identically in every city, from one snapshot of the
model. The three answers are then combined, the scale is set by the 219 themselves,
and the whole method is re-run 2,000 times with perturbed assumptions — the wobble
from those re-runs is the interval printed beside every rank.</p>
</div>
<div class="prose">
<h2>Five results that will start arguments</h2>
<ol class="arglist">
<li><b>Stockholm is first — and we audited our own headline before publishing it.</b><br>
No famous ranking puts Stockholm on the podium; the new Copenhagenize Index has it 26th. So we
stress-tested our own result. It held: 64% of Stockholm's street network is explicitly signed at
30&nbsp;km/h — Dutch levels (Amsterdam: 73%, Copenhagen: 6%) — its speed-limit tagging is 94%
complete, its street density matches Copenhagen's, and it carries ~2,000&nbsp;km of separated
cycleways, the largest such network of any peer. Its one soft spot is a very low modelled traffic
load — plausibly real, given two decades of congestion charging — and even if we triple that
penalty to the peer level, Stockholm still finishes on the podium. What we won't claim: that it
beats Helsinki. The two are one point apart with overlapping intervals. Top of the leading
cluster — that, the data supports.</li>
<li><b>The cycling capitals are top-20, not top-3.</b><br>
Amsterdam 9th. Paris 11th. Utrecht 14th. Copenhagen 17th. All world-class — and all measurably
closer to the chasing pack than their reputations suggest. We don't score culture, mode share or
ambition. On pure network risk, the gap has closed more than the folklore has.</li>
<li><b>Nobody celebrates Vantaa and Espoo. The data does.</b><br>
Helsinki's suburbs rank 6th and 8th, above almost every famous cycling city in Europe. Fame-based
indices never test suburbs. A risk model doesn't know what a suburb is — it just measures the
paths, and Finland built them everywhere.</li>
<li><b>Where rankings disagree, the injury data picks a side — ours.</b><br>
Copenhagenize puts <span class="hotword">Bordeaux 9th</span>; we put it 116th — and Bordeaux has
the <i>worst measured serious-injury rate of any French city in our outcome panel</i> (4.0 per 10M
passages vs Paris's 1.9). They put <span class="hotword">Zurich 21st</span>; we put it 135th — and
Zurich has the worst injury rate in the entire panel (7.4). Indices that reward policy momentum
measure ambition. We measure asphalt. In both checkable disagreements, the crash data sides with
the asphalt.</li>
<li><b>The bottom of the table is where the work is.</b><br>
{ro_last20} of the last 20 cities are Romanian — Bucharest ranks {by_slug["bucharest"]["rank"]},
Timișoara {by_slug["timisoara"]["rank"]}, Brăila {N}th of {N}. That reads brutal, and it is. It is
also, for the first time, <i>measured</i> — segment by segment, on the same scale as Stockholm.
A gap you can measure is a gap you can close.</li>
</ol>

<h2>Us vs. the famous ranking</h2>
<p>The Copenhagenize Index 2025 scores infrastructure <i>plus usage plus policy</i>. We score risk
only. The two agree far more than they disagree (rank correlation 0.47 across their European top
30; 19 of their 27 European cities are in our top 50) — and where they don't, see argument #4.</p>
</div>

<div class="figure">{scatter}
<p class="figcap">Each dot is one of the 27 European cities in the Copenhagenize 2025 top 30.
On the dashed line, the two rankings agree. Below it, we rank the city higher; above it, lower.
<span class="hotword">Orange</span>: the two disagreements where independent injury data exists —
it supports the risk model in both.</p></div>

<div class="prose">
<h2>Why you can trust it</h2>
</div>
<div class="tiles">
<div class="tile"><div class="big">0.50</div><div class="what">Rank correlation with measured
bicycle commuting share across 156 cities (Eurostat) — exactly the pre-registered validation
target, on par with the best published city indices.</div></div>
<div class="tile"><div class="big">0.79</div><div class="what">Serious-injury rate ratio per +10
index points across 2.6&nbsp;billion measured cyclist passages (p&nbsp;&lt;&nbsp;0.001): higher-ranked
cities really do hurt fewer riders.</div></div>
<div class="tile"><div class="big">2,000</div><div class="what">Re-runs of the entire method with
perturbed weights and goalposts behind every rank. The interval printed next to each city is
where it lands in 90% of them.</div></div>
</div>


<div class="appcta reveal-cta">
  <div class="appcta-txt">
    <div class="appcta-h">Don&rsquo;t just read the ranking &mdash; ride it.</div>
    <p>Defensive Pedal plans bike routes that minimize risk, using the exact same
    score behind this page. Free on iOS and Android.</p>
  </div>
  <div class="storebtns"><a href="https://apps.apple.com/ro/app/defensive-pedal/id6778694757" target="_blank" rel="noopener"><svg width="16" height="19" viewBox="0 0 384 512" fill="currentColor" aria-hidden="true"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg> App Store</a><a href="https://play.google.com/store/apps/details?id=com.defensivepedal.mobile" target="_blank" rel="noopener"><svg width="17" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg> Google Play</a></div>
</div>
<div class="prose">
<div class="caveat"><b>What we won't claim.</b> Two cities with overlapping intervals are a tie —
read the intervals, not just the places: Stockholm's #1 means "top of the leading cluster", not
"beats Helsinki". Once you control for country, the injury association is inconclusive (five
countries of outcome data can't separate a city from its nation). Rankings that carry no caveats
are marketing.</div>

<h2>The full ranking</h2>
<p class="figcap">* = straddles a tier boundary under re-specification. Index 0–100, higher =
lower assessed risk. Interval = 90% rank range over 2,000 re-runs.</p>
</div>
<div class="tblwrap"><table>
<thead><tr><th>#</th><th>City</th><th>Index</th><th>Interval</th></tr></thead>
<tbody>{table}</tbody>
</table></div>

<div class="citycta" id="forcities">
  <div class="citycta-inner">
    <h2 class="citycta-h">For the cities on this list</h2>
    <p class="citycta-p">Every city here can get what this page only summarizes: a
    street-by-street diagnosis of where its cycling risk lives and what drives it
    &mdash; the same decomposition behind this ranking. We work with municipalities
    on three things: <b>street-level diagnosis</b> (which streets, which factor,
    what to fix first), <b>an interactive risk map of your city</b>
    (<a href="https://map.defensivepedal.com/bucuresti/" target="_blank"
    rel="noopener">see the live Bucharest sample</a>), and <b>before/after
    measurement</b> of what you build &mdash; because a gap you can measure is a
    gap you can close, and re-measure.</p>
    <div class="citycta-act">
      <a id="citymail" class="citycta-btn" href="#forcities">Email us about your city</a>
      <span class="citycta-addr" id="citymail-addr">victor [at] defensivepedal [dot] com</span>
    </div>
  </div>
</div>

<div class="foot">
<p><b>Work for a city?</b> Street-level cycling intelligence for your municipality &mdash; <a href="#forcities">get in touch</a>.</p>
<p><b>Method in one line:</b> every scored road segment of the production Defensive Pedal risk
model (the one that plans real routes today) is aggregated per city across three pillars — street
network risk, the risk of 210 simulated journeys, and low-stress accessibility — normalised on the
{N}-city sample and stress-tested 2,000 times. Roads above 80&nbsp;km/h and carriageways with a
mandatory parallel path don't count against a city's streets; cities are official municipal
boundaries.</p>
<p>Full technical report, criterion analysis and every caveat:
<a href="https://victorwho.github.io/european-cycling-risk-ranking/report/">The European
Cycling Risk Study</a> (open access, DOI 10.5281/zenodo.22771452) · Defensive Pedal Research, 2026.
Study archived at DOI <a href="https://doi.org/10.5281/zenodo.22771452">10.5281/zenodo.22771452</a> (CC-BY-4.0).
External reference: <a href="https://www.eiturbanmobility.eu/the-copenhagenize-index-2025-eit-urban-mobility-edition-reveals-the-best-bicycle-friendly-cities/">Copenhagenize
Index 2025 — EIT Urban Mobility Edition</a>.</p>
</div>
</div>


<div id="cta" hidden>
  <button id="cta-head" aria-expanded="true">
    <span>Get Defensive Pedal</span><span id="cta-chev">&#9662;</span>
  </button>
  <div id="cta-body">
    <p>Ride on routes that minimize risk with <strong>Defensive Pedal</strong>&nbsp;&mdash;
    the app that uses this same safety algorithm.</p>
    <div class="storebtns"><a href="https://apps.apple.com/ro/app/defensive-pedal/id6778694757" target="_blank" rel="noopener"><svg width="16" height="19" viewBox="0 0 384 512" fill="currentColor" aria-hidden="true"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg> App Store</a><a href="https://play.google.com/store/apps/details?id=com.defensivepedal.mobile" target="_blank" rel="noopener"><svg width="17" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg> Google Play</a></div>
  </div>
</div>
<div id="tip"></div>
<script>
(function () {{
  var tip = document.getElementById("tip");
  document.addEventListener("mousemove", function (e) {{
    var t = e.target;
    if (t && t.getAttribute && t.getAttribute("data-n")) {{
      tip.innerHTML = "<b>" + t.getAttribute("data-n") + "</b>" + t.getAttribute("data-v");
      tip.style.opacity = 1;
      var x = Math.min(e.clientX + 14, window.innerWidth - 270);
      tip.style.left = x + "px";
      tip.style.top = (e.clientY + 16) + "px";
    }} else {{
      tip.style.opacity = 0;
    }}
  }});
}})();
</script>

<script>
(function () {{
  if (!("IntersectionObserver" in window)) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var doc = document.documentElement;
  doc.classList.add("anim");
  // failsafe: whatever happens, nothing stays hidden
  setTimeout(function () {{
    document.querySelectorAll(".reveal").forEach(function (el) {{ el.classList.add("in"); }});
    document.querySelectorAll("svg").forEach(function (s) {{ s.classList.add("skyplay", "scplay"); }});
  }}, 4000);

  // index the skyline bars and scatter points for their staggers
  var svgs = Array.prototype.slice.call(document.querySelectorAll("svg"));
  var sky = null, sc = null;
  svgs.forEach(function (s) {{
    if (s.querySelector(".bar")) sky = s;
    if (s.querySelector(".pt")) sc = s;
  }});
  if (sky) sky.querySelectorAll(".bar").forEach(function (b, i) {{ b.style.setProperty("--i", i); }});
  if (sc) sc.querySelectorAll(".pt").forEach(function (d, i) {{ d.style.setProperty("--i", i); }});

  // reveal groups with sibling stagger
  var groups = [".plates .plate", ".howgrid .howcard", ".dims .dimcard", ".arglist > li", ".tiles .tile", ".appcta", ".caveat", ".citycta"];
  groups.forEach(function (sel) {{
    document.querySelectorAll(sel).forEach(function (el, i) {{
      el.classList.add("reveal");
      el.style.setProperty("--rd", (i * 45) + "ms");
    }});
  }});

  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (!e.isIntersecting) return;
      var t = e.target;
      if (t === sky) t.classList.add("skyplay");
      else if (t === sc) t.classList.add("scplay");
      else if (t.classList.contains("reveal")) t.classList.add("in");
      else if (t.classList.contains("big")) countUp(t);
      io.unobserve(t);
    }});
  }}, {{ threshold: 0.2, rootMargin: "0px 0px -5% 0px" }});

  document.querySelectorAll(".reveal").forEach(function (el) {{ io.observe(el); }});
  if (sky) io.observe(sky);
  if (sc) io.observe(sc);

  // stat tiles count up (tabular-nums prevents layout shift)
  function countUp(el) {{
    var raw = el.textContent.trim();
    var target = parseFloat(raw.replace(/,/g, ""));
    if (!isFinite(target)) return;
    var dec = (raw.split(".")[1] || "").length;
    var grouped = raw.indexOf(",") >= 0;
    var t0 = null, DUR = 900;
    function frame(ts) {{
      if (!t0) t0 = ts;
      var k = Math.min(1, (ts - t0) / DUR);
      k = 1 - Math.pow(1 - k, 3);
      var v = target * k;
      el.textContent = grouped ? Math.round(v).toLocaleString("en-US")
                               : v.toFixed(dec);
      if (k < 1) requestAnimationFrame(frame);
      else el.textContent = raw;
    }}
    requestAnimationFrame(frame);
  }}
  document.querySelectorAll(".tile .big").forEach(function (el) {{ io.observe(el); }});
}})();
</script>

<script>
(function () {{
  var cta = document.getElementById("cta");
  if (!cta) return;
  var KEY = "dpCtaOpen";
  var open = sessionStorage.getItem(KEY) === "1";
  function apply() {{
    cta.classList.toggle("closed", !open);
    document.getElementById("cta-head").setAttribute("aria-expanded", open ? "true" : "false");
  }}
  apply();
  document.getElementById("cta-head").addEventListener("click", function () {{
    open = !open;
    try {{ sessionStorage.setItem(KEY, open ? "1" : "0"); }} catch (e) {{}}
    apply();
  }});
  // appear after the reader has actually engaged (one screen of scroll)
  var shown = false;
  function maybeShow() {{
    if (shown) return;
    if (window.scrollY > window.innerHeight * 0.8) {{
      shown = true;
      cta.hidden = false;
      window.removeEventListener("scroll", maybeShow);
    }}
  }}
  window.addEventListener("scroll", maybeShow, {{ passive: true }});
  maybeShow();
}})();
</script>

<script>
(function () {{
  // assemble the address at runtime so scrapers reading HTML never see it
  var u = "victor", d = "defensivepedal.com", addr = u + "@" + d;
  var subject = "Cycling intelligence for [your city]";
  var body = "City:\nYour role:\nInterested in: street-level diagnosis / "
           + "interactive risk map / before-after measurement\n\n";
  var a = document.getElementById("citymail");
  if (a) a.href = "mailto:" + addr + "?subject=" + encodeURIComponent(subject)
               + "&body=" + encodeURIComponent(body);
  var t = document.getElementById("citymail-addr");
  if (t) t.textContent = addr + " — we answer personally.";
}})();
</script>
"""

open(OUT, "w", encoding="utf-8").write(html)
print(f"wrote {OUT} ({len(html):,} chars)")
