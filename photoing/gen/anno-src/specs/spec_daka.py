from anno import *
# measured off maciej_dakowicz_..._superman.jpg (1600x1067) with a percent grid;
# cape edges and road paint located by colour mask, not by eye.
MAN = (46.5, 28.5, 14.5, 36.7)          # x, y, w, h — hat crown to sole, cape at full spread
LINE = [(54.5,64),(56.8,70),(59.2,75),(61.5,80),(64,85),(65.5,90),(66.7,95),(66.5,100)]

pts = " ".join(f"{x:g},{y:g}" for x,y in LINE)
svg_txt = ('<svg viewBox="0 0 100 100" preserveAspectRatio="none">'
  f'<polyline points="{pts}" fill="none" stroke="{STREET}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>'
  f'<rect x="{MAN[0]}" y="{MAN[1]}" width="{MAN[2]}" height="{MAN[3]}" fill="none" stroke="{ACCENT}" stroke-width="1.5" vector-effect="non-scaling-stroke"/>'
  '</svg>')
labels = [("always there", "al-street", 46, 92),
          ("the variable", "al-accent", 29, 42)]

# bake path equivalents purely for the local mock-up (never shipped for a hotlink)
mock_paths = [(" ".join(f"{'M' if i==0 else 'L'} {x:g} {y:g}" for i,(x,y) in enumerate(LINE)), STREET),
              (f"M {MAN[0]} {MAN[1]} L {MAN[0]+MAN[2]} {MAN[1]} L {MAN[0]+MAN[2]} {MAN[1]+MAN[3]} "
               f"L {MAN[0]} {MAN[1]+MAN[3]} L {MAN[0]} {MAN[1]}", ACCENT)]

if __name__ == "__main__":
    bake("dakowicz-superman.jpg", "mock-daka.jpg", mock_paths, labels)
    print(svg_txt)
    for t,c,l,tp in labels: print(f'<span class="anno-label {c}" style="left:{l}%;top:{tp}%">{t}</span>')
