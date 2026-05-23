import urllib.request
import json
from pathlib import Path

CARTOON_DIR = Path(__file__).resolve().parent.parent / 'data' / 'database' / 'cartoon'

chars = {
    "Belle": "Belle_(Beauty_and_the_Beast)",
    "Mulan": "Mulan_(character)",
}

for name, page in chars.items():
    try:
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'LookAlike/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        image_url = None
        if 'originalimage' in data:
            image_url = data['originalimage']['source']
        elif 'thumbnail' in data:
            image_url = data['thumbnail']['source']
        
        if not image_url:
            print(f"[SKIP] {name}")
            continue
        
        ext = ".png" if ".png" in image_url.lower() else ".jpg"
        file_path = CARTOON_DIR / f"{name}{ext}"
        
        req2 = urllib.request.Request(image_url, headers={'User-Agent': 'LookAlike/1.0'})
        with urllib.request.urlopen(req2) as resp, open(file_path, 'wb') as out:
            out.write(resp.read())
        print(f"[OK] {name}")
    except Exception as e:
        print(f"[ERREUR] {name} : {e}")
