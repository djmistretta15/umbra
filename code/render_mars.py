import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

m = np.load("mars_maps.npz")
BG, TX, MU = "#0b1020", "#e8ecf4", "#9aa6bd"
fig, ax = plt.subplots(1, 3, figsize=(16, 3.9), facecolor=BG)
ext = [-180, 180, -90, 90]
def frame(a, t, sub):
    a.set_facecolor(BG); a.tick_params(colors=MU, labelsize=8)
    for sp in a.spines.values(): sp.set_color("#2a3550")
    a.set_title(t, color=TX, fontsize=13, loc="left", pad=22, fontweight="bold")
    a.text(0, 1.03, sub, transform=a.transAxes, color=MU, fontsize=9.5)
def cb(im, a):
    c = fig.colorbar(im, ax=a, fraction=0.025, pad=0.02); c.ax.tick_params(colors=MU, labelsize=8)

im = ax[0].imshow(m["P"], cmap="plasma", vmin=300, vmax=1100, extent=ext)
frame(ax[0], "Air at the ground (MOLA)", "Surface pressure, Pa (Earth sea level: 101,325)")
cb(im, ax[0])
im = ax[1].imshow(m["ti"], cmap="cividis", vmin=30, vmax=500, extent=ext)
frame(ax[1], "What the ground is made of (TES)", "Thermal inertia: dark = loose dust, bright = firm")
cb(im, ax[1])
im = ax[2].imshow(m["h2o"], cmap="Blues", vmin=1, vmax=8, extent=ext)
ax[2].imshow(np.ma.masked_where(~m["base"], m["base"]), cmap=matplotlib.colors.ListedColormap(["#ffb547"]), extent=ext, alpha=0.95)
frame(ax[2], "Water in the top metre (Odyssey GRS)", "Weight %; amber = water, thicker air, firm ground")
cb(im, ax[2])
fig.text(0.01, 0.01, "Umbra by Team Forced Futures · NASA Space Apps 2026 · MGS MOLA and TES, Mars Odyssey GRS (NASA PDS) · computed with AI-assisted code", color=MU, fontsize=9)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig("cons/mars_orbiters.png", dpi=110, facecolor=BG)
print("ok")
