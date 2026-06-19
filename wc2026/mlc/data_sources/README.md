# data_sources — richer-data ingestion

Turns external football datasets into one **unified match corpus** so the
transformer can train on club football (transfer learning) and real **xG**, and
so the tabular models can use **historical FIFA rankings**. Every adapter
normalizes a source into the same `UnifiedMatch` shape (`schema.py`) and
canonicalizes team names to the martj42 spelling.

> Downloads run **locally** (`fetch_data.py`), not in the Cowork sandbox. The
> adapters, corpus builder, FIFA feature, and tests all run with numpy/stdlib.

## Pipeline

```bash
cd mlc/data_sources
python3 test_adapters.py                 # 1. prove parsers work (synthetic, no network)
python3 fetch_data.py --all              # 2. download (LOCAL) -> raw/
python3 build_corpus.py                  # 3. merge everything -> corpus.csv (+ coverage report)

# transformer on the rich corpus (club + xG):
cd ../transformer
python3 prep_transformer_rich.py
python3 train_transformer.py --data rich --epochs 40

# tabular models + historical FIFA-ranking feature:
cd ..
python3 prep_data_plus.py                # needs data_sources/raw/fifa_ranking.csv
```

## Sources

| source | file(s) → `raw/` | gives | license | how to get |
|--------|------------------|-------|---------|-----------|
| **FiveThirtyEight SPI** | `spi_matches.csv`, `spi_matches_intl.csv` | club + intl results **with xG** (`xg1/xg2`), pre-match ratings | open (frozen ~2023) | `fetch_data.py --spi` |
| **football-data.co.uk** | `football_data/*.csv` | club results + **shots / shots-on-target** + odds, 2000→present, ~20 leagues | free, permissive | `fetch_data.py --football-data` |
| **StatsBomb Open Data** | `statsbomb/open-data/` | event-level → **xG, shots, lineups** for World Cups/Euros/Copa/AFCON | free, **attribution required** (© StatsBomb) | `fetch_data.py --statsbomb` (git clone) |
| **historical FIFA rankings** | `fifa_ranking.csv` | monthly FIFA points/rank since 1992 | Kaggle (CC) | manual — see below |
| martj42 internationals | `../../scripts/intl-results.csv` | the base (always included; holds WC2026 val) | — | already present |

**Avoid FBref / Sports-Reference** — its terms explicitly forbid training AI on
scraped data.

### FIFA rankings (manual)
Kaggle needs a login, so it isn't auto-downloaded. Grab
<https://www.kaggle.com/datasets/cashncarry/fifaworldranking> and save the CSV as
`raw/fifa_ranking.csv`. The adapter is tolerant of column naming
(`country_full`/`country`, `total_points`/`points`, `rank_date`/`date`).

## Files

| file | role |
|------|------|
| `schema.py` | `UnifiedMatch` dataclass, `canon()` team-name map, corpus read/write |
| `adapt_538_spi.py` | 538 SPI → rows (xG) |
| `adapt_football_data_couk.py` | football-data.co.uk → rows (shots) |
| `adapt_statsbomb.py` | StatsBomb events/matches → rows (xG aggregated from shots) |
| `adapt_fifa_rankings.py` | FIFA ranking CSV → no-leakage `points_as_of(team, date)` |
| `build_corpus.py` | merge + de-dup (richness-priority) → `corpus.csv` + report |
| `fetch_data.py` | local downloader |
| `test_adapters.py` | synthetic-fixture smoke tests |

## Extending

- **New team-name mismatches:** `build_corpus.py` prints unmapped names — add them
  to `ALIASES` in `schema.py`.
- **New richness field (e.g. possession):** add the column to `UnifiedMatch`, set
  it in the relevant adapter, and append it to `NUM_FIELDS` in
  `transformer/prep_transformer_rich.py` (and the numeric projection adapts
  automatically — `train_transformer.py` reads the field count from the vocab).
- **Don't drop matches for missing richness** — the token schema masks absent xG
  (`has_xg = 0`).
