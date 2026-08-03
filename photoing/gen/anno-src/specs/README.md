# Annotation specs — street-guide.html

The three studies shipped 2026-07-31, kept verbatim so a later study can start from a working
example rather than from scratch. Each is the single source for both outputs: `svg()` emits the
inline overlay pasted into the page, `bake()` paints the same geometry into a `-anno.jpg`.

**Copy the spec into a scratch directory beside `anno.py` and `grid.py`** (both in
`gen/_gemini-pipeline/`) before running it — `from anno import *` resolves against the *script's*
directory, so running a spec in place here fails with `ModuleNotFoundError` even when your cwd
holds `anno.py`. (`PYTHONPATH=. python path/to/spec.py` also works.) The scratch directory also
needs a venv with Pillow + numpy, `JetBrainsMono-Bold.ttf`, and the source image under the
filename each spec names:

| spec | source image | treatment |
|---|---|---|
| `spec_delano.py` | LoC master `…/master/pnp/fsac/1a33000/1a33900/1a33932u.tif`, cropped to (231, 190, 3537, 5175) to clear the slide mount, resized to 1200px → `delano-crop-test.jpg` | **baked** into `img/street-delano-staircase-anno.jpg` |
| `spec_daka.py` | `maciejdakowicz.com/…_superman.jpg` (1600×1067) → `dakowicz-superman.jpg` | SVG overlay, hotlink kept |
| `spec_cart.py` | `circuitgallery.com/…/Cartagena_CP10.jpg` (492×800) → `cartagena-cp10.jpg` | SVG overlay, hotlink kept |

`bake()` on the two hotlinked frames produces a **local mock-up only** — never ship a painted copy
of an in-copyright photograph. Looking at that mock-up before writing any HTML is step 2 of the
method and is not optional; it is what caught the invisible strokes in `spec_cart.py`.
