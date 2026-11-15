"""Render the three test maps and the verification chart (PNG, AI-assist watermark)."""
import sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

g = dict(np.load(sys.argv[1])); r = json.load(open(sys.argv[2])); out = sys.argv[3]
land, ice = g["land"], g["ice"]
WM = "Umbra by Team Forced Futures · NASA Space Apps 2026 · computed with AI-assisted code"
INK, MUTED, BLUE, GREEN = "#1d1d1f", "#6e6e73", "#1f6feb", "#0a8a5f"

def base(ax):
    bg = np.where(land, np.where(ice, 0.80, 0.90), 1.0)
    ax.imshow(bg, extent=[-180, 180, -90, 90], cmap="gray", vmin=0, vmax=1, aspect="auto")
    ax.set_xlim(-180, 180); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)

def map_png(key, title, sub, fname, vmax, ylim=(-60, 85), cmap="magma_r", floor=0.5, top_n=6, size=(13, 6), aspect="equal"):
    s = g[key].astype(float).copy(); s[~land | ice] = np.nan; s[s < floor] = np.nan
    fig, ax = plt.subplots(figsize=size, dpi=140)
    base(ax); ax.set_aspect(aspect)
    im = ax.imshow(s, extent=[-180, 180, -90, 90], cmap=cmap, vmin=0, vmax=vmax, aspect=aspect)
    for k in r["known"]:
        ax.plot(k["lon"], k["lat"], "o", mfc="none", mec=BLUE, ms=7, mew=1.6)
    if top_n:
        for p in r["top"][key][:top_n]:
            ax.plot(p["lon"], p["lat"], "*", color=GREEN, ms=12, mec="white", mew=0.6)
    ax.set_ylim(*ylim)
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, color=INK, weight="bold")
    ax.set_title(sub, loc="left", fontsize=10, color=MUTED)
    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01); cb.set_label("score (0-100)", color=MUTED)
    ax.plot([], [], "o", mfc="none", mec=BLUE, label="sites NASA already uses")
    if top_n: ax.plot([], [], "*", color=GREEN, ms=10, label="top new candidates")
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    fig.text(0.99, 0.01, WM, ha="right", fontsize=7, color="#aaaaaa")
    plt.tight_layout(); plt.savefig(f"{out}/{fname}", facecolor="white"); plt.close()

map_png("scoreAC", "Seal test: Moon dust + cold",
        "Sharp, dry, lifeless dust that is also cold. Ice sheets excluded. Grey = Earth adds too much (water, life, wind).",
        "map_seal.png", 28)
map_png("scoreB", "Low-sun navigation test",
        "Days per year the sun stays under 7 degrees AND the sky is clear AND the ground is dark (not snow).",
        "map_lowsun.png", 18, ylim=(52, 84), top_n=8, size=(13, 4.6), aspect=2.2)
map_png("scoreC", "Deep cold test",
        "Share of the gap to the Moon's shadowed craters (about -233 C) the coldest month reaches. Ice-free best ~26%; Antarctic ice sheet (grey) ~35%.",
        "map_cold.png", 36, ylim=(-90, 85), cmap="Blues", floor=0.1, top_n=0)

# verification chart: percentile of NASA's own sites on the seal test
ks = sorted(r["known"], key=lambda k: k["scoreAC_pct"])
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=140)
names = [k["name"].split(" (")[0] for k in ks]
vals = [k["scoreAC_pct"] for k in ks]
note = {"Mauna Kea, Hawaii": "data too coarse (18 km cell averages wet slopes)",
        "Haughton Crater, Devon Island": "soil map overstates Arctic organics; wet summer",
        "McMurdo Dry Valleys, Antarctica": "no soil data for Antarctica",
        "Bockfjord, Svalbard": "wet, vegetated: geology analog, not dust",
        "Askja / Icelandic highlands": "wet, vegetated: geology analog, not dust"}
cols = [GREEN if v >= 95 else ("#c9a227" if v >= 75 else "#c0c0c0") for v in vals]
ax.barh(names, vals, color=cols)
for i, (k, v) in enumerate(zip(ks, vals)):
    n = note.get(k["name"].split(" (")[0])
    ax.text(v + 1, i, f"{v:.0f}" + (f"   {n}" if n else ""), va="center", fontsize=8, color=MUTED)
ax.set_xlim(0, 100); ax.axvline(95, color=GREEN, lw=0.8, ls="--")
ax.set_xlabel("percentile among all ice-free land on Earth (seal test)", color=MUTED)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.suptitle("Verification: the engine found NASA's lunar test sites on its own", x=0.02, ha="left",
             fontsize=13, weight="bold", color=INK)
fig.text(0.99, 0.01, WM, ha="right", fontsize=7, color="#aaaaaa")
plt.tight_layout(); plt.savefig(f"{out}/verification.png", facecolor="white"); plt.close()
print("rendered")
