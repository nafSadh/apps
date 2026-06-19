import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "knn_model.pkl"

class KNNClassifier:
    def __init__(self, k=25):
        self.k = k
        self.X_train = None
        self.y_train = None
        self.scaler = None
        
    def fit(self, X_train, y_train, scaler):
        self.X_train = X_train
        self.y_train = y_train
        self.scaler = scaler
        
    def predict_proba(self, X):
        probas = []
        for x in X:
            # Compute Euclidean distances to all training points
            dists = np.sqrt(np.sum((self.X_train - x) ** 2, axis=1))
            # Get indices of the k nearest neighbors
            nearest_idx = np.argsort(dists)[:self.k]
            # Get the classes of these neighbors
            classes = self.y_train[nearest_idx]
            # Count class frequencies
            counts = np.bincount(classes, minlength=3)
            # Normalize to get probabilities
            probas.append(counts / self.k)
        return np.array(probas)
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

def main():
    print("=== Training K-Nearest Neighbors ===")
    data = load_and_preprocess()
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    # Instantiate and fit
    k_val = 25
    model = KNNClassifier(k=k_val)
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
    print(f"KNN Accuracy: {accuracy*100:.1f}% ({correct}/{len(y_val)} matches correct)")

if __name__ == "__main__":
    main()
