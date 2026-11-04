# apps

Various small, self-contained web apps — hosted at **[sadh.app](https://sadh.app)**.

Each app lives in its own folder and is a single static page (no build step). GitHub Pages serves the repo root; `CNAME` points it at `sadh.app` and `.nojekyll` disables Jekyll processing.

| App | URL | What it is |
|-----|-----|------------|
| **matchday** | [sadh.app/matchday](https://sadh.app/matchday/) | Matchday Pacific — Pacific Time viewing guide for European club football, 2026–27 |
| **games/c-queens** | [sadh.app/games/c-queens](https://sadh.app/games/c-queens/) | Colored N-Queens — a Star Battle style logic puzzle: 100 levels, a daily board, hints that explain the deduction. `games/c-queens/scripts/gen.js` rebuilds the level bank; `games/c-queens/scripts/test.js` verifies it. |
| **pantheon-cup** | [sadh.app/pantheon-cup](https://sadh.app/pantheon-cup/) | Fictional gods, monsters & heroes stripped of their powers and made to play football |
| **election2026** | [sadh.app/election2026](https://sadh.app/election2026/) | Midterms 2026: Nov. 3 results in charts, with a district hex map of the swing from 2024, exit polls and ballot measures |
| **wc2026** | [sadh.app/wc2026](https://sadh.app/wc2026/) | Interactive 2026 World Cup bracket simulator |

## Hosting

- GitHub Pages → source: `main` branch, root (`/`).
- DNS: point `sadh.app` at GitHub Pages (apex `A`/`AAAA` records to GitHub's IPs, or an `ALIAS`/`CNAME` to `nafsadh.github.io`).
