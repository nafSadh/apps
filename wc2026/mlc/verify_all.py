"""Evaluate every trained mlc model on the played 2026 World Cup matches.

Reports, per model: 3-class accuracy, log-loss, Brier score, and a decisive
hit-rate (draws excluded as pushes) that is directly comparable to the
'Model accuracy' back-test in index.html. Writes results.json and refreshes
leaderboard.html for quick viewing."""

import json
import pickle
from pathlib import Path

import numpy as np

from prep_data import load_and_preprocess
from metrics import summary, CLASS_NAMES
# import model classes so pickle can resolve them
import models  # noqa: F401

HERE = Path(__file__).resolve().parent

# pkl prefix -> display name (order = display order before sorting)
MODELS = [
    ("logistic", "Softmax logistic"),
    ("logistic_elo", "Elo-only logistic"),
    ("ordinal", "Ordinal logistic"),
    ("poisson", "Dixon-Coles Poisson"),
    ("knn", "k-NN"),
    ("naive_bayes", "Gaussian NB"),
    ("decision_tree", "Decision tree"),
    ("random_forest", "Random forest"),
    ("mlp", "MLP (neural net)"),
    ("voting", "Soft-vote ensemble"),
    ("ensemble", "Stacking ensemble"),
]


def load(prefix):
    p = HERE / f"{prefix}_model.pkl"
    if not p.exists():
        return None
    with open(p, "rb") as f:
        return pickle.load(f)


def main():
    d = load_and_preprocess()
    Xv, yv = d["X_val"], d["y_val"]

    rows = []
    for prefix, name in MODELS:
        model = load(prefix)
        if model is None:
            print(f"(skipping {name}: {prefix}_model.pkl not found — run its trainer)")
            continue
        P = model.predict_proba(Xv)
        s = summary(P, yv)
        s["name"] = name
        rows.append(s)

    # naive majority-class baseline
    maj = int(np.bincount(d["y_train"]).argmax())
    Pbase = np.zeros((len(yv), 3))
    Pbase[:, maj] = 1.0
    sb = summary(Pbase, yv)
    sb["name"] = f"Naive baseline ({CLASS_NAMES[maj]})"

    rows_sorted = sorted(rows, key=lambda r: (-r["accuracy"], r["log_loss"]))

    print("\n" + "=" * 84)
    print(f"  WC 2026 leaderboard — {len(yv)} played matches "
          f"({sum(yv==0)} home / {sum(yv==1)} draw / {sum(yv==2)} away)")
    print("=" * 84)
    hdr = f"{'Model':<24}{'Acc':>7}{'LogLoss':>10}{'Brier':>9}{'Decisive':>11}{'W-L':>9}"
    print(hdr)
    print("-" * 84)
    best_acc = max(r["accuracy"] for r in rows_sorted) if rows_sorted else 0
    for r in rows_sorted:
        star = " *" if r["accuracy"] == best_acc else "  "
        print(f"{r['name']:<24}{r['accuracy']*100:6.1f}%{r['log_loss']:10.3f}"
              f"{r['brier']:9.3f}{r['decisive_hit_rate']*100:9.0f}% "
              f"{r['decisive_ok']}-{r['decisive_miss']:<2}{star}")
    print("-" * 84)
    print(f"{sb['name']:<24}{sb['accuracy']*100:6.1f}%{sb['log_loss']:10.3f}"
          f"{sb['brier']:9.3f}{'—':>9}  (always {CLASS_NAMES[maj]})")
    print("=" * 84)
    print("Acc = 3-class accuracy (draws count).  Decisive = draws excluded as pushes,")
    print("matching index.html's hit-rate metric.  Lower log-loss / Brier = better.")

    out = {
        "as_of": d["config"]["cutoff_date"],
        "n_val": int(len(yv)),
        "val_breakdown": {"home": int(sum(yv == 0)), "draw": int(sum(yv == 1)),
                          "away": int(sum(yv == 2))},
        "baseline": sb,
        "models": rows_sorted,
    }
    with open(HERE / "results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results.json")
    write_leaderboard_html(out)
    print("wrote leaderboard.html")


def write_leaderboard_html(out):
    rows = out["models"]
    best = max((r["accuracy"] for r in rows), default=0)
    trs = ""
    for i, r in enumerate(rows, 1):
        lead = ' class="lead"' if r["accuracy"] == best else ""
        trs += (f"<tr><td class='r'>{i}</td><td class='nm'>{r['name']}</td>"
                f"<td{lead}>{r['accuracy']*100:.1f}%</td>"
                f"<td>{r['log_loss']:.3f}</td><td>{r['brier']:.3f}</td>"
                f"<td>{r['decisive_hit_rate']*100:.0f}%</td>"
                f"<td class='mut'>{r['decisive_ok']}-{r['decisive_miss']} "
                f"({r['decisive_push']}p)</td></tr>")
    b = out["baseline"]
    vb = out["val_breakdown"]
    html = f"""<!doctype html><meta charset=utf-8>
<title>mlc leaderboard — WC2026</title>
<style>
:root{{--bg:#0b0e18;--card:#141a2e;--line:#26304d;--ink:#e8eaf6;--mut:#7f88ad;--acc:#9b7aed;--good:#67d99b}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;padding:28px}}
.wrap{{max-width:760px;margin:0 auto}}
h1{{font-size:22px;margin:0 0 2px}} .sub{{color:var(--mut);margin:0 0 18px;font-size:13px}}
table{{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th,td{{padding:9px 12px;text-align:right;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}}
th{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:600}}
td.nm,th.nm{{text-align:left}} td.r{{text-align:left;color:var(--mut);width:28px}}
td.mut{{color:var(--mut)}} .lead{{color:var(--good);font-weight:700}}
tr:last-child td{{border-bottom:none}}
.foot{{color:var(--mut);font-size:12px;margin-top:14px}}
</style>
<div class=wrap>
<h1>mlc model leaderboard</h1>
<p class=sub>Validated on {out['n_val']} played 2026 World Cup matches
({vb['home']} home / {vb['draw']} draw / {vb['away']} away) · as of {out['as_of']}</p>
<table>
<thead><tr><th class=r>#</th><th class=nm>Model</th><th>Accuracy</th><th>Log-loss</th>
<th>Brier</th><th>Decisive</th><th class=mut>W-L (push)</th></tr></thead>
<tbody>{trs}
<tr><td class=r>—</td><td class=nm>Naive baseline</td><td>{b['accuracy']*100:.1f}%</td>
<td>{b['log_loss']:.3f}</td><td>{b['brier']:.3f}</td><td>—</td><td class=mut>majority class</td></tr>
</tbody></table>
<p class=foot><b>Accuracy</b> counts draws as a class you must predict.
<b>Decisive</b> excludes draws as pushes — directly comparable to index.html's hit-rate.
Lower log-loss / Brier = better-calibrated probabilities.</p>
</div>"""
    with open(HERE / "leaderboard.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
