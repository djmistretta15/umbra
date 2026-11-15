import sys, json
import numpy as np

g = dict(np.load(sys.argv[1]))
H, W = g["LAT"].shape
res = 1 / 6.0

KNOWN = [  # NASA / analog-community sites (name, lat, lon, used for)
    ("Haughton Crater, Devon Island (HMP)", 75.43, -89.82, "Mars/Moon"),
    ("McMurdo Dry Valleys, Antarctica", -77.55, 161.5, "Mars"),
    ("Atacama Desert (Yungay)", -24.08, -69.92, "Mars"),
    ("Mauna Kea, Hawaii (PISCES/ISRU tests)", 19.80, -155.47, "Moon"),
    ("Black Point Lava Flow, Arizona (Desert RATS)", 35.68, -111.43, "Moon"),
    ("Meteor Crater, Arizona", 35.03, -111.02, "Moon"),
    ("Craters of the Moon, Idaho", 43.42, -113.52, "Moon/Mars"),
    ("Mars Desert Research Station, Utah", 38.41, -110.79, "Mars"),
    ("Bockfjord, Svalbard (AMASE)", 79.43, 13.93, "Mars"),
    ("Askja / Icelandic highlands", 65.05, -16.75, "Moon"),
    ("Rio Tinto, Spain", 37.70, -6.60, "Mars"),
]

def cell(lat, lon):
    i = int((90 - lat) / res); j = int((lon + 180) / res)
    return min(max(i, 0), H - 1), min(max(j, 0), W - 1)

def nearest_land(lat, lon, rad=6):
    i, j = cell(lat, lon)
    best = None
    for di in range(-rad, rad + 1):
        for dj in range(-rad, rad + 1):
            a, b = i + di, (j + dj) % W
            if 0 <= a < H and g["land"][a, b]:
                d = di * di + dj * dj
                if best is None or d < best[0]:
                    best = (d, a, b)
    return best[1:] if best else (i, j)

def row(i, j):
    f = lambda k: float(np.round(g[k][i, j], 3)) if not np.isnan(g[k][i, j]) else None
    return {k: f(k) for k in ["scoreA", "scoreB", "scoreC", "scoreAC", "rawA", "rawB", "presA", "durA", "penA", "durB", "penB",
                              "coverC", "sand", "silt", "clay", "soc", "bio6", "bio12", "elev", "vapr",
                              "wind", "rh", "good_days", "raw_days", "relief", "cloud_lowsun", "alb_lowsun", "LSD", "low_days_clear"]} | {"has_soil": bool(g["has_soil"][i, j]), "ice_mask": bool(g["ice"][i, j])}

out = {"known": [], "top": {}}
for name, lat, lon, use in KNOWN:
    i, j = nearest_land(lat, lon)
    out["known"].append({"name": name, "lat": lat, "lon": lon, "use": use} | row(i, j))

# percentile of each known site among all land cells
land = g["land"]
for k in out["known"]:      # known sites are ice-free by definition: use unmasked scores
    k["scoreA"], k["scoreB"] = k["rawA"], k["rawB"]
for t in ["scoreA", "scoreB", "scoreC", "scoreAC"]:
    vals = np.sort(np.nan_to_num(g[t][land], nan=0))
    for k in out["known"]:
        v = k[t] or 0
        k[t + "_pct"] = round(100 * np.searchsorted(vals, v) / len(vals), 1)

# top distinct regions per test (greedy, 300 km apart)
def top_regions(key, n=12, sep_deg=3.0):
    s = np.nan_to_num(g[key], nan=-1).copy()
    s[~land | g["ice"]] = -1
    idx = np.argsort(s.ravel())[::-1]
    picks = []
    for f in idx[:200000]:
        i, j = divmod(int(f), W)
        la, lo = float(g["LAT"][i, j]), float(g["LON"][i, j])
        if all(abs(la - p["lat"]) > sep_deg or abs(lo - p["lon"]) > sep_deg / max(np.cos(np.radians(la)), 0.2) for p in picks):
            picks.append({"lat": round(la, 2), "lon": round(lo, 2)} | row(i, j))
        if len(picks) >= n:
            break
    return picks

for t in ["scoreA", "scoreB", "scoreC", "scoreAC"]:
    out["top"][t] = top_regions(t)

json.dump(out, open(sys.argv[2], "w"), indent=1)
print("KNOWN SITES  (score / percentile among all land)")
for k in out["known"]:
    print(f"{k['name'][:42]:42s} dust {(k['scoreA'] or 0):5.1f} ({k['scoreA_pct']:5.1f})  sun {(k['scoreB'] or 0):5.1f} ({k['scoreB_pct']:5.1f})  cold {(k['scoreC'] or 0):5.1f}  seal {(k['scoreAC'] or 0):5.1f} ({k['scoreAC_pct']:5.1f})  soil={k['has_soil']} ice={k['ice_mask']}")
for t in ["scoreA", "scoreB", "scoreC", "scoreAC"]:
    print("\nTOP", t)
    for p in out["top"][t]:
        print(f"  {p['lat']:7.2f} {p['lon']:8.2f}  {p[t]:5.1f}  gooddays {p['good_days']} of {p['raw_days']} cloud {p['cloud_lowsun']} alb {p['alb_lowsun']} relief {p['relief']} | sand {p['sand']} silt {p['silt']} clay {p['clay']} soc {p['soc']} rain {p['bio12']} rh {p['rh']} elev {p['elev']}")
