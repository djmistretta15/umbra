"""Umbra constraint engine.

The mechanism:
  1. The Moon (or Mars) sets a constraint: something it does to hardware, robots or people.
  2. Each constraint becomes a recipe: presence (is the condition here), duration (share of the year),
     Earth penalty (what Earth adds that the Moon lacks), confidence (data quality),
     translation gap (what will not carry over), and infrastructure stage (bottleneck order).
  3. The engine scores every 18 km land cell on Earth for every recipe and returns the most
     extreme distinct regions. No site is chosen by hand.
  4. Constraints Earth cannot reproduce are kept in the registry with no Earth site.
"""
import sys, json, glob, datetime
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize

D = sys.argv[1]; G = sys.argv[2]; OUT = sys.argv[3]
g = dict(np.load(G))
H, W = g["LAT"].shape
LAT, LON = g["LAT"], g["LON"]
lat = LAT[:, 0]
land, ice, has_soil = g["land"], g["ice"], g["has_soil"]

def ramp(x, lo, hi): return np.clip((x - lo) / (hi - lo), 0, 1)
def wc(p):
    with rasterio.open(p) as r:
        a = r.read(1).astype(float); a[a < -1e30] = np.nan; return a
bio1 = wc(f"{D}/worldclim/wc_bio/wc2.1_10m_bio_1.tif")      # annual mean temp, C
bio2 = wc(f"{D}/worldclim/wc_bio/wc2.1_10m_bio_2.tif")      # mean daily temperature range, C
tavg = np.stack([wc(f"{D}/worldclim/wc_tavg/wc2.1_10m_tavg_{m:02d}.tif") for m in range(1, 13)])
prec = np.stack([wc(f"{D}/worldclim/wc_prec/wc2.1_10m_prec_{m:02d}.tif") for m in range(1, 13)])
with rasterio.open(f"{D}/soilgrids/cfvo_0-5cm_5000.tif") as r:
    src = r.read(1).astype(float); src[(src == r.nodata) | (src < 0)] = np.nan
    cfvo = np.full((H, W), np.nan)
    reproject(src, cfvo, src_transform=r.transform, src_crs=r.crs, src_nodata=np.nan,
              dst_transform=rasterio.transform.from_origin(-180, 90, 1/6, 1/6), dst_crs="EPSG:4326",
              dst_nodata=np.nan, resampling=Resampling.average)
cfvo = cfvo / 10.0   # cm3/dm3 -> % coarse fragments (gravel and rock)
rh, soc, elev, relief, sand = g["rh"], g["soc"], g["elev"], g["relief"], g["sand"]
# ---- NASA Earth observations drive the Earth side (WorldClim only fills the 2% of land MODIS misses) ----
_m = np.load(f"{D}/gibs/modis_lst.npz"); _d, _n = _m["day"].astype(float), _m["night"].astype(float)
with np.errstate(all="ignore"):
    LST_MEAN = (np.nanmean(_d, 0) + np.nanmean(_n, 0)) / 2 - 273.15      # annual mean ground temperature, C (MODIS Terra)
    LST_SWING = np.nanmean(_d - _n, 0)                                    # mean day-minus-night ground swing, C
    LST_COLD = np.nanmin(_n, 0) - 273.15                                  # coldest-month night ground temperature, C
from scipy import ndimage as _ndi
def _fillnear(a, maxd=6):          # fill MODIS gaps (lakes, coast) from the nearest MODIS cell, so sources are not mixed
    m = np.isfinite(a); dist, idx = _ndi.distance_transform_edt(~m, return_indices=True)
    return np.where(m, a, np.where(dist <= maxd, a[idx[0], idx[1]], np.nan))
LST_MEAN, LST_SWING = _fillnear(LST_MEAN), _fillnear(LST_SWING)
LST_COLD = _fillnear(_ndi.median_filter(np.where(np.isfinite(LST_COLD), LST_COLD, 99), 3))   # 3x3 median removes cloud-contaminated pixels
LST_COLD = np.where(LST_COLD > 90, np.nan, LST_COLD)
bio1_air, bio2_air = bio1.copy(), bio2.copy()
bio1 = np.where(np.isfinite(LST_MEAN), LST_MEAN, bio1)
SWING = np.where(np.isfinite(LST_SWING), LST_SWING, bio2 * 1.6)
COLD = np.where(np.isfinite(LST_COLD), LST_COLD, g["bio6"])
g["bio6"] = COLD
bio12 = np.where(land, np.load(f"{D}/power_prec/power_prec_mm_yr.npy").astype(float), np.nan)   # NASA POWER (MERRA-2 corrected)
g["bio12"] = bio12
MOON_COLD_C = json.load(open("moon_ref.json"))["diviner"]["coldest_max_K"] - 273.15
coverC = np.clip((15 - COLD) / (15 - MOON_COLD_C), 0, 1)                  # share of the gap to the coldest lunar crater floor
g["scoreC"] = np.where(land, 100 * coverC, np.nan)
g["scoreAC"] = g["scoreA"] * coverC / np.nanmax(coverC[land & ~ice])
NASA_EARTH = dict(modis_land_share=float((np.isfinite(LST_MEAN) & land).sum() / land.sum()), modis_years="2018-2022",
                  swing_p99_C=float(np.nanpercentile(LST_SWING[land & np.isfinite(LST_SWING)], 99.9)), coldest_night_C=float(np.nanmin(LST_COLD[land])),
                  best_cold_cover=float(np.nanmax(coverC[land])), best_cold_cover_bare=float(np.nanmax(coverC[land & ~ice])))
snowy = (tavg <= 0.5) & (prec > 5)
snowfree = (~snowy).sum(0) / 12.0
bare = np.where(has_soil, 1 - ramp(np.nan_to_num(soc, nan=30), 2, 25), np.where(ice, 1.0, 0.5))
dry = 1 - ramp(np.nan_to_num(rh, nan=1), 0.25, 0.75)

# ---- sun geometry ----
decl = 23.44 * np.sin(np.radians(360 / 365 * (np.arange(365) - 81)))
def sun_counts(phi):
    noon = 90 - np.abs(phi - decl)
    midnight = -90 + np.abs(phi + decl) if phi >= 0 else -90 + np.abs(phi + decl)
    # sun never sets when the midnight sun stays above the horizon: |phi| + |decl| >= 90 with same sign
    polar_day = ((np.sign(decl) == np.sign(phi)) & (np.abs(phi) + np.abs(decl) >= 90)).sum()
    polar_night = (noon <= 0).sum()
    return polar_day, polar_night
pd_row, pn_row = np.array([sun_counts(p) for p in lat]).T
POLAR_DAY = np.repeat(pd_row[:, None], W, 1); POLAR_NIGHT = np.repeat(pn_row[:, None], W, 1)

# ---- NASA POWER cloud on polar-day months (tiles fetched earlier for high latitudes) ----
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
cl1 = np.full((12, 180, 360), np.nan)
for fn in glob.glob(f"{D}/power/CLOUD_AMT_*.json"):
    for f in json.load(open(fn)):
        lo, la = f["geometry"]["coordinates"][:2]
        v = f["properties"]["parameter"]["CLOUD_AMT"]
        for m, k in enumerate(MON):
            x = v.get(k); cl1[m, min(int(np.floor(la)) + 90, 179), min(int(np.floor(lo)) + 180, 359)] = np.nan if x is None or x < -900 else x / 100
for _ in range(2):
    nb = [np.roll(cl1, s, a) for s in (1, -1) for a in (1, 2)]
    cl1 = np.where(np.isnan(cl1), np.nanmean(np.stack(nb), 0), cl1)
I1 = np.clip(np.floor(LAT).astype(int) + 90, 0, 179); J1 = np.clip(np.floor(LON).astype(int) + 180, 0, 359)
cloud = cl1[:, I1, J1]
summer = [5, 6] if True else []
clear_summer = np.where(LAT >= 0, 1 - np.nanmean(cloud[[5, 6]], 0), 1 - np.nanmean(cloud[[11, 0]], 0))

# ---- geomagnetic field: horizontal strength (IGRF) ----
import ppigrf
la1 = np.arange(-89.5, 90, 1.0); lo1 = np.arange(-179.5, 180, 1.0)
LO1, LA1 = np.meshgrid(lo1, la1)
Be, Bn, Bu = ppigrf.igrf(LO1.ravel(), LA1.ravel(), 0.0, datetime.datetime(2026, 11, 1))
Hh = np.sqrt(np.asarray(Be).ravel() ** 2 + np.asarray(Bn).ravel() ** 2).reshape(LA1.shape)
Hmag = Hh[np.clip(np.floor(LAT).astype(int) + 90, 0, 179), J1]

def nbmax(a, k=2):
    pad = np.pad(np.nan_to_num(a), k, mode="edge")
    return np.max(np.stack([pad[k + di:H + k + di, k + dj:W + k + dj] for di in range(-k, k + 1) for dj in range(-k, k + 1)]), 0)

# ---- Moon targets from real LRO maps (moon_ref.py) ----
M = json.load(open("moon_ref.json")); dv, su, sl = M["diviner"], M["sunlight"], M["slope"]
pc = lambda x: f"{100*x:.0f}%"
MOON = {
 "deep_cold": f"Diviner: coldest crater floors never pass {dv['coldest_max_K']:.0f} K (-{273-dv['coldest_max_K']:.0f} C) even at noon in summer. {pc(dv['frac_avg_below_184K'])} of ground south of 80S averages colder than Earth's record low air (184 K).",
 "dry_permafrost": f"Diviner: ice is stable within 1 m of the surface on {pc(dv['ice_within_1m_frac'])} of ground south of 80S. Where it is buried, the median dry cover is {dv['ice_buried_depth_m_pct']['p50']*100:.0f} cm (90% under {dv['ice_buried_depth_m_pct']['p90']*100:.0f} cm). That is the depth a drill test must match.",
 "power_ridge": f"LOLA: the sunniest spot within 5 degrees of the south pole is lit {pc(su['max_avg_sun_frac'])} of the time, but only {su['area_km2_sun_over_70pct']:.1f} km2 is lit more than 70%. Earth's midnight sun gives 50% at most over a year.",
 "sun_ice_edge": f"LOLA: from ground lit over 70% of the time, permanent shadow is a median {su['km_lit70_to_psr_pct']['p50']*1000:.0f} m away (90% within {su['km_lit70_to_psr_pct']['p90']:.1f} km). The engine now requires sun and frozen ground in the same 18 km cell.",
 "low_sun": f"LOLA: {pc(su['psr_frac'])} of ground within 5 degrees of the pole is in permanent shadow, so robots drive in and out of total darkness.",
 "pad_rock": f"LOLA 40 m slopes: the sunniest ground (where a base and pad would go) has a median slope of {sl['sunlit70_median_deg']:.0f} degrees, and {pc(sl['sunlit70_frac_under_10'])} is under 10. Test sites should be that flat.",
 "featureless": f"LOLA 40 m slopes: median {sl['median_deg']:.0f} degrees near the pole; {pc(sl['frac_over_15'])} of ground is steeper than 15 degrees, so long featureless runs are rarer there than on the maria.",
 "thermal_swing": f"Diviner: summer highs south of 80S run from {dv['t_max_K_pct']['p10']:.0f} K to {dv['t_max_K_pct']['p90']:.0f} K, while yearly averages sit near {dv['t_avg_K_pct']['p50']:.0f} K.",
 "lunar_night": f"Diviner: half the ground south of 80S averages under {dv['t_avg_K_pct']['p50']:.0f} K ({dv['t_avg_K_pct']['p50']-273:.0f} C) across the year.",
 "seal_dust": f"Diviner: dust at the poles sits under {dv['t_avg_K_pct']['p50']:.0f} K on average, far colder than any Earth dust test.",
}
# ---- Mars targets from real orbiter maps (mars_ref.py) ----
MA = json.load(open("mars_ref.json")); air, gr, wa = MA["air"], MA["ground"], MA["water"]
MARS = {
 "thin_air": f"MOLA terrain: half of Mars has under {air['pressure_Pa_pct']['p50']:.0f} Pa of air; even the deepest basin has {air['pressure_Pa_pct']['max']:.0f} Pa. Earth's highest bare ground still has about {air['earth_to_mars_ratio_median']:.0f} times the median Mars pressure.",
 "mars_hyperarid": f"Odyssey gamma-ray map: even the dry low latitudes hold a median {wa['equator_30_median']:.0f}% water by weight, locked in salts and minerals ({wa['min_wt_pct']:.1f} to {wa['max_wt_pct']:.1f}%). The Earth test is getting water out of bone-dry, salty soil.",
 "soft_sand": f"TES thermal inertia: {pc(gr['frac_sand_150_400'])} of Mars between 60S and 60N is sand or crusted soil, and {pc(gr['frac_dust_under100'])} is loose dust. Spirit died in soft soil under a crust.",
 "dust_devils": f"TES albedo: {pc(gr['frac_bright_dusty_albedo_over_0_25'])} of Mars is bright, dust-covered ground that devils and storms can lift.",
 "dust_storm": f"TES albedo: {pc(gr['frac_bright_dusty_albedo_over_0_25'])} of the planet is dust-mantled, the source for regional and global storms.",
}
# Mars data adds a test when a ground type covers over 10% of the planet and no recipe covers it yet
ADD_DUST_MANTLE = gr["frac_dust_under100"] > 0.10

# Moon data sets the commute: lit rim to shadow is under 1 km, so no neighbour search
SUN_ICE_RADIUS = 0 if su["km_lit70_to_psr_pct"]["p90"] < 9 else 1

# ---- recipes: (presence, duration, penalty) -> score ----
R = {}
def add(key, **kw): R[key] = kw

add("seal_dust", score=np.nan_to_num(g["scoreAC"]),
    title="Sharp, dry dust that is also cold", world="Moon", stage="Mines and roads",
    why="Regolith grinds seals, joints and bearings; cold stiffens them.",
    gap="Earth wind rounds some grains; no electrostatic cling from sunlight.", conf="Medium")
add("low_sun", score=np.nan_to_num(g["scoreB"]),
    title="Low sun and black shadows", world="Moon", stage="Mobility and navigation",
    why="Cameras, lidar and eyes face glare beside total darkness.",
    gap="Earth air scatters light into shadows; they never go fully black.", conf="Medium")
add("deep_cold", score=np.nan_to_num(g["scoreC"]),
    title="Deep cold", world="Moon", stage="Mines and processing",
    why="Shadowed crater floors freeze machines and hold the ice.",
    gap="Best ice-free ground covers about 26% of the gap; the rest needs a chamber.", conf="High")
p = (POLAR_NIGHT >= 14).astype(float)
add("lunar_night", score=100 * p * np.minimum(POLAR_NIGHT / 90, 1) * ramp(-np.nan_to_num(g["bio6"]), 20, 50) * bare,
    title="Two weeks of night", world="Moon", stage="Power",
    why="Landers must ride out 14 days of dark and cold on stored power.",
    gap="Earth air and wind move heat; the Moon only radiates it away.", conf="High")
add("thermal_swing", score=100 * ramp(np.nan_to_num(SWING), 14, 40) * dry * bare * snowfree,
    title="Big daily temperature swings", world="Moon & Mars", stage="All hardware",
    why="Repeated hot-cold cycles crack joints, solder and seals over years.",
    gap=f"MODIS: Earth's ground swings reach about {NASA_EARTH['swing_p99_C']:.0f} C from day to night; Mars about 80 C; the Moon far more.", conf="High")
add("thin_air", score=100 * ramp(np.nan_to_num(elev), 2500, 5500) * dry * bare * snowfree,
    title="Thin, dry air and strong UV", world="Mars", stage="Habitats and life support",
    why="Low pressure and UV drive equipment cooling, materials ageing and crew health.",
    gap="Earth's highest ground keeps about half its air; Mars has under 1%.", conf="High")
add("pad_rock", score=100 * ramp(np.nan_to_num(cfvo), 8, 35) * (1 - ramp(relief, 150, 900)) * bare * dry * snowfree,
    title="Rocky, flat ground to build landing pads", world="Moon", stage="Port (landing pads)",
    why="Engine blast sprays loose regolith; pads must be built from local rock on flat ground.",
    gap="Rocket plume in vacuum spreads farther than in air; gravity 1/6.", conf="Medium")
add("dry_permafrost", score=100 * ramp(-np.nan_to_num(bio1, nan=0), 2, 18) * (1 - ramp(np.nan_to_num(bio12), 80, 450)) * np.where(ice, 0, 1) * bare,
    title="Ice locked in dry frozen ground", world="Moon & Mars", stage="Mines",
    why="Ice cemented into soil is the water and fuel source, and fights drills.",
    gap="Earth ground ice is warmer and younger than lunar cold-trap ice.", conf="Medium")
add("featureless", score=100 * (1 - ramp(relief, 15, 250)) * bare * dry * snowfree * np.where(ice, 0, 1),
    title="Flat, featureless ground", world="Moon & Mars", stage="Mobility and navigation",
    why="Robots lose track of distance travelled when nothing in view changes.",
    gap="Earth light and haze still give visual cues the Moon lacks. Ice sheets are even flatter but are ice, not ground.", conf="Medium")
add("no_compass", score=100 * (1 - ramp(Hmag, 1500, 9000)) * (land.astype(float)),
    title="No usable compass", world="Moon & Mars", stage="Mobility and navigation",
    why="Neither world has a global magnetic field to steer by.",
    gap="Field near the magnetic pole is weak, not absent, and it moves each year.", conf="High")
pw = ramp(POLAR_DAY, 30, 100) * np.nan_to_num(clear_summer, nan=0) * ramp(relief, 150, 1200)
add("power_ridge", score=100 * pw * np.where(ice, 0.5, 1),
    title="Ridges with sun that never sets", world="Moon", stage="Power",
    why="Solar farms on crater rims that see the sun most of the time.",
    gap="Earth's midnight sun lasts weeks to months; cloud still interrupts it.", conf="Medium")
add("sun_ice_edge", score=100 * np.sqrt((nbmax(pw, SUN_ICE_RADIUS) if SUN_ICE_RADIUS else pw) * (nbmax(R["dry_permafrost"]["score"] / 100, SUN_ICE_RADIUS) if SUN_ICE_RADIUS else R["dry_permafrost"]["score"] / 100)),
    title="Sunlit ridge next to frozen ground", world="Moon", stage="Power + mines",
    why="The best base sites sit on the edge: power on the rim, ice in the crater below.",
    gap="Our Earth grid is 18 km; the lunar commute is under 1 km, so pick the exact spot locally.", conf="Low")
add("mars_hyperarid", score=100 * (1 - ramp(np.nan_to_num(bio12), 2, 120)) * (1 - ramp(np.nan_to_num(rh), 0.15, 0.55)) * ramp(-np.nan_to_num(bio1, nan=30), -15, 15) * bare,
    title="Cold, hyperarid, sterile ground", world="Mars", stage="Habitats and food",
    why="Mars soil is bone dry with oxidizing salts that hurt crops and life detection.",
    gap="Earth deserts still have trace life and liquid fog; no global perchlorate map was used.", conf="Medium")

# ---- extra layers for round 2 ----
Bu_ = np.asarray(Bu).ravel().reshape(LA1.shape)
dip = np.degrees(np.arctan2(-Bu_, Hh))                      # magnetic inclination
mlat = np.degrees(np.arctan(0.5 * np.tan(np.radians(dip))))  # geomagnetic latitude
Rc1 = 14.9 * np.cos(np.radians(mlat)) ** 4                  # cosmic-ray cutoff rigidity, GV (dipole approx.)
Rc = Rc1[np.clip(np.floor(LAT).astype(int) + 90, 0, 179), J1]
vap = g["vapr"]; windm = g["wind"]
add("radiation", score=100 * ramp(np.nan_to_num(elev), 1500, 4500) * (1 - Rc / 15.0),
    title="Highest natural cosmic-ray exposure", world="Moon & Mars", stage="All hardware",
    why="Space radiation flips bits and wears electronics; Earth's thinnest shielding is high ground near the magnetic poles.",
    gap="Earth's air and field still block most of it; a lunar surface dose is far higher.", conf="Medium")
add("radiative_cold", score=100 * (1 - ramp(np.nan_to_num(vap, nan=2), 0.05, 0.6)) * ramp(np.nan_to_num(elev), 1500, 4500) * snowfree,
    title="Heat lost straight to the sky", world="Moon", stage="Power",
    why="With no air, hardware cools only by radiating to space; radiators and night heaters are sized for that.",
    gap="Earth air still carries heat by convection, unlike the Moon.", conf="Medium")
add("dust_devils", score=100 * ramp(np.nan_to_num(g["silt"], nan=0), 15, 45) * (1 - ramp(np.nan_to_num(rh, nan=1), 0.1, 0.45)) * ramp(np.nan_to_num(SWING), 18, 38) * bare,
    title="Dry, fine dust lifted by heat: static and dust devils", world="Mars", stage="Mobility and navigation",
    why="Mars dust devils and charged dust coat solar panels and optics; robots must clean or ride it out.",
    gap="Earth dust devils are smaller and wetter than Mars's.", conf="Low")
add("soft_sand", score=100 * ramp(np.nan_to_num(sand, nan=0), 70, 95) * (1 - ramp(np.nan_to_num(bio12), 20, 200)) * bare,
    title="Soft sand that traps wheels", world="Mars", stage="Mobility and navigation",
    why="Spirit ended its drive stuck in soft sand; rovers need to detect and escape it.",
    gap="Earth gravity presses wheels harder into the sand than Mars does.", conf="Medium")
add("dust_storm", score=100 * ramp(np.nan_to_num(windm), 3, 7) * ramp(np.nan_to_num(g["silt"], nan=0), 10, 40) * (1 - ramp(np.nan_to_num(bio12), 20, 250)) * bare,
    title="Windy, dusty plains", world="Mars", stage="Power",
    why="Dust storms cut solar power for weeks and sandblast hardware.",
    gap="Martian storms can wrap the whole planet; Earth's are regional.", conf="Low")

if ADD_DUST_MANTLE:
    add("dust_mantle", score=100 * ramp(np.nan_to_num(g["silt"], nan=0), 25, 50) * (1 - ramp(np.nan_to_num(g["clay"], nan=40), 12, 30)) * (1 - ramp(np.nan_to_num(rh, nan=1), 0.1, 0.4)) * (1 - ramp(np.nan_to_num(bio12), 20, 150)) * bare,
        title="Deep loose dust, not sand", world="Mars", stage="Mobility and navigation",
        why="Mars data shows a fifth of the planet is fine dust a rover sinks into, not dune sand. Wheels, drills and suits behave differently in each.",
        gap="Earth dust is rarely more than a few cm deep outside dry lakebeds; Mars mantles can be metres thick.", conf="Low")
    MARS["dust_mantle"] = f"TES thermal inertia: {pc(gr['frac_dust_under100'])} of Mars between 60S and 60N reads under 100, which means loose, fine dust. This test exists because the Mars data asked for it."

exec(open("breadcrumbs.py").read())
SCALE.update({"seal_dust": "Mineral", "low_sun": "Terrain", "deep_cold": "Planet", "lunar_night": "Planet", "thermal_swing": "Air",
              "thin_air": "Air", "pad_rock": "Terrain", "dry_permafrost": "Underground", "featureless": "Terrain", "no_compass": "Planet",
              "power_ridge": "Terrain", "sun_ice_edge": "Terrain", "mars_hyperarid": "Life", "radiation": "Planet", "radiative_cold": "Air",
              "dust_devils": "Air", "soft_sand": "Terrain", "dust_storm": "Air", "dust_mantle": "Mineral"})

for k in R:
    s = np.array(R[k]["score"], dtype=float); s[~land] = np.nan
    if k not in ("dry_permafrost", "featureless", "no_compass", "power_ridge", "sun_ice_edge", "thermal_swing", "thin_air", "radiation", "radiative_cold", "erasers_off", "radio_quiet", "magnetic_memory"):
        s[ice] = np.nan
    if k in ("thermal_swing", "thin_air", "pad_rock", "dust_devils", "soft_sand", "dust_storm", "radiative_cold", "dust_mantle"):
        s[ice] = np.nan
    R[k]["score"] = s

# ---- countries for labels ----
cg = json.load(open(f"{D}/ne/countries.geojson"))
names = [f["properties"].get("ADMIN") or f["properties"].get("NAME") for f in cg["features"]]
cid = rasterize([(f["geometry"], i + 1) for i, f in enumerate(cg["features"])], out_shape=(H, W),
                transform=rasterio.transform.from_origin(-180, 90, 1/6, 1/6), fill=0, dtype="int32")
def country(i, j):
    c = cid[i, j]
    if c == 0:
        for r in range(1, 6):
            win = cid[max(i - r, 0):i + r + 1, max(j - r, 0):j + r + 1]; nz = win[win > 0]
            if nz.size: c = np.bincount(nz).argmax(); break
    return names[c - 1] if c else "Open ocean/ice"

def top(s, n=5, sep=4.0):
    a = np.nan_to_num(s, nan=-1); idx = np.argsort(a.ravel())[::-1]; out = []
    for f in idx[:300000]:
        i, j = divmod(int(f), W)
        if a[i, j] <= 0: break
        la, lo = float(LAT[i, j]), float(LON[i, j])
        if all(abs(la - o["lat"]) > sep or abs(lo - o["lon"]) > sep / max(np.cos(np.radians(la)), 0.25) for o in out):
            out.append({"lat": round(la, 2), "lon": round(lo, 2), "score": round(float(a[i, j]), 1), "country": country(i, j)})
        if len(out) >= n: break
    return out

KNOWN = [("Haughton Crater", 75.43, -89.82), ("McMurdo Dry Valleys", -77.55, 161.5), ("Atacama (Yungay)", -24.08, -69.92),
         ("Mauna Kea", 19.80, -155.47), ("Black Point Lava Flow", 35.68, -111.43), ("Meteor Crater", 35.03, -111.02),
         ("Mars Desert Research Station", 38.41, -110.79), ("Svalbard (Bockfjord)", 79.43, 13.93), ("Salar de Uyuni", -20.13, -67.49)]
def cell(la, lo): return min(int((90 - la) * 6), H - 1), min(int((lo + 180) * 6), W - 1)

res = {}
for k, r in R.items():
    s = r["score"]; vals = np.sort(s[np.isfinite(s)])
    kn = []
    for nm, la, lo in KNOWN:
        i, j = cell(la, lo)
        v = float(np.nanmax(s[max(i-2,0):i+3, max(j-2,0):j+3])) if np.isfinite(s[max(i-2,0):i+3, max(j-2,0):j+3]).any() else 0.0
        kn.append({"name": nm, "score": round(v, 1), "pct": round(100 * np.searchsorted(vals, v) / max(len(vals), 1), 1)})
    meta = {x: r[x] for x in r if x != "score"}
    if k in MOON: meta["moon"] = MOON[k]
    if k in MARS: meta["mars"] = MARS[k]
    meta["scale"] = SCALE.get(k, "Terrain")
    res[k] = meta | {"top": top(s), "known": kn, "cells_above_50pct_of_max": int((s > 0.5 * np.nanmax(s)).sum())}
    np.save(f"{OUT}/score_{k}.npy", s.astype(np.float32))
EARTH_CANT = [
    {"title": "Vacuum", "world": "Moon & Mars", "why": "Changes heat flow, outgassing, lubrication and dust behaviour.", "instead": "Thermal-vacuum chambers"},
    {"title": "Low gravity (1/6 g Moon, 3/8 g Mars)", "world": "Moon & Mars", "why": "Changes walking, digging, traction and how dust falls.", "instead": "Parabolic flights, offloading rigs, neutral buoyancy"},
    {"title": "Space radiation", "world": "Moon & Mars", "why": "Damages electronics and crews over years.", "instead": "Particle-beam facilities"},
    {"title": "Carbon dioxide geysers under seasonal ice", "world": "Mars", "why": "Spring gas jets near the Martian south pole.", "instead": "Mars-condition chambers (already recreated at JPL)"},
    {"title": "Superconducting cold for free", "world": "Moon", "why": "Crater cold could run superconducting power lines and maglevs; nowhere on Earth is cold enough.", "instead": "Cryogenic labs"},
]
json.dump({"constraints": res, "earth_cant": EARTH_CANT, "moon_ref": M, "mars_ref": MA, "nasa_earth": NASA_EARTH, "ratios": RATIO, "meteor_check": METEOR_CHECK}, open(f"{OUT}/constraints.json", "w"), indent=1)
for k, v in res.items():
    print(f"{k:15s}", [(t['country'], t['lat'], t['lon'], t['score']) for t in v["top"][:4]])
