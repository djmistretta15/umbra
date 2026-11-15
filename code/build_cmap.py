import base64, json, html, sys
e = html.escape
MR = json.load(open("moon_ref.json")); MA = json.load(open("mars_ref.json"))
_C = json.load(open("cons/constraints.json")); RT = _C["ratios"]; MC = _C["meteor_check"]; NASA_E = _C["nasa_earth"]
ST = json.load(open("site_tibet.json"))
LF = json.load(open("lightflow.json")); EX = json.load(open("exposure.json")); A6 = json.load(open("analogs6.json")); LX = json.load(open("live_extra.json")); UP = json.load(open("underpriced.json"))
NMM = len(json.load(open("/home/claude/data/new/moon_mars_meteorites.json")))
def pc(x): return f"{100*x:.0f}%"
def moonline(v):
    o = f'<p class="moon"><b>Moon target (LRO data):</b> {e(v["moon"])}</p>' if v.get("moon") else ""
    if v.get("mars"): o += f'<p class="moon"><b class="r">Mars target (orbiter data):</b> {e(v["mars"])}</p>'
    return o
def img(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
C = json.load(open("cons/constraints.json")); cons = C["constraints"]; cant = C["earth_cant"]
port = json.load(open("cons/portfolio.json"))
keys = list(cons.keys())
STAGES = ["Port (landing pads)", "Power", "Power + mines", "Mobility and navigation", "Mines", "Mines and roads",
          "Mines and processing", "Habitats and life support", "Habitats and food", "All hardware"]
STEP = {"Port (landing pads)": 1, "Power": 2, "Power + mines": 2, "Mobility and navigation": 3, "Mines and roads": 4,
        "Mines": 4, "Mines and processing": 4, "Habitats and life support": 5, "Habitats and food": 5, "Habitat": 5, "All hardware": 6, "Science": 7}
STEPNAME = {1: "Port", 2: "Power", 3: "Mobility", 4: "Mines", 5: "Habitat", 6: "Endurance", 7: "Science"}
def ll(t): return f'{abs(t["lat"]):.1f}°{"N" if t["lat"] >= 0 else "S"}, {abs(t["lon"]):.1f}°{"E" if t["lon"] >= 0 else "W"}'
order = sorted(keys, key=lambda k: (STEP[cons[k]["stage"]], keys.index(k)))
num = {k: i + 1 for i, k in enumerate(keys)}
cards = []
for k in order:
    v = cons[k]
    tops = "".join(f'<tr><td class=num>{i+1}</td><td>{e(t["country"])}</td><td class=num>{ll(t)}</td><td class=num>{t["score"]:.0f}</td></tr>' for i, t in enumerate(v["top"][:5]))
    kn = [x for x in v["known"] if x["pct"] >= 90]
    kns = ", ".join(f'{e(x["name"])} ({x["pct"]:.0f}th pct)' for x in kn) or "None of the 9 known analog sites rank in the top 10% for this test."
    cards.append(f'''<article class="card" data-step="{STEP[v["stage"]]}" id="c-{k}">
<div class="ctop"><span class="no">{num[k]}</span><span class="tag">Step {STEP[v["stage"]]} · {STEPNAME[STEP[v["stage"]]]}</span><span class="pill grey">{e(v["world"])}</span><span class="pill grey">Scale: {e(v.get("scale",""))}</span><span class="pill grey">Confidence: {e(v["conf"])}</span></div>
<h3>{e(v["title"])}</h3>
<p class="why">{e(v["why"])}</p>
{moonline(v)}
<div class="two"><figure><img src="{img(f"cons/map_{k}.png")}" alt="World map of the {e(v["title"].lower())} score with the top five regions circled"></figure>
<div><table><thead><tr><th>#</th><th>Country</th><th>Location</th><th>Score</th></tr></thead><tbody>{tops}</tbody></table>
<p class="small"><b>Known analog sites in the top 10%:</b> {kns}</p></div></div>
<p class="gap"><b>Will not carry over:</b> {e(v["gap"])}</p>
</article>''')
ports = "".join(f'<tr><td class=num>{abs(p["lat"]):.0f}°{"N" if p["lat"]>=0 else "S"}, {abs(p["lon"]):.0f}°{"E" if p["lon"]>=0 else "W"}</td><td class=num>{p["count"]}</td><td>{e("; ".join(p["tests"]))}</td></tr>' for p in port[:8])
legend = "".join(f'<li><a href="#c-{k}"><span class="no sm">{num[k]}</span>{e(cons[k]["title"])}</a></li>' for k in keys)

SCALES = ["Planet", "Air", "Terrain", "Underground", "Rock", "Mineral", "Molecule", "Life", "Water history", "Time", "Process", "Ratio", "Reader"]
EXTRA = [  # dimensions without a global map yet: (scale, dimension, status, how)
 ("Planet", "Gravity (1/6 Moon, 3/8 Mars)", "Ratio rule", "No site lowers gravity. Match the ratio instead: lighten the test vehicle, as NASA's Scarecrow rover does for Curiosity."),
 ("Planet", "Vacuum", "Earth can't", "Thermal-vacuum chambers."),
 ("Planet", "Day length (Mars sol 24 h 39 min)", "Proxy", "Crews and robots can run on Mars time anywhere; polar summer removes the sun cue (see never-setting sun)."),
 ("Air", "Sound in thin CO2 air", "Earth can't outdoors", "Perseverance recorded Mars sound; test microphones and acoustic sensing in pressure chambers."),
 ("Air", "Electric charge on dust and plumes", "Hypothesis", "Strongest where dust storms and volcanic plumes meet dry air; links to dust storms and dust devils tests."),
 ("Terrain", "Megaflood scars (Mars outflow channels)", "Hypothesis", "Channeled Scablands, USA, and the Altai, Russia; no global flood-scar layer loaded yet."),
 ("Terrain", "Mud volcanoes (possible on Mars)", "Hypothesis", "Azerbaijan and Trinidad; no global layer loaded yet."),
 ("Terrain", "Shape fingerprint: roughness across scales", "Next", "Compare terrain roughness from metres to kilometres in LOLA, MOLA and Earth elevation data, matching geometry instead of looks."),
 ("Mineral", "Clays and sulfates (Gale, Jezero)", "Next", "NASA's EMIT mineral maps cover Earth's dry lands (needs an Earthdata login); Rio Tinto, Spain, is the known sulfate analog."),
 ("Mineral", "Surface coatings: desert varnish vs space weathering", "Proxy", "Slow coatings form on rock left alone in hyperarid land (see ancient exposed crust)."),
 ("Molecule", "Solar-wind hydrogen and helium-3 in soil", "Earth can't", "Earth's magnetic field and air block the solar wind; needs returned samples or ion-beam labs."),
 ("Life", "Life inside rock", "Hypothesis", "Antarctic Dry Valleys sandstone and Atacama salt crusts host microbes inside rock."),
 ("Life", "Deep underground life", "Hypothesis", "Deep mines (for example Kidd Creek, Canada) host deep life; no global layer."),
 ("Process", "Tilt cycles and ice ages", "Hypothesis", "Mars's polar layers record tilt cycles; Antarctic ice cores (Dome C) record Earth's."),
 ("Process", "Two-way library", "Narrative", "The Moon may hold Earth's oldest rock (Big Bertha, disputed); Earth holds lunar and Martian meteorites."),
]
SC = {k: [] for k in SCALES}
for k in keys:
    v = cons[k]; st = "Ratio test" if v.get("scale") == "Ratio" else "Map"
    SC.setdefault(v.get("scale", "Terrain"), []).append((f'<a href="#c-{k}">{e(v["title"])}</a>', st, e(v["world"])))
for s, d, st, how in EXTRA:
    SC.setdefault(s, []).append((e(d), st, e(how)))
nmap = sum(1 for k in keys); nall = nmap + len(EXTRA)
ledger = "".join(f'<tr class="sc"><th colspan="3">{e(s)}</th></tr>' + "".join(f'<tr><td>{a}</td><td><span class="st st-{st.split()[0].lower().replace(chr(39),"")}">{e(st)}</span></td><td>{c}</td></tr>' for a, st, c in SC[s]) for s in SCALES if SC.get(s))
cantrows = "".join(f'<tr><td>{e(c["title"])}</td><td>{e(c["world"])}</td><td>{e(c["why"])}</td><td>{e(c["instead"])}</td></tr>' for c in cant)
chips = '<button class="chip" data-s="0" aria-pressed="true">All steps</button>' + "".join(f'<button class="chip" data-s="{s}" aria-pressed="false">{s} · {n}</button>' for s, n in STEPNAME.items())

page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Umbra Constraint Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root {{
  /* Umbra world: night blue, low-sun amber */
  --night:#0f1424; --deep:#171e33; --line:#2a3350; --text:#e9ebf3; --muted:#9aa3bd; --amber:#f2a541; --blue:#6aa6ff; --green:#3fb68b; --bad:#e5675f; --paper:#f4f2ec;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif; --body:"IBM Plex Sans","Segoe UI",Arial,sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  color-scheme: dark;
}}
*{{box-sizing:border-box}} html,body{{margin:0;background:var(--night);color:var(--text);font:16px/1.55 var(--body)}}
.wrap{{max-width:1180px;margin:0 auto;padding:32px 20px 56px;display:grid;gap:26px}}
.team{{font:500 13px var(--mono);color:var(--amber);letter-spacing:.06em;text-transform:uppercase}}
h1{{font:800 clamp(28px,4.2vw,44px)/1.08 var(--display);margin:0;text-wrap:balance;max-width:24ch}}
h2{{font:700 22px var(--display);margin:0 0 4px;text-wrap:balance}}
.lede{{color:var(--muted);max-width:72ch;margin:0;font-size:17px}} .lede b{{color:var(--text);font-weight:600}}
.mech{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;counter-reset:m}}
.mech div{{background:var(--deep);border:1px solid var(--line);border-top:3px solid var(--amber);border-radius:10px;padding:12px 14px;font-size:14.5px;color:var(--muted)}}
.mech b{{display:block;color:var(--text);font:700 16px var(--display);margin-bottom:4px}}
figure{{margin:0;background:#fff;border-radius:10px;padding:6px}} figure img{{display:block;width:100%;height:auto;border-radius:6px}}
.ov{{display:grid;grid-template-columns:2.2fr 1fr;gap:16px;align-items:start}}
@media(max-width:880px){{.ov{{grid-template-columns:1fr}}}}
.legend{{list-style:none;margin:0;padding:0;display:grid;gap:4px;font-size:14px}}
.legend a{{color:var(--text);text-decoration:none;display:flex;gap:8px;align-items:center}} .legend a:hover{{color:var(--amber)}}
.no{{display:inline-grid;place-items:center;min-width:28px;height:28px;border-radius:50%;background:var(--amber);color:#0f1424;font:700 13px var(--mono)}}
.no.sm{{min-width:22px;height:22px;font-size:11px}}
.box{{background:var(--deep);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:0 12px 12px 0;padding:18px 20px;display:grid;gap:10px}}
.box p{{margin:0;color:var(--muted);max-width:78ch}} .box p b{{color:var(--text)}}
.chips{{display:flex;gap:8px;flex-wrap:wrap}}
.chip{{font:600 14px var(--body);color:var(--text);background:var(--deep);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}}
.chip[aria-pressed=true]{{border-color:var(--amber);color:var(--amber)}}
.chip:focus-visible,a:focus-visible{{outline:2px solid var(--amber);outline-offset:2px}}
.cards{{display:grid;gap:16px}}
.card{{background:var(--deep);border:1px solid var(--line);border-radius:12px;padding:18px 20px;display:grid;gap:10px}} .card[hidden]{{display:none}}
.ctop{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.tag{{font:500 12px var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
.pill{{font:600 12px var(--mono);border:1px solid currentColor;border-radius:999px;padding:2px 9px;white-space:nowrap}}
.pill.amber{{color:var(--amber)}} .pill.blue{{color:var(--blue)}} .pill.green{{color:var(--green)}} .pill.grey{{color:var(--muted)}}
.card h3{{font:700 21px/1.2 var(--display);margin:0}} .why{{margin:0;color:var(--muted)}}
.two{{display:grid;grid-template-columns:1.35fr 1fr;gap:16px;align-items:start}} @media(max-width:820px){{.two{{grid-template-columns:1fr}}}}
.moon{{margin:0;font-size:15px;color:var(--text)}} .moon b{{color:var(--blue);font-weight:600}} .moon b.r{{color:#ff8a65}} .gap{{margin:0;font-size:15px}} .gap b,.small b{{color:var(--amber);font-weight:600}}
.small{{font-size:13.5px;color:var(--muted);margin:8px 0 0}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;font-size:14px;width:100%}}
th{{text-align:left;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);padding:6px 12px 6px 0}}
td{{border-bottom:1px solid var(--line);padding:6px 12px 6px 0;vertical-align:top}} td.num{{font:500 13px var(--mono);white-space:nowrap;font-variant-numeric:tabular-nums}}

.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}} @media(max-width:860px){{.three{{grid-template-columns:1fr}}}}
.three ul{{margin:6px 0 0;padding-left:18px;display:grid;gap:6px;font-size:14.5px;color:var(--muted)}} .three b{{color:var(--text)}}

.small2{{margin:6px 0 0;font-size:14.5px;color:var(--muted)}} .small2 b{{color:var(--text)}}
.ledger tr.sc th{{background:#16203a;color:var(--amber);font:600 13px var(--mono);text-transform:uppercase;letter-spacing:.06em;padding:8px}}
.st{{display:inline-block;font:500 11px var(--mono);padding:2px 8px;border-radius:99px;border:1px solid var(--line);white-space:nowrap}}
.st-map{{color:var(--green);border-color:var(--green)}} .st-ratio{{color:var(--blue);border-color:var(--blue)}} .st-earth{{color:#ff8a65;border-color:#ff8a65}} .st-hypothesis,.st-next,.st-proxy,.st-narrative{{color:var(--muted)}}
.three h3{{font:700 16px var(--display);margin:0}} h3.g{{color:var(--green)}} h3.b{{color:var(--blue)}} h3.a{{color:var(--amber)}}
footer{{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;display:grid;gap:6px}} footer a{{color:var(--amber)}}
</style></head><body><div class="wrap">
<header style="display:grid;gap:10px">
<div class="team">Project Umbra · Team Forced Futures · NASA Space Apps 2026</div>
<h1>Match the physics, not the scenery</h1>
<p class="lede">No place on Earth is the Moon. So we let the Moon and Mars set each <b>constraint</b> a permanent base must survive, and let an engine find <b>the most extreme place on Earth for each one</b>, in the order a settlement has to be built: port, power, mobility, mines, habitat. Where Earth falls short, the map says so. Then it goes deeper: down the scale ladder from planet to molecule to life, and across three lenses no analog list uses: <b>ratios</b>, <b>erasers</b> and <b>breadcrumbs</b>.</p>
</header>
<section class="mech">
<div><b>1 · The Moon sets the constraint</b>Something it does to hardware, robots or people: dust, cold, night, no GPS, low sun.</div>
<div><b>2 · It becomes a recipe</b>Is the condition there, for how much of the year, and what Earth adds that the Moon lacks.</div>
<div><b>3 · The engine scores all of Earth</b>Every 18 km of land, from open NASA and Earth data. No site is picked by hand.</div>
<div><b>4 · It reports the gap</b>What won't carry over to the Moon, how sure we are, and what needs a chamber instead.</div>
</section>
<section class="box">
<h2>Three lenses</h2>
<div class="three">
<div><h3 class="b">1 · Ratios, not looks</h3><p class="small2">Wind tunnels don't rebuild the plane; they match the ratios that govern the flow. We do the same for planets. On Mars, thin air means sand moves only in rare gusts: wind relative to the lift threshold is about {RT["sand"]["mars"]:.2f} there, versus a median of {RT["sand"]["earth_median"]:.2f} on Earth's land. So the Mars-like dunes are not the windiest but the calmest sand seas. Ground ice works the same way: it lasts where the air's frost point equals the ground's mean temperature. NASA already uses this lens for wheels: its Scarecrow test rover weighs on Earth what Curiosity weighs on Mars. We apply it to whole sites.</p></div>
<div><h3 class="a">2 · Earth's erasers</h3><p class="small2">The Moon and Mars keep their records because nothing erases them. Earth erases constantly with water, life, earthquakes and people. The engine maps where all four are weakest. Independent check, never shown to the engine: of {MC["n_found"]:,} meteorites found on land in NASA's catalogue, <b>{100*MC["share_top25"]:.0f}% lie in the top quarter</b> of that map (chance: 25%). Meteorites are breadcrumbs from space, and they survive where Earth stops erasing.</p></div>
<div><h3 class="g">3 · Breadcrumbs both ways</h3><p class="small2">Each world keeps pages the other lost. An Apollo 14 sample, "Big Bertha", holds a 4-billion-year-old fragment that may have been blasted off the early Earth (Bellucci et al. 2019; disputed by Warren and Rubin 2020). NASA's catalogue holds {NMM} lunar and Martian meteorites found on Earth. Earth reads the Moon's record and the Moon may hold Earth's oldest. Analogs run in both directions.</p></div>
</div>
</section>
<section class="box">
<h2>What today's analog programs don't cover</h2>
<p>From NASA's publicly listed analog programs (Desert RATS, NEEMO, HERA, HI-SEAS, CHAPEA) and the challenge statement itself:</p>
<div class="tw"><table><thead><tr><th>Missing today</th><th>What this map adds</th></tr></thead><tbody>
<tr><td><b>Winter tests.</b> Field campaigns run in summer; nobody tests the 14-day lunar night, which the Odysseus lander did not survive.</td><td>Polar-night sites ranked worldwide; the Lena Delta and northern Ellesmere top the list.</td></tr>
<tr><td><b>Robot-first analogs.</b> Programs center on crews, but machines will build the base.</td><td>Tests for no GPS, no compass, featureless ground and low-sun vision.</td></tr>
<tr><td><b>A "will it translate?" measure.</b> No analog states how much of a test carries over to the Moon.</td><td>Every constraint lists what won't carry over, with a confidence level.</td></tr>
<tr><td><b>One map from constraint to site.</b> Sites are picked program by program.</td><td>Every constraint mapped to Earth's most extreme site, plus places that cover several tests in one trip.</td></tr>
<tr><td><b>Infrastructure analogs.</b> Camps and crews, not a town.</td><td>Landing-pad ground, never-dark power ridges, the sunlit-ridge-beside-ice layout.</td></tr>
<tr><td><b>Well-characterized sites.</b> The challenge notes current sites are not entirely well characterized.</td><td>Numbers, rankings and data limits for every site.</td></tr>
</tbody></table></div>
<p><b>In one line:</b> today's analogs train crews for a visit. This map shows where Earth can test the machines and infrastructure of a permanent settlement, and where it can't.</p>
</section>
<section class="box">
<h2>The Moon sets the targets: real NASA lunar maps</h2>
<p>Every Moon target below comes from NASA's Lunar Reconnaissance Orbiter, read straight from the Planetary Data System: Diviner temperatures and ice depth, and LOLA laser-altimeter sunlight, permanent shadow and slope maps for the south pole, where Artemis is going. The Moon tells the engine what to aim for and how far Earth falls short.</p>
<figure><img src="{img("cons/moon_lro.png")}" alt="Three maps of the lunar south pole: annual maximum temperature, fraction of time sunlit with permanent shadow in cyan, and ground slope"></figure>
<div class="tw"><table><thead><tr><th>What the Moon data says</th><th>What it means for Earth tests</th></tr></thead><tbody>
<tr><td>{pc(MR["diviner"]["frac_avg_below_184K"])} of ground south of 80S averages colder than Earth's record low air. The coldest floors never pass {MR["diviner"]["coldest_max_K"]:.0f} K.</td><td>Earth can test cold only partway. The final step needs a vacuum chamber.</td></tr>
<tr><td>Buried ice sits under a median {MR["diviner"]["ice_buried_depth_m_pct"]["p50"]*100:.0f} cm of dry soil; it is within 1 m on {pc(MR["diviner"]["ice_within_1m_frac"])} of the polar ground.</td><td>Drill and excavation tests should hit ice in the top half metre of dry, frozen ground.</td></tr>
<tr><td>The best-lit ground is a median {MR["sunlight"]["km_lit70_to_psr_pct"]["p50"]*1000:.0f} m from permanent shadow.</td><td>The power-to-ice commute is under 1 km. The engine now demands sun and frozen ground in the same cell.</td></tr>
<tr><td>The sunniest spot is lit {pc(MR["sunlight"]["max_avg_sun_frac"])} of the time, but under 1 km² tops 70%.</td><td>Prime solar ground is tiny and contested. Earth's midnight sun reaches 50% over a year at most.</td></tr>
<tr><td>Sunny ground has a median slope of {MR["slope"]["sunlit70_median_deg"]:.0f}°; {pc(MR["slope"]["sunlit70_frac_under_10"])} of it is under 10°.</td><td>Pad and rover test sites should be gentle, not flat salt pans.</td></tr>
</tbody></table></div>
<p class="small">Slope data covers {pc(MR["slope"]["data_coverage"])} of the area at 40 m (gaps between laser tracks). Sunlight maps are LOLA-team extras, not formal PDS products.</p>
</section>
<section class="box">
<h2>Mars sets its own targets: real NASA orbiter maps</h2>
<p>The Mars tests now read from three NASA orbiter datasets in the Planetary Data System: Mars Global Surveyor's laser altimeter (MOLA, terrain and so air pressure), its thermal spectrometer (TES, what the ground is made of), and Mars Odyssey's gamma-ray spectrometer (water in the top metre).</p>
<figure><img src="{img("cons/mars_orbiters.png")}" alt="Three maps of Mars: surface air pressure, thermal inertia showing dust versus firm ground, and water content with the best base ground in amber"></figure>
<div class="tw"><table><thead><tr><th>What the Mars data says</th><th>What it means for Earth tests</th></tr></thead><tbody>
<tr><td>Half of Mars has under {MA["air"]["pressure_Pa_pct"]["p50"]:.0f} Pa of air; the deepest basin has {MA["air"]["pressure_Pa_pct"]["max"]:.0f} Pa.</td><td>Earth's highest bare ground has about {MA["air"]["earth_to_mars_ratio_median"]:.0f} times more. Thin-air tests on Earth are a first step; the rest needs a chamber.</td></tr>
<tr><td>{pc(MA["ground"]["frac_dust_under100"])} of Mars (60S to 60N) is loose, fine dust; {pc(MA["ground"]["frac_sand_150_400"])} is sand or crusted soil.</td><td>The data triggered a new test the engine did not have: deep loose dust, not sand. Its top Earth sites are in the central Sahara.</td></tr>
<tr><td>Even the dry low latitudes hold a median {MA["water"]["equator_30_median"]:.0f}% water by weight, locked in minerals and salts.</td><td>Water-extraction tests should use salty, bone-dry soil, not just ice.</td></tr>
<tr><td>Only {pc(MA["base_zone"]["frac_of_mars"])} of the mapped area has water above 5%, thicker air and firm ground within 50° of the equator.</td><td>Base ground on Mars is as scarce as sunlit rims on the Moon: the same bottleneck, on another world.</td></tr>
</tbody></table></div>
<p class="small">Pressure is estimated from MOLA height with an 11 km scale height and is an annual average. The gamma-ray water map covers about 57S to 57N in 5° bins; ice-rich ground nearer the poles is outside it. Thermal inertia under 100 is read as loose dust (Putzig and Mellon 2007).</p>
</section>
<section class="box" id="lightflow">
<h2>New analog type: paths and hubs, decided by the Moon</h2>
<p>A base is not one spot. It is power, ice, landing ground and the roads between them. On Earth, water carves the paths and cities form where they meet. On the Moon, light does the carving. We let physics alone route {LF["summary"]["trips"]:,} random trips across the south pole: the cost of each metre is the energy to drive it (rolling resistance plus climbing, from LOLA slope) divided by the energy the Sun supplies there (LOLA average sunlight). Slopes over {LF["summary"]["max_slope_deg"]:.0f}° are closed. Nobody chose a site.</p>
<figure><img src="{img("cons/moon_lightflow.png")}" alt="Map of the lunar south pole with sunlight in grey, permanent shadow in blue, travel corridors in orange and twelve numbered hub rings"></figure>
<div class="tw"><table><thead><tr><th>What the flow found</th><th>What it means</th></tr></thead><tbody>
<tr><td>Traffic squeezes into {pc(LF["summary"]["corridor_share_of_area"])} of the ground. Those corridors get {LF["summary"]["corridor_mean_sun"]/LF["summary"]["map_mean_sun"]:.1f} times the average sunlight and are gentler ({LF["summary"]["corridor_mean_slope"]:.0f}° vs {LF["summary"]["map_mean_slope"]:.0f}°).</td><td>The Moon has natural roads: lit, gentle bands. Road and rover tests should copy their sun and slope, not just the terrain.</td></tr>
<tr><td>{LF["summary"]["hubs_near_artemis"]} of the {LF["summary"]["n_hubs"]} hubs are closest to Shackleton or de Gerlache, craters that anchor NASA Artemis III candidate regions (2022 and 2024 lists). The strongest cluster lies between Shackleton and de Gerlache, where NASA's 2022 list placed two regions on the ridge that joins them.</td><td>Physics, with no human input, lands in the same neighbourhood NASA's site team chose. That is the validation.</td></tr>
<tr><td>Every hub is within {max(h["km_to_shadow_ice"] for h in LF["hubs"]):.1f} km of permanent shadow, where ice is trapped.</td><td>Hubs are where sun, gentle ground and ice meet: the lunar NYC. Earth layout analogs should keep all three within a few km.</td></tr>
</tbody></table></div>
<div class="tw"><table><thead><tr><th>Hub</th><th>Where</th><th>Sunlight</th><th>Slope</th><th>To shadow (ice)</th><th>Nearest named feature</th></tr></thead><tbody>
{"".join(f'<tr><td>{k+1}</td><td>{-h["lat"]:.2f}S, {h["lon"]:.1f}E</td><td>{pc(h["sun"])}</td><td>{h["slope_deg"]:.0f}°</td><td>{h["km_to_shadow_ice"]} km</td><td>{e(h["near"])}{" (Artemis III candidate area)" if h["artemis_feature"] else ""}</td></tr>' for k, h in enumerate(LF["hubs"][:6]))}
</tbody></table></div>
<p class="small">240 m grid from LOLA AVGVISIB, LPSR and LDSM, 85S to the pole; NASA's candidates further north (Malapert, Mons Mouton, Nobile, Cabeus) are outside this map. Rolling resistance 0.15 and the 25° limit are Apollo rover values. Earth visibility for radio is not yet in the cost; it needs a horizon model from LOLA elevation. Feature names: IAU / USGS Gazetteer of Planetary Nomenclature.</p>
</section>
<section class="box" id="underpriced">
<h2>Underpriced analogs: five jobs, credited for none</h2>
<p>Markets sometimes price an asset for one use while it quietly does five. Analog sites work the same way. We counted, for every 2° block of Earth, how many of Umbra's {UP["n_layers"]} analog layers it ranks in the top 3% on (its <b>jobs</b>), and how many of the challenge's dimensions those jobs span. Then we discounted each block by how close it sits to the analog sites already studied. What is left is value nobody has priced in.</p>
<figure><img src="{img("cons/underpriced.png")}" alt="World map of underpriced analog value with the top ten blocks ringed in the Sahara, Arabia and the edges of the Tibetan Plateau, and already-studied analog sites marked with blue crosses"></figure>
<div class="tw"><table><thead><tr><th>#</th><th>Block (nearest town)</th><th>Jobs</th><th>Dimensions</th><th>To nearest studied site</th></tr></thead><tbody>
{"".join(f'<tr><td>{k+1}</td><td>{e(t["near"])}{" (on the Tibetan Plateau, Aksai Chin)" if t["near"].startswith("Hotan") else ""}<br><span class="small">{t["lat"]:.0f}°, {t["lon"]:.0f}°</span></td><td class="n">{t["jobs"]}</td><td class="n">{t["dimensions"]}</td><td class="n">{t["km_to_studied_site"]:,} km</td></tr>' for k, t in enumerate(UP["top_underpriced"][:8]))}
</tbody></table></div>
<div class="three">
<div><h3 class="g">Northern Chad, 11 jobs</h3><p>Dust storms, dust devils, deep dust, dirty panels, landing-pad rock, flat featureless ground, big temperature swings, oxidizing soil, magnetized rock, ringing bedrock, and impact rock (the Aorounga craters sit here). Six of the nine dimensions, almost 3,000 km from any studied analog site.</p></div>
<div><h3 class="b">The studied sites, for comparison</h3><p>{", ".join(f'{e(x["site"])} {x["jobs"]}' for x in UP["studied_sites"][:6])}. The famous sites earn their fame on depth of study, not breadth: several blocks nobody visits do more jobs at once.</p></div>
<div><h3 class="a">Read it carefully</h3><p>Jobs are counted per 2° block (about 220 km), so they may sit in different spots inside it. Ice-covered ground is outside the engine, which is why the Dry Valleys score low here though they are superb for what they do. Attention is measured by distance to well-known sites, not by papers published.</p></div>
</div>
</section>
<section class="box" id="systems">
<h2>System analogs: Earth is already running pieces of the Moon's future</h2>
<p>An analog does not have to be a place. Each Moon bottleneck below comes from our forced-futures map of what a lunar base must solve. Next to it is an Earth system that already lives with that problem every day, and the Umbra places where it could be stress-tested in Moon-like conditions. Life support comes first, because it is the one that cannot fail.</p>
<div class="tw"><table><thead><tr><th>Moon bottleneck</th><th>Earth system already living it</th><th>Stress-test it where (from Umbra)</th><th>What transfers / what does not</th></tr></thead><tbody>
<tr><td><b>The air must balance</b>: every breath of CO2 out, oxygen in, in a sealed volume</td><td>Nuclear submarines (sealed for months, oxygen split from water, CO2 scrubbed); refuge chambers in underground mines; Biosphere 2, whose oxygen fell when its concrete and soil microbes absorbed it</td><td>Dirty-panel and dust-storm Sahara (dust loading on air filters); work-in-the-shadows Yakutia (deep cold on seals)</td><td>Transfers: control loops, failure modes. Does not: gravity-driven airflow and sedimentation of dust</td></tr>
<tr><td><b>Every drop circles back</b>; on the Moon the same ice is also rocket fuel</td><td>Water-reuse plants that return wastewater to drinking water (Orange County, Singapore NEWater); Antarctic station grey-water recycling</td><td>Hyperarid sterile ground (Atacama, northern Chad), where no water can be topped up</td><td>Transfers: membranes, monitoring, public trust. Does not: the trade-off between drinking water and propellant</td></tr>
<tr><td><b>Food is grown with electricity</b>: calories per watt</td><td>Vertical farms; DLR's EDEN ISS greenhouse at Antarctica's Neumayer III station</td><td>Two-weeks-of-night and low-sun sites (Svalbard, Northern Ellesmere) where food must be grown through darkness</td><td>Transfers: yield per watt, lighting, crop choice. Does not: partial gravity, radiation on seeds</td></tr>
<tr><td><b>Small ecosystems tip over</b></td><td>Biosphere 2; closed aquaculture and hydroponic systems</td><td>Any Umbra site with a sealed test habitat; the test is the loop, not the ground</td><td>Transfers: monitoring and early warning. Does not: the full isolation of a Moon base</td></tr>
<tr><td><b>Microbes in the walls; quarantine has nowhere to go</b></td><td>Biofilm control in hospital water systems; outbreak playbooks on cruise ships, submarines and Antarctic winter-over crews</td><td>Winter-over sites (Concordia, Eureka) and remote blocks from the underpriced list</td><td>Transfers: cleaning, detection, isolation. Does not: microgravity-boosted germs</td></tr>
<tr><td><b>For crews, power is breath</b></td><td>Hospitals and data centres with tiered backup power and load shedding</td><td>Two-weeks-of-night sites; power-ridge sites with near-constant sun</td><td>Transfers: priorities and switching. Does not: 14-day nights with no grid to fall back on</td></tr>
<tr><td><b>Living sealed, underground, with everything shipped in</b></td><td>SNOLAB: a clean-room laboratory 2 km down a working nickel mine in Sudbury, Canada, with all air and supplies coming down one shaft</td><td>Lava tubes and caves (Saudi harrats, the top underpriced block near At Taif)</td><td>Transfers: clean operations, shaft logistics, radiation shielding by rock. Does not: vacuum outside the walls</td></tr>
</tbody></table></div>
<h3>Borrowed senses: Earth sensors already built for another job</h3>
<ul>
<li><b>Wastewater surveillance.</b> Cities sequence sewage to spot outbreaks early. In a sealed base the water loop is the sewer: sequencing it is an outbreak alarm before anyone feels sick.</li>
<li><b>Handheld ultrasound.</b> Built for medicine; also checks habitat walls, welds and pressure tanks, and gives robots touch.</li>
<li><b>Car lidar.</b> Built for driving; the answer to landing and roving in low, blinding sun.</li>
<li><b>Oil-field geophones and archaeology ground radar.</b> Built to find oil and ruins; the tools for buried ice and lava tubes.</li>
<li><b>Electronic noses from food safety.</b> Built to smell spoilage; early warning of contaminants and fires in sealed air.</li>
</ul>
</section>
<section class="box" id="operations">
<h2>New analog type: operations, the problems Artemis must solve</h2>
<p>Six rehearsal sites for jobs a crew will actually do, each built from data and physics, not a list someone wrote. All six are also live layers in Umbra Live, where they can be mixed with any data a user drops in.</p>
<figure><img src="{img("cons/analogs6.png")}" alt="Six world maps: landing-blast ground, dirty solar panels, work in the shadows, radio shadow, the walk back, and oxygen-plant feedstock, each with its top five regions ringed"></figure>
<div class="tw"><table><thead><tr><th>Analog</th><th>Why it matters</th><th>Earth's top regions</th></tr></thead><tbody>
{"".join(f'<tr><td><b>{e(o["title"])}</b></td><td>{e(o["why"])}<br><span class="small">{e(o.get("moon") or o.get("mars") or "")}</span></td><td>{"<br>".join(e(t["place"]) for t in A6[o["key"]]["top"][:3])}</td></tr>' for o in LX["ops"])}
</tbody></table></div>
<p>Two of these connect straight back to the Moon data. <b>The walk back</b> compares Earth's slopes with the corridors Umbra's light-flow found on the Moon, measured the same way over 5 km with LOLA elevation; its top regions include western Tibet and the Atacama, both already on our expedition list. <b>Oxygen-plant feedstock</b> puts three of its top five in Saudi Arabia's lava fields (harrats), where our mare-basalt test also ranked Harrat Khaybar first.</p>
<p class="small">Terrain from AWS Terrain Tiles (SRTM-based) at about 2.4 km; lunar slopes from LOLA LDEM_80S_80M. Dust deposition is NASA MERRA-2 via GIBS and saturates in the dustiest deserts. Winter shade is computed at solstice noon. Radio shadow uses 7 degrees, about the highest the Earth climbs in the south-polar sky.</p>
</section>
<section class="box" id="exposure">
<h2>New analog type: exposure, the hidden chemistry</h2>
<p>Suits, seals and electronics fail on the Moon and Mars from slow chemistry, not just use: UV breaks plastics, daily temperature swings crack joints, charged dust sticks and abrades. We ranked Earth's ice-free land on four NASA layers at once (POWER surface UV, MODIS day-night swing, MERRA-2 dust and POWER rainfall) to find where gear left outside ages fastest in the same ways.</p>
<figure><img src="{img("cons/exposure.png")}" alt="World map of the exposure score with top regions ringed in the central Sahara and Arabia and fresh volcanic glass sites marked in the Andes"></figure>
<div class="three">
<div><h3 class="g">All four at once</h3><ul>{"".join(f"<li>{e(t['place'])}: {t['swing_C']:.0f} °C daily swing, {t['rain_mm']:.0f} mm rain a year</li>" for t in EX["combined_top"][:4])}</ul><p class="small">The central Sahara around Tibesti and Murzuq, then southern Arabia. Northern Chad is also on our portfolio list.</p></div>
<div><h3 class="b">Fresh volcanic glass</h3><ul>{"".join(f"<li>{e(t['place'])}</li>" for t in EX["fresh_glass_top"][:4])}</ul><p class="small">Volcanoes active since 1900 in bone-dry ground: sharp, unweathered glass, the nearest Earth gets to freshly broken lunar dust.</p></div>
<div><h3 class="a">Where it breaks down</h3><ul><li>Earth's highest yearly UV (around {EX["earth_max"]["uv_index"]:.1f} on POWER's daily-average index, in the Atacama and Altiplano) is still filtered by ozone and air. Moon and Mars surfaces get unfiltered UV.</li><li>No Earth surface matches space radiation.</li><li>The dust map tops out at its highest colour band (90+ µg/m³), so the Sahara's peak is a floor, not a measurement.</li></ul></div>
</div>
</section>
<section class="ov">
<figure><img src="{img("cons/overview.png")}" alt="World map with one numbered pin for the most extreme Earth site of each constraint"></figure>
<div><h2>{len(keys)} constraints, one best site each</h2><ul class="legend">{legend}</ul></div>
</section>
<section class="box">
<h2>One expedition, many tests</h2>
<p>With every scale added, the engine counts, for each 2° block, how many tests it is in Earth's top 3% for. <b>Northern Chad around the Borkou plains: nine</b>, from landing-pad rock and deep loose dust to impact rock (the Aorounga craters) and soil that destroys organic molecules. <b>Western Tibet (Changtang and Aksai Chin): eight</b>, including cold Moon dust, Mars-thin air, sterile ground, big day-night swings, dust devils and caves. <b>The Atacama around Yungay and the salt flats: eight</b>, from salt that preserves life traces to soil that destroys organic molecules. <b>The McMurdo Dry Valleys: seven</b>, the cold, dry, frozen-ground set. <b>Saudi Arabia's lava fields: seven</b>, with lunar-style basalt plains and lava tubes. <b>The Axel Heiberg area of the Canadian High Arctic: seven</b>, and <b>northern Ellesmere around Eureka Sound: six</b>, the winter tests no summer campaign can run, including the two-week night. The Atacama, Dry Valleys and Axel Heiberg are already analog sites: the engine found them unprompted. Northern Chad, western Tibet and the Saudi lava fields are not used today.</p>
<div class="tw"><table><thead><tr><th>Region (2° block)</th><th>Tests</th><th>Top 3% for</th></tr></thead><tbody>{ports}</tbody></table></div>
</section>
<section class="box" id="tibet">
<h2>Site profile: western Tibet at 1 km</h2>
<p>The 18 km engine points to a region; this profile zooms to about 1 km to name the spot. It re-scores the region's tests (thin air, cold ground, day-night swing, flat ground, loose sediment, limestone or salt nearby) using NASA MODIS ground temperature, SRTM-based terrain and the USGS rock-type map, then keeps spots within reach of a mapped road. Across the box ({ST["region"]["box"][0]} to {ST["region"]["box"][1]}N, {ST["region"]["box"][2]:.0f} to {ST["region"]["box"][3]:.0f}E), {100*ST["region"]["share_above_4800"]:.0f}% of the ground is above 4,800 m and {100*ST["region"]["share_flat_under5"]:.0f}% slopes less than 5°.</p>
<figure><img src="{img("cons/site_tibet.png")}" alt="Two maps of western Tibet: where the region's tests overlap at 1 km with three numbered spots, and NASA MODIS day-night ground temperature swing"></figure>
<div class="tw"><table><thead><tr><th>#</th><th>Where</th><th>Height, slope</th><th>Ground (MODIS)</th><th>Rock</th><th>Access</th></tr></thead><tbody>
{"".join(f'<tr><td>{k+1}</td><td>{s["lat"]:.2f}N, {s["lon"]:.2f}E<br><span class="small">{s["km_to_lake"]} km from {e(s["nearest_lake"])}</span></td><td>{s["elev_m"]:,} m, {s["slope_deg"]}°</td><td>mean {s["ground_mean_C"]:.0f} °C, swings {s["swing_C"]:.0f} °C a day, coldest nights {s["coldest_night_C"]:.0f} °C</td><td>{e(s["rock"])}</td><td>{s["km_to_road"]} km to a mapped road</td></tr>' for k, s in enumerate(ST["sites"]))}
</tbody></table></div>
<div class="three">
<div><h3 class="g">How analogous</h3><ul><li>Flat plains of loose, dry, cold sediment at over 5,000 m: a place to test excavators, rovers, dust seals and landing pads together.</li><li>Ground swings of 21 to 24 °C every day, larger than on 96 to 99% of Earth's land in MODIS.</li><li>Half the air of sea level and strong UV.</li></ul></div>
<div><h3 class="a">Where it breaks down</h3><ul><li>Air: about 53 kPa at 5,200 m, roughly {MA["air"]["earth_to_mars_ratio_median"]:.0f} times Mars. Gravity, vacuum and space radiation: none.</li><li>Cold: ground averages about -3 °C; lunar crater floors stay near -246 °C.</li><li>Not sterile: summer rain, seasonal snow and sparse grassland.</li></ul></div>
<div><h3 class="b">Before going</h3><ul><li>Spots 2 and 3 lie in Aksai Chin, administered by China and claimed by India; spot 1 is in Tibet. All need permits, and foreign access is restricted.</li><li>Elevation over 5,000 m: crews need altitude planning.</li><li>Confirm surface type with high-resolution imagery before any trip.</li></ul></div>
</div>
</section>
<section class="box">
<h2>What the engine found: rediscovered, new use, new</h2>
<p>We checked every top site against published analog research. Rediscovered sites prove the engine works: it found them without being told. "Not found" means not found in our searches, not proof that nobody has proposed it.</p>
<div class="three">
<div><h3 class="g">Rediscovered</h3><ul>
<li><b>Qaidam Basin, Tibet</b>: published Mars analog (Xiao et al. 2017)</li>
<li><b>Axel Heiberg Island</b>: McGill Arctic Research Station, Mars analog science</li>
<li><b>North Greenland near Thule</b>: LUNARK Moon habitat test (2020)</li>
<li><b>Namib Sand Sea</b>: studied as a Mars dune analog</li>
<li><b>Pinacate and Gran Desierto, Mexico</b>: Apollo astronaut training, 1965 to 1970</li>
<li><b>Antarctic plateau (Concordia)</b>: ESA's "White Mars" crew-isolation analog</li>
<li><b>Lanzarote, Canary Islands</b>: ESA's PANGAEA astronaut training, including its lava tubes (found by the lava-tube test, #4 worldwide)</li>
<li><b>Pinacate, Mexico</b> again: top 5 for both lunar-mare basalt and volcanic glass</li>
</ul></div>
<div><h3 class="b">Known place, new use</h3><ul>
<li><b>Eureka, Ellesmere Island</b>: two-week lunar night. Year-round station, airstrip and a 610 m ridge lab reachable by road in winter; used by astronomers, not space agencies.</li>
<li><b>Axel Heiberg in winter</b>: its station runs March to August, so its polar night is unused.</li>
<li><b>Antarctic plateau</b>: radiation and radiative heat-loss tests for hardware, not just crew isolation.</li>
<li><b>Gran Desierto and Namib dunes</b>: soft-sand traps for rover escape tests.</li>
<li><b>Harrat Khaybar, Saudi Arabia</b>: home of Umm Jirsan, Arabia's longest known lava tube (about 1.5 km), studied by archaeologists, not as a lunar-tube robot test site.</li>
</ul></div>
<div><h3 class="a">Apparently new</h3><ul>
<li><b>Western Tibet (Changtang, Aksai Chin)</b>: five constraints at once, at about 5,000 m</li>
<li><b>Verkhoyansk and Chersky ranges, Siberia</b>: robot vision in low sun</li>
<li><b>Mackenzie Mountains, Yukon</b>: low-sun navigation</li>
<li><b>Oymyakon region, Siberia</b>: deep cold, about a quarter of the way to crater cold</li>
<li><b>Severnaya Zemlya, Russian Arctic</b>: no usable compass</li>
<li><b>Tian Shan high peaks</b>: highest cosmic-ray exposure on ice-free ground</li>
<li><b>Calm southern Namib and Namaqualand sands</b>: the best match for how rarely Mars sand moves (ratio test)</li>
</ul></div>
</div>
</section>
<div class="chips" role="group" aria-label="Filter by build step">{chips}</div>
<section class="cards">{"".join(cards)}</section>
<section class="box" id="ledger">
<h2>Every dimension, accounted for: {nall} in all</h2>
<p>Down the scale ladder from planet to molecule to life. {nmap} are mapped worldwide by the engine; the rest are named with their status, so nothing is dropped silently. "Map" and "Ratio test" link to their cards.</p>
<div class="tw"><table class="ledger"><thead><tr><th>Dimension</th><th>Status</th><th>World or how</th></tr></thead><tbody>{ledger}</tbody></table></div>
</section>
<section class="box">
<h2>What no place on Earth can test</h2>
<div class="tw"><table><thead><tr><th>Constraint</th><th>World</th><th>Why it matters</th><th>Test it with</th></tr></thead><tbody>{cantrows}</tbody></table></div>
</section>
<footer>
<div><b>Data:</b> NASA MODIS Terra land surface temperature, monthly day and night, 2018 to 2022, read through NASA GIBS with NASA's published colour key (ground temperature, day-night swing, coldest nights); NASA POWER precipitation (MERRA-2, bias-corrected) and cloud cover and surface albedo; WorldClim 2.1 (humidity, wind, elevation, and gap-filling where MODIS has no data); SoilGrids 2.0, ISRIC (texture, organic carbon, gravel); NASA POWER (cloud cover, surface albedo); IGRF-14 geomagnetic model via ppigrf; Natural Earth (ice and country outlines). Moon targets from NASA LRO via the Planetary Data System: Diviner polar resource product (temperature, ice depth; Paige, UCLA) and LOLA polar slope, average-sunlight and permanent-shadow maps (Mazarico and LOLA team). Mars targets from NASA PDS: MGS MOLA MEGDR topography, MGS TES thermal inertia (Putzig and Mellon 2007) and albedo, Mars Odyssey GRS water-equivalent hydrogen.</div>
<div><b>Limits:</b> 18 km climate grid; 1° cloud data; dust sharpness and pad rock are proxies from climate and soil; country names come from map outlines, not site visits. Scores rank places on Earth against each other; none reaches the Moon.</div>
<div><b>More:</b> the Umbra Analog Atlas lists caves, ocean-floor and Mars field sites with sources. AI use: code, maps and text produced with an AI assistant (Claude) under the team's direction; maps are labeled.</div>
</footer>
</div>
<script>
(function(){{var ch=document.querySelectorAll('.chip'),cs=document.querySelectorAll('.card');
ch.forEach(function(c){{c.addEventListener('click',function(){{var s=c.dataset.s;ch.forEach(function(x){{x.setAttribute('aria-pressed',x===c?'true':'false')}});
cs.forEach(function(k){{k.hidden=!(s==='0'||k.dataset.step===s)}});}})}});}})();
</script></body></html>'''
open(sys.argv[1], "w").write(page); print(len(page)//1024, "KB")
