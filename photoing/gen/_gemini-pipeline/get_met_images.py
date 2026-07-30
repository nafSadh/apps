import urllib.request
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

api_url = 'https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&medium=Photographs&q=street'
req = urllib.request.Request(api_url, headers=headers)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())

obj_ids = data['objectIDs'][:80]
met_images = []

for oid in obj_ids:
    if len(met_images) >= 20:
        break
    obj_url = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}'
    try:
        r = urllib.request.urlopen(urllib.request.Request(obj_url, headers=headers))
        od = json.loads(r.read().decode())
        img = od.get('primaryImageSmall') or od.get('primaryImage')
        page = od.get('objectURL')
        title = od.get('title') or 'Metropolitan Museum Photography Master'
        if img and page:
            # Check image
            ir = urllib.request.urlopen(urllib.request.Request(img, headers=headers))
            if ir.status == 200:
                met_images.append((img, page, title))
                print(f"[{len(met_images)}/20] {title[:40]} -> {img}")
    except Exception as e:
        pass
    time.sleep(0.1)

with open('met_20_dataset.json', 'w') as f:
    json.dump(met_images, f, indent=2)

print(f"Saved {len(met_images)} verified Met Museum photos.")
