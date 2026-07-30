# street-guide.html rework plan (2026-07-29, post-Gemini enrichment)

Direction confirmed by Sadh: the guide teaches with EXTERNAL photographs, not his frames
("shift away from teaching me with my photos" — intentional). Keep Gemini's direction:
archive imagery, 10 lessons, annotation studies. Fix execution. Claude is the author,
Sadh is the reader (standing ruling). Add contemporary photographers via hotlinks where
legal, soft links (outbound text links) where copyrighted.

## What Gemini got right (KEEP)
- LoC FSA/OWI corpus (Delano/Vachon/Wolcott et al., incl. 1940s Kodachromes) — public
  domain, hotlinkable, genuinely canonical street-adjacent material.
- Met open-access set (`met_20_dataset.json` → images/img_0XX.jpg, e.g. Charles Nègre
  1850s Grasse) — public domain.
- Two new lessons: "Layering & spatial stacking" (Webb) and "Color as structure vs
  monochrome" (Leiter/Kodachrome) — good additions; research digests already cover both.
- The original-vs-annotated pair concept ("annotation study") — pedagogically sound.

## What broke (FIX)

### A. Format/UX (do first)
1. Triple hero: page now stacks THREE h1 intros — mine, a pasted copy of
   in-practice.html's intro ("In practice." + its lede/standfirst), and a third inside a
   nested `<main class="guide">` inside `<main class="content">`. Collapse to one intro,
   valid HTML.
2. Chassis regressions: sticky topbar + jump menu, lightbox, scroll-reveal, noscript
   fallback, and the working-distance SIMULATOR are all gone (I have every one of these
   in the pre-Gemini version; restore them). Old `.progress` div returned — remove.
3. Inline styles everywhere (style="..." on ~every element, gold #FFD700 links, ⚙️ emoji,
   colored borders). Move everything into the house design system classes
   (.fig-row/figure/figcaption b/.ex, .takeaway, .planlist). No emoji, no gold.
4. `object-fit:cover; aspect-ratio:4/3` CROPS every photograph — never crop teaching
   frames; show full aspect. One image fakes B&W with `filter:grayscale(100%)` — delete.
5. figcaption used outside <figure> in annotation blocks — invalid.
6. Image count: KEEP ~100 and GROW (Sadh 2026-07-29: "100 images is good, more
   examples -> more learning"; he will ask to increase). No down-curation. The rule
   is per-image, not total: every frame still earns ONE distinct caption point.
   Prevent the wall with layout, not deletion: per-lesson galleries (grid of
   lightbox thumbs) after each lesson's 2–3 featured full-width figures.

### B. Caption/source truth (Sadh: "honest labels, real data")
7. ALL gear EXIF is fabricated ("⚙️ Leica Q2, 28mm f/1.7" on an 1852 Nègre salt print;
   "Ricoh GR III" / "Sony A7III" on 1940s FSA frames). Delete every invented camera line.
   CHANGELOG.md admits this: "EXIF Data Simulation: Injected realistic camera... metadata".
8. Era labels are wrong: "[Color · Contemporary]" on 1940s FSA/OWI images; "LOC:
   Contemporary Archive" is not a thing. Real attribution per frame: photographer, title,
   place, year, collection — fetched from the loc.gov / metmuseum.org item pages already
   linked in each figure's href (verify with a fetch pass; do NOT trust remembered names).
9. Caption prose is rotating boilerplate (~8 sentences recycled across 100 figures:
   "Notice how the harsh directional light...", "sacrifices shadow detail..."). Rewrite:
   one specific, checkable observation per frame, tied to its lesson (where the
   photographer stood, what peaked, what was excluded, what the thumbnail shows).
   "Study in Visual Structure" heading x100 — delete; use per-frame craft labels.

### C. Teaching text (all deleted by Gemini)
10. Lesson prose is GONE — no optics, no worked numbers, no masters material, no drills
    text, no ethics. Restore from the pre-Gemini version (full text exists in session
    history / can be re-derived): distance geometry + table (2.9m/23% vs 25m/71%),
    zone-focus numbers, HCB Gare Saint-Lazare mechanics, reaction-time ≈230ms (Woods
    2015), Fan Ho (cowboy-one-bullet, Approaching Shadow posed + darkroom shadow),
    Leiter (85/90/150mm, Kodachrome-from-1948, Early Color 2006 at 82), Magnum contact
    sheets (Burri 8 rolls, Kalvar last frame, Frank 767→83, Franck 4 frames, Winogrand
    ~2,500 undeveloped), Hurn, Webb 99.9%, Stuart fishing, drills x6, ethics
    (Nussenzweig, CA §1708.8, Turpin norm). Voice: Claude author → reader "you".
11. Since Sadh's frames are out: rewrite intro/lede (no more "case study" framing), and
    write §Layering + §Chroma fresh from the Webb/Leiter research digests. The two
    Gemini lesson titles keep their slots (#layering, #chroma).

### D. Annotations done right
12. Current Gemini annotations = neon-green glowing "TENSION VECTOR" arrows snaking over
    a re-rendered, aspect-squashed copy of the photo (1:1 from 3:4), invented jargon,
    no concrete claim. Also SVG-overlay variants with generic "HORIZON LINE ALIGNMENT".
13. Primary approach — NO image regeneration: absolutely-positioned inline SVG overlays
    on the UNTOUCHED original (house palette: thin #b8422a / #2e6e62 strokes, small
    JetBrains Mono labels, ≤3 marks per frame, tap/hover to toggle overlay like
    in-practice's SOOC hover). Each overlay states ONE checkable claim in lesson
    vocabulary (stage / mark / peak / exclusion edge / background slice / working
    distance), never invented jargon.
14. Gemini (nano banana) image gen ONLY for true diagrams with no underlying photo
    (per image-sourcing policy): top-down working-distance scenes, contact-sheet strip
    illustration, zone-focus band diagram. Prompt pack in the reply / below.
15. One annotation study per lesson (10 total), each: original (full frame, credited) +
    overlay toggle + a 3–5 sentence breakdown that makes a falsifiable claim.
15b. Annotation taxonomy — calibrated against Sadh's ratings of Gemini's PNGs
    (2026-07-29). LIKED: annotation_motion_vectors_*.png (eye-path arrows tracing
    reading order through the Nègre frame) and annotation_depth_layering_*.png
    (fg/mid/bg zone bands). USELESS: annotation_person_v3.png (a glowing rectangle
    around the subjects — outlines the obvious, claims nothing). Conclusion: the
    annotation TYPE carries the value; restyle the liked types in house SVG.
    Overlay types to build (one per study, matched to lesson):
    - eye-path: numbered polyline 1→2→3 tracing reading order (replaces "tension
      vector" jargon)
    - depth bands: 2–3 translucent tinted zones w/ labels (fg / mid / bg) — layering
    - exclusion edge: mark what the frame edge cuts and why (distance/subject)
    - background slice: bracket showing how little bg the focal length admits
    - peak markers: dot on the gesture + ghost dots where it wasn't yet / was gone
    - figure-ground: thumbnail-size inset reduced to 2-tone shape (objects/chroma)
    - light direction: single arrow + shadow-edge trace (light lessons)
    NEVER: boxes/halos around subjects, jargon labels without a claim.

### E. Contemporary photographers (NEW, Sadh's ask)
16. Research pass (web agents) to build per-lesson "study this" material.
    LICENSING TIERS (settled with Sadh 2026-07-29):
    POLICY (Sadh, final, 2026-07-29): "if a server is allowing hotlinks, let's use
    it. if not, then we resort to softlinking."
    a. Hotlink FIRST, for any image whose host serves it to a cross-origin page —
       PD/open-license hosts (LoC, Met, Wikimedia/Flickr Commons, CC-BY Flickr) and
       copyrighted contemporary work alike, when the server technically permits.
       Legal footing noted once and settled: sadh.app operates from CA → 9th Cir.
       Perfect 10 v. Amazon server test (inline linking ≠ copying) is controlling
       here even though SDNY cases disagree; a host that leaves hotlinking open
       strengthens that further. Sadh's call, made informed.
    b. Every hotlinked figure ALWAYS carries: photographer, title/frame name, year,
       source link to the host page, and license/collection line. onerror JS swaps
       a dead/blocked image for its soft-link card automatically, so hotlink rot
       degrades to tier (c) instead of a broken image.
    c. Softlink fallback for hosts that block (referer checks) or rotate URLs:
       named frame/series + where to view it + one line on why it teaches the
       lesson. Verify hotlinkability per-candidate with a cross-origin fetch test
       (curl -e "https://sadh.app/" -I) during the research pass, not by guessing.
    d. NEVER local-mirror non-PD/non-CC images into the repo (reproduction +
       distribution — strictly worse than hotlinking, no server-test cover).
       Local mirroring stays fine for PD (LoC/Met) where page-weight argues for it.
    - Candidates to verify per lesson: Webb (layering), Gilden/Stuart/Turpin (distance,
      fishing), Meyerowitz (gesture/peak), Fan Ho estate + Leiter Foundation (objects/
      chroma), Moriyama, Trent Parke, Melissa O'Shaughnessy, Shin Noguchi, Jonathan
      Higbee, Dimpy Bhalotia — verify each link + frame name before citing.
    - Plus study materials: books (Bystander, On Being a Photographer, Magnum Contact
      Sheets, The Suffering of Light, Early Color), masterclasses (Meyerowitz MoP),
      documentaries (In No Great Hurry, Everybody Street, Finding Vivian Maier).
    - Render as an om1-style tiered reading list section + per-lesson .xref-style
      "study" lines.
17. Logistics: mirror the ~50 kept LoC/Met images locally (img/archive/ + manifest
    mapping file→item page for credits) — PD so legal; hotlinks to tile.loc.gov are
    slow/fragile. Flag to Sadh: this deviates from hotlink-first policy, justified by
    PD status + page weight. Keep source links in every caption regardless.

## Order of work
1. A (chassis restore + valid HTML + house styles) — on the pre-Gemini skeleton, porting
   Gemini's keeper content in.
2. B truth pass (fetch LoC/Met item pages for real credits; batch by item ID).
3. C text restore + two new lessons.
4. D annotations (SVG overlays; Gemini prompts only for diagrams).
5. E contemporary research + reading list.
6. Verify (console, overflow, mobile, lightbox, sim), update index card copy
   ("taught through my real frames" → external-archive framing), CHANGELOG entry.

## Gemini prompt pack (for Sadh to run; nano banana)
Rules that go in EVERY prompt: flat matte vector illustration, warm paper background
#f2f1ea, ink #1a1610, single accent #2e6e62 (secondary #b8422a), thin 2px strokes,
small uppercase monospace labels, NO glow, NO gradients, NO neon, NO photorealism,
16:10, generous margins.

1. Top-down working distance: "Flat vector instructional diagram, top-down view of a
   street. A photographer figure at left. Two scenarios in one frame: camera at 2.9 m
   from a subject with a wide 54° view cone (label '35mm-e · 2.9 m · background slice
   13 m'), and a second camera position far left at 25 m with a narrow 6.9° cone (label
   '300mm-e · 25 m · background slice 4.2 m'). Same subject figure. Background row of
   small building fronts. Style: [rules]."
2. Contact-sheet strip: "Flat vector illustration of a 35mm contact sheet strip, 8
   frames of the same street corner, tiny figure changing position frame to frame,
   frame 7 circled in red grease-pencil style, label 'THE KEEPER IS ALMOST NEVER FRAME
   ONE'. Style: [rules]."
3. Zone-focus band: "Flat vector diagram, side view of a sidewalk 12 m deep. Camera at
   left. A shaded acceptable-focus band from 1.7 m to infinity, hyperfocal mark at
   3.3 m labeled 'f/8 · focus here'. Two pedestrian figures inside the band, one
   outside at 1 m labeled 'too close — move, don't refocus'. Style: [rules]."
4. (If photo annotation via Gemini is ever attempted — not recommended, SVG overlays
   preferred): "Reproduce this photograph EXACTLY — same pixels, same aspect ratio, no
   recoloring, no crop. Add ONLY: two thin matte dark-red (#b8422a) hand-drawn-style
   arrows [describe exactly what each points at], and up to 2 small uppercase monospace
   labels [exact words]. No glow, no neon, nothing else." Check output for base-image
   drift; discard if the photo re-rendered.

## Open items carried over
- People-frame publish approvals now MOOT for street-guide (Sadh's frames removed) but
  still open for in-practice.html h16/h17. img/street/ (21 files) currently unreferenced
  — keep on disk until Sadh decides; some may return as a small "your own frames" coda
  if he ever wants it.
- gen/*.py one-off scripts + inspect_* files + test.jpg in photoing/ are Gemini pipeline
  litter — propose moving to gen/ or deleting before any commit.
- CHANGELOG.md documents the fabricated-EXIF decision — rewrite entry after rework.
