"""Umbra: six operational analogs (problems NASA is working on now). Output: analogs6.json, score_*.npy (10' grid), cons/analogs6.png

plume_blast     fine, loose, dry, flat ground that a landing engine would blast (SoilGrids texture, NASA POWER rain, terrain)
dirty_panels    most dust falling, least rain to wash it off, strong sun (NASA MERRA-2 dust deposition, POWER rain and UV)
dark_pocket     ground shaded at winter noon that is also very cold and dry: practice for work in permanent shadow
                (terrain horizon from AWS Terrain Tiles, NASA MODIS coldest nights, POWER rain)
radio_shadow    terrain that rises above 7 degrees in most directions, the height of Earth in the lunar south-pole sky
walk_back       same mix of slopes, at the same 5 km baseline, as the Moon's natural corridors (LOLA LDEM vs Earth terrain)
oxygen_feed     the best Moon-like feedstock rock (mare basalt or highland rock tests) within reach of a town
"""
import json, numpy as np, shapefile, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage
D = "/home/claude/data"
g = np.load("grid.npz"); land = g["land"].astype(bool); ice = g["ice"].astype(bool); ok = land & ~ice; LAT, LON = g["LAT"], g["LON"]
def ramp(x, lo, hi): return np.clip((x - lo) / (hi - lo), 0, 1)
def nz(a): return np.nan_to_num(a, nan=0.0)
rain = np.load(f"{D}/power_prec/power_prec_mm_yr.npy"); uv = np.load(f"{D}/power_uv/power_uv_index.npy")
depo = nz(np.load(f"{D}/gibs/merra2_dust_depo.npy"))
m = np.load(f"{D}/gibs/modis_lst.npz")
with np.errstate(all="ignore"): cold = np.nanmin(m["night"], axis=0) - 273.15
f = np.isfinite(cold); idx = ndimage.distance_transform_edt(~f, return_distances=False, return_indices=True); cold = cold[idx[0], idx[1]]
T6 = np.load("terrain6.npz"); tn = T6["n"]; hist = T6["slope_hist"]; flat = hist[0] + hist[1]
NL = np.load(f"{D}/new/layers.npz"); km_town = NL["km_to_town"]; unc = nz(NL["lith_unconsolidated"].astype(float))
silt, clay, soc, sand = nz(g["silt"]), nz(g["clay"]), nz(g["soc"]), nz(g["sand"]); has_soil = g["has_soil"].astype(bool)
def rank(a): out = np.zeros(a.shape, np.float32); v = a[ok]; o = v.argsort().argsort(); out[ok] = (o + .5) / len(v); return out
MW = json.load(open("moon_walk.json")); hc = np.array(MW["corridor_hist"])
S = {}
dry = 1 - ramp(rain, 50, 300)
S["plume_blast"] = 100 * ramp(silt, 15, 45) * (1 - ramp(clay, 15, 35)) * (1 - ramp(soc, 20, 80)) * dry * ramp(flat, .6, .95) * (0.6 + 0.4 * ramp(unc, 0, .6)) * has_soil * ok
S["dirty_panels"] = 100 * rank(depo) * (1 - ramp(rain, 25, 250)) * rank(uv) * ok
S["dark_pocket"] = 100 * ramp(T6["winter_shade"], 0, .15) * ramp(-cold, 10, 40) * (1 - ramp(rain, 100, 600)) * (T6["shade_n"] > 20) * ok
S["radio_shadow"] = 100 * ramp(T6["radio_block"], 0, .25) * (tn > 20) * ok
sim = 1 - 0.5 * np.abs(hist - hc[:, None, None]).sum(0)
S["walk_back"] = 100 * ramp(sim, .6, .95) * (1 - ramp(rain, 100, 500)) * (tn > 20) * ok
mb = nz(np.load("cons/score_mare_basalt.npy")); hr = nz(np.load("cons/score_highland_rock.npy"))
S["oxygen_feed"] = np.maximum(mb, hr) * (1 - ramp(km_town, 150, 600)) * ok
for k, v in S.items(): np.save(f"cons/score_{k}.npy", v.astype(np.float32))

r = shapefile.Reader(f"{D}/new/pop/ne_10m_populated_places_simple.shp")
P = [(x["latitude"], x["longitude"], x["name"], x["adm0name"]) for x in r.records()]; PL = np.array([[p[0], p[1]] for p in P])
def name(lat, lon):
    d = np.hypot(PL[:, 0] - lat, (PL[:, 1] - lon) * np.cos(np.radians(lat))); k = d.argmin(); return f"near {P[k][2]}, {P[k][3]}"
def top(score, n=5, block=18):
    s = ndimage.uniform_filter(score, 3); out = []
    for _ in range(n):
        i, j = np.unravel_index(s.argmax(), s.shape)
        if s[i, j] <= 0: break
        out.append(dict(lat=round(float(LAT[i, j]), 2), lon=round(float(LON[i, j]), 2), score=round(float(score[i, j]), 1), place=name(LAT[i, j], LON[i, j])))
        s[max(i - block, 0):i + block, max(j - block, 0):j + block] = 0
    return out
TITLES = dict(plume_blast="Landing-blast ground", dirty_panels="Dirty solar panels", dark_pocket="Work in the shadows",
              radio_shadow="Radio shadow", walk_back="The walk back", oxygen_feed="Oxygen-plant feedstock")
res = {k: dict(title=TITLES[k], top=top(v), share_scored=float((v > 50).sum() / ok.sum())) for k, v in S.items()}
res["walk_back"]["moon"] = MW
json.dump(res, open("analogs6.json", "w"), indent=1)
for k, v in res.items(): print(k, [t["place"] for t in v["top"]])

fig, axs = plt.subplots(3, 2, figsize=(14, 11), facecolor="#0b0d12")
for ax, (k, v) in zip(axs.ravel(), S.items()):
    ax.set_facecolor("#0b0d12"); ax.imshow(np.where(land, v, np.nan), cmap="magma", vmin=0, vmax=100, extent=[-180, 180, -90, 90])
    for n_, t in enumerate(res[k]["top"], 1):
        ax.plot(t["lon"], t["lat"], "o", mfc="none", mec="#7CFFB2", ms=10, mew=1.8); ax.text(t["lon"] + 3, t["lat"] + 2, str(n_), color="#7CFFB2", fontsize=9, weight="bold")
    ax.set_title(TITLES[k], color="w", fontsize=12); ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-60, 84)
fig.suptitle("Six operational analogs: where Earth can rehearse what Artemis must solve", color="w", fontsize=14)
fig.tight_layout(); fig.savefig("cons/analogs6.png", dpi=90, facecolor=fig.get_facecolor())
