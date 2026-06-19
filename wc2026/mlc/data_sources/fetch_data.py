"""
Downloader for the open datasets — RUN THIS LOCALLY (it needs network; it is not
run inside the Cowork sandbox). Everything lands under data_sources/raw/.

    python3 fetch_data.py --spi              # FiveThirtyEight SPI (club + intl, w/ xG)
    python3 fetch_data.py --football-data    # football-data.co.uk club CSVs (shots/odds)
    python3 fetch_data.py --statsbomb        # git clone StatsBomb open-data (xG)
    python3 fetch_data.py --all

FIFA rankings need a Kaggle login, so they're not auto-downloaded — see README.
After downloading, run:  python3 build_corpus.py
"""

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
UA = {"User-Agent": "Mozilla/5.0 (wc2026 mlc data fetch)"}

SPI = {
    "spi_matches.csv": "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv",
    "spi_matches_intl.csv": "https://projects.fivethirtyeight.com/soccer-api/international/spi_matches_intl.csv",
    "spi_global_rankings_intl.csv": "https://projects.fivethirtyeight.com/soccer-api/international/spi_global_rankings_intl.csv",
}

# football-data.co.uk: /mmz4281/{season}/{div}.csv  (season code e.g. 2425 = 2024/25)
FD_LEAGUES = ["E0", "E1", "E2", "E3", "SC0", "D1", "D2", "I1", "I2",
              "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
FD_SEASONS = [f"{y%100:02d}{(y+1)%100:02d}" for y in range(2010, 2026)]


def _get(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
        print(f"  ok  {dest.relative_to(HERE)}  ({dest.stat().st_size//1024} KB)")
        return True
    except Exception as e:                                    # noqa: BLE001
        print(f"  --  {url}  ({e})")
        return False


def fetch_spi():
    print("FiveThirtyEight SPI:")
    for name, url in SPI.items():
        _get(url, RAW / name)


def fetch_football_data():
    print("football-data.co.uk (leagues x seasons):")
    ok = 0
    for s in FD_SEASONS:
        for lg in FD_LEAGUES:
            url = f"https://www.football-data.co.uk/mmz4281/{s}/{lg}.csv"
            if _get(url, RAW / "football_data" / f"{lg}_{s}.csv"):
                ok += 1
    print(f"  downloaded {ok} league-season files")


def fetch_statsbomb():
    print("StatsBomb open-data (git clone, ~shallow):")
    dest = RAW / "statsbomb" / "open-data"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print("  already present; pull latest with `git -C <dir> pull`")
        return
    try:
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/statsbomb/open-data", str(dest)], check=True)
    except Exception as e:                                    # noqa: BLE001
        print(f"  git clone failed ({e}). Install git or download the repo zip manually.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spi", action="store_true")
    ap.add_argument("--football-data", action="store_true")
    ap.add_argument("--statsbomb", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not any([a.spi, a.football_data, a.statsbomb, a.all]):
        ap.print_help()
        sys.exit(0)
    if a.spi or a.all:
        fetch_spi()
    if a.football_data or a.all:
        fetch_football_data()
    if a.statsbomb or a.all:
        fetch_statsbomb()
    print("\nNext:  python3 build_corpus.py")


if __name__ == "__main__":
    main()
