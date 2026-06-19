"""
Build per-team match-history SEQUENCES for the transformer experiment.

Unlike the tabular models (which see 4 engineered numbers per match), the
transformer reads each team's recent match history as a sequence of tokens and
learns its own representation of form/strength. This script does a single
chronological pass over the international results and, for every match, snapshots
each side's last L matches *before kickoff* (no future leakage), alongside the
same 4 engineered static features the tabular models use (so the transformer can
fuse sequence + tabular signal and be compared fairly).

Output (saved next to this file):
    wc_sequences.npz   - all arrays (see SCHEMA below)
    vocab.json         - team -> id map + token schema + config + counts

TOKEN SCHEMA (extensible — richer sources slot in here later):
    categorical, embedded:
        opp_id   : opponent team id        (0 = pad)
        result   : 1=win 2=draw 3=loss      (0 = pad)  [from this team's view]
    numeric:
        was_home, neutral, goals_for, goals_against, recency_log
    >>> To add xG / shots / possession later: append columns to NUM_FIELDS in
        this file and to the numeric projection in train_transformer.py. Use a
        mask/`-1` sentinel for matches whose source lacks the field; do NOT drop
        rows for missing richness. See README.md ("Hunting richer data").
"""

import csv
import json
import math
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE.parent.parent / "scripts" / "intl-results.csv"   # read-only

# --- config ---
WARM_YEAR = 1990            # transformer era (lean + richer-data-friendly); WC2026 val is unaffected
CUTOFF = "2026-06-11"       # val = played matches on/after this (the WC2026 group games)
SEQ_LEN = 12                # history tokens per team
K, HOME_ADV, FORM_N = 30, 65, 5

NUM_FIELDS = ["was_home", "neutral", "goals_for", "goals_against", "recency_log"]
RESULT_PAD, RESULT_W, RESULT_D, RESULT_L = 0, 1, 2, 3


def _parse_date(s):
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def load_matches():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        h = next(r)
        ci = {n: h.index(n) for n in
              ("date", "home_team", "away_team", "home_score", "away_score", "neutral")}
        for row in r:
            if not row or len(row) <= max(ci.values()):
                continue
            hs, as_ = row[ci["home_score"]].strip(), row[ci["away_score"]].strip()
            if hs in ("", "NA") or as_ in ("", "NA"):
                continue
            try:
                hs, as_ = int(hs), int(as_)
            except ValueError:
                continue
            rows.append({
                "date": row[ci["date"]].strip(),
                "home": row[ci["home_team"]].strip(),
                "away": row[ci["away_team"]].strip(),
                "hs": hs, "as": as_,
                "neutral": row[ci["neutral"]].strip().upper() == "TRUE",
            })
    rows.sort(key=lambda m: m["date"])
    return rows


def build():
    matches = load_matches()

    # team vocabulary (1-indexed; 0 = pad)
    teams = sorted({t for m in matches for t in (m["home"], m["away"])})
    vocab = {t: i + 1 for i, t in enumerate(teams)}
    V = len(vocab)

    elo, last, h2h, hist = {}, {}, {}, {}     # hist[team] = list of past tokens (dicts)

    def E(t):
        return elo.get(t, 1500.0)

    def form_gd(t):
        a = last.get(t, [])
        return sum(a) / len(a) if a else 0.0

    def snapshot(team, cur_d):
        """last SEQ_LEN tokens for `team`, oldest->newest, as arrays."""
        seq = hist.get(team, [])[-SEQ_LEN:]
        opp = np.zeros(SEQ_LEN, np.int32)
        res = np.zeros(SEQ_LEN, np.int32)
        num = np.zeros((SEQ_LEN, len(NUM_FIELDS)), np.float32)
        mask = np.zeros(SEQ_LEN, np.float32)
        for i, tok in enumerate(seq):                 # left-pad: align to the right
            slot = SEQ_LEN - len(seq) + i
            opp[slot] = tok["opp_id"]
            res[slot] = tok["result"]
            days = (cur_d - tok["d"]).days
            num[slot] = [tok["was_home"], tok["neutral"], tok["gf"], tok["ga"],
                         math.log1p(max(days, 0))]
            mask[slot] = 1.0
        return opp, res, num, mask

    H_opp, H_res, H_num, H_mask = [], [], [], []
    A_opp, A_res, A_num, A_mask = [], [], [], []
    Hid, Aid, STATIC, Y, NEUTRAL, DATES = [], [], [], [], [], []
    is_val = []

    for m in matches:
        home, away, cur_d = m["home"], m["away"], _parse_date(m["date"])
        eh, ea = E(home), E(away)
        h_adv = 0.0 if m["neutral"] else HOME_ADV

        key = f"{home}|{away}" if home < away else f"{away}|{home}"
        rec = h2h.get(key, {"x": 0, "d": 0, "y": 0})
        tot = rec["x"] + rec["d"] + rec["y"]
        h2h_val = ((rec["x"] - rec["y"] if home < away else rec["y"] - rec["x"]) / tot) if tot else 0.0
        static = [(eh - ea) / 100.0, 0.0 if m["neutral"] else 1.0,
                  form_gd(home) - form_gd(away), h2h_val]

        y = 0 if m["hs"] > m["as"] else (1 if m["hs"] == m["as"] else 2)
        year = cur_d.year

        if year >= WARM_YEAR:
            ho, hr, hn, hm = snapshot(home, cur_d)
            ao, ar, an, am = snapshot(away, cur_d)
            H_opp.append(ho); H_res.append(hr); H_num.append(hn); H_mask.append(hm)
            A_opp.append(ao); A_res.append(ar); A_num.append(an); A_mask.append(am)
            Hid.append(vocab[home]); Aid.append(vocab[away])
            STATIC.append(static); Y.append(y); NEUTRAL.append(int(m["neutral"]))
            DATES.append(m["date"]); is_val.append(m["date"] >= CUTOFF)

        # ---- chronological state updates ----
        exp = 1.0 / (1.0 + 10.0 ** (-((eh - ea + h_adv) / 400.0)))
        sc = 1.0 if m["hs"] > m["as"] else (0.5 if m["hs"] == m["as"] else 0.0)
        mov = math.log(abs(m["hs"] - m["as"]) + 1.0)
        elo[home] = eh + K * mov * (sc - exp)
        elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))

        last.setdefault(home, []).append(m["hs"] - m["as"])
        last[home][:] = last[home][-FORM_N:]
        last.setdefault(away, []).append(m["as"] - m["hs"])
        last[away][:] = last[away][-FORM_N:]

        rh = h2h.setdefault(key, {"x": 0, "d": 0, "y": 0})
        if m["hs"] == m["as"]:
            rh["d"] += 1
        elif (m["hs"] > m["as"]) == (home < away):
            rh["x"] += 1
        else:
            rh["y"] += 1

        def res_for(gf, ga):
            return RESULT_W if gf > ga else (RESULT_D if gf == ga else RESULT_L)

        hist.setdefault(home, []).append(
            {"opp_id": vocab[away], "result": res_for(m["hs"], m["as"]),
             "was_home": 1.0, "neutral": float(m["neutral"]),
             "gf": float(m["hs"]), "ga": float(m["as"]), "d": cur_d})
        hist.setdefault(away, []).append(
            {"opp_id": vocab[home], "result": res_for(m["as"], m["hs"]),
             "was_home": 0.0, "neutral": float(m["neutral"]),
             "gf": float(m["as"]), "ga": float(m["hs"]), "d": cur_d})

    is_val = np.array(is_val, bool)
    static = np.array(STATIC, np.float32)
    # standardize static cols 0,2,3 on TRAIN rows only
    cont = [0, 2, 3]
    tr = ~is_val
    mean = static[tr][:, cont].mean(axis=0)
    std = static[tr][:, cont].std(axis=0)
    std[std == 0] = 1.0
    static[:, cont] = (static[:, cont] - mean) / std

    npz_path = HERE / "wc_sequences.npz"
    np.savez_compressed(
        npz_path,
        home_opp=np.array(H_opp), home_res=np.array(H_res),
        home_num=np.array(H_num), home_mask=np.array(H_mask),
        away_opp=np.array(A_opp), away_res=np.array(A_res),
        away_num=np.array(A_num), away_mask=np.array(A_mask),
        home_id=np.array(Hid, np.int32), away_id=np.array(Aid, np.int32),
        static=static, y=np.array(Y, np.int64),
        neutral=np.array(NEUTRAL, np.int32), is_val=is_val,
        dates=np.array(DATES),
    )

    meta = {
        "vocab": vocab,
        "n_teams": V,
        "seq_len": SEQ_LEN,
        "num_fields": NUM_FIELDS,
        "result_codes": {"pad": 0, "win": 1, "draw": 2, "loss": 3},
        "static_fields": ["elo_diff", "home_adv", "form_gd", "h2h_rate"],
        "static_scaler": {"cont_idx": cont, "mean": mean.tolist(), "std": std.tolist()},
        "config": {"warm_year": WARM_YEAR, "cutoff": CUTOFF, "seq_len": SEQ_LEN,
                   "K": K, "home_adv": HOME_ADV, "form_n": FORM_N},
        "counts": {"total": int(len(is_val)), "train": int(tr.sum()),
                   "val": int(is_val.sum())},
    }
    with open(HERE / "vocab.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"teams (vocab): {V}")
    print(f"sequences: {len(is_val)}  (train {int(tr.sum())} / val {int(is_val.sum())})")
    print(f"seq_len={SEQ_LEN}  num_fields={NUM_FIELDS}")
    print(f"saved {npz_path.name} ({npz_path.stat().st_size/1e6:.1f} MB) and vocab.json")


if __name__ == "__main__":
    build()
