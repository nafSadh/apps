# apps

Various small, self-contained web apps — hosted at **[sadh.app](https://sadh.app)**.

Each app lives in its own folder and is a single static page (no build step). GitHub Pages serves the repo root; `CNAME` points it at `sadh.app` and `.nojekyll` disables Jekyll processing.

| App | URL | What it is |
|-----|-----|------------|
| **wc2026** | [sadh.app/wc2026](https://sadh.app/wc2026/) | Interactive 2026 World Cup bracket simulator |

## Hosting

- GitHub Pages → source: `main` branch, root (`/`).
- DNS: point `sadh.app` at GitHub Pages (apex `A`/`AAAA` records to GitHub's IPs, or an `ALIAS`/`CNAME` to `nafsadh.github.io`).
