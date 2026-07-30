# street-guide.html — state as of 2026-07-30

Resume file. Read this plus `CLAUDE.md` before touching the guide.

## Where it stands
- **135 figures**, 12 lessons, HTML valid, TOC/jump-menu consistent (12 sections ↔ 12 TOC entries).
- **76 distinct photographers**, six continents.
- Source split: **65 archive/museum · 70 living photographers** (hotlinked, in copyright).
- **Counts no longer appear in the prose** (Sadh, 2026-07-30: "is the number correct? do we need to
  specify the number?"). They were stated in the lede, the intro block and the index card and had to
  be kept in sync by hand. Do not reintroduce them. Numbers that carry an argument stay — the FSA's
  171,074 negatives (still cited twice, in §06 and §Sources), the 40:1 response spread.
- **The `#howtoread` intro block is DELETED** (Sadh, 2026-07-30: "this whole section is bullshit").
  It had already been rewritten once as "Reading old photographs" and that was not enough — the
  problem was the block existing at all, not its wording. The lede is now two sentences and the page
  goes straight into the TOC. **Do not write a new one.** Also deleted with it: the sentence
  describing the guide's own sourcing ("The photographs run from the 1850s to this year, half out of
  public archives and half from…"), flagged as meta in the same pass, and the `.standfirst` line
  about the optics being computed. `.standfirst` CSS removed as dead; `.caveat` kept (still used).
- **18 annotation studies** (inline SVG over untouched originals, toggleable + `a` key). Three added
  2026-07-30 on the **local public-domain files**, which is the trick when the CDNs are unreachable —
  `img/` can be opened with PIL and measured, so a sandbox with no network can still produce studies:
  `annoPanier` (Atget *Marchand du Panier*, §01 takeaway — seller 51% / customer 54% / onlooker 34%
  of frame height), `annoTerminal` (Stieglitz *The Terminal*, §05 takeaway — near / event / far
  markers on the three planes), `annoOrgue` (Atget *Joueur d'orgue*, §02 fig-row — her thrown-back
  head and flung arm against the grinder holding still). All heights and positions were measured off
  a rendered percent grid and checked against a PIL mock-up before any HTML was written.
  **Labels must be short.** `.anno-label` is `.62rem` and does *not* scale with the image, so a
  6–12 character label ("seller 51%", "the peak", "near") is legible at 384px and a 30-character one
  is not. That, not the annotation itself, is what forces a study to full width — see figure rhythm.
  Seven earlier ones added
  2026-07-30: `annoGiza` (Majali, four peaks + the monument doing nothing), `annoFrieze`
  (Abdolahabadi, five compartments + one ground line), `annoFerris` (the crop, the kerb line, the
  foot landing on it), `annoArgolo` (42% vs 21% head heights), `annoNarula` (23% lit slot, two
  issued colours), `annoTofanelli` (four warm sources = 6% of frame), `annoVapour` (the cloud, the
  empty two-thirds). **An annotated figure can live inside a `.fig-row` pair** — three of the
  originals already did, and the lightbox clones the overlay at full size, so annotating does not
  require promoting a figure to full column.
- **Figure rhythm (Sadh, 2026-07-30 — "we already have lightbox to see full image, but on the
  article keep images half row width"):** measured at 1280px wide, verified in-browser —
  - `.fig-study` **592px** (`--measure`) — the only wide class. **8 figures: the 5 full-column
    annotation studies + 3 drawn diagrams.** They keep the text measure because `.anno-label` is
    sized in `rem` and does *not* scale with the image; below ~592px the labels overlap the frame.
  - `.fig-narrow` **384px** (`--half`, 24rem) — every solo photograph. Was 592px.
  - `.fig-row` **365–388px** — two-up pairs, unchanged, and now the same scale as a solo figure.
  - `.gal` **300px** — masonry shelves, unchanged.
  - Bare `<figure>` inside `.takeaway` → 384px via `.takeaway figure`. **This was the actual bug
    behind "why is this image big?"** — `.takeaway` is `max-width:var(--wide)`, so an unclassed
    figure in a "Carry this" box rendered at ~774px, wider than anything else on the page.
  **Do not put a photograph at `.fig-study`.** The lightbox is the full-size view; the article body
  never needs to be. Pairing script kept at `gen/_gemini-pipeline/pair-figures.py` — line-based,
  never regex across `</figure>`.
- Simulator, topbar, lightbox (covers every figure, carries annotation overlays), scroll reveal, noscript — all working.
- Local server: `preview_start {name:"photoing"}` → port 8873.

## Rulings from Sadh — these override defaults
1. **Hotlink copyrighted images.** Stated three times. Fair use for criticism; every figure carries photographer, place/series, "© the photographer, shown here for critical commentary", and a source link. Do not retreat to PD-only.
2. **"Copyright-free" is not neutral** — it is what governments funded and museums kept. This still governs *sourcing*: prefer living photographers' own sites over archives. But it is **no longer argued on the page** — the `#howtoread` block that carried it was deleted 2026-07-30 as "bullshit". Treat it as a rule for picking frames, not as copy to reinstate.
3. **Children rule applies to frames Sadh makes, not to citing published work.** Bhalotia's *Flying Boys* is in on that basis. Still exclude: frames whose interest IS someone's misfortune.
4. **Ethics are culturally specific** — the Turpin/in-Public rule is labelled as one British collective's position, not universal. §Ethics carries the Shahidul Alam counter-argument about who gets to decide.
5. **No museum-anchor requirement.** Contest records, platform reach and collectives count. This filter had excluded Rimita Sen, Sarmistha Bera, Roopsha Samanta — all now on the page.
6. **Pick the representative frame, not the polite one.** I had chosen Dakowicz's Superman out of a book about drunken nightlife. Confrontational, raw, grainy, sexual, intoxicated subjects are all in scope.
7. **Aim ≥25 distinct photographers**; more examples is better than fewer.
8. He is an **amateur who wants to get much better** — do not build anything that flatters four Reddit scores.
9. **Never let the page explain itself.** 2026-07-30: "how to read the images disclaimer reads like an
   AI explaining itself, there are many such meta comments, which can be removed." Thirty were removed.
   Banned shapes: "it belongs in this lesson because…", "chosen because…", "the case study behind this
   lesson…", "which is how the shelves on this page were built", "X is the second and last figure in
   this guide". Write the observation, not the reason it was included. Still allowed: the TOC label,
   the "Diagram drawn for this guide" credit, and cross-references like "Lesson 09 gathers them by name".
10. **Images stay small in the body; the lightbox is the full view.** See figure rhythm above.

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
- Six more SVG annotation studies wanted (Sadh: "a lot of SVG based annotations"; 2026-07-30 named
  `tile.loc.gov/…/fsac/1a33000/1a33900/1a33932r.jpg`, the Delano staircase street, as a candidate —
  it is public domain, so a baked overlay would be legal, but keep the SVG-over-untouched pattern for
  the toggle and the lightbox clone). Also gridded and ready: Abdolahabadi panorama, Majali Giza.
  Method: render a percent grid with PIL, read coordinates, verify by drawing locally, then emit SVG.
  **Still blocked 2026-07-30:** the sandbox network policy answers 403 to CONNECT for `tile.loc.gov`,
  `images.squarespace-cdn.com` and `arabnews.com`, so those source pixels cannot be fetched.
  Coordinates must be measured, never estimated — see the swapped-Delano and invented-URL entries
  above. Do the *hotlinked* ones from an environment that can reach the CDNs. Meanwhile the three
  local public-domain files were annotated instead (see above) — check `img/` first before declaring
  this blocked.
- ~~CHANGELOG needs a 5.0.0 entry~~ — present, and 5.1.0 covers the 2026-07-30 editing pass.
- `photoing/` **is** git-committed as of 2026-07-30 (branch `claude/street-guide-review-lsoe7b`), so
  `git checkout HEAD -- <file>` is a real undo for images. Earlier note said otherwise; it was stale.
