import json
import math
import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

# Import classes to allow pickle loading
from train_knn import KNNClassifier
from train_naive_bayes import GaussianNaiveBayes
from train_decision_tree import DecisionTreeClassifierScratch, DecisionTreeNode
from train_mlp import MLPClassifierScratch

HERE = Path(__file__).resolve().parent
DATA_JSON_PATH = HERE.parent / "data.json"

class MulticlassLogisticRegression:
    def __init__(self, input_dim=7, output_dim=3, l2_reg=1e-2):
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

def main():
    print("=== Training Stacked ML Meta-Model (Historic Match + Ratings) ===")
    
    # 1. Load data.json and prep data
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        data_json = json.load(f)
        
    locked = {int(k): v for k, v in data_json["locked"].items()}
    fixtures = {int(f["no"]): f for f in data_json["fixtures"]}
    ratings = data_json["ratings"]
    squad = data_json.get("squad", {})
    
    prep_data = load_and_preprocess()
    X_val = prep_data["X_val"] # Historic features standardized
    y_val = prep_data["y_val"]
    val_metadata = prep_data["val_metadata"]
    
    # 2. Load the base ML models (trained on 46k historical matches)
    base_models = {}
    for name in ["knn", "naive_bayes", "decision_tree", "mlp"]:
        with open(HERE / f"{name}_model.pkl", "rb") as f:
            base_models[name] = pickle.load(f)
            
    # 3. Generate predictions of base models for the 28 played matches
    base_probs = {}
    for name, model in base_models.items():
        base_probs[name] = model.predict_proba(X_val) # N x 3
        
    # 4. Construct stacked features combining ML predictions and ratings
    X_stacked = []
    
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
        
        # Base model probabilities of Home Win
        p_knn = base_probs["knn"][i, 0]
        p_nb = base_probs["naive_bayes"][i, 0]
        p_dt = base_probs["decision_tree"][i, 0]
        p_mlp = base_probs["mlp"][i, 0]
        
        # Stacked feature vector:
        # 0. KNN H-prob
        # 1. NB H-prob
        # 2. DT H-prob
        # 3. MLP H-prob
        # 4. Squad log-value diff
        # 5. Betting odds ratio
        # 6. FIFA ranking diff
        features = [
            p_knn,
            p_nb,
            p_dt,
            p_mlp,
            math.log(val_h) - math.log(val_a),
            math.log(odd_a) - math.log(odd_h),
            (rh["fifa"] - ra["fifa"]) / 100.0
        ]
        X_stacked.append(features)
        
    X_stacked = np.array(X_stacked)
    N = len(y_val)
    
    # 5. Evaluate the Stacked Model using Leave-One-Out Cross-Validation (LOOCV)
    best_margin_acc = 0.0
    best_margin = 0.0
    best_margin_correct = 0
    
    margins = np.linspace(0.0, 0.4, 41)
    
    for m in margins:
        correct = 0
        for i in range(N):
            X_train = np.delete(X_stacked, i, axis=0)
            y_train = np.delete(y_val, i, axis=0)
            X_test = X_stacked[i:i+1]
            y_test = y_val[i]
            
            # Standardize continuous features based on training fold
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            std[std == 0] = 1.0
            
            X_train_std = (X_train - mean) / std
            X_test_std = (X_test - mean) / std
            
            # Train multiclass classifier
            clf = MulticlassLogisticRegression(input_dim=7, output_dim=3)
            clf.fit(X_train_std, y_train, epochs=400, lr=0.1)
            
            # Predict probability
            prob = clf.predict_proba(X_test_std)[0]
            p_h, p_d, p_a = prob
            
            # Decision rule
            if p_h - p_a > m:
                pick = 0
            elif p_a - p_h > m:
                pick = 2
            else:
                pick = 1 # Draw
                
            if pick == y_test:
                correct += 1
                
        acc = correct / N
        if acc > best_margin_acc:
            best_margin_acc = acc
            best_margin = m
            best_margin_correct = correct
            
    print("-" * 75)
    print(f"Optimal Prediction Margin (H/A vs Draw): {best_margin:.2f}")
    print(f"Stacked LOOCV ML Accuracy: {best_margin_acc*100:.1f}% ({best_margin_correct}/{N} correct)")
    print("-" * 75)
    
    # Train on full dataset to inspect feature weights
    mean = np.mean(X_stacked, axis=0)
    std = np.std(X_stacked, axis=0)
    std[std == 0] = 1.0
    X_stacked_std = (X_stacked - mean) / std
    
    clf = MulticlassLogisticRegression(input_dim=7, output_dim=3)
    clf.fit(X_stacked_std, y_val, epochs=500, lr=0.1)
    
    feature_names = [
        "ML KNN prob H",
        "ML Naive Bayes prob H",
        "ML Decision Tree prob H",
        "ML Neural Net prob H",
        "Squad log-val diff",
        "Betting odds ratio",
        "FIFA points diff"
    ]
    
    print("\nLearned Model Weights (Higher = pushes towards that outcome):")
    print("-" * 80)
    print(f"{'Feature Name':<25} | {'Home Win (H)':<15} | {'Draw (D)':<15} | {'Away Win (A)':<15}")
    print("-" * 80)
    for idx, name in enumerate(feature_names):
        w_h = clf.W[idx, 0]
        w_d = clf.W[idx, 1]
        w_a = clf.W[idx, 2]
        print(f"{name:<25} | {w_h:+.4f}         | {w_d:+.4f}         | {w_a:+.4f}")
    print("-" * 80)

def name_to_code(name, data_json):
    for code, t in data_json["teams"].items():
        if t["name"].lower().strip() == name.lower().strip():
            return code
    # Fallback to update.py aliases
    from prep_data import WC_INTL_NAMES
    return WC_INTL_NAMES.get(name)

if __name__ == "__main__":
    main()
