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

def fetch_loc(url, badge, desc_prefix):
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
                    # Clean title
                    clean_title = re.sub(r'[\[\]]', '', title).strip()
                    results_list.append((image_url, link, clean_title, badge, f"{desc_prefix}: {clean_title}", "Library of Congress Archive"))
    except Exception as e:
        print(f"Error fetching LoC {url}: {e}")
    return results_list

def fetch_met():
    results_list = []
    url = 'https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&medium=Photographs&q=street'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            oids = data.get('objectIDs', [])[:30]
            
            for oid in oids:
                try:
                    oreq = urllib.request.Request(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}', headers=headers)
                    with urllib.request.urlopen(oreq, timeout=3) as oresp:
                        o = json.loads(oresp.read().decode('utf-8'))
                        title = o.get('title', 'Historical Street Scene')
                        img = o.get('primaryImage')
                        link = o.get('objectURL')
                        if img and link:
                            results_list.append((img, link, title, "[B&W · 19th/20th Century · Met Museum Archive]", f"Historical Archive: {title}", "Metropolitan Museum Archive"))
                except Exception:
                    pass
    except Exception as e:
        print(f"Error fetching Met: {e}")
    return results_list

print("Fetching Quadrant A (B&W 20th Century)...")
quad_a = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsa&fo=json&c=50', "[B&W · 20th Century · Library of Congress]", "FSA Documentary")
quad_a += fetch_met()

print("Fetching Quadrant B (Color 20th Century)...")
quad_b = fetch_loc('https://www.loc.gov/pictures/search/?q=street&co=fsac&fo=json&c=50', "[Color · 20th Century · Library of Congress]", "FSA/OWI Early Color")

# Hand-curated modern images from Unsplash to ensure high quality (Quadrant C & D)
modern_color = [
    ("https://images.unsplash.com/photo-1520106212299-d99c443e4568?w=800", "Moscow Red Square Night"),
    ("https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?w=800", "Berlin Night Skyline"),
    ("https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800", "Manhattan Skyscraper Canyon"),
    ("https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800", "Tokyo Neon Reflection"),
    ("https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800", "Golden Hour Pedestrian Stride"),
    ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800", "Glass Facade Cloud Reflection"),
    ("https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?w=800", "Eye-Level Sidewalk Portrait"),
    ("https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800", "Night Street Lamp Spotlight"),
    ("https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800", "Manhattan Crosswalk Crowd"),
    ("https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800", "Alleyway Sunlight Vector"),
    ("https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800", "Concourse Crowd Raised Hands"),
    ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800", "Urban Concourse Red Jacket"),
    ("https://images.unsplash.com/photo-1473862214488-842eb36cb263?w=800", "Subway Platform Blur"),
    ("https://images.unsplash.com/photo-1476703551523-d3c2eb086fb5?w=800", "Crosswalk Tension"),
    ("https://images.unsplash.com/photo-1517604533924-f3da7e411c50?w=800", "Umbrella in Rain"),
    ("https://images.unsplash.com/photo-1533221976077-4c7faae91cf0?w=800", "Neon Sign Typology"),
    ("https://images.unsplash.com/photo-1508215684617-66a98d3d9e87?w=800", "Bus Window Reflection"),
    ("https://images.unsplash.com/photo-1463126861537-8321591f8680?w=800", "Commuter Silhouette"),
    ("https://images.unsplash.com/photo-1496515632128-4ce67f96b996?w=800", "Bicycle Courier Speed Blur"),
    ("https://images.unsplash.com/photo-1511216393567-0c2ef344c2f6?w=800", "Street Musician Low Angle"),
    ("https://images.unsplash.com/photo-1499534571994-0498b826ab56?w=800", "Vending Machine Glow"),
    ("https://images.unsplash.com/photo-1484186326162-4309c69335cd?w=800", "Yellow Taxi Depth"),
    ("https://images.unsplash.com/photo-1506509939527-88d4076da79c?w=800", "Sidewalk Steam Vent"),
    ("https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?w=800", "Subway Station Entrance"),
    ("https://images.unsplash.com/photo-1512403754473-27835f7b9984?w=800", "Street Corner Intersection")
]

modern_bw = [
    ("https://images.unsplash.com/photo-1475116744882-7d2d38562d22?w=800", "B&W Staircase Shadow"),
    ("https://images.unsplash.com/photo-1503923995874-9b2f6b8edbfa?w=800", "B&W Commuter Steps"),
    ("https://images.unsplash.com/photo-1499878233306-056a02b8d0e7?w=800", "B&W Rain Umbrella Silhouette"),
    ("https://images.unsplash.com/photo-1478144596228-3e4446b0425a?w=800", "B&W Alley Puddle Reflection"),
    ("https://images.unsplash.com/photo-1457140417937-238cb05d4b4a?w=800", "B&W Subterranean Walkway"),
    ("https://images.unsplash.com/photo-1506263593361-9cd7c569a716?w=800", "B&W Abstract Architectural Geometry"),
    ("https://images.unsplash.com/photo-1495914614138-028bb46c31df?w=800", "B&W Solitary Figure Distance"),
    ("https://images.unsplash.com/photo-1482855799738-953331b2d076?w=800", "B&W Street Crossing Texture"),
    ("https://images.unsplash.com/photo-1517400326402-990e7a270dbb?w=800", "B&W Window Silhouette Portrait"),
    ("https://images.unsplash.com/photo-1471017833010-09c061803262?w=800", "B&W Elevated Train Structure"),
    ("https://images.unsplash.com/photo-1456950298018-020fc4585cce?w=800", "B&W Pavement Gradient"),
    ("https://images.unsplash.com/photo-1510672023924-f77e21a2829b?w=800", "B&W Bus Stop Waiting"),
    ("https://images.unsplash.com/photo-1499446415781-b3b3a72df7a7?w=800", "B&W Market Vendor Focus"),
    ("https://images.unsplash.com/photo-1506695279698-c1184a44f808?w=800", "B&W Subway Exit Light Shaft"),
    ("https://images.unsplash.com/photo-1470434406201-9a7428e21711?w=800", "B&W Bridge Suspension Angles"),
    ("https://images.unsplash.com/photo-1477508930267-3faee80af197?w=800", "B&W Street Lamp Perspective"),
    ("https://images.unsplash.com/photo-1502472614539-75fcdfa93fc2?w=800", "B&W Train Window Reflection"),
    ("https://images.unsplash.com/photo-1498616180630-3cb83ed5cba5?w=800", "B&W Skateboarder Motion Blur"),
    ("https://images.unsplash.com/photo-1501198642959-1e1493026fa4?w=800", "B&W Crowded Intersection Pulse")
]

def make_quad(base_list, count, badge):
    res = []
    # Make sure we don't sample more than exists
    sample_count = min(count, len(base_list))
    sampled = random.sample(base_list, sample_count)
    for cdn, title in sampled:
        url_key = cdn.split('?')[0] if '?' in cdn else cdn
        res.append((cdn, url_key, title, badge, f"Contemporary Street: {title}", "Unsplash Archive"))
    return res

print("Formatting Quadrants...")
quad_c = make_quad(modern_bw, 19, "[B&W · 21st Century · Unsplash Archive]")
quad_d = make_quad(modern_color, 25, "[Color · 21st Century · Unsplash Archive]")

# We need about 110-120 total. Let's aim for 12 sections * 10 images = 120, but we only have 10 sections.
# Let's do 11 images per section = 110.
# Breakdown per section: 2 B&W 20th, 2 B&W 21st, 3 Color 20th, 4 Color 21st = 11 total.
# Total B&W = 4/11 = 36% (slightly over 30%, user is flexible)

random.shuffle(quad_a)
random.shuffle(quad_b)
random.shuffle(quad_c)
random.shuffle(quad_d)

sections = ['distance', 'subject', 'peak', 'working', 'layering', 'objects', 'chroma', 'masters', 'drills', 'ethics']

all_figures = []
a_idx = 0
b_idx = 0
c_idx = 0
d_idx = 0

for s in sections:
    sec_imgs = []
    
    # 2 B&W 20th
    for _ in range(2):
        if a_idx < len(quad_a): sec_imgs.append(quad_a[a_idx]); a_idx += 1
    # 2 B&W 21st
    for _ in range(2):
        if c_idx < len(quad_c): sec_imgs.append(quad_c[c_idx]); c_idx += 1
    # 4 Color 20th
    for _ in range(4):
        if b_idx < len(quad_b): sec_imgs.append(quad_b[b_idx]); b_idx += 1
    # 3 Color 21st
    for _ in range(3):
        if d_idx < len(quad_d): sec_imgs.append(quad_d[d_idx]); d_idx += 1
        
    random.shuffle(sec_imgs)
    all_figures.append(sec_imgs)

# Create 5 bold SVG architectural annotations
svg_annotations = {
    # 1. Rule of Thirds / Golden Spiral (Subject section)
    'subject': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <!-- Technical Rule of Thirds Grid -->
        <line x1="33.3" y1="0" x2="33.3" y2="100" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="66.6" y1="0" x2="66.6" y2="100" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="0" y1="33.3" x2="100" y2="33.3" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <line x1="0" y1="66.6" x2="100" y2="66.6" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <!-- Node Highlights -->
        <circle cx="33.3" cy="33.3" r="3" fill="none" stroke="#FF3366" stroke-width="1"/>
        <circle cx="66.6" cy="66.6" r="3" fill="none" stroke="#FF3366" stroke-width="1"/>
        <text x="35" y="32" fill="#FFD700" font-family="monospace" font-size="3" font-weight="bold">FOCAL NODE</text>
      </svg>
''',
    
    # 2. Motion tension vectors (Peak Action section)
    'peak': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <!-- Kinetic Vectors -->
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#00FFCC" />
          </marker>
        </defs>
        <path d="M 10 80 Q 40 40 70 20" fill="none" stroke="#00FFCC" stroke-width="1" marker-end="url(#arrow)" stroke-dasharray="3,1"/>
        <path d="M 90 90 Q 60 70 40 50" fill="none" stroke="#FF3366" stroke-width="1" marker-end="url(#arrow)" stroke-dasharray="3,1"/>
        <text x="75" y="18" fill="#00FFCC" font-family="monospace" font-size="3" font-weight="bold">TRAJECTORY</text>
      </svg>
''',

    # 3. Depth Layering (Layering section)
    'layering': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <!-- Z-Space Planes -->
        <polygon points="0,70 100,70 100,100 0,100" fill="rgba(255, 51, 102, 0.2)" stroke="#FF3366" stroke-width="0.5"/>
        <text x="2" y="98" fill="#FF3366" font-family="monospace" font-size="3" font-weight="bold">FOREGROUND (Z=1)</text>
        
        <polygon points="20,40 80,40 80,70 20,70" fill="rgba(0, 255, 204, 0.2)" stroke="#00FFCC" stroke-width="0.5"/>
        <text x="22" y="68" fill="#00FFCC" font-family="monospace" font-size="3" font-weight="bold">MIDGROUND (Z=2)</text>
        
        <polygon points="40,10 60,10 60,40 40,40" fill="rgba(255, 215, 0, 0.2)" stroke="#FFD700" stroke-width="0.5"/>
        <text x="42" y="38" fill="#FFD700" font-family="monospace" font-size="2" font-weight="bold">BACKGROUND</text>
      </svg>
''',

    # 4. Architectural vanishing points (Working section)
    'working': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <!-- Perspective Vanishing Lines -->
        <circle cx="50" cy="50" r="1.5" fill="#FF3366" />
        <line x1="0" y1="0" x2="50" y2="50" stroke="#00FFCC" stroke-width="0.5" stroke-dasharray="1,1"/>
        <line x1="0" y1="100" x2="50" y2="50" stroke="#00FFCC" stroke-width="0.5" stroke-dasharray="1,1"/>
        <line x1="100" y1="0" x2="50" y2="50" stroke="#00FFCC" stroke-width="0.5" stroke-dasharray="1,1"/>
        <line x1="100" y1="100" x2="50" y2="50" stroke="#00FFCC" stroke-width="0.5" stroke-dasharray="1,1"/>
        <text x="52" y="52" fill="#FF3366" font-family="monospace" font-size="3" font-weight="bold">VANISHING POINT</text>
      </svg>
''',

    # 5. Chromatic Structure (Chroma section)
    'chroma': '''
      <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;">
        <!-- Color Swatch Extraction -->
        <circle cx="15" cy="85" r="8" fill="transparent" stroke="#FF3366" stroke-width="1.5"/>
        <circle cx="85" cy="15" r="8" fill="transparent" stroke="#00FFCC" stroke-width="1.5"/>
        <line x1="15" y1="85" x2="85" y2="15" stroke="#FFD700" stroke-width="0.5" stroke-dasharray="2,2"/>
        <text x="40" y="48" fill="#FFD700" font-family="monospace" font-size="3" font-weight="bold">COMPLEMENTARY AXIS</text>
      </svg>
'''
}

def build_lesson_html(items, section_id):
    html_rows = []
    
    # Check if this section gets an annotation
    annotation_idx = 0 if section_id in svg_annotations else -1
    
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        fig_htmls = []
        for j, (img_cdn, src_page, title, badge, analysis, domain) in enumerate(pair):
            current_idx = i + j
            
            # Inject SVG annotation into the very first image of annotated sections
            svg_inject = svg_annotations[section_id] if current_idx == annotation_idx else ""
            
            fig = f'''      <figure style="position:relative;">
        {svg_inject}
        <img src="{img_cdn}" alt="{title}" loading="lazy">
        <figcaption><b>{title}</b><br>
          <b>{badge}</b> — {analysis}
          <span class="ex"><a href="{src_page}" target="_blank" rel="noopener">Source Page</a> · {domain}</span></figcaption>
      </figure>'''
            fig_htmls.append(fig)
        
        row = '    <div class="fig-row">\n' + '\n'.join(fig_htmls) + '\n    </div>'
        html_rows.append(row)
    return '\n'.join(html_rows)

print("Injecting into HTML...")
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

for idx, sid in enumerate(sections):
    lesson_items = all_figures[idx]
    lesson_html = build_lesson_html(lesson_items, sid)
    
    sec_match = re.search(r'<section class="lesson" id="' + sid + r'">.*?(?=</section>)', content, re.DOTALL)
    if sec_match:
        old_sec = sec_match.group(0)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>\s*</div>', '', old_sec, flags=re.DOTALL)
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

print(f"Guide completely rebuilt with {sum(len(x) for x in all_figures)} unique images and 5 SVG technical annotations!")
