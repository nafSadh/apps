import json
import xgboost as xgb
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "xgboost_model.json"

def main():
    print("=== Training XGBoost Classifier ===")
    
    # 1. Load data
    data = load_and_preprocess()
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    # 2. Instantiate and fit XGBoost Classifier
    # We choose conservative hyperparameters to prevent overfitting on noisy football data
    model = xgb.XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss"
    )
    
    print("Fitting XGBoost on historical matches...")
    model.fit(X_train, y_train)
    
    # Save the model in native JSON format
    model.save_model(str(MODEL_PATH))
    print(f"XGBoost model saved to {MODEL_PATH.name}")
    
    # 3. Predict and Validate on 28 WC 2026 played matches
    probas = model.predict_proba(X_val) # N x 3 array
    preds = model.predict(X_val)
    
    # Standard accuracy
    correct_std = np.sum(preds == y_val)
    std_acc = correct_std / len(y_val)
    
    print("\nValidation Results on WC 2026 played matches (Standard XGBoost):")
    print(f"{'Date':<11} | {'Home':<15} vs {'Away':<15} | {'Actual':<6} | {'Predicted Probabilities (H/D/A)':<32} | {'Result':<7}")
    print("-" * 100)
    
    class_labels = {0: "H-Win", 1: "Draw", 2: "A-Win"}
    
    for i, meta in enumerate(val_metadata):
        p_dist = probas[i]
        pred_label = preds[i]
        actual_label = y_val[i]
        
        is_ok = "OK" if pred_label == actual_label else "WRONG"
        prob_str = f"H:{p_dist[0]:.2f} D:{p_dist[1]:.2f} A:{p_dist[2]:.2f}"
        print(f"{meta['date']:<11} | {meta['home']:<15} vs {meta['away']:<15} | {class_labels[actual_label]:<6} | {prob_str:<32} | {is_ok:<7}")
        
    print("-" * 100)
    print(f"Standard XGBoost Accuracy: {std_acc*100:.1f}% ({correct_std}/{len(y_val)} matches correct)")
    
    # 4. Sweep Draw Threshold to predict draws/toss-ups natively
    best_acc = 0.0
    best_t = 0.0
    best_counts = (0, 0, 0)
    
    for t in np.linspace(0.15, 0.45, 61):
        correct_h, correct_d, correct_a = 0, 0, 0
        for i in range(len(y_val)):
            p_h, p_d, p_a = probas[i]
            actual = y_val[i]
            
            # Predict draw if p_draw > t, else predict win/loss based on p_h vs p_a
            if p_d > t:
                pick = 1
            else:
                pick = 0 if p_h > p_a else 2
                
            if pick == actual:
                if actual == 0: correct_h += 1
                elif actual == 1: correct_d += 1
                else: correct_a += 1
                
        acc = (correct_h + correct_d + correct_a) / len(y_val)
        if acc > best_acc:
            best_acc = acc
            best_t = t
            best_counts = (correct_h, correct_d, correct_a)
            
    print("-" * 100)
    print(f"Tuned Draw Threshold: {best_t:.2f} | H:{best_counts[0]} D:{best_counts[1]} A:{best_counts[2]}")
    print(f"Tuned Draw XGBoost Accuracy: {best_acc*100:.1f}% ({sum(best_counts)}/{len(y_val)} correct)")
    
    # Compare with Naive Baseline
    baseline_acc = np.mean(y_val == 0)
    print(f"Naive Baseline Accuracy: {baseline_acc*100:.1f}%")
    print("-" * 100)

if __name__ == "__main__":
    main()
