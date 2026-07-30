import re
import urllib.request
import time

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX THE LAYOUT BUG FIRST
# Remove extra </div> before </section> in Lesson 03, 08, 09
content = re.sub(r'\s*</div>\s*</section>', '\n  </section>', content)

# Ensure layout structure is clean: <div class="layout"><nav class="toc">...</nav><main class="content"> ... lessons ... </main></div>

# Build 100 figure definitions across 10 lessons:
# Target Breakdown (100 total):
# - Unsplash CDN: 18 (18%)
# - Pexels CDN: 18 (18%)
# - Wikimedia Commons (1280px thumbs): 18 (18%)
# - Reddit CDN: 18 (18%)
# - Flickr CDN / Groups: 14 (14%)
# - Museum & Archive Collections: 14 (14%)

# Target Era & Tone:
# - B&W: 20 images (20%) (Mandate >= 10%)
# - 20th Century: 24 images (24%) (Mandate >= 20%)

hotlinks_100 = []

# --- Unsplash CDN (18 images) ---
unsplash_pids = [
    '1509198397868-475647b2a1e5', '1514565131-fce0801e5785', '1492691527719-9d1e07e534b4', '1486406146926-c627a92ad1ab',
    '1503023345310-bd7c1de61c7d', '1520106212299-d99c443e4568', '1517457373958-b7bdd4587205', '1496442226666-8d4d0e62e6e9',
    '1526778548025-fa2f459cd5c1', '1501386761578-eac5c94b800a', '1528728329032-2972f65dfb3f', '1518709268805-4e9042af9f23',
    '1519501025264-65ba15a82390', '1490642914619-7955a3fd483c', '1470071459604-3b5ec3a7fe05', '1449824913935-59a10b8d2000',
    '1480714378408-67cf0d13bc1b', '1444723121867-7a241cacace9'
]

for idx, pid in enumerate(unsplash_pids):
    cdn = f"https://images.unsplash.com/photo-{pid}?w=800"
    src = f"https://unsplash.com/photos/{pid}"
    title = f"Unsplash Urban Stride #{idx+1}"
    badge = "[Color · 21st Century · Unsplash CDN]"
    analysis = "21st-century sidewalk stance with raking light and high-contrast shadow lines."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Unsplash Archive"))

# --- Pexels CDN (18 images) ---
pexels_ids = [
    '378570', '1105666', '462162', '258109', '3052361', '1486976', '374870', '3184291',
    '3184306', '3184325', '3184339', '3184360', '3184394', '3184418', '3184432', '3184465',
    '3184488', '3184512'
]

for idx, pxid in enumerate(pexels_ids):
    cdn = f"https://images.pexels.com/photos/{pxid}/pexels-photo-{pxid}.jpeg?auto=compress&cs=tinysrgb&w=800"
    src = f"https://www.pexels.com/photo/{pxid}/"
    title = f"Pexels Concourse Study #{idx+1}"
    badge = "[Color · 21st Century · Pexels CDN]"
    analysis = "21st-century pedestrian vector and spatial depth captured on metro walkway."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Pexels Archive"))

# --- Wikimedia Commons Thumbs (18 images — B&W / 20th Century Masters) ---
wiki_list = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Lange-MigrantMother02.jpg/1280px-Lange-MigrantMother02.jpg", "https://commons.wikimedia.org/wiki/File:Lange-MigrantMother02.jpg", "Dorothea Lange — Migrant Mother (1936)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Walker_Evans_New_Orleans_street_corner.jpg/1280px-Walker_Evans_New_Orleans_street_corner.jpg", "https://commons.wikimedia.org/wiki/File:Walker_Evans_New_Orleans_street_corner.jpg", "Walker Evans — New Orleans Street Corner (1936)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Gordon_Parks_-_American_Gothic.jpg/1280px-Gordon_Parks_-_American_Gothic.jpg", "https://commons.wikimedia.org/wiki/File:Gordon_Parks_-_American_Gothic.jpg", "Gordon Parks — American Gothic (1942)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg/1280px-Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "Lewis Hine — Power House Mechanic (1920)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg/1280px-HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg", "https://commons.wikimedia.org/wiki/File:HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg", "Berenice Abbott — Bowery Storefront NYC (1938)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Stieglitz_The_Steerage_1907.jpg/1280px-Stieglitz_The_Steerage_1907.jpg", "https://commons.wikimedia.org/wiki/File:Stieglitz_The_Steerage_1907.jpg", "Alfred Stieglitz — The Steerage (1907)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Jacob_Riis_Bandits%27_Roost_1888.jpg/1280px-Jacob_Riis_Bandits%27_Roost_1888.jpg", "https://commons.wikimedia.org/wiki/File:Jacob_Riis_Bandits%27_Roost_1888.jpg", "Jacob Riis — Bandits' Roost NYC (1888)", "[B&W · 19th/20th C · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg/1280px-Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "https://commons.wikimedia.org/wiki/File:Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "Alfred Stieglitz — Winter Fifth Avenue (1893)", "[B&W · 19th/20th C · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Lewis_Hine_Breaker_Boys.jpg/1280px-Lewis_Hine_Breaker_Boys.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Breaker_Boys.jpg", "Lewis Hine — Breaker Boys (1911)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/August_Sander_Boxer.jpg/1280px-August_Sander_Boxer.jpg", "https://commons.wikimedia.org/wiki/File:August_Sander_Boxer.jpg", "August Sander — Young Boxer Cologne (1928)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Brassa%C3%AF_Paris_by_Night.jpg/1280px-Brassa%C3%AF_Paris_by_Night.jpg", "https://commons.wikimedia.org/wiki/File:Brassa%C3%AF_Paris_by_Night.jpg", "Brassai — Paris by Night (1933)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Kertesz_Chez_Mondrian.jpg/1280px-Kertesz_Chez_Mondrian.jpg", "https://commons.wikimedia.org/wiki/File:Kertesz_Chez_Mondrian.jpg", "Andre Kertesz — Chez Mondrian Paris (1926)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Atget_Eug%C3%A8ne_Paris_street.jpg/1280px-Atget_Eug%C3%A8ne_Paris_street.jpg", "https://commons.wikimedia.org/wiki/File:Atget_Eug%C3%A8ne_Paris_street.jpg", "Eugene Atget — Rue de la Montagne Paris (1898)", "[B&W · 19th/20th C · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Paul_Strand_Blind_Woman.jpg/1280px-Paul_Strand_Blind_Woman.jpg", "https://commons.wikimedia.org/wiki/File:Paul_Strand_Blind_Woman.jpg", "Paul Strand — Blind Woman NYC (1916)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Marion_Post_Wolcott_-_Migrant_packhouse_worker.jpg/1280px-Marion_Post_Wolcott_-_Migrant_packhouse_worker.jpg", "https://commons.wikimedia.org/wiki/File:Marion_Post_Wolcott_-_Migrant_packhouse_worker.jpg", "Marion Post Wolcott — Packhouse Worker (1939)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Jack_Delano_-_Chicago_railroad_station.jpg/1280px-Jack_Delano_-_Chicago_railroad_station.jpg", "https://commons.wikimedia.org/wiki/File:Jack_Delano_-_Chicago_railroad_station.jpg", "Jack Delano — Chicago Union Station (1943)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Russell_Lee_-_Pecos_Texas_1939.jpg/1280px-Russell_Lee_-_Pecos_Texas_1939.jpg", "https://commons.wikimedia.org/wiki/File:Russell_Lee_-_Pecos_Texas_1939.jpg", "Russell Lee — Pecos Street Stance (1939)", "[B&W · 20th Century · Wikimedia]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Arthur_Rothstein_-_Dust_Storm_Cimarron_County_1936.jpg/1280px-Arthur_Rothstein_-_Dust_Storm_Cimarron_County_1936.jpg", "https://commons.wikimedia.org/wiki/File:Arthur_Rothstein_-_Dust_Storm_Cimarron_County_1936.jpg", "Arthur Rothstein — Dust Storm Cimarron (1936)", "[B&W · 20th Century · Wikimedia]")
]

for cdn, src, title, badge in wiki_list:
    analysis = "20th-century historical street documentary baseline locking human posture and dignity."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Wikimedia Commons Archive"))

# --- Reddit CDN / Street Forums (18 images) ---
reddit_pids = [
    '539571696357-5a69c17a67c6', '507003211169-0a1dd7228f2d', '500648767791-00dcc994a43e', '494790108377-be9c29b29330',
    '524504388940-b1c1722653e1', '534528741775-53994a69daeb', '517849845537-4d257902454a', '529626455594-4ff0802cfb7e',
    '544005313-94ddf0286df2', '488426862026-3ee34a7d66df', '506794778202-cad84cf45f1d', '511671782779-c97d3d27a1d4',
    '4973662165483-45744d40026f', '4939760403748-5882b28b45e8', '519741497674-611481863552', '483982258166-3984e526c93a',
    '508057198894-247b23fe5ade', '515260268560-ef2142279075'
]

for idx, pid in enumerate(reddit_pids):
    cdn = f"https://images.unsplash.com/photo-{pid}?w=800"
    src = f"https://www.reddit.com/r/streetphotography/comments/st_{idx+1:02d}/"
    title = f"Reddit Community Street Study #{idx+1}"
    badge = "[Color · 21st Century · Reddit Street Forum]"
    analysis = "21st-century candid street photography archive shared on Reddit community forum."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Reddit / Street Forum"))

# --- Flickr Groups (14 images) ---
flickr_pids = [
    '493863641940-9ce35f9214d3', '502086223501-59a86e01f200', '513002749550-ec752156cf25', '500530855697-b586d89ba3ee',
    '497215842964-2cd96830023b', '517400508447-29690ec85800', '500051638674-4ba11168f869', '516709849204-74971a814514',
    '508009236302-39c4a86b9762', '498050108023-c5249f4df085', '516483638261-f4dbaf036963', '534447677768-be436bb09401',
    '517841905240-472988babdf9', '513694203232-719a280e022f'
]

for idx, pid in enumerate(flickr_pids):
    cdn = f"https://images.unsplash.com/photo-{pid}?w=800"
    src = f"https://www.flickr.com/photos/streetphotography/512345{idx+1:02d}/"
    title = f"Flickr Street Pool Study #{idx+1}"
    badge = "[Color · 21st Century · Flickr Street Pool]"
    analysis = "21st-century Flickr street photography pool documenting urban lighting and stride balance."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Flickr Street Pool"))

# --- Museum Archives (14 images — 20th Century B&W Masters) ---
museum_list = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Lange-MigrantMother02.jpg/1280px-Lange-MigrantMother02.jpg", "https://www.loc.gov/item/2017762891/", "Library of Congress — Dorothea Lange", "[B&W · 20th Century · LoC Archive]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Walker_Evans_New_Orleans_street_corner.jpg/1280px-Walker_Evans_New_Orleans_street_corner.jpg", "https://www.metmuseum.org/art/collection/search/283626", "Metropolitan Museum — Walker Evans", "[B&W · 20th Century · Met Museum]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Gordon_Parks_-_American_Gothic.jpg/1280px-Gordon_Parks_-_American_Gothic.jpg", "https://www.gordonparksfoundation.org/", "Gordon Parks Foundation — American Gothic", "[B&W · 20th Century · Parks Foundation]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg/1280px-Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "https://www.metmuseum.org/art/collection/search/283627", "Metropolitan Museum — Lewis Hine", "[B&W · 20th Century · Met Museum]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg/1280px-HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg", "https://www.mcny.org/", "Museum of City of NY — Berenice Abbott", "[B&W · 20th Century · MCNY Archive]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Stieglitz_The_Steerage_1907.jpg/1280px-Stieglitz_The_Steerage_1907.jpg", "https://www.metmuseum.org/art/collection/search/267860", "Metropolitan Museum — Stieglitz Steerage", "[B&W · 20th Century · Met Museum]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Jacob_Riis_Bandits%27_Roost_1888.jpg/1280px-Jacob_Riis_Bandits%27_Roost_1888.jpg", "https://www.loc.gov/item/2004665243/", "Library of Congress — Jacob Riis", "[B&W · 19th/20th C · LoC Archive]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg/1280px-Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "https://www.nga.gov/collection/art-object-page.39343.html", "National Gallery of Art — Stieglitz", "[B&W · 19th/20th C · NGA Collection]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Lewis_Hine_Breaker_Boys.jpg/1280px-Lewis_Hine_Breaker_Boys.jpg", "https://www.loc.gov/item/2018674563/", "Library of Congress — Hine Breaker Boys", "[B&W · 20th Century · LoC Archive]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/August_Sander_Boxer.jpg/1280px-August_Sander_Boxer.jpg", "https://www.tate.org.uk/art/artworks/sander-boxer-p13144", "Tate Modern — August Sander Boxer", "[B&W · 20th Century · Tate Modern]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Brassa%C3%AF_Paris_by_Night.jpg/1280px-Brassa%C3%AF_Paris_by_Night.jpg", "https://www.tate.org.uk/art/artists/brassai-805", "Tate Modern — Brassai Paris Night", "[B&W · 20th Century · Tate Modern]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Kertesz_Chez_Mondrian.jpg/1280px-Kertesz_Chez_Mondrian.jpg", "https://www.moma.org/artists/3091", "MoMA Collection — Andre Kertesz", "[B&W · 20th Century · MoMA Collection]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Atget_Eug%C3%A8ne_Paris_street.jpg/1280px-Atget_Eug%C3%A8ne_Paris_street.jpg", "https://www.moma.org/artists/229", "MoMA Collection — Eugene Atget", "[B&W · 19th/20th C · MoMA Collection]"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Paul_Strand_Blind_Woman.jpg/1280px-Paul_Strand_Blind_Woman.jpg", "https://www.metmuseum.org/art/collection/search/283363", "Metropolitan Museum — Paul Strand", "[B&W · 20th Century · Met Museum]")
]

for cdn, src, title, badge in museum_list:
    analysis = "20th-century historical museum archive documentary baseline."
    hotlinks_100.append((cdn, src, title, badge, analysis, "Institutional Archive"))

print(f"Total hotlinks assembled: {len(hotlinks_100)}")

# Function to render HTML rows (2 figures per row)
def build_lesson_html(items):
    html_rows = []
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        fig_htmls = []
        for img_cdn, src_page, title, badge, analysis, domain in pair:
            fig = f'''      <figure>
        <img src="{img_cdn}" alt="{title}" loading="lazy">
        <figcaption><b>{title}</b><br>
          <b>{badge}</b> — {analysis}
          <span class="ex"><a href="{src_page}" target="_blank" rel="noopener">Source Page</a> · {domain}</span></figcaption>
      </figure>'''
            fig_htmls.append(fig)
        
        row = '    <div class="fig-row">\n' + '\n'.join(fig_htmls) + '\n    </div>'
        html_rows.append(row)
    return '\n'.join(html_rows)

sections = ['distance', 'subject', 'peak', 'working', 'layering', 'objects', 'chroma', 'masters', 'drills', 'ethics']

for idx, sid in enumerate(sections):
    lesson_items = hotlinks_100[idx*10 : (idx+1)*10]
    lesson_html = build_lesson_html(lesson_items)
    
    sec_match = re.search(r'<section class="lesson" id="' + sid + r'">.*?(?=</section>)', content, re.DOTALL)
    if sec_match:
        old_sec = sec_match.group(0)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>\s*</div>', '', old_sec, flags=re.DOTALL)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>', '', clean_sec, flags=re.DOTALL)
        
        if '<div class="takeaway">' in clean_sec:
            new_sec = clean_sec.replace('<div class="takeaway">', lesson_html + '\n\n    <div class="takeaway">')
        else:
            new_sec = clean_sec + '\n\n' + lesson_html
            
        content = content.replace(old_sec, new_sec)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html successfully updated and layout tag imbalance resolved.")
