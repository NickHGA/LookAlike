import urllib.request
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ANIME_DIR = BASE_DIR / 'data' / 'database' / 'anime'
ANIME_DIR.mkdir(parents=True, exist_ok=True)

# Wikipedia page titles for Anime characters
ANIME_CHARACTERS = [
    "Naruto_Uzumaki",
    "Sasuke_Uchiha",
    "Monkey_D._Luffy",
    "Roronoa_Zoro",
    "Goku",
    "Vegeta",
    "Ichigo_Kurosaki",
    "Edward_Elric",
    "Light_Yagami",
    "L_(Death_Note)",
    "Levi_Ackerman",
    "Eren_Yeager",
    "Mikasa_Ackerman",
    "Saitama_(One-Punch_Man)",
    "Spike_Spiegel",
    "Guts_(Berserk)",
    "Usagi_Tsukino",
    "Gon_Freecss",
    "Killua_Zoldyck",
    "Izuku_Midoriya"
]

def get_wikipedia_image_url(page_title):
    """Use the Wikipedia API to get the main image URL for a page."""
    api_url = (
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
    )
    req = urllib.request.Request(api_url, headers={'User-Agent': 'LookAlike/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'originalimage' in data:
                return data['originalimage']['source']
            elif 'thumbnail' in data:
                return data['thumbnail']['source']
    except Exception:
        pass
    return None


def download_images():
    print("Telechargement des personnages d'Anime...")
    success = 0
    for page_title in ANIME_CHARACTERS:
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
            file_path = ANIME_DIR / f"{safe_name}{ext}"
            
            req = urllib.request.Request(image_url, headers={'User-Agent': 'LookAlike/1.0'})
            with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
            
            print(f"  [OK] {name} -> {file_path.name}")
            success += 1
        except Exception as e:
            print(f"  [ERREUR] {name} : {e}")

    print(f"\nTermine ! {success}/{len(ANIME_CHARACTERS)} images telechargees dans {ANIME_DIR}")


if __name__ == "__main__":
    download_images()
