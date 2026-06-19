import json
import math
import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
DATA_JSON_PATH = HERE.parent / "data.json"

def name_to_code(name, data_json):
    for code, t in data_json["teams"].items():
        if t["name"].lower().strip() == name.lower().strip():
            return code
    from prep_data import WC_INTL_NAMES
    return WC_INTL_NAMES.get(name)


# Import classes to allow pickle loading
from train_knn import KNNClassifier
from train_naive_bayes import GaussianNaiveBayes
from train_decision_tree import DecisionTreeClassifierScratch, DecisionTreeNode
from train_mlp import MLPClassifierScratch

HERE = Path(__file__).resolve().parent

def load_model(name):
    path = HERE / f"{name}_model.pkl"
    with open(path, "rb") as f:
        return pickle.load(f)

def main():
    print("=== Verification of All Trained ML Models ===")
    
    # Load prep data
    data = load_and_preprocess()
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    models = {
        "K-Nearest Neighbors": "knn",
        "Gaussian Naive Bayes": "naive_bayes",
        "Decision Tree (CART)": "decision_tree",
        "Neural Network (MLP)": "mlp"
    }
    
    results = {}
    
    print("\nEvaluating models on WC 2026 validation matches...")
    print("-" * 65)
    print(f"{'Model Name':<25} | {'Trained Parameters/State':<25} | {'Accuracy':<10}")
    print("-" * 65)
    
    for display_name, file_prefix in models.items():
        try:
            model = load_model(file_prefix)
            preds = model.predict(X_val)
            acc = np.mean(preds == y_val)
            results[display_name] = acc
            
            # Simple state info
            if file_prefix == "knn":
                info = f"K={model.k}, N={len(model.X_train)}"
            elif file_prefix == "naive_bayes":
                info = f"Classes={len(model.priors)}"
            elif file_prefix == "decision_tree":
                info = f"Max Depth={model.max_depth}"
            elif file_prefix == "mlp":
                info = f"W1:{model.W1.shape}, W2:{model.W2.shape}"
            else:
                info = "N/A"
                
            print(f"{display_name:<25} | {info:<25} | {acc*100:.1f}%")
        except Exception as e:
            print(f"{display_name:<25} | Error loading or running: {str(e)}")
            
    print("-" * 65)
    
    # Load and evaluate best_meta_model.pkl
    try:
        meta_path = HERE / "best_meta_model.pkl"
        with open(meta_path, "rb") as f:
            meta_model = pickle.load(f)
            
        W = np.array(meta_model["weights"])
        b = np.array(meta_model["biases"])
        mean = np.array(meta_model["mean"])
        std = np.array(meta_model["std"])
        margin = meta_model["margin"]
        
        # Load ratings and squad values
        with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
            data_json = json.load(f)
        ratings = data_json["ratings"]
        squad = data_json.get("squad", {})
        
        X_meta = []
        for meta in val_metadata:
            h_code = name_to_code(meta["home"], data_json)
            a_code = name_to_code(meta["away"], data_json)
            
            rh = ratings[h_code]
            ra = ratings[a_code]
            sqh = squad.get(h_code, {})
            sqa = squad.get(a_code, {})
            
            val_h = sqh.get("value", 10.0)
            val_a = sqa.get("value", 10.0)
            odd_h = rh.get("odds", 1000.0)
            odd_a = ra.get("odds", 1000.0)
            
            features = [
                meta["feat"][0],
                math.log(val_h) - math.log(val_a),
                math.log(odd_a) - math.log(odd_h)
            ]
            X_meta.append(features)
            
        X_meta = np.array(X_meta)
        X_meta_std = (X_meta - mean) / std
        
        def softmax(Z):
            exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
            return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)
            
        probs = softmax(np.dot(X_meta_std, W) + b)
        
        meta_preds = np.argmax(probs, axis=1)
        meta_acc = np.mean(meta_preds == y_val)
        print(f"{'Optimal Meta-Classifier':<25} | {'Elo + Squad + Odds':<25} | {meta_acc*100:.1f}%")
    except Exception as e:
        print(f"{'Optimal Meta-Classifier':<25} | Error loading or running: {str(e)}")
        
    print("-" * 65)
    
    # Naive baseline (majority class)
    # The majority class in the training set
    y_train = data["y_train"]
    majority_class = np.argmax(np.bincount(y_train))
    baseline_acc = np.mean(y_val == majority_class)
    class_names = {0: "Home Win", 1: "Draw", 2: "Away Win"}
    print(f"{'Naive Baseline (' + class_names[majority_class] + ')':<25} | {'Majority Class':<25} | {baseline_acc*100:.1f}%")
    print("-" * 65)

if __name__ == "__main__":
    main()
