#!/usr/bin/env python3
"""Copy the shared map geometry (state outlines, bounds, city and town labels) from
election2026/dots/meta.json into election-history/data/geo.json, so this app stands alone."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.dirname(HERE)
E26 = os.environ.get("ELECTION2026_DIR", os.path.join(os.path.dirname(APP), "election2026"))
m = json.load(open(os.path.join(E26, "dots", "meta.json")))
geo = {k: m[k] for k in ("frame", "states", "outline", "bbox", "cities", "places") if k in m}
os.makedirs(os.path.join(APP, "data"), exist_ok=True)
json.dump(geo, open(os.path.join(APP, "data", "geo.json"), "w"), separators=(",", ":"))
print("geo.json:", {k: len(v) if hasattr(v, "__len__") else v for k, v in geo.items()})
