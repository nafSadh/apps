import urllib.request
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, timeout=5)
        return res.status == 200
    except Exception as e:
        return False

# Test Wikimedia Commons URLs with proper UA
wiki_urls = [
    ("https://upload.wikimedia.org/wikipedia/commons/5/54/Lange-MigrantMother02.jpg", "https://commons.wikimedia.org/wiki/File:Lange-MigrantMother02.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/3/3b/Walker_Evans_New_Orleans_street_corner.jpg", "https://commons.wikimedia.org/wiki/File:Walker_Evans_New_Orleans_street_corner.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/9/94/Gordon_Parks_-_American_Gothic.jpg", "https://commons.wikimedia.org/wiki/File:Gordon_Parks_-_American_Gothic.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/6/60/Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/c/cb/HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg", "https://commons.wikimedia.org/wiki/File:HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/8/87/Stieglitz_The_Steerage_1907.jpg", "https://commons.wikimedia.org/wiki/File:Stieglitz_The_Steerage_1907.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/7/7b/Jacob_Riis_Bandits%27_Roost_1888.jpg", "https://commons.wikimedia.org/wiki/File:Jacob_Riis_Bandits%27_Roost_1888.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/1/14/Hyde_Park_corner_1937_Weegee.jpg", "https://commons.wikimedia.org/wiki/File:Hyde_Park_corner_1937_Weegee.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/d/d4/Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg", "https://commons.wikimedia.org/wiki/File:Alfred_Stieglitz_-_Winter_-_Fifth_Avenue.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/3/30/Lewis_Hine_Breaker_Boys.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Breaker_Boys.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/a/a2/August_Sander_Boxer.jpg", "https://commons.wikimedia.org/wiki/File:August_Sander_Boxer.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/0/05/Brassa%C3%AF_Paris_by_Night.jpg", "https://commons.wikimedia.org/wiki/File:Brassa%C3%AF_Paris_by_Night.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/2/25/Kertesz_Chez_Mondrian.jpg", "https://commons.wikimedia.org/wiki/File:Kertesz_Chez_Mondrian.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/4/4e/Atget_Eug%C3%A8ne_Paris_street.jpg", "https://commons.wikimedia.org/wiki/File:Atget_Eug%C3%A8ne_Paris_street.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/7/78/Paul_Strand_Blind_Woman.jpg", "https://commons.wikimedia.org/wiki/File:Paul_Strand_Blind_Woman.jpg")
]

valid_wiki = []
for cdn, page in wiki_urls:
    if check_url(cdn):
        valid_wiki.append((cdn, page))
    time.sleep(0.1)

print(f"Verified Wikimedia Commons URLs: {len(valid_wiki)} / {len(wiki_urls)}")
