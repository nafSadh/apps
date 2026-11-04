# Handoff — `audit` request, 2026-09-25

**Branch:** `main`, working tree clean. Nothing staged, nothing stashed, no local commits ahead of origin.
**Prior session:** `session_012NE5zX1aRtEoNF6sMmzscA` (sandbox). It launched a 12-area audit workflow moments before teleport; that run's report is stuck on the sandbox and cannot be pulled here. **Restart the audit locally.**

---

## Honest scope of this handoff

What is in this file: (1) reconnaissance I completed on both machines before the workflow launched — **verified**, with `file:line` and byte counts, and (2) leads the workflow was going to check — **not yet verified**. I explicitly mark which is which. Do not treat the "leads" as findings. Verify them.

The workflow itself (find → adversarial verify → gap round → synthesize) never returned any results to me, so there are **zero completed audit findings** to hand off. Everything below is either a fact from `git`/`grep`/`wc` or a hypothesis to test.

---

## Confirmed facts (safe to cite)

### Repo shape

- 587 tracked files. Pack is ~415 MiB. `photoing/` = 395 MB on disk.
- Served: everything tracked, because `CNAME` + `.nojekyll` at the root and GitHub Pages serves the whole repo. So `sadh.app/photoing/CLAUDE.md` etc. resolve.

### CI workflows

- `.github/workflows/matchday-brief.yml` — daily at 14:00 UTC (cron `0 14 * * *`). Runs `matchday/brief/fetch.py`, `scores.py`, `render.py`, then sanity-checks the rendered page and commits back.
- `.github/workflows/live-wc2026.yml:11` and `update-wc2026.yml:10` — schedule commented out with `# schedule disabled 2026-07-21 — tournament over (Spain champions); re-enable for the next cycle:`. Both now `workflow_dispatch:` only. WC2026 is dormant; only matchday runs daily.
- Both wc2026 workflows and the matchday-brief workflow pass the FOOTBALL_DATA_TOKEN via env, but then hand it to the Python script as `--token "$FD_TOKEN"`:
  - `live-wc2026.yml:38` — `python3 live.py --token "$FD_TOKEN"`
  - `update-wc2026.yml:33` — `python update.py --fetch-footballdata --token "$FD_TOKEN" --sync-embed`
  - Not a critical leak (GitHub-hosted runners are single-tenant and GH auto-redacts secrets in logs), but argv is worse than env because any `subprocess`/log-dump inside the script can echo it. Note as **info/low**.
- `matchday-brief.yml:19` has an inline reminder: `# 14:00 UTC = 7am PDT (6am once PST starts — shift to 15 then)`. **PST begins 2026-11-01**, so the cron needs a manual bump then. That's 37 days away.

### Escaping in the brief pipeline

- `matchday/brief/render.py:31` — `return html.escape(s or "", quote=True)`. Present.
- `matchday/brief/fetch.py:84` — strips tags via regex `re.sub("<[^>]+>", "", html.unescape(s or ""))`. Enough for RSS text bodies, weak for attribute contexts.
- `matchday/brief/scores.py:29` — comment "are written with `</` escaped so no name can close the script block", which is the right idea but should be re-checked against implementation.
- **Lead** for the audit: whether every field flowing into `brief.html` and `cal.html` actually passes through `esc()` (not just some), and whether URLs from feeds are validated as `http(s)://` before becoming `href` values.

### Bot cadence in git log

- Two commits per weekday (matchday-brief bot): `brief: digest YYYY-MM-DD` at ~15:XX UTC, `brief + scores: daily refresh YYYY-MM-DD` at ~17:XX UTC. No sign of failures in recent history.
- Bot commit author: `github-actions[bot]` per the workflow's `git config user.email 41898282+github-actions[bot]@users.noreply.github.com`.

### Commit hygiene

- 10 recent commits have message `.` — all human, not bot: `e1d3f81`, `422b2cc`, `1b1ec8f`, `7d9889d`, `bcf1fe8`, `80b4504`, `c60b132`, `bae8939`, `8ff06ca`, `b6cab70`. Cosmetic, but the pattern is worth mentioning to the user.

### Tracked-but-ignored files

`.gitignore` has `__pycache__/` (line 12) but these `.pyc` files are still in the index (added before the rule):

```
wc2026/mlc/__pycache__/metrics.cpython-310.pyc
wc2026/mlc/__pycache__/models.cpython-310.pyc
wc2026/mlc/__pycache__/prep_data.cpython-310.pyc
wc2026/mlc/__pycache__/prep_data_plus.cpython-310.pyc
wc2026/mlc/__pycache__/report.cpython-310.pyc
wc2026/mlc/__pycache__/run_all.cpython-310.pyc
wc2026/mlc/__pycache__/train_decision_tree.cpython-310.pyc
wc2026/mlc/__pycache__/train_ensemble.cpython-310.pyc
wc2026/mlc/__pycache__/train_knn.cpython-310.pyc
wc2026/mlc/__pycache__/train_logistic.cpython-310.pyc
```

Full list: `git ls-files -ci --exclude-standard`. Also under `wc2026/mlc/data_sources/__pycache__/` and `wc2026/mlc/transformer/__pycache__/`.

### Bloat — exact byte counts

Candidates for removal, with paths and sizes:

| Path | Size | Notes |
|---|---:|---|
| `photoing/gen/_gemini-pipeline/images/` (89 files, whole dir) | **150 MB** | One-off Gemini build artefacts. |
| `photoing/gen/*.jpeg` (12 largest) | **184 MB total** | Triptychs / demo renders. `shutter-speed-triptych.jpeg` alone is 4.1 MB. Need to check whether any `photoing/*.html` references them or only smaller derivatives. |
| `matchday/img/*-src.jpeg` (7 originals) | **16.0 MB** | Compressed derivatives already exist next to them (`dawn-arc.jpg` 196 KB, `five-am.jpg` 296 KB). Confirm no page references the `-src` originals. |
| `wc2026/mlc/transformer/wc_sequences.npz` | 4.3 MB | Model training input. |
| `wc2026/mlc/data_sources/corpus.csv` | 4.0 MB | Training data. |
| `wc2026/scripts/intl-results.csv` | 3.7 MB | Training data. |
| `wc2026/mlc/transformer/wc_sequences_rich.npz` | 2.9 MB | |
| `photoing/Camera Metering_ OM-1 vs. X100VI - Google Gemini.pdf` | 972 KB | Grep says referenced only from `photoing/CLAUDE.md` and `photoing/CHANGELOG.md`. Not linked from any served HTML. |
| `photoing/gen/_gemini-pipeline/*.py` (non-image) | 41 scripts | One-off `build_*` / `fix_*` scripts. Almost certainly dead. |

If all four `photoing/` categories go, that's ~350 MB off the pack — most of the 415 MB total.

### Internal / AI-assistant files served publicly at sadh.app

These are tracked and therefore live-linkable. **Not necessarily bad**, but the user should decide intentionally:

- `photoing/CLAUDE.md` — Claude Code project instructions.
- `matchday/agents-talk.md` — agent notes.
- `photoing/STREET-GUIDE-STATE.md`, `photoing/gen/PENDING-FRAMES.md`, `photoing/gen/GEMINI-PROMPTS.md` — build-state files.
- `photoing/CHANGELOG.md` — may be intentional.
- The Google Gemini PDF above.

### README gap

`README.md` app table lists matchday, games/c-queens, pantheon-cup, wc2026 — but **not** `photoing/`, which contains five HTML guides (`index.html`, `x100vi-guide.html`, `om1-guide.html`, `street-guide.html`, `in-practice.html`) and is served at `sadh.app/photoing/`.

---

## Leads still to verify (audit these, don't quote them yet)

Group these by area. For each area, the sandbox workflow was going to (a) find candidate issues, (b) have 1–3 skeptics per finding try to refute it, (c) keep only what survives majority vote. Redo that here.

### 1. CI workflows

- Argv-passed FOOTBALL_DATA_TOKEN — is it echoed anywhere inside `live.py` / `update.py` (verbose logging, error branches)?
- Rebase-and-retry loop in `live-wc2026.yml:59-64` — could it clobber a human-authored commit if there's a mid-run push race?
- `matchday-brief.yml` sanity check at lines 76–101: does the f-string leak regex actually cover every field the renderer interpolates? What happens if it fires — is the page not written, or written with `{expr}` visible?
- Any `${{ github.event.* }}` context flowing into a `run:` block unescaped? (Grep confirmed no, but re-check.)

### 2. matchday/brief pipeline

- Do `fetch.py`, `render.py`, `scores.py` HTML-escape **every** field that goes into `brief.html`, or only the body text? Attributes especially.
- URL fields from RSS — validated as `^https?://`? A `javascript:` URL in a feed becomes a live XSS on sadh.app if it lands in an `href`.
- XML parsing — is it `defusedxml` or vanilla `xml.etree`? Billion-laughs / XXE from a hostile feed.
- Regex-based rewrite of `cal.html` in `scores.py` — what if two matches have the same team names or date? Corruption?
- Request timeouts / retries — a hung host slowing the cron.

### 3. matchday frontend (index, cal, clubs, guide, players)

- Kickoff-time math around the DST boundaries:
  - **2026-10-25** Europe falls back to standard time.
  - **2026-11-01** US falls back to standard time.
  - The offset between kickoff-country and Pacific changes twice in a week. Off-by-one hour is very likely.
- Season 2026–27 dates and fixtures — stale?
- localStorage / innerHTML paths — search for `innerHTML =` in `matchday/*.html` and `matchday/brief/transfers.js` (3754 lines).

### 4. wc2026 frontend + scripts

- Tournament ended — is the page still polling `live.json`? What state is `data.json` in vs the workflow's stated "Spain champions"?
- Third-place seeding for 48-team format in the bracket JS — logic bug hotspot.
- ML scripts in `wc2026/scripts/` and `wc2026/mlc/` — hard-coded absolute paths, cannot-run-as-committed problems.

### 5. games/c-queens

- Run `node games/c-queens/scripts/test.js` and report. **Check first that it does not write into the repo**; if it does, copy the dir to `/tmp/` and run there.
- Level uniqueness and solvability.
- Daily-board TZ — same board across users? Rolls at what local time?

### 6. Root + pantheon-cup + photoing

- Root `index.html` link inventory — does every href resolve to a tracked file?
- Photoing pages — do they reference the huge `photoing/gen/*.jpeg` files or smaller derivatives?
- `photoing/index.html` — 127 lines, worth a quick read.

### 7. Runtime sweep (headless browser)

- Serve `python3 -m http.server` on a random free port.
- Playwright + Chromium — on this Mac, run `npx playwright install chromium` (not `/opt/pw-browsers/...` — that path is sandbox-only).
- Load every tracked `.html` at 1280×800 and 375×812; record console errors, page errors, same-origin 404s, `documentElement.scrollWidth > innerWidth` at 375px, total transferred bytes.
- Exercise one main control on each app (c-queens click, wc2026 bracket pick, matchday filter) and report exceptions.

### 8. a11y / SEO

- `<html lang>`, `<title>`, meta viewport, meta description, favicon.
- `<img alt>` coverage.
- Contrast for main body + muted text in light and dark.
- `outline: none` without a replacement.
- `prefers-reduced-motion` on any animation.
- Heading order.

### 9. Privacy / secrets across full git history

- `git log -p --all | grep -E` for token patterns (`ghp_`, `github_pat_`, `sk-`, `AIza`, 32+ hex adjacent to token/key words).
- **EXIF/GPS on every tracked JPEG/PNG** — use PIL or `exiftool`. Especially `matchday/img/*.jpeg`, `photoing/gen/*.jpeg`, `photoing/gen/_gemini-pipeline/images/*`. If any real photo carries GPS or camera-serial + owner-name tags, that's a **high**-severity leak on a public site.
- Emails / real names in the tree — grep for `@gmail.com`, `@`, common names.
- **Never paste any secret value into output. Redact.**

### 10. External deps

- Every `<script src>` and `<link>` — CDN URLs without SRI, versions unpinned.
- Third-party fonts / analytics / trackers.
- Hotlinked images from Wikipedia / Wikimedia / club sites / ESPN — may violate hotlinking policies.
- `target="_blank"` links without `rel="noopener"`.
- GitHub Actions versions (`actions/checkout@v4`, `actions/setup-python@v5`) — check currency.
- Committed trademark logos in `matchday/logos/*.svg` (Arsenal, Bayern, PSG, La Liga mark, etc.) — note as **info** with licensing risk.

---

## How to run the audit

Ultracode is on. Two shapes to pick from:

**Fast path** — one message with parallel `Agent` calls, one per area above. Use `Explore` for read-only sweeps and `general-purpose` where Playwright / Python is needed.

**Thorough path** — re-author a `Workflow` with the shape the sandbox used:

1. Fan out one finder agent per area, each returning structured `{title, file, line, severity, category, evidence, failure_scenario, fix}`.
2. Per finding, spawn 1–3 skeptics with distinct lenses: REPRODUCE (re-check the claim literally), REFUTE (find a mitigation elsewhere), IMPACT (does it matter for this personal static site?). Drop findings a majority refutes. Severity ladder: critical=exploitable/site-down, high=user-visible breakage or private-data leak or XSS, medium=likely bug, low/info=polish.
3. Completeness critic proposes up to 5 gap areas; run them the same way.
4. Synthesis agent merges dupes, applies verifier corrections, ranks, and writes Markdown.

**Rules for the run:**

- Read-only until the audit is complete. No edits, no commits, no pushes. Scratch under `/tmp/` — never inside the repo.
- Every finding must have `file:line`, a quoted evidence snippet, a concrete failure scenario, one-line fix. No generic best-practice lectures.
- Never paste secret values in output.

Write the report to `AUDIT-2026-09-25.md` at the repo root when done. Ask before applying any fixes.

## Housekeeping

Delete this file (`handoff.md`) once you've read and continued — it's not meant to ship to sadh.app.
