#!/usr/bin/env python3
"""U.S. House, 1976-2026: results by district, dot layers, and one hex layout per map era.

Sources:
  results 1976-2024  MIT Election Data + Science Lab, U.S. House 1976-2024 (CC0), via electiondata.dev
  results 2026       election2026/data.json (NBC News / AP)
  lines 1976-2024    Lewis, DeVine, Pritcher & Martis, congressional district boundaries
                     (github.com/JeffreyBLewis/congressional-district-boundaries)
  lines 2026         NBC News district maps (the same files election2026 uses)

Hex layouts: one per apportionment era (1976-80, 1982-90, 1992-2000, 2002-10, 2012-20,
2022-24), each built from the first election's district population centers; 2026 reuses the
election2026 honeycomb. Within an era a seat keeps its hex, so the slider only reshuffles at
redistricting. Mid-decade redraws (Texas 2004, Ohio 2022, the 2025-26 redraws) keep the
seat's slot but the ground under it changed, which the page says.

Output (election-history/data/): house.json, house-<year>-<scale>.bin
"""
import glob, io, json, math, os, re, sys
import numpy as np
import pandas as pd
import shapely
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "data")
CACHE = os.environ.get("HIST_CACHE", "/tmp/election-history-cache")
LEWIS = os.environ.get("LEWIS_DIR", os.path.join(CACHE, "congressional-district-boundaries"))
NBC26 = os.environ.get("NBC26_CACHE", os.environ.get("DOTS_CACHE", CACHE))   # <ST>-house.json from build_dots
E26 = os.environ.get("ELECTION2026_DIR", os.path.join(os.path.dirname(APP), "election2026"))
sys.path.insert(0, os.environ.get("ELECTION2026_SCRIPTS", os.path.join(E26, "scripts")))
import build_dots as B

MIT_HOUSE = "https://api.electiondata.dev/v1/house-results/download/house-results.csv"
SCALES = [1000, 10000, 100000]
YEARS = list(range(1976, 2025, 2)) + [2026]
ERAS = [(1976, 1980), (1982, 1990), (1992, 2000), (2002, 2010), (2012, 2020), (2022, 2024), (2026, 2026)]
NAME2ST = {v.replace("-", " ").title(): k for k, v in B.NAMES.items()}


def era_of(y):
    return next(a for a, b in ERAS if a <= y <= b)


# ---------------------------------------------------------------- results
def mit_results():
    fn = os.path.join(CACHE, "mit_house.csv")
    if not os.path.exists(fn):
        import urllib.request
        open(fn, "wb").write(urllib.request.urlopen(MIT_HOUSE, timeout=300).read())
    h = pd.read_csv(fn, low_memory=False)
    h["runoff"] = h.runoff.fillna(False).astype(bool)
    h["special"] = h.special.fillna(False).astype(bool)
    h = h[h.state_po != "DC"]
    # the regular November election; where a court threw out the map mid-cycle (Texas 1996) the
    # November vote was a "special" all-party primary, so fall back to that for those seats
    reg = h[(h.stage == "GEN") & (~h.special)]
    have = set(zip(reg.year, reg.state_po, reg.district))
    alt = h[h.special & ~h.runoff]
    alt = alt[[(y, s, d) not in have for y, s, d in zip(alt.year, alt.state_po, alt.district)]]
    alt = alt[alt.year % 2 == 0]
    h = pd.concat([reg, alt])
    h = h[~h.candidate.fillna("").str.upper().isin(["BLANK", "VOID", "SCATTERING", "OVER VOTES", "UNDER VOTES", "WRITEIN", "WRITE-IN", "EXHAUSTED BALLOT", "OVERVOTES", "UNDERVOTES"])]
    h["pty"] = np.where(h.party.fillna("").str.contains("DEMOCRAT"), "D",
                np.where(h.party.fillna("").str.contains("REPUBLICAN"), "R", "O"))
    out = {}
    for (y, st, d, ro), g in h.groupby(["year", "state_po", "district", "runoff"]):
        cands = {}
        for r in g.itertuples():
            c = cands.setdefault(r.candidate, {"p": "O", "v": 0.0, "lines": 0})
            if r.pty != "O" and c["p"] == "O":
                c["p"] = r.pty
            v = r.candidate_total_votes if not pd.isna(r.candidate_total_votes) else r.candidatevotes
            c["v"] = max(c["v"], 0 if pd.isna(v) else float(v))
        key = f"{st}-{max(int(d), 1)}"
        rec = out.setdefault(int(y), {}).setdefault(key, {})
        win = max(cands.values(), key=lambda c: c["v"])
        if ro:
            rec["win"] = win["p"]                       # a runoff decides the seat
            continue
        rec.setdefault("win", win["p"])
        v = {"D": 0.0, "R": 0.0, "O": 0.0}
        for c in cands.values():
            v[c["p"]] += c["v"]
        rec["v"] = [int(v["D"]), int(v["R"]), int(v["O"])]
    return out


def results_2026():
    d = json.load(open(os.path.join(E26, "data.json"), encoding="utf-8"))
    out = {}
    for x in d["house"]["districts"]:
        st, n = x["id"].split("-")
        key = f"{st}-{max(int(n) if n.isdigit() else 1, 1)}"
        v = {"D": 0, "R": 0, "O": 0}
        lead = None
        for c in x["c"]:
            p = c[0] if c[0] in ("D", "R") else "O"
            v[p] += int(c[2] or 0)
            if lead is None or (c[2] or 0) > (lead[2] or 0):
                lead = c
        out[key] = {"win": lead[0] if lead[0] in ("D", "R") else "O", "v": [v["D"], v["R"], v["O"]]}
    return out


# ---------------------------------------------------------------- shapes
_lewis_idx = None

def lewis_index():
    global _lewis_idx
    if _lewis_idx is None:
        _lewis_idx = []
        for f in glob.glob(os.path.join(LEWIS, "GeoJson", "*.geojson")):
            m = re.match(r"(.+)_(\d+)_to_(\d+)\.geojson$", os.path.basename(f))
            name = m.group(1).replace("_", " ")
            st = NAME2ST.get(name.title())
            if st:
                _lewis_idx.append((st, int(m.group(2)), int(m.group(3)), f))
    return _lewis_idx


def shapes_for(year):
    """{'ST-n': projected shapely geom on land} for the House elected in `year`."""
    out = {}
    if year == 2026:
        for st in B.ST:
            fn = os.path.join(NBC26, f"{st}-house.json")
            pg = json.load(open(fn))
            dsh = {}
            for props, polys in B.topo_geoms(pg["counties"], "districts"):
                n = max(int(str(props.get("CDFP", "1")) or 1), 1)
                g = B.on_land(B.to_shape(polys, st), st)
                if g is not None:
                    k = f"{st}-{n}"
                    dsh[k] = shapely.union(dsh[k], g) if k in dsh else g
            out.update(dsh)
        return out
    cong = (year - 1786) // 2
    for st, a, b, f in lewis_index():
        if not (a <= cong <= b):
            continue
        gj = json.load(open(f))
        for ft in gj["features"]:
            p = ft["properties"]
            if not (p.get("startcong", 0) <= cong <= p.get("endcong", 999)):
                continue
            n = max(int(float(p.get("district") or 0)), 1)
            geom = ft["geometry"]
            polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            g = B.on_land(B.to_shape([[np.array(r)[:, :2] for r in poly] for poly in polys], st), st)
            if g is not None:
                k = f"{st}-{n}"
                out[k] = shapely.union(out[k], g) if k in out else g
    return out


# ---------------------------------------------------------------- hex layout (from election2026's honeycomb builder)
def nbrs(c, rw):
    d = [(1, 0), (-1, 0), (0, -1), (1, -1), (0, 1), (1, 1)] if rw & 1 else [(1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (0, 1)]
    return [(c + a, rw + b) for a, b in d]


def hex_layout(centers, scale=26, lam=0.4, aw=0.5):
    """centers: {'ST-n': (x, y)} in the Albers frame. Returns {'ST-n': [col, row]}."""
    L48 = {k: v for k, v in centers.items() if not k.startswith(("AK-", "HI-"))}
    ks = list(L48)
    def warp(vals):
        v = np.array(vals); o = np.argsort(np.argsort(v)); q = o / (len(v) - 1) * (v.max() - v.min()) + v.min()
        return aw * v + (1 - aw) * q
    WX = warp([L48[k][0] for k in ks]); WY = warp([L48[k][1] for k in ks])
    x0, x1, y0 = WX.min(), WX.max(), WY.min()
    pts = {k: ((WX[i] - x0) / (x1 - x0) * scale + 2, (WY[i] - y0) / (x1 - x0) * scale / 0.866 + 2) for i, k in enumerate(ks)}
    states = {}
    for k in ks:
        states.setdefault(k.split("-")[0], []).append(k)
    cen = {s: (np.mean([pts[k][0] for k in kk]), np.mean([pts[k][1] for k in kk])) for s, kk in states.items()}
    C = [(c, rw) for rw in range(0, int(max(p[1] for p in pts.values())) + 6) for c in range(0, int(scale) + 6)]
    HP = np.array([(c + 0.5 * (rw & 1), rw * 0.866) for c, rw in C])
    DP = np.array([(pts[k][0], pts[k][1] * 0.866) for k in ks])
    SC = np.array([(cen[k.split("-")[0]][0], cen[k.split("-")[0]][1] * 0.866) for k in ks])
    SZ = np.array([len(states[k.split("-")[0]]) for k in ks])
    cost = ((DP[:, None, :] - HP[None, :, :]) ** 2).sum(2) + lam * ((SC[:, None, :] - HP[None, :, :]) ** 2).sum(2) / np.sqrt(SZ)[:, None]
    i, j = linear_sum_assignment(cost)
    H = {ks[a]: tuple(C[b]) for a, b in zip(i, j)}
    H = repair(H)
    maxr = max(h[1] for h in H.values()); minc = min(h[0] for h in H.values())
    for k in centers:
        if k.startswith("AK-"):
            H[k] = (minc + 1, maxr + 1)
        elif k.startswith("HI-"):
            H[k] = (minc + 4 + int(k.split("-")[1]), maxr + 2)
    return {k: list(v) for k, v in H.items()}


def layout_score(L):
    """Lower is better: hexes with at most one neighbor, enclosed holes, states split in two."""
    at = {tuple(v): k for k, v in L.items() if not k.startswith(("AK-", "HI-"))}
    iso = sum(1 for (c, r) in at if sum(1 for nb in nbrs(c, r) if nb in at) <= 1)
    cs = [p[0] for p in at]; rs = [p[1] for p in at]
    holes = sum(1 for c in range(min(cs), max(cs) + 1) for r in range(min(rs), max(rs) + 1)
                if (c, r) not in at and sum(1 for nb in nbrs(c, r) if nb in at) >= 5)
    split = sum(1 for s in {k.split("-")[0] for k in L} if s not in ("AK", "HI") and len(comps(s, {k: tuple(v) for k, v in L.items()})) > 1)
    return iso * 3 + holes * 2 + split * 20


def best_layout(centers):
    """Try a few grid widths and state-pull strengths; keep the most compact, unbroken map."""
    best = None
    for scale in (20, 22, 24):
        for lam in (0.4, 1.0):
            L = hex_layout(centers, scale=scale, lam=lam, aw=0.3)
            sc = layout_score(L)
            if best is None or sc < best[0]:
                best = (sc, L)
    return best[1]


def comps(st, H):
    S = {v for k, v in H.items() if k.split("-")[0] == st}; out = []
    while S:
        h = S.pop(); c = {h}; q = [h]
        while q:
            x = q.pop()
            for n in nbrs(*x):
                if n in S: S.remove(n); c.add(n); q.append(n)
        out.append(c)
    return sorted(out, key=len, reverse=True)


def repair(H):
    for _ in range(300):
        at = {v: k for k, v in H.items()}
        bad = [s for s in {k.split("-")[0] for k in H} if len(comps(s, H)) > 1]
        if not bad:
            break
        s = bad[0]; cs = comps(s, H); main = cs[0]; h = next(iter(cs[-1]))
        best = None
        for m in main:
            for n in nbrs(*m):
                if n in at and at[n].split("-")[0] != s:
                    t = at[n].split("-")[0]; H2 = dict(H); H2[at[n]] = h; H2[at[h]] = n
                    if len(comps(t, H2)) == 1:
                        d = (n[0] - h[0]) ** 2 + (n[1] - h[1]) ** 2
                        if best is None or d < best[0]: best = (d, at[n])
        if not best:
            free = [n for m in main for n in nbrs(*m) if n not in at]
            if not free:
                break
            n = min(free, key=lambda n: (n[0] - h[0]) ** 2 + (n[1] - h[1]) ** 2); H[at[h]] = n; continue
        k2 = best[1]; n = H[k2]; H[k2] = h; H[at[h]] = n
    still = [s for s in {k.split("-")[0] for k in H} if len(comps(s, H)) > 1]
    if still:
        print("  hex: still split", still)
    return H


# ---------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    import zipfile, shapefile
    z = zipfile.ZipFile(os.path.join(os.environ.get("DOTS_CACHE", CACHE), "states.zip")); base = "cb_2024_us_state_20m"
    sf = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")), shx=io.BytesIO(z.read(base + ".shx")))
    fips2st = {}
    for rec, shp in zip(sf.records(), sf.shapes()):
        st = rec["STUSPS"]
        if st in B.NAMES:
            fips2st[str(rec["STATEFP"]).zfill(2)] = st
            gj = shp.__geo_interface__
            polys = gj["coordinates"] if gj["type"] == "MultiPolygon" else [gj["coordinates"]]
            B.LAND[st] = B.to_shape([[np.array(r) for r in p] for p in polys], st)
    B.BG = B.BlockGroups(fips2st); BG = B.BG

    res = mit_results(); res[2026] = results_2026()
    e26_hex = json.load(open(os.path.join(E26, "data.json"), encoding="utf-8"))["house"].get("hex", {})

    meta = {"years": YEARS, "scales": SCALES, "eras": [[a, b] for a, b in ERAS], "quant": 4096, "frame": [960, 500],
            "states": B.ST, "seats": {}, "district": {}, "hex": {}, "sources": [
                "MIT Election Data + Science Lab, U.S. House 1976-2024 (CC0)",
                "NBC News / AP, 2026",
                "Lewis, DeVine, Pritcher & Martis, U.S. congressional district boundaries 1789-2025",
                "NBC News district maps, 2026"]}
    prev = None
    for y in YEARS:
        R = res.get(y, {})
        shp = shapes_for(y)
        keys = sorted(set(R) | set(shp), key=lambda k: (k.split("-")[0], int(k.split("-")[1])))
        missing_shape = [k for k in R if k not in shp]
        missing_res = [k for k in shp if k not in R]
        # block groups per district (point in polygon), population centers
        kk = [k for k in keys if k in shp]
        geoms = [shp[k] for k in kk]
        tree = shapely.STRtree(geoms)
        pi, gi = tree.query(BG.pts, predicate="within")
        first = {}
        for a, b in zip(pi, gi):
            if a not in first:
                first[a] = b
        members = [[] for _ in kk]
        for a, b in first.items():
            members[b].append(a)
        members = [np.array(m, dtype=int) for m in members]
        centers = {}
        for k in missing_shape:                      # a seat with results but no drawn shape (NY-33 in 1982-90)
            st, n = k.split("-"); n = int(n)
            nb = [shp[f"{st}-{j}"] for j in (n - 1, n + 1) if f"{st}-{j}" in shp]
            if nb:
                c = shapely.union_all(nb).representative_point(); centers[k] = (c.x, c.y)
        for k, m, g in zip(kk, members, geoms):
            if len(m):
                w = BG.pop[m]; centers[k] = (float((BG.x[m] * w).sum() / w.sum()), float((BG.y[m] * w).sum() / w.sum()))
            else:
                c = g.representative_point(); centers[k] = (c.x, c.y)
        # seats + per-district record
        seats = {"D": 0, "R": 0, "O": 0}
        drec = {}
        for k in keys:
            r = R.get(k)
            if not r:
                continue
            seats[r["win"]] += 1
            v = r.get("v", [0, 0, 0])
            flip = 0
            if prev and era_of(prev[0]) == era_of(y) and k in prev[1] and prev[1][k][0] != "DRO".index(r["win"]):
                flip = 1
            drec[k] = ["DRO".index(r["win"]), v[0], v[1], v[2], flip]
        meta["seats"][y] = seats
        meta["district"][y] = drec
        print(f"{y}: D {seats['D']} R {seats['R']} O {seats['O']}  (no shape {len(missing_shape)}{' ' + str(missing_shape[:4]) if missing_shape else ''}, no result {len(missing_res)}{' ' + str(missing_res[:4]) if missing_res else ''})")
        # hex layout for the era, from its first election
        e = era_of(y)
        if str(e) not in meta["hex"]:
            meta["hex"][str(e)] = e26_hex if (e == 2026 and e26_hex) else best_layout(centers)
        # dots
        rng = np.random.default_rng(5000 + y)
        for s in SCALES:
            xs, ys, ps, ss = [], [], [], []
            for k, m, g in zip(kk, members, geoms):
                r = R.get(k)
                if not r or "v" not in r:
                    continue
                for p, v in enumerate(r["v"]):
                    n = B.sround(v, s, rng)
                    if n <= 0:
                        continue
                    pts = B.place(g, m if len(m) else None, n, rng)
                    xs.append(pts[:, 0]); ys.append(pts[:, 1]); ps.append(np.full(n, p)); ss.append(np.full(n, B.ST.index(k.split("-")[0])))
            x = np.concatenate(xs); yy = np.concatenate(ys); p = np.concatenate(ps).astype(np.uint8); si = np.concatenate(ss).astype(np.uint8)
            o = rng.permutation(len(x)); x, yy, p, si = x[o], yy[o], p[o], si[o]
            qx = np.clip(np.round(x * 4096), 0, 2**32 - 1).astype("<u4"); qy = np.clip(np.round(yy * 4096), 0, 2**32 - 1).astype("<u4")
            open(os.path.join(OUT, f"house-{y}-{s}.bin"), "wb").write(np.column_stack([qx, qy]).tobytes() + (si | (p << 6)).astype(np.uint8).tobytes())
        prev = (y, drec)
    json.dump(meta, open(os.path.join(OUT, "house.json"), "w"), separators=(",", ":"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
