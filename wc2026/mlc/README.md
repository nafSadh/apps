# mlc — model lab (added algorithms)

A self-contained lab of **from-scratch** match-prediction models (numpy only),
trained on 150 years of international football and validated on the **20 played
2026 World Cup group-stage matches** (June 11–16).

It lives entirely in `mlc/`. It **reads** `../scripts/intl-results.csv` but never
writes to or imports from `scripts/` (owned by another workstream), and it does
not touch `../ml.html` or `../index.html`.

## What's here

| model | file | one-liner |
|-------|------|-----------|
| Softmax logistic (+ Elo-only) | `train_logistic.py` | multinomial logistic over the 4 features |
| **Ordinal logistic** | `train_ordinal.py` | proportional-odds; treats W/D/L as ordered |
| **Dixon-Coles Poisson** | `train_poisson.py` | two goal regressions + low-score correction → scoreline |
| **Random forest** | `train_random_forest.py` | bagged trees, feature subsampling → interactions |
| k-NN | `train_knn.py` | nearest neighbours in feature space |
| Gaussian NB | `train_naive_bayes.py` | generative baseline |
| Decision tree | `train_decision_tree.py` | single CART tree |
| MLP | `train_mlp.py` | 1 hidden layer + softmax |
| **Soft-vote + Stacking ensembles** | `train_ensemble.py` | average / meta-logistic over the bases |

Shared: `prep_data.py` (features + no-leakage split), `models.py` (all classes),
`metrics.py`, `report.py`. Transformer experiment: `transformer/` (scaffold).

Richer data (club football, xG, historical FIFA rankings): `data_sources/` —
source adapters + a unified corpus builder + a local downloader, all tested with
synthetic fixtures. `prep_data_plus.py` adds an optional historical-FIFA-ranking
feature to the tabular models. See `data_sources/README.md`.

## Run

```bash
cd mlc
python3 run_all.py            # train everything, then verify on WC2026
python3 run_all.py --verify   # re-score existing .pkl files only
python3 train_ordinal.py      # or run any single model
```

`verify_all.py` writes `results.json` and `leaderboard.html` (open it in a browser).

## Features (same as the tabular lab, no future leakage)

Walking matches in date order, using only what was known before kickoff:
`elo_diff`, `home_adv`, `recent_form_gd`, `head_to_head_rate`. Continuous columns
are standardized on training statistics only.

## Reading the leaderboard

Two accuracy numbers, on purpose:

- **Accuracy** — 3-class, draws count. This is the honest hard metric.
- **Decisive hit-rate** — draws excluded as "pushes", `✓ ÷ (✓+✗)`. This matches
  the "Model accuracy" back-test in `index.html`, so the two are comparable.

The validation set is **40% draws** (8 of 20). Because a draw is almost never the
single most-likely outcome, every model's *3-class accuracy* takes a big hit there,
while the *decisive* metric (which `index.html` uses) looks much higher. That gap —
not model quality — is most of why a squad-value heuristic appears to "beat" these
models. On the decisive metric these models land at **82–92%**, right in the mix.

Latest run (20 matches — small sample, differences are mostly noise):

| model | accuracy | log-loss | decisive |
|-------|---------:|---------:|---------:|
| Decision tree | 55% | 0.994 | 92% (11–1) |
| Elo-only logistic | 55% | 1.053 | 92% (11–1) |
| Softmax logistic | 50% | 1.042 | 83% (10–2) |
| Ordinal logistic | 50% | 1.059 | 83% (10–2) |
| Dixon-Coles Poisson | 50% | 1.067 | 83% (10–2) |
| Random forest / MLP / ensembles | 50% | ~1.06 | 83% |
| Gaussian NB | 50% | 1.149 | 91% (10–1) |
| k-NN | 45% | 1.101 | 82% (9–2) |
| naive (always home) | 50% | 17.27 | — |

> ⚠️ **20 matches is a tiny test set.** Treat the ordering as indicative, not
> significant. Log-loss/Brier (probability quality) are more informative here than
> raw accuracy.

## Richer features (squad value, FIFA rank, EA FC, odds) — the catch

These are strong predictors (squad market value especially). But in `data.json`
they're a **current snapshot for the 48 WC teams only**. To *train* a model on
them, every historical match needs its own *time-correct* value of each feature —
which we don't have for the 46k-match history. So:

- The squad-value "model" in `index.html` is a **heuristic** (strength proxy), not
  trained — and 20 played matches is far too few to train one from.
- To train properly we'd need **historical, time-stamped** versions: historical
  FIFA rankings (free, monthly since Aug 1992), FIFA-game/EA-FC squad ratings
  (~2007+), Transfermarkt squad values (~2004+, license grey). That's a data-hunt
  prerequisite — see `transformer/README.md` for sources.

## Notes

- Pure stdlib + numpy. No model trains for more than a few seconds; full `run_all`
  is ~30 s.
- Everything is from scratch (gradient descent, Gini trees, etc.) — readable, not
  a library wrapper.
