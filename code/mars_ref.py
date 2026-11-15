"""Umbra: Mars reference values from real NASA orbiter maps.

Inputs (data/mars):
  megt90n000eb.img       MGS MOLA MEGDR topography, 16 px/deg (m above areoid)
  global_ti_night_2007   MGS TES nightside thermal inertia, 20 px/deg (Putzig and Mellon 2007)
  global_albedo_8ppd     MGS TES bolometric albedo, 8 px/deg
  h2o_sr_5x5.tab         Mars Odyssey GRS water-equivalent hydrogen, 5 deg bins (+-~60 lat)
Output: mars_ref.json, mars_maps.npz
"""
import sys, json, numpy as np

D = sys.argv[1]
def area_w(lat): return np.cos(np.radians(lat))
def wfrac(mask, w):
    m = np.asarray(mask, dtype=float); ok = np.isfinite(m)
    return float((w[ok] * m[ok]).sum() / w[ok].sum())

# --- common grid: 4 px/deg, lat 90..-90, lon -180..180
G = 4; LAT = 90 - (np.arange(180 * G) + 0.5) / G; LON = -180 + (np.arange(360 * G) + 0.5) / G
W = np.repeat(area_w(LAT)[:, None], 360 * G, 1)

def block(a, f):  # mean-downsample by integer factor, ignoring nan
    h, w = a.shape; a = a.reshape(h // f, f, w // f, f)
    return np.nanmean(np.nanmean(a, 3), 1)

topo = np.fromfile(f"{D}/megt90n000eb.img", dtype=">i2").reshape(2880, 5760).astype(np.float32)
topo = np.roll(topo, 2880, 1)                        # 0..360E -> -180..180
topo = block(topo, 4)
ti = np.fromfile(f"{D}/global_ti_night_2007.img", dtype=">i2").reshape(3600, 7200).astype(np.float32)
ti[ti <= 0] = np.nan; ti = block(ti, 5)
alb = np.fromfile(f"{D}/global_albedo_8ppd.img", dtype="<f4").reshape(1440, 2880)
alb = np.where((alb > 0) & (alb < 1), alb, np.nan); alb = block(alb, 2)
h2o = np.full((36, 72), np.nan)
for la, lo, c, *_ in np.loadtxt(f"{D}/h2o_sr_5x5.tab"):
    if c < 9000:
        lo = lo - 360 if lo > 180 else lo
        h2o[int((90 - la) // 5), int((lo + 180) // 5) % 72] = c
h2o = np.kron(h2o, np.ones((5 * G, 5 * G)))

# surface pressure from MOLA height: ~610 Pa at the areoid, scale height ~11 km (annual-mean approximation)
P = 610 * np.exp(-topo / 11100)
mid = np.abs(LAT)[:, None] <= 60 * np.ones((1, 360 * G))
out = {}
out["air"] = dict(
    pressure_Pa_pct={k: float(np.round(np.percentile(P, q), 0)) for k, q in [("p10", 10), ("p50", 50), ("p90", 90), ("max", 100)]},
    frac_above_700Pa=wfrac(P > 700, W),
    earth_best_ground_Pa=50500,   # about 5,500 m on Earth (standard atmosphere)
    earth_to_mars_ratio_median=float(np.round(50500 / np.percentile(P, 50), 0)),
)
tim = np.where(mid, ti, np.nan)
out["ground"] = dict(
    note="thermal inertia, J m-2 K-1 s-1/2; under ~100 = loose dust, 150-400 = sand and crusted soil, over ~1000 = rock",
    ti_pct={k: float(np.round(np.nanpercentile(tim, q), 0)) for k, q in [("p10", 10), ("p50", 50), ("p90", 90)]},
    frac_dust_under100=wfrac(np.where(np.isfinite(tim), tim < 100, np.nan), W),
    frac_sand_150_400=wfrac(np.where(np.isfinite(tim), (tim >= 150) & (tim <= 400), np.nan), W),
    frac_rock_over1000=wfrac(np.where(np.isfinite(tim), tim > 1000, np.nan), W),
    frac_bright_dusty_albedo_over_0_25=wfrac(np.where(np.isfinite(alb), alb > 0.25, np.nan), W),
)
hh = np.where(np.isfinite(h2o), h2o, np.nan)
out["water"] = dict(
    note="Odyssey GRS water-equivalent wt%, top ~1 m, 5 deg bins",
    equator_30_median=float(np.round(np.nanmedian(np.where(np.abs(LAT)[:, None] <= 30, hh, np.nan)), 1)),
    coverage="about 57S to 57N; ice-rich ground poleward is outside this map",
    frac_over_5pct=wfrac(np.where(np.isfinite(hh), hh > 5, np.nan), W),
    min_wt_pct=float(np.round(np.nanmin(hh), 1)), max_wt_pct=float(np.round(np.nanmax(hh), 1)),
)
# where a crewed base wants to be: water nearby, thicker air for landing, firm ground, not too far from the equator for sun
base = (hh > 5) & (topo < 0) & (ti >= 150) & (np.abs(LAT)[:, None] <= 50)
out["base_zone"] = dict(rule="GRS water over 5 wt%, below the areoid (thicker air), thermal inertia 150+ (firm), within 50 deg of equator",
                        frac_of_mars=wfrac(np.where(np.isfinite(hh), base, np.nan), W))
json.dump(out, open("mars_ref.json", "w"), indent=1)
print(json.dumps(out, indent=1))
np.savez_compressed("mars_maps.npz", P=P, ti=ti, h2o=hh, base=base, topo=topo)
