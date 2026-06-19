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

## Notes

- numpy + scipy only — runs in this environment (sklearn/torch are NOT installed).
- `transformer.py` is gradient-checked; a non-finite-loss guard aborts on divergence.
- `seq.npz` is regenerable from `prep.py` (gitignored).
