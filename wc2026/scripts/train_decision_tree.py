import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "decision_tree_model.pkl"

class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, probs=None, is_leaf=False):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.probs = probs
        self.is_leaf = is_leaf

class DecisionTreeClassifierScratch:
    def __init__(self, max_depth=5, min_samples_split=20):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        self.scaler = None
        
    def _gini(self, y):
        n = len(y)
        if n == 0:
            return 0.0
        counts = np.bincount(y, minlength=3)
        probs = counts / n
        return 1.0 - np.sum(probs ** 2)
        
    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        if n_samples < self.min_samples_split:
            return None, None
            
        best_gini = 999.0
        best_feat = None
        best_thresh = None
        
        current_gini = self._gini(y)
        
        for feat in range(n_features):
            # For continuous/numerical features, check quantiles to make it fast
            vals = X[:, feat]
            unique_vals = np.unique(vals)
            if len(unique_vals) > 50:
                # Continuous feature: evaluate percentiles
                thresholds = np.percentile(vals, np.linspace(2, 98, 40))
            else:
                thresholds = unique_vals
                
            for thresh in thresholds:
                left_mask = vals <= thresh
                right_mask = ~left_mask
                
                n_l, n_r = np.sum(left_mask), np.sum(right_mask)
                if n_l == 0 or n_r == 0:
                    continue
                    
                gini_l = self._gini(y[left_mask])
                gini_r = self._gini(y[right_mask])
                
                # Weighted Gini
                split_gini = (n_l / n_samples) * gini_l + (n_r / n_samples) * gini_r
                
                if split_gini < best_gini:
                    best_gini = split_gini
                    best_feat = feat
                    best_thresh = thresh
                    
        # Only split if we actually reduce impurity
        if best_gini < current_gini:
            return best_feat, best_thresh
        return None, None

    def _build_tree(self, X, y, depth=0):
        n_samples = X.shape[0]
        unique_classes = np.unique(y)
        
        # Calculate leaf probabilities
        counts = np.bincount(y, minlength=3)
        probs = counts / (n_samples if n_samples > 0 else 1.0)
        
        # Base cases: pure node, max depth, or too few samples
        if len(unique_classes) == 1 or depth >= self.max_depth or n_samples < self.min_samples_split:
            return DecisionTreeNode(probs=probs, is_leaf=True)
            
        feat, thresh = self._best_split(X, y)
        if feat is None:
            return DecisionTreeNode(probs=probs, is_leaf=True)
            
        # Split and recurse
        left_mask = X[:, feat] <= thresh
        right_mask = ~left_mask
        
        left_node = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_node = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return DecisionTreeNode(feature=feat, threshold=thresh, left=left_node, right=right_node)

    def fit(self, X, y, scaler):
        self.scaler = scaler
        self.root = self._build_tree(X, y)
        
    def _predict_one(self, node, x):
        if node.is_leaf:
            return node.probs
        if x[node.feature] <= node.threshold:
            return self._predict_one(node.left, x)
        else:
            return self._predict_one(node.right, x)
            
    def predict_proba(self, X):
        return np.array([self._predict_one(self.root, x) for x in X])
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

def main():
    print("=== Training Decision Tree (CART) ===")
    data = load_and_preprocess()
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    # Instantiate and fit
    model = DecisionTreeClassifierScratch(max_depth=5, min_samples_split=50)
    model.fit(X_train, y_train, data["scaler"])
    
    # Save the model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {MODEL_PATH.name}")
    
    # Predict and validate
    probas = model.predict_proba(X_val)
    preds = np.argmax(probas, axis=1)
    
    correct = 0
    print("\nValidation Results on WC 2026 played matches:")
    print(f"{'Date':<11} | {'Home':<15} vs {'Away':<15} | {'Actual':<6} | {'Predicted Probabilities (H/D/A)':<32} | {'Result':<7}")
    print("-" * 100)
    
    class_labels = {0: "H-Win", 1: "Draw", 2: "A-Win"}
    
    for i, meta in enumerate(val_metadata):
        p_dist = probas[i]
        pred_label = preds[i]
        actual_label = y_val[i]
        
        is_ok = "OK" if pred_label == actual_label else "WRONG"
        if pred_label == actual_label:
            correct += 1
            
        prob_str = f"H:{p_dist[0]:.2f} D:{p_dist[1]:.2f} A:{p_dist[2]:.2f}"
        print(f"{meta['date']:<11} | {meta['home']:<15} vs {meta['away']:<15} | {class_labels[actual_label]:<6} | {prob_str:<32} | {is_ok:<7}")
        
    accuracy = correct / len(y_val)
    print("-" * 100)
    print(f"Decision Tree Accuracy: {accuracy*100:.1f}% ({correct}/{len(y_val)} matches correct)")

if __name__ == "__main__":
    main()
