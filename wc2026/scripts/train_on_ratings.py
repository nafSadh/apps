import json
import math
import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
DATA_JSON_PATH = HERE.parent / "data.json"
MODEL_PATH = HERE / "best_meta_model.pkl"

class MulticlassLogisticRegression:
    def __init__(self, input_dim=3, output_dim=3, l2_reg=1e-2):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.l2_reg = l2_reg
        self.W = np.zeros((input_dim, output_dim))
        self.b = np.zeros((1, output_dim))
        
    def _softmax(self, Z):
        exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
        return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)
        
    def fit(self, X, y, epochs=500, lr=0.1):
        N = X.shape[0]
        Y_oh = np.zeros((N, self.output_dim))
        Y_oh[np.arange(N), y] = 1.0
        
        for epoch in range(epochs):
            Z = np.dot(X, self.W) + self.b
            A = self._softmax(Z)
            
            dZ = A - Y_oh
            dW = np.dot(X.T, dZ) / N + self.l2_reg * self.W
            db = np.sum(dZ, axis=0, keepdims=True) / N
            
            self.W -= lr * dW
            self.b -= lr * db
            
    def predict_proba(self, X):
        Z = np.dot(X, self.W) + self.b
        return self._softmax(Z)

def name_to_code(name, data_json):
    for code, t in data_json["teams"].items():
        if t["name"].lower().strip() == name.lower().strip():
            return code
    from prep_data import WC_INTL_NAMES
    return WC_INTL_NAMES.get(name)

def main():
    print("=== Training Optimal ML Meta-Model (Elo + Squad Value + Betting Odds) ===")
    
    # Load data.json and prep data
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        data_json = json.load(f)
        
    locked = {int(k): v for k, v in data_json["locked"].items()}
    fixtures = {int(f["no"]): f for f in data_json["fixtures"]}
    ratings = data_json["ratings"]
    squad = data_json.get("squad", {})
    
    prep_data = load_and_preprocess()
    val_metadata = prep_data["val_metadata"]
    y_val = prep_data["y_val"]
    
    # Extract features for all 28 played matches
    X_raw = []
    y = []
    
    for i, meta in enumerate(val_metadata):
        h_code = name_to_code(meta["home"], data_json)
        a_code = name_to_code(meta["away"], data_json)
        
        # Pre-tournament ratings
        rh, ra = ratings[h_code], ratings[a_code]
        sqh, sqa = squad.get(h_code, {}), squad.get(a_code, {})
        
        # Get squad values (€m)
        val_h = sqh.get("value", 10.0)
        val_a = sqa.get("value", 10.0)
        
        # Use chronologically computed Elo difference (meta["feat"][0])
        # alongside pre-tournament Squad log-val ratio and Betting odds ratio
        features = [
            meta["feat"][0],
            math.log(val_h) - math.log(val_a),
            math.log(rh.get("odds", 1000.0)) - math.log(ra.get("odds", 1000.0)) # Note: (log(odds_a) - log(odds_h)) matching odds ratio
        ]
        
        X_raw.append(features)
        y.append(y_val[i])
        
    X_raw = np.array(X_raw)
    y = np.array(y)
    N = len(y)
    
    # Fix features definition to match ablation study exactly:
    # index 0: Elo diff (meta["feat"][0])
    # index 4: math.log(val_h) - math.log(val_a)
    # index 5: math.log(odd_a) - math.log(odd_h)
    X_raw = []
    for i, meta in enumerate(val_metadata):
        h_code = name_to_code(meta["home"], data_json)
        a_code = name_to_code(meta["away"], data_json)
        
        # Pre-tournament ratings
        rh, ra = ratings[h_code], ratings[a_code]
        sqh, sqa = squad.get(h_code, {}), squad.get(a_code, {})
        val_h = sqh.get("value", 10.0)
        val_a = sqa.get("value", 10.0)
        
        odd_h = rh.get("odds", 1000.0)
        odd_a = ra.get("odds", 1000.0)
        
        features = [
            meta["feat"][0],
            math.log(val_h) - math.log(val_a),
            math.log(odd_a) - math.log(odd_h)
        ]
        X_raw.append(features)
        
    X_raw = np.array(X_raw)
    
    # Run Leave-One-Out Cross-Validation (LOOCV)
    print(f"Dataset contains {N} matches. Running Leave-One-Out Cross-Validation (LOOCV)...")
    
    best_margin_acc = 0.0
    best_margin = 0.0
    best_margin_correct = 0
    
    margins = np.linspace(0.0, 0.4, 41)
    
    for m in margins:
        correct = 0
        for i in range(N):
            X_train = np.delete(X_raw, i, axis=0)
            y_train = np.delete(y, i, axis=0)
            X_test = X_raw[i:i+1]
            y_test = y[i]
            
            # Standardize based on training fold
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            std[std == 0] = 1.0
            
            X_train_std = (X_train - mean) / std
            X_test_std = (X_test - mean) / std
            
            clf = MulticlassLogisticRegression(input_dim=3)
            clf.fit(X_train_std, y_train, epochs=450, lr=0.1)
            
            prob = clf.predict_proba(X_test_std)[0]
            p_h, p_d, p_a = prob
            
            # Decision rule
            if p_h - p_a > m:
                pick = 0
            elif p_a - p_h > m:
                pick = 2
            else:
                pick = 1 # Predict Draw
                
            if pick == y_test:
                correct += 1
                
        acc = correct / N
        if acc > best_margin_acc:
            best_margin_acc = acc
            best_margin = m
            best_margin_correct = correct
            
    print("-" * 70)
    print(f"Optimal Prediction Margin (H/A vs Draw): {best_margin:.2f}")
    print(f"Toss-up Aware LOOCV ML Accuracy: {best_margin_acc*100:.1f}% ({best_margin_correct}/{N} correct)")
    print("-" * 70)
    
    # Train on full dataset to inspect weights and save the final model
    mean = np.mean(X_raw, axis=0)
    std = np.std(X_raw, axis=0)
    std[std == 0] = 1.0
    
    X_std = (X_raw - mean) / std
    
    final_clf = MulticlassLogisticRegression(input_dim=3)
    final_clf.fit(X_std, y, epochs=500, lr=0.1)
    
    # Save parameters, mean, and std in pickle
    model_data = {
        "weights": final_clf.W.tolist(),
        "biases": final_clf.b.tolist(),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "margin": best_margin
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)
    print(f"Optimal model saved to {MODEL_PATH.name}")
    print("-" * 70)
    
    feature_names = ["Elo diff", "Squad log-val diff", "Betting odds ratio"]
    print("\nLearned Model Weights (Higher = pushes towards that outcome):")
    print("-" * 78)
    print(f"{'Feature Name':<20} | {'Home Win (H)':<15} | {'Draw (D)':<15} | {'Away Win (A)':<15}")
    print("-" * 78)
    for idx, name in enumerate(feature_names):
        w_h = final_clf.W[idx, 0]
        w_d = final_clf.W[idx, 1]
        w_a = final_clf.W[idx, 2]
        print(f"{name:<20} | {w_h:+.4f}         | {w_d:+.4f}         | {w_a:+.4f}")
    print("-" * 78)

if __name__ == "__main__":
    main()
