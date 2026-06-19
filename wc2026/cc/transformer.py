"""
cc/ — a match-history Transformer, FROM SCRATCH in numpy (no torch/tf).

A real Transformer encoder (multi-head self-attention + residual + LayerNorm +
GELU feed-forward) reads each team's last-12 match tokens, masked-mean-pools to a
team vector, fuses home+away reps with identity embeddings and the 4 static
features, and predicts home-win / draw / away-win. Full manual backprop + Adam.

Run:
    python3 prep.py                       # build seq.npz
    python3 transformer.py --gradcheck    # verify analytic grads (must pass first)
    python3 transformer.py --curriculum   # pretrain<=2002 then walk forward per year
"""
import argparse, json, math, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore", category=RuntimeWarning)  # numpy 2.0/Accelerate spurious matmul FP warnings

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(0)

# ----------------------------------------------------------------- primitives
def gelu(x):
    return 0.5 * x * (1.0 + np.tanh(0.7978845608028654 * (x + 0.044715 * x**3)))

def dgelu(x):
    c = 0.7978845608028654
    t = np.tanh(c * (x + 0.044715 * x**3))
    dt = (1 - t**2) * c * (1 + 3 * 0.044715 * x**2)
    return 0.5 * (1 + t) + 0.5 * x * dt

def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)

def layernorm_fwd(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True); var = x.var(-1, keepdims=True)
    inv = 1.0 / np.sqrt(var + eps); xh = (x - mu) * inv
    return xh * g + b, (xh, inv, g)

def layernorm_bwd(dy, cache):
    xh, inv, g = cache
    D = xh.shape[-1]
    dxh = dy * g
    dx = inv * (dxh - dxh.mean(-1, keepdims=True) - xh * (dxh * xh).mean(-1, keepdims=True))
    dg = (dy * xh).reshape(-1, D).sum(0); db = dy.reshape(-1, D).sum(0)
    return dx, dg, db

# ----------------------------------------------------------------- model
class Cfg:
    def __init__(s, V, L, n_num, d=32, dr=8, dn=16, H=2, dff=64, dh=64):
        s.V, s.L, s.n_num, s.d, s.dr, s.dn, s.H, s.dff, s.dh = V, L, n_num, d, dr, dn, H, dff, dh
        s.hd = d // H

def init_params(c):
    sc = lambda a, b: rng.standard_normal((a, b)).astype(np.float64) * math.sqrt(2.0 / a)
    P = {
        "TeamEmb": rng.standard_normal((c.V + 1, c.d)) * 0.05,
        "ResEmb":  rng.standard_normal((4, c.dr)) * 0.05,
        "Wn": sc(c.n_num, c.dn), "bn": np.zeros(c.dn),
        "Wtok": sc(c.d + c.dr + c.dn, c.d), "btok": np.zeros(c.d),
        "Pos": rng.standard_normal((c.L, c.d)) * 0.02,
        "Wq": sc(c.d, c.d), "Wk": sc(c.d, c.d), "Wv": sc(c.d, c.d), "Wo": sc(c.d, c.d),
        "g1": np.ones(c.d), "b1": np.zeros(c.d),
        "W1": sc(c.d, c.dff), "f1": np.zeros(c.dff), "W2": sc(c.dff, c.d), "f2": np.zeros(c.d),
        "g2": np.ones(c.d), "b2": np.zeros(c.d),
        "Wh1": sc(4 * c.d + 4, c.dh), "bh1": np.zeros(c.dh),
        "Wh2": sc(c.dh, 3), "bh2": np.zeros(3),
    }
    P["TeamEmb"][0] = 0.0; P["ResEmb"][0] = 0.0
    return P

def encode(P, c, opp, res, num, mask):
    """opp,res:(B,L) int; num:(B,L,n); mask:(B,L) -> rep:(B,d), cache"""
    B, L = opp.shape
    e_opp = P["TeamEmb"][opp]; e_res = P["ResEmb"][res]
    proj = num @ P["Wn"] + P["bn"]
    tin = np.concatenate([e_opp, e_res, proj], -1)
    tok = tin @ P["Wtok"] + P["btok"]
    x = tok + P["Pos"][None]                                   # (B,L,d)
    # --- multi-head self-attention ---
    Q = (x @ P["Wq"]).reshape(B, L, c.H, c.hd).transpose(0, 2, 1, 3)
    K = (x @ P["Wk"]).reshape(B, L, c.H, c.hd).transpose(0, 2, 1, 3)
    Vv = (x @ P["Wv"]).reshape(B, L, c.H, c.hd).transpose(0, 2, 1, 3)
    scores = Q @ K.transpose(0, 1, 3, 2) / math.sqrt(c.hd)     # (B,H,L,L)
    keypad = (mask[:, None, None, :] < 0.5)
    scores = np.where(keypad, -1e4, scores)   # finite sentinel: exp() underflows to 0, no FP-overflow noise
    attn = softmax(scores, -1)
    ctx = (attn @ Vv).transpose(0, 2, 1, 3).reshape(B, L, c.d)
    out = ctx @ P["Wo"]
    x1, ln1 = layernorm_fwd(x + out, P["g1"], P["b1"])
    h1 = x1 @ P["W1"] + P["f1"]; a1 = gelu(h1); ff = a1 @ P["W2"] + P["f2"]
    x2, ln2 = layernorm_fwd(x1 + ff, P["g2"], P["b2"])
    w = mask[:, :, None]; denom = np.clip(w.sum(1), 1.0, None)
    rep = (x2 * w).sum(1) / denom                              # (B,d)
    cache = dict(opp=opp, res=res, num=num, mask=mask, e_opp=e_opp, e_res=e_res,
                 tin=tin, x=x, Q=Q, K=K, Vv=Vv, attn=attn, ctx=ctx, x1=x1, ln1=ln1,
                 h1=h1, a1=a1, x2=x2, ln2=ln2, w=w, denom=denom, B=B, L=L)
    return rep, cache

def encode_bwd(P, c, drep, cache, G):
    B, L = cache["B"], cache["L"]; w = cache["w"]
    dx2 = drep[:, None, :] * w / cache["denom"][:, None, :]    # broadcast pooled grad
    dx2 = dx2 + np.zeros_like(cache["x2"])
    dxin2, dg2, db2 = layernorm_bwd(dx2, cache["ln2"])
    G["g2"] += dg2; G["b2"] += db2
    dx1 = dxin2.copy(); dff = dxin2
    da1 = dff @ P["W2"].T; G["W2"] += cache["a1"].reshape(-1, c.dff).T @ dff.reshape(-1, c.d)
    G["f2"] += dff.reshape(-1, c.d).sum(0)
    dh1 = da1 * dgelu(cache["h1"])
    G["W1"] += cache["x1"].reshape(-1, c.d).T @ dh1.reshape(-1, c.dff); G["f1"] += dh1.reshape(-1, c.dff).sum(0)
    dx1 = dx1 + dh1 @ P["W1"].T
    dxin1, dg1, db1 = layernorm_bwd(dx1, cache["ln1"])
    G["g1"] += dg1; G["b1"] += db1
    dx = dxin1.copy(); dout = dxin1
    dctx = dout @ P["Wo"].T
    G["Wo"] += cache["ctx"].reshape(-1, c.d).T @ dout.reshape(-1, c.d)
    dctx = dctx.reshape(B, L, c.H, c.hd).transpose(0, 2, 1, 3)
    dattn = dctx @ cache["Vv"].transpose(0, 1, 3, 2)
    dV = cache["attn"].transpose(0, 1, 3, 2) @ dctx
    dscores = cache["attn"] * (dattn - (dattn * cache["attn"]).sum(-1, keepdims=True))
    dscores = dscores / math.sqrt(c.hd)
    dQ = dscores @ cache["K"]; dK = dscores.transpose(0, 1, 3, 2) @ cache["Q"]
    def merge(t): return t.transpose(0, 2, 1, 3).reshape(B, L, c.d)
    dQ, dK, dV = merge(dQ), merge(dK), merge(dV)
    G["Wq"] += cache["x"].reshape(-1, c.d).T @ dQ.reshape(-1, c.d)
    G["Wk"] += cache["x"].reshape(-1, c.d).T @ dK.reshape(-1, c.d)
    G["Wv"] += cache["x"].reshape(-1, c.d).T @ dV.reshape(-1, c.d)
    dx = dx + dQ @ P["Wq"].T + dK @ P["Wk"].T + dV @ P["Wv"].T
    # token embed + pos
    G["Pos"] += dx.reshape(-1, c.d).reshape(B, L, c.d).sum(0)
    dtok = dx
    G["Wtok"] += cache["tin"].reshape(-1, c.d + c.dr + c.dn).T @ dtok.reshape(-1, c.d)
    G["btok"] += dtok.reshape(-1, c.d).sum(0)
    dtin = dtok @ P["Wtok"].T
    de_opp = dtin[:, :, :c.d]; de_res = dtin[:, :, c.d:c.d + c.dr]; dproj = dtin[:, :, c.d + c.dr:]
    G["Wn"] += cache["num"].reshape(-1, c.n_num).T @ dproj.reshape(-1, c.dn)
    G["bn"] += dproj.reshape(-1, c.dn).sum(0)
    np.add.at(G["TeamEmb"], cache["opp"], de_opp)
    np.add.at(G["ResEmb"], cache["res"], de_res)

def forward(P, c, b):
    rh, ch = encode(P, c, b["home_opp"], b["home_res"], b["home_num"], b["home_mask"])
    ra, ca = encode(P, c, b["away_opp"], b["away_res"], b["away_num"], b["away_mask"])
    idh = P["TeamEmb"][b["home_id"]]; ida = P["TeamEmb"][b["away_id"]]
    z = np.concatenate([rh, ra, idh, ida, b["static"]], -1)
    hh = gelu(z @ P["Wh1"] + P["bh1"]); logits = hh @ P["Wh2"] + P["bh2"]
    p = softmax(logits, -1)
    cache = dict(ch=ch, ca=ca, z=z, hh=hh, hpre=z @ P["Wh1"] + P["bh1"],
                 idh_idx=b["home_id"], ida_idx=b["away_id"], p=p)
    return p, cache

def loss_and_grad(P, c, b, y, wd=0.0):
    p, cache = forward(P, c, b)
    B = len(y)
    loss = -np.log(np.clip(p[np.arange(B), y], 1e-12, 1)).mean()
    G = {k: np.zeros_like(v) for k, v in P.items()}
    dlogits = p.copy(); dlogits[np.arange(B), y] -= 1; dlogits /= B
    G["Wh2"] += cache["hh"].T @ dlogits; G["bh2"] += dlogits.sum(0)
    dhh = dlogits @ P["Wh2"].T; dz = (dhh * dgelu(cache["hpre"]))
    G["Wh1"] += cache["z"].T @ dz; G["bh1"] += dz.sum(0)
    dz = dz @ P["Wh1"].T
    d = c.d
    drh = dz[:, :d]; dra = dz[:, d:2 * d]; didh = dz[:, 2 * d:3 * d]; dida = dz[:, 3 * d:4 * d]
    np.add.at(G["TeamEmb"], cache["idh_idx"], didh)
    np.add.at(G["TeamEmb"], cache["ida_idx"], dida)
    encode_bwd(P, c, drh, cache["ch"], G)
    encode_bwd(P, c, dra, cache["ca"], G)
    if wd:
        for k in P:
            if k not in ("TeamEmb", "ResEmb", "Pos") and P[k].ndim == 2:
                G[k] += wd * P[k]; loss += 0.5 * wd * (P[k]**2).sum()
    G["TeamEmb"][0] = 0.0; G["ResEmb"][0] = 0.0
    return loss, G, p

# ----------------------------------------------------------------- adam
class Adam:
    def __init__(s, P, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8):
        s.lr, s.b1, s.b2, s.eps, s.t = lr, b1, b2, eps, 0
        s.m = {k: np.zeros_like(v) for k, v in P.items()}
        s.v = {k: np.zeros_like(v) for k, v in P.items()}
    def step(s, P, G):
        s.t += 1
        for k in P:
            s.m[k] = s.b1 * s.m[k] + (1 - s.b1) * G[k]
            s.v[k] = s.b2 * s.v[k] + (1 - s.b2) * G[k]**2
            mh = s.m[k] / (1 - s.b1**s.t); vh = s.v[k] / (1 - s.b2**s.t)
            P[k] -= s.lr * mh / (np.sqrt(vh) + s.eps)
        P["TeamEmb"][0] = 0.0; P["ResEmb"][0] = 0.0

# ----------------------------------------------------------------- gradcheck
def _toy(c, B=5):
    L, n = c.L, c.n_num
    b = dict(
        home_opp=rng.integers(0, c.V + 1, (B, L)), home_res=rng.integers(0, 4, (B, L)),
        home_num=rng.standard_normal((B, L, n)), home_mask=(rng.random((B, L)) > 0.3).astype(float),
        away_opp=rng.integers(0, c.V + 1, (B, L)), away_res=rng.integers(0, 4, (B, L)),
        away_num=rng.standard_normal((B, L, n)), away_mask=(rng.random((B, L)) > 0.3).astype(float),
        home_id=rng.integers(1, c.V + 1, B), away_id=rng.integers(1, c.V + 1, B),
        static=rng.standard_normal((B, 4)))
    b["home_mask"][:, -1] = 1.0; b["away_mask"][:, -1] = 1.0   # avoid all-pad
    y = rng.integers(0, 3, B)
    return b, y

def gradcheck():
    c = Cfg(V=12, L=6, n_num=5, d=16, dr=4, dn=8, H=2, dff=24, dh=20)
    P = init_params(c); b, y = _toy(c)
    _, G, _ = loss_and_grad(P, c, b, y)
    worst = 0.0
    for k in ["Wh2", "Wh1", "Wo", "Wq", "W1", "W2", "Wtok", "Wn", "Pos", "g1", "g2", "TeamEmb", "ResEmb"]:
        idx = tuple(rng.integers(0, s) for s in P[k].shape)
        if k in ("TeamEmb", "ResEmb") and idx[0] == 0:
            idx = (1,) + idx[1:]
        e = 1e-5; orig = P[k][idx]
        P[k][idx] = orig + e; lp, _, _ = loss_and_grad(P, c, b, y)
        P[k][idx] = orig - e; lm, _, _ = loss_and_grad(P, c, b, y)
        P[k][idx] = orig
        num = (lp - lm) / (2 * e); ana = G[k][idx]
        rel = abs(num - ana) / max(1e-8, abs(num) + abs(ana))
        worst = max(worst, rel)
        print(f"  {k:8} num={num:+.3e} ana={ana:+.3e} rel={rel:.2e}")
    print(f"\nworst relative error: {worst:.2e}  ->  {'PASS' if worst < 1e-4 else 'FAIL'}")
    return worst < 1e-4

# ----------------------------------------------------------------- data
def load():
    z = np.load(HERE / "seq.npz", allow_pickle=True)
    meta = json.load(open(HERE / "meta.json"))
    keys = ["home_opp", "home_res", "home_num", "home_mask", "away_opp", "away_res",
            "away_num", "away_mask", "home_id", "away_id", "static"]
    D = {k: z[k] for k in keys}
    return D, z["y"].astype(int), z["year"].astype(int), z["is_val"].astype(bool), meta

def batch_of(D, idx):
    return {k: v[idx] for k, v in D.items()}

def metrics(P, c, D, y, idx, bs=2048):
    ps = []
    for s in range(0, len(idx), bs):
        p, _ = forward(P, c, batch_of(D, idx[s:s + bs]))
        ps.append(p)
    P_ = np.concatenate(ps); yy = y[idx]
    pred = P_.argmax(1); acc = (pred == yy).mean()
    ll = -np.log(np.clip(P_[np.arange(len(yy)), yy], 1e-12, 1)).mean()
    brier = ((P_ - np.eye(3)[yy])**2).sum(1).mean()
    return dict(acc=float(acc), ll=float(ll), brier=float(brier), n=len(yy)), P_

def train_epochs(P, c, opt, D, y, idx, epochs, bs=512, wd=1e-5, log=None):
    for ep in range(epochs):
        perm = rng.permutation(idx); tot = 0.0
        for s in range(0, len(perm), bs):
            bi = perm[s:s + bs]
            loss, G, _ = loss_and_grad(P, c, batch_of(D, bi), y[bi], wd)
            if not np.isfinite(loss):
                raise SystemExit(f"non-finite loss at epoch {ep} — training diverged")
            opt.step(P, G); tot += loss * len(bi)
        if log:
            log(ep, tot / len(perm))

def static_logistic_wf(D, y, year, is_val):
    """Baseline: multinomial logistic on the 4 static features (elo_diff, home_adv,
    form_gd, h2h_rate) — the tabular labs' ceiling — on the SAME curriculum/walk-forward."""
    X = D["static"].astype(np.float64)
    Xb = np.concatenate([X, np.ones((len(X), 1))], 1)
    W = np.zeros((Xb.shape[1], 3))
    def sm(idx):
        z = Xb[idx] @ W; z -= z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)
    def fit(idx, epochs, lr):
        nonlocal W
        for _ in range(epochs):
            perm = rng.permutation(idx)
            for s in range(0, len(perm), 1024):
                bi = perm[s:s + 1024]; p = sm(bi); g = p.copy(); g[np.arange(len(bi)), y[bi]] -= 1; g /= len(bi)
                W -= lr * (Xb[bi].T @ g + 1e-4 * W)
    fit(np.where(year <= 2002)[0], 80, 0.3)
    AP, AY = [], []
    for yr in range(2003, 2027):
        te = np.where(year == yr)[0]
        if not len(te):
            continue
        AP.append(sm(te)); AY.append(y[te]); fit(te, 3, 0.1)
    AP = np.concatenate(AP); AY = np.concatenate(AY)
    acc = (AP.argmax(1) == AY).mean(); ll = -np.log(np.clip(AP[np.arange(len(AY)), AY], 1e-12, 1)).mean()
    wc = np.where(is_val)[0]; wp = sm(wc)
    return dict(acc=float(acc), log_loss=float(ll), wc_acc=float((wp.argmax(1) == y[wc]).mean()))


def curriculum():
    D, y, year, is_val, meta = load()
    c = Cfg(V=meta["n_teams"], L=meta["seq_len"], n_num=len(meta["num_fields"]))
    P = init_params(c)
    # cast float64 -> keep float64 for numeric stability (small model)
    opt = Adam(P, lr=1.5e-3)
    pre = np.where(year <= 2002)[0]
    print(f"[pretrain] {len(pre)} matches <=2002, decades of epochs...")
    t0 = time.time()
    train_epochs(P, c, opt, D, y, pre, epochs=12, bs=512, wd=1e-5,
                 log=lambda ep, l: print(f"  epoch {ep+1:2d}  loss {l:.4f}") if (ep % 3 == 0 or ep == 11) else None)
    print(f"  pretrain done in {time.time()-t0:.0f}s")
    # walk forward: for each year >2002, eval THEN train on it (online, no leakage)
    print("\n[walk-forward] eval each year before training on it:")
    opt2 = Adam(P, lr=8e-4)
    rows = []; allP = []; allY = []
    for yr in range(2003, 2027):
        te = np.where(year == yr)[0]
        if len(te) == 0:
            continue
        m, Pr = metrics(P, c, D, y, te)
        rows.append((yr, m)); allP.append(Pr); allY.append(y[te])
        train_epochs(P, c, opt2, D, y, te, epochs=1, bs=256, wd=1e-5)
        print(f"  {yr}: n={m['n']:4d}  acc {m['acc']*100:4.1f}%  logloss {m['ll']:.3f}")
    # aggregate walk-forward
    AP = np.concatenate(allP); AY = np.concatenate(allY)
    acc = (AP.argmax(1) == AY).mean()
    ll = -np.log(np.clip(AP[np.arange(len(AY)), AY], 1e-12, 1)).mean()
    # baseline: always-home and class-prior
    prior = np.bincount(y[year <= 2002], minlength=3) / (year <= 2002).sum()
    base_ll = -np.log(prior[AY]).mean(); base_acc = (np.full(len(AY), prior.argmax()) == AY).mean()
    wc = np.where(is_val)[0]; mwc, _ = metrics(P, c, D, y, wc)
    print("\n[baseline] Elo/static logistic on the same walk-forward...")
    elo = static_logistic_wf(D, y, year, is_val)
    out = {"walkforward": {"n": int(len(AY)), "acc": float(acc), "log_loss": float(ll),
                           "elo_logistic_acc": elo["acc"], "elo_logistic_log_loss": elo["log_loss"],
                           "prior_acc": float(base_acc), "prior_log_loss": float(base_ll)},
           "by_year": [{"year": yr, **m} for yr, m in rows],
           "wc2026": {"transformer": mwc, "elo_logistic_acc": elo["wc_acc"]}}
    json.dump(out, open(HERE / "transformer_result.json", "w"), indent=2)
    print("\n=== WALK-FORWARD (2003-2026, {} held-out matches) ===".format(len(AY)))
    print(f"  Transformer (seq+static): acc {acc*100:.1f}%   log-loss {ll:.3f}")
    print(f"  Elo/static logistic:      acc {elo['acc']*100:.1f}%   log-loss {elo['log_loss']:.3f}")
    print(f"  Prior baseline:           acc {base_acc*100:.1f}%   log-loss {base_ll:.3f}")
    print(f"  (WC2026 20-game noise: transformer {mwc['acc']*100:.0f}% / elo {elo['wc_acc']*100:.0f}%)")
    print("saved transformer_result.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gradcheck", action="store_true")
    ap.add_argument("--curriculum", action="store_true")
    a = ap.parse_args()
    if a.gradcheck:
        gradcheck()
    elif a.curriculum:
        curriculum()
    else:
        print("use --gradcheck or --curriculum")
