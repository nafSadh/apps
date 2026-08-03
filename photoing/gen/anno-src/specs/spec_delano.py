from anno import *
# measured off delano-crop-test.jpg (1200x1809) against a percent grid, 1% in the walker region
WALK_X, WALK_TOP, WALK_BOT = 49.5, 70.1, 74.5   # near walker, hat crown to sole
ST_X,   ST_TOP,  ST_BOT    = 22.0, 37.8, 99.3   # farthest visible road surface -> bottom edge

paths = [(vbar(WALK_X, WALK_TOP, WALK_BOT, cap=1.6), ACCENT),
         (vbar(ST_X,   ST_TOP,  ST_BOT,  cap=1.6), STREET)]
labels = [("walker 4%", "al-accent", 34, 72.3),
          ("street 62%", "al-street", 37, 58)]

if __name__ == "__main__":
    bake("delano-crop-test.jpg", "mock-delano.jpg", paths, labels)
    print(svg(paths, labels))

# Shipped 2026-07-31 (re-encoded same day in the audit pass):
#   original: master TIFF crop (231,190,3537,5175) -> 1200px, quality=85, subsampling=0
#   bake("img/street-delano-staircase.jpg", "img/street-delano-staircase-anno.jpg",
#        paths, labels, quality=85)
# Bake onto the shipped original, not the master crop, so the two files stay pixel-identical
# outside the painted marks and the toggle swap doesn't pop.
