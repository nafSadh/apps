#!/usr/bin/env python3
"""Refresh election2026/data.json (and data.js) from NBC News / AP state results pages.

One request per state (50 total, ~1s apart). Each NBC state page embeds its results as
JSON (__NEXT_DATA__): Senate and governor races, every House district, and ballot
measures, each with AP vote shares and NBC Decision Desk call status.

Safety rules:
  * If more than MAX_FAILED states fail to load or parse, nothing is written (exit 1).
    A stale page beats a half-updated one.
  * A state that fails keeps its previous numbers.
  * Hand-written notes, 2024 baselines, map layout and history data are never touched.
  * Files are rewritten only when results change, so the workflow commits nothing
    on quiet runs.
  * After STOP_AFTER the script exits 0 without fetching, so the schedule goes quiet
    once counting is over.

Usage:  python3 update.py [--dry-run]
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "data.json"
DATA_JS = ROOT / "data.js"
BASE = "https://www.nbcnews.com/politics/2026-elections/{}-results"
UA = "Mozilla/5.0 (compatible; sadh.app-election2026-updater; +https://sadh.app/election2026/)"
STOP_AFTER = dt.date(2026, 12, 15)
MAX_FAILED = 3
PAUSE = 1.0

STATES = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas", "CA": "california",
    "CO": "colorado", "CT": "connecticut", "DE": "delaware", "FL": "florida", "GA": "georgia",
    "HI": "hawaii", "ID": "idaho", "IL": "illinois", "IN": "indiana", "IA": "iowa",
    "KS": "kansas", "KY": "kentucky", "LA": "louisiana", "ME": "maine", "MD": "maryland",
    "MA": "massachusetts", "MI": "michigan", "MN": "minnesota", "MS": "mississippi",
    "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada", "NH": "new-hampshire",
    "NJ": "new-jersey", "NM": "new-mexico", "NY": "new-york", "NC": "north-carolina",
    "ND": "north-dakota", "OH": "ohio", "OK": "oklahoma", "OR": "oregon", "PA": "pennsylvania",
    "RI": "rhode-island", "SC": "south-carolina", "SD": "south-dakota", "TN": "tennessee",
    "TX": "texas", "UT": "utah", "VT": "vermont", "VA": "virginia", "WA": "washington",
    "WV": "west-virginia", "WI": "wisconsin", "WY": "wyoming",
}
PARTY = {"dem": "D", "gop": "R"}


def party(code):
    return PARTY.get(code, "I")


def fetch_state(slug):
    req = urllib.request.Request(BASE.format(slug), headers={"User-Agent": UA, "Accept": "text/html"})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", "replace")
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
            if not m:
                raise ValueError("no __NEXT_DATA__ on page")
            pp = json.loads(m.group(1))["props"]["pageProps"]
            if "stateRaceResults" not in pp:
                raise ValueError("no stateRaceResults")
            return pp
        except Exception as e:  # network errors, 403s, layout changes
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"{slug}: {last}")


def cands(race):
    out = []
    for c in race.get("candidates") or []:
        if c.get("percentVote") is None:
            continue
        out.append(c)
    return sorted(out, key=lambda c: (-(c.get("percentVote") or 0), -(c.get("votes") or 0)))


def recalc(r):
    """Margin = Democrat (or leading non-Republican) minus Republican; swing vs 2024."""
    w, rp = r.get("wpct"), r.get("rpct")
    if w is None or rp is None or (r.get("wp") != "R" and r.get("rp") != "R"):
        r["margin"], r["swing"] = None, None
        return
    m = w - rp if r["wp"] != "R" else -(w - rp)
    r["margin"] = round(m, 1)
    r["swing"] = None if r.get("pres24") is None else round(m - r["pres24"], 1)


def update_statewide(r, race, label_incumbents):
    cs = cands(race)
    if len(cs) < 1:
        return False
    win = next((c for c in cs if c.get("isWinner")), None)
    top = win or cs[0]
    second = next((c for c in cs if c is not top), None)

    def nm(c):
        return c["name"] + (" (inc.)" if label_incumbents and c.get("isIncumbent") else "")

    called = bool(win)
    new = {
        "called": called,
        "win": nm(top), "wp": party(top.get("party")), "wpct": round(top["percentVote"], 1),
        "flip": bool(called and race.get("partyGain")),
        "pct_in": race.get("percentIn"),
    }
    # NBC's state pages list only the top Democrat and top Republican. When the listed
    # candidates cover under 90% of the vote, a strong independent or a second same-party
    # candidate is missing, so the runner-up shown would be wrong: keep the previous one.
    listed = sum(c["percentVote"] for c in cs)
    if second and listed >= 90:
        new.update({"ru": nm(second), "rp": party(second.get("party")), "rpct": round(second["percentVote"], 1)})
    changed = any(r.get(k) != v for k, v in new.items())
    r.update(new)
    recalc(r)
    return changed


def measure_key(s):
    s = s.lower().split(":")[0]
    s = s.replace("prop.", "proposition").replace("amend.", "amendment")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main():
    dry = "--dry-run" in sys.argv
    if dt.datetime.now(dt.timezone.utc).date() > STOP_AFTER:
        print(f"Past {STOP_AFTER}; results are final. Nothing to do.")
        return 0

    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    before = json.dumps({k: v for k, v in data.items() if k != "meta"}, sort_keys=True)

    pages, failed = {}, []
    for i, (st, slug) in enumerate(STATES.items()):
        if i:
            time.sleep(PAUSE)
        try:
            pages[st] = fetch_state(slug)
        except Exception as e:
            failed.append(st)
            print(f"::warning::{e}")
    if len(failed) > MAX_FAILED:
        print(f"::error::{len(failed)} states failed ({', '.join(failed)}); not writing anything.")
        return 1

    sen = {r["st"]: r for r in data["senate"]["races"]}
    gov = {r["st"]: r for r in data["governors"]["races"]}
    dist = {d["id"]: d for d in data["house"]["districts"]}
    meas = data.get("measures", [])
    newest = None
    n_races = n_dist = n_meas = 0

    for st, pp in pages.items():
        lm = pp.get("lastModified")
        if lm:
            try:
                t = parsedate_to_datetime(lm)
                newest = t if newest is None or t > newest else newest
            except Exception:
                pass
        srr = pp["stateRaceResults"]
        for race in srr.get("discreteOffices") or []:
            office = race.get("office")
            if office == "senate" and st in sen:
                n_races += update_statewide(sen[st], race, label_incumbents=False)
            elif office == "governor" and st in gov:
                n_races += update_statewide(gov[st], race, label_incumbents=True)
        for race in srr.get("house") or []:
            n = race.get("district") or 1
            key = f"{st}-{n}"
            d = dist.get(key)
            cs = cands(race)
            if not d or not cs:
                continue
            new_c = [[party(c.get("party")), c.get("lastName") or c["name"], int(c.get("votes") or 0),
                      round(c["percentVote"], 1), 1 if c.get("isIncumbent") else 0, 1 if c.get("isWinner") else 0]
                     for c in cs[:3]]
            new = {"pin": race.get("percentIn") or 0, "flip": bool(race.get("isGain")),
                   "tv": int(race.get("votes") or 0), "c": new_c}
            if any(d.get(k) != v for k, v in new.items()):
                n_dist += 1
                d.update(new)
        for race in srr.get("ballotProps") or []:
            k = measure_key(race.get("raceName") or "")
            m = next((x for x in meas if x["st"] == st and measure_key(x["m"]) == k), None)
            if not m:
                continue
            yes = next((c for c in race.get("candidates") or [] if (c.get("name") or "").lower() == "yes"), None)
            no = next((c for c in race.get("candidates") or [] if (c.get("name") or "").lower() == "no"), None)
            if not yes or yes.get("percentVote") is None:
                continue
            res = "passed" if yes.get("isWinner") else "failed" if (no and no.get("isWinner")) else "uncalled"
            if m.get("yes") != round(yes["percentVote"], 1) or m.get("res") != res:
                n_meas += 1
                m["yes"], m["res"] = round(yes["percentVote"], 1), res

    # House aggregates
    D = R = Dl = Rl = 0
    Dv = Rv = 0
    for d in data["house"]["districts"]:
        w = next((c for c in d["c"] if c[5] == 1), None)
        lead = w or (d["c"][0] if d["c"] else None)
        if w:
            D += w[0] == "D"
            R += w[0] == "R"
        elif lead:
            Dl += lead[0] == "D"
            Rl += lead[0] == "R"
        for c in d["c"]:
            Dv += c[2] if c[0] == "D" else 0
            Rv += c[2] if c[0] == "R" else 0
    h = data["house"]
    h["called"] = {"D": D, "R": R, "uncalled": 435 - D - R}
    nv = h.setdefault("national_vote", {})
    nv.update({"D_votes": Dv, "R_votes": Rv, "D_pct": round(100 * Dv / (Dv + Rv), 2),
               "R_pct": round(100 * Rv / (Dv + Rv), 2), "margin": round(100 * (Dv - Rv) / (Dv + Rv), 2),
               "d_leading": Dl, "r_leading": Rl,
               "flips_projected": sum(1 for d in h["districts"] if d["flip"] and any(c[5] for c in d["c"]))})
    # House flips list: keep curated entries, refresh call status, add new gains, drop seats D no longer leads
    flips = []
    seen = set()
    for f in h.get("flips", []):
        d = dist.get(f["d"])
        if not d or not d["c"] or d["c"][0][0] != "D":
            continue
        f["called"] = any(c[5] for c in d["c"])
        flips.append(f)
        seen.add(f["d"])
    for d in h["districts"]:
        if d["flip"] and d["id"] not in seen and d["c"] and d["c"][0][0] == "D":
            loser = next((c[1] for c in d["c"] if c[0] != "D"), "")
            flips.append({"d": d["id"], "st": d["st"], "winner": d["c"][0][1], "loser": loser,
                          "type": "", "called": any(c[5] for c in d["c"])})
    h["flips"] = flips

    # Senate / governor aggregates
    s = data["senate"]
    sc = [r for r in s["races"] if r.get("called")]
    s["after"] = {"D": s["not_up"]["D"] + sum(r["wp"] != "R" for r in sc),
                  "R": s["not_up"]["R"] + sum(r["wp"] == "R" for r in sc),
                  "uncalled": sum(not r.get("called") for r in s["races"])}
    g = data["governors"]
    gc = [r for r in g["races"] if r.get("called")]
    g["after_called"] = {"D": g["not_up"]["D"] + sum(r["wp"] != "R" for r in gc),
                         "R": g["not_up"]["R"] + sum(r["wp"] == "R" for r in gc),
                         "uncalled": sum(not r.get("called") for r in g["races"])}
    g["net_called"] = sum(1 for r in gc if r.get("flip") and r["wp"] == "D") - sum(1 for r in gc if r.get("flip") and r["wp"] == "R")

    # Sanity checks before writing
    assert len(h["districts"]) == 435, "district count changed"
    assert h["called"]["D"] + h["called"]["R"] <= 435
    assert len(s["races"]) == 35 and len(g["races"]) == 36

    after = json.dumps({k: v for k, v in data.items() if k != "meta"}, sort_keys=True)
    print(f"states ok {len(pages)}/50; changed: {n_races} statewide races, {n_dist} districts, {n_meas} measures")
    if after == before:
        print("No result changes; leaving files untouched.")
        return 0

    if newest:
        et = newest.astimezone(ZoneInfo("America/New_York"))
        pt = newest.astimezone(ZoneInfo("America/Los_Angeles"))

        def clock(t):
            return t.strftime("%-I:%M ") + ("a.m." if t.hour < 12 else "p.m.")

        data["meta"]["as_of"] = pt.isoformat(timespec="seconds")
        data["meta"]["as_of_label"] = f"{et.strftime('%b.').replace('May.', 'May')} {et.day}, {et.year} · {clock(et)} ET ({clock(pt)} PT)"

    if dry:
        print("--dry-run: not writing.", data["meta"].get("as_of_label"))
        return 0
    txt = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    DATA_JSON.write_text(txt, encoding="utf-8")
    DATA_JS.write_text("window.ELECTION_DATA = " + txt + ";\n", encoding="utf-8")
    print("Wrote data.json and data.js:", data["meta"].get("as_of_label"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
