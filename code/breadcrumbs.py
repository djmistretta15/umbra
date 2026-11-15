# Umbra breadcrumb and ratio tests. Executed inside constraints.py (shares its namespace:
# g, ramp, add, bare, rh, bio1, bio12, elev, relief, sand, soc, ice, land, LAT, LON, windm, vap, H, W, MOON, MARS).
# Each test: the Moon or Mars left a record (breadcrumb); Earth's erasers (water, life, tectonics, people) destroy
# records; the test finds where Earth keeps the same record, or where the same governing ratio holds.
import numpy as np
NL = np.load(f"{D}/new/layers.npz")
def L_(k): return np.nan_to_num(NL[k].astype(float), nan=0.0)
def norm99(a):
    v = a[land & (a > 0)]
    return a / (np.percentile(v, 99) if v.size else 1)
el = np.where(elev < -1000, np.nan, elev)
P12 = np.nan_to_num(bio12, nan=0); T1 = np.nan_to_num(bio1, nan=0)
noice = np.where(ice, 0.0, 1.0)
hyper = 1 - ramp(P12, 20, 250)
arid = 1 - ramp(P12, 100, 800)
bas, pyro, evap, carb = L_("lith_basalt"), L_("lith_pyroclastic"), L_("lith_evaporite"), L_("lith_carbonate")
bplut, meta, aplut = L_("lith_basic_plutonic"), L_("lith_metamorphic"), L_("lith_acid_plutonic")
sedi = L_("lith_unconsolidated") + L_("lith_siliciclastic")
vb, va = norm99(NL["volc_basaltic"]), norm99(NL["volc_all"])
quake = np.log10(1 + norm99(NL["quakes"]) * 100) / 2          # 0 quiet .. ~1 most active
met = NL["meteor_found"]; imp = norm99(NL["impacts"])
playa = NL["playa"].astype(float); km_town = NL["km_to_town"]; mag = np.nan_to_num(NL["mag_abs"], nan=0)

SCALE = {}   # key -> scale on the ladder
def B(key, score, scale, **kw):
    add(key, score=score, **kw); SCALE[key] = scale

# ---------------- underground ----------------
B("lava_tubes", 100 * ramp(bas, .3, .9) * ramp(vb, .02, .4) * arid * noice, "Underground",
  title="Lava tubes and caves in young basalt", world="Moon & Mars", stage="Habitat",
  why="Lava tubes could shelter crews from radiation, impacts and temperature swings. Robots must learn to find, enter and map them.",
  gap="Earth tubes are younger, wetter and smaller; lunar tubes may be far wider in low gravity.", conf="Medium")
MOON["lava_tubes"] = "LRO cameras have mapped about 300 lunar pits, 16 of them in mare basalt; some open into voids that may be lava tubes (Wagner and Robinson)."
MARS["lava_tubes"] = "Orbiter images show pit chains and skylight-like holes on the flanks of Mars's big shield volcanoes."
B("karst_caves", 100 * ramp(carb + evap, .3, .9) * ramp(relief, 100, 800) * noice, "Underground",
  title="Caves for robots without GPS or light", world="Moon & Mars", stage="Mobility and navigation",
  why="Inside a cave a robot has no sun, no GPS and no radio link. It must navigate by what it senses itself.",
  gap="These caves are dissolved limestone and salt, not lava; useful for the robot, not the geology.", conf="Low")

# ---------------- rock ----------------
B("mare_basalt", 100 * ramp(bas, .4, .95) * (1 - ramp(relief, 100, 700)) * bare * arid * noice, "Rock",
  title="Dark basalt plains like the lunar maria", world="Moon & Mars", stage="Mines and roads",
  why="The lunar maria and most of Mars's crust are basalt. Excavators, sintered pads and oxygen extraction should be tested on it.",
  gap="Earth basalt is weathered and often soil-covered; lunar mare basalt is bone-dry and fresh under regolith.", conf="Medium")
MOON["mare_basalt"] = "The dark lunar maria are basalt lava plains; Apollo 11, 12, 15 and 17 sampled them."
MARS["mare_basalt"] = "TES and other orbiter spectrometers show much of Mars's dark surface is basaltic."
B("highland_rock", 100 * ramp(bplut, .2, .8) * bare * noice, "Rock",
  title="Pale gabbro-family rock like the lunar highlands", world="Moon", stage="Mines and roads",
  why="The bright lunar highlands are anorthosite. The closest mapped class on Earth is gabbro and related deep-cooled rock.",
  gap="The global map lumps anorthosite with gabbro; true anorthosite massifs need a finer map.", conf="Low")
MOON["highland_rock"] = "Apollo 16 returned highland anorthosite; 69 meteorites in NASA's catalogue are classed lunar anorthosite."
B("impact_rock", 100 * ramp(imp, .05, .6) * arid, "Rock",
  title="Impact-shocked rock", world="Moon & Mars", stage="Science",
  why="Craters are the main landform on the Moon and Mars. Shocked rock and impact melt are what samples will mostly be.",
  gap="Earth keeps only about 200 confirmed craters, most eroded or buried; the Moon and Mars keep millions.", conf="Low")

# ---------------- minerals and molecules ----------------
B("volcanic_glass", 100 * ramp(pyro, .15, .7) * arid * bare * noice, "Mineral",
  title="Volcanic ash and glass beads", world="Moon & Mars", stage="Mines and processing",
  why="Apollo 17's orange soil was volcanic glass beads, a candidate feedstock for oxygen. Ash fields test handling and processing.",
  gap="Earth ash weathers to clay within thousands of years; lunar glass beads are billions of years old.", conf="Medium")
B("salt_biosig", 100 * np.maximum(ramp(evap, .1, .6), playa * .8) * hyper, "Life",
  title="Salt deposits that preserve traces of life", world="Mars", stage="Science",
  why="Salt can trap and preserve organic molecules and microbes for very long times. It is a prime place to look for past life.",
  gap="Earth salt flats hold living microbes today; Mars salt would hold only ancient traces, if any.", conf="Medium")
MARS["salt_biosig"] = "Mars Odyssey's THEMIS camera found about 640 chloride salt deposits across the ancient southern highlands (Osterloo et al. 2010)."
uv = ramp(np.nan_to_num(el, nan=0), 1000, 4500) * np.cos(np.radians(LAT)) ** 2
B("oxidant_soil", 100 * (1 - ramp(P12, 2, 60)) * uv * bare * noice, "Molecule",
  title="Soil that destroys organic molecules", world="Mars", stage="Science",
  why="Mars soil chemistry and UV break down organics, so a life-detection instrument can miss what is there. Test it where the same happens.",
  gap="Earth's ozone blocks the harshest UV; oxidants form more slowly here.", conf="Low")
MARS["oxidant_soil"] = "NASA's Phoenix lander found perchlorate, a strong oxidant, in Mars soil in 2008."
B("hydrothermal", 100 * ramp(va, .05, .5) * hyper * bare, "Life",
  title="Volcanic heat and water in dry land", world="Mars", stage="Science",
  why="Hot springs build silica crusts that lock in traces of life. Spirit found silica-rich deposits on Mars that may have formed this way.",
  gap="Earth springs are active and alive today; Mars deposits are billions of years old.", conf="Low")

# ---------------- time, planet and reader ----------------
B("ancient_crust", 100 * ramp(meta + aplut, .5, .95) * (1 - ramp(P12, 50, 400)) * (1 - ramp(relief, 200, 1200)) * bare * noice, "Time",
  title="Ancient exposed crust in dry land", world="Moon & Mars", stage="Science",
  why="Most of the Moon's surface is over 3 billion years old. Earth's oldest exposed shields hold its earliest record.",
  gap="Rock type is a proxy for age; the map does not date the rock.", conf="Low")
B("seismic_quiet", 100 * (1 - ramp(quake, .1, .6)) * ramp(bas + meta + aplut + bplut, .3, .8) * ramp(km_town, 30, 300) * noice, "Planet",
  title="Seismically quiet bedrock", world="Moon & Mars", stage="Science",
  why="Seismometers read a planet's interior. They are tested best on solid rock far from earthquakes and people.",
  gap="Earth's oceans and weather make background noise that the Moon does not have.", conf="Medium")
MARS["seismic_quiet"] = "NASA's InSight seismometer recorded 1,319 marsquakes before the mission ended in 2022."
B("magnetic_memory", 100 * ramp(mag, 150, 700), "Planet",
  title="Rock with strong fossil magnetism", world="Moon & Mars", stage="Science",
  why="Mars and the Moon lost their global magnetic fields, but some rocks kept the old magnetism. It is a record of an ancient planetary core.",
  gap="Earth still has an active field that dwarfs crustal anomalies; instruments must subtract it.", conf="Medium")
MARS["magnetic_memory"] = "Mars Global Surveyor mapped strong crustal magnetic fields, mostly in the ancient southern highlands."
B("radio_quiet", 100 * ramp(km_town, 100, 900), "Reader",
  title="Far from people, signals and contamination", world="Moon & Mars", stage="Science",
  why="Mars is minutes away by radio, so robots must decide alone; samples must stay free of Earth life. Test where people barely reach.",
  gap="Distance to towns is a proxy; it does not measure radio noise directly.", conf="Low")
B("dried_lakes", 100 * playa * (1 - ramp(P12, 50, 400)), "Water history",
  title="Dried ancient lake beds", world="Mars", stage="Science",
  why="Mars had lakes and river deltas, such as Jezero crater where Perseverance landed. Dry lake beds on Earth keep the same kind of layered record.",
  gap="Earth lake beds dried thousands of years ago; Mars's dried billions of years ago.", conf="Medium")

# ---------------- the ratio lens (similitude) ----------------
# Sand: wind strength relative to what it takes to lift a grain (Bagnold threshold), u*/u*t.
rho = 1.225 * np.exp(-np.nan_to_num(el, nan=0) / 8500) * 288 / (273.15 + np.nan_to_num(bio1_air, nan=0))
d = 2.5e-4
ust_t = 0.1 * np.sqrt((2650 - rho) / rho * 9.81 * d)
ust = 0.4 * np.nan_to_num(windm, nan=0) / np.log(10 / 1e-4)
R_earth = ust / ust_t
R_mars = 0.40 / (0.1 * np.sqrt((2650 - 0.020) / 0.020 * 3.71 * d))     # assumes typical Mars u* ~0.4 m/s
RATIO = {"sand": dict(mars=float(R_mars), earth_median=float(np.nanmedian(R_earth[land])))}
B("sand_ratio", 100 * ramp(sand, 60, 90) * (1 - ramp(P12, 50, 300)) * np.exp(-np.log(np.maximum(R_earth, 1e-3) / R_mars) ** 2 / (2 * .25 ** 2)), "Ratio",
  title="Sand that moves like Mars sand (ratio match)", world="Mars", stage="Mobility and navigation",
  why="On Mars, thin air means sand moves only in rare gusts. The match is not the windiest desert but sand seas where wind relative to the lift threshold is just as low.",
  gap="Matches the wind-to-threshold ratio, not grain hop height; Mars grains fly higher and longer in low gravity.", conf="Low")
MARS["sand_ratio"] = f"Lifting a 0.25 mm grain takes about {0.1*np.sqrt((2650-0.02)/0.02*3.71*d):.1f} m/s friction speed on Mars vs {float(np.nanmedian(ust_t[land])):.2f} on Earth. With typical Mars winds the ratio is about {R_mars:.2f}; Earth's median is {RATIO['sand']['earth_median']:.2f}."
# Ice: frost point of the air vs mean ground temperature. Ice lasts in the ground where they are about equal.
e = np.maximum(np.nan_to_num(vap, nan=.01), 1e-3); x = np.log(e / 0.6112)
Tf = 272.62 * x / (22.46 - x)
dT = Tf - T1
B("ice_ratio", 100 * np.exp(-(dT / 3) ** 2) * ramp(-T1, 5, 20) * (1 - ramp(P12, 50, 400)) * noice, "Ratio",
  title="Ground ice balanced like Mars ice (ratio match)", world="Mars", stage="Mines",
  why="On Mars, ground ice lasts where the air's frost point equals the ground's mean temperature. The match is where the same balance holds, with almost no snow to resupply it.",
  gap="Earth's balance also depends on summer melt and snow, which Mars lacks.", conf="Low")
MARS["ice_ratio"] = "Mars mid-latitude ground ice sits near this balance line, which is why it is found shallow there (Phoenix dug into it at 68N)."
RATIO["mobility"] = dict(note="NASA's Scarecrow test rover was stripped so it weighs on Earth what Curiosity weighs on Mars: the ratio lens already used for wheels.")

# ---------------- the headline: where Earth's erasers are off ----------------
eras_water = 1 - ramp(P12, 20, 600)
eras_life = 1 - ramp(np.nan_to_num(soc, nan=0), 2, 40)
eras_tect = 1 - ramp(quake, .1, .7)
eras_people = ramp(km_town, 20, 300)
ERASERS_OFF = 100 * eras_water * eras_life * eras_tect * eras_people
B("erasers_off", ERASERS_OFF, "Process",
  title="Earth's erasers switched off", world="Moon & Mars", stage="Science",
  why="Water, life, earthquakes and people erase Earth's records. Where all four are weakest, Earth keeps records the way the Moon and Mars do.",
  gap="Wind and ice also erase; not yet included.", conf="Medium")
# independent check: are meteorites (breadcrumbs from space) found where the natural erasers are off?
# The people term is left out of the check: meteorites need people to find them (the reader's own bias).
import csv as _csv
NAT = eras_water * eras_life * eras_tect
pts = [(float(m["reclat"]), float(m["reclong"])) for m in _csv.DictReader(open(f"{D}/new/meteorites.csv"))
       if m["fall"] == "Found" and m["reclat"] and not (float(m["reclat"]) == 0 and float(m["reclong"]) == 0)]
pi = np.clip(((90 - np.array([p[0] for p in pts])) * 6).astype(int), 0, H - 1); pj = (((np.array([p[1] for p in pts]) + 180) % 360) * 6).astype(int) % W
ok = land[pi, pj]
landv = np.sort(NAT[land])
pct = 100 * np.searchsorted(landv, NAT[pi[ok], pj[ok]], side="right") / landv.size
METEOR_CHECK = dict(n_found=int(ok.sum()), median_pct=float(np.median(pct)), share_top10=float(np.mean(pct >= 90)),
                    share_top25=float(np.mean(pct >= 75)))
MOON["erasers_off"] = MARS["erasers_off"] = (f"Independent check with NASA's Meteorite Landings catalogue ({METEOR_CHECK['n_found']:,} finds on land, never given to the engine): "
    f"{100*METEOR_CHECK['share_top25']:.0f}% of finds lie in the top quarter of land where water, life and earthquakes are weakest (chance would give 25%). The median find sits at the {METEOR_CHECK['median_pct']:.0f}th percentile.")
print("ratios", RATIO, "meteor check", METEOR_CHECK)
