import json
import math
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess
from train_mlp import MLPClassifierScratch

HERE = Path(__file__).resolve().parent

def get_match_year(date_str):
    try:
        return int(date_str[:4])
    except ValueError:
        return 1950

def main():
    print("=== Training Incremental MLP Neural Network ===")
    
    # 1. Load data
    data = load_and_preprocess()
    X_train = data["X_train"]
    y_train = data["y_train"]
    X_val = data["X_val"]
    y_val = data["y_val"]
    train_metadata = data["train_metadata"]
    val_metadata = data["val_metadata"]
    
    # Extract years for training samples
    train_years = np.array([get_match_year(r["date"]) for r in train_metadata])
    
    # 2. Instantiate MLP model
    model = MLPClassifierScratch(input_dim=4, hidden_dim=8, output_dim=3, l2_reg=1e-4)
    model.scaler = data["scaler"]
    
    print("\n--- Phase 1: Training by Decades (1950 to 1999) ---")
    decades = [1950, 1960, 1970, 1980, 1990]
    
    for dec in decades:
        mask = (train_years >= dec) & (train_years < dec + 10)
        X_dec = X_train[mask]
        y_dec = y_train[mask]
        
        if len(y_dec) == 0:
            continue
            
        print(f"Decade {dec}s | Match Count: {len(y_dec)} | Running 100 epochs...")
        # Train on this decade's slice
        model.fit(X_dec, y_dec, data["scaler"], epochs=100, lr=0.1, momentum=0.9)
        
    print("\n--- Phase 2: Training Annually (2000 to 2025) ---")
    years = list(range(2000, 2026))
    
    for yr in years:
        mask = train_years == yr
        X_yr = X_train[mask]
        y_yr = y_train[mask]
        
        if len(y_yr) == 0:
            continue
            
        # Run fewer epochs for annual updates (e.g. 20 epochs) to adapt without catastrophic forgetting
        print(f"Year {yr} | Match Count: {len(y_yr)} | Running 20 epochs...")
        model.fit(X_yr, y_yr, data["scaler"], epochs=20, lr=0.08, momentum=0.9)
        
    # Save the trained model
    model_path = HERE / "mlp_incremental_model.pkl"
    with open(model_path, "wb") as f:
        import pickle
        pickle.dump(model, f)
    print(f"\nIncremental Model saved to {model_path.name}")
    
    # 3. Predict and Validate on the 28 WC 2026 matches
    probas = model.predict_proba(X_val)
    preds = np.argmax(probas, axis=1)
    
    correct = 0
    print("\nValidation Results on WC 2026 played matches (Incremental MLP):")
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
    print(f"Incremental MLP Accuracy: {accuracy*100:.1f}% ({correct}/{len(y_val)} matches correct)")
    
    # Compare with standard batch MLP accuracy
    with open(HERE / "mlp_model.pkl", "rb") as f:
        std_model = pickle.load(f)
    std_acc = np.mean(std_model.predict(X_val) == y_val)
    print(f"Standard Batch MLP Accuracy: {std_acc*100:.1f}%")

if __name__ == "__main__":
    main()
