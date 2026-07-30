import urllib.request
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def verify(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, timeout=5)
        return res.status == 200
    except Exception:
        return False

# Candidate pools across multiple distinct domains:

# Pool 1: Unsplash (Max 18)
unsplash_candidates = [
    '509198397868-475647b2a1e5', '514565131-fce0801e5785', '492691527719-9d1e07e534b4', '486406146926-c627a92ad1ab',
    '503023345310-bd7c1de61c7d', '520106212299-d99c443e4568', '517457373958-b7bdd4587205', '496442226666-8d4d0e62e6e9',
    '526778548025-fa2f459cd5c1', '501386761578-eac5c94b800a', '528728329032-2972f65dfb3f', '518709268805-4e9042af9f23',
    '519501025264-65ba15a82390', '490642914619-7955a3fd483c', '470071459604-3b5ec3a7fe05', '449824913935-59a10b8d2000',
    '480714378408-67cf0d13bc1b', '444723121867-7a241cacace9'
]

# Pool 2: Pexels (Max 18)
pexels_candidates = [
    '378570', '1105666', '462162', '258109', '3052361', '1486976', '374870', '3184291',
    '3184306', '3184325', '3184339', '3184360', '3184394', '3184418', '3184432', '3184465',
    '3184488', '3184512'
]

# Pool 3: Wikimedia Commons (Max 18)
wikimedia_candidates = [
    ("https://upload.wikimedia.org/wikipedia/commons/5/54/Lange-MigrantMother02.jpg", "https://commons.wikimedia.org/wiki/File:Lange-MigrantMother02.jpg", "Dorothea Lange — Migrant Mother (1936)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/3/3b/Walker_Evans_New_Orleans_street_corner.jpg", "https://commons.wikimedia.org/wiki/File:Walker_Evans_New_Orleans_street_corner.jpg", "Walker Evans — New Orleans Street Corner (1936)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/9/94/Gordon_Parks_-_American_Gothic.jpg", "https://commons.wikimedia.org/wiki/File:Gordon_Parks_-_American_Gothic.jpg", "Gordon Parks — American Gothic (1942)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/6/60/Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "Lewis Hine — Power House Mechanic (1920)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/a/a2/August_Sander_Boxer.jpg", "https://commons.wikimedia.org/wiki/File:August_Sander_Boxer.jpg", "August Sander — Young Boxer (1928)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/7/7b/Jacob_Riis_Bandits%27_Roost_1888.jpg", "https://commons.wikimedia.org/wiki/File:Jacob_Riis_Bandits%27_Roost_1888.jpg", "Jacob Riis — Bandits' Roost (1888)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/8/87/Stieglitz_The_Steerage_1907.jpg", "https://commons.wikimedia.org/wiki/File:Stieglitz_The_Steerage_1907.jpg", "Alfred Stieglitz — The Steerage (1907)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/d/d4/Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "https://commons.wikimedia.org/wiki/File:Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "Alfred Stieglitz — Winter, Fifth Avenue (1893)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/3/30/Lewis_Hine_Breaker_Boys.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Breaker_Boys.jpg", "Lewis Hine — Breaker Boys (1911)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/0/05/Brassa%C3%AF_Paris_by_Night.jpg", "https://commons.wikimedia.org/wiki/File:Brassa%C3%AF_Paris_by_Night.jpg", "Brassai — Paris by Night (1933)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/2/25/Kertesz_Chez_Mondrian.jpg", "https://commons.wikimedia.org/wiki/File:Kertesz_Chez_Mondrian.jpg", "Andre Kertesz — Chez Mondrian (1926)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/4/4e/Atget_Eug%C3%A8ne_Paris_street.jpg", "https://commons.wikimedia.org/wiki/File:Atget_Eug%C3%A8ne_Paris_street.jpg", "Eugene Atget — Rue de la Montagne (1898)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/7/78/Paul_Strand_Blind_Woman.jpg", "https://commons.wikimedia.org/wiki/File:Paul_Strand_Blind_Woman.jpg", "Paul Strand — Blind Woman (1916)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/e/e0/Marion_Post_Wolcott_-_Migrant_packhouse_worker.jpg", "https://commons.wikimedia.org/wiki/File:Marion_Post_Wolcott_-_Migrant_packhouse_worker.jpg", "Marion Post Wolcott — Packhouse Worker (1939)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/1/15/Jack_Delano_-_Chicago_railroad_station.jpg", "https://commons.wikimedia.org/wiki/File:Jack_Delano_-_Chicago_railroad_station.jpg", "Jack Delano — Chicago Union Station (1943)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/0/06/Russell_Lee_-_Pecos_Texas_1939.jpg", "https://commons.wikimedia.org/wiki/File:Russell_Lee_-_Pecos_Texas_1939.jpg", "Russell Lee — Street Stance Texas (1939)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/2/23/Arthur_Rothstein_-_Dust_Storm_Cimarron_County_1936.jpg", "https://commons.wikimedia.org/wiki/File:Arthur_Rothstein_-_Dust_Storm_Cimarron_County_1936.jpg", "Arthur Rothstein — Dust Storm (1936)", "B&W", "20th Century"),
    ("https://upload.wikimedia.org/wikipedia/commons/b/b8/Carl_Mydans_-_Washington_DC_slum_1935.jpg", "https://commons.wikimedia.org/wiki/File:Carl_Mydans_-_Washington_DC_slum_1935.jpg", "Carl Mydans — Washington Street (1935)", "B&W", "20th Century")
]

# Pool 4: Flickr (Max 18)
flickr_candidates = [
    ("https://live.staticflickr.com/65535/51234567890_abcdef1234_b.jpg", "https://www.flickr.com/photos/streetphotography/51234567890/"),
]

# Let's run a test verification of all candidate pools
verified_u = []
for pid in unsplash_candidates:
    cdn = f"https://images.unsplash.com/photo-{pid}?w=800"
    page = f"https://unsplash.com/photos/{pid}"
    if verify(cdn):
        verified_u.append((cdn, page))

verified_p = []
for pxid in pexels_candidates:
    cdn = f"https://images.pexels.com/photos/{pxid}/pexels-photo-{pxid}.jpeg?auto=compress&cs=tinysrgb&w=800"
    page = f"https://www.pexels.com/photo/{pxid}/"
    if verify(cdn):
        verified_p.append((cdn, page))

verified_w = []
for cdn, page, title, col, era in wikimedia_candidates:
    if verify(cdn):
        verified_w.append((cdn, page, title, col, era))

print(f"Verified Unsplash: {len(verified_u)} / {len(unsplash_candidates)}")
print(f"Verified Pexels: {len(verified_p)} / {len(pexels_candidates)}")
print(f"Verified Wikimedia: {len(verified_w)} / {len(wikimedia_candidates)}")
