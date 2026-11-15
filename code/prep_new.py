"""Umbra: put the new breadcrumb datasets on the engine's 10 arc-minute grid (1080 x 2160).

Inputs (data/new): litho_c.tif (USGS/EcoTapestry lithology classes, 250 m), volcanoes.csv (Smithsonian GVP Holocene),
q_*.csv (USGS earthquakes M4.5+ 1976-2025), meteorites.csv (NASA Meteorite Landings), craters.json (confirmed impact
craters from the Impact Earth database, Western University, impact.uwo.ca), playas/ (Natural Earth), pop/ (Natural Earth populated places), emag2_10min.csv (NOAA EMAG2v3, 4 km).
Output: data/new/layers.npz
"""
import sys, json, csv, glob, numpy as np, rasterio, shapefile
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
from scipy import ndimage

D = sys.argv[1]
H, W = 1080, 2160
LAT = 90 - (np.arange(H) + .5) / 6; LON = -180 + (np.arange(W) + .5) / 6
def idx(la, lo):
    return np.clip(((90 - np.asarray(la)) * 6).astype(int), 0, H - 1), (((np.asarray(lo) + 180) % 360) * 6).astype(int) % W
out = {}

# --- rock type fractions: reproject classes to a 4x finer global grid, then count per 10' cell
src = rasterio.open(f"{D}/litho_c.tif")
fine = np.full((H * 4, W * 4), 255, np.uint8)
reproject(rasterio.band(src, 1), fine, dst_transform=rasterio.transform.from_origin(-180, 90, 1/24, 1/24),
          dst_crs="EPSG:4326", resampling=Resampling.nearest, dst_nodata=255)
CLS = {1: "acid_plutonic", 3: "basic_plutonic", 4: "basalt", 5: "carbonate", 6: "evaporite", 9: "intermediate_volcanic",
       10: "metamorphic", 12: "pyroclastic", 13: "siliciclastic", 14: "unconsolidated"}
f4 = fine.reshape(H, 4, W, 4)
valid = (f4 != 255).sum((1, 3))
for c, nm in CLS.items():
    out["lith_" + nm] = np.where(valid > 0, (f4 == c).sum((1, 3)) / np.maximum(valid, 1), np.nan).astype(np.float32)
out["lith_valid"] = (valid > 0)
del fine, f4

# --- volcanoes: kernel density of basaltic shield/field/fissure volcanoes, and of all Holocene volcanoes
V = list(csv.DictReader(open(f"{D}/volcanoes.csv")))
def dens(points, sigma_cells):
    g = np.zeros((H, W), np.float32)
    for la, lo, w in points:
        i, j = idx(la, lo); g[i, j] += w
    return ndimage.gaussian_filter(g, sigma_cells, mode=["nearest", "wrap"])
bas = [(float(v["Latitude"]), float(v["Longitude"]), 1.0) for v in V
       if any(k in v["Primary_Volcano_Type"] for k in ("Shield", "Volcanic field", "Fissure", "Lava cone", "Crater rows"))
       and ("Basalt" in v["Major_Rock_Type"] or "Trachybasalt" in v["Major_Rock_Type"])]
allv = [(float(v["Latitude"]), float(v["Longitude"]), 1.0) for v in V if v["Latitude"]]
out["volc_basaltic"] = dens(bas, 4); out["volc_all"] = dens(allv, 4)
out["n_volc_basaltic"] = len(bas)

# --- earthquakes M4.5+ (50 years): smoothed count
Q = []
for f in glob.glob(f"{D}/q_*.csv"):
    for r in csv.DictReader(open(f)):
        try: Q.append((float(r["latitude"]), float(r["longitude"]), 1.0))
        except: pass
out["quakes"] = dens(Q, 6); out["n_quakes"] = len(Q)

# --- meteorites: found (not seen falling) per cell, smoothed; Martian and lunar finds kept as points
M = list(csv.DictReader(open(f"{D}/meteorites.csv")))
found = [(float(m["reclat"]), float(m["reclong"]), 1.0) for m in M
         if m["fall"] == "Found" and m["reclat"] and not (float(m["reclat"]) == 0 and float(m["reclong"]) == 0)]
out["meteor_found"] = dens(found, 3); out["n_found"] = len(found)
sp = [dict(name=m["name"], cls=m["recclass"], lat=float(m["reclat"]), lon=float(m["reclong"]))
      for m in M if ("Martian" in m["recclass"] or "Lunar" in m["recclass"]) and m["reclat"] and not (float(m["reclat"]) == 0 and float(m["reclong"]) == 0)]
json.dump(sp, open(f"{D}/moon_mars_meteorites.json", "w"))

# --- impact structures: diameter-weighted density
C = json.load(open(f"{D}/craters.json"))
out["impacts"] = dens([(c["lat"], c["lon"], np.log1p(c["dia_km"] or 1)) for c in C], 3); out["n_impacts"] = len(C)

# --- playas (dry lake beds)
sh = shapefile.Reader(f"{D}/playas/ne_10m_playas.shp")
out["playa"] = rasterize([(s.__geo_interface__, 1) for s in sh.shapes()], out_shape=(H, W),
                         transform=rasterio.transform.from_origin(-180, 90, 1/6, 1/6), fill=0, dtype="uint8", all_touched=True)

# --- distance to nearest populated place (km), a proxy for human noise, radio noise and contamination
P = shapefile.Reader(f"{D}/pop/ne_10m_populated_places_simple.shp")
town = np.ones((H, W), bool)
for s in P.shapes():
    lo, la = s.points[0]; i, j = idx(la, lo); town[i, j] = False
dist_cells = ndimage.distance_transform_edt(town)
out["km_to_town"] = (dist_cells * 18.5 * np.maximum(np.cos(np.radians(LAT))[:, None], .3) ** .5).astype(np.float32)

# --- crustal magnetic anomaly (EMAG2v3 at 4 km altitude), absolute, nT
E = np.loadtxt(f"{D}/emag2_10min.csv", delimiter=",")
mag = np.full((H, W), np.nan, np.float32)
lo = np.where(E[:, 0] > 180, E[:, 0] - 360, E[:, 0]); i, j = idx(E[:, 1], lo); mag[i, j] = np.abs(E[:, 2])
m = np.isfinite(mag); near = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True)
out["mag_abs"] = np.where(ndimage.distance_transform_edt(~m) < 3, mag[near[0], near[1]], np.nan).astype(np.float32)

np.savez_compressed(f"{D}/layers.npz", **out)
print({k: (v.shape if hasattr(v, "shape") else v) for k, v in out.items()})
