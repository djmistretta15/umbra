"""Terrarium elevation tiles (AWS Terrain Tiles, SRTM-based) at zoom 6, land latitudes 60S-82N."""
import os, math, urllib.request
from concurrent.futures import ThreadPoolExecutor
T = "/home/claude/data/terr6"; z = 6
def row(lat): return int((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * 2 ** z)
y0, y1 = row(82), row(-60)
def get(t):
    x, y = t; p = f"{T}/{x}_{y}.png"
    if os.path.exists(p): return 1
    for _ in range(4):
        try: open(p, "wb").write(urllib.request.urlopen(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", timeout=60).read()); return 1
        except Exception: pass
    return 0
jobs = [(x, y) for y in range(y0, y1 + 1) for x in range(2 ** z)]
with ThreadPoolExecutor(32) as ex: r = list(ex.map(get, jobs))
print("rows", y0, y1, "ok", sum(r), "of", len(jobs))
