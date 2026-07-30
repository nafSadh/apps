# street-guide.html — state as of 2026-07-30

Resume file. Read this plus `CLAUDE.md` before touching the guide.

## Where it stands
- **135 figures**, 12 lessons, all loading (verified in-browser, 0 broken), HTML valid, TOC/jump-menu consistent.
- **76 distinct photographers**, six continents.
- Source split: **65 archive/museum · 70 living photographers** (hotlinked, in copyright).
- The intro lede, the `#howtoread` block and the index card all state these numbers — **if the count
  changes, update all three.** The lede previously claimed "almost every frame predates 1943"; that
  stopped being true and is now "roughly half".
- **15 annotation studies** (inline SVG over untouched originals, toggleable + `a` key). Seven added
  2026-07-30: `annoGiza` (Majali, four peaks + the monument doing nothing), `annoFrieze`
  (Abdolahabadi, five compartments + one ground line), `annoFerris` (the crop, the kerb line, the
  foot landing on it), `annoArgolo` (42% vs 21% head heights), `annoNarula` (23% lit slot, two
  issued colours), `annoTofanelli` (four warm sources = 6% of frame), `annoVapour` (the cloud, the
  empty two-thirds). **An annotated figure can live inside a `.fig-row` pair** — three of the
  originals already did, and the lightbox clones the overlay at full size, so annotating does not
  require promoting a figure to full column.
- **Figure rhythm (Sadh's call, 2026-07-30 — "most new photos are added at full col… too big"):**
  full column (`.fig-narrow`, 592px) is reserved for the annotation studies and roughly one
  opening frame per lesson. Everything else pairs into `.fig-row` two-ups at ~380px, and the
  masonry `.gal` shelves run ~300px. **Three scales, in that order. Do not add a run of
  full-column figures.** Page height is 51,959px at 1280px wide; it was 103,947px before pairing.
  Pairing script kept at `gen/_gemini-pipeline/pair-figures.py` — line-based, never regex across
  `</figure>`. Re-runnable: it only touches figures still carrying `class="fig-narrow"`.
- Simulator, topbar, lightbox (covers every figure, carries annotation overlays), scroll reveal, noscript — all working.
- Local server: `preview_start {name:"photoing"}` → port 8873.

## Rulings from Sadh — these override defaults
1. **Hotlink copyrighted images.** Stated three times. Fair use for criticism; every figure carries photographer, place/series, "© the photographer, shown here for critical commentary", and a source link. Do not retreat to PD-only.
2. **"Copyright-free" is not neutral** — it is what governments funded and museums kept. This argument is on the page in the `#howtoread` intro block. Prefer living photographers' own sites over archives.
3. **Children rule applies to frames Sadh makes, not to citing published work.** Bhalotia's *Flying Boys* is in on that basis. Still exclude: frames whose interest IS someone's misfortune.
4. **Ethics are culturally specific** — the Turpin/in-Public rule is labelled as one British collective's position, not universal. §Ethics carries the Shahidul Alam counter-argument about who gets to decide.
5. **No museum-anchor requirement.** Contest records, platform reach and collectives count. This filter had excluded Rimita Sen, Sarmistha Bera, Roopsha Samanta — all now on the page.
6. **Pick the representative frame, not the polite one.** I had chosen Dakowicz's Superman out of a book about drunken nightlife. Confrontational, raw, grainy, sexual, intoxicated subjects are all in scope.
7. **Aim ≥25 distinct photographers**; more examples is better than fewer.
8. He is an **amateur who wants to get much better** — do not build anything that flatters four Reddit scores.

## Mistakes made, do not repeat
- **A regex with `.*?</figure>` under `re.S` deleted six lesson sections.** Always anchor removal by walking back from the matched `<img>` to its own `<figure>`. Recovery method that worked: replay Write+Edit+Bash steps from the session JSONL onto the last good Write.
- **I invented URL characters** where a report truncated long CDN hashes with "…". Never reconstruct an identifier not seen in full; ask for it verbatim.
- **I swapped two Delano frames** (`fsac.1a33939` is the Coca-Cola street, `1a33945` is the raking-light sidewalk) and captioned the wrong one. Verify image↔caption by viewing.
- **`og:image` scraping returns book covers, headshots and favicons** — never use it to pick a photograph.
- **Browser screenshots came back blank/stale after scrolling** for a long time. Cause found: the page
  sets `scroll-behavior:smooth`, so a `window.scrollTo` of 76,000px never arrives. Set
  `document.documentElement.style.scrollBehavior='auto'` first. Even then this harness's screenshot
  often lags — verify layout by reading `getBoundingClientRect()` and `naturalWidth` off the DOM instead.

## Hotlink map (tested with a sadh.app referer)
Works: `tile.loc.gov`, `images.metmuseum.org`, `openaccess-cdn.clevelandart.org`, `upload.wikimedia.org`, `live.staticflickr.com`, `content.magnumphotos.com`, `images.squarespace-cdn.com`, `static1.squarespace.com`, `static.wixstatic.com`, `static-assets.artlogic.net`, `format.creatorcdn.com`, `cdn.prod.website-files.com`, `assets.yesstud.io`, `121clicks.com`, `arabnews.com`, `1854.photography`, `nickturpin.com`, `maciejdakowicz.com`, `siegfried-hansen.de`, `yusufsevincli.com`, `shinnoguchiphotography.com`, `agencevu.com`, `circuitgallery.com`, `burnmagazine.org`, `lenscratch.com`, `independent-photo.com`, `streetphotographersfoundation.com`, `joanachoumali.com`, `melissaoshaughnessy.com`, `vivianmaier.com`.
Blocked/unusable: Instagram (signed URLs), `preview.redd.it` (403), `www.artic.edu` (curl 200 but fails in real browsers — its 3 CC0 frames are mirrored into `img/`), `cdn.myportfolio.com` (400 without its `?h=` hash), `cdn.magazine.exposuresop.com` (403 on referer), MoMA/NGA/Getty (bot-blocked).
Notes: LoC metadata API rate-limits hard (~40 req/10 min); the tile CDN never blocks. Adobe Portfolio needs its `?h=` content hash. `format.creatorcdn.com` signatures are bound to the crop segment — cannot be resized.

## Open threads
- **`beside-the-streets.html`** — approved, not started. Outline: thumbnail truth · the graphic frame · negative space · scale figure · light as subject · time as material (long exposure) · return to one place · the edit · where it fails. Key source: **Ansel Adams's 1941–42 Dept of the Interior work is public domain** (US Government work) at the National Archives. Research agent running.
- ~~Embed the 12 verified frames from `gen/PENDING-FRAMES.md`~~ — **done 2026-07-30**, 10 embedded, 2 skipped as duplicate photographers.
- Six more SVG annotation studies wanted (Sadh: "a lot of SVG based annotations"). Gridded and ready: Abdolahabadi panorama, Majali Giza. Method: render a percent grid with PIL, read coordinates, verify by drawing locally, then emit SVG.
- CHANGELOG needs a 5.0.0 entry covering the contemporary-photographer expansion.
- Nothing in `photoing/` is git-committed. Do not commit without being asked.
