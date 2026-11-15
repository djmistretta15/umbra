"""Lunar corridor slopes at the same ~5 km baseline as the Earth terrain (LOLA LDEM_80S_80M, NASA PDS / MIT).
Corridors = top 10% traffic cells from lightflow.py. Output: moon_walk.json (slope histogram on the corridors and on all ground)."""
import json, numpy as np
R = 1737.4e3; N = 7600; S0 = 3799.5; PX = 80.0
E = np.fromfile("/home/claude/data/moon/LDEM_80S_80M.IMG", "<i2").reshape(N, N).astype(np.float32) * 0.5
k = 30   # +-2.4 km
gy = (np.roll(E, -k, 0) - np.roll(E, k, 0)) / (2 * k * PX); gx = (np.roll(E, -k, 1) - np.roll(E, k, 1)) / (2 * k * PX)
S = np.degrees(np.arctan(np.hypot(gx, gy)))
M = np.load("lightflow_maps.npz"); T = M["traffic"]; G = T.shape[0]; c0 = (G - 1) / 2
inside = np.isfinite(M["vis"]) & (M["lat"] <= -85)
thr = np.percentile(T[inside & (T > 0)], 90); cor = inside & (T >= thr)
ii, jj = np.nonzero(cor); x = (jj - c0) * 240.0; y = (c0 - ii) * 240.0
li = np.round(S0 - y / PX).astype(int); lj = np.round(S0 + x / PX).astype(int)
cs = S[li, lj]
ai, aj = np.nonzero(inside); xa = (aj - c0) * 240.0; ya = (c0 - ai) * 240.0
sa = S[np.round(S0 - ya / PX).astype(int), np.round(S0 + xa / PX).astype(int)]
BINS = [0, 2, 5, 10, 15, 25, 90]
h = np.histogram(cs, BINS)[0] / len(cs); ha = np.histogram(sa, BINS)[0] / len(sa)
out = dict(baseline_km=4.8, bins=BINS, corridor_hist=h.round(4).tolist(), all_ground_hist=ha.round(4).tolist(),
           corridor_median_deg=float(np.median(cs)), all_median_deg=float(np.median(sa)), n_corridor_cells=int(len(cs)))
json.dump(out, open("moon_walk.json", "w"), indent=1); print(out)
