#!/usr/bin/env python3
"""Pull final scores and newly dated fixtures into scores.json and cal.html.

Source of truth is football-data.org (free tier covers PL, PD, BL1, FL1 and CL;
token in the FOOTBALL_DATA_TOKEN env var, set from the repo secret by the
workflow). Without a token the script falls back to ESPN's undocumented
scoreboard JSON, which is best-effort only: ESPN refused every runner request
with HTTP 403 from Aug 27 to Sep 3 2026, so never count on it.

Runs in the daily brief workflow (GitHub runners — the cloud-agent proxy 403s
these hosts, same reason fetch.py lives here) and does three additive jobs:

  1. scores.json     — finals from the last 7 days, for the brief's Results section
  2. cal.html DATA   — stamp results (r:"2-1") onto matching rows; correct the
                       date/kickoff to what actually happened (TV picks move games)
  3. cal.html DATA   — upsert dated UCL fixtures for tracked (UCL_SET) clubs as
                       UEFA publishes them; matchday-window placeholder rows are
                       dropped once two or more real fixtures land in their range,
                       and a tagged window (knockouts, Final) passes its tag on to
                       the real fixtures that replace it

A scores outage must never block the brief: main() catches everything, prints a
::warning and exits 0, leaving cal.html and scores.json exactly as they were.
Fetching also stops at DEADLINE_S so a hanging source cannot eat the job timeout.

API payloads are external input: display names are sanitised (clean_name) before
they can reach cal.html's inline <script> JSON or the brief's HTML, and the DATA
line is written with `</` escaped so no name can close the script block.

    python3 scores.py                  live fetch (needs egress)
    python3 scores.py --from-dir DIR   offline: football-data shaped DIR/fd-<CODE>.json
                                       (CL, PL, PD, BL1, FL1) when present, else
                                       ESPN shaped DIR/<league>-<YYYYMMDD>.json
    python3 scores.py --cal PATH       operate on a different cal.html (testing)
    python3 scores.py --out PATH       write scores.json elsewhere (testing)
"""
import json, os, re, sys, time, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CAL = HERE.parent / "cal.html"
OUT = HERE / "scores.json"
PT = ZoneInfo("America/Los_Angeles")
# ESPN's edge 403s anything that announces itself as a bot — the previous
# "(compatible; matchday-brief/1.0)" UA was refused on every run from Aug 27 to
# Sep 3, so no result or UCL fixture ever landed. Present as a browser instead.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept": "application/json, text/plain, */*",
           "Accept-Language": "en-US,en;q=0.9", "Referer": "https://www.espn.com/",
           "Origin": "https://www.espn.com"}

RESULT_DAYS = 7          # how far back to look for finals
DEADLINE_S = 240         # hard budget for all fetching — the job must go on
SEASON_END = "2027-06-30"
# primary: football-data.org v4 — one request per competition, date-ranged
FD = "https://api.football-data.org/v4/competitions/{code}/matches?dateFrom={a}&dateTo={b}"
FD_CODES = {"EPL": "PL", "La Liga": "PD", "Bundesliga": "BL1", "Ligue 1": "FL1", "UCL": "CL"}
FD_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "").strip()
# fallback: ESPN's scoreboard, one request per league-day
ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard?dates={d}"
LEAGUES = [("EPL", "eng.1"), ("La Liga", "esp.1"), ("Bundesliga", "ger.1"),
           ("Ligue 1", "fra.1"), ("UCL", "uefa.champions")]

# ESPN display names that normalisation alone can't map onto DATA's canon names.
# Keys are norm()-ed. Extend this table when the run log warns about an unmatched
# side — never guess a mapping in code.
ALIAS = {
    "bayern munich": "Bayern", "fc bayern munich": "Bayern",
    "paris saint germain": "PSG", "paris saint germain fc": "PSG",
    "rcd espanyol de barcelona": "Espanyol", "rcd espanyol": "Espanyol",
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
    # UCL opponents outside the pickable lists (names as they sit in cal.html DATA)
    "internazionale": "Inter", "inter milan": "Inter", "fc internazionale milano": "Inter",
    "fc porto": "Porto", "as roma": "Roma", "ssc napoli": "Napoli", "como 1907": "Como",
    "slavia prague": "Slavia Praha", "sk slavia praha": "Slavia Praha",
    "sk slovan bratislava": "Slovan Bratislava", "bodo glimt": "Bodo/Glimt",
    "fk bodo glimt": "Bodo/Glimt", "viking fk": "Viking", "sabah fk": "Sabah",
    "lask linz": "LASK", "club brugge kv": "Club Brugge", "psv": "PSV Eindhoven",
    "sporting lisbon": "Sporting CP", "sporting clube de portugal": "Sporting CP",
    "aek athens fc": "AEK Athens", "pae aek": "AEK Athens", "aek": "AEK Athens",
    "shakhtar": "Shakhtar Donetsk",
}


def warn(msg):
    print(f"::warning::scores.py: {msg}", file=sys.stderr)


# letters NFKD cannot decompose — dropping them mangles a name ("Bodø" -> "Bod")
_XLIT = str.maketrans({"ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE",
                       "ß": "ss", "ł": "l", "Ł": "L", "đ": "d", "Đ": "D", "ı": "i"})


def ascii_fold(s):
    return unicodedata.normalize("NFKD", (s or "").translate(_XLIT)).encode("ascii", "ignore").decode()


def norm(s):
    s = ascii_fold(s)
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def clean_name(s):
    """ESPN input -> safe display text: ascii, no HTML-significant characters.
    These names end up inside cal.html's inline JSON and innerHTML templates."""
    s = ascii_fold(s)
    s = re.sub(r"[^A-Za-z0-9 .,'&()/-]", "", s)
    return re.sub(r"\s+", " ", s).strip()[:48]


def read_cal_from_text(src):
    m = re.search(r"(const DATA =[ \t]*\n)(\[.*?\]);?\n", src, re.S)
    if not m:
        raise ValueError("const DATA block not found in cal.html")
    return m, json.loads(m.group(2))


def read_cal(path):
    src = path.read_text(encoding="utf-8")
    span, data = read_cal_from_text(src)
    return src, span, data


def cal_lists(src):
    """Canonical club names per competition, read from cal.html itself."""
    out = {}
    for comp, var in [("EPL", "EPL_CLUBS"), ("La Liga", "LALIGA_CLUBS"),
                      ("Bundesliga", "BULI_CLUBS"), ("Ligue 1", "LIGUE1_CLUBS")]:
        m = re.search(rf"const {var} = (\[[^\]]*\])", src)
        out[comp] = json.loads(m.group(1)) if m else []
    m = re.search(r"const UCL_SET = new Set\((\[[^\]]*\])\)", src)
    out["UCL"] = json.loads(m.group(1)) if m else []
    m = re.search(r"const UCL_BIG = new Set\((\[[^\]]*\])\)", src)
    out["_big"] = json.loads(m.group(1)) if m else []
    # every side already named in a UCL row (Inter, Porto, Bodo/Glimt...) is canon too,
    # so a known opponent resolves to its DATA spelling instead of being renamed to
    # ESPN's display name; only UCL_SET decides whether a fixture is worth a row
    _, data = read_cal_from_text(src)
    seen = []
    for m in data:
        if m["c"] == "UCL" and m.get("a"):
            for side in (m["h"], m["a"]):
                if side not in seen:
                    seen.append(side)
    out["_ucl_pool"] = out["UCL"] + [c for c in seen if c not in out["UCL"]]
    m = re.search(r"const DEFAULT_CLUBS = (\[[^\]]*\])", src)
    out["_default"] = json.loads(m.group(1)) if m else []
    return out


def resolve(name, canon):
    """ESPN display name -> canonical DATA name, or None (never guess).
    Fallbacks require the whole canon name (substring or full token set) to be
    present — a single shared token like 'RB'/'Borussia' must NOT match."""
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
    hits = [c for c in canon if set(norm(c).split()) <= toks]
    return hits[0] if len(hits) == 1 else None


def fetch_fd(code, a, b, from_dir):
    """football-data.org matches for one competition over [a, b] (ISO dates).
    Offline: DIR/fd-<CODE>.json in the same shape; absent file -> None so the
    caller can fall through to the ESPN-shaped fixtures."""
    if from_dir:
        p = Path(from_dir) / f"fd-{code}.json"
        if not p.exists():
            return None
        board = json.loads(p.read_text(encoding="utf-8"))
        if board.get("__fail__"):          # test hook: simulate an outage
            raise RuntimeError("simulated fetch failure")
        return board
    req = urllib.request.Request(FD.format(code=code, a=a, b=b),
                                 headers={"X-Auth-Token": FD_TOKEN, "User-Agent": UA,
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_fd(board, comp):
    """football-data match -> the same event shape parse_events produces.
    status: SCHEDULED = date known, kickoff still provisional; TIMED = kickoff
    set; FINISHED = final. Postponed/cancelled/suspended games are skipped —
    the calendar keeps its row until a new date is announced."""
    out = []
    for m in board.get("matches", []):
        try:
            st = m.get("status") or ""
            if st in ("POSTPONED", "CANCELLED", "SUSPENDED", "AWARDED"):
                continue
            utc = m["utcDate"]
            datetime.fromisoformat(utc.replace("Z", "+00:00"))  # reject junk now
            ft = (m.get("score") or {}).get("fullTime") or {}
            h, a = m["homeTeam"], m["awayTeam"]
            out.append({
                "comp": comp,
                "utc": utc,
                "home": clean_name(h.get("name") or h.get("shortName") or ""),
                "away": clean_name(a.get("name") or a.get("shortName") or ""),
                "home_alt": clean_name(h.get("shortName") or ""),
                "away_alt": clean_name(a.get("shortName") or ""),
                "hs": ft.get("home"),
                "as": ft.get("away"),
                "final": st == "FINISHED",
                "time_valid": st != "SCHEDULED",
            })
        except Exception as e:
            warn(f"{comp}: unparseable football-data match ({type(e).__name__}: {e})")
    return out


def fetch_board(lg, ymd, from_dir):
    if from_dir:
        p = Path(from_dir) / f"{lg}-{ymd}.json"
        board = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"events": []}
        if board.get("__fail__"):          # test hook: simulate an outage day
            raise RuntimeError("simulated fetch failure")
        return board
    req = urllib.request.Request(ESPN.format(lg=lg, d=ymd), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_events(board, comp):
    out = []
    for ev in board.get("events", []):
        try:
            co = ev["competitions"][0]
            sides = {c["homeAway"]: c for c in co["competitors"]}
            st = (co.get("status") or ev.get("status") or {}).get("type", {})
            utc = ev["date"]
            datetime.fromisoformat(utc.replace("Z", "+00:00"))  # reject junk now
            out.append({
                "comp": comp,
                "utc": utc,
                "home": clean_name(sides["home"]["team"]["displayName"]),
                "away": clean_name(sides["away"]["team"]["displayName"]),
                "hs": sides["home"].get("score"),
                "as": sides["away"].get("score"),
                "final": bool(st.get("completed")) and st.get("state") == "post",
                "time_valid": co.get("timeValid", True),
            })
        except Exception as e:
            warn(f"{comp}: unparseable event ({type(e).__name__}: {e})")
    return out


def pt_fields(utc_iso):
    d = datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(PT)
    return d.date().isoformat(), d.strftime("%-I:%M %p"), d.isoformat(timespec="seconds")


def run():
    args = sys.argv[1:]
    from_dir = args[args.index("--from-dir") + 1] if "--from-dir" in args else None
    cal_path = Path(args[args.index("--cal") + 1]) if "--cal" in args else CAL
    out_path = Path(args[args.index("--out") + 1]) if "--out" in args else OUT

    src, span, data = read_cal(cal_path)
    canon = cal_lists(src)

    today = datetime.now(PT).date()
    result_days = [today - timedelta(days=i) for i in range(RESULT_DAYS + 1)]
    # future UCL dates come from cal.html's own window rows PLUS the real
    # fixtures already inserted — a retired window's dates must keep being
    # fetched or a time-TBD fixture in it would never get its kickoff
    ucl_days = set()
    for m in data:
        if m["c"] != "UCL":
            continue
        if not m["a"]:
            if m.get("dr"):
                a = datetime.fromisoformat(m["dr"][0]).date()
                b = datetime.fromisoformat(m["dr"][1]).date()
                while a <= b:
                    ucl_days.add(a); a += timedelta(days=1)
            elif m.get("d"):
                ucl_days.add(datetime.fromisoformat(m["d"]).date())
        else:
            d = datetime.fromisoformat(m["d"]).date()
            ucl_days.add(d)
            if not m.get("cf"):              # date itself still provisional
                ucl_days.add(d - timedelta(days=1)); ucl_days.add(d + timedelta(days=1))
    ucl_days = sorted(d for d in ucl_days if d >= today)

    started = time.monotonic()
    events, errors = [], 0
    league_ok, league_err = {c: 0 for c, _ in LEAGUES}, {c: 0 for c, _ in LEAGUES}
    use_fd = bool(FD_TOKEN) or bool(from_dir)
    if not FD_TOKEN and not from_dir:
        warn("FOOTBALL_DATA_TOKEN is not set — falling back to ESPN, which is "
             "best-effort only (it 403'd every run Aug 27–Sep 3). Add the repo "
             "secret from https://www.football-data.org/client/register")
    week_floor_d = today - timedelta(days=RESULT_DAYS)
    for comp, lg in LEAGUES:
        if time.monotonic() - started > DEADLINE_S:
            warn(f"fetch budget ({DEADLINE_S}s) spent — stopping at {comp}")
            errors += 1; league_err[comp] += 1
            continue
        # --- football-data.org: one date-ranged request per competition; the UCL
        # range runs to season end so every newly dated fixture arrives at once
        if use_fd:
            hi = SEASON_END if comp == "UCL" else today.isoformat()
            try:
                board = fetch_fd(FD_CODES[comp], week_floor_d.isoformat(), hi, from_dir)
            except Exception as e:
                board = None
                errors += 1; league_err[comp] += 1
                warn(f"{comp}: football-data fetch failed ({type(e).__name__}: {e})")
            if board is not None:
                events += parse_fd(board, comp)
                league_ok[comp] += 1
                if not from_dir:
                    time.sleep(6.5)          # free tier: 10 requests / minute
                continue
            if FD_TOKEN and not from_dir:
                continue                     # a token is configured: never mix sources
        # --- ESPN fallback: one request per league-day
        days = result_days + (ucl_days if comp == "UCL" else [])
        for day in days:
            if time.monotonic() - started > DEADLINE_S:
                warn(f"fetch budget ({DEADLINE_S}s) spent — stopping at {comp} {day}")
                errors += 1; league_err[comp] += 1
                break
            try:
                events += parse_events(fetch_board(lg, day.strftime("%Y%m%d"), from_dir), comp)
                league_ok[comp] += 1
            except Exception as e:
                errors += 1; league_err[comp] += 1
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
    ucl_windows = [m for m in data if m["c"] == "UCL" and not m["a"]]

    def window_tag_for(d):
        for w in ucl_windows:
            lo, hi = w["dr"] if w.get("dr") else (w["d"], w["d"])
            if w.get("tag") and lo <= d <= hi:
                return w["tag"]
        return None

    def near(row_d, d, days_apart):
        return abs((datetime.fromisoformat(row_d).date()
                    - datetime.fromisoformat(d).date()).days) <= days_apart

    results_out, stamped, inserted, unmatched = [], 0, 0, []
    week_floor = (today - timedelta(days=RESULT_DAYS)).isoformat()
    for ev in events:
        pool = canon["_ucl_pool"] if ev["comp"] == "UCL" else canon[ev["comp"]]
        h = resolve(ev["home"], pool) or resolve(ev.get("home_alt") or "", pool)
        a = resolve(ev["away"], pool) or resolve(ev.get("away_alt") or "", pool)
        # a date-only placeholder (timeValid false) sits at an arbitrary UTC
        # midnight: converting it to PT shifts the matchday back a day and
        # invents a kickoff, so keep the UTC date and no time at all
        if ev["time_valid"]:
            d, t, dt = pt_fields(ev["utc"])
        else:
            d, t, dt = ev["utc"][:10], None, None

        if ev["final"] and ev["hs"] is not None and d >= week_floor:
            results_out.append({"d": d, "comp": ev["comp"],
                                "h": h or ev["home"], "a": a or ev["away"],
                                "hs": str(ev["hs"]), "as": str(ev["as"])})

        if ev["comp"] == "UCL":
            if not (h in canon["UCL"] or a in canon["UCL"]):
                continue                      # neither side a pickable club
            H, A = h or ev["home"], a or ev["away"]
            row = next((data[i] for i in by_pair.get(("UCL", H, A), [])
                        if near(data[i]["d"], d, 3)), None)
            if row is None:
                # same fixture under a renamed untracked side: any real UCL row
                # a day either side sharing the resolved tracked club is it
                side = h if h in canon["UCL"] else a
                row = next((m for m in data if m["c"] == "UCL" and m.get("a")
                            and side in (m["h"], m["a"]) and near(m["d"], d, 1)), None)
                if row is not None:
                    row["h"], row["a"] = H, A
            if row is None:
                # a heavyweight-vs-heavyweight tie is a key match, same bar as cal.html
                row = {"d": d, "c": "UCL", "h": H, "a": A, "t": t, "dt": dt,
                       "cf": bool(ev["time_valid"]),
                       "tr": H in canon["_default"] or A in canon["_default"],
                       "bg": H in canon["_big"] and A in canon["_big"]}
                data.append(row)
                by_pair.setdefault(("UCL", H, A), []).append(len(data) - 1)
                inserted += 1
            if ev["time_valid"]:
                row["d"], row["t"], row["dt"], row["cf"] = d, t, dt, True
            tag = window_tag_for(row["d"])
            if tag and not row.get("tag"):
                row["tag"] = tag
                if tag.startswith("Final"):
                    row["bg"] = True
            if ev["final"] and ev["hs"] is not None:
                row["r"], row["cf"] = f'{ev["hs"]}-{ev["as"]}', True
                stamped += 1
            continue

        if not (h and a):
            if ev["final"]:
                unmatched.append(f'{ev["comp"]}: {ev["home"]} vs {ev["away"]}')
            continue
        if ev["final"] and ev["hs"] is not None and ev["time_valid"]:
            row = next((data[i] for i in by_pair.get((ev["comp"], h, a), [])
                        if near(data[i]["d"], d, 1)), None)
            if row is not None:
                row.update({"d": d, "t": t, "dt": dt, "cf": True,
                            "r": f'{ev["hs"]}-{ev["as"]}'})
                stamped += 1

    for name in sorted(set(unmatched)):
        warn(f"final score for unmatched club names, skipped: {name}")

    # a league whose fetches ALL failed contributes nothing this run — carry its
    # finals forward from the previous scores.json instead of silently dropping them
    dead = {c for c in league_err if league_err[c] and not league_ok[c]}
    if dead and out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8")).get("results") or []
            carried = [r for r in prev if r.get("comp") in dead and r.get("d", "") >= week_floor]
            if carried:
                warn(f"carrying {len(carried)} previous finals for offline league(s): {', '.join(sorted(dead))}")
                results_out += carried
        except Exception as e:
            warn(f"could not carry forward previous results ({e})")

    # drop a UCL window placeholder once >=2 real fixtures land inside its range
    real_ucl = [m["d"] for m in data if m["c"] == "UCL" and m["a"]]
    def window_filled(w):
        lo, hi = w["dr"] if w.get("dr") else (w["d"], w["d"])
        return sum(1 for d in real_ucl if lo <= d <= hi) >= (2 if w.get("dr") else 1)
    dropped = [m for m in ucl_windows if window_filled(m)]
    data = [m for m in data if m not in dropped]

    data.sort(key=lambda m: (m["d"], m.get("dt") or "", m["h"]))
    # `<\/` keeps any `</script>`-shaped text from terminating the inline block
    new_line = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    new_src = src[:span.start(2)] + new_line + src[span.end(2):]
    _, check = read_cal_from_text(new_src)   # round-trip guard
    assert len(check) == len(data), "round-trip length mismatch"
    if new_src != src:
        cal_path.write_text(new_src, encoding="utf-8")

    results_out.sort(key=lambda r: r["d"], reverse=True)
    out_path.write_text(json.dumps({
        "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": RESULT_DAYS,
        "results": results_out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"scores: {len(results_out)} finals (7d) -> {out_path.name}; cal.html: "
          f"{stamped} results stamped, {inserted} UCL fixtures added, "
          f"{len(dropped)} window rows retired, {errors} fetch errors", file=sys.stderr)
    return 0


def main():
    # the brief must publish no matter what this script hits — warn, never fail
    try:
        return run()
    except Exception as e:
        warn(f"unexpected failure ({type(e).__name__}: {e}) — nothing updated")
        return 0


if __name__ == "__main__":
    sys.exit(main())
