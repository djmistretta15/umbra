"""Mini maps per constraint, the multi-test site finder, and the overview pin map."""
import json, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
g = dict(np.load("grid.npz")); land, ice = g["land"], g["ice"]
C = json.load(open("cons/constraints.json")); cons = C["constraints"]
H, W = land.shape
PIN = "#f2a541"
WM = "Umbra · Team Forced Futures · computed with AI-assisted code"
bg = np.where(land, np.where(ice, 0.80, 0.88), 1.0)

def mini(k, v, s):
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=110)
    ax.imshow(bg, extent=[-180, 180, -90, 90], cmap="gray", vmin=0, vmax=1, aspect="auto")
    vmax = np.nanpercentile(s[s > 0], 99.5) if np.any(s > 0) else 1
    m = np.where(s > 0.03 * vmax, s, np.nan)
    ax.imshow(m, extent=[-180, 180, -90, 90], cmap="magma_r", vmin=0, vmax=vmax, aspect="auto")
    for n, t in enumerate(v["top"][:5]):
        ax.plot(t["lon"], t["lat"], "o", ms=9, mfc="none", mec=PIN, mew=2)
        ax.text(t["lon"] + 3, t["lat"] + 2, str(n + 1), fontsize=8, color="#14213d", weight="bold")
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 85); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.text(0.99, 0.01, WM, ha="right", fontsize=6, color="#999999")
    plt.tight_layout(pad=0.2); plt.savefig(f"cons/map_{k}.png", facecolor="white"); plt.close()

pct95 = {}
hits = np.zeros((H, W), int); which = [[[] for _ in range(W)] for _ in range(1)]  # placeholder
masks = {}
for k, v in cons.items():
    s = np.load(f"cons/score_{k}.npy").astype(float); s = np.nan_to_num(s, nan=0)
    mini(k, v, s)
    pos = s[s > 0]
    thr = np.percentile(pos, 97) if pos.size else np.inf
    masks[k] = s >= thr
    hits += masks[k]

# multi-test sites: regions in the top 3% of the most constraints (coarsened to 2-degree blocks)
B = 12  # 12 cells of 10' = 2 degrees
hb = hits[:H - H % B, :W - W % B].reshape(H // B, B, W // B, B).max(axis=(1, 3))
order = np.argsort(hb.ravel())[::-1]; port = []
for f in order[:400]:
    bi, bj = divmod(int(f), W // B)
    if hb[bi, bj] < 3: break
    la = 90 - (bi + 0.5) * 2; lo = -180 + (bj + 0.5) * 2
    if any(abs(la - p["lat"]) < 6 and abs(lo - p["lon"]) < 12 for p in port): continue
    sl = (slice(bi * B, (bi + 1) * B), slice(bj * B, (bj + 1) * B))
    tests = [cons[k]["title"] for k in cons if masks[k][sl].any()]
    port.append({"lat": round(la, 1), "lon": round(lo, 1), "count": len(tests), "tests": tests})
    if len(port) >= 8: break
json.dump(port, open("cons/portfolio.json", "w"), indent=1)
for p in port: print(p["lat"], p["lon"], p["count"], p["tests"])

# overview: #1 site per constraint
fig, ax = plt.subplots(figsize=(13, 6.2), dpi=130)
ax.imshow(bg, extent=[-180, 180, -90, 90], cmap="gray", vmin=0, vmax=1, aspect="auto")
keys = list(cons.keys())
for n, k in enumerate(keys):
    t = cons[k]["top"][0]; c = PIN
    ax.plot(t["lon"], t["lat"], "o", ms=16, mfc=c, mec="white", mew=1.5, alpha=0.95)
    ax.text(t["lon"], t["lat"], str(n + 1), ha="center", va="center", fontsize=8, color="#0f1424", weight="bold")
ax.set_xlim(-180, 180); ax.set_ylim(-90, 85); ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)
fig.text(0.99, 0.01, WM, ha="right", fontsize=7, color="#999999")
plt.tight_layout(pad=0.3); plt.savefig("cons/overview.png", facecolor="white"); plt.close()
print("done")
