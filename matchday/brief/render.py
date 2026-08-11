#!/usr/bin/env python3
"""Render feed.json into matchday/brief.html, in the app's own shell.

Nothing here asserts a rumour is true. Every item carries the outlet that ran it
and links out; corroboration across outlets is shown, not resolved. The editorial
pass (what leads, what gets cut) happens before this, in curate.json if present.

    python3 render.py
"""
import json, html, re, sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # matchday/
FEED = HERE / "feed.json"               # full haul, written by fetch.py (local only)
SLIM = HERE / "feed.slim.json"          # committed copy — what the writer job sees
CURATE = HERE / "curate.json"           # written by the brief-writer job, see below
OUT = ROOT / "brief.html"
PT = ZoneInfo("America/Los_Angeles")

SHELL_SRC = ROOT / "clubs.html"         # single source of truth for theme + header CSS


def esc(s):
    return html.escape(s or "", quote=True)


def shell_css():
    s = SHELL_SRC.read_text(encoding="utf-8")
    return s[s.index("<style>") + len("<style>"): s.index("  .eyebrow .tag{")]


def nav(exclude="brief"):
    ico = {
        "index.html": ('Home', '<path d="M2 7.5 8 2.5l6 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M3.5 6.5V13h9V6.5" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M6.3 13v-3.6h3.4V13" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>'),
        "clubs.html": ('Clubs', '<path d="M8 1.6 13.5 3.4V7.8C13.5 11.2 11.2 13.4 8 14.4 4.8 13.4 2.5 11.2 2.5 7.8V3.4Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>'),
        "players.html": ('Players', '<circle cx="8" cy="5.4" r="2.6" stroke="currentColor" stroke-width="1.3"/><path d="M2.8 13.6c.9-2.9 2.9-4.4 5.2-4.4s4.3 1.5 5.2 4.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>'),
        "guide.html": ('Viewing guide', '<path d="M8 3.2C6.5 2.3 4.7 2 3 2.3v9.6c1.7-.3 3.5 0 5 .9 1.5-.9 3.3-1.2 5-.9V2.3c-1.7-.3-3.5 0-5 .9Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M8 3.2v9.6" stroke="currentColor" stroke-width="1.2"/>'),
        "cal.html": ('Full calendar', '<rect x="2" y="3" width="12" height="11" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M2 6.5h12" stroke="currentColor" stroke-width="1.3"/><path d="M5 1.5v3M11 1.5v3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>'),
    }
    out = []
    for href, (label, path) in ico.items():
        out.append(f'      <a class="iconbtn" href="{href}" data-tip="{label}" aria-label="{label}">\n'
                   f'        <svg width="15" height="15" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{path}</svg>\n      </a>')
    out.append('      <button class="iconbtn" id="themeToggle" type="button" data-tip="Toggle theme" aria-label="Toggle light or dark theme">◐</button>')
    return "\n".join(out)


def item_html(e):
    srcs = [e["source"]] + e.get("also", [])
    corr = f'<span class="corr" title="reported by {len(srcs)} outlets">×{len(srcs)}</span>' if len(srcs) > 1 else ""
    tags = "".join(f'<span class="wtag">{esc(w)}</span>' for w in e.get("watch", [])[:4])
    link = esc(e.get("link") or "#")
    summ = e.get("summary", "")
    summ = re.sub(r"\s+", " ", summ)[:190]
    # built outside the f-string: quotes/backslashes inside an f-string expression
    # need Python 3.12+, and the runners this has to survive are not all on 3.12
    blurb = '<p class="bs">' + esc(summ) + "</p>" if summ else ""
    title = esc(e["title"])
    srclist = esc(", ".join(srcs))
    return (f'    <li class="bitem">\n'
            f'      <a class="bt" href="{link}" target="_blank" rel="noopener">{title}</a>\n'
            f'      {blurb}\n'
            f'      <div class="bmeta"><span class="src">{srclist}</span>{corr}{tags}</div>\n'
            f'    </li>')


def section(title, tag, items, note=None):
    if not items:
        return ""
    body = "\n".join(item_html(e) for e in items)
    n = f'<p class="snote">{esc(note)}</p>' if note else ""
    return (f'<div class="eyebrow"><h2>{esc(title)}</h2><div class="rule"></div><div class="tag">{esc(tag)}</div></div>\n'
            f'{n}<ul class="blist">\n{body}\n</ul>\n')


def main():
    src = FEED if FEED.exists() else SLIM      # writer job only has the slim copy
    if not src.exists():
        sys.exit("no feed.json or feed.slim.json — run fetch.py first")
    blob = json.loads(src.read_text(encoding="utf-8"))
    items = blob["items"]

    cur = json.loads(CURATE.read_text(encoding="utf-8")) if CURATE.exists() else {}
    drop = {d.lower() for d in cur.get("drop", [])}
    items = [e for e in items if e["title"].lower() not in drop]

    def rank(pool):
        # corroboration/relevance first, then RECENCY (newest first) — the old
        # oldest-first tiebreak led a "Daily Brief" with last week's items
        fresh = sorted(pool, key=lambda e: e.get("published") or "", reverse=True)
        return sorted(fresh, key=lambda e: -(len(e.get("also", [])) + len(e.get("watch", []))))

    rumours = rank([e for e in items if e["kind"] == "rumour"])[:14]
    news = rank([e for e in items if e["kind"] == "news"])[:10]
    reads = rank([e for e in items if e["kind"] in ("analysis", "data")])[:8]

    now = datetime.now(timezone.utc).astimezone(PT)
    fetched = blob.get("fetched", "")
    srcs = sorted({e["source"] for e in blob["items"]})
    errs = blob.get("errors", [])
    errnote = (f' <span class="ferr">{len(errs)} feed(s) failed this run: '
               + esc(", ".join(e["source"] for e in errs)) + "</span>") if errs else ""

    paras = cur.get("paragraphs") or ([cur["lead"]] if cur.get("lead") else [])
    if paras:
        head = f'<h2 class="dh">{esc(cur["headline"])}</h2>' if cur.get("headline") else ""
        body = "".join(f"<p>{esc(p)}</p>" for p in paras)
        stamp = esc((cur.get("written") or "")[:16].replace("T", " "))
        by = (f'<div class="dby">written {stamp}Z from the feed below · not independently verified</div>'
              if stamp else "")
        leadhtml = f'<div class="digest">{head}{body}{by}</div>\n'
    else:
        leadhtml = ""

    page = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<script>try{{var t=localStorage.getItem('mdcal-theme');if(t==='dark'||t==='light')document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Brief — Matchday Pacific</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Caveat:wght@600;700&display=swap" rel="stylesheet">
<style>
{shell_css()}  .eyebrow .tag{{font-family:var(--mono);font-size:11px;letter-spacing:.12em;color:var(--muted);white-space:nowrap}}
  .kick a{{color:inherit;text-decoration:none}}
  .kick a:hover{{color:var(--chalk)}}
  .digest{{border:1px solid var(--hair);border-left:3px solid var(--ucl);border-radius:10px;background:var(--card);padding:18px 22px;margin-bottom:26px;max-width:760px}}
  .digest .dh{{font-family:var(--disp);font-weight:800;font-size:20px;line-height:1.25;margin:0 0 8px}}
  .digest p{{font-size:15px;line-height:1.7;color:var(--soft);margin:0 0 10px}}
  .digest p:last-of-type{{margin-bottom:0}}
  .dby{{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;color:var(--muted);margin-top:12px;padding-top:10px;border-top:1px solid var(--hair)}}
  .meta{{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em;margin-top:6px}}
  .snote{{font-family:var(--mono);font-size:11px;color:var(--muted);margin:-4px 0 12px;letter-spacing:.03em}}
  .blist{{list-style:none;padding:0;margin:0 0 30px;display:grid;gap:10px}}
  .bitem{{border:1px solid var(--hair);border-radius:10px;padding:13px 16px;background:var(--card)}}
  .bitem:hover{{border-color:var(--hair2)}}
  .bt{{font-family:var(--body);font-weight:600;font-size:15px;line-height:1.4;color:var(--chalk);text-decoration:none}}
  .bt:hover{{text-decoration:underline}}
  .bs{{font-size:13.5px;line-height:1.6;color:var(--soft);margin:5px 0 0}}
  .bmeta{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:9px;font-family:var(--mono);font-size:10.5px;letter-spacing:.05em}}
  .src{{color:var(--muted);text-transform:uppercase}}
  .corr{{color:var(--ucl);border:1px solid var(--hair);border-radius:999px;padding:1px 6px}}
  .wtag{{color:var(--soft);background:var(--wash);border-radius:999px;padding:1px 8px}}
  .ferr{{color:var(--l1)}}
  footer{{margin-top:40px;border-top:1px solid var(--hair);padding-top:14px;font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.7}}
  @media(max-width:640px){{
    .head-row{{flex-wrap:wrap;align-items:flex-start}}
    .head-actions{{width:100%;justify-content:flex-start}}
    h1{{white-space:normal}}
    .eyebrow{{flex-wrap:wrap;gap:8px 12px}}
  }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="head-row">
    <div>
      <div class="kick"><a href="index.html">Matchday Pacific</a> <span class="hand">— Daily Brief</span></div>
      <h1>Daily <span class="pac">Brief</span></h1>
    </div>
    <div class="head-actions">
{nav()}
    </div>
  </div>
  <p class="sub">What the transfer desks and analysts are saying today — every line attributed to the outlet that ran it, nothing here confirmed by this page.</p>
  <div class="meta">{now.strftime('%A, %B %-d, %Y')} · {len(blob['items'])} items from {len(srcs)} feeds · pulled {esc(fetched[:16].replace('T',' '))}Z</div>
</header>

<section>
{leadhtml}{section('Rumour Mill', 'attributed · unconfirmed', rumours, 'Reports, not facts. ×N marks a story carried by more than one outlet.')}
{section('Around the Grounds', 'news', news)}
{section('Worth Reading', 'analysis', reads)}
</section>

<footer>
  Aggregated from {esc(', '.join(srcs))}. Headlines and links belong to their publishers; follow the link for the full story.{errnote}<br>
  Transfer rumours are wrong more often than they are right — treat everything above as reported, not settled.<br>
  Part of <a href="index.html" style="color:inherit">Matchday Pacific</a> · <a href="guide.html" style="color:inherit">viewing guide</a> · <a href="cal.html" style="color:inherit">calendar</a>
</footer>

</div>
<script>
document.getElementById('themeToggle').addEventListener('click',function(){{
  var next=document.documentElement.dataset.theme==='dark'?'light':'dark';
  document.documentElement.dataset.theme=next;
  try{{localStorage.setItem('mdcal-theme',next);}}catch(e){{}}
}});
</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} — {len(rumours)} rumours, {len(news)} news, {len(reads)} reads")


if __name__ == "__main__":
    main()
