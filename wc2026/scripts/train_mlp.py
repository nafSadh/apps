import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "mlp_model.pkl"

class MLPClassifierScratch:
    def __init__(self, input_dim=4, hidden_dim=8, output_dim=3, l2_reg=1e-4):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.l2_reg = l2_reg
        
        # Initialize weights (Glorot/Xavier normal)
        np.random.seed(42)
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((1, output_dim))
        
        self.scaler = None
        
    def _softmax(self, Z):
        # Subtract max for numerical stability
        exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
        return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)
        
    def forward(self, X):
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = np.maximum(0, Z1) # ReLU activation
        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self._softmax(Z2)
        return Z1, A1, Z2, A2
        
    def fit(self, X, y, scaler, epochs=1000, lr=0.15, momentum=0.9):
        self.scaler = scaler
        N = X.shape[0]
        
        # Convert y to one-hot encoding
        Y_oh = np.zeros((N, self.output_dim))
        Y_oh[np.arange(N), y] = 1.0
        
        # Momentum variables
        vW1 = np.zeros_like(self.W1)
        vb1 = np.zeros_like(self.b1)
        vW2 = np.zeros_like(self.W2)
        vb2 = np.zeros_like(self.b2)
        
        for epoch in range(1, epochs + 1):
            # Forward pass
            Z1, A1, Z2, A2 = self.forward(X)
            
            # Loss computation
            loss = -np.sum(Y_oh * np.log(np.clip(A2, 1e-15, 1.0))) / N
            loss += 0.5 * self.l2_reg * (np.sum(self.W1**2) + np.sum(self.W2**2))
            
            # Backward pass
            dZ2 = A2 - Y_oh
            dW2 = np.dot(A1.T, dZ2) / N + self.l2_reg * self.W2
            db2 = np.sum(dZ2, axis=0, keepdims=True) / N
            
            dA1 = np.dot(dZ2, self.W2.T)
            dZ1 = dA1 * (Z1 > 0) # Derivative of ReLU
            dW1 = np.dot(X.T, dZ1) / N + self.l2_reg * self.W1
            db1 = np.sum(dZ1, axis=0, keepdims=True) / N
            
            # Update weights with momentum
            vW1 = momentum * vW1 + lr * dW1
            vb1 = momentum * vb1 + lr * db1
            vW2 = momentum * vW2 + lr * dW2
            vb2 = momentum * vb2 + lr * db2
            
            self.W1 -= vW1
            self.b1 -= vb1
            self.W2 -= vW2
            self.b2 -= vb2
            
            if epoch % 100 == 0 or epoch == 1:
                # Compute training accuracy
                preds = np.argmax(A2, axis=1)
                acc = np.mean(preds == y)
                print(f"Epoch {epoch}/{epochs} | Loss: {loss:.4f} | Train Acc: {acc*100:.2f}%")
                
    def predict_proba(self, X):
        _, _, _, A2 = self.forward(X)
        return A2
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

def main():
    print("=== Training Neural Network (MLP) ===")
    data = load_and_preprocess()
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    val_metadata = data["val_metadata"]
    
    # Instantiate and fit
    model = MLPClassifierScratch(input_dim=4, hidden_dim=8, output_dim=3, l2_reg=1e-4)
    model.fit(X_train, y_train, data["scaler"], epochs=800, lr=0.12, momentum=0.9)
    
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
    print(f"Neural Network Accuracy: {accuracy*100:.1f}% ({correct}/{len(y_val)} matches correct)")

if __name__ == "__main__":
    main()
