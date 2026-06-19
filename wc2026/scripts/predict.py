import sys
import json
import math
import pickle
import numpy as np
from pathlib import Path
from prep_data import load_and_preprocess

HERE = Path(__file__).resolve().parent
DATA_JSON_PATH = HERE.parent / "data.json"
MODEL_PATH = HERE / "best_meta_model.pkl"

# Hardcoded mapping from update.py for name translation
WC_INTL_NAMES = {
    "Argentina": "ARG", "Spain": "ESP", "France": "FRA", "England": "ENG", "Portugal": "POR",
    "Brazil": "BRA", "Netherlands": "NED", "Germany": "GER", "West Germany": "GER", "Belgium": "BEL",
    "Croatia": "CRO", "Morocco": "MAR", "Colombia": "COL", "Mexico": "MEX", "Senegal": "SEN",
    "Uruguay": "URU", "United States": "USA", "Japan": "JPN", "Switzerland": "SUI", "Iran": "IRN",
    "Turkey": "TUR", "Türkiye": "TUR", "Ecuador": "ECU", "South Korea": "KOR", "Austria": "AUT",
    "Australia": "AUS", "Algeria": "ALG", "Egypt": "EGY", "Canada": "CAN", "Norway": "NOR",
    "Ivory Coast": "CIV", "Côte d'Ivoire": "CIV", "Panama": "PAN", "Sweden": "SWE", "Czech Republic": "CZE",
    "Paraguay": "PAR", "Scotland": "SCO", "Tunisia": "TUN", "DR Congo": "COD", "Zaïre": "COD", "Zaire": "COD",
    "Uzbekistan": "UZB", "Qatar": "QAT", "Iraq": "IRQ", "South Africa": "RSA", "Saudi Arabia": "KSA",
    "Jordan": "JOR", "Bosnia and Herzegovina": "BIH", "Cape Verde": "CPV", "Ghana": "GHA", "Haiti": "HAI",
    "Curaçao": "CUW", "Netherlands Antilles": "CUW", "New Zealand": "NZL"
}

def resolve_team(input_str, data_json):
    """
    Resolves a string (code or name) to a 3-letter team code and full name.
    """
    clean_str = input_str.strip().lower()
    
    # Check if direct 3-letter code
    for code, t in data_json["teams"].items():
        if code.lower() == clean_str:
            return code, t["name"]
            
    # Check if team name in data_json
    for code, t in data_json["teams"].items():
        if t["name"].lower().strip() == clean_str:
            return code, t["name"]
            
    # Check alias dictionary
    for name, code in WC_INTL_NAMES.items():
        if name.lower().strip() == clean_str:
            # Get canonical name from data.json if code exists
            if code in data_json["teams"]:
                return code, data_json["teams"][code]["name"]
            return code, name
            
    return None, None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/predict.py <Home Team> <Away Team>")
        print("Examples:")
        print("  python3 scripts/predict.py ARG FRA")
        print("  python3 scripts/predict.py \"Argentina\" \"France\"")
        sys.exit(1)
        
    home_input = sys.argv[1]
    away_input = sys.argv[2]
    
    # Load data.json
    if not DATA_JSON_PATH.exists():
        print(f"Error: {DATA_JSON_PATH} not found.")
        sys.exit(1)
        
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        data_json = json.load(f)
        
    home_code, home_name = resolve_team(home_input, data_json)
    away_code, away_name = resolve_team(away_input, data_json)
    
    if not home_code or not home_name:
        print(f"Error: Could not resolve home team input '{home_input}'.")
        sys.exit(1)
        
    if not away_code or not away_name:
        print(f"Error: Could not resolve away team input '{away_input}'.")
        sys.exit(1)
        
    if home_code == away_code:
        print("Error: Home and Away teams must be different.")
        sys.exit(1)
        
    # Load optimal meta-classifier model
    if not MODEL_PATH.exists():
        print(f"Error: {MODEL_PATH} not found. Please train it first.")
        sys.exit(1)
        
    with open(MODEL_PATH, "rb") as f:
        meta_model = pickle.load(f)
        
    W = np.array(meta_model["weights"])
    b = np.array(meta_model["biases"])
    mean = np.array(meta_model["mean"])
    std = np.array(meta_model["std"])
    margin = meta_model["margin"]
    
    # Load processed ratings and elo
    data = load_and_preprocess()
    elo_map = data["elo"]
    
    # Get Elo ratings (fall back to 1500.0)
    # Note that elo_map uses the full CSV name as key
    elo_h = elo_map.get(home_name, 1500.0)
    elo_a = elo_map.get(away_name, 1500.0)
    
    ratings = data_json["ratings"]
    squad = data_json.get("squad", {})
    
    # Get squad values and outright odds
    sqh = squad.get(home_code, {})
    sqa = squad.get(away_code, {})
    val_h = sqh.get("value", 10.0)
    val_a = sqa.get("value", 10.0)
    
    rh = ratings.get(home_code, {})
    ra = ratings.get(away_code, {})
    odd_h = rh.get("odds", 1000.0)
    odd_a = ra.get("odds", 1000.0)
    
    # Prepare raw features:
    # 0. Elo diff: (elo_h - elo_a) / 100.0
    # 1. Squad log-value diff: log(val_h) - log(val_a)
    # 2. Betting odds ratio: log(odds_a) - log(odds_h)
    elo_diff = (elo_h - elo_a) / 100.0
    squad_diff = math.log(val_h) - math.log(val_a)
    odds_ratio = math.log(odd_a) - math.log(odd_h)
    
    X_raw = np.array([elo_diff, squad_diff, odds_ratio])
    
    # Standardize
    X_std = (X_raw - mean) / std
    
    # Predict
    def softmax(Z):
        exp_Z = np.exp(Z - np.max(Z))
        return exp_Z / np.sum(exp_Z)
        
    prob = softmax(np.dot(X_std, W) + b)[0]
    p_h, p_d, p_a = prob
    
    # Verdict decision rule (highest probability)
    idx = np.argmax(prob)
    if idx == 0:
        verdict = f"{home_name} Win"
    elif idx == 1:
        verdict = "Draw"
    else:
        verdict = f"{away_name} Win"
        
    print(f"=== Optimal Meta-Classifier Prediction ===")
    print(f"Matchup: {home_name} ({home_code}) vs {away_name} ({away_code})")
    print(f"Elo Ratings: {home_name} {elo_h:.1f} | {away_name} {elo_a:.1f} (Diff: {elo_h - elo_a:+.1f})")
    print(f"Squad Values: {home_name} €{val_h:.1f}m | {away_name} €{val_a:.1f}m")
    print(f"Outright Betting Odds: {home_name} {odd_h:.1f} | {away_name} {odd_a:.1f}")
    print("-" * 50)
    print(f"Raw Features: Elo_diff={elo_diff:.4f}, Squad_diff={squad_diff:.4f}, Odds_ratio={odds_ratio:.4f}")
    print(f"Standardized Features: {X_std.tolist()}")
    print("-" * 50)
    print(f"Probabilities:")
    print(f"  * Home Win ({home_name}): {p_h*100:.2f}%")
    print(f"  * Draw:                  {p_d*100:.2f}%")
    print(f"  * Away Win ({away_name}): {p_a*100:.2f}%")
    print("-" * 50)
    print(f"Prediction Verdict: {verdict}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
