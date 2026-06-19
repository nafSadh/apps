"""Single CART decision tree (Gini impurity)."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import DecisionTreeClassifier
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training decision tree (CART) ===")
    d = load_and_preprocess()
    model = DecisionTreeClassifier(max_depth=6, min_samples_split=50).fit(
        d["X_train"], d["y_train"], d["scaler"])
    pickle.dump(model, open(HERE / "decision_tree_model.pkl", "wb"))
    print(f"saved decision_tree_model.pkl   (max_depth={model.max_depth})")
    per_match("Decision tree", model.predict_proba(d["X_val"]), d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
