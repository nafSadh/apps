"""
Merge every available source into one unified, de-duplicated match corpus.

    python3 build_corpus.py

Auto-detects what you've downloaded under data_sources/raw/:
    raw/spi_matches.csv            -> 538 club (xG)
    raw/spi_matches_intl.csv       -> 538 internationals (xG)
    raw/football_data/*.csv        -> football-data.co.uk club (shots)
    raw/statsbomb/open-data/       -> StatsBomb internationals (xG, from events)
The martj42 international base (../../scripts/intl-results.csv) is always
included so the 2026 World Cup validation matches are present.

De-dup is by (date, home, away); when two sources describe the same match we
keep one row and fill in any richness (xG/shots) the other had. Writes
`corpus.csv` and prints a coverage report + the first unmapped team names so you
can extend schema.ALIASES.
"""

import csv
from pathlib import Path

from schema import (UnifiedMatch, canon, write_corpus, unmapped_names,
                    register_canonical)

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
BASE_CSV = HERE.parent.parent / "scripts" / "intl-results.csv"


def load_base_intl():
    rows = []
    with open(BASE_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        recs = list(r)
    # the base spellings ARE our canonical vocabulary
    register_canonical({d["home_team"].strip() for d in recs}
                       | {d["away_team"].strip() for d in recs})
    for d in recs:
        hs, as_ = d["home_score"].strip(), d["away_score"].strip()
        if hs in ("", "NA") or as_ in ("", "NA"):
            continue
        rows.append(UnifiedMatch(
            date=d["date"].strip(), home=canon(d["home_team"]),
            away=canon(d["away_team"]), home_score=int(hs), away_score=int(as_),
            neutral=d["neutral"].strip().upper() == "TRUE",
            competition=d.get("tournament", "International").strip(),
            source="intl_base", is_intl=True))
    return rows


def _merge_rich(keep, other):
    """Fill keep's None richness fields from other."""
    for fld in ("home_xg", "away_xg", "home_shots", "away_shots",
                "home_sot", "away_sot", "home_poss", "away_poss"):
        if getattr(keep, fld) is None and getattr(other, fld) is not None:
            setattr(keep, fld, getattr(other, fld))
    return keep


# richness priority when the same match appears in multiple sources
_PRIORITY = {"statsbomb": 3, "spi_intl": 2, "spi_club": 2, "football_data": 1, "intl_base": 0}


def main():
    all_rows = load_base_intl()
    print(f"base internationals: {len(all_rows)}")

    if (RAW / "spi_matches_intl.csv").exists():
        from adapt_538_spi import load_spi
        r = load_spi(RAW / "spi_matches_intl.csv", is_intl=True)
        all_rows += r
        print(f"+ 538 SPI internationals: {len(r)}")
    if (RAW / "spi_matches.csv").exists():
        from adapt_538_spi import load_spi
        r = load_spi(RAW / "spi_matches.csv", is_intl=False)
        all_rows += r
        print(f"+ 538 SPI club: {len(r)}")
    if (RAW / "football_data").exists():
        from adapt_football_data_couk import load_dir
        r = load_dir(RAW / "football_data")
        all_rows += r
        print(f"+ football-data.co.uk club: {len(r)}")
    sb = RAW / "statsbomb" / "open-data"
    if sb.exists() or (RAW / "statsbomb").exists():
        from adapt_statsbomb import load_statsbomb
        root = sb if sb.exists() else (RAW / "statsbomb")
        r = load_statsbomb(root, international_only=True, include_xg=True)
        all_rows += r
        print(f"+ StatsBomb internationals: {len(r)}")

    # de-dup, merging richness; higher-priority source wins the base row
    best = {}
    for m in all_rows:
        k = m.key()
        if k not in best:
            best[k] = m
        else:
            cur = best[k]
            hi, lo = (m, cur) if _PRIORITY[m.source] > _PRIORITY[cur.source] else (cur, m)
            best[k] = _merge_rich(hi, lo)

    rows = list(best.values())
    n = write_corpus(rows, HERE / "corpus.csv")

    intl = sum(1 for r in rows if r.is_intl)
    with_xg = sum(1 for r in rows if r.home_xg is not None)
    with_shots = sum(1 for r in rows if r.home_shots is not None)
    by_src = {}
    for r in rows:
        by_src[r.source] = by_src.get(r.source, 0) + 1

    print("\n=== corpus.csv ===")
    print(f"total matches : {n}")
    print(f"  international: {intl}   club: {n - intl}")
    print(f"  with xG      : {with_xg}")
    print(f"  with shots   : {with_shots}")
    print("by source     :", by_src)
    um = unmapped_names()
    if um:
        print(f"\n{len(um)} unmapped team names (add to schema.ALIASES if any are dupes):")
        print("  " + ", ".join(um[:30]) + (" ..." if len(um) > 30 else ""))


if __name__ == "__main__":
    main()
