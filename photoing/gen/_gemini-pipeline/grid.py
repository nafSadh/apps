import sys
from PIL import Image, ImageDraw, ImageFont
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def grid(src, out, step=5, label_every=10, box=None, width=1400):
    im = Image.open(src).convert("RGB")
    if box:
        # box in percent of source
        W,H = im.size
        x0,y0,x1,y1 = box
        im = im.crop((int(W*x0/100), int(H*y0/100), int(W*x1/100), int(H*y1/100)))
    W,H = im.size
    sc = width / W
    im = im.resize((width, round(H*sc)), Image.LANCZOS)
    W,H = im.size
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, 18)
    n = int(100/step)
    for i in range(n+1):
        p = i*step
        x = W*p/100; y = H*p/100
        major = (p % label_every == 0)
        col = (255,255,0,230) if major else (0,255,255,140)
        wd = 2 if major else 1
        d.line([(x,0),(x,H)], fill=col, width=wd)
        d.line([(0,y),(W,y)], fill=col, width=wd)
        if major:
            d.rectangle([x+2,2,x+40,24], fill=(0,0,0,200))
            d.text((x+4,3), f"{p}", fill=(255,255,0), font=f)
            d.rectangle([2,y+2,44,y+24], fill=(0,0,0,200))
            d.text((4,y+3), f"{p}", fill=(255,255,0), font=f)
    im.save(out, quality=92)
    print(out, im.size, "| source box:", box)

if __name__ == "__main__":
    a = sys.argv[1:]
    src, out = a[0], a[1]
    step = float(a[2]) if len(a)>2 else 5
    le = float(a[3]) if len(a)>3 else 10
    box = [float(x) for x in a[4].split(",")] if len(a)>4 else None
    w = int(a[5]) if len(a)>5 else 1400
    grid(src,out,step,le,box,w)
