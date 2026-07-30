import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1-to-1 Image-to-Source Page Mappings:
# Pexels photos link to www.pexels.com/photo/...
# Unsplash photos link to unsplash.com/photos/...
# LoC photos link to www.loc.gov/item/...
# Met Museum photos link to www.metmuseum.org/art/collection/search/...
# Wikimedia photos link to commons.wikimedia.org/wiki/File:...

# Replace Pexels source links on 1105666 figure
content = re.sub(
    r'<img src="https://images\.pexels\.com/photos/1105666/[^"]*" alt="([^"]*)" loading="lazy">\s*<figcaption><b>([^<]*)</b><br>\s*<b>([^<]*)</b> — ([^<]*)<span class="ex"><a href="[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span></figcaption>',
    r'<img src="https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=800" alt="\1" loading="lazy">\n        <figcaption><b>\2</b><br>\n          <b>\3</b> — \4<span class="ex"><a href="https://www.pexels.com/photo/1105666/" target="_blank" rel="noopener">Source Page</a> · Pexels Archive</span></figcaption>',
    content
)

# Apply 1-to-1 matching across all Unsplash figures:
def fix_unsplash_links(m):
    pid = m.group(1)
    full_fig = m.group(0)
    full_fig = re.sub(r'href="https://[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span>', f'href="https://unsplash.com/photos/{pid}" target="_blank" rel="noopener">Source Page</a> · Unsplash Archive</span>', full_fig)
    return full_fig

content = re.sub(r'<figure>\s*<img src="https://images\.unsplash\.com/photo-([0-9a-fA-F-]+)\?[^"]*"[\s\S]*?</figure>', fix_unsplash_links, content)

# Apply 1-to-1 matching across all Pexels figures:
def fix_pexels_links(m):
    pxid = m.group(1)
    full_fig = m.group(0)
    full_fig = re.sub(r'href="https://[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span>', f'href="https://www.pexels.com/photo/{pxid}/" target="_blank" rel="noopener">Source Page</a> · Pexels Archive</span>', full_fig)
    return full_fig

content = re.sub(r'<figure>\s*<img src="https://images\.pexels\.com/photos/(\d+)/[^"]*"[\s\S]*?</figure>', fix_pexels_links, content)

# Apply 1-to-1 matching across all LoC figures:
def fix_loc_links(m):
    lid = m.group(1)
    full_fig = m.group(0)
    full_fig = re.sub(r'href="https://[^"]*" target="_blank" rel="noopener">Source Page</a> · [^<]*</span>', f'href="https://www.loc.gov/item/fsa_{lid}/" target="_blank" rel="noopener">Source Page</a> · Library of Congress Archive</span>', full_fig)
    return full_fig

content = re.sub(r'<figure>\s*<img src="https://tile\.loc\.gov/[^"]*/([^/]+)\.jpg"[\s\S]*?</figure>', fix_loc_links, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html source page links corrected with strict 1-to-1 matching to original photo pages!")
