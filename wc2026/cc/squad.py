"""
cc/ — time-stamped national squad strength from the FIFA/EA team-ratings dataset.

Reads ~/src/misc-data/fifa-players/male_teams.csv (NOT in the repo) and exposes
per-(team, year) overall / attack / midfield / defence / international_prestige for
national sides, so the Transformer can finally train on a *historical* strength
signal — the thing Elo-only data lacks.

Coverage: FIFA editions 15-23 (~2014-2023). Outside that window the feature is
absent and must be masked (do NOT impute). This module just builds the lookup and
reports how much of our international history it can actually tag.
"""
import csv
from pathlib import Path

DATA_DIR = Path.home() / "src" / "misc-data"
TEAMS_CSV = DATA_DIR / "fifa-players" / "male_teams.csv"

# male_teams names -> the international-results CSV names (cc/prep.py vocab)
ALIAS = {
    "Korea Republic": "South Korea", "Korea DPR": "North Korea", "IR Iran": "Iran",
    "China PR": "China", "United States": "United States", "Republic of Ireland": "Ireland",
    "Czechia": "Czech Republic", "Türkiye": "Turkey", "Côte d'Ivoire": "Ivory Coast",
    "Cape Verde Islands": "Cape Verde", "Bosnia and Herzegovina": "Bosnia and Herzegovina",
}


def load_national():
    """{team_name -> {fifa_version:int -> dict(overall, att, mid, defence, prestige)}}."""
    table = {}
    with open(TEAMS_CSV, encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        for row in r:
            league = (row.get("league_name") or "").strip()
            # national sides have no club league in this dataset
            if league and "International" not in league:
                continue
            name = ALIAS.get(row["team_name"], row["team_name"])
            try:
                v = int(row["fifa_version"])
                ovr = int(row["overall"])
            except (ValueError, TypeError):
                continue
            d = table.setdefault(name, {})
            d[v] = {"overall": ovr,
                    "att": _i(row.get("attack")), "mid": _i(row.get("midfield")),
                    "defence": _i(row.get("defence")),
                    "prestige": _i(row.get("international_prestige"))}
    return table


def _i(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return None


def version_for(year):
    """Calendar year -> FIFA edition (FIFA 15 launched 2014 ... FIFA 23 -> 2022)."""
    return max(15, min(23, year - 2000))


def rating(table, team, year):
    d = table.get(team)
    if not d:
        return None
    v = version_for(year)
    # nearest available edition within +/-1
    for vv in (v, v - 1, v + 1, v - 2, v + 2):
        if vv in d:
            return d[vv]
    return None


if __name__ == "__main__":
    import json
    import numpy as np
    table = load_national()
    print(f"national sides with ratings: {len(table)}")
    # WC2026 teams coverage
    wc = json.load(open(Path(__file__).resolve().parent.parent / "data.json"))["teams"]
    names = [t["name"] for t in wc.values()]
    have = [n for n in names if table.get(n)]
    print(f"WC2026 teams matched: {len(have)}/48")
    miss = [n for n in names if not table.get(n)]
    if miss:
        print("  missing:", ", ".join(miss))
    # coverage over the international match history (both sides tagged), per era
    z = np.load(Path(__file__).resolve().parent / "seq.npz", allow_pickle=True)
    dates = z["dates"]
    meta = json.load(open(Path(__file__).resolve().parent / "meta.json"))
    inv = {v: k for k, v in meta["vocab"].items()}
    hid, aid, yr = z["home_id"], z["away_id"], z["year"]
    both = era = 0
    for i in range(len(dates)):
        if yr[i] < 2014 or yr[i] > 2023:
            continue
        era += 1
        h = inv.get(int(hid[i])); a = inv.get(int(aid[i]))
        if rating(table, h, int(yr[i])) and rating(table, a, int(yr[i])):
            both += 1
    print(f"internationals 2014-2023: {era}; both sides rated: {both} ({100*both/max(era,1):.0f}%)")
    arg = table.get("Argentina", {})
    print("Argentina overall by edition:", {v: arg[v]["overall"] for v in sorted(arg)})
