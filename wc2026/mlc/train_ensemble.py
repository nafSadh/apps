"""Ensembles over the base learners.

Two flavours, both saved:
  * Soft-vote  — simple average of base-model probabilities.
  * Stacking   — a meta softmax-logistic trained on base-model probabilities.

Leakage control for stacking: the meta-learner must NOT see base predictions on
data the bases were trained on. We therefore split the (chronologically ordered)
training set into an early 'base-fit' slice and a later 'meta-fit' holdout, train
fresh bases on the early slice, and train the meta-model on their predictions over
the held-out slice. The bases that ship inside the ensemble are then re-fit on the
FULL training set for inference."""

import pickle
import time
from pathlib import Path

import numpy as np

from prep_data import load_and_preprocess
from models import (SoftmaxRegression, OrdinalLogistic, DixonColesPoisson,
                    GaussianNaiveBayes, RandomForest, MLPClassifier, KNNClassifier,
                    StackingEnsemble, SoftVotingEnsemble)
from report import per_match

HERE = Path(__file__).resolve().parent


def build_bases(X, y, gh, ga, scaler):
    """Fit one of each base model on (X, y) and return [(name, model), ...]."""
    bases = []
    bases.append(("Softmax logistic", SoftmaxRegression(cols=(0, 1, 2, 3)).fit(X, y, scaler)))
    bases.append(("Ordinal logistic", OrdinalLogistic(cols=(0, 1, 2, 3)).fit(X, y, scaler)))
    bases.append(("Dixon-Coles Poisson", DixonColesPoisson(cols=(0, 1, 2, 3)).fit(X, gh, ga, scaler)))
    bases.append(("Gaussian NB", GaussianNaiveBayes().fit(X, y, scaler)))
    bases.append(("Random forest", RandomForest(n_trees=25, max_depth=8,
                  min_samples_split=40, max_features=2, sample_size=20000).fit(X, y, scaler)))
    bases.append(("MLP", MLPClassifier().fit(X, y, scaler)))
    bases.append(("k-NN", KNNClassifier(k=25).fit(X, y, scaler)))
    return bases


def main():
    print("=== Training ensembles (soft-vote + stacking) ===")
    d = load_and_preprocess()
    X, y = d["X_train"], d["y_train"]
    gh, ga = d["g_home_train"], d["g_away_train"]
    scaler = d["scaler"]
    n = len(X)

    # chronological split (train_metadata is in date order): early -> bases, late -> meta
    meta_size = min(4000, n // 6)
    split = n - meta_size
    print(f"base-fit slice: {split} matches  |  meta-fit holdout: {meta_size} matches")

    t = time.time()
    oof_bases = build_bases(X[:split], y[:split], gh[:split], ga[:split], scaler)
    Z_meta = np.hstack([m.predict_proba(X[split:]) for _, m in oof_bases])
    y_meta = y[split:]
    meta = SoftmaxRegression(cols=tuple(range(Z_meta.shape[1])),
                             lr=0.5, iters=600, l2=1e-3).fit(Z_meta, y_meta)
    print(f"meta-learner trained on {Z_meta.shape[1]} stacked features "
          f"[{time.time()-t:.1f}s]")

    # final bases re-fit on the FULL training set
    t = time.time()
    full_bases = build_bases(X, y, gh, ga, scaler)
    print(f"re-fit {len(full_bases)} bases on full train [{time.time()-t:.1f}s]")

    stack = StackingEnsemble(full_bases, meta)
    vote = SoftVotingEnsemble(full_bases)
    pickle.dump(stack, open(HERE / "ensemble_model.pkl", "wb"))
    pickle.dump(vote, open(HERE / "voting_model.pkl", "wb"))
    print("saved ensemble_model.pkl (stacking), voting_model.pkl (soft-vote)")

    print("\nMeta-learner weights (how much each base drives the home-win logit):")
    names = [nm for nm, _ in full_bases]
    Wh = meta.W[0]                      # home-win class weights; col0 is bias
    for i, nm in enumerate(names):
        # each base contributes 3 stacked cols: home,draw,away -> show the home col
        print(f"  {nm:<22} {Wh[1 + i * 3]:+.3f}")

    per_match("Soft-vote ensemble", vote.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])
    per_match("Stacking ensemble", stack.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
