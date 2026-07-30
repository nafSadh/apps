import re

with open('gen/build_deep_curated_guide.py', 'r') as f:
    content = f.read()

new_top = """import urllib.request
import json
import random
import os
import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'
in_practice_path = '/Users/nafsadh/src/apps/photoing/in-practice.html'

with open(in_practice_path, 'r', encoding='utf-8') as f:
    ip_content = f.read()

# Grab everything up to <main class="content">
header_part = ip_content.split('<main class="content">')[0]

# Replace the intro
intro_start = header_part.find('<div class="intro">')
intro_end = header_part.find('</div>', intro_start) + 6
new_intro = '''<div class="intro">
  <div class="kicker"><a href="/">sadh.app</a> · <a href="index.html">photoing</a> · street guide</div>
  <h1>Seeing the street.</h1>
  <p class="lede">A street photography guide, taught through real frames &mdash; failures included. Working distance as the medium, the peak moment as arithmetic, fishing over hunting, objects transformed instead of described.</p>
  <p class="standfirst">10 lessons · 100 annotated frames</p>
  </div>'''
header_part = header_part[:intro_start] + new_intro + header_part[intro_end:]

# Replace the TOC
toc_start = header_part.find('<nav class="toc">')
toc_end = header_part.find('</nav>', toc_start) + 6
new_toc = '''<nav class="toc"><span class="toc-label">On this page</span><ol>
    <li><a href="#distance">Distance is the medium</a></li>
    <li><a href="#subject">The person is the photo</a></li>
    <li><a href="#peak">The peak, and pressing on meaning</a></li>
    <li><a href="#working">Fishing, not hunting</a></li>
    <li><a href="#layering">Layering & spatial stacking</a></li>
    <li><a href="#objects">Objects: transform, don\\'t describe</a></li>
    <li><a href="#chroma">Color as structure vs monochrome</a></li>
    <li><a href="#masters">Masters as data</a></li>
    <li><a href="#drills">The drills</a></li>
    <li><a href="#ethics">Where the line is</a></li>
  </ol></nav>'''
header_part = header_part[:toc_start] + new_toc + header_part[toc_end:]

header_part += '\\n  <main class="content">\\n'

footer_part = '''
  </main>
  </div>
  <footer>
    <span>Diagrams drawn for these pages · photographs credited where shown</span>
    <span>by <a href="https://nafsadh.com">nafSadh</a></span>
  </footer>
</div>
</body>
</html>
'''
"""

# Replace from import to footer_part string block
pattern = re.compile(r"^.*?'''\n", re.DOTALL)
content = pattern.sub(new_top, content)

with open('gen/build_deep_curated_guide.py', 'w') as f:
    f.write(content)
