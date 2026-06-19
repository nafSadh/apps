"""Dixon-Coles bivariate Poisson goals model.

Two Poisson regressions predict home and away goal rates; a score matrix is
built and the Dixon-Coles correction adjusts the four low-scoring cells
(0-0, 1-0, 0-1, 1-1) where independent Poisson is known to misfit. Outcome
probabilities and a most-likely scoreline fall out of the matrix."""

import pickle
from pathlib import Path

import numpy as np

from prep_data import load_and_preprocess
from models import DixonColesPoisson
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training Dixon-Coles Poisson goals model ===")
    d = load_and_preprocess()
    model = DixonColesPoisson(cols=(0, 1, 2, 3)).fit(
        d["X_train"], d["g_home_train"], d["g_away_train"], d["scaler"])
    pickle.dump(model, open(HERE / "poisson_model.pkl", "wb"))
    print(f"saved poisson_model.pkl   (Dixon-Coles rho = {model.rho:+.3f})")

    per_match("Dixon-Coles Poisson", model.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])

    scores = model.most_likely_score(d["X_val"])
    print("\nMost-likely scorelines:")
    for m, (i, j) in zip(d["val_metadata"], scores):
        hs, as_ = m["score"]
        print(f"  {m['home'][:14]:<15} {i}-{j} {m['away'][:14]:<15}  (actual {hs}-{as_})")


if __name__ == "__main__":
    main()
