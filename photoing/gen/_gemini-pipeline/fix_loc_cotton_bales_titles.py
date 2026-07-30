import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update every figure using 8a03250v.jpg:
content = re.sub(
    r'<figure>\s*<img src="https://tile\.loc\.gov/storage-services/service/pnp/fsa/8a03000/8a03200/8a03250v\.jpg" alt="[^"]*" loading="lazy">\s*<figcaption><b>[^<]*</b><br>\s*<b>[^<]*</b> — [^<]*<span class="ex"><a href="[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span></figcaption>\s*</figure>',
    '''<figure>
        <img src="https://tile.loc.gov/storage-services/service/pnp/fsa/8a03000/8a03200/8a03250v.jpg" alt="FSA Archive — Cotton Bales & Rural Yard Stacking (1936)" loading="lazy">
        <figcaption><b>FSA Archive — Cotton Bales & Rural Yard Stacking (1936)</b><br>
          <b>[B&W · 20th Century · Library of Congress Archive]</b> — FSA Documentary Archive: Cylindrical cotton bales wrapped in wire mesh sitting in a rural dirt yard in front of a wooden clapboard store.
          <span class="ex"><a href="https://www.loc.gov/item/fsa_8a03250v/" target="_blank" rel="noopener">Source Page</a> · Library of Congress Archive</span></figcaption>
      </figure>''',
    content
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html updated: 8a03250v.jpg correctly titled 'FSA Archive — Cotton Bales & Rural Yard Stacking (1936)'.")
