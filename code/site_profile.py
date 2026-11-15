"""Umbra: fine-scale profile of the western Tibet expedition region (33.5-36.5N, 78-86E) at 0.01 deg (~1 km).

Data: AWS Terrain Tiles (SRTM-based elevation, ~270 m), NASA MODIS Terra monthly land surface temperature via
NASA GIBS (0.035 deg tiles, 2018-2022), USGS/EcoTapestry lithology (250 m), Natural Earth roads and lakes.
Output: site_tibet.json, cons/site_tibet.png
"""
import sys, io, os, re, json, math, numpy as np, urllib.request, shapefile, rasterio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from scipy import ndimage
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize

D = sys.argv[1]; T = f"{D}/tibet"; os.makedirs(f"{T}/dem", exist_ok=True); os.makedirs(f"{T}/lst", exist_ok=True)
LA0, LA1, LO0, LO1, R = 33.5, 36.5, 78.0, 86.0, 0.01
H, W = int((LA1 - LA0) / R), int((LO1 - LO0) / R)
LAT = LA1 - (np.arange(H) + .5) * R; LON = LO0 + (np.arange(W) + .5) * R
TR = rasterio.transform.from_origin(LO0, LA1, R, R)
op = urllib.request.build_opener()
def fetch(url, path):
    if os.path.exists(path): return path
    for _ in range(4):
        try: open(path, "wb").write(op.open(url, timeout=60).read()); return path
        except Exception: pass

# ---- elevation: Terrarium tiles z9 (web mercator), mosaic and reproject to the 0.01 deg grid
z = 9
def tx(lon): return int((lon + 180) / 360 * 2 ** z)
def ty(lat): r = math.radians(lat); return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** z)
xs, ys = range(tx(LO0), tx(LO1) + 1), range(ty(LA1), ty(LA0) + 1)
jobs = [(x, y) for x in xs for y in ys]
with ThreadPoolExecutor(12) as ex:
    list(ex.map(lambda t: fetch(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{t[0]}/{t[1]}.png", f"{T}/dem/{z}_{t[0]}_{t[1]}.png"), jobs))
mos = np.zeros((len(ys) * 256, len(xs) * 256), np.float32)
for i, y in enumerate(ys):
    for j, x in enumerate(xs):
        a = np.asarray(Image.open(f"{T}/dem/{z}_{x}_{y}.png").convert("RGB")).astype(np.float32)
        mos[i * 256:(i + 1) * 256, j * 256:(j + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
n = 2 ** z; ms = 2 * math.pi * 6378137 / n / 256
mtr = rasterio.transform.from_origin(xs[0] * 256 * ms - math.pi * 6378137, math.pi * 6378137 - ys[0] * 256 * ms, ms, ms)
elev = np.zeros((H, W), np.float32)
reproject(mos, elev, src_transform=mtr, src_crs="EPSG:3857", dst_transform=TR, dst_crs="EPSG:4326", resampling=Resampling.bilinear)
dy = R * 111320; dx = dy * np.cos(np.radians(LAT))[:, None]
gy, gx = np.gradient(elev); slope = np.degrees(np.arctan(np.hypot(gx / dx, gy / dy)))

# ---- MODIS LST via GIBS, 2km matrix level 4 (0.03515625 deg/px), tiles covering the box
lut = {}
for rgb, lo, hi in re.findall(r'rgb="(\d+,\d+,\d+)" transparent="false"[^>]*value="\[([\d.]+),([\d.]+)\)"', open(f"{D}/gibs/lst_cm.xml").read()):
    k = tuple(map(int, rgb.split(","))); lut[(k[0] << 16) | (k[1] << 8) | k[2]] = (float(lo) + float(hi)) / 2
keys = np.array(list(lut)); vals = np.array([lut[k] for k in keys]); order = np.argsort(keys); keys, vals = keys[order], vals[order]
px = 360 / (20 * 512)
tiles = [(r, c) for r in (2, 3) for c in (14,)]
def lst(dn, y, m):
    out = np.full((2 * 512, 512), np.nan, np.float32)
    for k, (r, c) in enumerate(tiles):
        p = fetch(f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_L3_Land_Surface_Temp_Monthly_{dn}/default/{y}-{m:02d}-01/2km/4/{r}/{c}.png", f"{T}/lst/{dn}_{y}_{m}_{r}_{c}.png")
        if not p: continue
        a = np.asarray(Image.open(p).convert("RGBA")); key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
        idx = np.clip(np.searchsorted(keys, key), 0, len(keys) - 1); v = np.where((keys[idx] == key) & (a[..., 3] > 0), vals[idx], np.nan)
        out[k * 512:(k + 1) * 512] = v
    return out   # rows from 54N down to 18N, cols 72E to 90E
YEARS = [2018, 2019, 2020, 2021, 2022]
with ThreadPoolExecutor(12) as ex:
    list(ex.map(lambda a: lst(*a), [(dn, y, m) for dn in ("Day", "Night") for y in YEARS for m in range(1, 13)]))
def clim(dn):
    s = np.zeros((12, 1024, 512)); c = np.zeros((12, 1024, 512))
    for y in YEARS:
        for m in range(1, 13):
            a = lst(dn, y, m); ok = np.isfinite(a); s[m - 1][ok] += a[ok]; c[m - 1][ok] += 1
    return np.where(c > 0, s / np.maximum(c, 1), np.nan)
Dd, Nn = clim("Day"), clim("Night")
ri = ((54 - LAT) / px).astype(int); ci = ((LON - 72) / px).astype(int)
with np.errstate(all="ignore"):
    lst_mean = ((np.nanmean(Dd, 0) + np.nanmean(Nn, 0)) / 2 - 273.15)[ri][:, ci]
    lst_swing = np.nanmean(Dd - Nn, 0)[ri][:, ci]
    lst_cold = (np.nanmin(Nn, 0) - 273.15)[ri][:, ci]
    lst_hot = (np.nanmax(Dd, 0) - 273.15)[ri][:, ci]

# ---- lithology (250 m) to 0.01 deg classes and fractions
with rasterio.open(f"{D}/new/litho_c.tif") as src:
    lith = np.full((H, W), 255, np.uint8)
    reproject(rasterio.band(src, 1), lith, dst_transform=TR, dst_crs="EPSG:4326", resampling=Resampling.mode, dst_nodata=255)
CL = {1: "granite-type rock", 3: "gabbro-type rock", 4: "basalt", 5: "limestone", 6: "salt and gypsum", 7: "ice", 9: "andesite-type lava",
      10: "metamorphic rock", 11: "mixed sedimentary rock", 12: "volcanic ash", 13: "sandstone and shale", 14: "loose sediment", 255: "unmapped"}
def frac(cls, rad=3):
    return ndimage.uniform_filter(np.isin(lith, cls).astype(float), 2 * rad + 1)
loose = frac([14], 2); carb = frac([5, 6], 5); icef = frac([7], 2)

# ---- roads and lakes
rd = shapefile.Reader(f"{T}/roads/ne_10m_roads.shp")
road = rasterize([(s.__geo_interface__, 1) for s in rd.shapes() if s.bbox[2] > LO0 - 1 and s.bbox[0] < LO1 + 1 and s.bbox[3] > LA0 - 1 and s.bbox[1] < LA1 + 1],
                 out_shape=(H, W), transform=TR, fill=0, dtype="uint8", all_touched=True)
km_road = ndimage.distance_transform_edt(road == 0) * R * 111.32 * 0.85
lk = shapefile.Reader(f"{T}/lakes/ne_10m_lakes.shp")
LAKES = [((rec.as_dict()["name"] or "").strip(), s) for s, rec in zip(lk.shapes(), lk.records()) if s.bbox[2] > LO0 and s.bbox[0] < LO1 and s.bbox[3] > LA0 and s.bbox[1] < LA1]
lake = rasterize([(s.__geo_interface__, 1) for _, s in LAKES], out_shape=(H, W), transform=TR, fill=0, dtype="uint8")

# ---- composite: the region's 8 tests, re-scored at 1 km (each 0..1)
def ramp(x, a, b): return np.clip((x - a) / (b - a), 0, 1)
T_ = {
 "thin_air": ramp(elev, 4300, 5300),                     # Mars-thin air proxy: higher is thinner
 "cold": ramp(-np.nan_to_num(lst_mean, nan=30), -2, 10),  # colder ground (MODIS)
 "swing": ramp(np.nan_to_num(lst_swing), 8, 22),          # day-night ground swing (MODIS)
 "flat": 1 - ramp(slope, 3, 12),                          # landing and rover ground
 "loose": ramp(loose, .3, .9),                            # loose sediment for dust and excavation
 "caves": ramp(carb, .05, .4),                            # limestone or salt nearby (caves, salt)
}
score = np.ones((H, W))
for v in T_.values(): score *= (0.25 + 0.75 * v)
score *= (lake == 0) * (icef < .3)
access = 1 - ramp(km_road, 25, 120)
best = []
order_ = np.argsort(score.ravel())[::-1]
for f in order_:
    i, j = divmod(int(f), W)
    if any(abs(LAT[i] - b["lat"]) < .25 and abs(LON[j] - b["lon"]) < .3 for b in best): continue
    if access[i, j] <= 0: continue
    if not (LA0 + .25 < LAT[i] < LA1 - .25 and LO0 + .25 < LON[j] < LO1 - .25): continue
    near = min([L for L in LAKES if L[0].strip()], key=lambda L: (np.mean([p[1] for p in L[1].points]) - LAT[i]) ** 2 + (np.mean([p[0] for p in L[1].points]) - LON[j]) ** 2)
    nl = near[1]; nkm = 111.32 * math.hypot(np.mean([p[1] for p in nl.points]) - LAT[i], (np.mean([p[0] for p in nl.points]) - LON[j]) * math.cos(math.radians(LAT[i])))
    best.append(dict(lat=round(float(LAT[i]), 3), lon=round(float(LON[j]), 3), elev_m=int(elev[i, j]), slope_deg=round(float(slope[i, j]), 1),
                     ground_mean_C=round(float(lst_mean[i, j]), 1), swing_C=round(float(lst_swing[i, j]), 1), coldest_night_C=round(float(lst_cold[i, j]), 1),
                     hottest_day_C=round(float(lst_hot[i, j]), 1), rock=CL.get(int(lith[i, j]), "unmapped"), km_to_road=round(float(km_road[i, j])),
                     nearest_lake=near[0].strip(), km_to_lake=round(nkm), score=round(float(score[i, j]), 3),
                     tests={k: round(float(v[i, j]), 2) for k, v in T_.items()}))
    if len(best) >= 3: break
REG = dict(box=[LA0, LA1, LO0, LO1], cell_km=1.1, elev_median=int(np.median(elev)), share_above_4800=float((elev > 4800).mean()),
           share_flat_under5=float((slope < 5).mean()), ground_mean_C_median=float(np.nanmedian(lst_mean)), swing_C_median=float(np.nanmedian(lst_swing)),
           coldest_night_C_min=float(np.nanmin(lst_cold)), lst_coverage=float(np.isfinite(lst_mean).mean()))
json.dump(dict(region=REG, sites=best), open("site_tibet.json", "w"), indent=1)
print(json.dumps(REG, indent=1)); [print(b) for b in best]

# ---- figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
BG, TX, MU = "#0b1020", "#e8ecf4", "#9aa6bd"; ext = [LO0, LO1, LA0, LA1]
fig, ax = plt.subplots(1, 2, figsize=(15, 4.6), facecolor=BG)
ls = matplotlib.colors.LightSource(315, 35); hs = ls.hillshade(elev, vert_exag=0.02, dx=dx.mean(), dy=dy)
ax[0].imshow(hs, cmap="gray", extent=ext); im = ax[0].imshow(score, cmap="magma", alpha=.6, extent=ext, vmin=0, vmax=np.percentile(score, 99.9))
ax[1].imshow(hs, cmap="gray", extent=ext); im2 = ax[1].imshow(lst_swing, cmap="inferno", alpha=.65, extent=ext, vmin=5, vmax=25)
for a, t, s in [(ax[0], "Where to go: the region's tests at 1 km", "Brighter = more tests met at once; numbers = top 3 spots near a road"),
                (ax[1], "NASA MODIS: day-night ground swing", "C, 2018-2022 monthly mean; terrain shading from SRTM-based tiles")]:
    a.set_facecolor(BG); a.tick_params(colors=MU, labelsize=8)
    for sp in a.spines.values(): sp.set_color("#2a3550")
    a.set_title(t, color=TX, fontsize=13, loc="left", pad=20, fontweight="bold"); a.text(0, 1.02, s, transform=a.transAxes, color=MU, fontsize=9)
    for k, b in enumerate(best):
        a.plot(b["lon"], b["lat"], "o", ms=18, mfc="#ffb547", mec="#071021", mew=2); a.text(b["lon"], b["lat"], str(k + 1), ha="center", va="center", fontsize=11, fontweight="bold", color="#1a1200")
    for nm, s in LAKES:
        if nm.strip(): a.text(np.mean([p[0] for p in s.points]), np.mean([p[1] for p in s.points]) + .12, nm.strip(), color="#9ad1ff", fontsize=8, ha="center")
c = fig.colorbar(im2, ax=ax[1], fraction=.025, pad=.02); c.ax.tick_params(colors=MU, labelsize=8)
fig.text(.01, .01, "Umbra by Team Forced Futures · NASA Space Apps 2026 · NASA MODIS via GIBS, AWS Terrain Tiles, USGS lithology, Natural Earth · computed with AI-assisted code", color=MU, fontsize=9)
plt.tight_layout(rect=[0, .05, 1, 1]); plt.savefig("cons/site_tibet.png", dpi=110, facecolor=BG)
