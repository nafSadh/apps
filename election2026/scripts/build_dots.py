#!/usr/bin/env python3
"""Build the dot-density layers for election2026 (Senate, House, governor).

Each dot stands for a block of votes (1,000 / 10,000 / 100,000) for one party,
dropped at a random spot inside the smallest unit NBC News / AP report:

  Senate, governor  county (town in New England, municipality in RI,
                    state House district in Alaska), colored by that unit's result.
  House             district (2026 lines), colored by the district result. Inside a
                    district, dots are spread over its counties in proportion to
                    each county's turnout in that state's Senate or governor race,
                    so a district's dots land where its voters live. States with no
                    statewide race (IN, MO, ND, UT, WA) spread them evenly.

Counts use stochastic rounding (a unit with 1,400 D votes at 1k/dot gets 1 dot
60% of the time and 2 dots 40%), with a fixed seed, so totals stay unbiased at
every scale and rebuilds are stable.

Output (next to index.html):
  dots/meta.json            scales, per-layer totals, as-of, state outline paths
  dots/<layer>-<scale>.bin  per dot: uint16 x, uint16 y|party<<14, uint8 state

Coordinates are Albers USA (same constants as d3.geoAlbersUsa) in a 960x500
frame, quantized x*64 and y*24.

Needs numpy, shapely, pyshp:  pip install numpy shapely pyshp
Usage: python3 election2026/scripts/build_dots.py [--cached]
(about 2.5 minutes: 121 pages, one second apart)
"""
import io, json, math, os, re, sys, tempfile, time, urllib.request, zipfile
import numpy as np
import shapefile
import shapely
from shapely.geometry import Polygon, MultiPolygon, shape
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # election2026/
OUT = os.path.join(ROOT, "dots")
CACHE = os.environ.get("DOTS_CACHE", os.path.join(tempfile.gettempdir(), "election2026-dots-cache"))
UA = "sadh.app-election2026-dots"
SCALES = [1000, 10000, 100000]
STATES_ZIP = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip"

NAMES = {'AL':'alabama','AK':'alaska','AZ':'arizona','AR':'arkansas','CA':'california','CO':'colorado','CT':'connecticut','DE':'delaware','FL':'florida','GA':'georgia','HI':'hawaii','ID':'idaho','IL':'illinois','IN':'indiana','IA':'iowa','KS':'kansas','KY':'kentucky','LA':'louisiana','ME':'maine','MD':'maryland','MA':'massachusetts','MI':'michigan','MN':'minnesota','MS':'mississippi','MO':'missouri','MT':'montana','NE':'nebraska','NV':'nevada','NH':'new-hampshire','NJ':'new-jersey','NM':'new-mexico','NY':'new-york','NC':'north-carolina','ND':'north-dakota','OH':'ohio','OK':'oklahoma','OR':'oregon','PA':'pennsylvania','RI':'rhode-island','SC':'south-carolina','SD':'south-dakota','TN':'tennessee','TX':'texas','UT':'utah','VT':'vermont','VA':'virginia','WA':'washington','WV':'west-virginia','WI':'wisconsin','WY':'wyoming'}
ST = sorted(NAMES)
FIPS2ST = {}
SPECIAL = {("OH", "senate"), ("FL", "senate")}     # 2026 special elections live under another path
PARTY = {"dem": 0, "gop": 1}                       # anything else -> 2 (other / independent)


# ---------------------------------------------------------------- fetching
def fetch_race(st, office, refetch=False):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"{st}-{office}.json")
    if os.path.exists(fn) and not refetch:
        return json.load(open(fn))
    kind = "2026-special-elections" if (st, office) in SPECIAL else "2026-elections"
    url = f"https://www.nbcnews.com/politics/{kind}/{NAMES[st]}-{office}-results"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    pp = json.loads(m.group(1))["props"]["pageProps"]
    race = (pp.get("races") or [None])[0] or {}
    keep = {"geo": pp.get("geography"), "lastModified": pp.get("lastModified"),
            "mapData": race.get("mapData") or {}, "counties": pp["topojsons"].get("counties"),
            "cities": (pp["topojsons"].get("cities") or {}).get("features", [])}
    json.dump(keep, open(fn, "w"))
    time.sleep(1)
    return keep


# ---------------------------------------------------------------- topojson
def topo_geoms(topo, obj):
    tr = topo.get("transform")
    arcs = []
    for a in topo["arcs"]:
        pts = np.array(a, dtype=float)
        if tr:
            pts = np.cumsum(pts, axis=0)
            pts = pts * tr["scale"] + tr["translate"]
        arcs.append(pts)

    def ring(idx):
        parts = []
        for i in idx:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            parts.append(p if not parts else p[1:])
        return np.concatenate(parts)

    out = []
    for g in topo["objects"][obj]["geometries"]:
        t = g.get("type")
        if t == "Polygon":
            polys = [g["arcs"]]
        elif t == "MultiPolygon":
            polys = g["arcs"]
        else:
            continue
        out.append((g.get("properties", {}), [[ring(r) for r in poly] for poly in polys]))
    return out


# ---------------------------------------------------------------- projection (d3.geoAlbersUsa)
def _conic(phi0, phi1, lam0, center, k, tx, ty):
    p0, p1 = math.radians(phi0), math.radians(phi1)
    sy0 = math.sin(p0)
    n = (sy0 + math.sin(p1)) / 2
    c = 1 + sy0 * (2 * n - sy0)
    r0 = math.sqrt(c) / n

    def raw(lon, lat, rot=lam0):
        lam = np.radians(lon + rot)
        lam = (lam + np.pi) % (2 * np.pi) - np.pi
        r = np.sqrt(np.maximum(c - 2 * n * np.sin(np.radians(lat)), 0)) / n
        return r * np.sin(lam * n), r0 - r * np.cos(lam * n)

    cx, cy = raw(np.array([center[0]]), np.array([center[1]]), 0)   # d3 center is in rotated coords
    cx, cy = cx[0], cy[0]

    def f(lon, lat):
        x, y = raw(lon, lat)
        return tx + (x - cx) * k, ty - (y - cy) * k
    return f

K, TX, TY = 1070, 480, 250
P_L48 = _conic(29.5, 45.5, 96, (-0.6, 38.7), K, TX, TY)
P_AK = _conic(55, 65, 154, (-2, 58.5), 0.35 * K, TX - 0.307 * K, TY + 0.201 * K)
P_HI = _conic(8, 18, 157, (-3, 19.9), K, TX - 0.205 * K, TY + 0.212 * K)

def proj_for(st):
    return P_AK if st == "AK" else P_HI if st == "HI" else P_L48

def to_shape(polys, st):
    f = proj_for(st)
    out = []
    for poly in polys:
        rings = []
        for r in poly:
            x, y = f(r[:, 0], r[:, 1])
            rings.append(np.column_stack([x, y]))
        if len(rings[0]) >= 4:
            p = Polygon(rings[0], rings[1:])
            if not p.is_valid:
                p = p.buffer(0)
            out.append(p)
    g = unary_union(out) if out else None
    return g if g is not None and not g.is_empty else None


# ---------------------------------------------------------------- matching NBC result keys to shapes
def slug(s):
    s = str(s).lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

SUFFIXES = ("-town", "-city", "-plantation", "-ut", "-township", "-twp", "-gore", "-grant", "-location")

LAND = {}                                          # st -> projected Census land outline (no water)

def on_land(g, st):
    """Clip a county/town/district shape to the state's land outline, so no dots land in bays or lakes."""
    land = LAND.get(st)
    if g is None or land is None:
        return g
    try:
        c = g.intersection(land)
    except Exception:
        return g
    return c if not c.is_empty and c.area > 0.02 * g.area else g

def unit_shapes(page, st):
    """{result_key: shapely geom} for one statewide race page."""
    topo = page["counties"]
    geo = page["geo"]
    objs = topo["objects"]
    obj = geo if geo in objs else next(iter(objs))
    geoms = topo_geoms(topo, obj)
    keys = list(page["mapData"])
    # pick the property field that matches the most result keys
    best = None
    fields = set().union(*[p.keys() for p, _ in geoms]) if geoms else set()
    kset = {slug(k) for k in keys}
    for fld in fields:
        m = len(kset & {slug(p.get(fld, "")) for p, _ in geoms})
        if not best or m > best[0]:
            best = (m, fld)
    fld = best[1]
    by = {}
    for p, polys in geoms:
        s = slug(p.get(fld, ""))
        g = on_land(to_shape(polys, st), st)
        if g is None:
            continue
        by[s] = unary_union([by[s], g]) if s in by else g
    out, missing = {}, []
    for k in keys:
        s = slug(k)
        cand = [s] + [s[: -len(x)] for x in SUFFIXES if s.endswith(x)]
        hit = next((c for c in cand if c in by), None)
        if hit is None and st == "IL" and k.startswith("17031"):
            hit = "17031"                                      # Chicago + suburban Cook -> Cook County
        if hit is None:
            missing.append(k)
        else:
            out.setdefault(hit, []).append(k)
    return by, out, missing


def party_votes(cands):
    v = [0, 0, 0]
    for c in cands or []:
        v[PARTY.get(c.get("party"), 2)] += c.get("votes") or 0
    return v


# ---------------------------------------------------------------- sampling
def sample_in(geom, n, rng):
    if n <= 0 or geom is None:
        return np.empty((0, 2))
    minx, miny, maxx, maxy = geom.bounds
    got = []
    need = n
    frac = max(geom.area / max((maxx - minx) * (maxy - miny), 1e-9), 0.02)
    tries = 0
    while need > 0 and tries < 60:
        m = int(need / frac * 1.3) + 8
        xs = rng.uniform(minx, maxx, m)
        ys = rng.uniform(miny, maxy, m)
        ok = shapely.contains_xy(geom, xs, ys)
        pts = np.column_stack([xs[ok], ys[ok]])[:need]
        got.append(pts)
        need -= len(pts)
        tries += 1
    if need > 0:                                               # sliver: fall back to a representative point
        rp = geom.representative_point()
        got.append(np.tile([rp.x, rp.y], (need, 1)))
    return np.concatenate(got)


def sround(v, s, rng):
    q = v / s
    f = math.floor(q)
    return f + (1 if rng.random() < q - f else 0)


# ---------------------------------------------------------------- build
def main():
    refetch = "--cached" not in sys.argv       # default: fresh results; --cached reuses the last fetch
    data = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
    sen = [r["st"] for r in data["senate"]["races"]]
    gov = [r["st"] for r in data["governors"]["races"]]

    pages, last, failed = {}, [], []
    for st in ST:
        for off, has in (("house", True), ("senate", st in sen), ("governor", st in gov)):
            if has:
                try:
                    pages[(st, off)] = fetch_race(st, off, refetch)
                    last.append(pages[(st, off)].get("lastModified") or "")
                except Exception as e:
                    failed.append(f"{st} {off}: {e}")
    if failed:                                   # never publish a map with a state silently missing
        sys.exit("fetch failed, nothing written:\n  " + "\n  ".join(failed))

    def path_of(g, tol):
        g = g.simplify(tol, preserve_topology=True)
        polys = [g] if isinstance(g, Polygon) else list(getattr(g, "geoms", []))
        d = []
        for p in polys:
            for r in [p.exterior, *p.interiors]:
                c = np.asarray(r.coords)
                if len(c) < 4:
                    continue
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in c) + "Z")
        return "".join(d)

    # state outlines
    os.makedirs(CACHE, exist_ok=True)
    zp = os.path.join(CACHE, "states.zip")
    if not os.path.exists(zp):
        open(zp, "wb").write(urllib.request.urlopen(STATES_ZIP, timeout=60).read())
    z = zipfile.ZipFile(zp)
    base = "cb_2024_us_state_20m"
    sf = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")),
                          shx=io.BytesIO(z.read(base + ".shx")))
    state_shape = {}
    for rec, shp in zip(sf.records(), sf.shapes()):
        st = rec["STUSPS"]
        if st not in NAMES:
            continue
        gj = shp.__geo_interface__
        polys = gj["coordinates"] if gj["type"] == "MultiPolygon" else [gj["coordinates"]]
        g = to_shape([[np.array(r) for r in p] for p in polys], st)
        state_shape[st] = g
        LAND[st] = g

    # turnout weights for House placement: statewide-race units with total votes
    turnout = {}
    unit_cache = {}
    for st in ST:
        for off in ("senate", "governor"):
            pg = pages.get((st, off))
            if not pg:
                continue
            by, keymap, missing = unit_shapes(pg, st)
            unit_cache[(st, off)] = (by, keymap, missing)
            if st not in turnout:
                md = pg["mapData"]
                turnout[st] = [(by[s], sum(sum(party_votes(md[k]["candidates"])) for k in ks))
                               for s, ks in keymap.items()]

    meta = {"scales": SCALES, "frame": [960, 500], "quant": [64, 24], "states": ST,
            "as_of": max(last) if last else None, "layers": {}, "outline": {}}
    os.makedirs(OUT, exist_ok=True)

    for layer in ("senate", "governor", "house"):
        rng = np.random.default_rng(2026 + len(layer))
        groups = []                   # (state_idx, party, geom-or-pieces, votes)
        dropped = 0
        for si, st in enumerate(ST):
            pg = pages.get((st, layer))
            if not pg:
                continue
            md = pg["mapData"]
            if layer != "house":
                by, keymap, missing = unit_cache[(st, layer)]
                dropped += sum(sum(party_votes(md[k]["candidates"])) for k in missing)
                for s, ks in keymap.items():
                    v = [0, 0, 0]
                    for k in ks:
                        pv = party_votes(md[k]["candidates"])
                        v = [a + b for a, b in zip(v, pv)]
                    for p in range(3):
                        if v[p]:
                            groups.append((si, p, [(by[s], 1.0)], v[p]))
            else:
                geoms = topo_geoms(pg["counties"], "districts")
                dshape = {}
                for props, polys in geoms:
                    cd = str(props.get("CDFP", "")).zfill(2)
                    g = on_land(to_shape(polys, st), st)
                    if g is not None:
                        dshape[cd] = unary_union([dshape[cd], g]) if cd in dshape else g
                for key, race in md.items():
                    cd = str(key).zfill(2)
                    g = dshape.get(cd) or (next(iter(dshape.values())) if len(dshape) == 1 else None)
                    v = party_votes(race.get("candidates"))
                    if g is None:
                        dropped += sum(v)
                        continue
                    pieces = []
                    if st in turnout:
                        for ug, tv in turnout[st]:
                            if tv <= 0 or not ug.intersects(g):
                                continue
                            part = ug.intersection(g)
                            if part.is_empty or part.area <= 0:
                                continue
                            pieces.append((part, tv * part.area / ug.area))
                    if not pieces or sum(w for _, w in pieces) <= 0:
                        pieces = [(g, 1.0)]
                    for p in range(3):
                        if v[p]:
                            groups.append((si, p, pieces, v[p]))

        tot = [0, 0, 0]
        by_state = {}
        for si, p, _, v in groups:
            tot[p] += v
            by_state.setdefault(ST[si], [0, 0, 0])[p] += v
        meta["layers"][layer] = {"votes": tot, "dropped_votes": dropped, "by_state": by_state, "dots": {}}
        for s in SCALES:
            xs, ys, ps, ss = [], [], [], []
            for si, p, pieces, v in groups:
                n = sround(v, s, rng)
                if n <= 0:
                    continue
                w = np.array([pw for _, pw in pieces], dtype=float)
                alloc = rng.multinomial(n, w / w.sum()) if len(pieces) > 1 else [n]
                for (pg_, _), k in zip(pieces, alloc):
                    if k:
                        pts = sample_in(pg_, int(k), rng)
                        xs.append(pts[:, 0]); ys.append(pts[:, 1])
                        ps.append(np.full(len(pts), p)); ss.append(np.full(len(pts), si))
            x = np.concatenate(xs); y = np.concatenate(ys)
            p = np.concatenate(ps).astype(np.uint16); si = np.concatenate(ss).astype(np.uint8)
            order = rng.permutation(len(x))                        # random draw order for the animation
            x, y, p, si = x[order], y[order], p[order], si[order]
            qx = np.clip(np.round(x * 64), 0, 65535).astype(np.uint16)
            qy = np.clip(np.round(y * 24), 0, 16383).astype(np.uint16) | (p << 14)
            buf = np.column_stack([qx, qy]).astype("<u2").tobytes() + si.tobytes()
            open(os.path.join(OUT, f"{layer}-{s}.bin"), "wb").write(buf)
            meta["layers"][layer]["dots"][str(s)] = {"n": int(len(x)),
                                                   "by_party": [int((p == i).sum()) for i in range(3)]}
            print(f"{layer:8s} 1:{s:<6d} {len(x):7d} dots  ({len(buf)/1024:.0f} kB)")
        print(f"{layer:8s} votes D {tot[0]:,} R {tot[1]:,} other {tot[2]:,}  unplaced {dropped:,}")

    meta["outline"] = {st: path_of(g, 0.35) for st, g in state_shape.items() if g is not None}
    meta["bbox"] = {st: [round(v, 1) for v in g.bounds] for st, g in state_shape.items() if g is not None}
    # city labels (NBC's own picks per state); TYPE national > primary > secondary, POSITION = label side
    meta["cities"] = {}
    for st in ST:
        pg = pages.get((st, "house"))
        out = []
        for f in (pg or {}).get("cities") or []:
            pr = f.get("properties", {})
            if pr.get("STATE") != st:
                continue
            lon, lat = f["geometry"]["coordinates"][:2]
            x, y = proj_for(st)(np.array([float(lon)]), np.array([float(lat)]))
            out.append([pr.get("NAME"), round(float(x[0]), 2), round(float(y[0]), 2),
                        {"national": 0, "primary": 1}.get(pr.get("TYPE"), 2), pr.get("POSITION") or "R"])
        if out:
            meta["cities"][st] = sorted(out, key=lambda c: c[3])
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), separators=(",", ":"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
