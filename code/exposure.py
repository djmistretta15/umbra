"""Umbra: exposure analogs. Where on Earth do suits, seals and gear age the way they will on the Moon and Mars?

Not wear and tear from use: slow chemical and physical damage from simply sitting outside.
  UV          NASA POWER surface UV index (CERES SYN1deg, 2001-2025 mean). Moon and Mars surfaces have far more.
  Thermal     NASA MODIS Terra day minus night land temperature (2018-2022). Cycling cracks seals and joints.
  Dust        NASA MERRA-2 dust near the ground (2018-2022), via GIBS. Abrasion and clinging dust.
  Dryness     NASA POWER precipitation. Dry air lets dust charge up and stick, like lunar dust.
  Fresh glass Smithsonian GVP volcanoes active since 1900, in dry ground: sharp, unweathered glass shards,
              the closest Earth gets to freshly broken lunar dust.
Each factor is ranked against all ice-free land (0 to 1). An exposure test bed needs all four at once,
so the combined score is their geometric mean. Output: exposure.json, cons/exposure.png
"""
import sys, json, numpy as np, pandas as pd, shapefile, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage
D = sys.argv[1]
g = np.load("grid.npz"); land = g["land"].astype(bool) & ~g["ice"].astype(bool); LAT, LON = g["LAT"], g["LON"]
uv = np.load(f"{D}/power_uv/power_uv_index.npy")
m = np.load(f"{D}/gibs/modis_lst.npz"); day, night = m["day"], m["night"]
with np.errstate(all="ignore"): swing = np.nanmean(day - night, axis=0)
ok = np.isfinite(swing); idx = ndimage.distance_transform_edt(~ok, return_distances=False, return_indices=True); swing = swing[idx[0], idx[1]]
dust = np.nan_to_num(np.load(f"{D}/gibs/merra2_dust.npy"))
prec = np.load(f"{D}/power_prec/power_prec_mm_yr.npy")

def rank(a):
    out = np.zeros_like(a, dtype=np.float32); v = a[land]; o = v.argsort().argsort()
    out[land] = (o + 0.5) / len(v); return out
R = dict(uv=rank(uv), thermal=rank(swing), dust=rank(dust), dry=rank(-prec))
combo = np.where(land, (R["uv"] * R["thermal"] * R["dust"] * R["dry"]) ** 0.25, 0)

v = pd.read_csv(f"{D}/new/volcanoes.csv")
v = v[pd.to_numeric(v.Last_Eruption_Year, errors="coerce") >= 1900]
H, W = LAT.shape; ash = np.zeros((H, W), np.float32)
ii = np.clip(((90 - v.Latitude.values) * 6).astype(int), 0, H - 1); jj = np.clip(((v.Longitude.values + 180) * 6).astype(int), 0, W - 1)
ash[ii, jj] = 1
ash = ndimage.gaussian_filter(ash, 3) > 1e-3   # within about 50 km
fresh = np.where(land & ash, R["dry"] * (0.5 + 0.5 * R["uv"]), 0)

r = shapefile.Reader(f"{D}/new/pop/ne_10m_populated_places_simple.shp")
P = [(x["latitude"], x["longitude"], x["name"], x["adm0name"]) for x in r.records()]
PL = np.array([[p[0], p[1]] for p in P])
def name(lat, lon):
    d = np.hypot(PL[:, 0] - lat, (PL[:, 1] - lon) * np.cos(np.radians(lat))); k = d.argmin()
    return f"near {P[k][2]}, {P[k][3]}", round(float(d[k] * 111), 0)
def top(score, n=8, block=12):
    S = score.copy(); out = []
    for _ in range(n):
        i, j = np.unravel_index(S.argmax(), S.shape)
        if S[i, j] <= 0: break
        nm, km = name(LAT[i, j], LON[i, j])
        out.append(dict(lat=round(float(LAT[i, j]), 2), lon=round(float(LON[i, j]), 2), score=round(float(S[i, j]) * 100, 1),
                        place=nm, km_to_place=km, uv=round(float(uv[i, j]), 2), swing_C=round(float(swing[i, j]), 1),
                        dust_ugm3=round(float(dust[i, j]), 1), rain_mm=round(float(prec[i, j]), 0)))
        S[max(i - block, 0):i + block, max(j - block, 0):j + block] = 0
    return out
res = dict(
    method="Rank each NASA layer across ice-free land; exposure test bed = geometric mean of UV, thermal cycling, dust, dryness.",
    earth_max=dict(uv_index=float(uv[land].max()), swing_C=float(np.percentile(swing[land], 99.9)), dust_ugm3=float(dust[land].max())),
    combined_top=top(combo), fresh_glass_top=top(fresh),
    uv_top=top(np.where(land, R["uv"] * (uv / uv[land].max()), 0), 5),
    sources=["NASA POWER ALLSKY_SFC_UV_INDEX", "NASA POWER PRECTOTCORR", "NASA MODIS Terra LST monthly (GIBS)",
             "NASA MERRA-2 dust surface mass concentration monthly (GIBS)", "Smithsonian GVP Holocene volcanoes"])
json.dump(res, open("exposure.json", "w"), indent=1)
for k in ("combined_top", "fresh_glass_top", "uv_top"):
    print(k); [print("  ", t) for t in res[k]]
print(res["earth_max"])

fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0b0d12"); ax.set_facecolor("#0b0d12")
ax.imshow(np.where(land, combo, np.nan), cmap="magma", vmin=0.5, vmax=1, extent=[-180, 180, -90, 90])
ax.imshow(np.where(land, np.nan, 0.15), cmap="gray", vmin=0, vmax=1, extent=[-180, 180, -90, 90])
for k, t in enumerate(res["combined_top"], 1):
    ax.plot(t["lon"], t["lat"], "o", mfc="none", mec="#7CFFB2", ms=12, mew=2); ax.text(t["lon"] + 3, t["lat"] + 2, str(k), color="#7CFFB2", weight="bold")
for t in res["fresh_glass_top"]:
    ax.plot(t["lon"], t["lat"], "^", color="#5ecbff", ms=8)
ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-60, 85)
ax.set_title("Exposure analogs: where gear ages like it will on the Moon and Mars\nNASA UV + MODIS thermal cycling + MERRA-2 dust + dryness (rings)   fresh volcanic glass in dry ground (triangles)", color="w", fontsize=11)
fig.tight_layout(); fig.savefig("cons/exposure.png", dpi=100, facecolor=fig.get_facecolor())
