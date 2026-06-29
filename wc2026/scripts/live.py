#!/usr/bin/env python3
"""
live.py — poll football-data.org for LIVE + FINISHED WC2026 matches (run hourly).

Writes a small `wc2026/live.json` (in-play scores + the full locked map) that the app
polls every minute to mark live games and a "Today" strip, and LOCKS any newly
FINISHED game into `data.json` (+ syncs the inline fallback) so the bracket, accuracy
tab and performance log pick it up at full-time.

    python3 live.py --token $FOOTBALL_DATA_TOKEN

Only rewrites files when something actually changed, so idle hours produce no commits.
Needs a free token from https://football-data.org (repo secret FOOTBALL_DATA_TOKEN).
"""
import argparse, datetime, json, sys, urllib.request, urllib.error
from pathlib import Path
import update                     # reuse name_to_code() + sync_embed()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.json"
LIVE = ROOT / "live.json"
COMP = "WC"                       # football-data.org competition code for the FIFA World Cup
LIVE_STATES = {"IN_PLAY", "PAUSED", "LIVE", "HALFTIME", "SUSPENDED"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="football-data.org API token")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    idx = update.name_to_code(data)
    by_pair = {(f["home"], f["away"]): f["no"] for f in data["fixtures"]}

    url = f"https://api.football-data.org/v4/competitions/{COMP}/matches"
    req = urllib.request.Request(url, headers={"X-Auth-Token": args.token})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        # transient API issues (rate-limit, 5xx) just mean "no new data this run" — don't fail the job
        print(f"football-data HTTP {e.code} — skipping this run (no data fetched)", file=sys.stderr)
        return
    except Exception as e:                       # noqa: BLE001
        print(f"football-data fetch failed: {e} — skipping this run", file=sys.stderr)
        return

    live, new_locks = {}, 0
    for m in payload.get("matches", []):
        h = idx.get((m.get("homeTeam", {}).get("name") or "").lower())
        a = idx.get((m.get("awayTeam", {}).get("name") or "").lower())
        no = by_pair.get((h, a)) if (h and a) else None
        if not no:
            continue                       # group fixtures map by team-pair; knockout handled below
        st = m.get("status")
        ft = m.get("score", {}).get("fullTime", {})
        hg, ag = ft.get("home"), ft.get("away")
        if st == "FINISHED" and hg is not None:
            if data["locked"].get(str(no)) != [int(hg), int(ag)]:
                data["locked"][str(no)] = [int(hg), int(ag)]
                new_locks += 1
        elif st in LIVE_STATES:
            live[str(no)] = {"h": int(hg or 0), "a": int(ag or 0), "status": st, "min": m.get("minute")}

    # knockout games carry bracket-slot placeholders, not fixed team-pairs — relay them raw (the app
    # maps each onto its slot). Finished -> data.json `ko` + live.json; in-play -> live.json `koLive`.
    ko = update.collect_ko(payload, idx)                              # FINISHED knockout results
    ko_live = update.collect_ko(payload, idx, statuses=tuple(LIVE_STATES))   # in-play knockout
    ko_changed = data.get("ko", []) != ko
    if ko_changed:
        data["ko"] = ko

    old = json.loads(LIVE.read_text(encoding="utf-8")) if LIVE.exists() else {}
    if (old.get("live") == live and old.get("locked") == data["locked"]
            and old.get("ko", []) == ko and old.get("koLive", []) == ko_live):
        print(f"no change ({len(live)} live, {len(data['locked'])} locked, {len(ko)} ko, {len(ko_live)} ko-live)")
        return

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    LIVE.write_text(json.dumps({"liveAt": now, "asOf": data["meta"].get("asOf"),
                                "live": live, "locked": data["locked"], "ko": ko, "koLive": ko_live},
                               ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"live.json updated: {len(live)} live, {len(data['locked'])} locked, "
          f"{len(ko)} ko ({new_locks} new group), {len(ko_live)} ko-live")

    if new_locks or ko_changed:
        data["meta"]["version"] = int(data["meta"].get("version", 0)) + 1
        data["meta"]["asOf"] = datetime.date.today().isoformat()
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        update.sync_embed(data)
        print(f"  -> data.json v{data['meta']['version']} ({new_locks} new group locks, "
              f"{len(ko)} knockout results) + inline fallback synced")


if __name__ == "__main__":
    main()
