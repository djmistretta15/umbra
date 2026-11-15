"""Umbra terrain analogs from AWS Terrain Tiles (SRTM-based, zoom 6, about 2.4 km pixels at the equator).

Per pixel, on a ground baseline of about 5 km (so Earth and Moon slopes are measured the same way):
  slope         grade over +-2.4 km
  horizon       highest terrain angle in 8 directions out to about 15 km
Per 10' engine cell:
  radio_block   share of pixels where at least 4 of 8 directions rise above 7 degrees. From the lunar south pole the Earth
                never climbs more than about 7 degrees above the horizon, so terrain this steep cuts the radio link.
  winter_shade  share of pixels shaded at winter-solstice noon (horizon toward the Equator above the noon sun)
  slope_hist    share of pixels in slope bins 0-2, 2-5, 5-10, 10-15, 15-25, >25 degrees
Output: terrain6.npz
"""
import math, numpy as np
from PIL import Image
T = "/home/claude/data/terr6"; Z = 6; NT = 2 ** Z; TS = 256; WPX = NT * TS
y0, y1 = 4, 45
EQ = 2 * math.pi * 6378137 / WPX          # metres per pixel at the Equator
H, W = 1080, 2160
BINS = [0, 2, 5, 10, 15, 25, 90]
acc = dict(n=np.zeros((H, W)), block=np.zeros((H, W)), shade=np.zeros((H, W)), shade_n=np.zeros((H, W)),
           hist=np.zeros((len(BINS) - 1, H, W)))
DIRS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # (dy, dx); dy=+1 is south
def tile(x, y):
    try: a = np.asarray(Image.open(f"{T}/{x}_{y}.png").convert("RGB")).astype(np.float32)
    except Exception: return np.zeros((TS, TS), np.float32)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
def lat_of_row(py):
    n = math.pi - 2 * math.pi * py / WPX; return math.degrees(math.atan(math.sinh(n)))
cache = {}
def strip(y):
    if y < y0 or y > y1: return None
    if y not in cache: cache[y] = np.hstack([tile(x, y) for x in range(NT)])
    return cache[y]
for y in range(y0, y1 + 1):
    for k in list(cache):
        if k < y - 1: del cache[k]
    up, mid, dn = strip(y - 1), strip(y), strip(y + 1)
    P = 32
    top = up[-P:] if up is not None else np.repeat(mid[:1], P, 0)
    bot = dn[:P] if dn is not None else np.repeat(mid[-1:], P, 0)
    E = np.vstack([top, mid, bot]); E = np.hstack([E[:, -P:], E, E[:, :P]])     # wrap in longitude
    E = np.where(E < -500, 0, E)                                                # ocean floor -> sea level
    latc = lat_of_row(y * TS + TS / 2); dx = EQ * math.cos(math.radians(latc))
    k = max(1, int(round(2400 / dx))); steps = max(1, int(round(15000 / (k * dx))))
    core = (slice(P, P + TS), slice(P, P + WPX))
    gy = (np.roll(E, -k, 0) - np.roll(E, k, 0)) / (2 * k * dx); gx = (np.roll(E, -k, 1) - np.roll(E, k, 1)) / (2 * k * dx)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))[core]
    hz = []
    for dy, dxx in DIRS:
        best = np.full(E.shape, -90.0, np.float32)
        for s in range(1, steps + 1):
            d = s * k * dx * math.hypot(dy, dxx)
            sh = np.roll(np.roll(E, -dy * s * k, 0), -dxx * s * k, 1)
            np.maximum(best, np.degrees(np.arctan((sh - E) / d)), out=best)
        hz.append(best[core])
    hz = np.stack(hz)
    land = E[core] > 0
    blocked = (hz > 7).sum(0) >= 4
    # winter noon: Sun due south in the north (dir index 2: dy=+1) and due north in the south (index 6)
    rows = np.arange(TS) + y * TS; lats = np.array([lat_of_row(r + .5) for r in rows])
    sun = 90 - np.abs(lats) - 23.44
    toward_eq = np.where(lats[:, None] >= 0, hz[2], hz[6])
    shaded = (toward_eq > sun[:, None]) & (sun[:, None] > 0)
    # map pixels to engine cells
    ci = np.clip(((90 - lats) * 6).astype(int), 0, H - 1)[:, None].repeat(WPX, 1)
    lons = -180 + (np.arange(WPX) + .5) * 360 / WPX; cj = np.clip(((lons + 180) * 6).astype(int), 0, W - 1)[None, :].repeat(TS, 0)
    m = land; idx = (ci[m], cj[m])
    np.add.at(acc["n"], idx, 1); np.add.at(acc["block"], idx, blocked[m])
    sm = m & (sun[:, None] > 0); np.add.at(acc["shade_n"], (ci[sm], cj[sm]), 1); np.add.at(acc["shade"], (ci[sm], cj[sm]), shaded[sm])
    b = np.digitize(slope[m], BINS[1:-1])
    for q in range(len(BINS) - 1):
        sel = b == q; np.add.at(acc["hist"][q], (idx[0][sel], idx[1][sel]), 1)
    print(y, round(latc, 1), "k", k, "steps", steps, "blocked", float(blocked[land].mean()) if land.any() else 0, flush=True)
n = np.maximum(acc["n"], 1)
np.savez_compressed("terrain6.npz", n=acc["n"], radio_block=acc["block"] / n, winter_shade=acc["shade"] / np.maximum(acc["shade_n"], 1),
                    shade_n=acc["shade_n"], slope_hist=acc["hist"] / n[None], bins=np.array(BINS))
print("done")
