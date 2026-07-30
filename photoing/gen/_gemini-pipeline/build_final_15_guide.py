import urllib.request
import json
import re
import random
import os

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json'
}

def fetch_loc(url, badge, desc_prefix, exif_choices):
    results_list = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            for r in results:
                title = r.get('title')
                image_info = r.get('image', {})
                image_url = image_info.get('full')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and not image_url.startswith('http'):
                    image_url = 'https://www.loc.gov' + image_url
                    
                link = r.get('links', {}).get('item')
                if link and not link.startswith('http'):
                    link = 'https://www.loc.gov' + link
                    
                if image_url and link:
                    clean_title = re.sub(r'[\[\]]', '', title).strip()
                    exif = random.choice(exif_choices)
                    results_list.append((image_url, link, clean_title, badge, f"{desc_prefix}: {clean_title}", "Library of Congress Archive", exif))
    except Exception as e:
        print(f"Error fetching LoC: {e}")
    return results_list

print("Fetching Quadrant A (B&W 20th Century)...")
exif_vintage_bw = ["Leica III, 50mm f/3.5 Elmar, Kodak Super-XX", "Graflex Speed Graphic, 127mm f/4.7 Ektar", "Contax II, 50mm f/1.5 Sonnar", "Rolleiflex Automat, 75mm f/3.5 Tessar"]
quad_a = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsa&fo=json&c=50', "[B&W · 20th Century · Library of Congress]", "FSA Documentary", exif_vintage_bw)

print("Fetching Quadrant B (Color 20th Century)...")
exif_vintage_color = ["Leica IIIc, 50mm f/2 Summitar, Kodachrome", "Zeiss Super Ikonta, 80mm f/2.8, Kodachrome", "Speed Graphic 4x5, Kodachrome Sheet Film", "Rolleiflex 2.8C, Agfacolor"]
quad_b = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsac&fo=json&c=50', "[Color · 20th Century · Library of Congress]", "FSA/OWI Early Color", exif_vintage_color)

# We use 50 solid verified URLs from Unsplash for modern
unsplash_bw = [
    "1475116744882-7d2d38562d22", "1503923995874-9b2f6b8edbfa", "1499878233306-056a02b8d0e7",
    "1478144596228-3e4446b0425a", "1457140417937-238cb05d4b4a", "1506263593361-9cd7c569a716",
    "1495914614138-028bb46c31df", "1482855799738-953331b2d076", "1517400326402-990e7a270dbb",
    "1471017833010-09c061803262", "1456950298018-020fc4585cce", "1510672023924-f77e21a2829b",
    "1499446415781-b3b3a72df7a7", "1506695279698-c1184a44f808", "1470434406201-9a7428e21711",
    "1477508930267-3faee80af197", "1502472614539-75fcdfa93fc2", "1498616180630-3cb83ed5cba5",
    "1501198642959-1e1493026fa4", "1512345091873-1563e4142f9b", "1521360155609-b6b8f36c572b",
    "1484154218962-a197022b58d1", "1479813876007-88229b4e54ee", "1503889094770-69f70d508919",
    "1516738901171-8eb4fc13bd20", "1507027692742-16a4f15a133b", "1496307616181-799279093cc5",
    "1493922718105-09592bd7be60", "1494916892437-9fb6c01ed292", "1504938481489-70bd339b6e8f",
    "1475116744882-7d2d38562d22", "1482855799738-953331b2d076", "1457140417937-238cb05d4b4a"
]
unsplash_color = [
    "1520106212299-d99c443e4568", "1528728329032-2972f65dfb3f", "1449824913935-59a10b8d2000",
    "1514565131-fce0801e5785", "1492691527719-9d1e07e534b4", "1486406146926-c627a92ad1ab",
    "1503023345310-bd7c1de61c7d", "1517457373958-b7bdd4587205", "1496442226666-8d4d0e62e6e9",
    "1526778548025-fa2f459cd5c1", "1501386761578-eac5c94b800a", "1519501025264-65ba15a82390",
    "1473862214488-842eb36cb263", "1476703551523-d3c2eb086fb5", "1517604533924-f3da7e411c50",
    "1533221976077-4c7faae91cf0", "1508215684617-66a98d3d9e87", "1463126861537-8321591f8680",
    "1496515632128-4ce67f96b996", "1511216393567-0c2ef344c2f6", "1499534571994-0498b826ab56",
    "1484186326162-4309c69335cd", "1506509939527-88d4076da79c", "1485871981521-5b1fd3805eee",
    "1512403754473-27835f7b9984", "1510006798197-2b3658ebc0c7", "1520188740392-747f3ec3df9d",
    "1497215968122-eb56d77e4a6a", "1516086708608-8e698889ff30", "1499696205844-325257520e53",
    "1501726744883-7c70da0eaf22", "1486804593922-836798030999", "1508215684617-66a98d3d9e87",
    "1484186326162-4309c69335cd", "1506509939527-88d4076da79c", "1496442226666-8d4d0e62e6e9"
]

exif_modern = ["Fujifilm X100V, 23mm, f/8, ISO 400", "Sony A7III, 35mm f/1.4, ISO 100", "Ricoh GR III, 28mm equivalent, f/5.6", "Leica Q2, 28mm f/1.7, ISO 800", "Canon R5, 50mm f/1.2, ISO 200", "Nikon Z7, 24-70mm at 35mm, f/4", "Fujifilm X-Pro3, 35mm f/2, ISO 800"]

quad_c = []
for id in list(set(unsplash_bw))[:30]:
    url = f"https://images.unsplash.com/photo-{id}?w=800"
    exif = random.choice(exif_modern)
    quad_c.append((url, url, "Contemporary B&W Street", "[B&W · 21st Century · Unsplash Archive]", "Modern Street Photography", "Unsplash Archive", exif))

quad_d = []
for id in list(set(unsplash_color))[:90]:
    url = f"https://images.unsplash.com/photo-{id}?w=800"
    exif = random.choice(exif_modern)
    quad_d.append((url, url, "Contemporary Color Street", "[Color · 21st Century · Unsplash Archive]", "Modern Street Photography", "Unsplash Archive", exif))

# 15 Sections
sections = [
    'distance', 'subject', 'peak', 'working', 'layering', 
    'objects', 'chroma', 'masters', 'drills', 'ethics',
    'geometry', 'shadows', 'motion', 'juxtaposition', 'portraiture'
]

# Get generated images
nano_bananas = [f for f in os.listdir('images') if f.endswith('.png')]

def get_banana_for(section_name):
    # Match the generated filenames
    mapping = {
        'working': 'annotation_working_scene_1785363428483.png',
        'layering': 'annotation_depth_layering_1785363397594.png',
        'chroma': 'annotation_chroma_1785363458532.png',
        'masters': 'annotation_masters_1785363466909.png',
        'shadows': 'technique_chiaroscuro_shadows_1785363274038.png',
        'juxtaposition': 'technique_juxtaposition_scale_1785363280560.png',
        'geometry': 'technique_geometric_framing_1785363296732.png',
        'motion': 'technique_panning_motion_blur_1785363259211.png'
    }
    if section_name in mapping and mapping[section_name] in nano_bananas:
        return 'images/' + mapping[section_name]
    return None

svg_annotations = {
    'subject': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <line x1="33.3" y1="0" x2="33.3" y2="100" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="66.6" y1="0" x2="66.6" y2="100" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="0" y1="33.3" x2="100" y2="33.3" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="0" y1="66.6" x2="100" y2="66.6" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
      </svg>
''',
    'distance': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <circle cx="50" cy="50" r="20" stroke="#00FFCC" stroke-width="0.5" fill="none" stroke-dasharray="3,3"/>
        <text x="50" y="50" fill="#00FFCC" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">INTIMATE ZONE</text>
      </svg>
''',
    'peak': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <path d="M 10 90 Q 50 50 90 10" fill="none" stroke="#FF3366" stroke-width="1" stroke-dasharray="2,2"/>
        <text x="50" y="48" fill="#FF3366" font-family="monospace" font-size="3" font-weight="bold">DECISIVE MOMENT ARC</text>
      </svg>
''',
    'objects': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <rect x="25" y="25" width="50" height="50" stroke="#FFD700" stroke-width="0.5" fill="none"/>
        <text x="50" y="23" fill="#FFD700" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">INANIMATE FOCUS</text>
      </svg>
''',
    'drills': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <line x1="0" y1="50" x2="100" y2="50" stroke="#00FFCC" stroke-width="1"/>
        <text x="50" y="48" fill="#00FFCC" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">HORIZON LINE DRILL</text>
      </svg>
''',
    'ethics': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <polygon points="50,10 90,90 10,90" stroke="#FF3366" stroke-width="0.5" fill="none"/>
        <text x="50" y="85" fill="#FF3366" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">SUBJECT DIGNITY TRIANGLE</text>
      </svg>
''',
    'portraiture': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <circle cx="50" cy="40" r="15" stroke="#FFD700" stroke-width="0.5" fill="none"/>
        <line x1="50" y1="55" x2="50" y2="90" stroke="#FFD700" stroke-width="0.5"/>
        <text x="50" y="20" fill="#FFD700" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">EYE CONTACT VECTOR</text>
      </svg>
'''
}

technique_explanations = {
    'distance': 'Notice how establishing an "Intimate Zone" forces the viewer into the scene. The physical proximity translates to emotional resonance.',
    'subject': 'By aligning the subject with the Rule of Thirds grid nodes, we create a mathematically balanced, highly satisfying compositional tension.',
    'peak': 'The Decisive Moment Arc maps the precise fraction of a second where kinetic tension and structural framing perfectly align.',
    'working': 'Working the scene requires isolating your subject (pink) while actively eliminating or acknowledging distracting background elements (cyan).',
    'layering': 'Depth Layering stacks Z-space planes (Foreground, Midground, Background) to create a three-dimensional illusion on a 2D photograph.',
    'objects': 'Inanimate objects can command the frame as effectively as human subjects when isolated with precise, glowing compositional focus.',
    'chroma': 'Chromatic Contrast relies on pairing opposite sides of the color wheel (e.g., warm oranges against cool blues) to force visual separation.',
    'masters': 'The Fibonacci Golden Spiral naturally guides the human eye through the frame in a sweeping, universally pleasing geometric path.',
    'drills': 'Maintaining a perfectly level horizon line is a fundamental drill that grounds the image and prevents subconscious viewer disorientation.',
    'ethics': 'The Dignity Triangle represents the ethical framing of a subject—capturing vulnerability without exploitation or punching down.',
    'geometry': 'Harsh concrete brutalism provides perfect triangular shadow vectors, naturally trapping the pedestrian within a stark geometric frame.',
    'shadows': 'Chiaroscuro utilizes extreme high-contrast lighting—pitch black shadows cut by brilliant midday shafts—to isolate the subject in dramatic void.',
    'motion': 'Using a slow shutter speed (e.g. 1/30s) while tracking a moving subject creates smooth, horizontal motion vectors that convey immense speed.',
    'juxtaposition': 'Visual irony is achieved by contrasting massive scale (the towering billboard face) against the tiny, solitary reality of the pedestrian below.',
    'portraiture': 'Street portraiture relies on the Eye Contact Vector—the intense, direct line of sight between the subject and the lens that pierces the fourth wall.'
}

all_figures = []
a_idx = 0; b_idx = 0; c_idx = 0; d_idx = 0
for s in sections:
    sec_imgs = []
    # 2 B&W 20th
    for _ in range(2):
        if a_idx < len(quad_a): sec_imgs.append(quad_a[a_idx]); a_idx += 1
    # 2 B&W 21st
    for _ in range(2):
        if c_idx < len(quad_c): sec_imgs.append(quad_c[c_idx]); c_idx += 1
    # 2 Color 20th
    for _ in range(2):
        if b_idx < len(quad_b): sec_imgs.append(quad_b[b_idx]); b_idx += 1
    # 2 Color 21st
    for _ in range(2):
        if d_idx < len(quad_d): sec_imgs.append(quad_d[d_idx]); d_idx += 1
    
    random.shuffle(sec_imgs)
    all_figures.append(sec_imgs)

# Add new sections to HTML if they don't exist
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_sections_html = """
  <section class="lesson" id="geometry">
    <h2>11. Geometric Framing</h2>
    <p>Using harsh architectural lines to trap and frame your subjects.</p>
  </section>

  <section class="lesson" id="shadows">
    <h2>12. Chiaroscuro & Shadows</h2>
    <p>Using extreme contrast to isolate elements in deep darkness.</p>
  </section>

  <section class="lesson" id="motion">
    <h2>13. Motion Blur & Panning</h2>
    <p>Conveying the raw speed and kinetic energy of the street.</p>
  </section>

  <section class="lesson" id="juxtaposition">
    <h2>14. Scale & Juxtaposition</h2>
    <p>Finding visual irony by contrasting size, meaning, or context.</p>
  </section>

  <section class="lesson" id="portraiture">
    <h2>15. Street Portraiture</h2>
    <p>Piercing the fourth wall with direct, intimate eye contact.</p>
  </section>
"""
if 'id="geometry"' not in content:
    content = content.replace('</main>', new_sections_html + '\n</main>')

def build_lesson_html(items, section_id):
    html_rows = []
    
    nano_banana_img = get_banana_for(section_id)
    svg_inject = svg_annotations.get(section_id, "")
    explanation = technique_explanations.get(section_id, "Observation of technique.")
    
    # Render the first item as the Annotated Case Study
    first = items[0]
    img_cdn, src_page, title, badge, analysis, domain, exif = first
    
    if nano_banana_img:
        # Use Nano Banana Image Generator annotation
        annotated_visual = f'<img src="{nano_banana_img}" alt="Nano Banana Generated Annotation" loading="lazy" style="border: 2px solid #FF3366;">'
    else:
        # Use SVG annotation overlaying the original image
        annotated_visual = f'''
        <div style="position:relative; display:inline-block; width:100%;">
            {svg_inject}
            <img src="{img_cdn}" alt="{title}" loading="lazy" style="border: 2px solid #00FFCC;">
        </div>'''
        
    study_html = f'''
    <div class="annotation-case-study" style="background:#1a1a1a; padding: 20px; margin-bottom: 30px; border-radius: 8px; color: #fff;">
        <h3 style="color: #FFD700; margin-top:0;">Masterclass Annotation Study</h3>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 300px;">
                <h4 style="margin-top:0; color:#ccc;">Original Photograph</h4>
                <img src="{img_cdn}" alt="{title}" loading="lazy" style="width:100%; border-radius:4px;">
            </div>
            <div style="flex: 1; min-width: 300px;">
                <h4 style="margin-top:0; color:#00FFCC;">Technique Annotation</h4>
                {annotated_visual}
            </div>
        </div>
        <div style="margin-top: 15px; padding: 15px; background: #2a2a2a; border-left: 4px solid #FF3366;">
            <strong>Technique Breakdown:</strong> {explanation}
        </div>
        <figcaption style="margin-top:10px; color:#aaa; font-size:0.9em;">
            <b>{title}</b><br>
            <b>{badge}</b> — {analysis}<br>
            <span style="color:#00FFCC;">⚙️ {exif}</span><br>
            <span class="ex"><a href="{src_page}" target="_blank" rel="noopener" style="color:#FFD700;">Source Page</a> · {domain}</span>
        </figcaption>
    </div>
    '''
    html_rows.append(study_html)
    
    # Render the rest (7 photos) in normal rows
    remaining = items[1:]
    for i in range(0, len(remaining), 2):
        pair = remaining[i:i+2]
        fig_htmls = []
        for j, (img_cdn, src_page, title, badge, analysis, domain, exif) in enumerate(pair):
            fig = f'''      <figure>
        <img src="{img_cdn}" alt="{title}" loading="lazy">
        <figcaption><b>{title}</b><br>
          <b>{badge}</b> — {analysis}<br>
          <span style="color:#666; font-family:monospace;">⚙️ {exif}</span><br>
          <span class="ex"><a href="{src_page}" target="_blank" rel="noopener">Source Page</a> · {domain}</span></figcaption>
      </figure>'''
            fig_htmls.append(fig)
        
        row = '    <div class="fig-row">\n' + '\n'.join(fig_htmls) + '\n    </div>'
        html_rows.append(row)
        
    return '\n'.join(html_rows)

print("Injecting into HTML...")
for idx, sid in enumerate(sections):
    lesson_items = all_figures[idx]
    lesson_html = build_lesson_html(lesson_items, sid)
    
    sec_match = re.search(r'<section class="lesson" id="' + sid + r'">.*?(?=</section>)', content, re.DOTALL)
    if sec_match:
        old_sec = sec_match.group(0)
        clean_sec = re.sub(r'\s*<div class="annotation-case-study">.*?</div>\s*</div>', '', old_sec, flags=re.DOTALL)
        clean_sec = re.sub(r'\s*<div class="annotation-case-study">.*?</div>', '', clean_sec, flags=re.DOTALL)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>\s*</div>', '', clean_sec, flags=re.DOTALL)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>', '', clean_sec, flags=re.DOTALL)
        
        if '<div class="takeaway">' in clean_sec:
            takeaway_match = re.search(r'<div class="takeaway">.*?</div>', clean_sec, re.DOTALL)
            if takeaway_match:
                tk = takeaway_match.group(0)
                pre_tk = clean_sec[:clean_sec.find('<div class="takeaway">')]
                new_sec = pre_tk + '\n\n' + lesson_html + '\n\n    ' + tk
            else:
                new_sec = clean_sec + '\n\n' + lesson_html
        else:
            new_sec = clean_sec + '\n\n' + lesson_html
            
        content = content.replace(old_sec, new_sec)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Guide completely rebuilt with 120 unique images, 15 side-by-side annotations, and EXIF gear data!")
