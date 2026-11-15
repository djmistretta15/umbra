"""Expedition portfolio, ranked by how many tests are in Earth's top 3% inside one 2-degree block (the same rule Umbra Live uses).
Replaces the ordering in render_cons.py, which ranked blocks by the busiest single cell. Output: cons/portfolio.json"""
import json, numpy as np
C = json.load(open("cons/constraints.json"))["constraints"]
first = np.load(f"cons/score_{next(iter(C))}.npy"); H, W = first.shape; B = 12
blocks = {}
for k, v in C.items():
    s = np.nan_to_num(np.load(f"cons/score_{k}.npy").astype(float)); pos = s[s > 0]
    m = s >= (np.percentile(pos, 97) if pos.size else np.inf)
    blocks[k] = m[:H - H % B, :W - W % B].reshape(H // B, B, W // B, B).any(axis=(1, 3))
union = sum(b.astype(int) for b in blocks.values())
order = np.argsort(union.ravel(), kind="stable")[::-1]; port = []
for f in order:
    bi, bj = divmod(int(f), W // B)
    if union[bi, bj] < 3: break
    la = 90 - (bi + .5) * 2; lo = -180 + (bj + .5) * 2
    if any(abs(la - p["lat"]) < 6 and abs(lo - p["lon"]) < 12 for p in port): continue
    port.append({"lat": round(la, 1), "lon": round(lo, 1), "count": int(union[bi, bj]), "tests": [C[k]["title"] for k in C if blocks[k][bi, bj]]})
    if len(port) >= 8: break
json.dump(port, open("cons/portfolio.json", "w"), indent=1)
for p in port: print(p["lat"], p["lon"], p["count"], p["tests"])
