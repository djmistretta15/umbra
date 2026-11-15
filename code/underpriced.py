"""Umbra: underpriced analogs. One place, many analog jobs, little attention.

Value  = jobs: how many of Umbra's 43 analog layers a 2-degree block ranks in the top 3% on (same rule as the expedition portfolio),
         plus how many of the challenge's 9 dimensions those jobs span.
Price  = attention: closeness to the analog sites already studied (Haughton, Dry Valleys, Atacama, Rio Tinto, Iceland and others).
Underpriced = jobs x (1 - attention), attention = exp(-distance / 400 km).
Output: underpriced.json, cons/underpriced.png
"""
import json, glob, os, numpy as np, shapefile, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
g = np.load("grid.npz"); land = g["land"].astype(bool); LAT, LON = g["LAT"], g["LON"]
DIM = {  # challenge dimension for each layer
 "geology": ["mare_basalt", "highland_rock", "impact_rock", "volcanic_glass", "ancient_crust", "magnetic_memory", "oxygen_feed"],
 "terrain": ["pad_rock", "featureless", "walk_back", "radio_shadow", "plume_blast"],
 "temperature & light": ["deep_cold", "thermal_swing", "low_sun", "lunar_night", "power_ridge", "radiative_cold", "dark_pocket", "sun_ice_edge"],
 "water & ice": ["dry_permafrost", "ice_ratio"],
 "dust & wind": ["seal_dust", "dust_devils", "dust_storm", "soft_sand", "sand_ratio", "dust_mantle", "dirty_panels", "thin_air"],
 "life & biosignatures": ["mars_hyperarid", "salt_biosig", "oxidant_soil", "hydrothermal", "dried_lakes", "erasers_off"],
 "underground": ["lava_tubes", "karst_caves", "ringing_ground"],
 "fields & signals": ["no_compass", "radio_quiet", "seismic_quiet", "radiation"],
}
L2D = {k: d for d, ks in DIM.items() for k in ks}
S = {os.path.basename(f)[6:-4]: np.nan_to_num(np.load(f)) for f in sorted(glob.glob("cons/score_*.npy"))}
ex = np.load("live_extra.npz")["ringing_ground"].astype(float); ex[ex == 255] = 0
S["ringing_ground"] = np.kron(ex, np.ones((3, 3)))[:LAT.shape[0], :LAT.shape[1]] * land
assert set(S) <= set(L2D), set(S) - set(L2D)
B = 12; H, W = LAT.shape[0] // B, LAT.shape[1] // B
blat = 90 - (np.arange(H) + .5) * 2; blon = -180 + (np.arange(W) + .5) * 2
hits = np.zeros((len(S), H, W), bool); names = list(S)
for n, (k, a) in enumerate(S.items()):
    v = a[land & (a > 0)]
    if not v.size: continue
    thr = np.percentile(v, 97); bm = a.reshape(H, B, W, B).max((1, 3)); hits[n] = bm >= max(thr, 1e-6)
jobs = hits.sum(0)
dims = np.zeros((H, W), int)
for d in DIM: dims += hits[[i for i, k in enumerate(names) if L2D[k] == d]].any(0)
KNOWN = [("Haughton Crater", 75.43, -89.82), ("McMurdo Dry Valleys", -77.55, 161.5), ("Atacama (Yungay)", -24.08, -69.92),
         ("Mauna Kea / HI-SEAS", 19.8, -155.47), ("Black Point Lava Flow", 35.68, -111.43), ("Meteor Crater", 35.03, -111.02),
         ("Mars Desert Research Station", 38.41, -110.79), ("Svalbard (AMASE)", 79.43, 13.93), ("Salar de Uyuni", -20.13, -67.49),
         ("Eureka, Ellesmere", 79.99, -85.93), ("Concordia Station", -75.10, 123.33), ("Qaidam Basin", 37.5, 93.0),
         ("Rio Tinto", 37.7, -6.55), ("Lanzarote", 29.0, -13.6), ("Iceland (Holuhraun)", 64.85, -16.83), ("Kilauea", 19.42, -155.29),
         ("Pilbara", -21.2, 119.4), ("Ries Crater", 48.88, 10.56), ("Sudbury", 46.6, -81.2), ("Craters of the Moon", 43.42, -113.52),
         ("Death Valley", 36.5, -117.0), ("White Sands", 32.8, -106.3), ("Sahara (Tindouf / Morocco)", 28.0, -8.0)]
la, lo = np.meshgrid(blat, blon, indexing="ij")
def km(a1, o1, a2, o2):
    a1, o1, a2, o2 = map(np.radians, (a1, o1, a2, o2))
    return 6371 * np.arccos(np.clip(np.sin(a1) * np.sin(a2) + np.cos(a1) * np.cos(a2) * np.cos(o1 - o2), -1, 1))
dist = np.min([km(la, lo, a, o) for _, a, o in KNOWN], axis=0)
att = np.exp(-dist / 400)
under = jobs * (1 - att)
r = shapefile.Reader("/home/claude/data/new/pop/ne_10m_populated_places_simple.shp")
P = [(x["latitude"], x["longitude"], x["name"], x["adm0name"]) for x in r.records()]; PL = np.array([[p[0], p[1]] for p in P])
def place(a, o):
    d = np.hypot(PL[:, 0] - a, (PL[:, 1] - o) * np.cos(np.radians(a))); k = d.argmin(); return f"{P[k][2]}, {P[k][3]}"
def rows(score, n):
    s = score.astype(float).copy(); out = []
    for _ in range(n):
        i, j = np.unravel_index(s.argmax(), s.shape)
        if s[i, j] <= 0: break
        ks = [names[q] for q in np.nonzero(hits[:, i, j])[0]]
        out.append(dict(lat=float(blat[i]), lon=float(blon[j]), near=place(blat[i], blon[j]), jobs=int(jobs[i, j]), dimensions=int(dims[i, j]),
                        km_to_studied_site=int(dist[i, j]), attention=round(float(att[i, j]), 2), underpriced=round(float(under[i, j]), 1), layers=ks))
        s[max(i - 2, 0):i + 3, max(j - 2, 0):j + 3] = 0
    return out
studied = []
for nm, a, o in KNOWN:
    i = int((90 - a) // 2); j = int((o + 180) // 2); studied.append(dict(site=nm, jobs=int(jobs[i, j]), dimensions=int(dims[i, j])))
res = dict(method=__doc__.strip(), n_layers=len(S), top_underpriced=rows(under, 12), top_jobs=rows(jobs, 8),
           studied_sites=sorted(studied, key=lambda x: -x["jobs"]), median_jobs_land=float(np.median(jobs[jobs > 0])))
json.dump(res, open("underpriced.json", "w"), indent=1)
for t in res["top_underpriced"]: print(t["near"], t["jobs"], t["dimensions"], t["km_to_studied_site"], t["underpriced"])
print("studied:", [(s["site"], s["jobs"]) for s in res["studied_sites"]][:12])

fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0b0d12"); ax.set_facecolor("#0b0d12")
ax.imshow(np.where(jobs > 0, under, np.nan), cmap="magma", extent=[-180, 180, -90, 90], vmin=0, vmax=max(under.max(), 1))
ax.contour(blon, blat, np.kron(land.reshape(H, B, W, B).any((1, 3)), 1).astype(float), [0.5], colors="#555", linewidths=.5)
for nm, a, o in KNOWN: ax.plot(o, a, "x", color="#9ecbff", ms=6, mew=1.5)
for k, t in enumerate(res["top_underpriced"][:10], 1):
    ax.plot(t["lon"], t["lat"], "o", mfc="none", mec="#7CFFB2", ms=13, mew=2); ax.text(t["lon"] + 3, t["lat"] + 2, str(k), color="#7CFFB2", weight="bold")
ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-80, 84)
ax.set_title("Underpriced analogs: many analog jobs, little attention\nbrightness = jobs x distance from studied sites   blue x = already-studied analog sites   rings = top 10", color="w", fontsize=11)
fig.tight_layout(); fig.savefig("cons/underpriced.png", dpi=100, facecolor=fig.get_facecolor())
