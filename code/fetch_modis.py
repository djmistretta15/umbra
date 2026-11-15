"""Umbra: NASA MODIS land surface temperature (Terra MOD11C3 monthly, day and night) via NASA GIBS.

No login needed. GIBS serves the product as colour-keyed tiles; NASA's published colour map
(MODIS_Land_Surface_Temp.xml) converts each colour back to a temperature bin 0.6 K wide (200-350 K).
Output: data/gibs/modis_lst.npz with 12-month day and night climatologies on the engine's 10' grid.
"""
import sys, re, io, os, numpy as np, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

D = sys.argv[1]; YEARS = [2018, 2019, 2020, 2021, 2022]
BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_L3_Land_Surface_Temp_Monthly_{dn}/default/{y}-{m:02d}-01/2km/2/{r}/{c}.png"
# colour -> Kelvin (bin centre)
lut = {}
for rgb, lo, hi in re.findall(r'rgb="(\d+,\d+,\d+)" transparent="false"[^>]*value="\[([\d.]+),([\d.]+)\)"', open(f"{D}/lst_cm.xml").read()):
    lut[tuple(map(int, rgb.split(",")))] = (float(lo) + float(hi)) / 2 if float(lo) >= 200 else 199.7
proxy = urllib.request.build_opener()

def tile(dn, y, m, r, c):
    p = f"{D}/tiles/{dn}_{y}_{m:02d}_{r}_{c}.png"
    if not os.path.exists(p):
        for _ in range(4):
            try:
                b = proxy.open(BASE.format(dn=dn, y=y, m=m, r=r, c=c), timeout=60).read(); open(p, "wb").write(b); break
            except Exception as e: err = e
        else: return None
    return p

def month(dn, y, m):
    full = np.full((3 * 512, 5 * 512), np.nan, np.float32)
    for r in range(3):
        for c in range(5):
            p = tile(dn, y, m, r, c)
            if not p: continue
            im = Image.open(p).convert("RGBA"); a = np.asarray(im)
            key = (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]
            out = np.full(key.shape, np.nan, np.float32)
            for (R, G, B), v in lut.items():
                out[(key == ((R << 16) | (G << 8) | B)) & (a[..., 3] > 0)] = v
            full[r * 512:(r + 1) * 512, c * 512:(c + 1) * 512] = out
    return full[:1280, :2560]          # 0.140625 deg/px: 180/0.140625 = 1280 rows, 2560 cols

jobs = [(dn, y, m) for dn in ("Day", "Night") for y in YEARS for m in range(1, 13)]
with ThreadPoolExecutor(16) as ex:
    list(ex.map(lambda j: [tile(j[0], j[1], j[2], r, c) for r in range(3) for c in range(5)], jobs))
res = {}
for dn in ("Day", "Night"):
    clim = np.zeros((12, 1280, 2560), np.float32); n = np.zeros((12, 1280, 2560), np.float32)
    for y in YEARS:
        for m in range(1, 13):
            a = month(dn, y, m); ok = np.isfinite(a)
            clim[m - 1][ok] += a[ok]; n[m - 1][ok] += 1
    res[dn] = np.where(n > 0, clim / np.maximum(n, 1), np.nan)
    print(dn, "coverage", float(np.isfinite(res[dn]).mean()))

# resample 0.140625 deg -> 10' grid (nearest by cell centre)
H, W = 1080, 2160
ii = np.clip(((np.arange(H) + .5) / 6 / 0.140625).astype(int), 0, 1279); jj = np.clip(((np.arange(W) + .5) / 6 / 0.140625).astype(int), 0, 2559)
out = {k.lower(): v[:, ii][:, :, jj].astype(np.float32) for k, v in res.items()}
np.savez_compressed(f"{D}/modis_lst.npz", **out, years=np.array(YEARS))
print("saved", {k: v.shape for k, v in out.items()})
