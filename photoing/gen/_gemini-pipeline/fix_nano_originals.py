import re

with open('street-guide.html', 'r', encoding='utf-8') as f:
    html = f.read()

mapping = {
    'working': 'images/img_005.jpg',
    'layering': 'images/img_002.jpg',
    'chroma': 'images/img_007.jpg',
    'masters': 'images/img_008.jpg',
    'distance': 'images/img_001.jpg',
    'subject': 'images/img_003.jpg',
    'peak': 'images/img_004.jpg',
    'objects': 'images/img_006.jpg'
}

for section_id, original_img in mapping.items():
    # Find the section
    sec_match = re.search(r'<section class="lesson" id="' + section_id + r'">.*?(?=</section>)', html, re.DOTALL)
    if not sec_match:
        continue
    sec_content = sec_match.group(0)
    
    # We need to replace the image src inside the Original Photograph div
    # It looks like:
    # <div style="flex: 1; min-width: 300px;">
    #     <h4 style="margin-top:0; color:#ccc;">Original Photograph</h4>
    #     <img src="https://..." alt="..." loading="lazy" style="...">
    # </div>
    
    # Find the Original Photograph block
    orig_block_match = re.search(r'(<h4[^>]*>Original Photograph</h4>\s*<img src=")([^"]+)(")', sec_content, re.DOTALL)
    if orig_block_match:
        # Check if this section actually uses Nano Banana. If it does, we replace it.
        if 'Nano Banana Generated Annotation' in sec_content:
            new_orig_block = orig_block_match.group(1) + original_img + orig_block_match.group(3)
            new_sec_content = sec_content.replace(orig_block_match.group(0), new_orig_block)
            
            # Also update the source link in the figcaption if desired, or just leave it.
            # Replace the source page link to be the original_img as well.
            link_match = re.search(r'(<span class="ex"><a href=")([^"]+)(")', new_sec_content, re.DOTALL)
            if link_match:
                new_link_block = link_match.group(1) + original_img + link_match.group(3)
                new_sec_content = new_sec_content.replace(link_match.group(0), new_link_block)
                
            html = html.replace(sec_content, new_sec_content)

with open('street-guide.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed original photographs to perfectly match Nano Banana annotations!")
