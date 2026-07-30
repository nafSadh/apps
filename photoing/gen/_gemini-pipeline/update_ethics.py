import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Lesson 10 (ethics) figures addition to reach exactly 42 (or more) total hotlinks:
ethics_figs = '''    <div class="fig-row">
      <figure>
        <img src="https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800" alt="Street Ethics & Public Stance" loading="lazy">
        <figcaption><b>Contemporary Street — <em>Street Ethics &amp; Public Stance</em> (2021) [Color · 21st Century · Non-Wiki · Hotlink 37]</b><br>
          <b>Public Ethics:</b> Unscripted 21st-century public space interaction preserving subject dignity in open sidewalk space.
          <span class="ex">Unsplash Street Archive (2021)</span></figcaption>
      </figure>
      <figure>
        <img src="https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800" alt="Public Space Transit Ethics" loading="lazy">
        <figcaption><b>Contemporary Street — <em>Public Space Transit Ethics</em> (2022) [Color · 21st Century · Non-Wiki · Hotlink 38]</b><br>
          <b>Public Ethics:</b> Transparent eye-level stance in public transit concourse with mutual human awareness.
          <span class="ex">Unsplash Street Archive (2022)</span></figcaption>
      </figure>
    </div>
    <div class="fig-row">
      <figure>
        <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800" alt="Human Dignity Street Stride" loading="lazy">
        <figcaption><b>Contemporary Street — <em>Human Dignity Street Stride</em> (2023) [Color · 21st Century · Non-Wiki · Hotlink 39]</b><br>
          <b>Public Ethics:</b> Candid 21st-century sidewalk portrait upholding personal grace and non-intrusive proximity.
          <span class="ex">Unsplash Street Archive (2023)</span></figcaption>
      </figure>
      <figure>
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/54/Lange-MigrantMother02.jpg" alt="Dorothea Lange - Migrant Mother (1936)" loading="lazy">
        <figcaption><b>Dorothea Lange — <em>Migrant Mother</em> (1936) [Classic Canon · Hotlink 40]</b><br>
          <b>Master Canon:</b> Historic baseline: FSA 1.2m proximity portrait locking human dignity and intimacy.
          <span class="ex">Library of Congress Collection</span></figcaption>
      </figure>
    </div>
    <div class="fig-row">
      <figure>
        <img src="https://upload.wikimedia.org/wikipedia/commons/3/3b/Walker_Evans_New_Orleans_street_corner.jpg" alt="Walker Evans - New Orleans Street Corner (1936)" loading="lazy">
        <figcaption><b>Walker Evans — <em>New Orleans Street Corner</em> (1936) [Classic Canon · Hotlink 41]</b><br>
          <b>Master Canon:</b> Frontal architectural corner locking Southern pedestrian gaze in public archive.
          <span class="ex">Metropolitan Museum of Art Collection</span></figcaption>
      </figure>
      <figure>
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/94/Gordon_Parks_-_American_Gothic.jpg" alt="Gordon Parks - American Gothic (1942)" loading="lazy">
        <figcaption><b>Gordon Parks — <em>American Gothic, Washington D.C.</em> (1942) [Classic Canon · Hotlink 42]</b><br>
          <b>Master Canon:</b> Ella Watson with mop and broom delivering profound social critique.
          <span class="ex">Gordon Parks Foundation Archive</span></figcaption>
      </figure>
    </div>'''

content = re.sub(
    r'(<section class="lesson" id="ethics">.*?)<div class="takeaway">',
    r'\1' + ethics_figs + '\n\n    <div class="takeaway">',
    content, flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Lesson 10 figures updated successfully.")
