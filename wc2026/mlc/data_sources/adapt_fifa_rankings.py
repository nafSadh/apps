"""
Adapter: historical FIFA rankings -> a no-leakage as-of lookup.

FIFA has published the men's ranking monthly since August 1992. The widely used
Kaggle CSV ("fifa_ranking-*.csv", e.g. cashncarry / Tadhg Fitzgerald) has columns
roughly:  rank, country_full, country_abrv, total_points, ..., rank_date.
This adapter is tolerant about exact column names.

Usage (for the tabular feature):
    fr = FifaRankings("raw/fifa_ranking.csv")
    pts = fr.points_as_of("Brazil", "2026-06-11")   # most recent BEFORE that date
    rk  = fr.rank_as_of("Brazil", "2026-06-11")
Returns None when a team/date isn't covered, so callers can fall back gracefully.
"""

import bisect
import csv
from pathlib import Path

from schema import canon

_RANK_COLS = ["rank", "rank_int", "position"]
_POINTS_COLS = ["total_points", "points", "rank_points", "total_points_int"]
_TEAM_COLS = ["country_full", "country", "team", "name", "country_name"]
_DATE_COLS = ["rank_date", "date", "ranking_date"]


def _pick(header, options):
    low = {h.lower(): h for h in header}
    for o in options:
        if o in low:
            return low[o]
    return None


class FifaRankings:
    def __init__(self, path):
        path = Path(path)
        self.by_team = {}        # canon team -> (sorted dates[], points[], ranks[])
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            header = r.fieldnames or []
            tc = _pick(header, _TEAM_COLS)
            dc = _pick(header, _DATE_COLS)
            pc = _pick(header, _POINTS_COLS)
            kc = _pick(header, _RANK_COLS)
            if not (tc and dc):
                raise ValueError(f"Could not find team/date columns in {header}")
            tmp = {}
            for d in r:
                team = canon(d[tc])
                date = d[dc].strip()[:10]
                pts = _num(d.get(pc)) if pc else None
                rk = _num(d.get(kc)) if kc else None
                tmp.setdefault(team, []).append((date, pts, rk))
        for team, recs in tmp.items():
            recs.sort(key=lambda x: x[0])
            self.by_team[team] = (
                [x[0] for x in recs], [x[1] for x in recs], [x[2] for x in recs])

    def _as_of(self, team, date, which):
        rec = self.by_team.get(canon(team))
        if not rec:
            return None
        dates, pts, ranks = rec
        i = bisect.bisect_left(dates, date) - 1     # most recent strictly before `date`
        if i < 0:
            return None
        return (pts if which == "points" else ranks)[i]

    def points_as_of(self, team, date):
        return self._as_of(team, date, "points")

    def rank_as_of(self, team, date):
        return self._as_of(team, date, "rank")

    def coverage(self):
        return {"teams": len(self.by_team),
                "rows": sum(len(v[0]) for v in self.by_team.values())}


def _num(s):
    s = (s or "").strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "raw/fifa_ranking.csv"
    fr = FifaRankings(p)
    print("coverage:", fr.coverage())
    print("Brazil pts as of 2022-11-01:", fr.points_as_of("Brazil", "2022-11-01"))
