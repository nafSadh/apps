# Transformer experiment (prep / scaffold)

A sequence model for match prediction. Instead of 4 engineered numbers per game,
it reads **each team's recent match history** as a sequence of tokens, learns its
own representation, fuses it with team-identity embeddings + the same 4 static
features the tabular models use, and predicts home-win / draw / away-win.

Status: **scaffold, not yet trained.** The data pipeline runs today (numpy only).
The model needs PyTorch, which isn't installed in this environment.

## Files

| file | what it does | needs |
|------|--------------|-------|
| `prep_transformer_data.py` | one chronological, no-leakage pass → `wc_sequences.npz` + `vocab.json` | numpy (runs now) |
| `train_transformer.py` | small Transformer encoder + train loop + WC2026 eval | **PyTorch** |
| `wc_sequences.npz` | generated tensors (≈4 MB) | — |
| `vocab.json` | team→id map, token schema, scaler, counts | — |

## Run it

```bash
cd mlc/transformer
python3 prep_transformer_data.py        # already runnable -> 32,307 seqs (32,287 train / 20 WC2026 val)
pip install torch                        # CPU wheel is fine for this size
python3 train_transformer.py --epochs 40
```

It evaluates on the 20 played 2026 World Cup matches and prints the same metrics
as the tabular lab (accuracy, log-loss, Brier, draws-excluded "decisive"
hit-rate), then writes `transformer_model.pt` + `transformer_result.json`.

## Token schema (built to grow)

Per history token, per team, oldest→newest, left-padded:

- **categorical (embedded):** `opp_id` (opponent), `result` (W/D/L from this team's view)
- **numeric:** `was_home`, `neutral`, `goals_for`, `goals_against`, `recency_log`

Plus per match: home/away team ids, the 4 static features (`elo_diff`, `home_adv`,
`form_gd`, `h2h_rate`), and the label.

## Will 32k matches be enough?

Enough to **train and experiment** with a small model — not enough to expect it to
beat the tabular models. The ceiling here isn't row count, it's **signal**: W/D/L
from result-only history is largely irreducible noise (draws/upsets), and football
prediction tops out around ~50–55% three-class accuracy regardless of model. More
*rows of the same features* won't move a transformer much.

## Hunting richer data (the real lever)

Two ways to make the transformer worth it, in priority order:

1. **Richer tokens (biggest win).** Add expected-goals (xG), shots, possession,
   lineups per match. Append columns to `NUM_FIELDS` (and the numeric projection in
   `train_transformer.py`); use a mask / `-1` sentinel for matches whose source
   lacks the field — **don't drop rows for missing richness.**
   - StatsBomb Open Data — free, ML-friendly license, event-level → xG/shots/lineups, tournament-focused (incl. World Cups). https://github.com/statsbomb/open-data
   - FiveThirtyEight SPI — frozen but one CSV each; `spi_matches.csv` + `spi_matches_intl.csv` carry pre-match ratings **and post-match xG**. https://github.com/fivethirtyeight/data/tree/master/soccer-spi
   - Avoid FBref/Sports-Reference — its terms explicitly forbid training AI on scraped data.

2. **More matches via club pre-training (transfer learning).** Pre-train the encoder
   on a large club corpus, then fine-tune on internationals with this same token
   format.
   - football-data.co.uk — free CSVs, ~22–25 leagues, 2000→present, results + shots + odds. https://www.football-data.co.uk/data.php
   - Kaggle European Soccer DB — ODbL, sqlite, ~25k matches w/ possession + lineups (2008–16). https://www.kaggle.com/datasets/hugomathien/soccer
   - openfootball/football.json — CC0, results-only top-up. https://github.com/openfootball/football.json

Main ingest cost is a **team-name → canonical-id map** across sources (each names
teams differently). Reconcile into the shared `vocab.json`, then pre-train on club
rows and fine-tune on the international rows.
