"""Analog engine: scores every land cell on Earth against Moon south pole tests.

Per test, per cell:
  presence  0..1  how much of what breaks that test is there
  duration  0..1  fraction of the year it holds
  penalty   0..1  what Earth adds that the Moon lacks
  score     = 100 * presence * duration * (1 - penalty)
  confidence 0..1 how good the data behind it is
"""
import sys, json
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

D = sys.argv[1]  # data dir
OUT = sys.argv[2]
WC = f"{D}/worldclim"
SG = f"{D}/soilgrids"

def wc(path):
    with rasterio.open(path) as r:
        a = r.read(1).astype("float64")
        a[a < -1e30] = np.nan
        return a, r.profile

bio6, prof = wc(f"{WC}/wc_bio/wc2.1_10m_bio_6.tif")      # min temp of coldest month, C
bio12, _ = wc(f"{WC}/wc_bio/wc2.1_10m_bio_12.tif")       # annual precip, mm
elev, _ = wc(f"{WC}/wc_elev/wc2.1_10m_elev.tif")
tavg = np.stack([wc(f"{WC}/wc_tavg/wc2.1_10m_tavg_{m:02d}.tif")[0] for m in range(1, 13)])
prec = np.stack([wc(f"{WC}/wc_prec/wc2.1_10m_prec_{m:02d}.tif")[0] for m in range(1, 13)])
vapr = np.stack([wc(f"{WC}/wc_vapr/wc2.1_10m_vapr_{m:02d}.tif")[0] for m in range(1, 13)])
wind = np.stack([wc(f"{WC}/wc_wind/wc2.1_10m_wind_{m:02d}.tif")[0] for m in range(1, 13)])
H, W = bio6.shape
transform = prof["transform"]

def soil(name):
    with rasterio.open(f"{SG}/{name}_0-5cm_5000.tif") as r:
        src = r.read(1).astype("float64")
        src[src == r.nodata] = np.nan
        src[src < 0] = np.nan
        dst = np.full((H, W), np.nan)
        reproject(src, dst, src_transform=r.transform, src_crs=r.crs, src_nodata=np.nan,
                  dst_transform=transform, dst_crs="EPSG:4326", dst_nodata=np.nan,
                  resampling=Resampling.average)
        return dst

# SoilGrids units: sand/silt/clay g/kg, soc dg/kg -> convert to % and g/kg
sand = soil("sand") / 10.0
silt = soil("silt") / 10.0
clay = soil("clay") / 10.0
soc = soil("soc") / 10.0
ice = np.load(f"{D}/ne/ice.npy")         # Natural Earth glaciers + ice shelves
land = ~np.isnan(bio6)
has_soil = ~np.isnan(sand)

lat = np.array([transform[5] + (i + 0.5) * transform[4] for i in range(H)])
LAT = np.repeat(lat[:, None], W, axis=1)
LON = np.repeat(np.array([transform[2] + (j + 0.5) * transform[0] for j in range(W)])[None, :], H, axis=0)

def ramp(x, lo, hi):
    """0 at lo, 1 at hi (clipped)."""
    return np.clip((x - lo) / (hi - lo), 0, 1)

# ---------- Moon south pole reference (sourced, see README) ----------
MOON = {
    "regolith_median_um": "60-80 (Apollo), sharp grains, no wind or water",
    "texture_target_pct": {"sand": 50, "silt": 45, "clay": 5},  # approx: median sits at 62.5 um sand/silt line
    "sun_max_elev_deg": 7.0,   # Artemis candidate sites, usually 1-2 deg (NESC)
    "psr_temp_K": 40,          # Haworth PSR never exceeds ~40 K (Diviner)
}

# ---------- sun geometry: days per year the whole day is low-sun ----------
decl = 23.44 * np.sin(np.radians(360.0 / 365.0 * (np.arange(365) - 81)))
def low_sun_days(phi):
    noon = 90 - np.abs(phi - decl)          # max sun elevation that day
    return int(np.sum((noon > 0) & (noon <= MOON["sun_max_elev_deg"])))
lsd_by_row = np.array([low_sun_days(p) for p in lat])
LSD = np.repeat(lsd_by_row[:, None], W, axis=1)
# month index for each day, to tie low-sun days to snow months
day_month = np.minimum((np.arange(365) / 30.42).astype(int), 11)

snowy = (tavg <= 0.5) & (prec > 5)
es = 0.6108 * np.exp(17.27 * tavg / (tavg + 237.3))   # saturation vapor pressure, kPa
rh = np.clip(vapr / es, 0, 1)                         # relative humidity, what static charge cares about             # month likely snow-covered (cold and not bone dry)

# ---------- penalties (what Earth adds) ----------
p_water = ramp(rh.mean(0), 0.15, 0.7)       # humidity bleeds off static charge
p_rain = ramp(bio12, 25, 500)               # liquid water rounds grains, forms clay
p_life = np.where(has_soil, ramp(soc, 2, 30), 0.5)  # unknown soil -> half penalty
p_wind = ramp(wind.mean(0), 2, 8)           # wind sorts and rounds dust
def combine(*pw):
    keep = np.ones((H, W))
    for p, w in pw:
        keep *= (1 - w * p)
    return 1 - keep

# ---------- TEST A: dust on seals and joints ----------
tex = np.where(has_soil,
               1 - (np.abs(sand - 50) + np.abs(silt - 45) + np.abs(clay - 5)) / 200.0, np.nan)
weather_free = np.where(has_soil, 1 - ramp(clay, 5, 30), np.nan)   # clay = water weathering
dry = 1 - ramp(bio12, 25, 400)
# frost shatter makes fresh angular grains (months hovering near freezing)
freeze_thaw = ((tavg > -8) & (tavg < 4)).sum(0) / 12.0
breakup = 0.4 + 0.6 * np.clip(freeze_thaw * 2, 0, 1)
sharp = dry * np.nan_to_num(weather_free, nan=0.5) * breakup          # angularity proxy
presA = np.where(has_soil, 0.5 * tex + 0.5 * sharp, 0.5 * dry)
dry_months = ((1 - ramp(rh, 0.3, 0.8)) * ~snowy).sum(0) / 12.0
durA = dry_months
penA = combine((p_water, 0.4), (p_rain, 0.3), (p_life, 0.4), (p_wind, 0.35))
scoreA = 100 * presA * durA * (1 - penA)
confA = np.where(has_soil, 0.5, 0.25)   # angularity is a proxy; no soil -> lower

# ---------- TEST B: navigation in low sun ----------
# whole-day low sun, but snow wrecks it (bright, fills shadows); haze adds scatter
low_days_clear = np.zeros((H, W))
for i in range(H):
    noon = 90 - np.abs(lat[i] - decl)
    mask = (noon > 0) & (noon <= MOON["sun_max_elev_deg"])
    if not mask.any():
        continue
    months = day_month[mask]
    low_days_clear[i] = (~snowy[months, i, :]).sum(0)
presB = np.where(LSD > 0, 1.0, 0.0)
durB = low_days_clear / 365.0
haze = ramp(rh.mean(0), 0.2, 0.8)
thin_air = ramp(elev, 0, 4000)              # higher = less sky glow into shadows
p_scatter = np.clip(0.6 * haze + 0.4 * (1 - thin_air), 0, 1)
penB = combine((p_scatter, 0.5), (p_life, 0.4))
scoreB = 100 * presB * durB * (1 - penB) * 4  # x4: 91 clear days ~ full credit (one season)
scoreB = np.clip(scoreB, 0, 100)
confB = np.full((H, W), 0.45)                  # no slope/relief layer yet

# ---------- TEST C: deep cold ----------
moon_C = MOON["psr_temp_K"] - 273.15
coverC = np.clip((15 - bio6) / (15 - moon_C), 0, 1)    # share of the cold gap Earth covers
scoreC = 100 * coverC
confC = np.full((H, W), 0.7)

rawA, rawB = scoreA.copy(), scoreB.copy()     # unmasked, for known ice-free sites the coarse mask misses
for a in (scoreA, scoreB):
    a[ice] = 0.0                               # ice sheet is not regolith
scoreB[~has_soil] = 0.0                        # coast/water-edge cells with no ground data
# combined seal test: dust that is ALSO cold (seals stiffen and dust bites hardest in the cold)
scoreAC = scoreA * coverC / np.nanmax(coverC[land & ~ice])
np.savez_compressed(OUT, rawA=rawA, rawB=rawB, scoreAC=scoreAC, ice=ice, freeze_thaw=freeze_thaw, scoreA=scoreA, scoreB=scoreB, scoreC=scoreC,
                    presA=presA, durA=durA, penA=penA, durB=durB, penB=penB,
                    coverC=coverC, confA=confA, land=land, has_soil=has_soil,
                    LAT=LAT, LON=LON, sand=sand, silt=silt, clay=clay, soc=soc,
                    bio6=bio6, bio12=bio12, elev=elev, vapr=vapr.mean(0), rh=rh.mean(0), wind=wind.mean(0),
                    LSD=LSD, low_days_clear=low_days_clear)
json.dump(MOON, open(OUT.replace(".npz", "_moon.json"), "w"), indent=1)
print("done", H, W, "land cells", int(land.sum()), "with soil", int((land & has_soil).sum()))
