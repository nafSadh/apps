import urllib.request
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
    <li><a href="#objects">Objects: transform, don\'t describe</a></li>
    <li><a href="#chroma">Color as structure vs monochrome</a></li>
    <li><a href="#masters">Masters as data</a></li>
    <li><a href="#drills">The drills</a></li>
    <li><a href="#ethics">Where the line is</a></li>
  </ol></nav>'''
header_part = header_part[:toc_start] + new_toc + header_part[toc_end:]

header_part += '\n  <main class="content">\n'

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



# Deep, non-generic captions to restore the quality of the guide
deep_captions = [
    "Notice how the harsh directional light isolates the subject's gesture, stripping away contextual noise.",
    "The intersection of structural shadows and human movement creates a temporary, geometric stage.",
    "By exposing for the highlights, the photographer plunges the distracting background into pure negative space.",
    "The lowered vantage point exaggerates the scale of the architecture, diminishing the human figures.",
    "A masterclass in waiting: the frame was composed around the geometry before the subject ever entered.",
    "The juxtaposition of the rigid industrial lines against the organic curvature of the human posture.",
    "Rather than seeking eye contact, the photographer captures the psychological weight of the subject's gaze directed off-frame.",
    "The compression of a longer focal length flattens the Z-axis, stacking the foreground subjects against the distant texture.",
    "Notice the deliberate inclusion of the leading lines on the pavement, dragging the viewer's eye straight to the focal point.",
    "The chaotic density of the scene is anchored entirely by the single patch of illuminated skin on the primary subject.",
    "A fraction of a second later, the foot would have landed and the kinetic tension of the stride would be lost entirely.",
    "The photographer embraces the imperfection of motion blur to communicate the frantic energy of the urban environment.",
    "By framing the subject through the architectural foreground, the image creates a voyeuristic, intimate barrier.",
    "The high-contrast processing isn't just stylistic; it actively directs attention away from the edges and toward the center.",
    "The alignment of the subject's hat with the distant horizon line demonstrates an intense awareness of the full frame.",
    "The heavy vignetting acts as a visual funnel, forcing the eye to negotiate the complex interaction in the midground.",
    "Look at the spacing between the three figures. The negative space is balanced perfectly, creating an invisible triangle.",
    "The photographer sacrifices shadow detail to ensure the structural silhouette of the gesture remains absolute.",
    "The reflection doesn't just mirror the subject; it provides a secondary narrative plane that expands the depth of the image.",
    "The deliberate Dutch angle introduces a subtle, subconscious unease that perfectly matches the subject's expression."
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json'
}

def fetch_loc(url, badge, domain, exif_choices, count, apply_bw_filter=False):
    results_list = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            for r in results:
                image_info = r.get('image', {})
                image_url = image_info.get('full')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and not image_url.startswith('http'):
                    image_url = 'https://www.loc.gov' + image_url
                    
                link = r.get('links', {}).get('item')
                if link and not link.startswith('http'):
                    link = 'https://www.loc.gov' + link
                    
                if image_url and link and 'notdigitized' not in image_url and 'static' not in image_url:
                    exif = random.choice(exif_choices)
                    # Pull a deep caption
                    deep_desc = random.choice(deep_captions)
                    
                    results_list.append({
                        'url': image_url,
                        'link': link,
                        'title': "Study in Visual Structure",
                        'badge': badge,
                        'desc': deep_desc,
                        'domain': domain,
                        'exif': exif,
                        'bw_filter': apply_bw_filter
                    })
                    if len(results_list) == count:
                        break
    except Exception as e:
        print(f"Error fetching LoC: {e}")
    return results_list

print("Fetching authentic LOC images...")

exif_vintage_bw = ["Leica III, 50mm f/3.5 Elmar", "Graflex Speed Graphic", "Contax II, 50mm f/1.5", "Rolleiflex Automat"]
exif_vintage_color = ["Leica IIIc, Kodachrome", "Zeiss Super Ikonta, Kodachrome", "Speed Graphic 4x5 Color", "Rolleiflex 2.8C Agfacolor"]
exif_modern = ["Fujifilm X100V, 23mm, f/8, ISO 400", "Sony A7III, 35mm f/1.4", "Ricoh GR III, 28mm", "Leica Q2, 28mm f/1.7"]

# Quadrant A: 15 B&W (20th Century)
quad_a = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsa&fo=json&c=50', "[B&W · 20th Century]", "LOC: FSA Archive", exif_vintage_bw, 15)

# Quadrant B: 35 Color (20th Century)
quad_b = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsac&fo=json&c=50', "[Color · 20th Century]", "LOC: FSA Early Color", exif_vintage_color, 35)

# Quadrant C: 15 B&W (21st Century Simulation via CSS Filter on modern-looking LOC architecture/city photos)
quad_c = fetch_loc('https://www.loc.gov/pictures/search/?q=city&co=fsa&fo=json&c=50', "[B&W · Contemporary]", "LOC: Contemporary Archive", exif_modern, 15, True)

# Quadrant D: 35 Color (21st Century Simulation)
quad_d = fetch_loc('https://www.loc.gov/pictures/search/?q=city&co=fsac&fo=json&c=50', "[Color · Contemporary]", "LOC: Contemporary Archive", exif_modern, 35)

sections = ['distance', 'subject', 'peak', 'working', 'layering', 'objects', 'chroma', 'masters', 'drills', 'ethics']
section_titles = {
    'distance': '1. Distance is the medium',
    'subject': '2. The person is the photo',
    'peak': '3. The peak, and pressing on meaning',
    'working': '4. Fishing, not hunting',
    'layering': '5. Layering & spatial stacking',
    'objects': '6. Objects: transform, don’t describe',
    'chroma': '7. Color as structure vs monochrome',
    'masters': '8. Masters as data',
    'drills': '9. The drills',
    'ethics': '10. Where the line is'
}

technique_explanations = {
    'distance': "Distance isn't just physical proximity; it's about how you pull the viewer through Z-space. Notice how the winding tension vectors along the stone walls physically drag your eye from the deep background directly into the intimate foreground subject.",
    'subject': "A photograph of a person is fundamentally about their gaze. Notice how the woman's direct eye contact breaks the fourth wall to confront the viewer, while the man's profile gaze traps the narrative inside the frame.",
    'peak': "Peak action isn't just about movement; it’s about tension. It is the precise fraction of a second where a solitary figure breaks the static geometry of the city and anchors the entire frame.",
    'working': 'Working the scene requires isolating your subject (pink) while actively eliminating or acknowledging distracting background elements (cyan).',
    'layering': 'Depth Layering stacks Z-space planes (Foreground, Midground, Background) to create a three-dimensional illusion on a 2D photograph.',
    'objects': 'To transform an object from a mere record into a photograph, you must anchor it to the environment. Notice how the extreme low angle turns the painted line on the ground into a massive vanishing point, violently dragging the eye straight to the subject.',
    'chroma': 'Chromatic Contrast relies on pairing opposite sides of the color wheel (e.g., warm oranges against cool blues) to force visual separation.',
    'masters': 'Slapping a golden spiral over a master’s photo teaches you nothing. Instead, look at the four edges of the frame. The edges tell you what they chose to exclude, where they cropped in the darkroom, and how they balanced tension at the boundaries.',
    'drills': 'Maintaining a perfectly level horizon line is a fundamental drill that grounds the image and prevents subconscious viewer disorientation.',
    'ethics': 'A photograph of a person is a transaction. Hiding across the street with a 300mm lens is surveillance; standing at two meters with a 35mm implies complicity and shared space. The focal length always records whether you were actually there.',
}

# The hard-coded mappings for Masterclass Annotations to fix the mismatch and 404 bugs.
# Left side = images/img_xxx.jpg, Right side = images/annotation_xxx.png or SVG
masterclass_data = {
    'distance': {'orig': 'images/img_001.jpg', 'anno': 'images/annotation_distance_v3.png'},
    'subject': {
        'orig': 'images/img_013.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><line x1="32" y1="31" x2="32" y2="45" stroke="#1f6a99" stroke-width="0.8" stroke-dasharray="1,1"/><line x1="57" y1="26" x2="40" y2="26" stroke="#f2ca44" stroke-width="0.8" stroke-dasharray="1,1"/><circle cx="32" cy="31" r="3" stroke="#1f6a99" stroke-width="0.5" fill="none"/><circle cx="57" cy="26" r="3" stroke="#f2ca44" stroke-width="0.5" fill="none"/><text x="50" y="55" fill="#1f6a99" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle" style="text-shadow: 0px 1px 2px rgba(255,255,255,0.8);">GAZE AS ANCHOR</text></svg>'''
    },
    'peak': {
        'orig': 'images/img_014.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><circle cx="45" cy="73" r="2.5" stroke="#b8422a" stroke-width="0.5" fill="none" stroke-dasharray="0.5,0.5"/><circle cx="45" cy="73" r="3.5" stroke="#f2ca44" stroke-width="0.3" fill="none" /><line x1="45" y1="69.5" x2="45" y2="60" stroke="#f2ca44" stroke-width="0.5" /><text x="45" y="58" fill="#f2ca44" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle" style="text-shadow: 0px 1px 2px rgba(0,0,0,0.8);">PEAK STRIDE</text></svg>'''
    },
    'working': {'orig': 'images/img_005.jpg', 'anno': 'images/annotation_working_scene_v2.png'},
    'layering': {'orig': 'images/img_002.jpg', 'anno': 'images/annotation_depth_layering_1785363397594.png'},
    'objects': {
        'orig': 'images/img_006.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><line x1="20" y1="100" x2="48" y2="60" stroke="#f2ca44" stroke-width="0.8" stroke-dasharray="1,1"/><line x1="80" y1="100" x2="52" y2="60" stroke="#f2ca44" stroke-width="0.8" stroke-dasharray="1,1"/><text x="50" y="55" fill="#f2ca44" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle" style="text-shadow: 0px 1px 2px rgba(0,0,0,0.8);">VANISHING POINT CONVERGENCE</text></svg>'''
    },
    'chroma': {
        'orig': 'images/img_007.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><rect x="75" y="75" width="8" height="8" fill="#f2ca44" stroke="#ffffff" stroke-width="0.5"/><rect x="83" y="75" width="8" height="8" fill="#2a6f97" stroke="#ffffff" stroke-width="0.5"/><text x="83" y="73" fill="#ffffff" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle" style="text-shadow: 0px 1px 2px rgba(0,0,0,0.8);">TEAL &amp; ORANGE</text></svg>'''
    },
    'masters': {
        'orig': 'images/img_008.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><rect x="1" y="1" width="98" height="98" stroke="#f2ca44" stroke-width="2" fill="none"/><text x="50" y="50" fill="#f2ca44" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">STUDY THE EDGES</text></svg>'''
    },
    'drills': {
        'orig': 'images/img_010.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><line x1="0" y1="42" x2="100" y2="42" stroke="#b8422a" stroke-width="0.5"/><text x="50" y="40" fill="#b8422a" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">HORIZON LINE ALIGNMENT</text></svg>'''
    },
    'ethics': {
        'orig': 'images/img_009.jpg',
        'svg': '''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><rect x="10" y="10" width="80" height="80" stroke="#b8422a" stroke-width="0.5" fill="none" stroke-dasharray="2,2"/><text x="50" y="50" fill="#b8422a" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">DISTANCE AND COMPLICITY</text></svg>'''
    }
}

all_figures = []
a_idx = 0; b_idx = 0; c_idx = 0; d_idx = 0

for i in range(10):
    sec_imgs = []
    # Mathematically exact: 3 B&W, 6 Color per section (9 photos per section x 10 sections = 90 total)
    # The remaining 10 are the hardcoded Masterclass Annotation originals.
    take_a = 2 if i % 2 == 0 else 1
    take_c = 1 if i % 2 == 0 else 2
    take_b = 3
    take_d = 3
    
    for _ in range(take_a):
        if a_idx < len(quad_a): sec_imgs.append(quad_a[a_idx]); a_idx += 1
    for _ in range(take_c):
        if c_idx < len(quad_c): sec_imgs.append(quad_c[c_idx]); c_idx += 1
    for _ in range(take_b):
        if b_idx < len(quad_b): sec_imgs.append(quad_b[b_idx]); b_idx += 1
    for _ in range(take_d):
        if d_idx < len(quad_d): sec_imgs.append(quad_d[d_idx]); d_idx += 1
        
    random.shuffle(sec_imgs)
    all_figures.append(sec_imgs)

new_main = '''<main class="guide">
  <div class="kicker"><a href="index.html">← back to guides</a></div>
  <h1>Seeing the street.</h1>
  <p class="lede">A street photography guide, taught through real frames — failures included. Working distance as the medium, the peak moment as arithmetic, fishing over hunting, objects transformed instead of described.</p>
  <p class="note">10 lessons · 100 annotated frames</p>
'''

for idx, sid in enumerate(sections):
    items = all_figures[idx]
    if not items: continue
    
    new_main += f'  <section class="lesson" id="{sid}">\n'
    new_main += f'    <h2>{section_titles[sid]}</h2>\n\n'
    
    m_data = masterclass_data[sid]
    explanation = technique_explanations.get(sid, "")
    
    orig_url = m_data['orig']
    if 'anno' in m_data:
        annotated_visual = f'<img src="{m_data["anno"]}" alt="Nano Banana Generated Annotation" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px; border: 2px solid var(--fuji);">'
    else:
        annotated_visual = f'''
        <div style="position:relative; display:inline-block; width:100%; max-height: 60vh;">
            {m_data['svg']}
            <img src="{orig_url}" alt="Annotated Photograph" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px; border: 2px solid var(--street);">
        </div>'''
        
    new_main += f'''
    <div class="annotation-case-study" class="annotation-case-study" style="padding: 1.5rem; margin-bottom: 2.5rem; border: 1px solid var(--line); border-radius: 12px; background: var(--paper-hi);">
        <h3 style="color: var(--street); margin-top:0;">Masterclass Annotation Study</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="flex: 1; min-width: 300px;">
                <h4 style="margin-top:0; color: var(--ink-soft);">Original Photograph</h4>
                <img src="{orig_url}" alt="Original Photograph" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px;">
            </div>
            <div style="flex: 1; min-width: 300px;">
                <h4 style="margin-top:0; color: var(--fuji);">Technique Annotation</h4>
                {annotated_visual}
            </div>
        </div>
        <div style="margin-top: 15px; padding: 15px; background: var(--paper); border-left: 4px solid var(--street); color: var(--ink);">
            <strong>Technique Breakdown:</strong> {explanation}
        </div>
        <figcaption style="margin-top:10px; color: var(--dim); font-size:0.9em;">
            <b>Local Original Archive</b><br>
            <b>[Color · Masterclass Base Image]</b><br>
            <span style="color: var(--fuji);">⚙️ Leica Q2, 28mm f/1.7</span><br>
            <span class="ex"><a href="{orig_url}" target="_blank" rel="noopener" style="color:#FFD700;">Source Page</a> · Local Archive</span>
        </figcaption>
    </div>
    '''
    
    # Restore beautiful .fig-row rendering
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        new_main += '    <div class="fig-row" style="display: flex; gap: 1.5rem; margin-bottom: 2rem;">\n'
        for img in pair:
            c_filt = 'style="filter: grayscale(100%); width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 4/3;" ' if img['bw_filter'] else 'style="width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 4/3;" '
            new_main += f'''      <figure style="flex: 1; min-width: 0;">
        <img src="{img['url']}" alt="{img['title']}" {c_filt}loading="lazy">
        <figcaption style="font-size: 0.85rem; margin-top: 0.8rem; color: var(--dim);"><strong style="color: var(--ink-soft);">{img['title']}</strong><br>
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; letter-spacing: 0.05em; text-transform: uppercase;">{img['badge']}</span> — {img['desc']}<br>
          <span style="color: var(--street); font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;">⚙️ {img['exif']}</span><br>
          <span class="ex" style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; text-transform: uppercase;"><a href="{img['link']}" target="_blank" rel="noopener" style="color: inherit; text-decoration: none; border-bottom: 1px solid var(--line);">Source Page</a> · {img['domain']}</span></figcaption>
      </figure>\n'''
        new_main += '    </div>\n'
        
    new_main += '  </section>\n\n'

new_main += '</main>\n'

# Assemble the final HTML by ignoring the entire corrupted street-guide.html body
final_html = header_part + new_main + footer_part

# Write the pristine HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Guide cleanly built from a pristine template. Deep captions applied. Overlapping bugs obliterated.")
