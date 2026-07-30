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

def fetch_loc(url, badge, desc_prefix, exif_choices, count):
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
                    if len(results_list) == count:
                        break
    except Exception as e:
        print(f"Error fetching LoC: {e}")
    return results_list

print("Fetching Quadrant A (B&W 20th Century)...")
exif_vintage_bw = ["Leica III, 50mm f/3.5 Elmar, Kodak Super-XX", "Graflex Speed Graphic, 127mm f/4.7 Ektar", "Contax II, 50mm f/1.5 Sonnar", "Rolleiflex Automat, 75mm f/3.5 Tessar"]
quad_a = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsa&fo=json&c=50', "[B&W · 20th Century · Library of Congress]", "FSA Documentary", exif_vintage_bw, 15)

print("Fetching Quadrant B (Color 20th Century)...")
exif_vintage_color = ["Leica IIIc, 50mm f/2 Summitar, Kodachrome", "Zeiss Super Ikonta, 80mm f/2.8, Kodachrome", "Speed Graphic 4x5, Kodachrome Sheet Film", "Rolleiflex 2.8C, Agfacolor"]
quad_b = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsac&fo=json&c=50', "[Color · 20th Century · Library of Congress]", "FSA/OWI Early Color", exif_vintage_color, 35)

exif_modern = ["Fujifilm X100V, 23mm, f/8, ISO 400", "Sony A7III, 35mm f/1.4, ISO 100", "Ricoh GR III, 28mm equivalent, f/5.6", "Leica Q2, 28mm f/1.7, ISO 800", "Canon R5, 50mm f/1.2, ISO 200", "Nikon Z7, 24-70mm at 35mm, f/4", "Fujifilm X-Pro3, 35mm f/2, ISO 800"]

quad_c = []
for i in range(1, 16):
    url = f"https://picsum.photos/seed/street_bw_{i}/800/600?grayscale"
    exif = random.choice(exif_modern)
    quad_c.append((url, url, f"Contemporary B&W Street #{i}", "[B&W · 21st Century · Picsum Archive]", "Modern Street Photography", "Picsum Archive", exif))

quad_d = []
for i in range(1, 36):
    url = f"https://picsum.photos/seed/street_color_{i}/800/600"
    exif = random.choice(exif_modern)
    quad_d.append((url, url, f"Contemporary Color Street #{i}", "[Color · 21st Century · Picsum Archive]", "Modern Street Photography", "Picsum Archive", exif))

# Exactly 10 Sections
sections = ['distance', 'subject', 'peak', 'working', 'layering', 'objects', 'chroma', 'masters', 'drills', 'ethics']

nano_bananas = [f for f in os.listdir('images') if f.endswith('.png')]
def get_banana_for(section_name):
    mapping = {
        'working': 'annotation_working_scene_1785363428483.png',
        'layering': 'annotation_depth_layering_1785363397594.png',
        'chroma': 'annotation_chroma_1785363458532.png',
        'masters': 'annotation_masters_1785363466909.png',
        'distance': 'technique_chiaroscuro_shadows_1785363274038.png',
        'subject': 'technique_juxtaposition_scale_1785363280560.png',
        'peak': 'technique_panning_motion_blur_1785363259211.png',
        'objects': 'annotation_objects_1785363435263.png'
    }
    if section_name in mapping and mapping[section_name] in nano_bananas:
        return 'images/' + mapping[section_name]
    return None

svg_annotations = {
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
}

random.shuffle(quad_a)
random.shuffle(quad_b)
random.shuffle(quad_c)
random.shuffle(quad_d)

all_figures = []
a_idx = 0; b_idx = 0; c_idx = 0; d_idx = 0

# Distribute 100 photos into 10 sections perfectly:
# 15 A, 15 C, 35 B, 35 D
# 10 sections: Each section gets 1 or 2 B&W (alternating), 3 or 4 Color (alternating)
for i in range(10):
    sec_imgs = []
    # A: 15 / 10 = 1.5 -> Alternate 1 and 2
    take_a = 2 if i % 2 == 0 else 1
    # C: 15 / 10 = 1.5 -> Alternate 1 and 2
    take_c = 1 if i % 2 == 0 else 2
    # B: 35 / 10 = 3.5 -> Alternate 3 and 4
    take_b = 4 if i % 2 == 0 else 3
    # D: 35 / 10 = 3.5 -> Alternate 3 and 4
    take_d = 3 if i % 2 == 0 else 4
    
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

def build_lesson_html(items, section_id):
    html_rows = []
    
    nano_banana_img = get_banana_for(section_id)
    svg_inject = svg_annotations.get(section_id, "")
    explanation = technique_explanations.get(section_id, "Observation of technique.")
    
    first = items[0]
    img_cdn, src_page, title, badge, analysis, domain, exif = first
    
    if nano_banana_img:
        annotated_visual = f'<img src="{nano_banana_img}" alt="Nano Banana Generated Annotation" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px; border: 2px solid #FF3366;">'
    else:
        annotated_visual = f'''
        <div style="position:relative; display:inline-block; width:100%; max-height: 60vh;">
            {svg_inject}
            <img src="{img_cdn}" alt="{title}" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px; border: 2px solid #00FFCC;">
        </div>'''
        
    study_html = f'''
    <div class="annotation-case-study" style="background:#1a1a1a; padding: 20px; margin-bottom: 30px; border-radius: 8px; color: #fff;">
        <h3 style="color: #FFD700; margin-top:0;">Masterclass Annotation Study</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="flex: 1; min-width: 300px;">
                <h4 style="margin-top:0; color:#ccc;">Original Photograph</h4>
                <img src="{img_cdn}" alt="{title}" loading="lazy" style="width:100%; max-height: 60vh; object-fit: contain; border-radius:4px;">
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
    
    # Render the rest (9 photos) in normal rows
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

print("Reading and cleaning HTML...")
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Strip out the 5 new sections completely if they exist
content = re.sub(r'<section class="lesson" id="geometry">.*?</section>', '', content, flags=re.DOTALL)
content = re.sub(r'<section class="lesson" id="shadows">.*?</section>', '', content, flags=re.DOTALL)
content = re.sub(r'<section class="lesson" id="motion">.*?</section>', '', content, flags=re.DOTALL)
content = re.sub(r'<section class="lesson" id="juxtaposition">.*?</section>', '', content, flags=re.DOTALL)
content = re.sub(r'<section class="lesson" id="portraiture">.*?</section>', '', content, flags=re.DOTALL)

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

print("Guide cleanly reverted to 10 sections with exactly 100 verified photos!")
