"""
Tabular features + an optional historical-FIFA-ranking feature.

This extends the 4 base features with a 5th — `fifa_rank_diff` — looked up
no-leakage (most recent ranking strictly BEFORE each match) from a historical
FIFA ranking CSV. FIFA has published rankings monthly since Aug 1992, so the
feature is live for ~30 years of internationals and 0 (masked) before that.

If `data_sources/raw/fifa_ranking.csv` is absent, the feature is all-zeros and
this behaves exactly like the 4-feature `prep_data` — so it always runs.

Get the file (Kaggle login needed), drop it at data_sources/raw/fifa_ranking.csv:
    https://www.kaggle.com/datasets/cashncarry/fifaworldranking

Demo:  python3 prep_data_plus.py     # trains logistic on 4 vs 5 features, compares
"""

import sys
from pathlib import Path

import numpy as np

from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
FIFA_CSV = HERE / "data_sources" / "raw" / "fifa_ranking.csv"


def _fifa_diffs(metadata):
    """Per-row (points_home - points_away)/100 as-of match date; 0 when unknown."""
    sys.path.insert(0, str(HERE / "data_sources"))
    try:
        from adapt_fifa_rankings import FifaRankings
    except Exception:                                        # noqa: BLE001
        return None, 0
    fr = FifaRankings(FIFA_CSV)
    diffs, hit = [], 0
    for r in metadata:
        ph = fr.points_as_of(r["home"], r["date"])
        pa = fr.points_as_of(r["away"], r["date"])
        if ph is not None and pa is not None:
            diffs.append((ph - pa) / 100.0)
            hit += 1
        else:
            diffs.append(0.0)
    return np.array(diffs, dtype=float), hit


def load_with_fifa(**kw):
    d = load_and_preprocess(**kw)
    has_fifa = FIFA_CSV.exists()
    tr_diff = np.zeros(len(d["X_train"]))
    va_diff = np.zeros(len(d["X_val"]))
    cov = 0
    if has_fifa:
        tr_diff, cov = _fifa_diffs(d["train_metadata"])
        va_diff, _ = _fifa_diffs(d["val_metadata"])
        if tr_diff is None:                                  # import failed
            has_fifa, tr_diff, va_diff = False, np.zeros(len(d["X_train"])), np.zeros(len(d["X_val"]))
        else:
            mu, sd = tr_diff.mean(), tr_diff.std() or 1.0    # standardize on train
            tr_diff = (tr_diff - mu) / sd
            va_diff = (va_diff - mu) / sd
    d["X_train5"] = np.hstack([d["X_train"], tr_diff.reshape(-1, 1)])
    d["X_val5"] = np.hstack([d["X_val"], va_diff.reshape(-1, 1)])
    d["has_fifa"] = has_fifa
    d["fifa_train_coverage"] = cov
    return d


def main():
    from models import SoftmaxRegression
    from metrics import summary
    d = load_with_fifa()
    if d["has_fifa"]:
        print(f"FIFA ranking file found — feature covers {d['fifa_train_coverage']} "
              f"/ {len(d['X_train5'])} training matches.")
    else:
        print("No data_sources/raw/fifa_ranking.csv — 5th feature is zeroed "
              "(download it to activate; see this file's docstring).")

    base = SoftmaxRegression(cols=(0, 1, 2, 3)).fit(d["X_train5"], d["y_train"])
    plus = SoftmaxRegression(cols=(0, 1, 2, 3, 4)).fit(d["X_train5"], d["y_train"])
    sb = summary(base.predict_proba(d["X_val5"]), d["y_val"])
    sp = summary(plus.predict_proba(d["X_val5"]), d["y_val"])
    print(f"\n4 features : acc {sb['accuracy']*100:.1f}%  log-loss {sb['log_loss']:.3f}  "
          f"decisive {sb['decisive_hit_rate']*100:.0f}%")
    print(f"+ FIFA rank: acc {sp['accuracy']*100:.1f}%  log-loss {sp['log_loss']:.3f}  "
          f"decisive {sp['decisive_hit_rate']*100:.0f}%")
    if not d["has_fifa"]:
        print("(identical until the FIFA file is added)")


if __name__ == "__main__":
    main()
