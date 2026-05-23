import urllib.request
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CARTOON_DIR = BASE_DIR / 'data' / 'database' / 'cartoon'
CARTOON_DIR.mkdir(parents=True, exist_ok=True)

# Wikipedia page titles for Disney princes and princesses
DISNEY_CHARACTERS = [
    "Cinderella_(Disney_character)",
    "Snow_White_(Disney_character)",
    "Ariel_(The_Little_Mermaid)",
    "Belle_(Beauty_and_the_Beast)",
    "Princess_Jasmine",
    "Rapunzel_(Tangled)",
    "Fa_Mulan",
    "Aladdin_(Disney_character)",
    "Elsa_(Frozen)",
    "Moana_(character)",
]

def get_wikipedia_image_url(page_title):
    """Use the Wikipedia API to get the main image URL for a page."""
    api_url = (
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
    )
    req = urllib.request.Request(api_url, headers={'User-Agent': 'LookAlike/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        if 'originalimage' in data:
            return data['originalimage']['source']
        elif 'thumbnail' in data:
            return data['thumbnail']['source']
    return None


def download_images():
    print("Telechargement des Princes et Princesses Disney...")
    success = 0
    for page_title in DISNEY_CHARACTERS:
        # Clean name for filename
        name = page_title.split("(")[0].strip("_").replace("_", " ").strip()
        safe_name = name.replace(" ", "_")
        
        try:
            image_url = get_wikipedia_image_url(page_title)
            if not image_url:
                print(f"  [SKIP] Pas d'image trouvee pour {name}")
                continue
            
            # Determine extension
            ext = ".png" if ".png" in image_url.lower() else ".jpg"
            file_path = CARTOON_DIR / f"{safe_name}{ext}"
            
            req = urllib.request.Request(image_url, headers={'User-Agent': 'LookAlike/1.0'})
            with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
            
            print(f"  [OK] {name} -> {file_path.name}")
            success += 1
        except Exception as e:
            print(f"  [ERREUR] {name} : {e}")

    print(f"\nTermine ! {success}/{len(DISNEY_CHARACTERS)} images telechargees dans {CARTOON_DIR}")


if __name__ == "__main__":
    download_images()
