from anno import *
# measured off Cartagena_CP10.jpg (492x800) with a percent grid; lane lines traced by
# colour mask row-by-row, bed corners read off a 2% grid.
# Colour choice is forced by the frame: accent red is invisible on a red truck and ink
# vanishes into the bed's shadow line, so the bed takes the solid street colour and the
# lane markings take the dashed ink the guide already uses for fixed context.
BED    = (29.0, 46.6, 43.5, 42.9)    # open cargo area, inside the red side walls
LANE_L = [(9.9, 0), (4.6, 100)]      # solid yellow, tilting with the overpass perspective
LANE_R = [(88.0, 0), (88.6, 47)]     # broken white; the dash ends inside the frame

def poly(pts): return " ".join(f"{x:g},{y:g}" for x, y in pts)

svg_txt = ('<svg viewBox="0 0 100 100" preserveAspectRatio="none">'
  f'<polyline points="{poly(LANE_L)}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/>'
  f'<polyline points="{poly(LANE_R)}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/>'
  f'<rect x="{BED[0]}" y="{BED[1]}" width="{BED[2]}" height="{BED[3]}" fill="none" stroke="{STREET}" stroke-width="1.7" vector-effect="non-scaling-stroke"/>'
  '</svg>')
labels = [("the cast", "al-street", 50, 42),
          ("every frame", "", 21, 95)]

mock_paths = [
    (f"M {LANE_L[0][0]} {LANE_L[0][1]} L {LANE_L[1][0]} {LANE_L[1][1]}", INK),
    (f"M {LANE_R[0][0]} {LANE_R[0][1]} L {LANE_R[1][0]} {LANE_R[1][1]}", INK),
    (f"M {BED[0]} {BED[1]} L {BED[0]+BED[2]} {BED[1]} L {BED[0]+BED[2]} {BED[1]+BED[3]} "
     f"L {BED[0]} {BED[1]+BED[3]} L {BED[0]} {BED[1]}", STREET)]

if __name__ == "__main__":
    bake("cartagena-cp10.jpg", "mock-cart.jpg", mock_paths, labels)
    print(svg_txt)
    for t,c,l,tp in labels: print(f'<span class="anno-label {c}" style="left:{l}%;top:{tp}%">{t}</span>')
