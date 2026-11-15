import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

m = np.load("moon_maps.npz"); tmax = np.load("moon_tmax.npy")
BG, TX, MU = "#0b1020", "#e8ecf4", "#9aa6bd"
fig, ax = plt.subplots(1, 3, figsize=(15, 5.6), facecolor=BG)
def frame(a, t, sub):
    a.set_facecolor(BG); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values(): sp.set_color("#2a3550")
    a.set_title(t, color=TX, fontsize=13, loc="left", pad=22, fontweight="bold")
    a.text(0, 1.02, sub, transform=a.transAxes, color=MU, fontsize=9.5)

im = ax[0].imshow(tmax, cmap="inferno", vmin=30, vmax=320, extent=[-305, 305, -305, 305])
frame(ax[0], "Hottest it ever gets (Diviner)", "Annual maximum temperature, 80S to pole, K")
c = fig.colorbar(im, ax=ax[0], fraction=0.046, pad=0.02); c.ax.tick_params(colors=MU)
ax[0].text(0.5, -0.1, "black crater floors never pass 110 K: ice can sit on the surface", transform=ax[0].transAxes, color=TX, fontsize=9, ha="center")

v = m["vis"]; e = 151.7
im = ax[1].imshow(v, cmap="gray", vmin=0, vmax=0.9, extent=[-e, e, -e, e])
ax[1].imshow(np.ma.masked_where(~m["psr"], m["psr"]), cmap=matplotlib.colors.ListedColormap(["#33c3ff"]), alpha=0.9, extent=[-e, e, -e, e])
frame(ax[1], "Sunlight and permanent shadow (LOLA)", "Fraction of time lit, 85S to pole; cyan = never lit")
c = fig.colorbar(im, ax=ax[1], fraction=0.046, pad=0.02); c.ax.tick_params(colors=MU)

im = ax[2].imshow(m["slope"], cmap="viridis", vmin=0, vmax=30, extent=[-e, e, -e, e])
frame(ax[2], "Ground slope (LOLA, 40 m)", "Degrees, 85S to pole; gaps = no 40 m data")
c = fig.colorbar(im, ax=ax[2], fraction=0.046, pad=0.02); c.ax.tick_params(colors=MU)
for a in ax:
    a.tick_params(colors=MU)
fig.text(0.01, 0.01, "Umbra by Team Forced Futures · NASA Space Apps 2026 · LRO Diviner and LOLA data (NASA PDS) · computed with AI-assisted code",
         color=MU, fontsize=9)
plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("cons/moon_lro.png", dpi=110, facecolor=BG)
print("ok")
