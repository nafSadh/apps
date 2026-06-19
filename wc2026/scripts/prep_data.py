import csv
import math
import json
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "intl-results.csv"
DATA_JSON_PATH = HERE.parent / "data.json"

# Standard name-to-code mapping matching update.py
WC_INTL_NAMES = {
    "Argentina": "ARG", "Spain": "ESP", "France": "FRA", "England": "ENG", "Portugal": "POR",
    "Brazil": "BRA", "Netherlands": "NED", "Germany": "GER", "West Germany": "GER", "Belgium": "BEL",
    "Croatia": "CRO", "Morocco": "MAR", "Colombia": "COL", "Mexico": "MEX", "Senegal": "SEN",
    "Uruguay": "URU", "United States": "USA", "Japan": "JPN", "Switzerland": "SUI", "Iran": "IRN",
    "Turkey": "TUR", "Türkiye": "TUR", "Ecuador": "ECU", "Austria": "AUT", "South Korea": "KOR",
    "Australia": "AUS", "Algeria": "ALG", "Egypt": "EGY", "Canada": "CAN", "Norway": "NOR",
    "Ivory Coast": "CIV", "Côte d'Ivoire": "CIV", "Panama": "PAN", "Sweden": "SWE", "Czech Republic": "CZE",
    "Paraguay": "PAR", "Scotland": "SCO", "Tunisia": "TUN", "DR Congo": "COD", "Zaïre": "COD", "Zaire": "COD",
    "Uzbekistan": "UZB", "Qatar": "QAT", "Iraq": "IRQ", "South Africa": "RSA", "Saudi Arabia": "KSA",
    "Jordan": "JOR", "Bosnia and Herzegovina": "BIH", "Cape Verde": "CPV", "Ghana": "GHA", "Haiti": "HAI",
    "Curaçao": "CUW", "Netherlands Antilles": "CUW", "New Zealand": "NZL",
}

def load_and_preprocess(warm_year=1950, cutoff_date="2026-06-11", K=30, home_adv=65, form_n=5):
    # Load data.json to get locked scores and mappings
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as jf:
        data_json = json.load(jf)
        
    locked = {int(k): v for k, v in data_json.get("locked", {}).items()}
    fixtures = data_json.get("fixtures", [])
    
    # Map (home_code, away_code) -> fixture number
    pair_to_fixture = {}
    for f in fixtures:
        pair_to_fixture[(f["home"], f["away"])] = int(f["no"])
        
    # Map full names to code using data.json and aliases
    name_to_code = {}
    for code, t in data_json.get("teams", {}).items():
        name_to_code[t["name"].lower().strip()] = code
    for k, v in WC_INTL_NAMES.items():
        name_to_code[k.lower().strip()] = v
        
    # Parse the raw international results CSV
    matches = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        header = next(r)
        
        col_date = header.index("date")
        col_home = header.index("home_team")
        col_away = header.index("away_team")
        col_hs = header.index("home_score")
        col_as = header.index("away_score")
        col_neutral = header.index("neutral")
        
        for row in r:
            if not row or len(row) <= max(col_hs, col_as):
                continue
                
            date = row[col_date].strip()
            home_name = row[col_home].strip()
            away_name = row[col_away].strip()
            neutral = row[col_neutral].strip().upper() == "TRUE"
            
            # Resolve to WC codes if possible
            hc = name_to_code.get(home_name.lower())
            ac = name_to_code.get(away_name.lower())
            
            hs = None
            as_ = None
            
            # If it's on or after the World Cup starts, check data.json's locked scores
            if date >= cutoff_date and hc and ac:
                fixture_no = pair_to_fixture.get((hc, ac))
                if fixture_no in locked:
                    hs, as_ = locked[fixture_no]
            else:
                # Historical match: read from CSV
                hs_str = row[col_hs].strip()
                as_str = row[col_as].strip()
                if hs_str not in ("", "NA") and as_str not in ("", "NA"):
                    try:
                        hs = int(hs_str)
                        as_ = int(as_str)
                    except ValueError:
                        pass
                        
            if hs is None or as_ is None:
                continue # Skip future/incomplete matches
                
            matches.append({
                "date": date,
                "home": home_name,
                "away": away_name,
                "hs": hs,
                "as": as_,
                "neutral": neutral
            })
            
    # Sort matches chronologically
    matches.sort(key=lambda m: m["date"])
    
    elo = {}
    last = {}
    h2h = {}
    
    def get_elo(team):
        return elo.get(team, 1500.0)
        
    def get_form_gd(team):
        lst = last.get(team, [])
        if not lst:
            return 0.0
        return sum(lst) / len(lst)
        
    train_rows = []
    val_rows = []
    
    for m in matches:
        home, away = m["home"], m["away"]
        eh, ea = get_elo(home), get_elo(away)
        h_adv = 0.0 if m["neutral"] else home_adv
        
        # H2H calculations
        key = f"{home}|{away}" if home < away else f"{away}|{home}"
        rec = h2h.get(key, {'x': 0, 'd': 0, 'y': 0})
        tot = rec['x'] + rec['d'] + rec['y']
        if tot > 0:
            signed = rec['x'] - rec['y'] if home < away else rec['y'] - rec['x']
            h2h_val = signed / tot
        else:
            h2h_val = 0.0
            
        # Feature vector
        feat = [
            (eh - ea) / 100.0,
            0.0 if m["neutral"] else 1.0,
            get_form_gd(home) - get_form_gd(away),
            h2h_val
        ]
        
        # Target labels: 0 = H, 1 = D, 2 = A
        if m["hs"] > m["as"]:
            y = 0
        elif m["hs"] == m["as"]:
            y = 1
        else:
            y = 2
            
        row_data = {
            "date": m["date"],
            "home": home,
            "away": away,
            "feat": feat,
            "y": y,
            "score": (m["hs"], m["as"])
        }
        
        try:
            year = int(m["date"][:4])
        except ValueError:
            year = 0
            
        if year >= warm_year:
            if m["date"] < cutoff_date:
                train_rows.append(row_data)
            else:
                val_rows.append(row_data)
                
        # Update Elo
        exp = 1.0 / (1.0 + math.pow(10.0, -((eh - ea + h_adv) / 400.0)))
        sc = 1.0 if m["hs"] > m["as"] else (0.5 if m["hs"] == m["as"] else 0.0)
        mov = math.log(abs(m["hs"] - m["as"]) + 1.0)
        
        elo[home] = eh + K * mov * (sc - exp)
        elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))
        
        # Update recent form
        last.setdefault(home, []).append(m["hs"] - m["as"])
        if len(last[home]) > form_n:
            last[home].pop(0)
        last.setdefault(away, []).append(m["as"] - m["hs"])
        if len(last[away]) > form_n:
            last[away].pop(0)
            
        # Update H2H
        r_h2h = h2h.setdefault(key, {'x': 0, 'd': 0, 'y': 0})
        if m["hs"] == m["as"]:
            r_h2h['d'] += 1
        else:
            home_is_first = home < away
            home_won = m["hs"] > m["as"]
            if home_won == home_is_first:
                r_h2h['x'] += 1
            else:
                r_h2h['y'] += 1
                
    X_train_raw = np.array([r["feat"] for r in train_rows])
    y_train = np.array([r["y"] for r in train_rows])
    X_val_raw = np.array([r["feat"] for r in val_rows])
    y_val = np.array([r["y"] for r in val_rows])
    
    mean = np.mean(X_train_raw[:, [0, 2, 3]], axis=0)
    std = np.std(X_train_raw[:, [0, 2, 3]], axis=0)
    std[std == 0] = 1.0
    
    def standardize_features(X_raw):
        X_std = X_raw.copy()
        X_std[:, [0, 2, 3]] = (X_raw[:, [0, 2, 3]] - mean) / std
        return X_std
        
    X_train = standardize_features(X_train_raw)
    X_val = standardize_features(X_val_raw)
    
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "mean": mean,
        "std": std,
        "train_metadata": train_rows,
        "val_metadata": val_rows,
        "scaler": {
            "mean": mean.tolist(),
            "std": std.tolist()
        },
        "elo": elo,
        "last": last,
        "h2h": h2h
    }

if __name__ == "__main__":
    data = load_and_preprocess()
    print("Train size:", len(data["X_train"]))
    print("Val size (WC 2026 played matches):", len(data["X_val"]))
    for i, r in enumerate(data["val_metadata"]):
        print(f"Match {i+1}: {r['date']} {r['home']} vs {r['away']} | score: {r['score']} | label: {r['y']}")
