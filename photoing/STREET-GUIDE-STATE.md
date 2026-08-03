# street-guide.html — state as of 2026-07-31

Resume file. Read this plus `CLAUDE.md` before touching the guide.

## Where it stands
- **135 figures** (136 `<figure>` elements — the extra one is the `#kit` hyperfocal diagram, the
  only figure whose graphic is an inline `<svg>` with no `<img>`), 13 lessons, HTML valid,
  TOC/jump-menu consistent (13 sections ↔ 13 TOC entries ↔
  13 jump-menu items; the jump menu auto-builds from `.lesson`, but the TOC `<li>` and the
  `.lesson-num` text are both manual — update all three when adding a section).
- **76 distinct photographers**, six continents.
- Source split: **65 archive/museum · 70 living photographers** (the living side hotlinked, in
  copyright). The split is by source, not hosting — mirroring the Delano staircase (2026-07-31)
  retired its hotlink, but it was archive before and after, so the numbers did not move. (An
  earlier draft of this line said 66 · 69; that confused the two axes.)
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
- **Two annotation mechanisms, both default-on.** 17 figures use inline SVG overlays; the 4 local
  public-domain frames are **baked** — annotations painted into `img/street-*-anno.jpg` with PIL, and
  the button swaps `src` between the baked file and the untouched original via `data-annotated` /
  `data-original` on the `<img>`, marked `class="anno anno-baked"` with **no `.anno-layer`**. The
  lightbox handles both: it clones a layer when one exists, otherwise it swaps `lbImg.src` and tracks
  `lbImg.dataset.state`. **Any code touching `.anno` must not assume `.anno-layer` exists** — that
  null deref is the trap. Baking rebuild: the bake script mirrors the SVG coordinates and the
  `.anno-label` CSS at `scale = 1200/384 = 3.125` (font 31px, stroke 5px), using
  `JetBrainsMono-Bold.ttf` — the page's actual font, so baked and SVG labels match. If a baked
  frame's geometry changes, re-bake *and* update nothing else; there is no SVG left on those four
  to keep in sync. **The bake and the SVG now come from one spec**, `gen/_gemini-pipeline/anno.py`
  (`svg()` and `bake()` read the same path/label lists), with the three 2026-07-31 specs kept in
  `gen/anno-src/specs/`. The old note pointed the font at `/mnt/skills/…`, a sandbox path that does
  not exist locally — fetch it from the JetBrainsMono GitHub release, and make a venv for Pillow
  and numpy, neither of which is in this Mac's system Python.
- **Annotation reads are ON by default** (Sadh, 2026-07-30: "show annotations by default / make the
  button -> show original / show the read"). CSS is `.anno .anno-layer{opacity:1}` with `.anno-off`
  hiding it — the old `.anno-on` class is gone, do not reintroduce it. Button labels name the *state's
  alternative*: "Show original" while the overlay is up, "Show the read" once hidden. The lightbox
  button follows the same rule and inherits the inline figure's state.
- **13 lessons** as of 2026-07-30 — Lesson 11 **"Kit and settings"** (`#kit`) was added, pushing
  drills to 12 and ethics to 13. `CLAUDE.md` says "do not talk about gear beyond the focal-length
  argument"; **Sadh overrode that** ("we probably need to add sections dedicated for x100vi and om-1
  with 12-40mm lens"). The section reuses numbers from the repo's own camera guides rather than
  recalled specs — X100VI f/8 hyperfocal 3.3 m → 1.65 m–∞, leaf shutter capped at 1/2000 at f/2
  (hence the 4-stop ND), OM-1 ProCapture keeping 70 pre-press frames, 12–40 at 0.3×. **Check
  `x100vi-guide.html` and `om1-guide.html` before writing any spec into this page.**
  The section leads on **zone focus**: the hyperfocal expression with `c` named as a print-size
  convention rather than physics, a hyperfocal table, why f/8 specifically (it is the first stop
  whose near limit falls under 2 m, i.e. inside conversational distance), the diffraction/near-limit
  trade at f/11, and the honest limit — f/8 needs daylight, so at blue hour the zone collapses and
  you are back on AF. Carries an **inline-SVG diagram** (`#kit figure svg`, no raster file): one
  focus distance at 2.5 m, four apertures, bars showing 0.97 m of depth at f/2 against 8.3 m at f/8.
  Rebuild numbers with `H = f²/(N·c) + f`, `near = Hs/(H+s−f)`, `far = Hs/(H−s+f)`.
  **Watch the viewBox.** A root `<svg>` computes `overflow:hidden`, so anything drawn past the
  viewBox is **clipped and silently disappears** — the f/8 value label rendered as "1.43 – 9" with
  the rest cut off, and had to move inside its bar. (An earlier version of this note said the
  opposite; it was wrong. Verified: default `<svg>` → `getComputedStyle().overflow === 'hidden'`;
  add `overflow:visible` and the same text spills outside the box instead.)
  **Audit method — do not use `getBBox()` for this.** `getBBox()` returns a bbox in the element's
  *own* user space and ignores ancestor transforms, so it reports dozens of false positives on any
  SVG that uses `<g transform>`. Compare `el.getBoundingClientRect()` against the `<svg>`'s own
  `getBoundingClientRect()` instead; that accounts for transforms and matches what renders.
  Audited across all 17 SVGs on the page: **the only genuine clipping is in `#distsim`**, where
  background figures get cropped at the panel edge at long focal lengths. That is intentional — the
  panel is captioned "what the frame holds", and a frame cropping its edges is the point.
- **Titles: plain, not poetic** (Sadh, 2026-07-30: *"just use less poetic titles. I am a poet who
  doesn't like poetics."*). "The two bodies, worked" became "Kit and settings"; its subheads are
  "Zone focus, and why f/8", "X100VI", "OM-1 with the 12–40", "Which camera, when". The older lesson
  titles ("Fishing, not hunting", "Distance is the medium") were not in scope and are untouched —
  ask before restyling them. **New sections get functional titles.**
- **21 annotation studies** (toggleable + `a` key). **Three added 2026-07-31 from a local session**,
  clearing the queue that the web sandbox's 403-on-CONNECT had blocked:
  `annoStaircase` (Delano, *Charlotte Amalie*, §01 — **baked**, and the frame is now a local mirror,
  so the LoC hotlink is retired: walker 4% of frame height against the street's 62%, the honest
  counter-example to the Vachon it is paired with);
  `annoCape` (Dakowicz, *Superman*, §04 — SVG, hotlink kept: a rect on the man labelled "the
  variable", a polyline down the double yellow line labelled "always there");
  `annoCarpool` (Cartagena, *Carpoolers* #10, §04 — SVG, hotlink kept: a teal rect on the truck bed
  labelled "the cast", dashed ink on both lane markings labelled "every frame").
  The two §04 studies sit in one `.fig-row` and deliberately carry the same fixed/variable read.
  **Stroke colours were chosen for legibility, not convention** — see the ruling below.
  Three earlier ones added
  2026-07-30 on the **local public-domain files**, which was the trick when the CDNs were unreachable —
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
  originals already did, all three of the 2026-07-31 additions do, and the lightbox clones the
  overlay at full size, so annotating does not require promoting a figure to full column.
- **Stroke colour is a legibility decision, not a palette one** (2026-07-31). The usual reading is
  accent `#b8422a` = the subject, street `#2e6e62` = the structural read, ink `#1a1610` dashed =
  fixed context. Cartagena's frame breaks it: accent red vanishes on a red pickup, and ink
  disappeared into the shadow line under the cab — verified on a mock-up, twice. The bed took the
  street teal and the lane markings the dashed ink, and the label classes followed the strokes.
  **Judge the colour off the mock-up before writing the HTML**; a mark nobody can see is worse than
  an unconventional one.
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
   **A second sweep found fourteen more that grep missed**, because they name no lesson and no guide.
   Four shapes to watch for: *process narration* ("every link below was fetched and confirmed to
   load", "Availability was checked"); *inclusion justification* ("which is why he is in the
   syllabus", "The reference case for this whole lesson", "and both belong here"); *structural
   self-reference* ("This is the paragraph above, executed", "the way the field decks isolate one
   scene per card"); *UI narration* ("Turn the read on and the fifth box is the point"). **Grep is
   not enough — extract the prose and read it.** Script that works: pull every `<p>` and
   `<figcaption>`, strip tags, print in blocks, read them.
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
  **2026-07-31: still blank on the real page even with `scrollBehavior='auto'` and reveal opacity forced**
  (the page is now ~80,000px). What worked: write a throwaway page under `photoing/` containing the
  page's `<style>` plus only the `<figure>` blocks under test, and screenshot that — it renders
  immediately and is the only way an annotation has been visually confirmed in-browser. Delete it after.

## Hotlink map (tested with a sadh.app referer)
Works: `tile.loc.gov`, `images.metmuseum.org`, `openaccess-cdn.clevelandart.org`, `upload.wikimedia.org`, `live.staticflickr.com`, `content.magnumphotos.com`, `images.squarespace-cdn.com`, `static1.squarespace.com`, `static.wixstatic.com`, `static-assets.artlogic.net`, `format.creatorcdn.com`, `cdn.prod.website-files.com`, `assets.yesstud.io`, `121clicks.com`, `arabnews.com`, `1854.photography`, `nickturpin.com`, `maciejdakowicz.com`, `siegfried-hansen.de`, `yusufsevincli.com`, `shinnoguchiphotography.com`, `agencevu.com`, `circuitgallery.com`, `burnmagazine.org`, `lenscratch.com`, `independent-photo.com`, `streetphotographersfoundation.com`, `joanachoumali.com`, `melissaoshaughnessy.com`, `vivianmaier.com`.
Blocked/unusable: Instagram (signed URLs), `preview.redd.it` (403), `www.artic.edu` (curl 200 but fails in real browsers — its 3 CC0 frames are mirrored into `img/`), `cdn.myportfolio.com` (400 without its `?h=` hash), `cdn.magazine.exposuresop.com` (403 on referer), MoMA/NGA/Getty (bot-blocked).
Notes: LoC metadata API rate-limits hard (~40 req/10 min); the tile CDN never blocks. Adobe Portfolio needs its `?h=` content hash. `format.creatorcdn.com` signatures are bound to the crop segment — cannot be resized.
LoC full-res: `…/storage-services/service/pnp/…/NNNNNNNr.jpg` is only ~450px. For a mirror, swap `service`→`master` and `r.jpg`→`u.tif` (`…/master/pnp/fsac/1a33000/1a33900/1a33932u.tif` = 3807×5432, 62 MB). `www.loc.gov/…?fo=json` is behind a Cloudflare challenge and 403s, so do not plan on the metadata API. **Kodachrome scans carry the black slide mount with rounded corners** — the 1a33932 image area was x 141–3627, y 100–5265 of 3807×5432, cropped at (231, 190, 3537, 5175) to clear the corner radius; crop before measuring or every percentage is against the holder.

## Open threads
- **`beside-the-streets.html`** — approved, not started. Outline: thumbnail truth · the graphic frame · negative space · scale figure · light as subject · time as material (long exposure) · return to one place · the edit · where it fails. Key source: **Ansel Adams's 1941–42 Dept of the Interior work is public domain** (US Government work) at the National Archives. Research agent running.
- ~~Embed the 12 verified frames from `gen/PENDING-FRAMES.md`~~ — **done 2026-07-30**, 10 embedded, 2 skipped as duplicate photographers.
- ~~Six more SVG annotation studies (Sadh: "a lot of SVG based annotations")~~ — **the named queue is
  done as of 2026-07-31**: Delano staircase (baked, mirrored), Dakowicz *Superman*, Cartagena
  *Carpoolers*; Abdolahabadi and Majali were already done 2026-07-30. That is 21 studies. The
  network block that stalled this was a web-sandbox policy only; from a local session `tile.loc.gov`,
  `maciejdakowicz.com`, `circuitgallery.com`, `images.squarespace-cdn.com` and `arabnews.com` all
  answer 200. If more are wanted, the constraint is now editorial, not technical — pick frames whose
  read is a *measurement*, since that is what separates these from decoration.
- **One hotlink fails in this in-app browser but not elsewhere**: Tavepong Pratoomwong's *Tree Man*,
  `live.staticflickr.com/7457/14060758691_90162ba1e5_b.jpg` (§ the contest-record shelf, line ~1470).
  curl returns 200 / 163 KB with any referer or none, and the file opens fine in a browser tab on its
  own — it only fails as a subresource of the localhost page, so the `img-dead` fallback fires and the
  figure shows "frame unavailable". Same signature as the `www.artic.edu` entry below. **Not
  introduced by the 2026-07-31 pass and not changed** — check it on real `sadh.app` before deciding
  whether to mirror or drop it.
- ~~CHANGELOG needs a 5.0.0 entry~~ — present, and 5.1.0 covers the 2026-07-30 editing pass.
- `photoing/` **is** git-committed — the street-guide work is on `main` as of 2026-07-31 — so
  `git checkout HEAD -- <file>` is a real undo for images. (The 2026-07-30 note named branch
  `claude/street-guide-review-lsoe7b`; it has since landed on `main`.)
