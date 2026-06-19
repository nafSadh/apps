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
        sys.exit(f"football-data HTTP {e.code} — check token / competition access")
    except Exception as e:                       # noqa: BLE001
        sys.exit(f"football-data fetch failed: {e}")

    live, new_locks = {}, 0
    for m in payload.get("matches", []):
        h = idx.get((m.get("homeTeam", {}).get("name") or "").lower())
        a = idx.get((m.get("awayTeam", {}).get("name") or "").lower())
        no = by_pair.get((h, a)) if (h and a) else None
        if not no:
            continue
        st = m.get("status")
        ft = m.get("score", {}).get("fullTime", {})
        hg, ag = ft.get("home"), ft.get("away")
        if st == "FINISHED" and hg is not None:
            if data["locked"].get(str(no)) != [int(hg), int(ag)]:
                data["locked"][str(no)] = [int(hg), int(ag)]
                new_locks += 1
        elif st in LIVE_STATES:
            live[str(no)] = {"h": int(hg or 0), "a": int(ag or 0), "status": st, "min": m.get("minute")}

    old = json.loads(LIVE.read_text(encoding="utf-8")) if LIVE.exists() else {}
    if old.get("live") == live and old.get("locked") == data["locked"]:
        print(f"no change ({len(live)} live, {len(data['locked'])} locked)")
        return

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    LIVE.write_text(json.dumps({"liveAt": now, "asOf": data["meta"].get("asOf"),
                                "live": live, "locked": data["locked"]},
                               ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"live.json updated: {len(live)} live, {len(data['locked'])} locked ({new_locks} new)")

    if new_locks:
        data["meta"]["version"] = int(data["meta"].get("version", 0)) + 1
        data["meta"]["asOf"] = datetime.date.today().isoformat()
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        update.sync_embed(data)
        print(f"  locked {new_locks} new at full-time -> data.json v{data['meta']['version']} + inline fallback synced")


if __name__ == "__main__":
    main()
