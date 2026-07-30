# Gemini prompt pack — street guide

Every prompt below is complete and self-contained. Copy one, paste it, run it. Nothing to collate.

**Section A — diagrams.** No input image; Gemini draws them from scratch. These are the safe, high-yield ones.
**Section B — annotations.** Attach the named file from `photoing/gen/anno-src/hires/` first, then paste the prompt.
Use the **hires** copies (about 3000 px, straight off the Library of Congress master TIFFs) — not the small
JPEGs in the parent folder. That is the difference that stops the model inventing detail.

Reject any annotation output where the photograph itself changed — squashed aspect ratio, repainted faces,
altered grain, different crop. That is the failure mode; regenerate rather than accept it.

---

# A · DIAGRAMS

## A1 · Working distance, top-down

Flat vector instructional diagram, top-down plan view of a street. One subject figure stands at the center right. Two camera positions on the left, both aimed at that same subject: a near camera 2.9 metres away with a wide view cone spreading past the subject, labelled "35MM-E · STAND AT 2.9 M · BACKGROUND SLICE 13.3 M"; a far camera 25 metres away with a very narrow view cone, labelled "300MM-E · STAND AT 25 M · BACKGROUND SLICE 4.2 M". Behind the subject, a row of small building fronts with a bracket measuring how much of that row each cone admits — a wide bracket for the near camera, a tiny bracket for the far one. A dimension line along the bottom marked in metres. Title at top left: "PERSPECTIVE IS SET BY YOUR FEET, NOT THE LENS".

Style: flat matte vector instructional diagram. Warm paper background #f2f1ea. Ink and figures in #1a1610. One accent green #2e6e62, secondary red #b8422a. Thin uniform 2px strokes. All labels in small uppercase monospace, letter-spaced. No glow, no neon, no gradients, no drop shadows, no 3D, no photorealism, no textures, no emoji, no watermark. Generous margins. Aspect ratio 16:10.

## A2 · Contact sheet strip

Flat vector illustration of a 35mm film contact sheet: two horizontal strips of 6 frames each, sprocket holes along the top and bottom edges of each strip, frame numbers in tiny monospace beside each frame. Every frame shows the same simple street corner drawn as minimal shapes — a lamp post, a doorway, a kerb line — with one small walking figure in a different position in each frame. In frame 11 the figure is at the doorway with an arm raised; that frame is circled with a loose red grease-pencil ring and has a small red tick in its corner. Caption below the strips in uppercase monospace: "THE KEEPER IS ALMOST NEVER FRAME ONE".

Style: flat matte vector instructional diagram. Warm paper background #f2f1ea. Ink and figures in #1a1610. One accent green #2e6e62, secondary red #b8422a. Thin uniform 2px strokes. All labels in small uppercase monospace, letter-spaced. No glow, no neon, no gradients, no drop shadows, no 3D, no photorealism, no textures, no emoji, no watermark. Generous margins. Aspect ratio 16:10.

## A3 · Zone focus band

Flat vector diagram, side elevation of a pavement receding 12 metres to the right. A camera icon at the far left at zero metres. A translucent green band lying along the ground from 1.7 metres to the right edge, where it ends in an arrow and the label "INFINITY". A vertical tick at 3.3 metres labelled "F/8 · SET FOCUS HERE · HYPERFOCAL". A second tick at 1.7 metres labelled "NEAR LIMIT". Two standing pedestrian figures inside the band, one at 3 metres and one at 8 metres, both drawn crisply. One more figure at 1 metre, outside and in front of the band, drawn with a dashed outline and labelled in red "TOO CLOSE — MOVE YOUR FEET, DON'T REFOCUS". A metre scale along the bottom.

Style: flat matte vector instructional diagram. Warm paper background #f2f1ea. Ink and figures in #1a1610. One accent green #2e6e62, secondary red #b8422a. Thin uniform 2px strokes. All labels in small uppercase monospace, letter-spaced. No glow, no neon, no gradients, no drop shadows, no 3D, no photorealism, no textures, no emoji, no watermark. Generous margins. Aspect ratio 16:10.

## A4 · Reaction time vs. the peak

Flat vector timeline diagram running left to right across the frame, marked in milliseconds from 0 to 500. A walking figure is drawn three times along the timeline: at 0 ms mid-stride, at 230 ms with the foot landing, at 460 ms already past. A green bracket spanning 0 to 230 ms labelled "YOUR REACTION TIME · 230 MS (WOODS ET AL. 2015)". A red vertical line at about 200 ms labelled "THE PEAK". A red arrow pointing from the peak line back to the left, labelled "PRESS HERE". A small note under the walking figures: "A WALKER COVERS 35 CM IN A QUARTER SECOND". Title top left: "YOU CANNOT REACT TO A PEAK. ONLY ANTICIPATE IT."

Style: flat matte vector instructional diagram. Warm paper background #f2f1ea. Ink and figures in #1a1610. One accent green #2e6e62, secondary red #b8422a. Thin uniform 2px strokes. All labels in small uppercase monospace, letter-spaced. No glow, no neon, no gradients, no drop shadows, no 3D, no photorealism, no textures, no emoji, no watermark. Generous margins. Aspect ratio 16:10.

## A5 · Layers, side elevation

Flat vector diagram, side elevation showing why a wide lens can stack layers and a telephoto cannot. Top half: a camera at the left, three figures at 1 metre, 3 metres and 12 metres, with a wide 63-degree view cone reaching all three; beside it, a small rectangle preview of the resulting frame where the three figures render large, medium and small. Label: "35MM-E FROM 2.9 M · THREE READABLE PLANES". Bottom half: a camera at the left, three figures at 24, 25 and 27 metres, with a narrow 7-degree cone; beside it, a preview rectangle where all three figures render almost the same size, overlapping into one mass. Label: "300MM-E FROM 25 M · THE PLANES FUSE". A short caption between the halves: "COMPRESSION DOESN'T STACK LAYERS. IT DELETES THEM."

Style: flat matte vector instructional diagram. Warm paper background #f2f1ea. Ink and figures in #1a1610. One accent green #2e6e62, secondary red #b8422a. Thin uniform 2px strokes. All labels in small uppercase monospace, letter-spaced. No glow, no neon, no gradients, no drop shadows, no 3D, no photorealism, no textures, no emoji, no watermark. Generous margins. Aspect ratio 16:10.

---

# B · ANNOTATIONS

## B1 · Peak markers — attach `anno-01-peak-pram.jpg`
*(Two women talking beside a pram outside a corner tailor shop.)*

Add exactly three annotation marks to this photograph, and nothing else. 1. A thin dark red circle, not filled, around the raised hand of the woman on the right — just the hand, roughly one tenth of the image width across. 2. A short dark red dashed line dropping straight down from that circle, ending in a small chip label reading: HALF A SECOND EITHER WAY AND THIS IS TWO WOMEN STANDING. 3. A thin deep green horizontal line under the pram at the bottom of the frame, with a chip label above it reading: THE STAGE THAT SAID WAIT HERE. Place both chip labels over the pavement or the shopfront, never over a face.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B2 · Depth bands — attach `anno-02-layers-window.jpg`
*(Old man at a shop window, two women behind him at the glass, the avenue beyond.)*

Add exactly three nested rectangles to this photograph to mark its three depth planes, and nothing else. 1. A dark red rectangle around the near man's head and body — the closest plane. 2. A deep green rectangle around the two women standing at the shop glass behind him. 3. A dark, dashed rectangle around the distant street with the pedestrians and cars. Each rectangle gets a small chip label at its own top-left corner, reading exactly: PLANE 1 · ARM'S LENGTH / PLANE 2 · THE PAIR AT THE GLASS / PLANE 3 · THE STREET. Keep every line thin and let the rectangles overlap where the planes overlap.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B3 · Background slice and size falloff — attach `anno-03-distance-closeman.jpg`
*(Close frame of an older man in a hat; a younger man passes a few paces behind.)*

Add exactly these marks to this photograph, and nothing else. 1. A thin dark red vertical measuring bar beside the near man, running from the top of his hat to his chin, with small end serifs. Chip label beside it: SUBJECT. 2. A thin deep green vertical measuring bar beside the passing man in the background, running from the top of his head to his chin, with the same end serifs — it will be much shorter. Chip label beside it: 3 PACES BACK · HALF THE SIZE. 3. One chip label in an empty area at the bottom reading: THAT FALLOFF ONLY HAPPENS UP CLOSE — A TELEPHOTO WOULD RENDER THEM THE SAME SIZE.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B4 · Eye path and light direction — attach `anno-04-eyepath-overhead.jpg`
*(A colonial main street seen from above: a Coca-Cola sign over a pale arcaded building, a man wheeling
a bicycle, walkers on the left pavement, hillside houses behind. My earlier description of this file was
wrong — it named a different frame, which is why the first B4 run looked mismatched.)*

Add exactly these marks to this photograph, and nothing else. 1. A thin deep green path with three small numbered dots along it, numbered 1, 2 and 3 with no number repeated, tracing the order the eye reads the picture: dot 1 on the group of walkers at the lower left, dot 2 on the man wheeling the bicycle, dot 3 on the Coca-Cola sign above the arcade. The numerals sit inside the dots. 2. One thin dark red straight arrow over the empty roadway on the right, pointing in the direction the sunlight travels — matching the direction the existing shadows fall. Chip label at its tail: LIGHT. 3. One chip label near the walkers reading: THE EYE ENTERS AT THE FIGURES AND CLIMBS TO THE SIGN. Do not draw a shadow, a sun, or any pictorial element — lines and labels only.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B5 · Rhythm and repetition — attach `anno-05-rhythm-loans.jpg`
*(A block of overlapping LOANS / JEWELRY / CLOTHING signs receding down the pavement, one man walking.)*

Add exactly these marks to this photograph, and nothing else. 1. A small deep green tick mark under each projecting shop sign as it recedes down the block — one tick per sign, following the diminishing rhythm. Do not cover the lettering. 2. A thin deep green line connecting all the ticks into one receding curve. 3. A thin dark red circle, not filled, around the walking man. 4. Two chip labels only: one near the ticks reading FIVE BEATS, ONE WORD; one near the circled man reading THE SCALE FIGURE THAT GIVES THE PATTERN A TEMPO.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B6 · Colour anchor — attach `anno-06-color-redsign.jpg`
*(Narrow street: a red Coca-Cola sign against blue sky and a yellow corner wall.)*

Add exactly these marks to this photograph, and nothing else. 1. A thin dark red circle, not filled, around the hanging red sign. 2. Three small chip labels placed over flat empty areas of the image, one per colour zone, reading exactly: THE WORKING COLOUR / BLUE FIELD / OCHRE FIELD — the first beside the circled sign, the second over the sky, the third over the large plain wall. 3. A thin deep green line tracing where the street bends, running from the bottom of the frame up to the circled sign. Do not adjust, boost or shift any colour in the photograph itself.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B7 · Scale figure and exclusion edges — attach `anno-07-scale-staircase.jpg`
*(A long staircase street between houses, one tiny figure at the centre.)*

Add exactly these marks to this photograph, and nothing else. 1. A thin dark red circle, not filled, around the single small figure on the steps, with a short leader line to a chip label reading: ONE FIGURE, 2% OF THE FRAME — REMOVE IT AND THE DEPTH DIES. 2. Two thin deep green corner brackets, one at the left frame edge and one at the right, each about a fifth of the image height, marking where the photographer chose to cut the houses off. One chip label between them reading: THE EXCLUSION EDGES. 3. A thin deep green line running down the centre of the staircase from top to bottom.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

## B8 · Timing, ghost positions — attach `anno-08-timing-seam.jpg`
*(A man in a long coat striding past two small wooden storefronts.)*

Add exactly these marks to this photograph, and nothing else. 1. A thin dark red outline of the walking man exactly where he is — trace his silhouette, do not fill it. 2. Two thin dashed grey ghost outlines of the same silhouette: one about one stride to the left of him, one about one stride to the right. Same size, same pose, dashed and faint. 3. Chip labels: TOO EARLY · HE OVERLAPS THE WINDOW on the left ghost, TOO LATE · HE'S LEAVING on the right ghost, and PRESSED AT THE SEAM on the solid red outline. Place the labels above the figures on the building wall, never across the man's body.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

---

# Template for a new annotation

Fill the brackets, keep the second paragraph verbatim.

Add exactly [N] annotation marks to this photograph, and nothing else. 1. [shape] in [dark red / deep green] around [precisely which thing in the picture]. 2. [shape] ... 3. One chip label reading: [THE ONE CHECKABLE CLAIM, IN CAPITALS]. Place labels over empty areas, never over a face.

Return the input photograph completely unchanged — identical pixels, identical tone and color, identical crop, identical aspect ratio. Do not redraw, restyle, upscale, sharpen, colorize or re-generate any part of the image. Only composite the annotation marks on top. Marks: thin clean vector lines, dark red #b8422a and deep green #2e6e62, stroke weight about 0.3% of image width, consistent everywhere. Labels: small uppercase monospace, white text on a solid dark #1a1610 rounded rectangle chip, placed in empty areas so they never cover a face or the subject. No glow, no neon, no drop shadows, no gradients, no 3D arrows, no emoji, no watermark, no extra marks beyond the ones listed.

**Three rules that keep these useful rather than decorative:**
- Three marks maximum. Four is a diagram of a photograph, not an annotation.
- Every overlay makes one claim a reader can check against the picture. A box drawn around the obvious
  subject claims nothing — that is why the glowing-rectangle version was useless.
- Lesson vocabulary only: stage, mark, peak, plane, exclusion edge, background slice, working distance,
  scale figure, working colour. Never invented jargon like "tension vector".

---

# Round 1 results (2026-07-30)

**Diagrams: A1, A2, A5 accepted** and are on the page. A3 and A4 need one regen each — both
came back with a duplicated label. Corrective prompts below; everything else in those prompts
stays the same.

**Annotations B1–B8: all rejected, and the prompts cannot fix it.** The mark design was good
— that part is now reproduced as SVG on the page. But every one of the eight regenerated the
photograph instead of compositing onto it: all were outpainted from landscape or portrait to
a 1:1 square, signage text came back as gibberish (`PROHIMUNES`, `ESPCCULIAOS` where the real
Spanish was), faces changed, and in B8 the walking man was erased and replaced by his own
outline. Publishing those under "Russell Lee, Library of Congress" would be a fabricated
archival photograph, so they can't go on the page.

**Do not re-run B1–B8.** Two rounds of prompt-hardening have now failed the same way; the
model does not have a composite-only path. Annotations stay as inline SVG over the untouched
originals — six are live on the page and the process is cheap to extend.

## A3 regen — zone focus band

Same prompt as A3 above, with this appended:

Label the near limit exactly once, at 1.7 metres on the focus band. Do not repeat the words NEAR LIMIT anywhere else in the diagram, and do not label the 2 metre tick on the ruler.

## A4 regen — reaction time

Same prompt as A4 above, with this appended:

Draw the reaction-time bracket exactly once, above the timeline only. Do not repeat the bracket or the words YOUR REACTION TIME below the timeline.
