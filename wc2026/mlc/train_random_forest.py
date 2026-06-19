"""Random forest — bagged CART trees with per-split feature subsampling.
Captures feature interactions (e.g. big Elo edge AND at home) that the linear
models cannot."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import RandomForest
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training random forest ===")
    d = load_and_preprocess()
    model = RandomForest(n_trees=25, max_depth=8, min_samples_split=40,
                         max_features=2, sample_size=20000, seed=42).fit(
        d["X_train"], d["y_train"], d["scaler"])
    pickle.dump(model, open(HERE / "random_forest_model.pkl", "wb"))
    print(f"saved random_forest_model.pkl   ({model.n_trees} trees, depth {model.max_depth})")
    per_match("Random forest", model.predict_proba(d["X_val"]), d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
