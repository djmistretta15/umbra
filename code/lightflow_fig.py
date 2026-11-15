"""Figure + ridge check for the Moon light-flow result."""
import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
R = 1737.4e3
J = json.load(open("lightflow.json")); M = np.load("lightflow_maps.npz")
names = json.load(open("/home/claude/data/moon_names/south80.json"))
def xy(lat, lon):
    r = 2 * R * np.tan(np.radians(90 + lat) / 2) / 1000; return r * np.sin(np.radians(lon)), r * np.cos(np.radians(lon))
A = np.array(xy(-89.67, 129.78)); B = np.array(xy(-88.48, 271.66))   # Shackleton and de Gerlache centres
def seg(p):
    p = np.array(p); t = np.clip(np.dot(p - A, B - A) / np.dot(B - A, B - A), 0, 1); return float(np.linalg.norm(p - (A + t * (B - A))))
for h in J["hubs"]:
    h["km_from_shackleton_degerlache_line"] = round(seg(xy(h["lat"], h["lon"])), 1)
    h["on_connecting_ridge"] = h["km_from_shackleton_degerlache_line"] <= 5
    h["km_from_feature_rim"] = float(h["km_from_feature_rim"])
s = J["summary"]; s["hubs_on_connecting_ridge"] = sum(h["on_connecting_ridge"] for h in J["hubs"])
s["hubs_at_artemis_feature_or_ridge"] = sum(h["artemis_feature"] or h["on_connecting_ridge"] for h in J["hubs"])
json.dump(J, open("lightflow.json", "w"), indent=1)
print(json.dumps(s, indent=1)); [print(h["near"], h["lat"], h["lon"], h["km_from_shackleton_degerlache_line"], h["artemis_feature"]) for h in J["hubs"]]

V, T, P = M["vis"], M["traffic"], M["psr"]
G = V.shape[0]; ext = G * 0.24 / 2
fig, ax = plt.subplots(figsize=(9, 9), facecolor="#0b0d12"); ax.set_facecolor("#0b0d12")
ax.imshow(np.nan_to_num(V), cmap="gray", vmin=0, vmax=0.8, extent=[-ext, ext, -ext, ext])
ax.imshow(np.ma.masked_less(P, 0.5), cmap="Blues", vmin=0, vmax=1.5, alpha=.55, extent=[-ext, ext, -ext, ext])
ax.imshow(np.ma.masked_less(T, 3), cmap="autumn", norm=LogNorm(3, T.max()), alpha=.9, extent=[-ext, ext, -ext, ext])
for k, h in enumerate(J["hubs"], 1):
    x, y = xy(h["lat"], h["lon"]); ax.plot(x, y, "o", ms=13, mfc="none", mec="#7CFFB2", mew=2); ax.text(x + 2.5, y + 2.5, str(k), color="#7CFFB2", fontsize=10, weight="bold")
for n in ["Shackleton", "de Gerlache", "Haworth", "Faustini", "Slater", "Shoemaker", "Nobile", "Mons Malapert", "Sverdrup", "Amundsen", "Cabeus"]:
    for q in names:
        if q["name"] == n:
            x, y = xy(q["lat"], q["lon"])
            if abs(x) < ext and abs(y) < ext: ax.text(x, y, n, color="#9ecbff", fontsize=8, ha="center", va="center", alpha=.9)
ax.set_xlim(-ext, ext); ax.set_ylim(-ext, ext); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("Moon south pole: where the light carries traffic\n12,000 random trips, routed only by LRO sunlight and LOLA slope", color="w", fontsize=12)
ax.text(-ext + 4, -ext + 6, "grey = average sunlight   blue = permanent shadow (ice)   orange = corridors   green rings = hubs", color="#ccc", fontsize=8)
fig.tight_layout(); fig.savefig("cons/moon_lightflow.png", dpi=110, facecolor=fig.get_facecolor())
