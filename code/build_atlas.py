import html, json, sys
e = html.escape
ST = {"mapped": ("Mapped by Umbra", "good"), "mappable": ("Mappable with open data", "amber"),
      "field": ("Known field site", "blue"), "hyp": ("Hypothesis to test", "warn"), "none": ("No Earth analog", "bad")}
# (group, condition, why it matters for a permanent base, earth analogs, status, evidence[(label,url)], data[(label,url)])
E = [
 ("moon", "Sharp, cold dust on seals and joints",
  "Abrasive regolith grinds seals, joints and suit bearings, and cold makes seals stiff.",
  "High cold deserts of the Tibetan Plateau (Qaidam Basin, Changtang, Aksai Chin); Black Point Lava Flow, Meteor Crater, Mars Desert Research Station.",
  "mapped", [("Umbra seal-test results", "")], [("SoilGrids", "https://soilgrids.org/"), ("WorldClim", "https://www.worldclim.org/")]),
 ("moon", "Low sun and pitch-black shadows",
  "At the south pole the sun stays near the horizon: cameras, lidar and human eyes face glare next to total darkness.",
  "Verkhoyansk and Chersky ranges (Yakutia), Mackenzie Mountains (Yukon), Alaska Range: about 35 to 45 usable clear, snow-free days a year at best.",
  "mapped", [("NESC: sun under 7 degrees at Artemis sites", "https://ntrs.nasa.gov/api/citations/20230006313/downloads/IAASS%202023%20Paper_Final_24apr23.pdf")],
  [("NASA POWER cloud and albedo", "https://power.larc.nasa.gov/")]),
 ("moon", "Deep cold of permanently shadowed craters",
  "Crater floors near 40 K hold the ice a base wants to mine, and freeze anything that enters.",
  "Eastern Siberia reaches about 26% of the gap; the Antarctic ice sheet about 35%. The rest needs a cryogenic vacuum chamber.",
  "mapped", [("Diviner crater temperatures", "https://meetingorganizer.copernicus.org/EPSC2013/EPSC2013-864.pdf")], [("Diviner", "https://www.diviner.ucla.edu/")]),
 ("moon", "Two weeks of night",
  "Solar-powered landers have died in their first lunar night. A permanent base has to run through 14 days of dark and cold on stored power.",
  "High Arctic polar night on bare ground: Ellesmere Island near Eureka, Bathurst and Melville Islands, the Taymyr Peninsula and Lena Delta. Devon Island (Haughton Crater) is a summer analog today; its winter is the lunar-night analog nobody uses.",
  "mapped", [("Odysseus lost to the lunar night", "https://intuitivemachines.com/post/im-1-lunar-night-update-farewell-odysseus")], [("Computed from solar geometry + WorldClim", "")]),
 ("moon", "Moonquakes that ring for minutes",
  "Dry rock barely absorbs shaking, so a moonquake keeps vibrating. Habitats, landing pads and towers need to be designed for long ringing, not a short jolt.",
  "The driest, coldest ground on Earth (McMurdo Dry Valleys, hyperarid Atacama) is the closest Earth gets to water-free rock, as a testbed for long-duration vibration sensing. Earth rock is still wetter, so treat this as partial.",
  "hyp", [("Apollo seismology: long duration from dry, scattering crust", "https://ig.utexas.edu/?p=7443")], [("Apollo seismic data (NASA PDS)", "https://pds-geosciences.wustl.edu/")]),
 ("moon", "Dust that charges up and floats",
  "Sunlight charges lunar dust; at the day-night line it can lift and cling to optics, radiators and suits.",
  "Natural charged-dust settings on Earth: volcanic ash plumes and desert dust devils both build strong static charge. Useful for testing dust-repelling coatings outdoors.",
  "hyp", [("Surveyor horizon glow from levitated dust", "https://arxiv.org/pdf/1207.4965")], [("MERRA-2 dust (NASA GES DISC)", "https://disc.gsfc.nasa.gov/")]),
 ("moon", "Water that moves with the time of day",
  "Surface water molecules hop around as the ground heats, which matters for where and when to harvest it.",
  "Hyperarid places with a daily moisture cycle on bone-dry ground, like Atacama fog and dew zones.",
  "hyp", [("NASA LRO LAMP: lunar water migrates over the day", "https://www.nasa.gov/solar-system/moon/nasas-lro-sheds-light-on-lunar-water-movement/")], [("LRO LAMP data (NASA PDS)", "https://pds.nasa.gov/")]),
 ("moon", "Lava tubes as shelter",
  "Intact lava tubes give shelter from radiation, micrometeorites and temperature swings, and lunar tubes are far larger than Earth's.",
  "La Corona and Cueva de los Verdes (Lanzarote, used by ESA PANGAEA), Hawaii, Lava Beds (California), Craters of the Moon (Idaho).",
  "field", [("Lunar and Martian tubes 1-3 orders of magnitude larger", "https://phys.org/news/2020-08-lava-tubes-mars-moon-wide.pdf"), ("ESA Pangaea-X 3D scan, Lanzarote", "https://www.universetoday.com/articles/bizarre-image-3d-scan-cave-network-spain-technology-used-map-lava-tubes-moon-mars")],
  [("LROC skylight images", "https://www.lroc.asu.edu/")]),
 ("moon", "Light falling into pits and skylights",
  "Sun shining into a skylight gives a bright patch beside total darkness: the hardest lighting for robot vision.",
  "Lava-tube skylights (the jameos of Lanzarote), slot canyons, cave entrances.",
  "field", [("Skylights on Moon and Mars resemble Lanzarote jameos", "https://www.universetoday.com/articles/bizarre-image-3d-scan-cave-network-spain-technology-used-map-lava-tubes-moon-mars")], []),
 ("moon", "Magnetic swirls: natural solar-wind shields",
  "Patches of magnetized crust make mini-magnetospheres that deflect the solar wind. Worth knowing for siting and shielding.",
  "Strong crustal magnetic anomalies on Earth (for example the Kursk anomaly) as places to test the magnetometer surveys that would map them; magnetometer surveys already map lava-tube voids in Lanzarote.",
  "hyp", [("Swirls all sit on crustal magnetic anomalies (LROC)", "https://www.lroc.asu.edu/posts/925")], [("EMAG2 magnetic anomaly grid (NOAA)", "https://www.ncei.noaa.gov/products/earth-magnetic-model-anomaly-grid-2")]),
 ("moon", "Ice locked into frozen soil",
  "Mining water ice cemented into regolith fights drills and excavators differently from loose dust.",
  "Dry permafrost: McMurdo Dry Valleys, Devon Island, Svalbard, ice-rich Siberian ground.",
  "mappable", [], [("ESA CCI Permafrost", "https://climate.esa.int/en/projects/permafrost/")]),
 ("robot", "No GPS",
  "There is no satellite navigation on the Moon. A robot that quietly leans on GPS during Earth tests will fail there.",
  "Lava tubes, caves, deep slot canyons, the deep sea floor.",
  "field", [], []),
 ("robot", "No compass",
  "The Moon has no global magnetic field, so heading must come from stars, sun, terrain or inertial sensors.",
  "Near Earth's north magnetic pole, where the horizontal field is so weak that compasses become unreliable.",
  "mappable", [], [("World Magnetic Model (NOAA)", "https://www.ncei.noaa.gov/products/world-magnetic-model")]),
 ("robot", "Featureless ground that blinds navigation",
  "Visual odometry needs texture. Most of Curiosity's visual-odometry failures happened on sandy, low-feature ground.",
  "Salt flats (Salar de Uyuni), dune seas, glacier ice, smooth regolith-like plains.",
  "field", [("Curiosity VO failures mostly on low-feature sand (66 of 94)", "https://ar5iv.labs.arxiv.org/html/2207.13629")], []),
 ("robot", "Robots blinding themselves with their own dust",
  "Excavators and haulers on the Moon will kick up the fine dust that coats their own sensors.",
  "Deep-sea nodule collectors in the Clarion-Clipperton Zone already fight this: their sediment plumes reach about 10,000 times background near the vehicle and drift kilometers away.",
  "field", [("Deep-sea mining trial plume study (Nature Communications 2025)", "https://www.vliz.be/imisdocs/publications/411804.pdf")], [("ISA DeepData", "https://data.isa.org.jm/"), ("GEBCO bathymetry", "https://www.gebco.net/")]),
 ("robot", "Working in the dark on slow, thin links",
  "Robots inside shadowed craters will run with little light and limited bandwidth back to a relay.",
  "The deep sea floor: no sunlight, cold water, acoustic links that are slow and low-bandwidth. NASA already uses the Aquarius undersea lab (NEEMO) for crews; robot autonomy is the open use.",
  "field", [("NASA analog missions incl. NEEMO", "https://www.nasa.gov/wp-content/uploads/2016/04/nasa_analog_missions_2012.pdf")], []),
 ("mars", "Methane that comes at night and spikes",
  "Curiosity sees methane near the ground at night but not in daytime from orbit, plus sudden spikes. A gas source matters for both life and fuel.",
  "Gas-emission craters in Siberian permafrost (Yamal, Gydan), where trapped methane blows out; seafloor methane seeps.",
  "hyp", [("Day-night methane at Gale (A&A 2021)", "https://www.aanda.org/articles/aa/full_html/2021/06/aa40030-20/aa40030-20.html"), ("Yamal craters from methane release (AGU)", "https://news.agu.org/press-release/new-yamal-craters-explanation/")], []),
 ("mars", "Salty brines liquid far below freezing",
  "Brines are the most likely liquid water on Mars: a resource, a contamination risk and a place to look for life.",
  "Don Juan Pond, McMurdo Dry Valleys: calcium-chloride brine liquid to about -50 C; seafloor brine pools.",
  "field", [("Don Juan Pond stays liquid to -50 C", "https://sciencedaily.com/releases/2017/11/171115155625.htm")], []),
 ("mars", "Toxic, salty, UV-baked soil",
  "Perchlorate salts and strong UV affect crops, equipment and life detection.",
  "Atacama Desert (already a NASA Mars analog).",
  "field", [("NASA: 10 things to know about planetary analogs", "https://science.nasa.gov/earth/10-things-to-know-about-planetary-analogs/")], []),
 ("mars", "Carbon dioxide geysers under seasonal ice",
  "Each spring, dry-ice slabs at the Martian south pole vent gas jets that throw dust. Hardware near the pole would face them.",
  "None. Researchers describe these processes as unlike anything on Earth; NASA JPL recreated small versions in a chamber.",
  "none", [("NASA: an active seasonal process not seen on Earth", "https://science.nasa.gov/?p=335642")], []),
 ("none", "Vacuum, low gravity, space radiation",
  "These shape every system on a base and no place on Earth reproduces them.",
  "None. Vacuum and thermal chambers, parabolic flights and neutral-buoyancy pools, and radiation beam facilities instead.",
  "none", [], []),
]
GROUPS = [("all", "All"), ("moon", "Moon"), ("robot", "Robots and AI"), ("mars", "Mars"), ("none", "No Earth analog")]
polar = json.load(open("polar_night.json"))["picks"]

def links(lst):
    out = []
    for lab, url in lst:
        out.append(f'<a href="{e(url)}">{e(lab)}</a>' if url else f"<span>{e(lab)}</span>")
    return " · ".join(out)
cards = []
for g, cond, why, earth, st, ev, data in E:
    lab, tone = ST[st]
    grp = "none" if st == "none" else g
    cards.append(f'''<article class="card" data-g="{grp}">
<div class="ctop"><span class="tag">{dict(GROUPS)[g] if g != "none" else "Moon and Mars"}</span><span class="pill {tone}">{e(lab)}</span></div>
<h3>{e(cond)}</h3>
<p class="why">{e(why)}</p>
<p class="earth"><b>Earth analog:</b> {e(earth)}</p>
{f'<p class="src"><b>Evidence:</b> {links(ev)}</p>' if ev else ''}
{f'<p class="src"><b>Data:</b> {links(data)}</p>' if data else ''}
</article>''')
counts = {k: sum(1 for x in E if x[4] == k) for k in ST}
chips = "".join(f'<button class="chip" data-f="{k}" aria-pressed="{"true" if k == "all" else "false"}">{e(v)}</button>' for k, v in GROUPS)
prow = "".join(f"<tr><td class=num>{la:.1f}°N, {abs(lo):.1f}°{'E' if lo >= 0 else 'W'}</td><td class=num>{d}</td><td class=num>{t:.0f} °C</td></tr>" for la, lo, d, t in polar[:8])

page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Umbra Analog Atlas</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root {{
  /* same world as the Umbra explorer: night blue, low-sun amber; status colors carry meaning */
  --night:#0f1424; --deep:#171e33; --line:#2a3350; --text:#e9ebf3; --muted:#9aa3bd; --amber:#f2a541;
  --good:#3fb68b; --warn:#e3b341; --bad:#e5675f; --blue:#6aa6ff;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif; --body:"IBM Plex Sans","Segoe UI",Arial,sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  color-scheme: dark;
}}
*{{box-sizing:border-box}} html,body{{margin:0;background:var(--night);color:var(--text);font:16px/1.55 var(--body)}}
.wrap{{max-width:1180px;margin:0 auto;padding:32px 20px 56px;display:grid;gap:26px}}
.team{{font:500 13px var(--mono);color:var(--amber);letter-spacing:.06em;text-transform:uppercase}}
h1{{font:800 clamp(28px,4.2vw,44px)/1.08 var(--display);margin:0;text-wrap:balance;max-width:24ch}}
.lede{{color:var(--muted);max-width:70ch;margin:0;font-size:17px}} .lede b{{color:var(--text);font-weight:600}}
h2{{font:700 22px var(--display);margin:0;text-wrap:balance}}
.sum{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}}
.s{{background:var(--deep);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:grid;gap:2px}}
.s b{{font:800 26px var(--display);font-variant-numeric:tabular-nums}} .s span{{color:var(--muted);font-size:14px}}
.s.good b{{color:var(--good)}} .s.amber b{{color:var(--amber)}} .s.blue b{{color:var(--blue)}} .s.warn b{{color:var(--warn)}} .s.bad b{{color:var(--bad)}}
.chips{{display:flex;gap:8px;flex-wrap:wrap}}
.chip{{font:600 14px var(--body);color:var(--text);background:var(--deep);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}}
.chip[aria-pressed=true]{{border-color:var(--amber);color:var(--amber)}}
.chip:focus-visible,a:focus-visible{{outline:2px solid var(--amber);outline-offset:2px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}}
.card{{background:var(--deep);border:1px solid var(--line);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:8px}}
.card[hidden]{{display:none}}
.ctop{{display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap}}
.tag{{font:500 12px var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
.pill{{font:600 12px var(--mono);border:1px solid currentColor;border-radius:999px;padding:2px 9px;white-space:nowrap}}
.pill.good{{color:var(--good)}} .pill.amber{{color:var(--amber)}} .pill.blue{{color:var(--blue)}} .pill.warn{{color:var(--warn)}} .pill.bad{{color:var(--bad)}}
.card h3{{font:700 19px/1.25 var(--display);margin:0;text-wrap:balance}}
.card p{{margin:0;font-size:15px}} .why{{color:var(--muted)}} .earth b,.src b{{color:var(--amber);font-weight:600}}
.src{{font-size:13.5px!important;color:var(--muted)}} .src a{{color:var(--text)}}
.box{{background:var(--deep);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:0 12px 12px 0;padding:18px 20px;display:grid;gap:12px}}
.box p{{margin:0;color:var(--muted);max-width:75ch}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;font-size:14px;min-width:420px}}
th{{text-align:left;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);padding:6px 18px 6px 0}}
td{{border-bottom:1px solid var(--line);padding:6px 18px 6px 0}} td.num{{font:500 13px var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
footer{{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;display:grid;gap:6px}}
</style></head><body><div class="wrap">
<header style="display:grid;gap:10px">
<div class="team">Project Umbra · Team Forced Futures · NASA Space Apps 2026</div>
<h1>What the Moon and Mars will do that Earth analog lists miss</h1>
<p class="lede">A permanent base will be built and run mostly by <b>robots and AI vehicles</b>, not just visited by astronauts. This atlas lets the Moon and Mars set the conditions, then lists the <b>Earth place that can stand in</b>, how sure we are, and the <b>open data</b> NASA can use, including the conditions where no Earth site helps.</p>
</header>
<div class="sum">
<div class="s"><b>{len(E)}</b><span>conditions in the atlas</span></div>
<div class="s good"><b>{counts["mapped"]}</b><span>mapped worldwide by Umbra</span></div>
<div class="s blue"><b>{counts["field"]}</b><span>known field sites, new use</span></div>
<div class="s amber"><b>{counts["mappable"]}</b><span>mappable with open data</span></div>
<div class="s warn"><b>{counts["hyp"]}</b><span>hypotheses to test</span></div>
<div class="s bad"><b>{counts["none"]}</b><span>no Earth analog</span></div>
</div>
<section class="box">
<h2>New finding: the lunar night has an Earth analog nobody uses</h2>
<p>The first commercial lunar lander, Odysseus, did not survive its first 14-day lunar night. Bare, cold ground with at least two weeks of no sunrise exists across the High Arctic. Devon Island, home of NASA-linked Haughton Crater research in summer, is inside this zone: its winter is the lunar-night test site.</p>
<div class="tw"><table><thead><tr><th>Top region (approx.)</th><th>Days with no sunrise</th><th>Coldest month</th></tr></thead><tbody>{prow}</tbody></table></div>
<p style="font-size:13px">Days from solar geometry (no refraction), on ice-free cells with soil data; coldest-month mean low from WorldClim. Regions: Lena Delta, Olenyok and Taymyr (Siberia); Ellesmere, Axel Heiberg, Melville, Bathurst and Devon Islands (Canadian Arctic).</p>
</section>
<div class="chips" role="group" aria-label="Filter">{chips}</div>
<div class="grid">{"".join(cards)}</div>
<footer>
<div><b>Status key:</b> Mapped by Umbra = scored for all of Earth's land. Known field site = place exists and is used, here proposed for a new test. Mappable = global open data exists, not yet scored. Hypothesis = physics suggests the analog; needs a field check. No Earth analog = chamber, flight or simulation only.</div>
<div><b>AI use:</b> research summaries, code and page produced with an AI assistant (Claude) under the team's direction. Every link points to the source behind the claim.</div>
</footer>
</div>
<script>
(function(){{var chips=document.querySelectorAll('.chip'),cards=document.querySelectorAll('.card');
chips.forEach(function(c){{c.addEventListener('click',function(){{var f=c.dataset.f;
chips.forEach(function(x){{x.setAttribute('aria-pressed',x===c?'true':'false')}});
cards.forEach(function(k){{k.hidden=!(f==='all'||k.dataset.g===f)}});}})}});}})();
</script></body></html>'''
open(sys.argv[1], "w").write(page)
print(len(E), "entries", counts)
