"""Multinomial (softmax) logistic regression — the 'full logistic' baseline,
plus an Elo-only variant. Trained from scratch by gradient descent."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import SoftmaxRegression
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training softmax logistic regression ===")
    d = load_and_preprocess()
    full = SoftmaxRegression(cols=(0, 1, 2, 3)).fit(d["X_train"], d["y_train"], d["scaler"])
    elo = SoftmaxRegression(cols=(0, 1)).fit(d["X_train"], d["y_train"], d["scaler"])

    pickle.dump(full, open(HERE / "logistic_model.pkl", "wb"))
    pickle.dump(elo, open(HERE / "logistic_elo_model.pkl", "wb"))
    print("saved logistic_model.pkl, logistic_elo_model.pkl")

    per_match("Softmax logistic (full)", full.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])
    per_match("Elo-only logistic", elo.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])

    names = ["bias", "Elo diff", "home adv", "recent form", "head-to-head"]
    print("\nFull-logistic weights (home-win minus away-win class; + favours home):")
    W = full.W
    for j, nm in enumerate(names):
        print(f"  {nm:<14} {W[0][j] - W[2][j]:+.3f}")


if __name__ == "__main__":
    main()
