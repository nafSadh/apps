"""
Smoke tests for every source adapter, using tiny synthetic fixtures built in a
temp dir. No network, no downloads — proves the parsing/canonicalization logic
works before you point the adapters at real files.

    python3 test_adapters.py
"""

import json
import tempfile
from pathlib import Path

import schema
from schema import register_canonical, canon


def _reset_canon():
    # seed a minimal canonical vocabulary the way build_corpus does
    register_canonical(["United States", "South Korea", "England", "Brazil",
                        "Qatar", "Ecuador", "Arsenal", "Chelsea"])


def test_538():
    from adapt_538_spi import load_spi
    hdr = ("season,date,league_id,league,team1,team2,spi1,spi2,prob1,prob2,probtie,"
           "proj_score1,proj_score2,importance1,importance2,score1,score2,xg1,xg2,"
           "nsxg1,nsxg2,adj_score1,adj_score2")
    rows = [
        "2022,2022-11-20,9999,FIFA World Cup,USA,Korea Republic,70,68,.4,.3,.3,1.2,1.0,80,80,2,1,1.8,0.9,1.5,0.8,2,1",
        "2026,2026-12-01,9999,FIFA World Cup,Brazil,England,90,88,.4,.3,.3,1.1,1.0,,,,,,,,,",  # unplayed -> skipped
    ]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "spi_matches_intl.csv"
        p.write_text(hdr + "\n" + "\n".join(rows))
        r = load_spi(p, is_intl=True)
    assert len(r) == 1, f"expected 1 played row, got {len(r)}"
    m = r[0]
    assert m.home == "United States" and m.away == "South Korea", (m.home, m.away)
    assert m.home_score == 2 and m.away_score == 1
    assert abs(m.home_xg - 1.8) < 1e-6 and abs(m.away_xg - 0.9) < 1e-6
    assert m.is_intl and m.source == "spi_intl"
    print("538 SPI            OK")


def test_football_data():
    from adapt_football_data_couk import load_dir
    hdr = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST"
    rows = ["E0,17/08/24,Arsenal,Chelsea,2,0,H,15,8,6,3",
            "E0,18/08/2024,Chelsea,Arsenal,1,1,D,10,12,4,5"]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "E0_2425.csv").write_text(hdr + "\n" + "\n".join(rows))
        r = load_dir(d)
    assert len(r) == 2, len(r)
    a = r[0]
    assert a.date == "2024-08-17", a.date
    assert a.home == "Arsenal" and a.away == "Chelsea"
    assert a.home_score == 2 and a.home_shots == 15 and a.home_sot == 6
    assert a.is_intl is False and a.neutral is False
    print("football-data.co.uk OK")


def test_statsbomb():
    from adapt_statsbomb import load_statsbomb
    with tempfile.TemporaryDirectory() as td:
        data = Path(td) / "data"
        (data / "matches" / "43").mkdir(parents=True)
        (data / "events").mkdir(parents=True)
        comps = [{"competition_id": 43, "season_id": 106,
                  "competition_name": "FIFA World Cup", "competition_international": True}]
        (data / "competitions.json").write_text(json.dumps(comps))
        matches = [{"match_id": 7, "match_date": "2022-11-21",
                    "home_team": {"home_team_name": "England"},
                    "away_team": {"away_team_name": "USA"},
                    "home_score": 2, "away_score": 0}]
        (data / "matches" / "43" / "106.json").write_text(json.dumps(matches))
        events = [
            {"type": {"name": "Shot"}, "team": {"name": "England"},
             "shot": {"statsbomb_xg": 0.5, "outcome": {"name": "Goal"}}},
            {"type": {"name": "Shot"}, "team": {"name": "England"},
             "shot": {"statsbomb_xg": 0.3, "outcome": {"name": "Off T"}}},
            {"type": {"name": "Shot"}, "team": {"name": "USA"},
             "shot": {"statsbomb_xg": 0.2, "outcome": {"name": "Saved"}}},
            {"type": {"name": "Pass"}, "team": {"name": "USA"}},
        ]
        (data / "events" / "7.json").write_text(json.dumps(events))
        r = load_statsbomb(Path(td), international_only=True, include_xg=True)
    assert len(r) == 1, len(r)
    m = r[0]
    assert m.home == "England" and m.away == "United States", (m.home, m.away)
    assert abs(m.home_xg - 0.8) < 1e-6, m.home_xg          # 0.5 + 0.3
    assert m.home_shots == 2 and m.home_sot == 1           # only the Goal is on target
    assert abs(m.away_xg - 0.2) < 1e-6 and m.away_sot == 1
    assert m.is_intl and m.neutral is True
    print("StatsBomb           OK")


def test_fifa():
    from adapt_fifa_rankings import FifaRankings
    hdr = "rank,country_full,country_abrv,total_points,rank_date"
    rows = ["1,Brazil,BRA,1800,2022-09-01",
            "1,Brazil,BRA,1840,2022-11-01",
            "13,USA,USA,1650,2022-11-01"]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "fifa_ranking.csv"
        p.write_text(hdr + "\n" + "\n".join(rows))
        fr = FifaRankings(p)
    assert fr.points_as_of("Brazil", "2022-11-15") == 1840
    assert fr.points_as_of("Brazil", "2022-10-01") == 1800     # most recent BEFORE
    assert fr.points_as_of("Brazil", "2022-08-01") is None     # nothing before
    assert fr.points_as_of("USA", "2022-12-01") == 1650        # canonicalized to United States
    assert fr.rank_as_of("Brazil", "2022-11-15") == 1
    print("FIFA rankings       OK")


if __name__ == "__main__":
    _reset_canon()
    test_538()
    test_football_data()
    test_statsbomb()
    test_fifa()
    print("\nall adapter smoke tests passed.")
