#!/usr/bin/env python3
"""
update.py — maintain the data behind sadh.app/wc2026.

The app reads ../data.json (with an inline snapshot in index.html as offline
fallback). Only two things change during the tournament:

  * locked   {matchNo: [homeGoals, awayGoals]}  -- scores of played matches
  * ratings  {code: {fifa, elo, odds, opta, form}}

teams / fixtures / bracket are fixed at the draw and are not touched here.

Typical use
-----------
  python update.py --check                 # validate data.json, exit 1 on error
  python update.py --results results.csv   # set played scores from a CSV
  python update.py --ratings ratings.csv   # merge updated ratings from a CSV
  python update.py --fetch-footballdata --token $FD_TOKEN   # pull results from an API
  python update.py --sync-embed            # rewrite the inline fallback in index.html
  python update.py                         # just re-validate + pretty-write data.json

CSV formats
-----------
  results.csv : matchNo,homeGoals,awayGoals        (header optional)
  ratings.csv : code,fifa,elo,odds,opta,form       (form e.g. WWDLW, newest first)

Only the Python standard library is used (urllib for the optional fetch).
"""
import argparse, csv, json, re, sys, datetime, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data.json"
INDEX = ROOT / "index.html"

RATING_KEYS = ("fifa", "elo", "odds", "opta", "form")

# football-data.org / common feeds spell some teams differently than our codes.
NAME_ALIASES = {
    "united states": "USA", "usa": "USA", "korea republic": "KOR", "south korea": "KOR",
    "ir iran": "IRN", "iran": "IRN", "turkey": "TUR", "türkiye": "TUR", "turkiye": "TUR",
    "côte d'ivoire": "CIV", "cote d'ivoire": "CIV", "ivory coast": "CIV",
    "cabo verde": "CPV", "cape verde": "CPV", "cape verde islands": "CPV", "czech republic": "CZE", "czechia": "CZE",
    "dr congo": "COD", "congo dr": "COD", "bosnia and herzegovina": "BIH", "bosnia & h.": "BIH", "bosnia-herzegovina": "BIH",
}


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def name_to_code(data):
    idx = dict(NAME_ALIASES)
    for code, t in data["teams"].items():
        idx[t["name"].strip().lower()] = code
        idx[code.lower()] = code
    return idx


# ----------------------------------------------------------------------------- validate
def validate(data):
    errs = []
    teams = data.get("teams", {})
    fixtures = data.get("fixtures", [])
    locked = data.get("locked", {})
    ratings = data.get("ratings", {})
    codes = set(teams)

    if len(codes) != 48:
        errs.append(f"expected 48 teams, got {len(codes)}")
    if len(fixtures) != 72:
        errs.append(f"expected 72 fixtures, got {len(fixtures)}")

    fixture_nos = {f["no"] for f in fixtures}
    for f in fixtures:
        for side in ("home", "away"):
            if f[side] not in codes:
                errs.append(f"fixture {f['no']}: unknown team {f[side]!r}")

    for k, v in locked.items():
        if int(k) not in fixture_nos:
            errs.append(f"locked match {k}: not a valid fixture number")
        if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) and x >= 0 for x in v)):
            errs.append(f"locked match {k}: score must be [int,int], got {v!r}")

    for code in codes:
        r = ratings.get(code)
        if not r:
            errs.append(f"ratings: missing team {code}")
            continue
        for key in RATING_KEYS:
            if key not in r:
                errs.append(f"ratings[{code}]: missing {key!r}")
        if isinstance(r.get("form"), str) and any(ch not in "WDL" for ch in r["form"]):
            errs.append(f"ratings[{code}].form has chars outside W/D/L: {r['form']!r}")
    for code in ratings:
        if code not in codes:
            errs.append(f"ratings has unknown team {code!r}")

    ko = data.get("ko", [])
    if not isinstance(ko, list):
        errs.append("ko must be a list")
    else:
        for i, e in enumerate(ko):
            if not isinstance(e, dict):
                errs.append(f"ko[{i}]: must be an object"); continue
            for side in ("home", "away"):
                if e.get(side) not in codes:
                    errs.append(f"ko[{i}]: unknown team {e.get(side)!r}")
            if e.get("w") is not None and e["w"] not in codes:
                errs.append(f"ko[{i}]: unknown winner {e['w']!r}")
            for k in ("h", "a"):
                if not (isinstance(e.get(k), int) and e[k] >= 0):
                    errs.append(f"ko[{i}]: {k} must be a non-negative int, got {e.get(k)!r}")
            if "p" in e and not (isinstance(e["p"], list) and len(e["p"]) == 2
                                 and all(isinstance(x, int) and x >= 0 for x in e["p"])):
                errs.append(f"ko[{i}]: p (penalties) must be [int,int], got {e['p']!r}")

    kt = data.get("koTimes", [])
    if not isinstance(kt, list):
        errs.append("koTimes must be a list")
    else:
        for i, e in enumerate(kt):
            if not (isinstance(e, dict) and e.get("home") in codes and e.get("away") in codes and isinstance(e.get("t"), str)):
                errs.append(f"koTimes[{i}]: need {{home, away, t}} with valid codes, got {e!r}")

    ta = data.get("thirdAlloc", {})
    if not isinstance(ta, dict):
        errs.append("thirdAlloc must be an object {slot: group}")
    else:
        for slot, g in ta.items():
            if not (isinstance(g, str) and len(g) == 1 and g in "ABCDEFGHIJKL"):
                errs.append(f"thirdAlloc[{slot}]: group must be one letter A–L, got {g!r}")
    return errs


# ----------------------------------------------------------------------------- merges
def merge_results_csv(data, path):
    n = 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if not row or row[0].strip().lower() in ("matchno", "match", "#", ""):
                continue
            try:
                no, hg, ag = int(row[0]), int(row[1]), int(row[2])
            except (ValueError, IndexError):
                print(f"  ! skipped row {row!r}", file=sys.stderr); continue
            data["locked"][str(no)] = [hg, ag]; n += 1
    print(f"  merged {n} results from {path}")


def merge_ratings_csv(data, path):
    n = 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("code") or "").strip().upper()
            if code not in data["teams"]:
                print(f"  ! unknown code {code!r}", file=sys.stderr); continue
            r = data["ratings"].setdefault(code, {})
            for key in ("fifa", "elo", "odds", "opta"):
                val = row.get(key)
                if val not in (None, ""):
                    r[key] = float(val) if "." in val else int(val)
            if row.get("form"):
                r["form"] = row["form"].strip().upper()
            n += 1
    print(f"  merged ratings for {n} teams from {path}")


# --- international results dataset (Kaggle martj42 "results.csv", 1872→present) ---
# dataset name -> our code. Predecessors are folded into the modern successor (as FIFA does).
WC_INTL_NAMES = {
    "Argentina": "ARG", "Spain": "ESP", "France": "FRA", "England": "ENG", "Portugal": "POR",
    "Brazil": "BRA", "Netherlands": "NED", "Germany": "GER", "West Germany": "GER", "Belgium": "BEL",
    "Croatia": "CRO", "Morocco": "MAR", "Colombia": "COL", "Mexico": "MEX", "Senegal": "SEN",
    "Uruguay": "URU", "United States": "USA", "Japan": "JPN", "Switzerland": "SUI", "Iran": "IRN",
    "Turkey": "TUR", "Türkiye": "TUR", "Ecuador": "ECU", "Austria": "AUT", "South Korea": "KOR",
    "Australia": "AUS", "Algeria": "ALG", "Egypt": "EGY", "Canada": "CAN", "Norway": "NOR",
    "Ivory Coast": "CIV", "Côte d'Ivoire": "CIV", "Panama": "PAN", "Sweden": "SWE", "Czech Republic": "CZE",
    "Paraguay": "PAR", "Scotland": "SCO", "Tunisia": "TUN", "DR Congo": "COD", "Zaïre": "COD", "Zaire": "COD",
    "Uzbekistan": "UZB", "Qatar": "QAT", "Iraq": "IRQ", "South Africa": "RSA", "Saudi Arabia": "KSA",
    "Jordan": "JOR", "Bosnia and Herzegovina": "BIH", "Cape Verde": "CPV", "Ghana": "GHA", "Haiti": "HAI",
    "Curaçao": "CUW", "Netherlands Antilles": "CUW", "New Zealand": "NZL",
}
INTL_MERGED = {"GER": "West Germany", "COD": "Zaïre", "CUW": "Netherlands Antilles"}


def build_from_intl(data, path):
    """Rebuild h2h + formYears + recent form for all 48 teams from the international
    results CSV. Cut off the day BEFORE the World Cup starts, so the head-to-head and
    recent-form the models use never include the very WC2026 games they predict.
    Penalty shootouts count as the 90/120-min draw."""
    import datetime
    from collections import defaultdict
    cutoff = "2026-06-10"   # WC2026 kicked off 2026-06-11 — exclude the tournament itself
    h2h, hist, n = {}, defaultdict(list), 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            d = row.get("date", "")
            if not d or d > cutoff:
                continue
            try:
                hs, as_ = int(row["home_score"]), int(row["away_score"])
            except (ValueError, TypeError, KeyError):
                continue
            ht = WC_INTL_NAMES.get(row["home_team"]); at = WC_INTL_NAMES.get(row["away_team"])
            for code, gf, ga in ((ht, hs, as_), (at, as_, hs)):
                if code:
                    hist[code].append((d, "W" if gf > ga else "L" if gf < ga else "D"))
            if not (ht and at and ht != at):
                continue
            y = int(d[:4])
            for a, b, gf, ga in ((ht, at, hs, as_), (at, ht, as_, hs)):
                rec = h2h.setdefault(a, {}).setdefault(b, {"p": 0, "w": 0, "d": 0, "l": 0, "meetings": []})
                rec["p"] += 1
                rec["w"] += int(gf > ga); rec["d"] += int(gf == ga); rec["l"] += int(gf < ga)
                rec["meetings"].append({"d": d, "y": y, "r": "W" if gf > ga else "L" if gf < ga else "D", "s": f"{gf}-{ga}"})
            n += 1
    for a in h2h:
        for rec in h2h[a].values():
            rec["meetings"].sort(key=lambda m: m["d"], reverse=True)   # newest first
            for m in rec["meetings"]:
                del m["d"]
    cutd = datetime.date.fromisoformat(cutoff)
    fy = {}
    for code, h in hist.items():
        h.sort()
        def tally(years, h=h):
            since = cutd.replace(year=cutd.year - years).isoformat()
            c = {"w": 0, "d": 0, "l": 0}
            for dt, res in h:
                if dt > since:
                    c["w" if res == "W" else "d" if res == "D" else "l"] += 1
            return c
        fy[code] = {"y1": tally(1), "y3": tally(3), "y5": tally(5)}
        recent = "".join(res for _, res in h[-12:][::-1])   # last 12, newest first
        if recent and code in data.get("ratings", {}):
            data["ratings"][code]["form"] = recent
    data["h2h"], data["formYears"] = h2h, fy
    print(f"  built h2h from {n} matches between WC teams (<= {cutoff}); {len(h2h)} teams, "
          f"merged {', '.join(f'{k}<-{v}' for k, v in INTL_MERGED.items())}")


# football-data.org stage codes for the knockout bracket -> our short round names.
KO_STAGES = {"LAST_32": "R32", "LAST_16": "R16", "QUARTER_FINALS": "QF",
             "SEMI_FINALS": "SF", "THIRD_PLACE": "3rd", "FINAL": "Final"}


def collect_ko(payload, idx, statuses=("FINISHED",)):
    """Knockout matches from a football-data payload whose teams map to our codes.

    Returns [{stage, home, away, h, a, w, p?, status}] — raw bracket results. The app
    maps each onto its own slot by team-pair (so this never needs the bracket logic).
    `w` is the winner code from the feed (covers penalty shootouts); `p` = [hp, ap] if a
    shootout happened. Only the listed statuses are returned (FINISHED, or live states)."""
    out = []
    for m in payload.get("matches", []):
        stage = KO_STAGES.get(m.get("stage"))
        if not stage or m.get("status") not in statuses:
            continue
        h = idx.get((m.get("homeTeam", {}).get("name") or "").lower())
        a = idx.get((m.get("awayTeam", {}).get("name") or "").lower())
        if not (h and a):
            continue                                  # teams not decided / unmapped yet
        sc = m.get("score", {}) or {}
        ft = sc.get("fullTime", {}) or {}
        hg, ag = ft.get("home"), ft.get("away")
        if hg is None or ag is None:
            continue
        wf = sc.get("winner")
        w = h if wf == "HOME_TEAM" else a if wf == "AWAY_TEAM" else None
        e = {"stage": stage, "home": h, "away": a, "h": int(hg), "a": int(ag),
             "w": w, "status": m.get("status")}
        pens = sc.get("penalties", {}) or {}
        if pens.get("home") is not None and pens.get("away") is not None:
            e["p"] = [int(pens["home"]), int(pens["away"])]
        out.append(e)
    return out


def collect_ko_times(payload, idx):
    """Kickoff times for knockout matches whose teams map to our codes (any status).

    Returns [{home, away, t}] with t = ISO utcDate. The app maps each onto its bracket
    slot by team-pair, so the "Today" strip can order a day's games by real kickoff time
    instead of bracket-position match numbers."""
    out = []
    for m in payload.get("matches", []):
        if m.get("stage") not in KO_STAGES:
            continue
        h = idx.get((m.get("homeTeam", {}).get("name") or "").lower())
        a = idx.get((m.get("awayTeam", {}).get("name") or "").lower())
        t = m.get("utcDate")
        if h and a and t:
            out.append({"home": h, "away": a, "t": t})
    return out


def fetch_footballdata(data, token):
    """Pull finished WC matches from football-data.org (free tier needs a token)."""
    idx = name_to_code(data)
    by_pair = {}
    for f in data["fixtures"]:
        by_pair[(f["home"], f["away"])] = f["no"]
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    req = urllib.request.Request(url, headers={"X-Auth-Token": token})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ! football-data HTTP {e.code} (check token / competition access)", file=sys.stderr)
        return
    n = 0
    for m in payload.get("matches", []):
        if m.get("status") != "FINISHED":
            continue
        h = idx.get((m["homeTeam"].get("name") or "").lower())
        a = idx.get((m["awayTeam"].get("name") or "").lower())
        ft = m.get("score", {}).get("fullTime", {})
        if not (h and a and ft.get("home") is not None):
            continue
        no = by_pair.get((h, a))
        if no:
            data["locked"][str(no)] = [int(ft["home"]), int(ft["away"])]; n += 1
    ko = collect_ko(payload, idx)
    data["ko"] = ko
    data["koTimes"] = collect_ko_times(payload, idx)
    print(f"  fetched {n} finished group/league matches + {len(ko)} knockout result(s) from football-data.org")


# ----------------------------------------------------------------------------- embed sync
def sync_embed(data):
    """Rewrite the inline LOCKED / RATINGS fallback blocks inside index.html."""
    html = INDEX.read_text(encoding="utf-8")
    locked = "{" + ",".join(f"{k}:[{v[0]},{v[1]}]" for k, v in
                            sorted(data["locked"].items(), key=lambda kv: int(kv[0]))) + "}"
    def arr(c):
        r = data["ratings"][c]
        return f'{c}:[{r["fifa"]},{r["elo"]},{r["odds"]},{r["opta"]},"{r["form"]}"]'
    ratings = "{" + ",".join(arr(c) for c in data["teams"]) + "}"

    new = re.sub(r"(let|const)\s+LOCKED\s*=\s*\{.*?\};", f"let LOCKED={locked};", html, count=1, flags=re.S)
    new = re.sub(r"(let|const)\s+RATINGS\s*=\s*\{.*?\};", f"let RATINGS={ratings};", new, count=1, flags=re.S)
    # the inline EMBED block (head-to-head / squad / form-years / fifaPos / sources) so the app is self-contained.
    # h2h meetings are capped to the most recent EMBED_CAP per pair to keep index.html small; full history
    # (every dated meeting) stays in data.json, which the hosted app fetches.
    EMBED_CAP = 12
    h2h_emb = {}
    for a, opps in data.get("h2h", {}).items():
        h2h_emb[a] = {}
        for b, rec in opps.items():
            m = rec.get("meetings", [])
            h2h_emb[a][b] = ({**rec, "meetings": m[:EMBED_CAP]} if len(m) > EMBED_CAP else rec)
    embed = {"formYears": data.get("formYears", {}), "h2h": h2h_emb, "squad": data.get("squad", {}),
             "fifaPos": data.get("fifaPos", {}), "sources": data.get("sources", []), "ko": data.get("ko", []),
             "thirdAlloc": data.get("thirdAlloc", {}), "koTimes": data.get("koTimes", [])}
    new = re.sub(r"const\s+EMBED\s*=\s*\{[\s\S]*?\};\s*\napplyData\(EMBED\)",
                 "const EMBED=" + json.dumps(embed, ensure_ascii=False, separators=(",", ":")) + ";\napplyData(EMBED)",
                 new, count=1)
    if new == html:
        print("  ! no LOCKED/RATINGS blocks found to sync (is index.html refactored?)", file=sys.stderr)
    else:
        INDEX.write_text(new, encoding="utf-8")
        print("  synced inline fallback in index.html")


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Update sadh.app/wc2026 data.json")
    ap.add_argument("--results", metavar="CSV", help="set played scores from matchNo,hg,ag CSV")
    ap.add_argument("--ratings", metavar="CSV", help="merge ratings from code,fifa,elo,odds,opta,form CSV")
    ap.add_argument("--intl", metavar="CSV", help="rebuild h2h/formYears/form from the martj42 international results.csv")
    ap.add_argument("--fetch-footballdata", action="store_true", help="pull finished results from football-data.org")
    ap.add_argument("--token", help="football-data.org API token")
    ap.add_argument("--set-asof", metavar="YYYY-MM-DD", help="set meta.asOf")
    ap.add_argument("--sync-embed", action="store_true", help="rewrite inline fallback in index.html")
    ap.add_argument("--check", action="store_true", help="validate only; do not write")
    args = ap.parse_args()

    data = load()
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)   # snapshot to detect real changes

    if args.results:
        merge_results_csv(data, args.results)
    if args.ratings:
        merge_ratings_csv(data, args.ratings)
    if args.intl:
        build_from_intl(data, args.intl)
    if args.fetch_footballdata:
        if not args.token:
            sys.exit("--fetch-footballdata needs --token")
        fetch_footballdata(data, args.token)

    errs = validate(data)
    if errs:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(1)
    print(f"OK — {len(data['teams'])} teams, {len(data['fixtures'])} fixtures, "
          f"{len(data['locked'])} played, {len(data.get('ko', []))} knockout, {len(data['ratings'])} ratings")

    if args.check:
        return

    # only treat it as an update if a merge actually changed the data — a no-op fetch (e.g. no new
    # results) must NOT bump the version or rewrite data.json, so the workflow commits nothing.
    mutated = json.dumps(data, ensure_ascii=False, sort_keys=True) != before
    if args.set_asof:
        data["meta"]["asOf"] = args.set_asof
    if mutated and (args.results or args.ratings or args.fetch_footballdata or args.intl):
        data["meta"]["version"] = int(data["meta"].get("version", 0)) + 1
        data["meta"]["asOf"] = args.set_asof or datetime.date.today().isoformat()

    if mutated or args.set_asof:
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT.parent)}  (version {data['meta']['version']}, asOf {data['meta']['asOf']})")
    else:
        print("  no data changes — data.json left untouched")

    if args.sync_embed:
        sync_embed(data)


if __name__ == "__main__":
    main()
