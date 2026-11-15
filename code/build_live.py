"""Assemble umbra_live.html from live_src.html + live_data.js + sample files."""
import json
src = open("live_src.html").read(); data = open("live_data.js").read()
sites = open("bundle/samples/sample_sites.csv").read(); wind = open("bundle/samples/sample_wind_points.csv").read()
inj = data + f"const SAMPLE_SITES={json.dumps(sites)};\nconst SAMPLE_WIND={json.dumps(wind)};\n"
open("umbra_live.html", "w").write(src.replace("/*DATA*/", inj, 1)); print("ok", len(src) + len(inj))
