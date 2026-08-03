"""One spec -> inline SVG string + baked JPEG, so the two can never drift.

Mirrors the page CSS at scale = image_width / 384:
  .anno-label  font-size .62rem (9.92px at 16px root), weight 600, letter-spacing .08em,
               uppercase, color #f9f7f1, padding .18rem .45rem, radius 5px,
               transform translate(-50%,-50%)
  svg          viewBox 0 0 100 100, preserveAspectRatio="none", stroke-width 1.5 with
               vector-effect=non-scaling-stroke  -> 1.5 CSS px at any size
"""
from PIL import Image, ImageDraw, ImageFont

# The page's own label font. Not installed on macOS — fetch it once from
# https://github.com/JetBrains/JetBrainsMono/releases (fonts/ttf/JetBrainsMono-Bold.ttf)
# and point FONT at it. Pillow and numpy are not in the system Python either; use a venv.
FONT = "jb/fonts/ttf/JetBrainsMono-Bold.ttf"
ACCENT = "#b8422a"   # --fuji, .al-accent
STREET = "#2e6e62"   # --street, .al-street
INK    = "#1a1610"   # plain .anno-label background
BASE_W = 384.0       # .fig-narrow / .fig-row width the CSS is tuned for
FS_REM = 0.62 * 16   # 9.92px
STROKE = 1.5         # CSS px


def vbar(x, y0, y1, cap=1.6):
    """I-beam: cap, stem, cap. Returns an SVG path 'd'."""
    return (f"M {x-cap:g} {y0:g} L {x+cap:g} {y0:g} "
            f"M {x:g} {y0:g} L {x:g} {y1:g} "
            f"M {x-cap:g} {y1:g} L {x+cap:g} {y1:g}")


def hbar(y, x0, x1, cap=1.6):
    return (f"M {x0:g} {y-cap:g} L {x0:g} {y+cap:g} "
            f"M {x0:g} {y:g} L {x1:g} {y:g} "
            f"M {x1:g} {y-cap:g} L {x1:g} {y+cap:g}")


def svg(paths, labels):
    """paths: [(d, colour)]  labels: [(text, cls, left%, top%)]"""
    out = ['<svg viewBox="0 0 100 100" preserveAspectRatio="none">']
    for d, col in paths:
        out.append(f'<path d="{d}" stroke="{col}" stroke-width="1.5" fill="none" '
                   f'vector-effect="non-scaling-stroke"/>')
    out.append("</svg>")
    s = "".join(out)
    for text, cls, left, top in labels:
        c = f" {cls}" if cls else ""
        s += (f'\n          <span class="anno-label{c}" '
              f'style="left:{left:g}%;top:{top:g}%">{text}</span>')
    return s


# Alpha mirrors the page CSS: .al-accent/.al-street are rgba(…,.92) → 235, the plain
# .anno-label is rgba(…,.82) → 209.
LABEL_BG = {"al-accent": (184, 66, 42, 235), "al-street": (46, 110, 98, 235),
            "": (26, 22, 16, 209)}


def bake(src, dst, paths, labels, quality=90):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    sc = W / BASE_W
    d = ImageDraw.Draw(im, "RGBA")

    sw = max(1, round(STROKE * sc))
    for path, col in paths:
        toks, pen = path.split(), None
        i = 0
        while i < len(toks):
            op = toks[i]
            x, y = float(toks[i + 1]) * W / 100, float(toks[i + 2]) * H / 100
            if op == "M":
                pen = (x, y)
            elif op == "L":
                d.line([pen, (x, y)], fill=col, width=sw)
                pen = (x, y)
            i += 3

    fs = FS_REM * sc
    f = ImageFont.truetype(FONT, round(fs))
    track = round(0.08 * fs)                 # letter-spacing .08em
    pad_x, pad_y = 0.45 * 16 * sc, 0.18 * 16 * sc
    rad = round(5 * sc)
    for text, cls, left, top in labels:
        t = text.upper()
        widths = [f.getlength(ch) for ch in t]
        tw = sum(widths) + track * (len(t) - 1)
        asc, desc = f.getmetrics()
        th = asc + desc
        bw, bh = tw + 2 * pad_x, th + 2 * pad_y
        cx, cy = W * left / 100, H * top / 100
        x0, y0 = cx - bw / 2, cy - bh / 2      # translate(-50%,-50%)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=rad,
                            fill=LABEL_BG[cls])
        px = x0 + pad_x
        for ch, w in zip(t, widths):
            d.text((px, y0 + pad_y), ch, font=f, fill=(249, 247, 241))
            px += w + track
    im.save(dst, quality=quality, subsampling=0)
    print(f"baked {dst} {im.size} scale={sc:.3f} font={round(fs)}px stroke={sw}px")
