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
DATA_PATH = HERE.parent / "data.json"

def main():
    # Load data.json
    data_json = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    locked = {int(k): v for k, v in data_json["locked"].items()}
    fixtures = {f["no"]: f for f in data_json["fixtures"]}
    ratings = data_json["ratings"]
    h2h = data_json["h2h"]
    form_years = data_json["formYears"]
    squad = data_json.get("squad", {})

    # 1. Evaluate Simulation Models with the 40-60% Toss-up Rule
    def zscores(raw):
        vals = list(raw.values())
        mean = sum(vals) / len(vals)
        variance = sum((x - mean) ** 2 for x in vals) / len(vals)
        std = math.sqrt(variance) if variance > 0 else 1.0
        return {k: (v - mean) / std for k, v in raw.items()}
        
    def r_raw(method):
        out = {}
        for c, r in ratings.items():
            if method == "fifa":
                out[c] = r["fifa"]
            elif method == "elo":
                out[c] = r["elo"]
            elif method == "odds":
                out[c] = -math.log(r["odds"] or 1000.0)
            elif method == "opta":
                out[c] = math.log((r["opta"] or 0.01) + 0.02)
        return out

    Z_fifa = zscores(r_raw("fifa"))
    Z_elo = zscores(r_raw("elo"))
    Z_odds = zscores(r_raw("odds"))
    Z_opta = zscores(r_raw("opta"))
    Z_blend = {c: (Z_fifa[c] + Z_elo[c] + Z_odds[c] + Z_opta[c]) / 4.0 for c in ratings}
    
    squad_raw = {c: math.log(sq["value"]) for c, sq in squad.items() if sq.get("value", 0) > 0}
    Z_squad = zscores(squad_raw)
    
    Z_form = form_z = zscores({c: sum(3 if ch == "W" else 1 if ch == "D" else 0 for ch in ratings[c]["form"][:5]) / 5.0 for c in ratings})

    def zmap(z):
        return 66.0 + 9.0 * max(-2.3, min(2.3, z or 0.0))
        
    def method_strength(c, method):
        if method == "form":
            z = 0.7 * Z_form.get(c, 0.0) + 0.3 * Z_elo.get(c, 0.0)
        elif method == "h2h":
            z = Z_elo.get(c, 0.0)
        elif method == "fifa":
            z = Z_fifa.get(c, 0.0)
        elif method == "odds":
            z = Z_odds.get(c, 0.0)
        elif method == "opta":
            z = Z_opta.get(c, 0.0)
        elif method == "squad":
            z = Z_squad.get(c, Z_blend.get(c, 0.0))
        else: # blend
            z = Z_blend.get(c, 0.0)
        return zmap(z)

    def p_beat(a, b, method):
        if method == "h2h":
            opps = h2h.get(a, {})
            r = opps.get(b)
            if r and r.get("p", 0) > 0:
                return (r.get("w", 0) + 0.5 * r.get("d", 0)) / r.get("p", 0)
        return 1.0 / (1.0 + math.pow(10.0, -(method_strength(a, method) - method_strength(b, method)) / 13.0))

    sim_models = ["blend", "fifa", "elo", "odds", "opta", "squad", "form", "h2h"]
    sim_accuracies = {}

    print("=== Simulation Models (40-60% Toss-up = Draw Rule) ===")
    print("-" * 80)
    print(f"{'Model Name':<20} | {'Correct H':<10} | {'Correct D':<10} | {'Correct A':<10} | {'Total Correct':<15} | {'Accuracy':<10}")
    print("-" * 80)

    for m in sim_models:
        correct_h, correct_d, correct_a = 0, 0, 0
        total_correct = 0
        
        for no, score in locked.items():
            f = fixtures[no]
            hg, ag = score[0], score[1]
            actual = "H" if hg > ag else "A" if hg < ag else "D"
            
            p = p_beat(f["home"], f["away"], m)
            
            # 40-60% Toss-up Rule
            if p > 0.6:
                pick = "H"
            elif p < 0.4:
                pick = "A"
            else:
                pick = "D"
                
            if pick == actual:
                total_correct += 1
                if actual == "H":
                    correct_h += 1
                elif actual == "D":
                    correct_d += 1
                else:
                    correct_a += 1
                    
        acc = total_correct / len(locked)
        sim_accuracies[m] = acc
        print(f"{m.capitalize():<20} | {correct_h:<10} | {correct_d:<10} | {correct_a:<10} | {total_correct:<15} | {acc*100:.1f}%")
        
    print("-" * 80)
    print(f"Total validation matches: {len(locked)} (consisting of 10 H-wins, 8 Draws, 2 A-wins)\n")

    # 2. Evaluate ML Models with Optimized Probability Thresholds
    print("=== ML Models (Predicting Win / Draw / Loss) ===")
    
    # Load data from prep_data
    prep_data = load_and_preprocess()
    X_val = prep_data["X_val"]
    y_val = prep_data["y_val"] # 0 = H, 1 = D, 2 = A
    val_metadata = prep_data["val_metadata"]
    
    ml_files = {
        "K-Nearest Neighbors": "knn",
        "Gaussian Naive Bayes": "naive_bayes",
        "Decision Tree (CART)": "decision_tree",
        "Neural Network (MLP)": "mlp"
    }

    print("-" * 85)
    print(f"{'Model Name':<22} | {'Opt. Thresh':<12} | {'Correct H':<10} | {'Correct D':<10} | {'Correct A':<10} | {'Accuracy':<10}")
    print("-" * 85)

    for display_name, file_prefix in ml_files.items():
        with open(HERE / f"{file_prefix}_model.pkl", "rb") as f:
            model = pickle.load(f)
            
        probas = model.predict_proba(X_val) # N x 3 array
        
        # We find the threshold t for p_home and p_away that maximizes accuracy.
        # Rule: Predict H if p_home > t, A if p_away > t, else D.
        # (If both are > t, choose the larger one)
        best_acc = 0.0
        best_t = 0.0
        best_counts = (0, 0, 0)
        
        for t in np.linspace(0.3, 0.6, 61):
            correct_h, correct_d, correct_a = 0, 0, 0
            total_correct = 0
            
            for i in range(len(y_val)):
                p_h, p_d, p_a = probas[i]
                actual = y_val[i]
                
                # Apply decision rule
                if p_h > t and p_h >= p_a:
                    pick = 0
                elif p_a > t and p_a > p_h:
                    pick = 2
                else:
                    pick = 1 # Draw / Toss-up fallback
                    
                if pick == actual:
                    total_correct += 1
                    if actual == 0:
                        correct_h += 1
                    elif actual == 1:
                        correct_d += 1
                    else:
                        correct_a += 1
                        
            acc = total_correct / len(y_val)
            if acc > best_acc:
                best_acc = acc
                best_t = t
                best_counts = (correct_h, correct_d, correct_a)
                
        h, d, a = best_counts
        tot = h + d + a
        print(f"{display_name:<22} | {best_t:<12.2f} | {h:<10} | {d:<10} | {a:<10} | {best_acc*100:.1f}%")
        
    print("-" * 85)

if __name__ == "__main__":
    main()
