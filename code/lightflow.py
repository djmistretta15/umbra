"""Umbra: Moon light-flow. Let lunar physics, not us, show where paths and hubs form at the south pole.

Inputs (LRO / LOLA, 85S to pole): AVGVISIB (average sunlight fraction, 60 m), LPSR (permanent shadow, 60 m),
LDSM (slope, 40 m). Everything is resampled to a 240 m grid.

Physics only, no hand weights:
  energy to cross 1 m   ~ m g (Crr + sin(slope))         rolling resistance plus climbing (Apollo LRV class Crr = 0.15)
  energy available       ~ average sunlight fraction       a solar rover recharges only in sunlight
  cost per metre         = (Crr + sin(slope)) / max(sun, 0.02)
  slopes over 25 degrees are impassable (LRV design limit).
Flow: 150 random start points, each routed by least cost to 80 random end points across the whole map
(12,000 trips). Cells used by many trips are corridors; where corridors pile up are hubs. Nobody picks sites.
Check: distance from each hub to NASA's named Artemis III candidate regions (by their IAU feature).
"""
import sys, json, numpy as np
from scipy import ndimage
from skimage.graph import MCP_Geometric

D = sys.argv[1]; NAMES = sys.argv[2]
R = 1737.4e3; rng = np.random.default_rng(7)

def load(name, n, scale, off):
    return np.fromfile(f"{D}/{name}", "<i2").reshape(n, n).astype(np.float32) * scale + off

def block(a, k, n_out):
    a = a[:n_out * k, :n_out * k].reshape(n_out, k, n_out, k)
    return np.nanmean(a, axis=(1, 3))

G = 1264; PIX = 240.0
vis = load("AVGVISIB_85S_060M_201608.IMG", 5058, 0.00004, 0)
vis[(vis < 0) | (vis > 1)] = np.nan
psr = load("LPSR_85S_060M_201608.IMG", 5058, 0.000025, 0.5)
raw = np.fromfile(f"{D}/LDSM_85S_40M.IMG", "<i2").reshape(7584, 7584)
sl = raw.astype(np.float32) * 0.0015 + 45.0
sl[(raw == 0) | (sl < 0) | (sl >= 90)] = np.nan
with np.errstate(all="ignore"):
    V = block(vis, 4, G); P = block((psr > 0.5).astype(np.float32), 4, G); S = block(sl, 6, G)
# fill slope gaps from nearest measured cell
m = np.isfinite(S); idx = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True); S = S[idx[0], idx[1]]

c0 = (G - 1) / 2
yy, xx = np.mgrid[0:G, 0:G]
X = (xx - c0) * PIX; Y = (c0 - yy) * PIX
rho = np.hypot(X, Y); LAT = -90 + np.degrees(2 * np.arctan(rho / (2 * R))); LON = np.degrees(np.arctan2(X, Y)) % 360
inside = (LAT <= -85) & np.isfinite(V)

CRR, VMIN, SMAX = 0.15, 0.02, 25.0
cost = (CRR + np.sin(np.radians(S))) / np.maximum(np.nan_to_num(V), VMIN)
cost[(S > SMAX) | ~inside] = np.inf

pts = np.argwhere(inside & np.isfinite(cost))
src = pts[rng.choice(len(pts), 150, replace=False)]
traffic = np.zeros((G, G), np.float32)
for s in src:
    mcp = MCP_Geometric(cost, fully_connected=True)
    cum, _ = mcp.find_costs([tuple(s)])
    ends = pts[rng.choice(len(pts), 80, replace=False)]
    for e in ends:
        if not np.isfinite(cum[tuple(e)]): continue
        for p in mcp.traceback(tuple(e)): traffic[p] += 1

# hubs: local maxima of smoothed traffic (about 2.4 km window), at least 8 km apart
T = ndimage.gaussian_filter(traffic, 4)
peaks = (T == ndimage.maximum_filter(T, 33)) & (T > np.percentile(T[inside], 99))
cand = sorted([(float(T[i, j]), i, j) for i, j in np.argwhere(peaks)], reverse=True)[:12]

names = json.load(open(NAMES))
def xy(lat, lon):
    r = 2 * R * np.tan(np.radians(90 + lat) / 2); return r * np.sin(np.radians(lon)), r * np.cos(np.radians(lon))
def nearest(lat, lon):
    x, y = xy(lat, lon); best = None
    for n in names:
        nx, ny = xy(n["lat"], n["lon"]); d = np.hypot(x - nx, y - ny) / 1000 - (n["d"] or 0) / 2
        if best is None or d < best[0]: best = (d, n["name"])
    return best[1], round(max(best[0], 0), 1)
# NASA Artemis III candidate regions tied to these IAU features (2022 list of 13 and 2024 list of 9)
ARTEMIS = {"Shackleton", "de Gerlache", "Haworth", "Faustini", "Slater", "Nobile", "Mons Malapert", "Mons Mouton",
           "Amundsen", "Cabeus", "Mons Kocher", "Shoemaker"}
psrdist = ndimage.distance_transform_edt(P < 0.5) * PIX / 1000

hubs = []
for t, i, j in cand:
    nm, dkm = nearest(LAT[i, j], LON[i, j])
    hubs.append(dict(lat=round(float(LAT[i, j]), 3), lon=round(float(LON[i, j]), 2), traffic=round(t, 1),
                     sun=round(float(V[i, j]), 3), slope_deg=round(float(S[i, j]), 1),
                     km_to_shadow_ice=round(float(psrdist[i, j]), 1), near=nm, km_from_feature_rim=dkm,
                     artemis_feature=nm in ARTEMIS))

lit = inside & (V >= 0.5)
corr = traffic >= np.percentile(traffic[inside & (traffic > 0)], 90)
summary = dict(
    trips=int(150 * 80), grid_m=PIX, crr=CRR, max_slope_deg=SMAX,
    area_km2=float(inside.sum() * PIX ** 2 / 1e6),
    corridor_share_of_area=float((corr & inside).sum() / inside.sum()),
    corridor_mean_sun=float(np.nanmean(V[corr & inside])), map_mean_sun=float(np.nanmean(V[inside])),
    corridor_mean_slope=float(np.mean(S[corr & inside])), map_mean_slope=float(np.mean(S[inside])),
    hubs_near_artemis=int(sum(h["artemis_feature"] for h in hubs)), n_hubs=len(hubs),
    note="Earth visibility not yet included (needs LOLA elevation horizon model).")
json.dump(dict(summary=summary, hubs=hubs), open("lightflow.json", "w"), indent=1)
np.savez_compressed("lightflow_maps.npz", traffic=traffic, vis=V, psr=P, slope=S, lat=LAT, lon=LON)
print(json.dumps(summary, indent=1)); [print(h) for h in hubs]
