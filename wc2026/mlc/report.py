"""Shared per-match validation printout used by the train_*.py scripts."""

import numpy as np
from metrics import summary, CLASS_NAMES


def per_match(name, P, meta, y):
    print(f"\n{name} — validation on {len(y)} played WC 2026 matches")
    print(f"{'Date':<11} {'Home':<14} {'Sc':<5} {'Away':<15} {'Actual':<9} {'P(H/D/A)':<20} hit")
    print("-" * 92)
    pred = np.argmax(P, axis=1)
    for i, m in enumerate(meta):
        hs, as_ = m["score"]
        p = P[i]
        ok = "OK" if pred[i] == y[i] else " x"
        print(f"{m['date']:<11} {m['home'][:13]:<14} {hs}-{as_:<3} {m['away'][:14]:<15} "
              f"{CLASS_NAMES[y[i]]:<9} H{p[0]:.2f} D{p[1]:.2f} A{p[2]:.2f}    {ok}")
    s = summary(P, y)
    print("-" * 92)
    print(f"accuracy {s['accuracy']*100:.1f}%  |  log-loss {s['log_loss']:.3f}  |  "
          f"brier {s['brier']:.3f}  |  decisive hit-rate {s['decisive_hit_rate']*100:.0f}% "
          f"({s['decisive_ok']}-{s['decisive_miss']}, {s['decisive_push']} pushes)")
    return s
