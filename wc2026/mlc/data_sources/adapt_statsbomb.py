"""
Adapter: StatsBomb Open Data (local clone) -> UnifiedMatch rows with xG.

Expects the repo cloned at a path containing `data/`:
    git clone --depth 1 https://github.com/statsbomb/open-data
Layout used:
    data/competitions.json
    data/matches/{competition_id}/{season_id}.json   -> match list + final scores
    data/events/{match_id}.json                       -> shots (shot.statsbomb_xg) for xG/SoT

`international_only=True` keeps only competition_international fixtures (World
Cups, Euros, Copa America, AFCON ...) — the ones that overlap our internationals.
xG/shots are aggregated from shot events; set include_xg=False to skip the
(heavier) events parse and take results only.

Note: StatsBomb doesn't flag neutral venue; we set neutral=True for
international tournaments (a reasonable default — override if needed) and False
for club competitions. Attribution per StatsBomb terms: data © StatsBomb.
"""

import json
from pathlib import Path

from schema import UnifiedMatch, canon

_SOT_OUTCOMES = {"Goal", "Saved", "Saved To Post", "Saved Off Target"}


def _xg_for_match(events_dir, match_id):
    """Return {team_name: [xg_sum, shots, sot]} or None if events missing."""
    p = events_dir / f"{match_id}.json"
    if not p.exists():
        return None
    try:
        events = json.load(open(p, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    agg = {}
    for e in events:
        if e.get("type", {}).get("name") != "Shot":
            continue
        team = e.get("team", {}).get("name")
        shot = e.get("shot", {})
        xg = shot.get("statsbomb_xg", 0.0) or 0.0
        outcome = shot.get("outcome", {}).get("name", "")
        a = agg.setdefault(team, [0.0, 0, 0])
        a[0] += xg
        a[1] += 1
        if outcome in _SOT_OUTCOMES:
            a[2] += 1
    return agg


def load_statsbomb(root, international_only=True, include_xg=True):
    root = Path(root)
    data = root / "data" if (root / "data").exists() else root
    comps = json.load(open(data / "competitions.json", encoding="utf-8"))
    events_dir = data / "events"
    rows = []
    seen = set()
    for c in comps:
        if international_only and not c.get("competition_international"):
            continue
        cid, sid = c["competition_id"], c["season_id"]
        mfile = data / "matches" / str(cid) / f"{sid}.json"
        if not mfile.exists():
            continue
        matches = json.load(open(mfile, encoding="utf-8"))
        for m in matches:
            if m.get("home_score") is None or m.get("away_score") is None:
                continue
            home = m["home_team"].get("home_team_name") or m["home_team"].get("country", {}).get("name")
            away = m["away_team"].get("away_team_name") or m["away_team"].get("country", {}).get("name")
            mid = m["match_id"]
            ch, ca = canon(home), canon(away)
            k = (m["match_date"], ch, ca)
            if k in seen:
                continue
            seen.add(k)
            hx = ax = hs = as_ = hsot = asot = None
            if include_xg:
                agg = _xg_for_match(events_dir, mid)
                if agg:
                    if home in agg:
                        hx, hs, hsot = agg[home][0], agg[home][1], agg[home][2]
                    if away in agg:
                        ax, as_, asot = agg[away][0], agg[away][1], agg[away][2]
            is_intl = bool(c.get("competition_international"))
            rows.append(UnifiedMatch(
                date=m["match_date"], home=ch, away=ca,
                home_score=int(m["home_score"]), away_score=int(m["away_score"]),
                neutral=True if is_intl else False,
                competition=c.get("competition_name", "StatsBomb"),
                source="statsbomb", is_intl=is_intl,
                home_xg=hx, away_xg=ax,
                home_shots=hs, away_shots=as_, home_sot=hsot, away_sot=asot))
    return rows


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "raw/statsbomb/open-data"
    r = load_statsbomb(root)
    print(f"{len(r)} international StatsBomb matches")
    for m in r[:3]:
        print(" ", m.date, m.home, m.home_score, "-", m.away_score, m.away,
              f"xg {m.home_xg}-{m.away_xg}")
