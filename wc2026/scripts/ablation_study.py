import json
import math
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
DATA_JSON_PATH = HERE.parent / "data.json"

class MulticlassLogisticRegression:
    def __init__(self, input_dim, output_dim=3, l2_reg=1e-2):
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

def get_match_year(date_str):
    try:
        return int(date_str[:4])
    except ValueError:
        return 1950

def name_to_code(name, data_json):
    for code, t in data_json["teams"].items():
        if t["name"].lower().strip() == name.lower().strip():
            return code
    from prep_data import WC_INTL_NAMES
    return WC_INTL_NAMES.get(name)

def run_loocv(X_raw, y, feature_indices):
    # Slice the raw features to keep only selected indices
    X_sliced = X_raw[:, feature_indices]
    N = len(y)
    
    # We will search for the best margin threshold (0.0 to 0.4) under LOOCV
    best_acc = 0.0
    best_correct = 0
    best_m = 0.0
    
    margins = np.linspace(0.0, 0.4, 41)
    
    for m in margins:
        correct = 0
        for i in range(N):
            X_train = np.delete(X_sliced, i, axis=0)
            y_train = np.delete(y, i, axis=0)
            X_test = X_sliced[i:i+1]
            y_test = y[i]
            
            # Standardize based on training fold
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            std[std == 0] = 1.0
            
            X_train_std = (X_train - mean) / std
            X_test_std = (X_test - mean) / std
            
            clf = MulticlassLogisticRegression(input_dim=len(feature_indices))
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
        if acc > best_acc:
            best_acc = acc
            best_m = m
            best_correct = correct
            
    return best_acc, best_correct, best_m

def main():
    print("=== Running Feature Ablation Study ===")
    print("Evaluating feature subsets on 28 played matches using Softmax Regression (LOOCV)\n")
    
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
    
    # Rebuild the 8 candidate features for each validation match
    # Feature indices:
    # 0. Elo diff
    # 1. Home advantage
    # 2. Recent form diff (gd)
    # 3. H2H rate
    # 4. Squad log-value diff
    # 5. Betting odds ratio
    # 6. FIFA points diff
    # 7. Opta diff
    
    X_all = []
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
        
        # Historical match features (unstandardized from val_metadata)
        hist_feat = meta["feat"] # [Elo diff, home adv, form gd diff, H2H rate]
        
        features = [
            hist_feat[0], # Elo diff
            hist_feat[1], # Home adv
            hist_feat[2], # Recent form gd
            hist_feat[3], # H2H rate
            math.log(val_h) - math.log(val_a),
            math.log(odd_a) - math.log(odd_h),
            (rh["fifa"] - ra["fifa"]) / 100.0,
            (rh.get("opta", 0.0) - ra.get("opta", 0.0))
        ]
        X_all.append(features)
        
    X_all = np.array(X_all)
    
    # Define feature sets
    feature_sets = {
        "1. Raw Results (Elo + Home)": [0, 1],
        "2. Results + Recent Form": [0, 1, 2],
        "3. Results + Form + H2H": [0, 1, 2, 3],
        "4. Pre-Tournament Ratings (Squad + Odds + FIFA + Opta)": [4, 5, 6, 7],
        "5. Complete Stack (All 8 Features)": [0, 1, 2, 3, 4, 5, 6, 7],
        "6. High-Talent Features (Squad + Odds + Elo)": [0, 4, 5]
    }
    
    print("-" * 80)
    print(f"{'Feature Subset':<50} | {'Opt. Margin':<12} | {'Accuracy':<10}")
    print("-" * 80)
    
    for name, indices in feature_sets.items():
        acc, correct, m = run_loocv(X_all, y_val, indices)
        print(f"{name:<50} | {m:<12.2f} | {acc*100:.1f}% ({correct}/28)")
        
    print("-" * 80)

if __name__ == "__main__":
    main()
