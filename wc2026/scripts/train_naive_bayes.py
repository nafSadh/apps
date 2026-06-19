import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "naive_bayes_model.pkl"

class GaussianNaiveBayes:
    def __init__(self, eps=1e-9):
        self.eps = eps
        self.priors = {}
        self.means = {}
        self.vars = {}
        self.scaler = None
        
    def fit(self, X, y, scaler):
        self.scaler = scaler
        n_samples, n_features = X.shape
        self.classes = np.unique(y)
        
        for c in self.classes:
            X_c = X[y == c]
            self.priors[c] = X_c.shape[0] / float(n_samples)
            self.means[c] = np.mean(X_c, axis=0)
            self.vars[c] = np.var(X_c, axis=0) + self.eps
            
    def _calculate_likelihood(self, class_idx, x):
        mean = self.means[class_idx]
        var = self.vars[class_idx]
        # Gaussian PDF log-likelihood
        numerator = np.exp(-((x - mean) ** 2) / (2 * var))
        denominator = np.sqrt(2 * np.pi * var)
        # Avoid zero division or log(0)
        prob = numerator / denominator
        prob = np.clip(prob, self.eps, None)
        return np.sum(np.log(prob))
        
    def predict_proba(self, X):
        probas = []
        for x in X:
            log_posteriors = []
            for c in self.classes:
                log_prior = np.log(self.priors[c])
                log_likelihood = self._calculate_likelihood(c, x)
                log_posteriors.append(log_prior + log_likelihood)
            
            # Use log-sum-exp trick to get normalized probabilities safely
            log_posteriors = np.array(log_posteriors)
            max_log = np.max(log_posteriors)
            exps = np.exp(log_posteriors - max_log)
            probs = exps / np.sum(exps)
            probas.append(probs)
        return np.array(probas)
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

def main():
    print("=== Training Gaussian Naive Bayes ===")
    data = load_and_preprocess()
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    # Instantiate and fit
    model = GaussianNaiveBayes()
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
    print(f"Naive Bayes Accuracy: {accuracy*100:.1f}% ({correct}/{len(y_val)} matches correct)")

if __name__ == "__main__":
    main()
