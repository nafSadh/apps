# wc2026 — data update scripts

The app reads [`../data.json`](../data.json). The same data is also embedded
inline in `index.html` as an **offline fallback** (so the page works on
`file://` and if the fetch fails). Keep them in sync with `update.py`.

What changes during the tournament:

| field | shape | how to update |
|-------|-------|---------------|
| `locked` | `{matchNo: [homeGoals, awayGoals]}` (group games 1–72) | results CSV or API fetch |
| `ko` | `[{stage, home, away, h, a, w, p?}]` knockout results (codes) | API fetch (`collect_ko`) |
| `ratings` | `{code: {fifa, elo, odds, opta, form}}` | ratings CSV |
| `h2h` / `formYears` | full head-to-head + recent-form | `--intl` from the martj42 dataset |

Knockout games carry bracket-slot placeholders (not fixed team-pairs), so `ko` lists each
played bracket game by **team code** (`w` = winner code, covers shootouts; `p` = `[hp, ap]`
penalties). The app maps each entry onto its own bracket slot by team-pair, advances the
winner, and rolls the "Today" strip forward. `live.json` carries the same `ko` plus a
`koLive` list for in-play knockout games.

`teams`, `fixtures` and the knockout bracket are fixed at the draw — don't edit them here.

## Common commands

```bash
cd apps/wc2026/scripts

python3 update.py --check                       # validate data.json (CI-friendly, exits 1 on error)

# enter played scores (header optional): matchNo,homeGoals,awayGoals
python3 update.py --results results.example.csv --set-asof 2026-06-25

# refresh ratings: code,fifa,elo,odds,opta,form
python3 update.py --ratings ratings.example.csv

# rebuild the COMPLETE head-to-head + recent form for all 48 teams from the
# Kaggle martj42 dataset (intl-results.csv = its results.csv). Only matches on or
# before meta.asOf are counted; predecessors are folded in (West Germany->Germany,
# Zaire->DR Congo, Netherlands Antilles->Curacao). Penalty shootouts count as draws.
python3 update.py --intl intl-results.csv --sync-embed
#   dataset: https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017
#   refresh it by re-downloading the CSV over scripts/intl-results.csv and re-running.

# pull finished results automatically from football-data.org (free token: https://football-data.org)
python3 update.py --fetch-footballdata --token "$FD_TOKEN"

# after any change, keep the inline fallback in index.html identical to data.json
python3 update.py --sync-embed
```

`update.py` validates everything (team codes, fixture numbers, score shapes,
ratings completeness) before writing, bumps `meta.version`/`meta.asOf`, and
writes pretty-printed `data.json`. Stdlib only — no `pip install` needed.

## Per-match performance log

After locking new results, refresh the simulation performance log:

```bash
node perf_log.js     # writes perf-log.md (readable) + perf-log.json (structured)
```

It replays all 8 models against every played match using the app's own engine (`index.html`)
and the locked scores in `data.json`, so it mirrors the in-app **Simulation accuracy** tab —
but as a committed, version-controlled record (a leaderboard + a ✓/✗ grid per match). Diff it
over time to watch each model's hit rate move as the tournament unfolds.

## Live updates (hourly GitHub Action)

`live.py` polls football-data.org for in-play + finished matches and writes a tiny
`../live.json` (live scores + the full locked map) that the app fetches every minute —
driving the **Today** strip and the pulsing **LIVE** badges — and **locks any newly
finished game** into `data.json` at full-time (then syncs the inline fallback).

```bash
python3 live.py --token "$FOOTBALL_DATA_TOKEN"
```

`.github/workflows/live-wc2026.yml` runs this hourly, refreshes the performance log, and
commits/pushes. Add the repo secret **`FOOTBALL_DATA_TOKEN`** (free from football-data.org)
to enable it; without it the job is a no-op. `live.json` is tiny and only rewritten when
scores change, so idle hours produce no commits.

## Deploy

```bash
git add data.json index.html
git commit -m "data: update through <date>"
git push        # GitHub Pages redeploys sadh.app/wc2026
```

In the app, the **↻ Refresh data** button re-fetches `data.json` live, so users
get the new numbers without a hard reload once the push is deployed.

## True live (optional upgrade)

A browser can't call most football/ratings APIs directly (CORS + secret API
keys can't live in a public static page). For live data **without a redeploy**,
put a tiny serverless proxy in front (e.g. a Cloudflare Worker / Vercel function)
that fetches the API server-side and returns CORS-enabled JSON in this same
`data.json` shape, then point the Refresh button at it. Until then, the
Python-script → commit → push flow is the reliable path.
