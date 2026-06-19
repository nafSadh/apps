"""k-Nearest Neighbours in the standardized 4-feature space."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import KNNClassifier
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training k-Nearest Neighbours ===")
    d = load_and_preprocess()
    model = KNNClassifier(k=25).fit(d["X_train"], d["y_train"], d["scaler"])
    pickle.dump(model, open(HERE / "knn_model.pkl", "wb"))
    print(f"saved knn_model.pkl   (k={model.k}, N={len(model.X_train)})")
    per_match("k-NN", model.predict_proba(d["X_val"]), d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
