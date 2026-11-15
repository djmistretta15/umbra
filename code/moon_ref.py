"""Umbra: Moon reference values computed from real LRO maps (south pole).

Inputs (data/moon):
  prp_south.tab                 Diviner polar resource product (Paige, UCLA): per ~0.5 km triangle,
                                annual mean temp, annual max temp, depth to stable water ice
  AVGVISIB_85S_060M_201608.IMG  LOLA-derived average sunlight fraction, 85S-pole, 60 m (Mazarico)
  LPSR_85S_060M_201608.IMG      LOLA-derived permanent shadow map, 60 m
  LDSM_85S_40M.IMG              LOLA slope map, 85S-pole, 40 m
Output: moon_ref.json, moon_maps.npz (downsampled, for figures)
"""
import sys, json, numpy as np, pandas as pd
from scipy import ndimage

D = sys.argv[1]
R = 1737.4e3

def img(name, n, scale, offset):
    a = np.fromfile(f"{D}/{name}", dtype="<i2").reshape(n, n).astype(np.float32)
    return a * scale + offset

def latgrid(n, pix):
    c = (n - 1) / 2
    y, x = np.mgrid[0:n, 0:n]
    rho = np.hypot((x - c) * pix, (y - c) * pix)
    return -90 + np.degrees(2 * np.arctan(rho / (2 * R)))

out = {}

# ---- Diviner temperatures and ice
df = pd.read_csv(f"{D}/prp_south.tab", skipinitialspace=True,
                 usecols=["tri_clat", "temp_avg", "temp_max", "ice_depth"])
df = df[df.tri_clat <= -80]
ta, tm, ice = df.temp_avg.values, df.temp_max.values, df.ice_depth.values
n = len(df)
out["diviner"] = dict(
    region="80S to pole", cells=int(n),
    t_avg_K_pct=dict(zip(["p1", "p10", "p50", "p90"], np.percentile(ta, [1, 10, 50, 90]).round(1).tolist())),
    t_max_K_pct=dict(zip(["p1", "p10", "p50", "p90", "p99"], np.percentile(tm, [1, 10, 50, 90, 99]).round(1).tolist())),
    coldest_max_K=float(np.round(tm.min(), 1)),
    frac_max_below_110K=float(np.mean(tm < 110)),       # surface ice stable year round
    frac_avg_below_184K=float(np.mean(ta < 184)),       # colder on average than Earth's record low air
    frac_avg_below_216K=float(np.mean(ta < 216)),       # colder than Earth's coldest annual mean (~ -57 C)
    ice_surface_frac=float(np.mean(ice == 0)),
    ice_within_1m_frac=float(np.mean((ice >= 0) & (ice <= 1))),
    ice_buried_depth_m_pct=dict(zip(["p10", "p50", "p90"],
        np.percentile(ice[ice > 0], [10, 50, 90]).round(2).tolist()) if np.any(ice > 0) else None),
)

# ---- Illumination and permanent shadow (60 m, 85S to pole)
N = 5058
vis = img("AVGVISIB_85S_060M_201608.IMG", N, 0.00004, 0.0)
psr = img("LPSR_85S_060M_201608.IMG", N, 0.000025, 0.5)
lat = latgrid(N, 60.0)
inside = lat <= -85
vis = np.where(inside & (vis >= 0) & (vis <= 1), vis, np.nan)
psrm = inside & (psr > 0.5)
lit = inside & (vis >= 0.7)
dist_km = ndimage.distance_transform_edt(~psrm) * 0.06
out["sunlight"] = dict(
    region="85S to pole",
    max_avg_sun_frac=float(np.nanmax(vis)),
    area_km2_sun_over_70pct=float(lit.sum() * 0.0036),
    area_km2_sun_over_80pct=float((inside & (vis >= 0.8)).sum() * 0.0036),
    psr_frac=float(psrm.sum() / inside.sum()),
    km_lit70_to_psr_pct=dict(zip(["p10", "p50", "p90"], np.percentile(dist_km[lit], [10, 50, 90]).round(2).tolist())),
)

# ---- Slopes (40 m, 85S to pole)
Ns = 7584
sl = img("LDSM_85S_40M.IMG", Ns, 0.0015, 45.0)
lats = latgrid(Ns, 40.0)
raw = np.fromfile(f"{D}/LDSM_85S_40M.IMG", dtype="<i2").reshape(Ns, Ns)
ok = (lats <= -85) & (raw != 0) & (sl >= 0) & (sl < 90)   # DN 0 = no LOLA data at 40 m
out_cov = float(ok.sum() / (lats <= -85).sum())
s = sl[ok]
out["slope"] = dict(
    region="85S to pole", baseline_m=40, data_coverage=out_cov,
    median_deg=float(np.median(s).round(1)),
    frac_under_5=float(np.mean(s < 5)), frac_under_10=float(np.mean(s < 10)),
    frac_over_15=float(np.mean(s > 15)), frac_over_25=float(np.mean(s > 25)),
)
# slope on the sunniest ground (where a base would sit)
vis_on_s = ndimage.zoom(np.nan_to_num(vis, nan=-1), Ns / N, order=0)[:Ns, :Ns]
sun_ok = ok & (vis_on_s >= 0.7)
out["slope"]["sunlit70_median_deg"] = float(np.median(sl[sun_ok]).round(1))
out["slope"]["sunlit70_frac_under_10"] = float(np.mean(sl[sun_ok] < 10))

json.dump(out, open("moon_ref.json", "w"), indent=1)
print(json.dumps(out, indent=1))

# downsampled maps for figures
k = 4
np.savez_compressed("moon_maps.npz",
    vis=vis[::k, ::k], psr=psrm[::k, ::k], slope=np.where(ok, sl, np.nan)[::k * 2, ::k * 2])
# diviner raster: bin to 1 km polar-stereo grid
r = 2 * R * np.tan(np.radians(90 + df.tri_clat.values) / 2) / 1000
lon = np.radians(pd.read_csv(f"{D}/prp_south.tab", skipinitialspace=True, usecols=["tri_clon"]).tri_clon.values[(pd.read_csv(f"{D}/prp_south.tab", skipinitialspace=True, usecols=["tri_clat"]).tri_clat.values <= -80)])
x, y = r * np.sin(lon), r * np.cos(lon)
G = 600; ext = 305
ix = ((x + ext) / (2 * ext) * G).astype(int); iy = ((ext - y) / (2 * ext) * G).astype(int)
m = (ix >= 0) & (ix < G) & (iy >= 0) & (iy < G)
S = np.zeros((G, G)); C = np.zeros((G, G))
np.add.at(S, (iy[m], ix[m]), tm[m]); np.add.at(C, (iy[m], ix[m]), 1)
np.save("moon_tmax.npy", np.where(C > 0, S / np.maximum(C, 1), np.nan))
