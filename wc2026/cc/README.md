# cc/ — a from-scratch Transformer + the evaluation the other labs were missing

This lab exists to answer one question honestly: **can a sequence model (Transformer)
beat the tabular/Elo models at predicting football results — and how would we even
know?** The sibling labs (`../scripts/`, `../mlc/`) are *correct and leakage-free*,
but they validate on only **~20 played WC2026 games**, where 40% are draws and every
model lands 45–55% — pure noise. You cannot rank models on 20 games.

So `cc/` does two things differently:

1. **A real Transformer, from scratch in numpy** (no PyTorch in this env — the
   `mlc/transformer/` scaffold needs torch and has never run here). Multi-head
   self-attention + residual + LayerNorm + GELU FFN + Adam, **manual backprop,
   numerically gradient-checked to 8e-10**.
2. **A walk-forward backtest over decades** instead of 20 games — so the comparison
   is statistically real (22,523 held-out matches).

## The curriculum (as requested)

- **Pretrain** on everything **≤ 2002** (21,913 matches), many epochs.
- **Walk forward** one year at a time, 2003 → 2026: *evaluate* the model on year *N*
  (which it has never seen), *then* train on it. Online, no leakage. This yields a
  prediction for every match 2003–2026 — a 22.5k-match honest test set.

```bash
python3 prep.py                     # build seq.npz (44,436 sequences, 1960-2026)
python3 transformer.py --gradcheck  # verify analytic gradients (must PASS first)
python3 transformer.py --curriculum # pretrain<=2002, then per-year walk-forward
```

## Result (the honest headline)

| model | walk-forward acc (22,523 games) | log-loss |
|-------|--------------------------------:|---------:|
| Transformer (sequence + static) | 58.4% | 0.896 |
| **Elo / static logistic** | **58.8%** | **0.894** |
| Prior-probability baseline | 48.0% | 1.050 |
| *(WC2026 20-game noise)* | *transformer 45% / elo 50%* | — |

**Takeaway:** the Transformer matches Elo and beats the naive baseline by ~10pp — but
it does **not** beat Elo. The attention over match-history sequences adds nothing on
top of what an Elo rating + 4 engineered features already encode. This is the same
ceiling the `mlc` README predicted: *result-only history is largely irreducible noise;
football tops out ~55–60% three-class accuracy regardless of model.* The 20-game WC2026
number is uninformative either way — exactly why the other labs' leaderboards are noise.

## How to actually beat Elo (= why your multi-source idea is right)

The lever is **signal, not architecture**. The token schema in `prep.py` is built to
grow — add columns to `NUM_FIELDS` and the numeric projection. In priority order:

1. **xG / shots per match** — the single biggest win. **FiveThirtyEight SPI**
   (`spi_matches.csv` + `spi_matches_intl.csv`, CC-licensed, one download) carries
   pre-match ratings **and post-match xG** for **both club and international** games —
   so it delivers richer tokens *and* the club corpus for transfer learning at once.
2. **Club pre-training (transfer learning).** Pre-train the encoder on a large club
   corpus (football-data.co.uk free CSVs, or Kaggle European Soccer DB / ODbL), then
   fine-tune on internationals with this same token format. Cost = a team-name →
   canonical-id reconciliation across sources into the shared vocab.
3. **Time-stamped squad value / FIFA rank.** `data.json` only has a *current* snapshot
   for the 48 WC teams, so these can't be *trained* historically — they need a
   historical source (FIFA ranks are free monthly since 1992; EA-FC ratings ~2007+;
   Transfermarkt values ~2004+, license grey). Without that they remain WC2026
   inference-time features, not training signal.

The architecture is ready for all three; the blocker is the data download, not the model.

## Experiment 2 — do richer tokens (shots/possession) beat Elo?

Added the **ESPN dataset** (~51k matches, 2024–2026, club + international) which carries
per-match **shots / shots-on-target / possession** (no xG). `rich_prep.py` builds the
same leakage-free sequences with shot/possession token fields; `rich_train.py` runs a
date-based walk-forward (train < 2025-07-01, test after — **14,390 matches**):

| model | acc | log-loss |
|-------|----:|---------:|
| prior baseline | 44.7% | 1.068 |
| Elo-only logistic | 48.9% | 1.026 |
| **Elo + shots + possession** | **49.7%** | **1.018** |
| Transformer (rich tokens, regularized) | 49.6% | 1.019 |

**Findings:** (1) shots/possession add a *small but real* edge over Elo (+0.8pp, Δlog-loss
+0.008). (2) the Transformer — once regularized (smaller model, weight-decay 1.5e-3,
chronological early-stop; *un*regularized it overfits the 3,070-team × 2.5-yr data to 44%)
— **matches** the rich logistic but does not beat it. (3) absolute numbers are low because
2.5 years is **cold-start** for ratings (Elo here is only 48.9% vs 58.8% on the deep data).

```bash
python3 rich_prep.py    # ESPN shots/possession sequences  (reads ~/src/misc-data/espn-soccer)
python3 rich_train.py   # Elo vs Elo+shots vs Transformer, walk-forward
```

## Bottom line across both experiments

Elo is a strong, hard-to-beat baseline. A from-scratch Transformer **ties** the best simple
model in *both* regimes — deep result-only (58.4% vs 58.8% Elo) and shallow shot-rich (49.6%
vs 49.7%) — and never beats it. **Richer signal helps marginally; model complexity does not.**
The one untested lever that could plausibly break the ceiling is *deep + dense xG/lineup*
data over decades — which no free source provides at that depth.

## Notes

- numpy + scipy only — runs in this environment (sklearn/torch are NOT installed).
- `transformer.py` is gradient-checked; a non-finite-loss guard aborts on divergence.
- `seq.npz` is regenerable from `prep.py` (gitignored).
