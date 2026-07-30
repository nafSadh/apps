# Changelog — photoing (sadh.app/photoing)

Notable changes to the photoing guides. Written so that a later reader — human or agent —
can tell what is on the page, where it came from, and what has been retracted.

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
