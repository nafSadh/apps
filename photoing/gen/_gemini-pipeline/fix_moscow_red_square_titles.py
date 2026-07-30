import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update every figure using photo-1520106212299-d99c443e4568:
content = re.sub(
    r'<figure>\s*<img src="https://images\.unsplash\.com/photo-1520106212299-d99c443e4568\?[^"]*" alt="[^"]*" loading="lazy">\s*<figcaption><b>[^<]*</b><br>\s*<b>[^<]*</b> — [^<]*<span class="ex"><a href="[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span></figcaption>\s*</figure>',
    '''<figure>
        <img src="https://images.unsplash.com/photo-1520106212299-d99c443e4568?w=800" alt="Moscow Red Square Night & St. Basil's Cathedral Illumination" loading="lazy">
        <figcaption><b>Moscow Red Square Night & St. Basil's Cathedral Illumination</b><br>
          <b>[Color · 21st Century · Unsplash Archive]</b> — Nocturnal Perspective: Low-angle pavement vector pointing toward illuminated onion domes of St. Basil's Cathedral under a starry sky.
          <span class="ex"><a href="https://unsplash.com/photos/520106212299-d99c443e4568" target="_blank" rel="noopener">Source Page</a> · Unsplash Archive</span></figcaption>
      </figure>''',
    content
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html updated: 1520106212299-d99c443e4568 correctly titled 'Moscow Red Square Night & St. Basil's Cathedral Illumination'.")
