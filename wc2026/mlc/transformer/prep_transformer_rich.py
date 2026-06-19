"""
RICH sequence builder — same idea as prep_transformer_data.py, but it reads the
unified corpus (data_sources/corpus.csv: internationals + club + xG) and adds xG
tokens. This is the transfer-learning / richer-signal path:

  * club matches give the encoder far more sequence data to learn form from,
  * xG fields add real per-match signal where a source provides it (masked where not).

Run order:
    cd ../data_sources && python3 build_corpus.py        # writes corpus.csv
    cd ../transformer  && python3 prep_transformer_rich.py
    python3 train_transformer.py --data rich --epochs 40 # (train_transformer reads num_fields from vocab)

Output: wc_sequences_rich.npz + vocab_rich.json — same array names/shapes as the
plain builder, so train_transformer.py consumes either (it reads the numeric
field count from the vocab file). Validation set = the played 2026 World Cup
matches (international rows on/after the cutoff).

NUM_FIELDS = was_home, neutral, goals_for, goals_against, recency_log,
             xg_for, xg_against, has_xg
"""

import csv
import json
import math
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent / "data_sources" / "corpus.csv"

WARM_YEAR = 2005            # club xG era; internationals included from here on
CUTOFF = "2026-06-11"
SEQ_LEN = 12
K, HOME_ADV, FORM_N = 30, 65, 5
NUM_FIELDS = ["was_home", "neutral", "goals_for", "goals_against", "recency_log",
              "xg_for", "xg_against", "has_xg"]


def _d(s):
    y, m, dd = s.split("-")
    return date(int(y), int(m), int(dd))


def load_corpus():
    if not CORPUS.exists():
        raise SystemExit("corpus.csv not found — run ../data_sources/build_corpus.py first.")
    rows = []
    with open(CORPUS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["home_score"] in ("", "NA") or r["away_score"] in ("", "NA"):
                continue
            rows.append(r)
    rows.sort(key=lambda r: r["date"])
    return rows


def _f(v):
    v = (v or "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def build():
    matches = load_corpus()
    teams = sorted({t for m in matches for t in (m["home"], m["away"])})
    vocab = {t: i + 1 for i, t in enumerate(teams)}
    V = len(vocab)

    elo, last, h2h, hist = {}, {}, {}, {}

    def E(t):
        return elo.get(t, 1500.0)

    def form_gd(t):
        a = last.get(t, [])
        return sum(a) / len(a) if a else 0.0

    def snap(team, cur):
        seq = hist.get(team, [])[-SEQ_LEN:]
        opp = np.zeros(SEQ_LEN, np.int32)
        res = np.zeros(SEQ_LEN, np.int32)
        num = np.zeros((SEQ_LEN, len(NUM_FIELDS)), np.float32)
        mask = np.zeros(SEQ_LEN, np.float32)
        for i, tok in enumerate(seq):
            slot = SEQ_LEN - len(seq) + i
            opp[slot] = tok["opp"]
            res[slot] = tok["res"]
            days = (cur - tok["d"]).days
            hx = tok["xf"] if tok["xf"] is not None else 0.0
            ax = tok["xa"] if tok["xa"] is not None else 0.0
            has = 1.0 if tok["xf"] is not None else 0.0
            num[slot] = [tok["wh"], tok["nu"], tok["gf"], tok["ga"],
                         math.log1p(max(days, 0)), hx, ax, has]
            mask[slot] = 1.0
        return opp, res, num, mask

    cols = {k: [] for k in ("ho", "hr", "hn", "hm", "ao", "ar", "an", "am",
                            "hid", "aid", "static", "y", "neutral", "dates", "val")}

    for m in matches:
        home, away, cur = m["home"], m["away"], _d(m["date"])
        hs, as_ = int(float(m["home_score"])), int(float(m["away_score"]))
        neutral = str(m["neutral"]).lower() == "true"
        eh, ea = E(home), E(away)
        h_adv = 0.0 if neutral else HOME_ADV
        key = f"{home}|{away}" if home < away else f"{away}|{home}"
        rec = h2h.get(key, {"x": 0, "d": 0, "y": 0})
        tot = rec["x"] + rec["d"] + rec["y"]
        h2h_val = ((rec["x"] - rec["y"] if home < away else rec["y"] - rec["x"]) / tot) if tot else 0.0
        static = [(eh - ea) / 100.0, 0.0 if neutral else 1.0,
                  form_gd(home) - form_gd(away), h2h_val]
        y = 0 if hs > as_ else (1 if hs == as_ else 2)

        if cur.year >= WARM_YEAR:
            ho, hr, hn, hm = snap(home, cur)
            ao, ar, an, am = snap(away, cur)
            for k, v in (("ho", ho), ("hr", hr), ("hn", hn), ("hm", hm),
                         ("ao", ao), ("ar", ar), ("an", an), ("am", am)):
                cols[k].append(v)
            cols["hid"].append(vocab[home]); cols["aid"].append(vocab[away])
            cols["static"].append(static); cols["y"].append(y)
            cols["neutral"].append(int(neutral)); cols["dates"].append(m["date"])
            cols["val"].append(m["source"] == "intl_base" and m["date"] >= CUTOFF)

        # updates
        exp = 1.0 / (1.0 + 10.0 ** (-((eh - ea + h_adv) / 400.0)))
        sc = 1.0 if hs > as_ else (0.5 if hs == as_ else 0.0)
        mov = math.log(abs(hs - as_) + 1.0)
        elo[home] = eh + K * mov * (sc - exp)
        elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))
        last.setdefault(home, []).append(hs - as_); last[home][:] = last[home][-FORM_N:]
        last.setdefault(away, []).append(as_ - hs); last[away][:] = last[away][-FORM_N:]
        rh = h2h.setdefault(key, {"x": 0, "d": 0, "y": 0})
        if hs == as_:
            rh["d"] += 1
        elif (hs > as_) == (home < away):
            rh["x"] += 1
        else:
            rh["y"] += 1

        hxg, axg = _f(m["home_xg"]), _f(m["away_xg"])

        def res_for(gf, ga):
            return 1 if gf > ga else (2 if gf == ga else 3)
        hist.setdefault(home, []).append(
            {"opp": vocab[away], "res": res_for(hs, as_), "wh": 1.0,
             "nu": float(neutral), "gf": float(hs), "ga": float(as_),
             "xf": hxg, "xa": axg, "d": cur})
        hist.setdefault(away, []).append(
            {"opp": vocab[home], "res": res_for(as_, hs), "wh": 0.0,
             "nu": float(neutral), "gf": float(as_), "ga": float(hs),
             "xf": axg, "xa": hxg, "d": cur})

    val = np.array(cols["val"], bool)
    static = np.array(cols["static"], np.float32)
    cont = [0, 2, 3]
    tr = ~val
    mean = static[tr][:, cont].mean(axis=0)
    std = static[tr][:, cont].std(axis=0); std[std == 0] = 1.0
    static[:, cont] = (static[:, cont] - mean) / std

    np.savez_compressed(
        HERE / "wc_sequences_rich.npz",
        home_opp=np.array(cols["ho"]), home_res=np.array(cols["hr"]),
        home_num=np.array(cols["hn"]), home_mask=np.array(cols["hm"]),
        away_opp=np.array(cols["ao"]), away_res=np.array(cols["ar"]),
        away_num=np.array(cols["an"]), away_mask=np.array(cols["am"]),
        home_id=np.array(cols["hid"], np.int32), away_id=np.array(cols["aid"], np.int32),
        static=static, y=np.array(cols["y"], np.int64),
        neutral=np.array(cols["neutral"], np.int32), is_val=val,
        dates=np.array(cols["dates"]))

    xg_tokens = sum(int((np.array(cols["hn"])[:, :, 7] > 0).sum()) for _ in [0])
    meta = {"vocab": vocab, "n_teams": V, "seq_len": SEQ_LEN, "num_fields": NUM_FIELDS,
            "result_codes": {"pad": 0, "win": 1, "draw": 2, "loss": 3},
            "static_fields": ["elo_diff", "home_adv", "form_gd", "h2h_rate"],
            "static_scaler": {"cont_idx": cont, "mean": mean.tolist(), "std": std.tolist()},
            "config": {"warm_year": WARM_YEAR, "cutoff": CUTOFF, "seq_len": SEQ_LEN},
            "counts": {"total": int(len(val)), "train": int(tr.sum()), "val": int(val.sum()),
                       "home_tokens_with_xg": int(xg_tokens)}}
    json.dump(meta, open(HERE / "vocab_rich.json", "w"), indent=2)

    print(f"teams (vocab): {V}")
    print(f"sequences: {len(val)}  (train {int(tr.sum())} / val {int(val.sum())})")
    print(f"home-history tokens carrying xG: {xg_tokens}")
    print(f"num_fields={NUM_FIELDS}")
    print("saved wc_sequences_rich.npz and vocab_rich.json")


if __name__ == "__main__":
    build()
