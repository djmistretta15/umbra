"""Fetch NASA POWER monthly climatology (cloud amount, surface albedo) on 1-degree tiles
covering every ice-free land cell that ever gets Moon-south-pole-style low sun."""
import sys, json, os, time, urllib.request
import numpy as np
from concurrent.futures import ThreadPoolExecutor

g = dict(np.load(sys.argv[1])); outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
need = g["land"] & ~g["ice"] & (g["LSD"] > 0)
tiles = set()
for i, j in zip(*np.nonzero(need)):
    la, lo = g["LAT"][i, j], g["LON"][i, j]
    tiles.add((int(np.floor(la / 10) * 10), int(np.floor(lo / 10) * 10)))
# known Antarctic analog (Dry Valleys) is ice-masked at coarse scale; add its tile explicitly
tiles.add((-80, 160))
tiles = sorted(tiles)
print("tiles", len(tiles), flush=True)

def get(args):
    param, (la, lo) = args
    fn = f"{outdir}/{param}_{la}_{lo}.json"
    if os.path.exists(fn):
        return fn, "cached"
    la2, lo2 = min(la + 9, 89), min(lo + 9, 179)
    url = (f"https://power.larc.nasa.gov/api/temporal/climatology/regional?parameters={param}"
           f"&community=RE&latitude-min={max(la, -89)}&latitude-max={la2}&longitude-min={lo}&longitude-max={lo2}&format=JSON")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                d = json.load(r)
            if "features" in d:
                json.dump(d["features"], open(fn, "w"))
                return fn, "ok"
            err = d.get("messages")
        except Exception as e:
            err = str(e)
        time.sleep(3 * (attempt + 1))
    return fn, f"fail {err}"

jobs = [(p, t) for p in ["CLOUD_AMT", "ALLSKY_SRF_ALB"] for t in tiles]
done = 0
with ThreadPoolExecutor(6) as ex:
    for fn, st in ex.map(get, jobs):
        done += 1
        if st.startswith("fail") or done % 25 == 0:
            print(done, len(jobs), os.path.basename(fn), st, flush=True)
print("finished")
