"""Multi-layer perceptron — one hidden ReLU layer + softmax, SGD w/ momentum."""

import pickle
from pathlib import Path

from prep_data import load_and_preprocess
from models import MLPClassifier
from report import per_match

HERE = Path(__file__).resolve().parent


def main():
    print("=== Training MLP (neural net) ===")
    d = load_and_preprocess()
    model = MLPClassifier(input_dim=4, hidden_dim=8, epochs=800, lr=0.12)
    model.fit(d["X_train"], d["y_train"], d["scaler"], verbose=True)
    pickle.dump(model, open(HERE / "mlp_model.pkl", "wb"))
    print(f"saved mlp_model.pkl   (W1 {model.W1.shape}, W2 {model.W2.shape})")
    per_match("MLP (neural net)", model.predict_proba(d["X_val"]), d["val_metadata"], d["y_val"])


if __name__ == "__main__":
    main()
