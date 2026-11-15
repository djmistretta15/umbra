"""Umbra: NASA MERRA-2 total dust deposition (dry + wet, monthly, 2018-2022) via NASA GIBS, decoded with NASA colour map.
Output: data/gibs/merra2_dust_depo.npy, dust falling on the ground in grams per square metre per year, on the 10' grid."""
import sys, re, os, numpy as np, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
D = sys.argv[1]; YEARS = [2018, 2019, 2020, 2021, 2022]
L = "MERRA2_Total_Dust_Deposition_Dry_Wet_Monthly"
BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/" + L + "/default/{y}-{m:02d}-01/2km/2/{r}/{c}.png"
lut = {}
for rgb, lo, hi in re.findall(r'rgb="(\d+,\d+,\d+)" transparent="false"[^>]*value="\[([-\w.+]+),([-\w.+]+)\)"', open(f"{D}/depo_cm.xml").read()):
    lo = 0.0 if "INF" in lo else float(lo); hi = lo * 1.1 if "INF" in hi else float(hi)
    lut[tuple(map(int, rgb.split(",")))] = max((lo + hi) / 2, 0) * 3.156e10   # kg/m2/s -> g/m2/yr
os.makedirs(f"{D}/depo", exist_ok=True)
def tile(y, m, r, c):
    p = f"{D}/depo/{y}_{m:02d}_{r}_{c}.png"
    if not os.path.exists(p):
        for _ in range(4):
            try: open(p, "wb").write(urllib.request.urlopen(BASE.format(y=y, m=m, r=r, c=c), timeout=60).read()); break
            except Exception: pass
        else: return None
    return p
def month(y, m):
    full = np.full((3 * 512, 5 * 512), np.nan, np.float32)
    for r in range(3):
        for c in range(5):
            p = tile(y, m, r, c)
            if not p: continue
            a = np.asarray(Image.open(p).convert("RGBA"))
            key = (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]
            out = np.full(key.shape, np.nan, np.float32)
            for (R, G, B), v in lut.items(): out[(key == ((R << 16) | (G << 8) | B)) & (a[..., 3] > 0)] = v
            full[r * 512:(r + 1) * 512, c * 512:(c + 1) * 512] = out
    return full[:1280, :2560]
jobs = [(y, m) for y in YEARS for m in range(1, 13)]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda j: [tile(j[0], j[1], r, c) for r in range(3) for c in range(5)], jobs))
S = np.zeros((1280, 2560)); N = np.zeros((1280, 2560))
for y, m in jobs:
    a = month(y, m); ok = np.isfinite(a); S[ok] += a[ok]; N[ok] += 1
mean = np.where(N > 0, S / np.maximum(N, 1), np.nan)
H, W = 1080, 2160
ii = np.clip(((np.arange(H) + .5) / 6 / 0.140625).astype(int), 0, 1279); jj = np.clip(((np.arange(W) + .5) / 6 / 0.140625).astype(int), 0, 2559)
g = mean[ii][:, jj].astype(np.float32)
np.save(f"{D}/merra2_dust_depo.npy", g); print("coverage", float(np.isfinite(g).mean()), "pct g/m2/yr", np.nanpercentile(g, [50, 90, 99]))
