# street-guide.html — state as of 2026-07-30

Resume file. Read this plus `CLAUDE.md` before touching the guide.

## Where it stands
- **135 figures**, 13 lessons, HTML valid, TOC/jump-menu consistent (13 sections ↔ 13 TOC entries ↔
  13 jump-menu items; the jump menu auto-builds from `.lesson`, but the TOC `<li>` and the
  `.lesson-num` text are both manual — update all three when adding a section).
- **76 distinct photographers**, six continents.
- **Lesson 09 (`#living`) carries Wikipedia links** as of 2026-07-31 — a second link in the `.work`
  line, `view · wikipedia`, on the 26 of 40 entries whose subject has an English article. Two rules
  bind any future additions here. **Verify the article exists before linking; never build a URL from
  a name** — Nils Jorgensen has no article, but an article at his name does exist and is about a
  Norwegian fencer. And **check the disambiguator**: Daniel Arnold, Yolanda Andrade, Matt Stuart,
  Alex Webb, Siegfried Hansen and Tatsuo Suzuki all need the `(photographer)`-style title because a
  different subject holds the bare name. Unlinked today, for want of an article: Julia Coddington,
  Debrani Das, Nils Jorgensen, Melissa O'Shaughnessy, Rohit Vohra, Gustavo Minas, Pau Buscató,
  Tavepong Pratoomwong, Jonathan Higbee, Sandra Cattaneo Adorno, Ismail Ferdous, Alan Schaller,
  Women Street Photographers, Unexposed Collective. (Wikipedia is unreachable from the web sandbox —
  `403` to CONNECT — so verification ran through WebSearch, not fetches.)
- **`street-guide-CITATIONS-PLAN.md` is the open provenance backlog** (approved by Sadh 2026-07-31,
  not yet implemented): 28 unsubstantiated *subjective* claims — quotes, method stories, legal
  characterizations — plus the planned endnote/hover-card/glossary mechanism. Numeric and computed
  claims are out of scope by his ruling.
- Source split: **65 archive/museum · 70 living photographers** (hotlinked, in copyright).
- **Counts no longer appear in the prose** (Sadh, 2026-07-30: "is the number correct? do we need to
  specify the number?"). They were stated in the lede, the intro block and the index card and had to
  be kept in sync by hand. Do not reintroduce them. Numbers that carry an argument stay — the FSA's
  171,074 negatives (still cited twice, in §06 and §Sources).
- **The 40:1 response spread is OFF the page** (Sadh, 2026-07-31: "40:1 is not something we should
  have in the guide then"). It opened §06 as an anonymised account of his own posted record — one
  photographer, one city, one bag — which made it both unverifiable to a reader and a reintroduction
  of the frames the guide deliberately removed. The paragraph now carries the same point on the
  page's own terms (the gap is what light and angle were allowed to do before the shutter opened),
  with no number. The 40:1 fact stays true in `CLAUDE.md`'s diagnosis section, which is background
  for whoever writes here — it is just not a claim the page makes. **Do not reintroduce it**, and
  treat it as the precedent for any other number sourced only to Sadh's own record.
- **Glossary cards are BUILT** (2026-07-31). Eight house terms are marked on first use with
  `<a class="gterm" href="#gloss-…">`, and a **Provenance** block at the end of §09 holds the
  definitions in a `<dl class="study prov">`. A single shared `#pcard` popover clones the entry —
  written once, shown twice. `.cref` is styled identically and is the hook for the *sourced* tier
  when verification is possible; the JS already handles both selectors, so that tier is markup
  plus endnote entries, no new code.
  - **Markers are real anchors.** With JS off they jump to the entry. With JS on, click is
    intercepted and the card carries its own "Full entry ↓" link.
  - **Three input-path traps, all hit and fixed — do not "simplify" these back.** (1) A tap
    synthesizes `mouseenter`, so hover must be gated on `pointerenter` + `e.pointerType`, not on
    a touch latch. (2) `focus` fires *before* `click` on tap, so a naive click-toggle opened the
    card on focus and immediately closed it on click; the fix is tracking `openedBy` and only
    closing on a click that follows a click. (3) `blur` must not close a click-opened card.
  - Verified in Chromium at 1280px and at 390px with touch: hover opens/closes, tap opens,
    second tap closes, outside tap closes, focus opens, Escape closes, `aria-describedby` set,
    card stays inside the viewport, no horizontal scroll, all 8 markers resolve to an entry,
    annotation toggles still work both ways. Test scripts were scratch, not kept.
  - **A tap inside the card does not close it** — that is deliberate, so "Full entry" is
    reachable. A test that taps a coordinate the card covers will look like a failure.
- **No unearned confidence** (Sadh, 2026-07-31: *"Claude often puts in a lot of very confident
  statements like BCG. Your job is it cut all such bullshits."*). The existing repo test decides it:
  a claim survives if it carries **a number, a named frame, or a master's example** — otherwise it
  gets cut or stated as a position rather than a fact. Sixteen were fixed in that pass: invented
  quantities ("worth ten times the frames on either side"), unsupported universals ("the only exit",
  "what any trained eye finds", "Webb's edges … never mid-face", "the number everyone repeats"),
  mind-reading about viewers ("viewers feel it even when they can't name it"), causal certainty
  about how a master worked ("which is how she got this close" → "likely why"), superlatives on
  sources ("*the* honest teaching document" → "an"), and the unsourced demographic assertion in
  §12. The §12 footfall thresholds now say they were chosen by feel, not measured.
  **Absolutes that describe what is visibly in a frame are fine** — "not one of them looking up",
  "the only pure white in it" — a reader can check those by looking. Do not sand those out.
- **The `#howtoread` intro block is DELETED** (Sadh, 2026-07-30: "this whole section is bullshit").
  It had already been rewritten once as "Reading old photographs" and that was not enough — the
  problem was the block existing at all, not its wording. The lede is now two sentences and the page
  goes straight into the TOC. **Do not write a new one.** Also deleted with it: the sentence
  describing the guide's own sourcing ("The photographs run from the 1850s to this year, half out of
  public archives and half from…"), flagged as meta in the same pass, and the `.standfirst` line
  about the optics being computed. `.standfirst` CSS removed as dead; `.caveat` kept (still used).
- **Two annotation mechanisms, both default-on.** 15 figures use inline SVG overlays; the 3 local
  public-domain frames are **baked** — annotations painted into `img/street-*-anno.jpg` with PIL, and
  the button swaps `src` between the baked file and the untouched original via `data-annotated` /
  `data-original` on the `<img>`, marked `class="anno anno-baked"` with **no `.anno-layer`**. The
  lightbox handles both: it clones a layer when one exists, otherwise it swaps `lbImg.src` and tracks
  `lbImg.dataset.state`. **Any code touching `.anno` must not assume `.anno-layer` exists** — that
  null deref is the trap. Baking rebuild: the bake script mirrors the SVG coordinates and the
  `.anno-label` CSS at `scale = 1200/384 = 3.125` (font 31px, stroke 5px), using
  `/mnt/skills/examples/canvas-design/canvas-fonts/JetBrainsMono-Bold.ttf` — the page's actual font,
  so baked and SVG labels match. If a baked frame's geometry changes, re-bake *and* update nothing
  else; there is no SVG left on those three to keep in sync.
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
