"""Umbra: NASA POWER all-sky surface albedo climatology (ALLSKY_SRF_ALB, annual mean), global, onto the 10' grid."""
import sys, json, os, time, urllib.request, numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy import ndimage
out = sys.argv[1]
def get(t):
    la, lo = t; fn = f"{out}/A_{la}_{lo}.json"
    if os.path.exists(fn): return 1
    url = (f"https://power.larc.nasa.gov/api/temporal/climatology/regional?parameters=ALLSKY_SRF_ALB&community=AG"
           f"&latitude-min={max(la,-90)}&latitude-max={min(la+9.5,90)}&longitude-min={lo}&longitude-max={min(lo+9.5,180)}&format=JSON")
    for a in range(4):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=120))
            if "features" in d:
                json.dump([(f["geometry"]["coordinates"][:2], f["properties"]["parameter"]["ALLSKY_SRF_ALB"]["ANN"]) for f in d["features"]], open(fn, "w")); return 1
        except Exception as e: pass
        time.sleep(2 * (a + 1))
    return 0
tiles = [(la, lo) for la in range(-90, 90, 10) for lo in range(-180, 180, 10)]
with ThreadPoolExecutor(5) as ex: ok = list(ex.map(get, tiles))
print("tiles ok", sum(ok), "of", len(tiles))
H, W = 1080, 2160; g = np.full((H, W), np.nan, np.float32)
for la, lo in tiles:
    fn = f"{out}/A_{la}_{lo}.json"
    if not os.path.exists(fn): continue
    for (x, y), v in json.load(open(fn)):
        if v is None or v < -900: continue
        i0 = int(np.clip((90 - (y + .25)) * 6, 0, H - 1)); i1 = int(np.clip((90 - (y - .25)) * 6, 0, H)); j0 = int(np.clip((x - .3125 + 180) * 6, 0, W - 1)); j1 = int(np.clip((x + .3125 + 180) * 6, 0, W))
        g[i0:max(i1, i0 + 1), j0:max(j1, j0 + 1)] = v
m = np.isfinite(g); idx = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True)
g = g[idx[0], idx[1]]
np.save(f"{out}/power_albedo.npy", g); print("coverage before fill", float(m.mean()), "pct", np.percentile(g, [5, 50, 95]))
