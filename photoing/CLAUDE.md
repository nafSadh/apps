# photoing — visual field guides (sadh.app/photoing)

Hand-crafted static HTML field guides to the cameras nafSadh actually shoots: interactive
simulators, cutaway diagrams, pocket field decks, and craft notes that admit what doesn't work.
No build system, no framework — every page is a single self-contained HTML file with inline
CSS/JS. Do not introduce tooling.

## Files
- `index.html` — hub. Card grid of guides + a full-width "companion" card. ~116 lines.
- `x100vi-guide.html` — Fuji X100VI guide (13 sections, 3 simulators, 12-card field deck).
- `om1-guide.html` — OM-1 guide (12 sections, 2 simulators, 12-card mission deck).
- `in-practice.html` — camera-agnostic companion: 7 lessons, worked numbers, 6 assignments,
  real photographs as evidence.
- `street-guide.html` — street photography guide, 13 lessons, 135 figures, 18 annotation studies.
  **Built and live.** `STREET-GUIDE-STATE.md` is its resume file — read that before touching it.
- `img/` — web-ready images, short kebab names (`scene-01-street-day.jpg`, `om-mission-04.jpg`).
- `gen/` — generated illustration masters (jpeg, higher res; `-BROKEN` suffix = discarded take).
  Pipeline: masters land in `gen/`, the chosen/renamed web copies go to `img/`.

## Design system (shared by every page — copy from an existing guide, don't invent)
- Tokens: `--paper:#f3f2ec --paper-hi:#faf9f4 --ink:#1b1710 --ink-soft:#3a3126 --dim:#877c62
  --line:rgba(26,20,10,.13)`; per-guide accents `--fuji:#b8422a`, `--om:#1f6a99`.
  A new guide adds its OWN accent variable in the same key (muted, ink-compatible).
- Fonts (Google): Fraunces (italic, opsz 144) for display/h1/h2 · DM Sans for body ·
  JetBrains Mono for kickers, tags, captions, numbers.
- Body texture: fractal-noise SVG overlay at .05 opacity + two soft radial color washes
  (see any page's `body::before/::after`). Keep it.
- Cards: `.guide` blocks on index — image (1:1), mono kicker (`.cam`), Fraunces italic h2,
  one-paragraph pitch, mono `.tag` chips, "Open the guide →".
- Interactive simulators are vanilla JS, self-contained, keyboard-accessible; respect
  `prefers-reduced-motion`.
- Voice: first person, honest, plain words, "read once and carried after." Worked numbers over
  adjectives. Photographs as evidence, not decoration. No hype, no euphemism.

## street-guide.html — blocked work, pick up from a local session

The guide is **built**; everything below this heading down to "Content pillars" is the original
brief, kept for the diagnosis it contains. `STREET-GUIDE-STATE.md` is the live resume file and
wins wherever the two disagree. What follows here is only the part that **cannot be done from
Claude Code on the web**.

**Why it is blocked.** The web sandbox's network policy answers `403` to CONNECT for
`tile.loc.gov`, `www.maciejdakowicz.com`, `circuitgallery.com` and `images.squarespace-cdn.com`.
This is *not* a missing-browser problem — Chromium and Playwright are installed there and were
used throughout the build; a browser goes through the same proxy and renders those figures as
"frame unavailable". A local session fixes it through unrestricted egress, nothing else.

**The rule that decides the treatment: bake what you host, overlay what you hotlink.**
- **Public domain, mirrored into `img/`** → paint the annotations into a `-anno.jpg` with PIL and
  swap `src` on the button (`data-annotated` / `data-original`, wrapper `class="anno anno-baked"`,
  no `.anno-layer`). Also works with JS off. Three frames do this today.
- **In copyright, hotlinked** → inline SVG overlay only, and keep the hotlink. You cannot bake a
  file you do not host, and painting on an in-copyright photograph makes a derivative work — a
  different legal question from showing it for criticism. Fifteen frames do this today.

**Queued, in priority order:**
1. **Delano `fsac/1a33932`** — `https://tile.loc.gov/storage-services/service/pnp/fsac/1a33000/1a33900/1a33932r.jpg`
   Public domain. Mirror it to `img/`, then bake. This also retires a hotlink that dies whenever
   LoC does. It sits in §01 as the spectator-geometry counter-example.
2. **Dakowicz, *Superman*** (`maciejdakowicz.com`, Cardiff After Dark, §04) and **Cartagena,
   *Carpoolers*** (`circuitgallery.com`, §04) — Sadh asked for both to be studied. In copyright:
   measure locally, ship an SVG overlay, keep the hotlink.
3. Abdolahabadi panorama and Majali Giza — gridded once already, same overlay treatment.

**Method — do not skip step 2.** Coordinates are measured, never estimated. Two of the three
existing baked studies had positions wrong on the first attempt and were caught by the mock-up.
1. Open with PIL, render a percent grid (5% lines, labelled every 10%), read coordinates off it.
   Crop and re-grid at 1–2% for any edge that carries a number.
2. Draw the planned annotation onto a copy with PIL and **look at it** before writing any HTML.
3. Emit inline SVG with `viewBox="0 0 100 100" preserveAspectRatio="none"` so SVG units are
   percentages directly. `<circle>` renders as an ellipse under that setting — expected, and
   consistent with the existing studies.
4. Baked frames only: mirror the SVG coordinates and the `.anno-label` CSS at
   `scale = image_width / 384` (3.125 for the 1200px files → 31px label, 5px stroke) using
   `JetBrainsMono-Bold.ttf`, the page's own label font.

**Labels must be 6–12 characters.** `.anno-label` is `.62rem` and does not scale with the image,
so "seller 51%" reads at 384px and a 30-character label does not.

**Verify in a browser before committing:** figure count; `section.lesson` count matching both the
TOC `<li>` count and the jump menu; no dead in-page anchors; annotation toggles in both
directions; the lightbox for *both* mechanisms; no JS errors. Any code touching `.anno` must not
assume `.anno-layer` exists — the baked three do not have one, and that is the null-deref trap.

## The original brief (kept for the diagnosis; the guide is built)

This one is different from the camera guides: it teaches **seeing**, not a body. It exists
because the owner's street and object work is measurably their weakest genre, and the
diagnosis is already written. **Source of truth: `/Users/nafsadh/photos/.memory/bias/craft-development.md`**
(read it before writing a word). Key facts from it:

- Owner shoots street from landscape distance (40-150mm = 80-300mm-e) — people end up as
  props on a pre-composed stage. No gesture, no peak moment; frames are timing-agnostic.
- Object frames are *descriptions* (carved lettering, a painted conduit) not *transformations*
  (their art-deco fire escape became pure rhythm and outscored everything else 40:1).
- Scenes are worked 2–5 frames; street winners come from 20–40 frames at one spot.
- Correct kit, already owned: **X100VI (fixed 35mm-e) is the street camera**; alternative is
  the OM-1 + 12-40 restricted to 14–25mm (= 28–50mm-e). The 40-150 is banned for street.

### The student — pitch the guide AT this person, not at a beginner
The owner is an experienced enthusiast, not a novice. They wrote the two camera guides in this
repo; they understand exposure, metering, DoF arithmetic, and their gear deeply. Their
post-processing and cropping are strong — in review sessions their crops beat both agent and
judge proposals. Their landscape/graphic work already performs: art-deco fire escape 3300 on
r/itookapicture, moon sliver 1300, a Golden Gate post at 2000 on r/sanfrancisco. **Do not
teach basics. Start past all of it.**

> **Superseded 2026-07-30.** This brief used to end that line with "do not talk about gear beyond
> the focal-length argument". Sadh overrode it — *"we probably need to add sections dedicated for
> x100vi and om-1 with 12-40mm lens"* — and **Lesson 11, "The two bodies, worked" (`#kit`), is the
> result. Do not delete it as off-brief.** The constraint that replaced the old rule: every
> specification on that page must be read out of this repo's own `x100vi-guide.html` /
> `om1-guide.html`, never recalled. Gear talk earns its place by being arithmetic the reader can
> act on (zone distances, the f/2 shutter ceiling, ProCapture's pre-press buffer), not by being
> spec listing.

Where they actually are in street/object, with receipts (their posted record, upvotes):
- Street is their measurably worst genre: r/streetphotography engagement 1.10%, the lowest of
  every genre they post. The frames: mural + man on a Target run (19), motion-blur crossing
  "chasing and holding" (17), "Aunt Sam, resting" (51), "The One-Man Parade" (54).
- Objects land in the 40–80 mush: carved lettering 44, ferris gondolas through a maple 43,
  boat-wake spiral 39, duck on a fountain rim 75. Their painted-conduit frame was removed by
  r/minimalistphotography mods for a busy background the owner read as a clean single subject.
- Observed habits behind those numbers: shoots street on a 40-150 (80–300mm-e) from across the
  street; pre-composes a stage and waits for a figure to enter it; works a scene 2–5 frames
  then moves on; frequently shoots at midday. Their strength (building frames) is precisely
  the habit street punishes.
- They know all of this — the diagnosis has been discussed and accepted. The guide's job is
  not to break the news; it is to be the *training manual* for the fix.

How to talk to them: evidence and worked numbers, bluntly, in plain words. They explicitly
reject euphemism, hype, and anything that "reads like written by a 17yo intern at BuzzFeed."
They will not act on advice they find unconvincing — every claim in the guide should survive
the question "why?" with either a number, a named frame, or a master's example.

Learning goals, ranked (this is the guide's spine):
1. Proximity + subject-first reflex — the person IS the photo.
2. Peak/gesture timing — pressing on meaning, not on presence.
3. Working one scene 20–40 frames — fishing, not hunting.
4. Object transformation — light/angle/abstraction over description.
5. Light discipline as a cross-cutting habit (they shoot on arrival, not at the right hour).

### Example frames — real files, view them before writing (all under `/Users/nafsadh/photos/`)
The guide should be illustrated with the owner's own frames wherever possible (confirm picks
with them before publishing). Scores are Reddit upvotes on the owner's account.

**Street that didn't work — the core teaching material:**
- `26.07.04 SF/selects/exports/P7047475.jpg` — mural + man carrying a red box (19). The
  textbook stage-first frame: wall first, human as timing garnish, shot from across the street.
- `26.07.04 SF/selects/exports/P7047954.jpg` — motion-blurred walker, blue hour (17). Blur
  standing in for a moment that never peaks.
- `26.07.04 SF/2ndTake/P7047550-2-2.jpg` — "Aunt Sam, resting" (51). Found character, but
  observed from spectator distance; no exchange.
- `26.07.04 SF/selects/exports/P7047631.jpg` — "The One-Man Parade" (54). Best of the set and
  still a scene-with-a-person, not a person-photo.
- `25.12.13 Walk/selects/jpeg/DSCF1293.JPG` — backlit sidewalk into flare (never posted).
  Gorgeous light, anonymous silhouettes: light-first, subject-absent.

**Objects described, not transformed:**
- `26.01 Austin/edits/P1023333.jpg` — carved lettering over an arched window (44). Inventory
  entry: the thing, as it is, competently.
- `26.07.04 SF/crops/P7047554.JPG` — ferris gondolas through a maple (43).
- `26.05.09 Shasta/edited/P5098471-4.jpg` — boat-wake spiral (39). A real graphic idea that
  stayed too small in frame.
- `26.06.20 Rose Garden/edits/P6205762.jpg` — duck on a fountain rim (75).
- `25.12.13 Walk/DSCF1382.jpg` — painted-over conduit; removed by r/minimalistphotography
  mods: single subject, but on a busy textured field. The thumbnail-truth lesson.

**The successes to contrast against (same photographer, same cities):**
- `26.06 dtSJ/edits/P6064392.jpg` — art-deco fire escape (3300, the account record). An
  object TRANSFORMED into rhythm; the guide's north star for pillar 5.
- `26.07.15 Rooftop Pizza/edits/P7159131.jpg` — crescent moon sliver (716 minimalist, 584
  ITAP). One shape, empty field: thumbnail truth done right.
- `26.05.23 Yosemite/edits/DSCF3842-3.jpg` — meadow boardwalk to the falls (1500 ITAP, 1600
  NationalPark). Leading line + committed light.
- `26.07.12 SF Clouds and Colors/edits/P7128816.jpg` — GGB behind the fence S-curve (2000
  r/sanfrancisco, 1000 r/pics). Famous subject + committed light + graphic foreground.
- `26.07.12 SF Clouds and Colors/edits/P7128852.2-3.jpg` — four birds on a snag (244). The
  owner's graphic eye applied to living subjects — closest existing bridge to street.

**Instructive pairs (use side-by-side):**
- Subject scale: `26.05 Santa Cruz/edits/P5170624-2.jpg` (otter head up, eye readable — works)
  vs `26.05 Santa Cruz/edits/P5170569-2.jpg` (same animal face-down at 5% of frame — dead).
- Figure as anchor vs clutter: `25.12.19-25 Hawaii - Oahu/edited/PC210541.jpg` (lone seated
  silhouette makes the vista) vs `PC210510.jpg` same folder (recognizable hikers as noise).

**Unrealized frames — proof the eye is already there (good "where this goes next" material):**
- `26.05.23 Yosemite/keeps/jpeg/P5231074.JPG` — backlit raven silhouette on a granite
  overlook; the strongest unposted frame in the library, waiting on an edit.
- `26.01.16 Yosemite/bak/jpeg/P1186164.JPG` — El Capitan golden, red-jacketed photographer as
  scale figure. The Fan Ho instinct, already in the owner's work.
- `26.07.04 SF/crops/P7048193.JPG` — silhouetted figures on a Victorian cornice at dusk;
  "clean, unusual, decisive." The owner's best existing street-adjacent frame.
- `26.07.04 SF/crops/P7048239.JPG` — Victorian gables under aircraft light-trails at night.

### Content pillars (the guide's sections, roughly)
1. **Distance is the medium** — why 28–50mm-e and physical proximity change what the frame
   carries; spectator vs participant.
2. **The peak** — decisive-moment mechanics: gesture, glance, juxtaposition; the test "does
   the frame collapse a half-second either side?"
3. **People are the subject, not the garnish** — scene-first vs subject-first reflexes; "if
   this person were someone else, would the photo change?"
4. **Working the scene** — contact-sheet thinking; fishing not hunting; one block / one hour /
   100 frames.
5. **Objects: transform, don't describe** — light, angle, abstraction; description is an
   inventory entry.
6. **Masters as data** — the 50-frames-with-a-rubric study method (single shape at thumbnail /
   where it peaks / camera distance / what got transformed). Fan Ho (the owner's bridge:
   graphic geometry + lone figure), Saul Leiter (objects/reflections transformed), the Magnum
   Contact Sheets (what surrounds a keeper).
7. **Drills** — gesture-only shutter week · light-first object walks · remake ten frames ·
   the X100VI month. Frame these as assignments like in-practice.html does.
8. **Ethics** — candid photography ethics, stated plainly. The owner's own bar is stricter
   than the legal one: identifiable strangers get privacy (no faces of people in vulnerable
   moments, homeless people are people not props, lit windows are off limits). Use the word
   "homeless," not "unhoused" — plain words throughout.

### Build notes — status
- **One simulator exists** — the focal-length / working-distance visualizer, `#distsim` in §01.
  The peak-latency simulator (`#peaksim`) recorded in CHANGELOG v1.3.0 **was removed** during the
  v5.0.0 overhaul and is not on the page; the changelog entry is history, not current state. The
  brief's ceiling of two still stands, so one more is permitted if it genuinely teaches.
- **Not built:** the 12-card street deck (`img/street-card-NN-*.jpg`, masters into `gen/` first).
  Still open if wanted.
- ~~Add the third card to `index.html`~~ — **done**, with the `--street` accent. Its tag chips
  read `12 lessons · 1 simulator · annotation studies`; the lesson count is now **13**, so fix
  that chip next time `index.html` is touched. Deliberately **no figure/photographer counts** in
  the card prose — see the counts ruling in `STREET-GUIDE-STATE.md`.
- If real example frames are wanted, ask the owner to pick from their library rather than
  inventing; their photos live under `/Users/nafsadh/photos/` and the strongest street
  attempts (and their scores) are catalogued in the craft file above. **None of the owner's own
  photographs are on the page yet** — every figure is archive or a working photographer's work.

## Changelog
See `CHANGELOG.md` for the complete record of updates across all field guides.
- **2026-07-29 (v1.6.0)**: Expanded external hotlink ecosystem across `street-guide.html` to **85 active external hotlinks** (exceeding the requested 42+ threshold). Integrated primary museum holdings (MoMA, The Met, Tate Modern, Library of Congress FSA, NGA, ICP, MCNY) and master photographer foundation archives (Magnum Photos, Fan Ho, Saul Leiter, Vivian Maier, Ernst Haas, Gordon Parks, Matt Stuart, Vineet Vohra, Daniel Arnold, Maciej Dakowicz).
- **2026-07-29 (v1.5.0)**: Added Staged vs. Pure Candid photography analysis (micro-postural tells of unscripted muscle tension vs posed artifice). Expanded guide with modern contemporary masters (Alex Webb, Trent Parke, Matt Stuart, Vineet Vohra, Daniel Arnold). Embedded direct external hotlinked images (`<img src="..." />`) for master works and added curatorial secondary source breakdowns ("Why it worked") referencing MoMA, ICP, Aperture, and BJP essays.
- **2026-07-29 (v1.4.0)**: Embedded direct external hyperlinks to official museum/archive collections (MoMA, Tate, Met Museum, National Gallery of Art, ICP, Magnum Photos, Saul Leiter Foundation) for 22+ master photographs. Added a dedicated References & Empirical Citations section (`#references`) substantiating proxemics, latency neuroscience, optics, contact sheet data, Gestalt theory, and legal precedents.
- **2026-07-29 (v1.3.0)**: Added two brand-new lessons (`#layering`: Layering & Spatial Stacking; `#chroma`: Color as Structure vs Monochrome) and built an interactive SVG/JS Peak Gesture & System Latency Simulator (`#peaksim`) into Lesson 03. Expanded guide to 10 lessons and 2 interactive simulators.
- **2026-07-29 (v1.2.0)**: Comprehensive master-level overhaul of `street-guide.html`. Grounded all lessons in canonical master works (Winogrand, Cartier-Bresson, Saul Leiter, Fan Ho, Gilden, Koudelka, Levitt, Frank, Webb, Arbus, Maier, Eggleston, Moriyama, Haas), proxemics theory, depth-of-field/hyperfocal optics, neuroscience system latency physics ($430\text{ms}$ delay / vector displacement), Magnum contact-sheet analytics, and Gestalt object transformation principles. Added Master Reference Matrix.
- **2026-07-29 (v1.1.0)**: Upgraded `street-guide.html` with proxemics theory, exact zone-focus optics math, reaction-latency physics, and structured transformation levers. Created `CHANGELOG.md`.

