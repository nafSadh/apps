"""
Adapter: football-data.co.uk league CSVs -> UnifiedMatch rows (club football).

Each file is one league-season (e.g. raw/football_data/E0_2324.csv). Columns
(see https://www.football-data.co.uk/notes.txt):
    Date (dd/mm/yy or dd/mm/yyyy), HomeTeam, AwayTeam,
    FTHG, FTAG (full-time goals), FTR (H/D/A),
    HS/AS (shots), HST/AST (shots on target)   -- present from ~2010 on.

All club matches; neutral=False, is_intl=False. xG is not provided here (None).
Point this at a directory and it ingests every *.csv inside.
"""

import csv
from pathlib import Path

from schema import UnifiedMatch, canon


def _i(row, k):
    v = (row.get(k) or "").strip()
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _f(row, k):
    v = (row.get(k) or "").strip()
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _date(s):
    s = s.strip()
    d, m, y = s.split("/")
    y = ("20" + y) if len(y) == 2 else y           # dd/mm/yy -> 20yy
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"


def load_file(path):
    rows = []
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        for d in csv.DictReader(f):
            if not (d.get("Date") and d.get("HomeTeam") and d.get("AwayTeam")):
                continue
            hg, ag = _i(d, "FTHG"), _i(d, "FTAG")
            if hg is None:
                hg, ag = _i(d, "HG"), _i(d, "AG")   # very old column names
            if hg is None or ag is None:
                continue
            try:
                date = _date(d["Date"])
            except (ValueError, IndexError):
                continue
            rows.append(UnifiedMatch(
                date=date, home=canon(d["HomeTeam"]), away=canon(d["AwayTeam"]),
                home_score=hg, away_score=ag, neutral=False,
                competition=(d.get("Div") or "Club").strip(),
                source="football_data", is_intl=False,
                home_shots=_f(d, "HS"), away_shots=_f(d, "AS"),
                home_sot=_f(d, "HST"), away_sot=_f(d, "AST")))
    return rows


def load_dir(directory):
    directory = Path(directory)
    rows = []
    for csv_path in sorted(directory.glob("*.csv")):
        rows.extend(load_file(csv_path))
    return rows


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "raw/football_data"
    r = load_dir(d)
    print(f"{len(r)} club matches from {d}")
    for m in r[:3]:
        print(" ", m.date, m.home, m.home_score, "-", m.away_score, m.away,
              f"shots {m.home_shots}-{m.away_shots}")
