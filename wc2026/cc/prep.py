"""
cc/ — data prep for the numpy match-history Transformer.

Self-contained (reads ../scripts/intl-results.csv, never writes outside cc/).
One chronological, no-future-leakage pass over 150 years of internationals; for
every match we snapshot each side's last L games *before kickoff* as a sequence
of tokens, plus the 4 engineered static features the tabular models use.

KEY DIFFERENCE vs the scripts/ and mlc/ labs: we keep the integer `year` of every
sample so the trainer can run a CURRICULUM — bulk-pretrain on everything up to
2002, then walk forward one year at a time (train-on-past / test-on-next-year),
which yields a backtest over *thousands* of matches instead of 20.

Token schema is built to grow (xG, lineups, club rows) — see cc/README.md.

Output: cc/seq.npz, cc/meta.json
"""
import csv, json, math
from datetime import date
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE.parent / "scripts" / "intl-results.csv"   # read-only

WARM_YEAR = 1960          # keep decades of pre-2002 history for the curriculum
WC_CUTOFF = "2026-06-11"  # WC2026 group games (final headline eval)
SEQ_LEN = 12
K, HOME_ADV, FORM_N = 30, 65, 5
NUM_FIELDS = ["was_home", "neutral", "goals_for", "goals_against", "recency_log"]
PAD, WIN, DRAW, LOSS = 0, 1, 2, 3


def _d(s):
    y, m, dd = s.split("-"); return date(int(y), int(m), int(dd))


def load_matches():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.reader(f); h = next(r)
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
            rows.append({"date": row[ci["date"]].strip(),
                         "home": row[ci["home_team"]].strip(),
                         "away": row[ci["away_team"]].strip(),
                         "hs": hs, "as": as_,
                         "neutral": row[ci["neutral"]].strip().upper() == "TRUE"})
    rows.sort(key=lambda m: m["date"])
    return rows


def build():
    matches = load_matches()
    teams = sorted({t for m in matches for t in (m["home"], m["away"])})
    vocab = {t: i + 1 for i, t in enumerate(teams)}          # 0 = pad
    V = len(vocab)

    elo, last, h2h, hist = {}, {}, {}, {}

    def E(t): return elo.get(t, 1500.0)
    def form_gd(t):
        a = last.get(t, []); return sum(a) / len(a) if a else 0.0

    def snapshot(team, cur):
        seq = hist.get(team, [])[-SEQ_LEN:]
        opp = np.zeros(SEQ_LEN, np.int32); res = np.zeros(SEQ_LEN, np.int32)
        num = np.zeros((SEQ_LEN, len(NUM_FIELDS)), np.float32); mask = np.zeros(SEQ_LEN, np.float32)
        for i, tok in enumerate(seq):
            slot = SEQ_LEN - len(seq) + i
            opp[slot] = tok["opp"]; res[slot] = tok["res"]
            days = (cur - tok["d"]).days
            num[slot] = [tok["wh"], tok["nt"], tok["gf"], tok["ga"], math.log1p(max(days, 0))]
            mask[slot] = 1.0
        return opp, res, num, mask

    cols = {k: [] for k in ("Ho", "Hr", "Hn", "Hm", "Ao", "Ar", "An", "Am",
                            "hid", "aid", "static", "y", "year", "isval", "dates")}
    for m in matches:
        home, away, cur = m["home"], m["away"], _d(m["date"])
        eh, ea = E(home), E(away); hadv = 0.0 if m["neutral"] else HOME_ADV
        key = f"{home}|{away}" if home < away else f"{away}|{home}"
        rec = h2h.get(key, {"x": 0, "d": 0, "y": 0}); tot = rec["x"] + rec["d"] + rec["y"]
        h2hv = ((rec["x"] - rec["y"] if home < away else rec["y"] - rec["x"]) / tot) if tot else 0.0
        static = [(eh - ea) / 100.0, 0.0 if m["neutral"] else 1.0,
                  form_gd(home) - form_gd(away), h2hv]
        y = 0 if m["hs"] > m["as"] else (1 if m["hs"] == m["as"] else 2)

        if cur.year >= WARM_YEAR:
            ho, hr, hn, hm = snapshot(home, cur); ao, ar, an, am = snapshot(away, cur)
            cols["Ho"].append(ho); cols["Hr"].append(hr); cols["Hn"].append(hn); cols["Hm"].append(hm)
            cols["Ao"].append(ao); cols["Ar"].append(ar); cols["An"].append(an); cols["Am"].append(am)
            cols["hid"].append(vocab[home]); cols["aid"].append(vocab[away])
            cols["static"].append(static); cols["y"].append(y); cols["year"].append(cur.year)
            cols["isval"].append(m["date"] >= WC_CUTOFF); cols["dates"].append(m["date"])

        # chronological state updates (AFTER recording the row — no leakage)
        exp = 1.0 / (1.0 + 10.0 ** (-((eh - ea + hadv) / 400.0)))
        sc = 1.0 if m["hs"] > m["as"] else (0.5 if m["hs"] == m["as"] else 0.0)
        mov = math.log(abs(m["hs"] - m["as"]) + 1.0)
        elo[home] = eh + K * mov * (sc - exp); elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))
        last.setdefault(home, []).append(m["hs"] - m["as"]); last[home][:] = last[home][-FORM_N:]
        last.setdefault(away, []).append(m["as"] - m["hs"]); last[away][:] = last[away][-FORM_N:]
        rh = h2h.setdefault(key, {"x": 0, "d": 0, "y": 0})
        if m["hs"] == m["as"]: rh["d"] += 1
        elif (m["hs"] > m["as"]) == (home < away): rh["x"] += 1
        else: rh["y"] += 1
        rf = lambda gf, ga: WIN if gf > ga else (DRAW if gf == ga else LOSS)
        hist.setdefault(home, []).append({"opp": vocab[away], "res": rf(m["hs"], m["as"]),
            "wh": 1.0, "nt": float(m["neutral"]), "gf": float(m["hs"]), "ga": float(m["as"]), "d": cur})
        hist.setdefault(away, []).append({"opp": vocab[home], "res": rf(m["as"], m["hs"]),
            "wh": 0.0, "nt": float(m["neutral"]), "gf": float(m["as"]), "ga": float(m["hs"]), "d": cur})

    static = np.array(cols["static"], np.float32)
    year = np.array(cols["year"], np.int32)
    cont = [0, 2, 3]
    pre = year <= 2002                               # fit scaler on the pretrain era only (no leakage)
    mean = static[pre][:, cont].mean(axis=0); std = static[pre][:, cont].std(axis=0); std[std == 0] = 1.0
    static[:, cont] = (static[:, cont] - mean) / std

    np.savez_compressed(HERE / "seq.npz",
        home_opp=np.array(cols["Ho"]), home_res=np.array(cols["Hr"]),
        home_num=np.array(cols["Hn"]), home_mask=np.array(cols["Hm"]),
        away_opp=np.array(cols["Ao"]), away_res=np.array(cols["Ar"]),
        away_num=np.array(cols["An"]), away_mask=np.array(cols["Am"]),
        home_id=np.array(cols["hid"], np.int32), away_id=np.array(cols["aid"], np.int32),
        static=static, y=np.array(cols["y"], np.int64), year=year,
        is_val=np.array(cols["isval"], bool), dates=np.array(cols["dates"]))
    meta = {"vocab": vocab, "n_teams": V, "seq_len": SEQ_LEN, "num_fields": NUM_FIELDS,
            "static_fields": ["elo_diff", "home_adv", "form_gd", "h2h_rate"],
            "scaler": {"cont_idx": cont, "mean": mean.tolist(), "std": std.tolist()},
            "config": {"warm_year": WARM_YEAR, "wc_cutoff": WC_CUTOFF, "K": K,
                       "home_adv": HOME_ADV, "form_n": FORM_N},
            "counts": {"total": len(year), "pretrain<=2002": int((year <= 2002).sum()),
                       "walkforward>2002": int((year > 2002).sum()), "wc2026": int(np.array(cols["isval"]).sum())}}
    json.dump(meta, open(HERE / "meta.json", "w"), indent=2)
    yr_hist = {int(y): int((year == y).sum()) for y in [1970, 1980, 1990, 2000, 2010, 2020, 2024, 2025, 2026]}
    print(f"teams={V}  total seqs={len(year)}  (<=2002: {(year<=2002).sum()}, >2002: {(year>2002).sum()}, WC2026: {np.array(cols['isval']).sum()})")
    print(f"year span {year.min()}-{year.max()}; sample counts {yr_hist}")
    print("saved cc/seq.npz + cc/meta.json")


if __name__ == "__main__":
    build()
