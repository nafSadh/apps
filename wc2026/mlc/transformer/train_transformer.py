"""
Transformer match-predictor (SCAFFOLD — requires PyTorch).

Reads the sequences built by prep_transformer_data.py and trains a small
Transformer encoder that reads each team's recent match history, fuses it with
team-identity embeddings and the 4 engineered static features, and predicts
home-win / draw / away-win. Final evaluation is on the played 2026 World Cup
matches, reported with the same metrics as the tabular lab (accuracy, log-loss,
Brier, and the draws-excluded "decisive" hit-rate).

This file is intentionally runnable as-is once torch is installed:

    pip install torch            # CPU wheel is fine for this size
    python3 prep_transformer_data.py
    python3 train_transformer.py --epochs 40

It is a starting point, not a tuned model. With only ~32k matches and 4-ish
signals per game, expect it to land near the tabular models, not far above them
(see README.md). The payoff comes from richer tokens (xG, lineups) and more
matches (club pre-training) — the token schema is built to grow.
"""

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _need_torch():
    try:
        import torch  # noqa: F401
        return
    except ImportError:
        raise SystemExit(
            "\nPyTorch is not installed in this environment.\n"
            "  pip install torch        # CPU build is sufficient\n"
            "Then re-run:  python3 train_transformer.py\n")


def load_data(which="plain"):
    npz_name, vocab_name, prep = {
        "plain": ("wc_sequences.npz", "vocab.json", "prep_transformer_data.py"),
        "rich": ("wc_sequences_rich.npz", "vocab_rich.json", "prep_transformer_rich.py"),
    }[which]
    npz = HERE / npz_name
    if not npz.exists():
        raise SystemExit(f"Run `python3 {prep}` first.")
    z = np.load(npz, allow_pickle=True)
    meta = json.load(open(HERE / vocab_name))
    return z, meta


# ---- metrics (numpy; mirror ../metrics.py so this file stays standalone) ----
def _metrics(P, y):
    pred = P.argmax(1)
    acc = float((pred == y).mean())
    ll = float(-np.log(np.clip(P[np.arange(len(y)), y], 1e-15, 1)).mean())
    Y = np.eye(3)[y]
    brier = float(((P - Y) ** 2).sum(1).mean())
    ok = miss = push = 0
    for pk, yt in zip(pred, y):
        if pk == 1 or yt == 1:
            push += 1
        elif pk == yt:
            ok += 1
        else:
            miss += 1
    dec = ok / (ok + miss) if (ok + miss) else 0.0
    return dict(acc=acc, log_loss=ll, brier=brier, decisive=dec,
                ok=ok, miss=miss, push=push)


def build_model(torch, nn, meta, args):
    V = meta["n_teams"]
    n_num = len(meta["num_fields"])

    class MatchTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            d = args.d_model
            self.team = nn.Embedding(V + 1, d, padding_idx=0)        # shared: identity + opponent
            self.res = nn.Embedding(4, d // 4, padding_idx=0)
            self.num = nn.Linear(n_num, d // 2)
            self.tok = nn.Linear(d + d // 4 + d // 2, d)
            self.pos = nn.Parameter(torch.zeros(1, meta["seq_len"], d))
            layer = nn.TransformerEncoderLayer(
                d_model=d, nhead=args.heads, dim_feedforward=2 * d,
                dropout=args.dropout, batch_first=True, activation="gelu")
            self.enc = nn.TransformerEncoder(layer, num_layers=args.layers)
            self.head = nn.Sequential(
                nn.Linear(4 * d + 4, 2 * d), nn.GELU(), nn.Dropout(args.dropout),
                nn.Linear(2 * d, 3))

        def encode(self, opp, res, num, mask):
            t = torch.cat([self.team(opp), self.res(res), self.num(num)], dim=-1)
            t = self.tok(t) + self.pos
            pad = mask < 0.5                                          # True where padding
            h = self.enc(t, src_key_padding_mask=pad)
            w = mask.unsqueeze(-1)
            return (h * w).sum(1) / w.sum(1).clamp(min=1.0)          # masked mean pool

        def forward(self, b):
            hh = self.encode(b["home_opp"], b["home_res"], b["home_num"], b["home_mask"])
            ha = self.encode(b["away_opp"], b["away_res"], b["away_num"], b["away_mask"])
            z = torch.cat([hh, ha, self.team(b["home_id"]), self.team(b["away_id"]),
                           b["static"]], dim=-1)
            return self.head(z)

    return MatchTransformer()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight_decay", type=float, default=1e-4)
    ap.add_argument("--d_model", type=int, default=64)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--val_frac", type=float, default=0.05,
                    help="chronological tail of TRAIN used for early stopping")
    ap.add_argument("--data", choices=["plain", "rich"], default="plain",
                    help="plain = internationals only; rich = corpus w/ club + xG")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    _need_torch()
    import torch
    import torch.nn as nn

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    z, meta = load_data(args.data)
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    def T(name, dtype):
        return torch.tensor(z[name], dtype=dtype)

    feats = {
        "home_opp": T("home_opp", torch.long), "home_res": T("home_res", torch.long),
        "home_num": T("home_num", torch.float), "home_mask": T("home_mask", torch.float),
        "away_opp": T("away_opp", torch.long), "away_res": T("away_res", torch.long),
        "away_num": T("away_num", torch.float), "away_mask": T("away_mask", torch.float),
        "home_id": T("home_id", torch.long), "away_id": T("away_id", torch.long),
        "static": T("static", torch.float),
    }
    y = T("y", torch.long)
    is_val = z["is_val"].astype(bool)

    tr_idx = np.where(~is_val)[0]
    wc_idx = np.where(is_val)[0]
    cut = int(len(tr_idx) * (1 - args.val_frac))     # chronological split (rows are date-ordered)
    fit_idx, es_idx = tr_idx[:cut], tr_idx[cut:]
    print(f"device={dev}  fit={len(fit_idx)}  early-stop={len(es_idx)}  WC2026={len(wc_idx)}")

    model = build_model(torch, nn, meta, args).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    lossf = nn.CrossEntropyLoss()

    def batch(idx):
        return {k: v[idx].to(dev) for k, v in feats.items()}, y[idx].to(dev)

    def probs(idx):
        model.eval()
        out = []
        with torch.no_grad():
            for s in range(0, len(idx), 1024):
                b, _ = batch(idx[s:s + 1024])
                out.append(torch.softmax(model(b), dim=-1).cpu().numpy())
        return np.concatenate(out)

    best, best_state, bad = 1e9, None, 0
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = np.random.permutation(fit_idx)
        tot = 0.0
        for s in range(0, len(perm), args.batch):
            bi = perm[s:s + args.batch]
            b, yb = batch(bi)
            opt.zero_grad()
            loss = lossf(model(b), yb)
            loss.backward()
            opt.step()
            tot += float(loss) * len(bi)
        es = _metrics(probs(es_idx), y[es_idx].numpy())
        print(f"epoch {ep:3d}  train_loss {tot/len(perm):.4f}  "
              f"es_logloss {es['log_loss']:.4f}  es_acc {es['acc']*100:.1f}%")
        if es["log_loss"] < best - 1e-4:
            best, best_state, bad = es["log_loss"], {k: v.detach().cpu().clone()
                                                     for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= 6:
                print("early stop.")
                break

    if best_state:
        model.load_state_dict(best_state)
    m = _metrics(probs(wc_idx), y[wc_idx].numpy())
    print("\n=== Transformer on played WC 2026 matches ===")
    print(f"accuracy {m['acc']*100:.1f}%  |  log-loss {m['log_loss']:.3f}  |  "
          f"brier {m['brier']:.3f}  |  decisive {m['decisive']*100:.0f}% "
          f"({m['ok']}-{m['miss']}, {m['push']} pushes)")
    torch.save(model.state_dict(), HERE / "transformer_model.pt")
    json.dump(m, open(HERE / "transformer_result.json", "w"), indent=2)
    print("saved transformer_model.pt and transformer_result.json")


if __name__ == "__main__":
    main()
