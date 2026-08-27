#!/usr/bin/env python3
"""Pull final scores and newly dated fixtures from ESPN's public scoreboards.

Runs in the daily brief workflow (GitHub runners — the cloud-agent proxy 403s
these hosts, same reason fetch.py lives here) and does three additive jobs:

  1. scores.json     — finals from the last 7 days, for the brief's Results section
  2. cal.html DATA   — stamp results (r:"2-1") onto matching rows; correct the
                       date/kickoff to what actually happened (TV picks move games)
  3. cal.html DATA   — upsert dated UCL fixtures for tracked (UCL_SET) clubs as
                       UEFA publishes them; matchday-window placeholder rows are
                       dropped once two or more real fixtures land in their range

A scores outage must never block the brief: every failure path prints a
::warning and exits 0, leaving cal.html and scores.json exactly as they were.

    python3 scores.py                  live fetch (needs egress)
    python3 scores.py --from-dir DIR   offline: read DIR/<league>-<YYYYMMDD>.json
    python3 scores.py --cal PATH       operate on a different cal.html (testing)
"""
import json, re, sys, time, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CAL = HERE.parent / "cal.html"
OUT = HERE / "scores.json"
PT = ZoneInfo("America/Los_Angeles")
UA = "Mozilla/5.0 (compatible; matchday-brief/1.0; +https://sadh.app/matchday)"

RESULT_DAYS = 7          # how far back to look for finals
ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard?dates={d}"
LEAGUES = [("EPL", "eng.1"), ("La Liga", "esp.1"), ("Bundesliga", "ger.1"),
           ("Ligue 1", "fra.1"), ("UCL", "uefa.champions")]

# ESPN display names that normalisation alone can't map onto DATA's canon names.
# Keys are norm()-ed. Extend this table when the run log warns about an unmatched
# side — never guess a mapping in code.
ALIAS = {
    "bayern munich": "Bayern", "fc bayern munich": "Bayern",
    "paris saint germain": "PSG",
    "1 fc koln": "FC Koln", "fc cologne": "FC Koln", "cologne": "FC Koln",
    "1 fc union berlin": "Union Berlin",
    "1 fsv mainz 05": "Mainz 05", "mainz": "Mainz 05",
    "tsg 1899 hoffenheim": "TSG Hoffenheim", "hoffenheim": "TSG Hoffenheim",
    "sv werder bremen": "Werder Bremen",
    "borussia monchengladbach": "Borussia Monchengladbach",
    "deportivo alaves": "Alaves",
    "real racing club": "Racing Santander", "racing santander": "Racing Santander",
    "olympique marseille": "Marseille",
    "olympique lyon": "Olympique Lyonnais", "lyon": "Olympique Lyonnais",
    "losc lille": "Lille", "rc lens": "Lens",
    "as monaco": "Monaco", "ogc nice": "Nice", "stade brestois 29": "Brest",
    "afc bournemouth": "AFC Bournemouth", "bournemouth": "AFC Bournemouth",
    "brighton and hove albion": "Brighton & Hove Albion", "brighton": "Brighton & Hove Albion",
}


def warn(msg):
    print(f"::warning::scores.py: {msg}", file=sys.stderr)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def deaccent(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()


def read_cal(path):
    src = path.read_text(encoding="utf-8")
    m = re.search(r"(const DATA =[ \t]*\n)(\[.*?\]);?\n", src, re.S)
    if not m:
        raise ValueError("const DATA block not found in cal.html")
    return src, m, json.loads(m.group(2))


def cal_lists(src):
    """Canonical club names per competition, read from cal.html itself."""
    out = {}
    for comp, var in [("EPL", "EPL_CLUBS"), ("La Liga", "LALIGA_CLUBS"),
                      ("Bundesliga", "BULI_CLUBS"), ("Ligue 1", "LIGUE1_CLUBS")]:
        m = re.search(rf"const {var} = (\[[^\]]*\])", src)
        out[comp] = json.loads(m.group(1)) if m else []
    m = re.search(r"const UCL_SET = new Set\((\[[^\]]*\])\)", src)
    out["UCL"] = json.loads(m.group(1)) if m else []
    m = re.search(r"const DEFAULT_CLUBS = (\[[^\]]*\])", src)
    out["_default"] = json.loads(m.group(1)) if m else []
    return out


def resolve(name, canon):
    """ESPN display name -> canonical DATA name, or None (never guess)."""
    n = norm(name)
    by_norm = {norm(c): c for c in canon}
    if n in by_norm:
        return by_norm[n]
    if n in ALIAS and ALIAS[n] in canon:
        return ALIAS[n]
    hits = [c for c in canon if norm(c) in n or n in norm(c)]
    if len(hits) == 1:
        return hits[0]
    toks = set(n.split())
    hits = [c for c in canon if toks & set(norm(c).split())]
    return hits[0] if len(hits) == 1 else None


def fetch_board(lg, ymd, from_dir):
    if from_dir:
        p = Path(from_dir) / f"{lg}-{ymd}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"events": []}
    req = urllib.request.Request(ESPN.format(lg=lg, d=ymd), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_events(board, comp):
    """One scoreboard -> [{utc, home, away, hs, as_, final, time_valid}]"""
    out = []
    for ev in board.get("events", []):
        try:
            co = ev["competitions"][0]
            sides = {c["homeAway"]: c for c in co["competitors"]}
            st = (co.get("status") or ev.get("status") or {}).get("type", {})
            out.append({
                "comp": comp,
                "utc": ev["date"],
                "home": sides["home"]["team"]["displayName"],
                "away": sides["away"]["team"]["displayName"],
                "hs": sides["home"].get("score"),
                "as": sides["away"].get("score"),
                "final": bool(st.get("completed")) and st.get("state") == "post",
                "time_valid": co.get("timeValid", True),
            })
        except (KeyError, IndexError) as e:
            warn(f"{comp}: unparseable event ({e})")
    return out


def pt_fields(utc_iso):
    d = datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(PT)
    return d.date().isoformat(), d.strftime("%-I:%M %p"), d.isoformat(timespec="seconds")


def main():
    args = sys.argv[1:]
    from_dir = args[args.index("--from-dir") + 1] if "--from-dir" in args else None
    cal_path = Path(args[args.index("--cal") + 1]) if "--cal" in args else CAL

    try:
        src, span, data = read_cal(cal_path)
        canon = cal_lists(src)
    except Exception as e:
        warn(f"cannot read cal.html DATA ({e}) — nothing updated")
        return 0

    today = datetime.now(PT).date()
    result_days = [today - timedelta(days=i) for i in range(RESULT_DAYS + 1)]
    # future UCL dates come from cal.html's own window rows, so the fetch set
    # follows the season (knockout windows included) without hardcoding dates
    ucl_days = set()
    for m in data:
        if m["c"] == "UCL" and not m["a"]:
            if m.get("dr"):
                a = datetime.fromisoformat(m["dr"][0]).date()
                b = datetime.fromisoformat(m["dr"][1]).date()
                while a <= b:
                    ucl_days.add(a); a += timedelta(days=1)
            elif m.get("d"):
                ucl_days.add(datetime.fromisoformat(m["d"]).date())
    ucl_days = sorted(d for d in ucl_days if d >= today)

    events, errors = [], 0
    for comp, lg in LEAGUES:
        days = result_days + (ucl_days if comp == "UCL" else [])
        for day in days:
            try:
                events += parse_events(fetch_board(lg, day.strftime("%Y%m%d"), from_dir), comp)
            except Exception as e:
                errors += 1
                warn(f"{comp} {day}: fetch failed ({type(e).__name__}: {e})")
            if not from_dir:
                time.sleep(0.15)
    # scoreboards for adjacent dates repeat events — collapse on identity
    seen, uniq = set(), []
    for ev in events:
        k = (ev["comp"], ev["utc"][:10], norm(ev["home"]), norm(ev["away"]))
        if k not in seen:
            seen.add(k); uniq.append(ev)
    events = uniq
    if not events and errors:
        warn("no events fetched at all — leaving scores.json and cal.html untouched")
        return 0

    by_pair = {}
    for i, m in enumerate(data):
        if m.get("a"):
            by_pair.setdefault((m["c"], m["h"], m["a"]), []).append(i)

    results_out, stamped, inserted, unmatched = [], 0, 0, []
    week_floor = (today - timedelta(days=RESULT_DAYS)).isoformat()
    for ev in events:
        pool = canon["UCL"] if ev["comp"] == "UCL" else canon[ev["comp"]]
        h, a = resolve(ev["home"], pool), resolve(ev["away"], pool)
        d, t, dt = pt_fields(ev["utc"])

        if ev["final"] and ev["hs"] is not None and d >= week_floor:
            results_out.append({"d": d, "comp": ev["comp"],
                                "h": h or deaccent(ev["home"]), "a": a or deaccent(ev["away"]),
                                "hs": str(ev["hs"]), "as": str(ev["as"])})

        if ev["comp"] == "UCL":
            # upsert dated fixtures for tracked clubs (either side in UCL_SET)
            th, ta = h, a
            if not (th or ta):
                continue
            H = th or deaccent(ev["home"])
            A = ta or deaccent(ev["away"])
            rows = by_pair.get(("UCL", H, A), [])
            row = next((data[i] for i in rows
                        if abs((datetime.fromisoformat(data[i]["d"]).date()
                                - datetime.fromisoformat(d).date()).days) <= 3), None)
            if row is None:
                row = {"d": d, "c": "UCL", "h": H, "a": A, "t": t, "dt": dt,
                       "cf": bool(ev["time_valid"]),
                       "tr": H in canon["_default"] or A in canon["_default"], "bg": False}
                data.append(row)
                by_pair.setdefault(("UCL", H, A), []).append(len(data) - 1)
                inserted += 1
            row["d"] = d
            if ev["time_valid"]:
                row["t"], row["dt"], row["cf"] = t, dt, True
            if ev["final"] and ev["hs"] is not None:
                row["r"], row["cf"] = f'{ev["hs"]}-{ev["as"]}', True
                stamped += 1
            continue

        if not (h and a):
            if ev["final"]:
                unmatched.append(f'{ev["comp"]}: {ev["home"]} vs {ev["away"]}')
            continue
        if ev["final"] and ev["hs"] is not None:
            rows = by_pair.get((ev["comp"], h, a), [])
            row = next((data[i] for i in rows
                        if abs((datetime.fromisoformat(data[i]["d"]).date()
                                - datetime.fromisoformat(d).date()).days) <= 1), None)
            if row is not None:
                row.update({"d": d, "t": t, "dt": dt, "cf": True,
                            "r": f'{ev["hs"]}-{ev["as"]}'})
                stamped += 1

    for name in sorted(set(unmatched)):
        warn(f"final score for unmatched club names, skipped: {name}")

    # drop a UCL window placeholder once >=2 real fixtures land inside its range
    real_ucl = [m["d"] for m in data if m["c"] == "UCL" and m["a"]]
    def window_filled(w):
        if w.get("dr"):
            lo, hi = w["dr"]
        else:
            lo = hi = w["d"]
        return sum(1 for d in real_ucl if lo <= d <= hi) >= (2 if w.get("dr") else 1)
    dropped = [m for m in data if m["c"] == "UCL" and not m["a"] and window_filled(m)]
    data = [m for m in data if m not in dropped]

    data.sort(key=lambda m: (m["d"], m.get("dt") or "", m["h"]))
    new_line = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    new_src = src[:span.start(2)] + new_line + src[span.end(2):]
    try:  # round-trip guard: never write a cal.html the page can't parse
        _, _, check = read_cal_from_text(new_src)
        assert len(check) == len(data)
    except Exception as e:
        warn(f"round-trip check failed ({e}) — cal.html NOT written")
        return 0
    if new_src != src:
        cal_path.write_text(new_src, encoding="utf-8")

    results_out.sort(key=lambda r: r["d"], reverse=True)
    OUT.write_text(json.dumps({
        "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": RESULT_DAYS,
        "results": results_out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"scores: {len(results_out)} finals (7d) -> {OUT.name}; cal.html: "
          f"{stamped} results stamped, {inserted} UCL fixtures added, "
          f"{len(dropped)} window rows retired, {errors} fetch errors", file=sys.stderr)
    return 0


def read_cal_from_text(src):
    m = re.search(r"(const DATA =[ \t]*\n)(\[.*?\]);?\n", src, re.S)
    return src, m, json.loads(m.group(2))


if __name__ == "__main__":
    sys.exit(main())
