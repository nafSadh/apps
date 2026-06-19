"""
cc/ — TRAIN + VERIFY on the richer (shots/possession) ESPN sequences.

The decisive test: does adding real in-match stats (shots, possession) beat plain
Elo? Date-based walk-forward (train < 2025-07-01, test after). Three contenders,
same split:
    - Elo-only logistic          (static[0] = elo_diff+homeadv)
    - Elo + shots + possession    (all 3 static features)
    - Transformer (rich tokens)   (from-scratch numpy, shot/possession tokens)
plus a prior-probability baseline.

    python3 rich_prep.py      # build rich_seq.npz first
    python3 rich_train.py
"""
import json
from pathlib import Path
import numpy as np
import transformer as T   # the gradient-checked from-scratch transformer

HERE = Path(__file__).resolve().parent


def load_rich():
    z = np.load(HERE / "rich_seq.npz", allow_pickle=True)
    meta = json.load(open(HERE / "rich_meta.json"))
    keys = ["home_opp", "home_res", "home_num", "home_mask", "away_opp", "away_res",
            "away_num", "away_mask", "home_id", "away_id", "static"]
    return {k: z[k] for k in keys}, z["y"].astype(int), z["is_test"].astype(bool), meta


def logistic(Xtr, ytr, Xte, yte, iters=250, lr=0.3):
    Xtr = np.concatenate([Xtr, np.ones((len(Xtr), 1))], 1)
    Xte = np.concatenate([Xte, np.ones((len(Xte), 1))], 1)
    W = np.zeros((Xtr.shape[1], 3))
    def sm(X):
        z = X @ W; z -= z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)
    for _ in range(iters):
        p = sm(Xtr); g = p.copy(); g[np.arange(len(ytr)), ytr] -= 1; g /= len(ytr); W -= lr * (Xtr.T @ g + 1e-4 * W)
    P = sm(Xte)
    return float((P.argmax(1) == yte).mean()), float(-np.log(np.clip(P[np.arange(len(yte)), yte], 1e-12, 1)).mean())


def main():
    D, y, is_test, meta = load_rich()
    tr, te = np.where(~is_test)[0], np.where(is_test)[0]
    S = D["static"]
    elo_acc, elo_ll = logistic(S[tr][:, [0]], y[tr], S[te][:, [0]], y[te])
    rich_acc, rich_ll = logistic(S[tr], y[tr], S[te], y[te])
    prior = np.bincount(y[tr], minlength=3) / len(tr)
    base_acc = float((np.full(len(te), prior.argmax()) == y[te]).mean())
    base_ll = float(-np.log(prior[y[te]]).mean())

    # smaller model + strong weight-decay + early stop: the 3070-team vocab over 2.5yr overfits fast
    c = T.Cfg(V=meta["n_teams"], L=meta["seq_len"], n_num=len(meta["num_fields"]), n_static=S.shape[1],
              d=24, dh=32, dff=48)
    P = T.init_params(c); opt = T.Adam(P, lr=1e-3)
    cut = int(len(tr) * 0.9); fit, es = tr[:cut], tr[cut:]   # chronological early-stop tail
    print(f"training transformer (rich tokens, {len(fit)} fit / {len(es)} early-stop)...")
    best, best_ll = None, 1e9
    for ep in range(20):
        T.train_epochs(P, c, opt, D, y, fit, epochs=1, bs=512, wd=1.5e-3)
        m, _ = T.metrics(P, c, D, y, es)
        if m["ll"] < best_ll - 1e-3:
            best_ll, best = m["ll"], {k: v.copy() for k, v in P.items()}; bad = 0
        else:
            bad = bad + 1 if ep else 0
        if ep % 3 == 0:
            print(f"  epoch {ep+1:2d}  es_logloss {m['ll']:.4f}")
        if bad >= 4:
            print(f"  early stop @ epoch {ep+1}"); break
    if best:
        P = best
    tm, _ = T.metrics(P, c, D, y, te)

    print(f"\n=== ESPN walk-forward — train<2025-07-01, test after ({len(te)} matches) ===")
    print(f"  prior baseline:          acc {base_acc*100:4.1f}%   log-loss {base_ll:.3f}")
    print(f"  Elo-only logistic:       acc {elo_acc*100:4.1f}%   log-loss {elo_ll:.3f}")
    print(f"  Elo + shots + possession: acc {rich_acc*100:4.1f}%   log-loss {rich_ll:.3f}")
    print(f"  Transformer (rich seq):  acc {tm['acc']*100:4.1f}%   log-loss {tm['ll']:.3f}")
    d_ll = elo_ll - rich_ll
    print(f"\n  >>> shots vs Elo: Δlog-loss {d_ll:+.3f}  ->  "
          f"{'SHOTS HELP' if d_ll > 0.003 else 'no real gain over Elo'}")
    json.dump({"n_test": int(len(te)), "prior": {"acc": base_acc, "ll": base_ll},
               "elo_only": {"acc": elo_acc, "ll": elo_ll},
               "elo_shots_poss": {"acc": rich_acc, "ll": rich_ll},
               "transformer": tm}, open(HERE / "rich_result.json", "w"), indent=2)
    print("saved rich_result.json")


if __name__ == "__main__":
    main()
