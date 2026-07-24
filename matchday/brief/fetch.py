#!/usr/bin/env python3
"""Pull the daily football firehose into one deduped, source-tagged JSON blob.

Deliberately dumb: fetch, parse, tag, dedupe. No judgement about what matters —
that happens downstream, where claims can be checked before anything is published.

    python3 fetch.py            -> gen/brief/feed.json
    python3 fetch.py --print    -> also dump a readable digest to stdout
"""
import json, re, sys, html, urllib.request, urllib.error
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
OUT = HERE / "feed.json"
UA = "Mozilla/5.0 (compatible; matchday-brief/1.0; +https://sadh.app/matchday)"

# tier: 1 = attributed rumour digest, 2 = news/confirmation, 3 = analysis
FEEDS = [
    ("BBC Gossip",      "https://feeds.bbci.co.uk/sport/football/gossip/rss.xml", 1, "rumour"),
    ("Sky Transfers",   "https://www.skysports.com/rss/11095",                    1, "rumour"),
    ("BBC Sport",       "https://feeds.bbci.co.uk/sport/football/rss.xml",        2, "news"),
    ("Guardian",        "https://www.theguardian.com/football/rss",               2, "news"),
    ("Sky Sports",      "https://www.skysports.com/rss/12040",                    2, "news"),
    ("Opta Analyst",    "https://theanalyst.com/feed",                            3, "analysis"),
    ("FourFourTwo",     "https://www.fourfourtwo.com/feeds/all",                  3, "analysis"),
    ("Transfermarkt",   "https://www.transfermarkt.com/rss/news",                 3, "data"),
]

# clubs the app actually tracks — used only to mark relevance, never to drop items
WATCH = ["PSG","Paris Saint-Germain","Bayern","Real Madrid","Man City","Manchester City",
         "Arsenal","Liverpool","Barcelona","Atletico","Atlético","Chelsea","Man United",
         "Manchester United","Tottenham","Dortmund","Inter","Juventus","Napoli","Milan",
         "Marseille","Lyon","Ajax","PSV","Porto","Sporting","Celtic","Galatasaray"]


def strip(s):
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", "", html.unescape(s or ""))).strip()


def when(item):
    for tag in ("pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}updated"):
        raw = item.findtext(tag)
        if not raw:
            continue
        try:
            return parsedate_to_datetime(raw).astimezone(timezone.utc).isoformat()
        except Exception:
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return None


def pull(name, url, tier, kind):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    items = root.iter("item") or []
    out = []
    for it in items:
        title = strip(it.findtext("title"))
        if not title:
            continue
        out.append({
            "source": name, "tier": tier, "kind": kind,
            "title": title,
            "summary": strip(it.findtext("description"))[:600],
            "link": (it.findtext("link") or "").strip(),
            "published": when(it),
        })
    # Atom fallback (no <item>)
    if not out:
        ns = "{http://www.w3.org/2005/Atom}"
        for e in root.iter(ns + "entry"):
            title = strip(e.findtext(ns + "title"))
            if not title:
                continue
            link = ""
            for l in e.iter(ns + "link"):
                link = l.get("href") or link
            out.append({"source": name, "tier": tier, "kind": kind, "title": title,
                        "summary": strip(e.findtext(ns + "summary"))[:600],
                        "link": link, "published": when(e)})
    return out


def key(entry):
    """Loose identity so the same story from two outlets collapses to one."""
    t = re.sub(r"[^a-z0-9 ]", "", entry["title"].lower())
    return " ".join(sorted(t.split()))[:110]


def main():
    items, errors = [], []
    for name, url, tier, kind in FEEDS:
        try:
            got = pull(name, url, tier, kind)
            items += got
            print(f"  {name:<16} {len(got):>3} items", file=sys.stderr)
        except Exception as e:
            errors.append({"source": name, "url": url, "error": f"{type(e).__name__}: {e}"})
            print(f"  {name:<16}  !! {type(e).__name__}", file=sys.stderr)

    seen, deduped = {}, []
    for e in items:
        k = key(e)
        if k in seen:
            seen[k]["also"] = sorted(set(seen[k].get("also", []) + [e["source"]]))
            continue
        e["watch"] = sorted({w for w in WATCH if w.lower() in (e["title"] + " " + e["summary"]).lower()})
        seen[k] = e
        deduped.append(e)

    deduped.sort(key=lambda e: (e["tier"], e["published"] or ""), reverse=False)
    blob = {
        "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {"raw": len(items), "deduped": len(deduped),
                   "byTier": {t: sum(1 for e in deduped if e["tier"] == t) for t in (1, 2, 3)}},
        "errors": errors,
        "items": deduped,
    }
    OUT.write_text(json.dumps(blob, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(deduped)} unique of {len(items)} raw -> {OUT}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} feed(s) FAILED — see errors[] in the json", file=sys.stderr)

    if "--print" in sys.argv:
        for e in deduped[:40]:
            tag = f"[T{e['tier']} {e['source']}]"
            mark = " ★" + ",".join(e["watch"]) if e["watch"] else ""
            print(f"{tag:<26}{e['title'][:96]}{mark}")


if __name__ == "__main__":
    main()
