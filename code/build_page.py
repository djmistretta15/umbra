import base64, json, sys, html
out = sys.argv[1]
def img(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
M = {k: img(f"out/{k}.png") for k in ["map_seal", "map_lowsun", "map_cold", "verification"]}

TESTS = [
 {"id": "seal", "tab": "Dust on seals", "verdict": "Earth can", "tone": "good", "img": M["map_seal"],
  "q": "Where does Earth have sharp, dry, lifeless dust that is also cold, like the regolith that grinds lunar seals and joints?",
  "stats": [("Top 1-2%", "where NASA's own Arizona and Utah test sites rank, found blind"),
            ("#1", "Qaidam Basin, already proposed by researchers as a Mars analog"),
            ("5 km", "soil grid (SoilGrids), 18 km climate grid (WorldClim)")],
  "rows": [("Qaidam Basin, Tibetan Plateau", "37.6 N, 94.8 E", "27.8", "3,009 m, coldest month -21 C"),
           ("Changtang, western Tibet", "33.9 N, 83.1 E", "27.6", "5,023 m, coldest month -26 C"),
           ("Kumkol Basin, Altun Shan", "37.9 N, 90.9 E", "24.3", "2,982 m"),
           ("Aksai Chin / eastern Ladakh", "32.9 N, 79.4 E", "23.4", "4,590 m"),
           ("Kumtag Desert, Gansu", "40.9 N, 94.9 E", "22.5", "1,658 m"),
           ("Northern Kunlun foothills", "37.1 N, 84.8 E", "21.5", "3,388 m")],
  "gap": "Dust sharpness is inferred from how the dust formed (dryness, low clay, frost shattering), not measured grain by grain. A geology layer for glacial and volcanic ground would firm it up."},
 {"id": "lowsun", "tab": "Low-sun navigation", "verdict": "Barely", "tone": "warn", "img": M["map_lowsun"],
  "q": "Where does the sun stay as low as at the lunar south pole (under 7 degrees) with clear sky and dark ground, so cameras and eyes face the same glare and long shadows?",
  "stats": [("1 in 6", "low-sun days on Earth that are both clear and snow-free; the rest are cloudy or snow-bright"),
            ("60%", "median cloud cover during those days"),
            ("~35-45", "usable days a year at the very best sites")],
  "rows": [("Mackenzie Mountains, Yukon", "64.9 N, 131.1 W", "15.8", "34 usable days of 80"),
           ("East Greenland coast", "66.6 N, 35.6 W", "15.8", "24 of 87"),
           ("Alaska Range", "63.4 N, 146.4 W", "13.0", "16 of 68"),
           ("Verkhoyansk Range, Yakutia", "66.6 N, 127.1 E", "12.8", "42 of 87"),
           ("Chersky Range, Yakutia", "65.6 N, 138.8 E", "11.2", "38 of 85"),
           ("Chukotka interior", "65.9 N, 175.1 E", "10.4", "41 of 88")],
  "gap": "Earth's air scatters light into shadows. On the Moon there is no air and shadows go black. No field site reproduces that: it needs a chamber or simulation. Cloud and brightness data are 1-degree tiles (about 110 km)."},
 {"id": "cold", "tab": "Deep cold", "verdict": "About a third", "tone": "bad", "img": M["map_cold"],
  "q": "How close does any place on Earth get to the floor of a permanently shadowed lunar crater, which stays near 40 K (about -233 C)?",
  "stats": [("26%", "of the gap reached by the coldest ice-free ground (eastern Siberia)"),
            ("35%", "on the Antarctic ice sheet, which is ice, not regolith"),
            ("~2/3", "of the Moon's cold that no field site covers")],
  "rows": [("Oymyakon region, Yakutia", "63.3 N, 143.3 E", "26.1", "coldest month -50 C"),
           ("Central Yakutia", "65.3 N, 135.4 E", "26.0", "-49 C"),
           ("Lena Delta coast", "71.4 N, 135.1 E", "25.5", "-48 C"),
           ("Upper Yana basin", "68.4 N, 133.4 E", "25.3", "-48 C"),
           ("Olenyok basin", "68.6 N, 118.1 E", "25.2", "-47 C"),
           ("Ellesmere Island highlands", "79.8 N, 91.3 W", "24.7", "-46 C")],
  "gap": "Scored on the average low of the coldest month, not record lows. Even Earth's record (-89 C at Vostok) closes under half the gap. Deep cold belongs in a cryogenic vacuum chamber."},
]
KNOWN = [("Mars Desert Research Station, Utah", "99", "0", "10"), ("Black Point Lava Flow, Arizona", "99", "0", "8"),
         ("Meteor Crater, Arizona", "98", "0", "9"), ("Craters of the Moon, Idaho", "89", "0", "11"),
         ("Atacama Desert, Chile", "88", "0", "3"), ("Rio Tinto, Spain", "68", "0", "4"),
         ("Mauna Kea, Hawaii", "46*", "0", "5"), ("Haughton Crater, Devon Island", "0*", "92", "22"),
         ("McMurdo Dry Valleys, Antarctica", "0*", "91", "20"), ("Bockfjord, Svalbard", "0", "90", "14"),
         ("Askja, Iceland", "0", "86", "9")]
COND = [("Sharp, dry dust", "yes", "yes", "Field site", "good"), ("Ice mixed into soil", "cold traps", "yes", "Field site", "good"),
        ("Chemically harsh, salty soil", "", "yes", "Field site", "good"), ("Steep, rocky terrain", "yes", "yes", "Field site", "good"),
        ("Isolation and radio delay", "1.3 s", "up to 20+ min", "Field site", "good"),
        ("Big daily temperature swings", "crater rims", "about 80 C", "Partly", "warn"), ("Strong UV", "yes", "yes", "Partly", "warn"),
        ("Low sun, black shadows", "yes", "", "Barely", "warn"), ("Deep cold", "40 K", "yes", "About a third", "bad"),
        ("Low air pressure", "vacuum", "0.6% of Earth", "Chamber only", "bad"), ("Low gravity", "1/6 g", "3/8 g", "Flight only", "bad"),
        ("Space radiation", "yes", "yes", "Chamber or flight", "bad")]
e = html.escape
def stats(t): return "".join(f'<div class="stat"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in t["stats"])
def rows(t): return "".join(f"<tr><td>{e(a)}</td><td class=num>{e(b)}</td><td class=num>{e(c)}</td><td>{e(d)}</td></tr>" for a, b, c, d in t["rows"])
panels = "".join(f'''
<section class="panel" id="p-{t["id"]}" role="tabpanel" aria-labelledby="t-{t["id"]}" {"" if i == 0 else "hidden"}>
  <div class="phead"><p class="q">{e(t["q"])}</p><span class="pill {t["tone"]}">{e(t["verdict"])}</span></div>
  <div class="stats">{stats(t)}</div>
  <figure class="map"><img src="{t["img"]}" alt="World map of the {e(t["tab"].lower())} score"></figure>
  <div class="split">
    <div><h3>Top regions the engine found</h3><div class="tw"><table><thead><tr><th>Region (approx.)</th><th>Location</th><th>Score</th><th>Detail</th></tr></thead><tbody>{rows(t)}</tbody></table></div></div>
    <div class="gapbox"><h3>What the map can't tell you</h3><p>{e(t["gap"])}</p></div>
  </div>
</section>''' for i, t in enumerate(TESTS))
tabs = "".join(f'<button role="tab" id="t-{t["id"]}" aria-controls="p-{t["id"]}" aria-selected="{"true" if i == 0 else "false"}" data-id="{t["id"]}">{e(t["tab"])}<small class="{t["tone"]}">{e(t["verdict"])}</small></button>' for i, t in enumerate(TESTS))
known = "".join(f"<tr><td>{e(a)}</td><td class=num>{b}</td><td class=num>{c}</td><td class=num>{d}</td></tr>" for a, b, c, d in KNOWN)
cond = "".join(f'<tr><td>{e(a)}</td><td>{e(b) or "-"}</td><td>{e(c) or "-"}</td><td><span class="pill sm {t}">{e(d)}</span></td></tr>' for a, b, c, d, t in COND)

page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Umbra Analog Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root {{
  /* one visual world: deep shadow-blue night, low-sun amber as the single accent; maps sit on paper panels */
  --night: #0f1424; --deep: #171e33; --line: #2a3350; --paper: #f4f2ec;
  --text: #e9ebf3; --muted: #9aa3bd; --amber: #f2a541;
  --good: #3fb68b; --warn: #e3b341; --bad: #e5675f;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif; --body: "IBM Plex Sans", "Segoe UI", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
  color-scheme: dark;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--night); color: var(--text); font: 16px/1.55 var(--body); }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; display: grid; gap: 28px; }}
header {{ display: grid; gap: 10px; }}
.team {{ font: 500 13px var(--mono); color: var(--amber); letter-spacing: .06em; text-transform: uppercase; }}
h1 {{ font: 800 clamp(28px, 4.4vw, 46px)/1.08 var(--display); margin: 0; text-wrap: balance; max-width: 22ch; }}
.lede {{ color: var(--muted); max-width: 68ch; margin: 0; font-size: 17px; }}
.lede b {{ color: var(--text); font-weight: 600; }}
h2 {{ font: 700 22px var(--display); margin: 0 0 12px; text-wrap: balance; }}
h3 {{ font: 600 14px var(--body); color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin: 0 0 10px; }}
[role=tablist] {{ display: flex; gap: 8px; flex-wrap: wrap; }}
[role=tab] {{ font: 600 15px var(--body); color: var(--text); background: var(--deep); border: 1px solid var(--line); border-radius: 10px; padding: 10px 14px; cursor: pointer; display: grid; gap: 2px; text-align: left; }}
[role=tab] small {{ font: 500 12px var(--mono); }}
[role=tab][aria-selected=true] {{ border-color: var(--amber); box-shadow: inset 0 -3px 0 var(--amber); }}
[role=tab]:focus-visible, a:focus-visible {{ outline: 2px solid var(--amber); outline-offset: 2px; }}
small.good, .pill.good {{ color: var(--good); }} small.warn, .pill.warn {{ color: var(--warn); }} small.bad, .pill.bad {{ color: var(--bad); }}
.panel {{ display: grid; gap: 18px; }}
.panel[hidden] {{ display: none; }}
.phead {{ display: flex; gap: 16px; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; }}
.q {{ margin: 0; font-size: 18px; max-width: 70ch; }}
.pill {{ font: 600 13px var(--mono); border: 1px solid currentColor; border-radius: 999px; padding: 4px 12px; white-space: nowrap; }}
.pill.sm {{ font-size: 12px; padding: 2px 9px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.stat {{ background: var(--deep); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 4px; }}
.stat b {{ font: 800 26px var(--display); color: var(--amber); font-variant-numeric: tabular-nums; }}
.stat span {{ color: var(--muted); font-size: 14px; }}
figure {{ margin: 0; background: var(--paper); border-radius: 12px; padding: 8px; }}
figure img {{ display: block; width: 100%; max-width: 100%; height: auto; border-radius: 6px; }}
.split {{ display: grid; grid-template-columns: 1.6fr 1fr; gap: 18px; }}
@media (max-width: 760px) {{ .split {{ grid-template-columns: 1fr; }} }}
.tw {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ text-align: left; font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--line); padding: 8px 10px 8px 0; }}
td {{ border-bottom: 1px solid var(--line); padding: 8px 10px 8px 0; vertical-align: top; }}
td.num, th.num {{ font: 500 13px var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.gapbox {{ background: var(--deep); border-left: 3px solid var(--amber); border-radius: 0 10px 10px 0; padding: 14px 16px; }}
.gapbox p {{ margin: 0; color: var(--text); }}
.card {{ background: var(--deep); border: 1px solid var(--line); border-radius: 12px; padding: 20px; display: grid; gap: 14px; }}
.card > p {{ margin: 0; color: var(--muted); max-width: 72ch; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }}
@media (max-width: 860px) {{ .two {{ grid-template-columns: 1fr; }} }}
.note {{ font-size: 13px; color: var(--muted); }}
ol.method {{ margin: 0; padding-left: 20px; display: grid; gap: 8px; max-width: 72ch; }}
ol.method b {{ color: var(--amber); font-weight: 600; }}
footer {{ font-size: 13px; color: var(--muted); display: grid; gap: 6px; border-top: 1px solid var(--line); padding-top: 18px; }}
footer a {{ color: var(--amber); }}
</style></head>
<body><div class="wrap">
<header>
  <div class="team">Team Forced Futures · NASA Space Apps 2026 · Challenge: Earth analogs for Moon base sites and Mars</div>
  <h1>Where on Earth can NASA test for the Moon, and where can't it?</h1>
  <p class="lede">Every analog site fails somewhere. We let the Moon's south pole set the conditions, scored <b>all of Earth's land</b> against each one, and mapped both answers: <b>where Earth can stand in</b>, and <b>what no place on Earth can reproduce</b>, so NASA knows when a field trip stops paying off and a test chamber has to take over.</p>
</header>

<div role="tablist" aria-label="Moon tests">{tabs}</div>
{panels}

<section class="card">
  <h2>Verification: it found NASA's own sites without being told</h2>
  <p>We scored 11 analog sites already used by NASA and the analog community. Their names were never fed to the engine. On the seal test, the three sites NASA uses for lunar field tests land in the top 1 to 2% of all ice-free land. Low scores marked * are data limits, which we report instead of hiding.</p>
  <div class="two">
    <figure><img src="{M["verification"]}" alt="Bar chart of each known site's percentile on the seal test"></figure>
    <div class="tw"><table><thead><tr><th>Known site</th><th class=num>Seal pct</th><th class=num>Low-sun pct</th><th class=num>Cold %</th></tr></thead><tbody>{known}</tbody></table>
    <p class="note">Percentile among all ice-free land cells. Cold % is the share of the gap to the Moon's shadowed craters. *Mauna Kea: an 18 km cell averages its wet slopes. Haughton: the soil map overstates Arctic organics. Dry Valleys: no soil data for Antarctica.</p></div>
  </div>
</section>

<section class="card">
  <h2>The full list: what the Moon and Mars do to hardware, and whether Earth can do it too</h2>
  <p>Most analog work only lists what a site has. This table also lists what Earth cannot give you, so those risks get a chamber or a flight test instead of a field trip.</p>
  <div class="tw"><table><thead><tr><th>Condition</th><th>Moon south pole</th><th>Mars</th><th>On Earth</th></tr></thead><tbody>{cond}</tbody></table></div>
</section>

<section class="card">
  <h2>How it works</h2>
  <ol class="method">
    <li>List what acts on hardware there all the time: gravity, vacuum or thin air, sunlight, radiation, cold, the ground itself.</li>
    <li>For each test, score every 18 km patch of land on three things: are the conditions that break this test present, for how long each year, and what does Earth add that the Moon lacks (water, life, wind, cloud, snow).</li>
    <li>Every score carries its data limits, and conditions Earth cannot reproduce are reported, not dropped.</li>
  </ol>
  <p class="note">Score = presence x duration x (1 - Earth penalty). Scores compare places on Earth with each other; no site comes close to 100, because no place on Earth is the Moon.</p>
</section>

<footer>
  <div><b>Data:</b> NASA POWER (cloud amount and surface albedo, monthly climatology, 1 degree); WorldClim 2.1 (temperature, rainfall, humidity, wind, elevation, 10 arc-minute); SoilGrids 2.0, ISRIC (sand, silt, clay, organic carbon, 5 km); Natural Earth (glacier and ice-shelf outlines). Moon reference values: Diviner lunar radiometer (crater temperatures near 40 K, Sefton-Nash et al.); NASA Engineering and Safety Center paper on south pole lighting (sun under 7 degrees at Artemis sites); Apollo regolith grain sizes.</div>
  <div><b>Outside check:</b> Qaidam Basin was independently proposed as a Mars analog by Xiao et al., Earth-Science Reviews 164 (2017).</div>
  <div><b>AI use:</b> analysis code, maps and text were produced with an AI assistant (Claude) under the team's direction; all maps carry a visible label saying so.</div>
</footer>
</div>
<script>
(function () {{
  var tabs = document.querySelectorAll('[role=tab]');
  function show(id) {{
    tabs.forEach(function (t) {{
      var on = t.dataset.id === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      document.getElementById('p-' + t.dataset.id).hidden = !on;
    }});
  }}
  tabs.forEach(function (t) {{ t.addEventListener('click', function () {{ show(t.dataset.id); }}); }});
}})();
</script>
</body></html>'''
open(out, "w").write(page)
print(len(page) // 1024, "KB")
