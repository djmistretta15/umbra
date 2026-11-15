"""Pack the engine's 19 constraint layers (0.5 deg) + countries + metadata for the live dashboard."""
import json, gzip, base64, numpy as np, rasterio
from rasterio.features import rasterize

C = json.load(open("cons/constraints.json"))
keys = list(C["constraints"].keys())
H, W, F = 360, 720, 3

def pool(a):
    a = a.reshape(H, F, W, F)
    with np.errstate(all="ignore"):
        import warnings; warnings.simplefilter("ignore")
        return np.nanmax(np.nanmax(a, 3), 1)

blob = bytearray()
for k in keys:
    s = pool(np.load(f"cons/score_{k}.npy").astype(np.float32))
    u = np.where(np.isfinite(s), np.clip(np.round(s / max(np.nanmax(s), 1e-6) * 254), 0, 254), 255).astype(np.uint8)
    blob += u.tobytes()

g = np.load("grid.npz")
land = pool(np.where(g["land"], 1.0, np.nan)) == 1
blob += land.astype(np.uint8).tobytes()

cg = json.load(open("/home/claude/data/ne/countries.geojson"))
names = [f["properties"].get("ADMIN") or f["properties"].get("NAME") for f in cg["features"]]
cid = rasterize([(f["geometry"], i + 1) for i, f in enumerate(cg["features"])], out_shape=(H, W),
                transform=rasterio.transform.from_origin(-180, 90, 0.5, 0.5), fill=0, dtype="int32", all_touched=True).astype(np.uint16)
blob += cid.astype("<u2").tobytes()
EX = np.load("live_extra.npz"); EXM = json.load(open("live_extra.json"))
extra = [m["key"] for m in EXM["measures"]] + ["ringing_ground"] + [o["key"] for o in EXM["ops"]]
for k in extra: blob += EX[k].astype(np.uint8).tobytes()
# engine top-3% masks at full resolution, pooled to 0.5 deg, so Live's overlap and job counts match the engine exactly
mask_keys = list(keys) + [o["key"] for o in EXM["ops"]] + ["ringing_ground"]
for k in mask_keys:
    if k == "ringing_ground":
        a = EX[k].astype(float); a[a == 255] = 0; pos = a[a > 0]; m = a >= max(np.percentile(pos, 97), 1e-6)
    else:
        a = np.nan_to_num(np.load(f"cons/score_{k}.npy").astype(float)); pos = a[a > 0]
        m10 = a >= (np.percentile(pos, 97) if pos.size else np.inf); m = m10.reshape(H, 3, W, 3).any((1, 3))
    blob += np.packbits(m.astype(np.uint8).ravel()).tobytes()

meta = dict(H=H, W=W, keys=keys, names=names, extra=extra, masks=mask_keys, measures=EXM["measures"], ringing=EXM["ringing"], ops=EXM["ops"], presets=EXM["presets"],
            cons={k: {x: v[x] for x in ("title", "world", "stage", "why", "gap", "conf", "moon", "mars") if x in v} for k, v in C["constraints"].items()},
            cant=C["earth_cant"],
            known=[["Haughton Crater", 75.43, -89.82], ["McMurdo Dry Valleys", -77.55, 161.5], ["Atacama (Yungay)", -24.08, -69.92],
                   ["Mauna Kea / HI-SEAS", 19.80, -155.47], ["Black Point Lava Flow", 35.68, -111.43], ["Meteor Crater", 35.03, -111.02],
                   ["Mars Desert Research Station", 38.41, -110.79], ["Svalbard (AMASE)", 79.43, 13.93], ["Salar de Uyuni", -20.13, -67.49],
                   ["Eureka, Ellesmere", 79.99, -85.93], ["Concordia Station", -75.10, 123.33], ["Qaidam Basin", 37.5, 93.0],
                   ["Rio Tinto", 37.7, -6.55], ["Lanzarote", 29.0, -13.6], ["Iceland (Holuhraun)", 64.85, -16.83], ["Kilauea", 19.42, -155.29],
                   ["Pilbara", -21.2, 119.4], ["Ries Crater", 48.88, 10.56], ["Sudbury", 46.6, -81.2], ["Craters of the Moon", 43.42, -113.52],
                   ["Death Valley", 36.5, -117.0], ["White Sands", 32.8, -106.3], ["Sahara (Tindouf / Morocco)", 28.0, -8.0]])
b64 = base64.b64encode(gzip.compress(bytes(blob), 9)).decode()
open("live_data.js", "w").write(f"window.UMBRA_META={json.dumps(meta)};\nwindow.UMBRA_BLOB='{b64}';\n")
print(len(blob), len(b64))

# sample files for judges to drag in
import os; os.makedirs("bundle/samples", exist_ok=True)
wind = g["wind"].astype(np.float32)
wp = pool(np.where(g["land"], wind, np.nan))
with rasterio.open("bundle/samples/sample_wind_0p5deg.tif", "w", driver="GTiff", height=H, width=W, count=1, dtype="float32",
                   crs="EPSG:4326", transform=rasterio.transform.from_origin(-180, 90, 0.5, 0.5), nodata=-9999) as d:
    d.write(np.where(np.isfinite(wp), wp, -9999).astype(np.float32), 1)
rows = ["lat,lon,wind_m_s"]
for i in range(0, H, 2):
    for j in range(0, W, 2):
        v = wp[i, j]
        if np.isfinite(v): rows.append(f"{90 - (i + .5) * .5:.2f},{-180 + (j + .5) * .5:.2f},{v:.2f}")
open("bundle/samples/sample_wind_points.csv", "w").write("\n".join(rows))
open("bundle/samples/sample_sites.csv", "w").write("name,lat,lon\nDevon Island (Haughton),75.4,-89.8\nAtacama Yungay,-24.1,-69.9\nRio Tinto Spain,37.7,-6.6\nLanzarote,29.0,-13.6\nUtah MDRS,38.4,-110.8\nIceland Holuhraun,64.9,-16.8\nSvalbard,79.4,13.9\nAntarctica Dry Valleys,-77.5,161.5\nWestern Tibet (Umbra),35.0,81.0\nEureka Ellesmere (Umbra),80.0,-85.9\n")
print("samples ok")
