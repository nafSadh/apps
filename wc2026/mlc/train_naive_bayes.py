"""Gaussian Naive Bayes."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import GaussianNaiveBayes
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training Gaussian Naive Bayes ===")
    d = load_and_preprocess()
    model = GaussianNaiveBayes().fit(d["X_train"], d["y_train"], d["scaler"])
    pickle.dump(model, open(HERE / "naive_bayes_model.pkl", "wb"))
    print("saved naive_bayes_model.pkl")
    per_match("Gaussian NB", model.predict_proba(d["X_val"]), d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
