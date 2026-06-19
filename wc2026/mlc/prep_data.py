"""
Self-contained data prep for the `mlc/` model lab.

Mirrors the chronological, no-future-leakage feature engineering used by the
sibling `scripts/` pipeline so the two are directly comparable, but lives
entirely inside `mlc/` and does not import from (or write to) `scripts/`.

For every match, walking the dataset in date order, we build four features
using only information known *before* kickoff:
    0: Elo difference  (running rating, home advantage + margin-of-victory)   [continuous]
    1: home advantage  (0 on neutral ground, else 1)                          [binary]
    2: recent-form goal-difference, last N games each, home minus away        [continuous]
    3: pairwise head-to-head rate                                             [continuous]

Label y: 0 = home win, 1 = draw, 2 = away win.

Train = everything from `warm_year` up to (but not including) `cutoff_date`.
Validation = played matches on/after `cutoff_date` -> the 2026 World Cup
group-stage matches that have actually happened.

We also return raw goal counts (g_home / g_away) for the Poisson goals model.

Data source (read-only): ../scripts/intl-results.csv
    https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017
"""

import csv
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# The CSV is owned by the scripts/ pipeline; we only ever READ it.
CSV_PATH = HERE.parent / "scripts" / "intl-results.csv"

CONT_IDX = [0, 2, 3]          # continuous feature columns to standardize
CLASS_NAMES = {0: "Home win", 1: "Draw", 2: "Away win"}


def _load_matches():
    matches = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r)
        ci = {name: header.index(name) for name in
              ("date", "home_team", "away_team", "home_score", "away_score", "neutral")}
        for row in r:
            if not row or len(row) <= max(ci.values()):
                continue
            hs_str, as_str = row[ci["home_score"]].strip(), row[ci["away_score"]].strip()
            if hs_str in ("", "NA") or as_str in ("", "NA"):
                continue  # unplayed / future fixture
            try:
                hs, as_ = int(hs_str), int(as_str)
            except ValueError:
                continue
            matches.append({
                "date": row[ci["date"]].strip(),
                "home": row[ci["home_team"]].strip(),
                "away": row[ci["away_team"]].strip(),
                "hs": hs,
                "as": as_,
                "neutral": row[ci["neutral"]].strip().upper() == "TRUE",
            })
    matches.sort(key=lambda m: m["date"])
    return matches


def load_and_preprocess(warm_year=1950, cutoff_date="2026-06-11",
                        K=30, home_adv=65, form_n=5):
    matches = _load_matches()

    elo, last, h2h = {}, {}, {}

    def get_elo(t):
        return elo.get(t, 1500.0)

    def form_gd(t):
        lst = last.get(t, [])
        return sum(lst) / len(lst) if lst else 0.0

    train_rows, val_rows = [], []

    for m in matches:
        home, away = m["home"], m["away"]
        eh, ea = get_elo(home), get_elo(away)
        h_adv = 0.0 if m["neutral"] else home_adv

        key = f"{home}|{away}" if home < away else f"{away}|{home}"
        rec = h2h.get(key, {"x": 0, "d": 0, "y": 0})
        tot = rec["x"] + rec["d"] + rec["y"]
        if tot > 0:
            signed = rec["x"] - rec["y"] if home < away else rec["y"] - rec["x"]
            h2h_val = signed / tot
        else:
            h2h_val = 0.0

        feat = [
            (eh - ea) / 100.0,
            0.0 if m["neutral"] else 1.0,
            form_gd(home) - form_gd(away),
            h2h_val,
        ]

        if m["hs"] > m["as"]:
            y = 0
        elif m["hs"] == m["as"]:
            y = 1
        else:
            y = 2

        row = {
            "date": m["date"], "home": home, "away": away,
            "feat": feat, "y": y, "score": (m["hs"], m["as"]),
            "neutral": m["neutral"],
        }

        try:
            year = int(m["date"][:4])
        except ValueError:
            year = 0

        if year >= warm_year:
            (train_rows if m["date"] < cutoff_date else val_rows).append(row)

        # --- chronological state updates (after the row is recorded) ---
        exp = 1.0 / (1.0 + math.pow(10.0, -((eh - ea + h_adv) / 400.0)))
        sc = 1.0 if m["hs"] > m["as"] else (0.5 if m["hs"] == m["as"] else 0.0)
        mov = math.log(abs(m["hs"] - m["as"]) + 1.0)
        elo[home] = eh + K * mov * (sc - exp)
        elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))

        last.setdefault(home, []).append(m["hs"] - m["as"])
        if len(last[home]) > form_n:
            last[home].pop(0)
        last.setdefault(away, []).append(m["as"] - m["hs"])
        if len(last[away]) > form_n:
            last[away].pop(0)

        rh = h2h.setdefault(key, {"x": 0, "d": 0, "y": 0})
        if m["hs"] == m["as"]:
            rh["d"] += 1
        else:
            home_is_first = home < away
            home_won = m["hs"] > m["as"]
            if home_won == home_is_first:
                rh["x"] += 1
            else:
                rh["y"] += 1

    X_train_raw = np.array([r["feat"] for r in train_rows], dtype=float)
    y_train = np.array([r["y"] for r in train_rows], dtype=int)
    X_val_raw = np.array([r["feat"] for r in val_rows], dtype=float)
    y_val = np.array([r["y"] for r in val_rows], dtype=int)

    # Goal targets for the Poisson model.
    g_home_train = np.array([r["score"][0] for r in train_rows], dtype=float)
    g_away_train = np.array([r["score"][1] for r in train_rows], dtype=float)
    g_home_val = np.array([r["score"][0] for r in val_rows], dtype=float)
    g_away_val = np.array([r["score"][1] for r in val_rows], dtype=float)

    # Standardize continuous features on TRAIN statistics only.
    mean = np.mean(X_train_raw[:, CONT_IDX], axis=0)
    std = np.std(X_train_raw[:, CONT_IDX], axis=0)
    std[std == 0] = 1.0

    def standardize(X_raw):
        X = X_raw.copy()
        X[:, CONT_IDX] = (X_raw[:, CONT_IDX] - mean) / std
        return X

    return {
        "X_train": standardize(X_train_raw),
        "y_train": y_train,
        "X_val": standardize(X_val_raw),
        "y_val": y_val,
        "g_home_train": g_home_train, "g_away_train": g_away_train,
        "g_home_val": g_home_val, "g_away_val": g_away_val,
        "mean": mean, "std": std,
        "train_metadata": train_rows,
        "val_metadata": val_rows,
        "scaler": {"mean": mean.tolist(), "std": std.tolist()},
        "config": {"warm_year": warm_year, "cutoff_date": cutoff_date,
                   "K": K, "home_adv": home_adv, "form_n": form_n},
    }


if __name__ == "__main__":
    d = load_and_preprocess()
    print(f"Train size: {len(d['X_train'])}")
    print(f"Val size (played WC 2026 matches): {len(d['X_val'])}")
    print()
    for i, r in enumerate(d["val_metadata"], 1):
        hs, as_ = r["score"]
        print(f"{i:2d}. {r['date']}  {r['home']:<16} {hs}-{as_} {r['away']:<16} "
              f"-> {CLASS_NAMES[r['y']]}")
