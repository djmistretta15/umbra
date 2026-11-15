"""Umbra Live extras: orbiter-view measurement layers (for fingerprint search) and the ringing-ground test.

Measurement layers are what an orbiting instrument would record, ranked across Earth's ice-free land (0 = lowest, 254 = highest):
  brightness        NASA POWER all-sky surface albedo
  day-night swing   NASA MODIS Terra land surface temperature, day minus night
  thermal inertia   apparent thermal inertia (1 - albedo) / swing, the NASA HCMM-era way to read ground firmness from orbit
  surface UV        NASA POWER UV index
  dust              NASA MERRA-2 dust near the ground
  rain              NASA POWER precipitation
Ringing ground: dry crystalline bedrock without sediment cover, far from earthquakes. Water in pores damps seismic waves;
the Moon's dry crust lets them ring for a long time.
Output: live_extra.npz (0.5 deg, uint8) and live_extra.json (metadata), read by export_live.py.
"""
import json, numpy as np
MW_MED = json.load(open("moon_walk.json"))["corridor_median_deg"]
from scipy import ndimage
D = "/home/claude/data"
g = np.load("grid.npz"); land = g["land"].astype(bool); noice = ~g["ice"].astype(bool); ok = land & noice
alb = np.load(f"{D}/power_alb/power_albedo.npy")
m = np.load(f"{D}/gibs/modis_lst.npz")
with np.errstate(all="ignore"): sw = np.nanmean(m["day"] - m["night"], axis=0)
f = np.isfinite(sw); idx = ndimage.distance_transform_edt(~f, return_distances=False, return_indices=True); sw = sw[idx[0], idx[1]]
uv = np.load(f"{D}/power_uv/power_uv_index.npy"); dust = np.nan_to_num(np.load(f"{D}/gibs/merra2_dust.npy"))
rain = np.load(f"{D}/power_prec/power_prec_mm_yr.npy")
ati = (1 - alb) / np.maximum(sw, 1.0)

NL = np.load(f"{D}/new/layers.npz"); L_ = lambda k: np.nan_to_num(NL[k].astype(float))
def ramp(x, lo, hi): return np.clip((x - lo) / (hi - lo), 0, 1)
def norm99(a): v = a[land & (a > 0)]; return a / (np.percentile(v, 99) if v.size else 1)
cryst = L_("lith_metamorphic") + L_("lith_acid_plutonic") + L_("lith_basic_plutonic") + L_("lith_basalt")
sedi = L_("lith_unconsolidated") + L_("lith_siliciclastic")
quake = np.log10(1 + norm99(NL["quakes"]) * 100) / 2
ring = 100 * (1 - ramp(rain, 50, 400)) * ramp(cryst, .5, .95) * (1 - ramp(sedi, .1, .5)) * (1 - ramp(quake, .1, .6)) * ok

H, W, F = 360, 720, 3
def pool(a, how):
    a = np.where(ok, a, np.nan).reshape(H, F, W, F)
    with np.errstate(all="ignore"):
        import warnings; warnings.simplefilter("ignore")
        return (np.nanmax if how == "max" else np.nanmean)(np.nanmean(a, 3) if how == "mean" else np.nanmax(a, 3), 1)
def rank(a):
    out = np.full(a.shape, 255, np.uint8); v = np.isfinite(a); o = a[v].argsort().argsort()
    out[v] = np.round((o + .5) / v.sum() * 254).astype(np.uint8); return out
MEAS = [("brightness", "Orbiter view: brightness (albedo)", alb, "NASA POWER ALLSKY_SRF_ALB"),
        ("swing", "Orbiter view: day-night swing", sw, "NASA MODIS Terra LST"),
        ("ati", "Orbiter view: thermal inertia (apparent)", ati, "NASA POWER albedo + MODIS LST"),
        ("uv", "Surface UV", uv, "NASA POWER ALLSKY_SFC_UV_INDEX"),
        ("dust", "Dust near the ground", dust, "NASA MERRA-2 via GIBS"),
        ("rain", "Rain", rain, "NASA POWER PRECTOTCORR")]
arrs = {}; meta = dict(measures=[], ringing={})
for k, t, a, src in MEAS:
    p = pool(a, "mean"); arrs[k] = rank(p)
    v = p[np.isfinite(p)]
    meta["measures"].append(dict(key=k, title=t, source=src, q=[float(x) for x in np.percentile(v, [0, 10, 25, 50, 75, 90, 100])]))
r = pool(ring, "max"); arrs["ringing_ground"] = np.where(np.isfinite(r), np.clip(np.round(r / max(np.nanmax(r), 1e-6) * 254), 0, 254), 255).astype(np.uint8)
meta["ringing"] = dict(title="Ringing ground: dry bedrock for lunar seismometers", world="Moon & Mars", stage="Science",
    why="Water in rock pores soaks up seismic waves. The Moon's crust is bone dry, so moonquakes ring for a long time. Dry, bare crystalline rock far from earthquakes is Earth's closest match for testing lunar seismometers and the shaking from landings and mass drivers.",
    moon="Apollo seismometers (1969 to 1977) recorded moonquakes whose signals kept ringing for tens of minutes to about an hour.",
    mars="InSight found Mars's crust damps waves more than the Moon's but far less than Earth's wet crust.",
    gap="No Earth rock is as dry as the Moon's, and Earth's oceans add constant background noise.", conf="Low")
# Fingerprint presets, as target ranks on the measurement layers (0 = lowest on Earth, 254 = highest).
# Mars units from TES (Putzig and Mellon 2007): bright low-inertia dust; dark high-inertia sand and rock; intermediate crusted soil.
meta["presets"] = [
    dict(name="Mars dust plain (TES: bright, low thermal inertia)", t=dict(brightness=230, ati=25, rain=10)),
    dict(name="Mars dark sand and rock (TES: dark, high thermal inertia)", t=dict(brightness=40, ati=230, rain=10)),
    dict(name="Mars crusted soil (TES: middle brightness and inertia)", t=dict(brightness=150, ati=130, rain=10)),
    dict(name="Lunar mare soil (dark, loose, bone dry, big swings)", t=dict(brightness=30, ati=25, swing=245, rain=5)),
    dict(name="Lunar highlands soil (bright, loose, bone dry, big swings)", t=dict(brightness=200, ati=25, swing=245, rain=5)),
]
OPS = json.load(open("analogs6.json"))
OPTXT = {
 "plume_blast": dict(why="A lander's exhaust blasts loose dust and rocks outward at high speed, a known Artemis hazard. Fine, loose, dry, flat ground is where to test landing pads, berms and plume shields.", moon="Apollo 12 landed about 160 m from the Surveyor 3 probe; parts brought home showed pitting from the dust its exhaust blasted.", gap="Earth soil is usually clumped by moisture and roots; lunar dust is drier, sharper and in vacuum flies much farther."),
 "dirty_panels": dict(why="On the Moon and Mars no rain washes dust off. Where the most dust falls with the least rain and strong sun is where to test dust-shedding panels and coatings.", mars="NASA's InSight lander ended its mission in 2022 when dust on its solar panels cut its power.", gap="The dust map tops out at its highest colour band, so the dustiest places rank as ties."),
 "dark_pocket": dict(why="Astronauts will walk into permanently shadowed craters to sample ice in darkness and deep cold. Ground shaded at winter noon that is also very cold and dry is where to rehearse that work.", moon="LRO's LOLA maps put 11% of the ground south of 85S in permanent shadow; Diviner finds crater floors near -240 C.", gap="Earth's shade lifts in summer and its coldest nights are far warmer than lunar crater floors."),
 "radio_shadow": dict(why="From the lunar south pole the Earth hangs no more than about 7 degrees above the horizon, so ridges and crater walls cut the radio link. Valleys walled above 7 degrees in most directions are where to test relays and mesh networks.", moon="NASA is planning lunar relay satellites (LunaNet), partly because many south-polar sites lose direct sight of Earth for part of each month.", gap="Earth's terrain here is measured at about 2.4 km; smaller canyons are missed."),
 "walk_back": dict(why="If a rover breaks down, the crew walks home. This finds Earth ground with the same mix of slopes as the Moon's natural travel corridors, measured the same way over 5 km.", moon=f"On the lunar corridors found by Umbra's light-flow, half the ground is under {MW_MED:.1f} degrees at a 5 km baseline (LOLA elevation).", gap="Slopes are compared at a 5 km baseline; footing, boulders and dust at the metre scale are not."),
 "oxygen_feed": dict(why="Lunar oxygen plants will cook oxygen out of local rock. Test plants need tonnes of rock like the Moon's lava plains or highlands, close enough to a town to ship it.", moon="Mare basalt and highland anorthosite are the two main lunar feedstocks; Apollo samples are the reference.", gap="The rock map gives rock type, not titanium content or grain size; samples must be checked."),
}
meta["ops"] = []
for k, v in OPS.items():
    a = np.load(f"cons/score_{k}.npy"); p = pool(np.where(np.isfinite(a), a, np.nan), "max")
    arrs[k] = np.where(np.isfinite(p), np.clip(np.round(p / max(np.nanmax(p), 1e-6) * 254), 0, 254), 255).astype(np.uint8)
    meta["ops"].append(dict(key=k, title=v["title"], world="Moon & Mars" if k in ("dirty_panels",) else "Moon", stage="Operations", conf="Low", **OPTXT[k]))
np.savez_compressed("live_extra.npz", **arrs); json.dump(meta, open("live_extra.json", "w"), indent=1)
print({k: int((v < 255).sum()) for k, v in arrs.items()})
rk = arrs["ringing_ground"]; ii = np.argsort(rk.ravel())[::-1]
print("ringing top", [(round(90 - (i // W + .5) * .5, 1), round(-180 + (i % W + .5) * .5, 1), int(rk.ravel()[i])) for i in ii[:300:30] if rk.ravel()[i] < 255])
