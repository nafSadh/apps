"""Proportional-odds ordinal logistic regression.

W/D/L are not three unrelated classes — they are ordered on a single
'home favourability' axis (away win < draw < home win). This model fits one
latent score and two thresholds, which usually calibrates the draw band
better than an unordered softmax."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import OrdinalLogistic
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training ordinal logistic (proportional odds) ===")
    d = load_and_preprocess()
    model = OrdinalLogistic(cols=(0, 1, 2, 3)).fit(d["X_train"], d["y_train"], d["scaler"])
    pickle.dump(model, open(HERE / "ordinal_model.pkl", "wb"))
    print("saved ordinal_model.pkl")

    per_match("Ordinal logistic", model.predict_proba(d["X_val"]),
              d["val_metadata"], d["y_val"])

    names = ["Elo diff", "home adv", "recent form", "head-to-head"]
    gap = float(model._softplus(model.delta))
    print("\nLatent-score weights (+ favours home):")
    for nm, wj in zip(names, model.w):
        print(f"  {nm:<14} {wj:+.3f}")
    print(f"thresholds: away|draw at {model.theta0:+.3f}, draw|home at {model.theta0 + gap:+.3f}")


if __name__ == "__main__":
    main()
