"""Navigation-in-low-sun test, rebuilt with real cloud cover, ground brightness and relief.

Moon south pole: sun stays below ~7 deg, no air to scatter light into shadows, dark ground
(albedo ~0.1-0.2), rugged relief that throws long shadows.
A low-sun day on Earth only counts if the sky is clear AND the ground is dark (not snow).
"""
import sys, json, glob, os
import numpy as np

g = dict(np.load(sys.argv[1])); pdir = sys.argv[2]
H, W = g["LAT"].shape
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

def grid1(param):
    a = np.full((12, 180, 360), np.nan)
    for fn in glob.glob(f"{pdir}/{param}_*.json"):
        for f in json.load(open(fn)):
            lo, la = f["geometry"]["coordinates"][:2]
            i, j = int(np.floor(la)) + 90, int(np.floor(lo)) + 180
            vals = f["properties"]["parameter"][param]
            for m, k in enumerate(MON):
                v = vals.get(k)
                a[m, min(i, 179), min(j, 359)] = np.nan if v is None or v < -900 else v
    # tiles leave a 1-degree seam between them: fill gaps from east/west neighbours
    for _ in range(2):
        nb = [np.roll(a, 1, axis=2), np.roll(a, -1, axis=2), np.roll(a, 1, axis=1), np.roll(a, -1, axis=1)]
        fill = np.nanmean(np.stack(nb), axis=0)
        a = np.where(np.isnan(a), fill, a)
    return a

cloud1, alb1 = grid1("CLOUD_AMT"), grid1("ALLSKY_SRF_ALB")
I1 = np.clip(np.floor(g["LAT"]).astype(int) + 90, 0, 179)
J1 = np.clip(np.floor(g["LON"]).astype(int) + 180, 0, 359)
cloud = cloud1[:, I1, J1] / 100.0       # (12,H,W) fraction of sky cloudy
alb = alb1[:, I1, J1]                   # ground brightness 0..1

def ramp(x, lo, hi): return np.clip((x - lo) / (hi - lo), 0, 1)

# relief: elevation range in a 3x3 window (~50 km), proxy for long-shadow terrain
e = g["elev"].copy(); e[(e < -500) | ~g["land"]] = np.nan   # drop ocean / fill values
pad = np.pad(e, 1, mode="edge")
win = np.stack([pad[1+di:H+1+di, 1+dj:W+1+dj] for di in (-1,0,1) for dj in (-1,0,1)])
relief = np.nan_to_num(np.nanmax(win, 0) - np.nanmin(win, 0), nan=0.0)

decl = 23.44 * np.sin(np.radians(360.0 / 365.0 * (np.arange(365) - 81)))
day_month = np.minimum((np.arange(365) / 30.42).astype(int), 11)
lat = g["LAT"][:, 0]

clear = 1 - cloud
dark = 1 - ramp(alb, 0.25, 0.55)        # snow ~0.6-0.8 fails, bare rock/soil ~0.1-0.25 passes
credit_m = np.nan_to_num(clear * dark, nan=0.0)   # (12,H,W) value of one low-sun day that month
data_ok_m = ~np.isnan(clear * dark)

good_days = np.zeros((H, W)); raw_days = np.zeros((H, W)); seen = np.zeros((H, W))
for i in range(H):
    noon = 90 - np.abs(lat[i] - decl)
    mask = (noon > 0) & (noon <= 7.0)
    if not mask.any(): continue
    ms = day_month[mask]
    raw_days[i] = mask.sum()
    good_days[i] = credit_m[ms, i, :].sum(0)
    seen[i] = data_ok_m[ms, i, :].mean(0)

presence = 0.4 + 0.6 * ramp(relief, 100, 1000)
haze = ramp(np.nan_to_num(g["rh"], nan=1), 0.2, 0.8)
thin_air = ramp(np.nan_to_num(e, nan=0), 0, 4000)
p_scatter = np.clip(0.6 * haze + 0.4 * (1 - thin_air), 0, 1)
soc = g["soc"]
p_life = np.where(g["has_soil"], ramp(np.nan_to_num(soc), 2, 30), 0.5)
pen = 1 - (1 - 0.5 * p_scatter) * (1 - 0.4 * p_life)
rawB = np.clip(100 * presence * (good_days / 365.0) * 4 * (1 - pen), 0, 100)
scoreB = rawB.copy()
scoreB[g["ice"] | ~g["land"]] = 0

g.update(scoreB=scoreB, rawB=rawB, good_days=good_days, raw_days=raw_days, relief=relief,
         nav_seen=seen, durB=good_days / 365.0, penB=pen,
         cloud_lowsun=np.where(raw_days > 0, np.nan, np.nan))
# average cloud and albedo across each cell's low-sun days, for reporting
cl = np.full((H, W), np.nan); al = np.full((H, W), np.nan)
for i in range(H):
    noon = 90 - np.abs(lat[i] - decl); mask = (noon > 0) & (noon <= 7.0)
    if not mask.any(): continue
    ms = day_month[mask]
    cl[i] = np.nanmean(cloud[ms, i, :], 0); al[i] = np.nanmean(alb[ms, i, :], 0)
g.update(cloud_lowsun=cl, alb_lowsun=al)
np.savez_compressed(sys.argv[1], **g)

land = g["land"] & ~g["ice"] & (raw_days > 0)
print("ice-free land cells with Moon-like low sun:", int(land.sum()))
print("  median low-sun days/yr:", float(np.median(raw_days[land])))
print("  median cloud during those days: %.0f%%" % (100 * np.nanmedian(cl[land])))
print("  median ground brightness then: %.2f" % np.nanmedian(al[land]))
print("  share of low-sun days that are clear AND dark: %.1f%%" % (100 * good_days[land].sum() / raw_days[land].sum()))
print("  cells with >=30 clear+dark low-sun days:", int((good_days[land] >= 30).sum()))
