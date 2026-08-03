# Changelog — photoing (sadh.app/photoing)

Notable changes to the photoing guides. Written so that a later reader — human or agent —
can tell what is on the page, where it came from, and what has been retracted.

---

## [5.4.1] - 2026-07-31

Same-day audit of the 5.4.0 pass. Structural checks were clean — HTML parses with no mismatched
tags, no duplicate ids, no dead anchors or toggles, and all three shipped studies reproduce
byte-for-byte (baked) or character-for-character (SVG) from the specs in `gen/anno-src/specs/`.
What the sweep caught:

### Fixed
- **The source split had been mis-stated as 66 · 69.** Mirroring the Delano changed its *hosting*,
  not its *source* — it was LoC/archive before and after, so the split never moved from
  **65 archive/museum · 70 living**. Corrected in the state file and in the 5.4.0 entry below.
- **The Delano caption's ratio said fifteen to one; the measurement says fourteen.** The walker is
  4.4% of frame height against the street's 61.5% → 13.98:1. "Fifteen" came from dividing the
  rounded display values (62/4) instead of the raw ones. Now "fourteen to one".
- **The two local Delano files were twice the per-pixel weight of the other baked frames**
  (0.245 B/px against 0.12–0.17) — quality 90 on grainy Kodachrome. Re-encoded at quality 85,
  chroma untouched (4:4:4): 522→395 KB and 532→403 KB. The bake was re-run on the new original so
  the pair stays pixel-identical outside the painted marks; provenance re-verified byte-for-byte
  from the repo copies of `anno.py` + `spec_delano.py`.
- **`gen/anno-src/specs/README.md` gave run instructions that cannot work** — `from anno import *`
  resolves against the script's directory, not the cwd, so a spec run in place always throws
  `ModuleNotFoundError`. Now says to copy the spec beside `anno.py` (or set `PYTHONPATH`).
- **`anno.py` baked plain-class labels at the wrong opacity** — every label got alpha 235 (.92),
  but the page's plain `.anno-label` is rgba(…,.82) → 209. Per-class alpha now matches the CSS.
  No shipped file affected: the Delano bake uses only `al-accent`/`al-street`, which were right.
- **`CLAUDE.md` still said 18 annotation studies** in its files section; it is 21.

### Noted, not changed
- `data-lb` attributes on 19 images are vestigial — nothing reads them; the lightbox indexes
  `figure img` in document order. The new Delano img doesn't carry one and nothing breaks.
- 136 `<figure>` elements vs "135 figures": the `#kit` hyperfocal diagram is inline SVG with no
  `<img>`. The state file now says so.

---

## [5.4.0] - 2026-07-31

### Added
- **Three annotation studies that had been blocked on network access**, cleared from a local session.
  The queue in `CLAUDE.md` was stalled because Claude Code on the web answers `403` to CONNECT for
  `tile.loc.gov`, `maciejdakowicz.com` and `circuitgallery.com`; every one of those returns 200 from
  a local machine, so the block was environmental, not a property of the sources. Total is now
  **21 studies — 17 SVG overlays, 4 baked**.
  - `annoStaircase` — Jack Delano, *One of the steep hillside streets, Charlotte Amalie*, 1939, §01.
    The frame is the counter-example paired with Vachon's participant geometry, and the read makes
    the comparison numeric: the walker is **4%** of the frame's height, the street **62%** of it.
    Baked, per "bake what you host, overlay what you hotlink".
  - `annoCape` — Maciej Dakowicz, *Superman*, from *Cardiff After Dark*, §04. A rect on the man
    ("the variable") against a polyline down the double yellow line ("always there") — the fishing
    lesson stated as fixed set versus changing cast. SVG over the kept hotlink.
  - `annoCarpool` — Alejandro Cartagena, *Carpooler #10*, §04. A rect on the truck bed ("the cast")
    against dashed marks on both lane markings ("every frame"). SVG over the kept hotlink. The two
    §04 studies share one `.fig-row` and deliberately carry the same read twice.

### Changed
- **The Delano staircase is no longer hotlinked.** `img/street-delano-staircase.jpg` (1200×1809) and
  its baked `-anno.jpg` are mirrored from the LoC *master* TIFF — `…/master/pnp/fsac/1a33000/1a33900/
  1a33932u.tif`, 3807×5432 — not from the `…r.jpg` service copy, which is only 449px wide and far too
  small to bake. The Kodachrome's black slide mount and its rounded corners were cropped off first;
  measuring against the holder rather than the photograph would have made every percentage wrong.
  A 2400px master is kept at `gen/street-delano-staircase-master.jpg`. The archive/living source
  split is unchanged at 65 · 70 — mirroring moves hosting, not source.
- **Stroke colours are now chosen for legibility over convention**, and the state file says so.
  Accent red is invisible on Cartagena's red pickup and ink vanished into the shadow under its cab —
  both caught on the mock-up, which is what the mock-up step is for. That study inverts the usual
  accent-means-subject reading and is correct to.

### Tooling
- **One spec now emits both the SVG and the bake**, so the two cannot drift:
  `gen/_gemini-pipeline/anno.py` (`svg()` / `bake()`, encoding the `scale = width / 384` label maths,
  padding, radius, letter-spacing and label backgrounds) plus `grid.py` for the percent grid. The
  three specs shipped here are kept verbatim in `gen/anno-src/specs/`. Where an edge had a colour
  signature — the road paint, the red cape — it was located with a numpy mask over rows rather than
  read off a grid by eye.

### Verified
Figure count 135 and lesson count 13 unchanged; 13 sections ↔ 13 TOC entries ↔ 13 jump-menu items;
no dead in-page anchors; all 21 annotation toggles resolve to a real element; the three new studies
toggle correctly in both directions inline and in the lightbox, through both mechanisms; labels sit
inside their frames at 1280px; no console errors. One **pre-existing** hotlink, Tavepong
Pratoomwong's *Tree Man* on `live.staticflickr.com`, fails as a subresource in this in-app browser
though curl and a direct tab both load it — left alone, flagged in `STREET-GUIDE-STATE.md`.

---

## [5.3.0] - 2026-07-30

### Changed
- **Annotation reads show by default.** All 18 overlays were `opacity:0` until the reader pressed a
  button, so most of the annotation work on the page was invisible to anyone scrolling it. `.anno-on`
  is replaced by `.anno-off`. Buttons now name the alternative rather than the action — "Show
  original" while the read is up, "Show the read" once hidden — and the lightbox button matches.

### Added
- **The three local public-domain frames are now baked** (Sadh: "bake + also show original on button
  click"). Annotations are painted into `img/street-atget-panier-anno.jpg`,
  `street-atget-orgue-anno.jpg` and `street-stieglitz-terminal-anno.jpg`, shown by default, with the
  button swapping `src` back to the untouched original — so baking did not cost the "Show original"
  behaviour. The 15 hotlinked studies keep their SVG overlays; the lightbox now handles both paths.
  Labels are rendered in the page's own JetBrains Mono at 3.125× the display scale, so baked and SVG
  annotations are visually identical. Verified: inline toggle both directions, lightbox toggle both
  directions, SVG figures unaffected, no JS errors.
- **Lesson 11, "Kit and settings"** (`#kit`), on Sadh's request for sections dedicated to the
  X100VI and the OM-1 + 12–40. Drills move to 12, ethics to 13. Retitled from "The two bodies,
  worked" — *"just use less poetic titles. I am a poet who doesn't like poetics."* Subheads are
  functional for the same reason.
  - **Zone focus gets the space it needed**: the hyperfocal expression with `c` named honestly as a
    print-size convention rather than a fact about optics (so "acceptably sharp" is quoted, not
    claimed — pixel-peep a 40 MP file and the zone edges are soft); a hyperfocal table from f/2 to
    f/11; why f/8 rather than any other stop, which is that it is the first aperture whose near
    limit falls under 2 m and therefore inside the conversational distance Lesson 01 asks for; and
    the limit that matters — f/8 is a daylight technique, and at blue hour the zone collapses back
    to a metre and you are on autofocus again.
  - **An inline-SVG diagram** (no raster file, nothing to generate): one focus distance at 2.5 m
    against four apertures, showing 0.97 m of depth at f/2 versus 8.3 m at f/8.
  - **X100VI**: f/8 zone at 3.3 m holding 1.65 m→∞; the leaf shutter's 1/2000 ceiling at f/2 and why
    that is what the 4-stop ND is for; near-silent firing at conversational distance.
  - **A card on making the steamed-window frame** (the Baudet glass photograph), which was the
    specific question. The frame is a choice of which plane gets the slab: at ~30 cm and f/2 the
    sharp zone is 29.4–30.6 cm, about a centimetre, so the condensation renders and the face behind
    is gone; at ~1 m it is 93–108 cm, about fifteen, so the face resolves and the glass drops to
    texture. f/8 renders both and kills the effect. EVF, not OVF, below a metre.
  - **OM-1 + 12–40**: zoom restricted to 14–25 mm; 17 mm at f/8 focused at 2.5 m holds 1.2 m→∞;
    ProCapture keeping 70 frames from before the shutter press — the only thing on the page that
    actually beats the 230 ms reaction latency of Lesson 03.
  - **On a better alternative**: there isn't one worth buying, and the section says so.
  Every specification is taken from this repo's own `x100vi-guide.html` and `om1-guide.html` rather
  than from recall.

---

## [5.2.0] - 2026-07-30

Second pass from Sadh's read-through.

### Removed
- **The `#howtoread` intro block is gone.** Rewriting it in 5.1.0 was the wrong fix — Sadh:
  *"this whole section is bullshit."* The problem was six paragraphs of the page explaining
  which photographs it picked and how to regard them before a single lesson, not the wording.
  The page now runs title → two-sentence lede → Lesson 01.
- The lede sentence describing the guide's own sourcing ("The photographs run from the 1850s to
  this year, half out of public archives and half from…"), flagged as the same species of meta.
- The `.standfirst` line about the optics being computed, and its now-dead CSS rule.
- The FSA's 171,074 negatives survive in lesson 06 and the sources section, so that fact is not
  orphaned, and no inbound links pointed at `#howtoread`.

### Added
- **Three annotation studies, 15 → 18**, built on the local public-domain files rather than the
  hotlinked ones. The CDNs are still unreachable from this environment, but `img/` can be opened
  and measured, which is the workaround the earlier pass missed:
  - `annoPanier` — Atget, *Marchand du Panier*, §01 takeaway. Head-to-sole brackets: seller
    **51%** of frame height, customer **54%**, the onlooker a few paces back **34%**. The fall-off
    across those few paces is the record of where the camera stood.
  - `annoTerminal` — Stieglitz, *The Terminal*, §05 takeaway. Markers on the three stacked
    planes: churned snow near, the driver and his steaming team in the middle, shopfronts behind.
  - `annoOrgue` — Atget, *Joueur d'orgue*, §02. Her thrown-back head and flung arm as one line,
    against the grinder holding still — present versus peaking.
  Every coordinate was read off a rendered percent grid and checked against a PIL mock-up before
  any HTML was written, then verified in-browser.

### Changed
- **Second sweep for self-commentary, this time by reading the prose rather than grepping it.**
  Fourteen more instances across lessons 04–12 and the references, of a kind the earlier
  pattern-match missed because they name no lesson and no guide: process narration ("every link
  below was fetched and confirmed to load", "Availability was checked"), inclusion justification
  ("which is why he is in the syllabus", "The reference case for this whole lesson", "and both
  belong here"), structural self-reference ("This is the paragraph above, executed", "the way the
  field decks isolate one scene per card"), and UI narration ("Turn the read on and the fifth box
  is the point"). All rewritten to state the observation directly. Three references remain, all
  the "Diagram drawn for this guide" credit that distinguishes drawn figures from photographs.

### Note for later
- **Short labels are the real width constraint.** `.anno-label` is `.62rem` and does not scale
  with the image, so a 6–12 character label reads fine at 384px while a 30-character one does
  not. All three new studies sit at normal body width; none needed promoting to `.fig-study`.

---

## [5.1.0] - 2026-07-30

Editing pass on `street-guide.html` from Sadh's read-through. Four notes, all about the page
talking about itself and about figures being too large.

### Changed
- **Cut the page's self-commentary.** The `#howtoread` block read as the author explaining
  their own curation rather than teaching photography; it is now three paragraphs titled
  *Reading old photographs*, keeping the scarcity argument and the "free to use is a legal
  category" ruling and dropping the methodology narration. Thirty self-referential sentences
  across the file ("it belongs in this lesson because…", "chosen because each one solved a
  problem this guide diagnoses", "which is how the shelves on this page were built") are gone
  or rewritten to state the point directly. Five remain and are deliberate: the TOC label and
  the "Diagram drawn for this guide" credit lines.
- **Removed the figure counts from prose.** "135 photographs", "seventy-six photographers" and
  "seventy frames" are out of the lede, the intro block and the index card. The counts were
  accurate but had to be updated in three places whenever a figure moved, and they told the
  reader nothing. Numbers that carry an argument — the FSA's 171,074 negatives, the 40:1
  response spread — stay.
- **Figures default to half-row width (`--half`, 24rem).** The real cause of the oversized
  frames was that `.takeaway` is `max-width:var(--wide)`, so a bare `<figure>` inside a
  "Carry this" box rendered at ~774px — wider than anything else on the page. Solo figures now
  match the paired `.fig-row` scale at 384px, and the lightbox carries full size, per Sadh:
  *"we already have lightbox to see full image, but on the article keep images half row
  width."* Three stacked figures in the §02 takeaway became a two-up row.
- **`.fig-study` added** for the eight annotation studies and drawn diagrams, which keep the
  592px text measure. Their overlay labels are sized in `rem`, not scaled to the image, so they
  stop being legible inline below that width.
- **Local images re-encoded: 2,418 KB → 810 KB** at 1200px, quality 80, progressive. They were
  1400px masters at display sizes of 384px. The three `street-dia-*.png` diagrams were JPEG
  data carrying a `.png` extension; they are now `.jpg` and their references updated.

### Known gaps
- More SVG annotation studies were wanted (Delano `fsac.1a33932`, the Abdolahabadi panorama,
  the Majali Giza frame). Not done: coordinates have to be read off the source pixels, and the
  hosts are unreachable from the environment this pass ran in. Guessing them would repeat two
  errors already in the log.

---

## [5.0.0] - 2026-07-30

`street-guide.html` grows from an archive syllabus into a half-contemporary one, on Sadh's
instruction: *"u need to hotlink images from copyrighted sources, period"* and
*"at least 25 different photographers should be covered."*

### Added
- **135 photographs, 76 photographers, six continents** (from 72 / ~20). Every frame viewed
  at full size before it was captioned.
- **70 frames by living photographers**, hotlinked from their own sites, galleries or
  collectives — in copyright, shown for criticism, each credited to the photographer with a
  link back. This is now half the page. The 65 archive frames are the other half.
- **§09 The living bar** — 40 working photographers with a three-tier study list, on the
  argument that the archive teaches mechanism while the standard is set by people shooting
  into the same flood you are.
- **§10 Reading a city you don't know** — pedestrian-density counting, a sunrise-azimuth table
  by latitude, where street still happens in a car-first metro, the class bias of the genre,
  what to do at a landmark, and a 48-hour plan for a strange city.
- **§12 Ethics** reframed: the British collective position labelled as one position rather
  than the rule, Shahidul Alam's counter-argument on who decides, and an honest section on the
  parts of the canon that are uncomfortable rather than a page that quietly avoids them.
- **Fifteen annotation studies** (from six), inline SVG over untouched originals, toggled per
  figure and cloned into the lightbox at full size. Placement method: render a percent grid over
  the source with PIL, read coordinates off it, draw the marks with PIL to verify, only then emit
  SVG — browser screenshots in this harness are unreliable for checking placement.
- The `#howtoread` intro block: why "copyright-free" is a legal category and not a neutral
  sample — the FSA set is 171,074 negatives made by a small, overwhelmingly white and male
  federal staff to argue a specific political case, at fewer than sixty exposures a day for
  the whole United States.

### Changed
- **Figure layout: 34 full-column figures became 17 two-up rows.** Page height halved
  (103,947px → 51,959px). Full column is now reserved for the eight annotation studies and one
  opening frame per lesson; everything else is a pair at ~380px, with the masonry shelves at
  ~300px giving a third scale.
- Top-five photographer concentration cut from 63% to 36%; Delano reduced from 24 frames to 17
  after three near-duplicate pairs were found.
- Index card and guide lede rewritten to state the real composition. The lede had claimed
  "almost every frame here predates 1943", which stopped being true.

### Fixed
- A cross-reference pointing at Lesson 08 for the contemporary photographers, which are in
  Lesson 09.

---

## [4.0.0] - 2026-07-30

Rebuild of `street-guide.html` after the 1.1.0–3.0.0 pass was retracted (see below).

### Restored
- The page chassis: single hero, valid HTML, sticky topbar with jump menu, lightbox,
  scroll-reveal, `<noscript>` fallback, and the working-distance simulator — all of which
  the retracted pass had deleted. Recovered by replaying the original Write/Edit sequence
  out of the session transcript.
- The teaching text: optics with worked numbers, the masters material, drills and ethics.
- House design system throughout. No inline styles, no forced crops, no CSS grayscale.

### Added
- Two lessons kept from the retracted pass, written fresh from source: **§05 Layers**
  (Alex Webb) and **§07 Colour as structure** (Saul Leiter, FSA Kodachrome). Ten lessons total.
- **72 images.** Every photograph viewed before it was captioned, and credited to its actual
  photographer with a link to the item record: Library of Congress FSA/OWI (Jack Delano,
  John Vachon, Russell Lee, Arthur Rothstein, Carl Mydans, Marion Post Wolcott, Ben Shahn,
  Gordon Parks, Andreas Feininger, Esther Bubley) and The Met open access (Charles Nègre,
  Edgar Degas, W. H. F. Talbot, Charles Marville, Edward Anthony).
- **Per-lesson archive shelves** — lightbox galleries with credit-only captions, so the
  collection can grow without turning the page into a wall of prose.
- **Six annotation studies**: inline SVG overlays on the untouched originals, toggled by a
  button. Eye path, depth planes, size falloff, ghost timing positions, rhythm ticks,
  colour anchor. Each states one claim a reader can check against the picture.
- **Three diagrams** generated for the guide (working distance, contact sheet, layers
  elevation). Prompts and results are recorded in `gen/GEMINI-PROMPTS.md`.
- Hotlink policy: hotlink wherever the host permits it, with an `onerror` handler that
  degrades a blocked or dead image to its credit and source link. No local mirroring of
  anything that is not public domain.

### Fixed
- Two Delano frames (`fsac.1a33939`, `fsac.1a33945`) were swapped, putting a raking-light
  caption on a photograph of a different street. Each now carries its own image and credit.
- The dusk light-ribbon frame is catalogued as a switchman **demonstrating a fusee**, not a
  candid lantern swing. The caption now says so.
- Three Campton, Kentucky frames appeared on two shelves at once; replaced with Vachon's
  *Spectators at fire*, Lee's *Mexican boys looking at movie poster* and Lee's *Magazine stand*.
- Index card copy and cover image updated to match an archive-taught guide.

### Removed
- Roughly 30 frames from the retracted pass that are not street photographs at all —
  hog pens, a city dump, a refrigeration terminal, stockyards, farmsteads, an anti-aircraft
  crew, railyards, bombers — plus modern stock photographs (Moscow, Berlin, Toronto, a
  concert crowd) and 1860s studio portraits of enslaved vendors.
- The neon "TENSION VECTOR" annotation PNGs.
- 35 single-use build scripts and their working files, archived to
  `gen/_gemini-pipeline/` with a README recording what they were.

---

## [1.1.0 – 3.0.0] - 2026-07-29 — RETRACTED

An automated pass expanded `street-guide.html` to 120–200 figures. The imagery it found was
a genuinely good idea — public archives instead of one photographer's frames — and that
direction was kept. Its execution was not, and the entries are removed rather than left to
be cited. What was wrong, from its own logs:

- **Camera metadata was invented by design.** Its 3.0.0 entry reads: *"EXIF Data Simulation:
  Injected realistic camera, lens, ISO, and aperture metadata."* This put "Leica Q2, 28mm
  f/1.7" on an 1852 salted paper print and "Sony A7III" on 1940s negatives.
- **Image-to-source pairings were wrong in bulk**, while the log claimed *"100%
  Image-to-Caption Integrity"* and *"visually verified"* titles. An 1896 Degas was credited
  to Atget; a Chicago street was paired with a photograph of the Toronto skyline.
- **Stock photography was presented as street photography.** Its own entries record
  discovering that one figure was a levitating games controller and another a concert
  crowd — both had already been captioned as street scenes and published.
- **Ratios were forced rather than curated**: *"exactly 25% B&W and 75% Color"* per section,
  *"exactly 40 images per domain"* across five stock and archive sources.
- **Precise-sounding numbers were fabricated**, including per-photographer working distances
  ("Koudelka 25mm at 1.2 m") and keep rates in a "Master Reference Matrix".

Kept from it: the archive direction, the `#layering` and `#chroma` lesson slots, and the
original-versus-annotated study idea. All three were rebuilt from verified sources in 4.0.0.

---

## [1.0.0] - 2026-07-27

### Added
- Initial creation of `street-guide.html` — 8 lessons, 1 interactive simulator (working
  distance visualizer), 6 drills, and house ethics.
- Integrated the `street-guide.html` card into `index.html`.
- Created project instructions in `CLAUDE.md`.
