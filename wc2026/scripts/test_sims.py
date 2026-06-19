import json
import math
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "data.json"

def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    
    # 28 played matches
    locked = {int(k): v for k, v in data["locked"].items()}
    fixtures = {f["no"]: f for f in data["fixtures"]}
    ratings = data["ratings"]
    teams = data["teams"]
    h2h = data["h2h"]
    form_years = data["formYears"]
    
    # Replicate zscores
    def zscores(raw):
        vals = list(raw.values())
        mean = sum(vals) / len(vals)
        variance = sum((x - mean) ** 2 for x in vals) / len(vals)
        std = math.sqrt(variance) if variance > 0 else 1.0
        return {k: (v - mean) / std for k, v in raw.items()}
        
    def r_raw(method):
        out = {}
        for c, r in ratings.items():
            # RATING_KEYS: ("fifa", "elo", "odds", "opta", "form")
            # in ratings: r = {"fifa": float, "elo": float, "odds": float, "opta": float, "form": str}
            if method == "fifa":
                out[c] = r["fifa"]
            elif method == "elo":
                out[c] = r["elo"]
            elif method == "odds":
                out[c] = -math.log(r["odds"] or 1000.0)
            elif method == "opta":
                out[c] = math.log((r["opta"] or 0.01) + 0.02)
        return out

    # Build Z-scores
    Z_fifa = zscores(r_raw("fifa"))
    Z_elo = zscores(r_raw("elo"))
    Z_odds = zscores(r_raw("odds"))
    Z_opta = zscores(r_raw("opta"))
    
    Z_blend = {}
    for c in ratings:
        Z_blend[c] = (Z_fifa[c] + Z_elo[c] + Z_odds[c] + Z_opta[c]) / 4.0
        
    # Squad value € log Z-score
    # In index.html squad data is not fully parsed from data.json?
    # Wait, let's see if squad is in data.json
    # data.json has: squad: {code: {value, eafc}}
    squad = data.get("squad", {})
    squad_raw = {}
    eafc_raw = {}
    for c in ratings:
        sq = squad.get(c, {})
        val = sq.get("value", 0)
        eafc = sq.get("eafc", 0)
        if val > 0:
            squad_raw[c] = math.log(val)
        if eafc > 0:
            eafc_raw[c] = eafc
            
    Z_squad_val = zscores(squad_raw)
    Z_squad_eafc = zscores(eafc_raw)
    Z_squad_both = {}
    for c in ratings:
        Z_squad_both[c] = ((Z_squad_val.get(c, 0.0)) + (Z_squad_eafc.get(c, 0.0))) / 2.0
        
    # Form Z-scores
    def form_ppg(c, N_str):
        if N_str.startswith("y"):
            r = form_years.get(c, {}).get(N_str)
            if r:
                p = r.get("w", 0) + r.get("d", 0) + r.get("l", 0)
                return (r.get("w", 0) * 3.0 + r.get("d", 0)) / p if p > 0 else 1.0
            N_str = "11"
        num = max(1, int(N_str))
        f_str = ratings[c]["form"]
        n = min(num, len(f_str))
        if not n:
            return 1.0
        pts = sum(3 if ch == "W" else 1 if ch == "D" else 0 for ch in f_str[:n])
        return pts / n
        
    def form_z(N_str):
        raw = {c: form_ppg(c, N_str) for c in ratings}
        return zscores(raw)
        
    Z_form = form_z("5")
    
    # zmap function
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
            z = Z_squad_val.get(c, Z_blend.get(c, 0.0))
        else: # blend
            z = Z_blend.get(c, 0.0)
        return zmap(z)
        
    # Head-to-Head tally
    def h2h_tally(a, b):
        # ratings pairwise H2H
        opps = h2h.get(a, {})
        r = opps.get(b)
        if not r or r.get("p", 0) == 0:
            return None
        return {
            "w": r.get("w", 0),
            "d": r.get("d", 0),
            "l": r.get("l", 0),
            "n": r.get("p", 0)
        }
        
    def p_beat(a, b, method):
        if method == "h2h":
            t = h2h_tally(a, b)
            if t and t["n"] > 0:
                return (t["w"] + 0.5 * t["d"]) / t["n"]
        return 1.0 / (1.0 + math.pow(10.0, -(method_strength(a, method) - method_strength(b, method)) / 13.0))

    # Evaluate models on 28 played matches
    models = ["blend", "fifa", "elo", "odds", "opta", "squad", "form", "h2h"]
    
    print(f"Total played matches: {len(locked)}")
    print("-" * 80)
    print(f"{'Model':<15} | {'Pushes':<8} | {'Correct (✓)':<12} | {'Wrong (✗)':<10} | {'Hit Rate (index.html)':<22} | {'Standard 3-Class Acc':<20}")
    print("-" * 80)
    
    for m in models:
        ok = 0
        miss = 0
        push = 0
        
        # Standard accuracy metrics (treating H, D, A as absolute classes)
        std_correct = 0
        std_total = len(locked)
        
        for no, score in sorted(locked.items()):
            f = fixtures[no]
            hg, ag = score[0], score[1]
            actual = "H" if hg > ag else "A" if hg < ag else "D"
            actual_y = 0 if hg > ag else 2 if hg < ag else 1
            
            p = p_beat(f["home"], f["away"], m)
            
            # Predict based on probability thresholds (index.html logic)
            pick = "H" if p > 0.6 else "A" if p < 0.4 else "D"
            res = "ok" if pick == actual else "push" if (pick == "D" or actual == "D") else "miss"
            
            if res == "ok":
                ok += 1
            elif res == "miss":
                miss += 1
            else:
                push += 1
                
            # Standard prediction: argmax probability
            # (H win if p > 0.5, Draw/Tossup if p around some value? No, the index.html models do not predict draw as argmax, they only output win probability p.
            # So if p > 0.5, predict H win, else predict A win. That means they never predict draw!)
            std_pick_y = 0 if p > 0.5 else 2
            # Wait, what if they draw? If it's a draw, it's incorrect.
            if std_pick_y == actual_y:
                std_correct += 1
                
        hit_rate = (ok / (ok + miss) * 100.0) if (ok + miss) > 0 else 0.0
        std_acc = (std_correct / std_total) * 100.0
        
        print(f"{m:<15} | {push:<8} | {ok:<12} | {miss:<10} | {hit_rate:.1f}% ({ok}/{ok+miss}){'':<6} | {std_acc:.1f}% ({std_correct}/{std_total})")

if __name__ == "__main__":
    main()
