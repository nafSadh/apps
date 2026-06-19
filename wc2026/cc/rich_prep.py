"""
cc/ — RICHER-token sequences from the ESPN dataset (shots + possession).

Tests the core hypothesis: do real in-match stats beat Elo? ESPN (~51k matches
with stats, 2024-2026, club + international) gives per-match shots / shots-on-target
/ possession. We build the SAME leakage-free sequence format as prep.py but with
shot/possession token fields, so the Transformer (and an Elo+shots logistic) can be
compared against an Elo-only baseline on a date-based walk-forward.

Reads ~/src/misc-data/espn-soccer/base_data (NOT in the repo). Output: rich_seq.npz.
"""
import csv, json, math
from pathlib import Path
import numpy as np

DATA = Path.home() / "src" / "misc-data" / "espn-soccer" / "base_data"
HERE = Path(__file__).resolve().parent
SEQ_LEN, K, HOME_ADV, FORM_N = 12, 30, 65, 6
NUM_FIELDS = ["was_home", "gf", "ga", "shots_for", "shots_against", "poss", "recency_log"]
PAD, WIN, DRAW, LOSS = 0, 1, 2, 3


def load_matches():
    teams = {}
    with open(DATA / "teams.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            teams[r["teamId"]] = r["name"]
    stats = {}
    with open(DATA / "teamStats.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            try:
                stats[(r["eventId"], r["teamId"])] = (
                    float(r["totalShots"] or 0), float(r["shotsOnTarget"] or 0), float(r["possessionPct"] or 0))
            except (ValueError, TypeError):
                pass
    matches = []
    with open(DATA / "fixtures.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            hs, as_ = r["homeTeamScore"].strip(), r["awayTeamScore"].strip()
            if not hs or not as_:
                continue
            try:
                hs, as_ = int(float(hs)), int(float(as_))
            except ValueError:
                continue
            ev, h, a = r["eventId"], r["homeTeamId"], r["awayTeamId"]
            sh, sa = stats.get((ev, h)), stats.get((ev, a))
            if not sh or not sa:
                continue
            hn, an = teams.get(h), teams.get(a)
            if not hn or not an or hn == an:
                continue
            matches.append({"date": r["date"][:10], "home": hn, "away": an, "hs": hs, "as": as_,
                            "hsh": sh[0], "ash": sa[0], "hp": sh[2], "ap": sa[2]})
    matches.sort(key=lambda m: m["date"])
    return matches


def build():
    matches = load_matches()
    names = sorted({t for m in matches for t in (m["home"], m["away"])})
    vocab = {t: i + 1 for i, t in enumerate(names)}
    elo, sform, pform, hist = {}, {}, {}, {}

    def E(t): return elo.get(t, 1500.0)
    def avg(d, t):
        a = d.get(t, []); return sum(a) / len(a) if a else 0.0

    def snap(team, di):
        seq = hist.get(team, [])[-SEQ_LEN:]
        opp = np.zeros(SEQ_LEN, np.int32); res = np.zeros(SEQ_LEN, np.int32)
        num = np.zeros((SEQ_LEN, len(NUM_FIELDS)), np.float32); mask = np.zeros(SEQ_LEN, np.float32)
        for i, tk in enumerate(seq):
            s = SEQ_LEN - len(seq) + i
            opp[s] = tk["opp"]; res[s] = tk["res"]
            num[s] = [tk["wh"], tk["gf"], tk["ga"], tk["sf"] / 10.0, tk["sa"] / 10.0, tk["pp"] / 100.0,
                      math.log1p(max(di - tk["di"], 0))]
            mask[s] = 1.0
        return opp, res, num, mask

    cols = {k: [] for k in ("Ho", "Hr", "Hn", "Hm", "Ao", "Ar", "An", "Am", "hid", "aid", "static", "y", "dates")}
    for idx, m in enumerate(matches):
        home, away = m["home"], m["away"]; eh, ea = E(home), E(away)
        static = [(eh - ea + HOME_ADV) / 100.0,
                  avg(sform, home) - avg(sform, away),
                  avg(pform, home) - avg(pform, away)]
        y = 0 if m["hs"] > m["as"] else (1 if m["hs"] == m["as"] else 2)
        ho, hr, hn, hm = snap(home, idx); ao, ar, an, am = snap(away, idx)
        for k, v in zip(("Ho", "Hr", "Hn", "Hm", "Ao", "Ar", "An", "Am"), (ho, hr, hn, hm, ao, ar, an, am)):
            cols[k].append(v)
        cols["hid"].append(vocab[home]); cols["aid"].append(vocab[away])
        cols["static"].append(static); cols["y"].append(y); cols["dates"].append(m["date"])
        # chronological updates
        exp = 1.0 / (1.0 + 10.0 ** (-((eh - ea + HOME_ADV) / 400.0)))
        sc = 1.0 if m["hs"] > m["as"] else (0.5 if m["hs"] == m["as"] else 0.0)
        mov = math.log(abs(m["hs"] - m["as"]) + 1.0)
        elo[home] = eh + K * mov * (sc - exp); elo[away] = ea + K * mov * ((1.0 - sc) - (1.0 - exp))
        sform.setdefault(home, []).append(m["hsh"] - m["ash"]); sform[home][:] = sform[home][-FORM_N:]
        sform.setdefault(away, []).append(m["ash"] - m["hsh"]); sform[away][:] = sform[away][-FORM_N:]
        pform.setdefault(home, []).append(m["hp"]); pform[home][:] = pform[home][-FORM_N:]
        pform.setdefault(away, []).append(m["ap"]); pform[away][:] = pform[away][-FORM_N:]
        rf = lambda gf, ga: WIN if gf > ga else (DRAW if gf == ga else LOSS)
        hist.setdefault(home, []).append({"opp": vocab[away], "res": rf(m["hs"], m["as"]), "wh": 1.0,
            "gf": float(m["hs"]), "ga": float(m["as"]), "sf": m["hsh"], "sa": m["ash"], "pp": m["hp"], "di": idx})
        hist.setdefault(away, []).append({"opp": vocab[home], "res": rf(m["as"], m["hs"]), "wh": 0.0,
            "gf": float(m["as"]), "ga": float(m["hs"]), "sf": m["ash"], "sa": m["hsh"], "pp": m["ap"], "di": idx})

    static = np.array(cols["static"], np.float32); dates = np.array(cols["dates"])
    split = "2025-07-01"
    tr = dates < split
    mean = static[tr].mean(0); std = static[tr].std(0); std[std == 0] = 1.0
    static = (static - mean) / std
    np.savez_compressed(HERE / "rich_seq.npz",
        home_opp=np.array(cols["Ho"]), home_res=np.array(cols["Hr"]), home_num=np.array(cols["Hn"]), home_mask=np.array(cols["Hm"]),
        away_opp=np.array(cols["Ao"]), away_res=np.array(cols["Ar"]), away_num=np.array(cols["An"]), away_mask=np.array(cols["Am"]),
        home_id=np.array(cols["hid"], np.int32), away_id=np.array(cols["aid"], np.int32),
        static=static, y=np.array(cols["y"], np.int64), dates=dates, is_test=(~tr))
    meta = {"n_teams": len(vocab), "seq_len": SEQ_LEN, "num_fields": NUM_FIELDS,
            "static_fields": ["elo_diff+homeadv", "shot_form_diff", "poss_form_diff"],
            "split": split, "scaler": {"mean": mean.tolist(), "std": std.tolist()}}
    json.dump(meta, open(HERE / "rich_meta.json", "w"), indent=2)
    print(f"teams={len(vocab)}  matches w/ stats={len(dates)}  ({dates[0]}..{dates[-1]})")
    print(f"train(<{split})={int(tr.sum())}  test={int((~tr).sum())}")
    print(f"label split: H={int((np.array(cols['y'])==0).sum())} D={int((np.array(cols['y'])==1).sum())} A={int((np.array(cols['y'])==2).sum())}")
    print("saved rich_seq.npz + rich_meta.json")


if __name__ == "__main__":
    build()
