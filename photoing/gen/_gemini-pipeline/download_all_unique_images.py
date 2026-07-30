import re
import urllib.request
import os
import json

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'
out_dir = '/Users/nafsadh/src/apps/photoing/inspect_images'
os.makedirs(out_dir, exist_ok=True)

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

imgs = re.findall(r'<img\s+src=[\"\'](https?://[^\'\"]+)[\"\']', content)
unique_imgs = list(dict.fromkeys(imgs))

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

print(f"Total unique images to download and visually inspect: {len(unique_imgs)}")

download_manifest = []

for idx, url in enumerate(unique_imgs):
    ext = 'jpg'
    filename = f"img_{idx+1:03d}.{ext}"
    filepath = os.path.join(out_dir, filename)
    
    success = False
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            with open(filepath, 'wb') as f:
                f.write(data)
            success = True
    except Exception as e:
        print(f"Failed to download #{idx+1}: {url} ({e})")
        
    download_manifest.append({
        'index': idx + 1,
        'url': url,
        'local_path': filepath,
        'downloaded': success
    })

with open(os.path.join(out_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(download_manifest, f, indent=2)

print(f"Manifest written to {out_dir}/manifest.json. Successfully downloaded {sum(1 for d in download_manifest if d['downloaded'])} images.")
