#!/usr/bin/env python3
"""Presidential results by county, 1976-2024, as dot layers + a county table.

Sources (all public domain or open):
  1976-2020  Carlos Algara & Isaac Hale, county-level presidential returns 1868-2020
             (Harvard Dataverse, file 5028532). No Alaska.
  2024       MIT Election Data + Science Lab, County Presidential Returns 2000-2024
             (CC0), via electiondata.dev. Alaska 2000-2024 comes from here too.
  Alaska 1976-1996  state totals (Wikipedia, from the Alaska Division of Elections).

Dots are placed exactly like election2026/scripts/build_dots.py: a county's votes are shared
out across its 2020 Census block groups by population and scattered around each block
group's population center. That uses 2020 population for every year, so within a county,
1976 dots sit where people live today; across counties the vote totals are the real ones.
Alaska has no counties in these files, so its dots are spread over the whole state.

Output (in election-history/data/):
  pres-<year>-<scale>.bin   same format as election2026 dots (uint32 x, uint32 y, uint8 party<<6|state)
  pres.json                 years, national totals, per-county centers and D/R/other by year
"""
import io, json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "data")
CACHE = os.environ.get("HIST_CACHE", "/tmp/election-history-cache")
DOTS_CACHE = os.environ.get("DOTS_CACHE", CACHE)

sys.path.insert(0, os.environ.get("ELECTION2026_SCRIPTS", os.path.join(os.path.dirname(APP), "election2026", "scripts")))
os.environ.setdefault("DOTS_CACHE", DOTS_CACHE)
import build_dots as B                       # projection, block groups, placement

ALGARA = "https://dataverse.harvard.edu/api/access/datafile/5028532"
MIT_COUNTY = "https://api.electiondata.dev/v1/county-president/download/county-president.csv"
SCALES = [1000, 10000, 100000]
YEARS = list(range(1976, 2025, 4))

# counties that merged or were renumbered after 1976 -> their 2020 home
REMAP = {"12025": "12086",   # Dade -> Miami-Dade
         "51515": "51019",   # Bedford city -> Bedford County
         "51560": "51005",   # Clifton Forge -> Alleghany
         "51780": "51083",   # South Boston -> Halifax
         "46113": "46102",   # Shannon -> Oglala Lakota
         "46131": "46071"}   # Washabaugh -> Jackson
KC = ["29095", "29047", "29165"]   # Kansas City reports apart from Jackson/Clay/Platte; spread over all three

# Alaska totals before 2000 (D, R, total); "other" is the remainder
AK_OLD = {1976: (44058, 71555, 123574), 1980: (41842, 86112, 158445), 1984: (62007, 138377, 207605),
          1988: (72584, 119251, 200116), 1992: (78294, 102000, 258506), 1996: (80380, 122746, 241620)}


def fetch(url, name):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, name)
    if not os.path.exists(fn):
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "sadh.app-election-history"})
        open(fn, "wb").write(urllib.request.urlopen(req, timeout=300).read())
    return fn


NAMES_BY_FIPS = {}

def county_votes():
    """DataFrame year, fips, D, R, O  (fips '02000' = Alaska statewide)."""
    import pyreadr
    a = pyreadr.read_r(fetch(ALGARA, "algara_1868_2020.Rdata"))["pres_elections_release"]
    a = a[a.election_year >= 1976].copy()
    a["year"] = a.election_year.astype(int)
    a["fips"] = a.fips.astype(str).str.zfill(5).replace(REMAP)
    a["D"] = a.democratic_raw_votes.fillna(0)
    a["R"] = a.republican_raw_votes.fillna(0)
    a["O"] = (a.raw_county_vote_totals.fillna(0) - a.D - a.R).clip(lower=0)
    global NAMES_BY_FIPS
    nm = a.sort_values("year").groupby("fips").agg(n=("county_name", "last"), s=("state", "last"))
    NAMES_BY_FIPS = {f: (str(r.n).title().replace("'S", "'s"), r.s) for f, r in nm.iterrows()}
    a = a[["year", "fips", "D", "R", "O"]]

    m = pd.read_csv(fetch(MIT_COUNTY, "mit_county_president.csv"), dtype={"county_fips": str})
    m = m[m.year.isin([2000, 2004, 2008, 2012, 2016, 2020, 2024])]
    m["P"] = m.party.map({"DEMOCRAT": "D", "REPUBLICAN": "R"}).fillna("O")
    m.loc[m.state_po == "AK", "county_fips"] = "02000"
    kc = (m.state_po == "MO") & m.county_fips.isna() & (m.county_name == "KANSAS CITY")
    m = m[m.county_fips.notna() | kc].copy()
    m["county_fips"] = m.county_fips.fillna("").str.zfill(5).replace(REMAP)
    m.loc[kc[kc].index.intersection(m.index), "county_fips"] = "KC"
    p = m.pivot_table(index=["year", "county_fips"], columns="P", values="candidatevotes", aggfunc="sum", fill_value=0).reset_index()
    p = p.rename(columns={"county_fips": "fips"})
    ak = p[p.fips == "02000"]
    p2024 = p[p.year == 2024]

    ak_old = pd.DataFrame([{"year": y, "fips": "02000", "D": d, "R": r, "O": max(t - d - r, 0)} for y, (d, r, t) in AK_OLD.items()])
    out = pd.concat([a, ak_old, ak[ak.year < 2024][["year", "fips", "D", "R", "O"]], p2024[["year", "fips", "D", "R", "O"]]])
    return out.groupby(["year", "fips"], as_index=False)[["D", "R", "O"]].sum()


def main():
    os.makedirs(OUT, exist_ok=True)
    votes = county_votes()

    # block groups + state shapes (reuse the 2026 builder's loaders)
    import zipfile, shapefile, urllib.request
    zp = os.path.join(DOTS_CACHE, "states.zip")
    if not os.path.exists(zp):
        os.makedirs(DOTS_CACHE, exist_ok=True)
        open(zp, "wb").write(urllib.request.urlopen(B.STATES_ZIP, timeout=60).read())
    z = zipfile.ZipFile(zp); base = "cb_2024_us_state_20m"
    sf = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")), shx=io.BytesIO(z.read(base + ".shx")))
    fips2st = {}
    for rec, shp in zip(sf.records(), sf.shapes()):
        st = rec["STUSPS"]
        if st in B.NAMES:
            fips2st[str(rec["STATEFP"]).zfill(2)] = st
            gj = shp.__geo_interface__
            polys = gj["coordinates"] if gj["type"] == "MultiPolygon" else [gj["coordinates"]]
            B.LAND[st] = B.to_shape([[np.array(r) for r in p] for p in polys], st)
    fips2st["11"] = "MD"          # DC has no slot in the 50-state index; its dots ride with Maryland's
    B.BG = B.BlockGroups(fips2st)
    BG = B.BG

    # block-group index per county (and Alaska statewide, Kansas City over its three counties)
    by_cty = {}
    order = np.argsort(BG.cty, kind="stable")
    ctys, starts = np.unique(BG.cty[order], return_index=True)
    ends = list(starts[1:]) + [len(order)]
    for c, s, e in zip(ctys, starts, ends):
        by_cty[c] = order[s:e]
    by_cty["02000"] = np.where(BG.st == B.ST.index("AK"))[0]
    by_cty["KC"] = np.concatenate([by_cty[c] for c in KC])

    unplaced = votes[~votes.fips.isin(by_cty.keys())]
    if len(unplaced):
        print("unplaced counties:", unplaced.groupby("fips")[["D", "R", "O"]].sum().sum(axis=1).sort_values(ascending=False).head(10).to_dict())

    # county centers (population-weighted) for the shift map
    counties = {}
    for f, idx in by_cty.items():
        w = BG.pop[idx]
        counties[f] = [round(float((BG.x[idx] * w).sum() / w.sum()), 2), round(float((BG.y[idx] * w).sum() / w.sum()), 2),
                       int(BG.st[idx[0]])]

    meta = {"years": YEARS, "scales": SCALES, "states": B.ST, "quant": 4096, "frame": [960, 500],
            "national": {}, "counties": {}, "sources": [
                "Algara & Hale, county presidential returns 1868-2020 (Harvard Dataverse)",
                "MIT Election Data + Science Lab, County Presidential Returns 2000-2024 (CC0)",
                "Alaska 1976-1996: Alaska Division of Elections via Wikipedia"]}
    for y in YEARS:
        vy = votes[(votes.year == y) & votes.fips.isin(by_cty.keys())]
        meta["national"][y] = [int(vy.D.sum()), int(vy.R.sum()), int(vy.O.sum())]
        rng = np.random.default_rng(1000 + y)
        for s in SCALES:
            xs, ys, ps, ss = [], [], [], []
            for r in vy.itertuples():
                idx = by_cty[r.fips]
                for p, v in ((0, r.D), (1, r.R), (2, r.O)):
                    n = B.sround(v, s, rng)
                    if n <= 0:
                        continue
                    pts = place_bg(idx, n, rng)
                    xs.append(pts[:, 0]); ys.append(pts[:, 1])
                    ps.append(np.full(n, p)); ss.append(np.full(n, BG.st[idx[0]]))
            x = np.concatenate(xs); yy = np.concatenate(ys)
            p = np.concatenate(ps).astype(np.uint8); si = np.concatenate(ss).astype(np.uint8)
            o = rng.permutation(len(x)); x, yy, p, si = x[o], yy[o], p[o], si[o]
            qx = np.clip(np.round(x * 4096), 0, 2**32 - 1).astype("<u4")
            qy = np.clip(np.round(yy * 4096), 0, 2**32 - 1).astype("<u4")
            buf = np.column_stack([qx, qy]).tobytes() + (si | (p << 6)).astype(np.uint8).tobytes()
            open(os.path.join(OUT, f"pres-{y}-{s}.bin"), "wb").write(buf)
        nat = meta["national"][y]
        print(f"{y}: D {nat[0]:,}  R {nat[1]:,}  other {nat[2]:,}")

    # compact county table: fips -> [x, y, state, [D,R,O per year...]]
    piv = votes.pivot_table(index="fips", columns="year", values=["D", "R", "O"], fill_value=0)
    for f in piv.index:
        if f not in counties:
            continue
        row = []
        for y in YEARS:
            row.append([int(piv.loc[f, ("D", y)]), int(piv.loc[f, ("R", y)]), int(piv.loc[f, ("O", y)])])
        n, st = NAMES_BY_FIPS.get(f, ("", ""))
        if f == "02000": n, st = "Alaska (statewide)", "AK"
        if f == "KC": n, st = "Kansas City (city)", "MO"
        if f == "11001": n, st = "Washington, D.C.", "DC"
        if n and not n.endswith(("City", "(city)", "statewide)")) and st not in ("AK", "LA") and not f.startswith("51") or (f.startswith("51") and int(f[2:]) < 500):
            n = n + " County"
        if st == "LA" and n and "Parish" not in n: n = n + " Parish"
        meta["counties"][f] = counties[f] + [row, n, st]
    json.dump(meta, open(os.path.join(OUT, "pres.json"), "w"), separators=(",", ":"))
    print("wrote", OUT, "counties", len(meta["counties"]))


def place_bg(idx, n, rng):
    """Like build_dots.place, but with no unit polygon (counties are whole block groups)."""
    BG = B.BG
    w = BG.pop[idx]
    alloc = rng.multinomial(n, w / w.sum())
    rep = np.repeat(idx, alloc)
    ang = rng.uniform(0, 2 * np.pi, n)
    rad = BG.r[rep] * rng.uniform(0, 1, n)
    return np.column_stack([BG.x[rep] + rad * np.cos(ang), BG.y[rep] + rad * np.sin(ang)])


if __name__ == "__main__":
    main()
