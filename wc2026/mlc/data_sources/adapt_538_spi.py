"""
Adapter: FiveThirtyEight SPI match files -> UnifiedMatch rows.

Files (download with fetch_data.py):
    spi_matches.csv        (club, 2016+)            -> source="spi_club",  is_intl=False
    spi_matches_intl.csv   (internationals, w/ xG)  -> source="spi_intl",  is_intl=True

Columns we use: date, league, team1, team2, score1, score2, xg1, xg2.
Rows with empty score (future/forecast-only) are skipped. SPI carries no
neutral-venue flag, so neutral is left None.
"""

import csv
from pathlib import Path

from schema import UnifiedMatch, canon


def _num(s):
    s = (s or "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def load_spi(path, is_intl):
    path = Path(path)
    source = "spi_intl" if is_intl else "spi_club"
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for d in csv.DictReader(f):
            s1, s2 = _num(d.get("score1")), _num(d.get("score2"))
            if s1 is None or s2 is None:
                continue  # unplayed / forecast-only
            rows.append(UnifiedMatch(
                date=d["date"].strip(),
                home=canon(d["team1"]), away=canon(d["team2"]),
                home_score=int(s1), away_score=int(s2),
                neutral=None,
                competition=d.get("league", "").strip() or ("International" if is_intl else "Club"),
                source=source, is_intl=is_intl,
                home_xg=_num(d.get("xg1")), away_xg=_num(d.get("xg2"))))
    return rows


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "raw/spi_matches_intl.csv"
    intl = "intl" in p
    r = load_spi(p, intl)
    print(f"{len(r)} rows from {p}  (is_intl={intl})")
    for m in r[:3]:
        print(" ", m.date, m.home, m.home_score, "-", m.away_score, m.away,
              f"xg {m.home_xg}-{m.away_xg}")
