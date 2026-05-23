import os
import numpy as np
from deepface import DeepFace
from pathlib import Path
import pickle

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / 'data' / 'database'
EMBEDDINGS_DIR = BASE_DIR / 'data' / 'embeddings'
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = ['human', 'cartoon', 'anime']

def preprocess_database():
    embeddings = {}
    for category in CATEGORIES:
        category_dir = DATABASE_DIR / category
        if not category_dir.exists():
            continue
            
        enforce_det = (category == 'human')
            
        for image_file in category_dir.glob('*'):
            if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                try:
                    # Extract embedding using ArcFace model
                    result = DeepFace.represent(
                        img_path=str(image_file),
                        model_name='ArcFace',
                        enforce_detection=enforce_det
                    )
                    
                    # Ensure path works for web serving
                    # Keep relative path for frontend like: human/Brad_Pitt.jpg
                    rel_path = f"{category}/{image_file.name}"
                    
                    embeddings[image_file.stem] = {
                        'embedding': np.array(result[0]['embedding']),
                        'name': image_file.stem.replace('_', ' '),
                        'category': category,
                        'file_path': rel_path
                    }
                    print(f"Processed {image_file.name} [{category}]")
                except Exception as e:
                    print(f"Error processing {image_file.name}: {e}")
    
    # Save embeddings
    with open(EMBEDDINGS_DIR / 'embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings, f)
    
    print(f"Saved {len(embeddings)} embeddings to {EMBEDDINGS_DIR / 'embeddings.pkl'}")

if __name__ == '__main__':
    preprocess_database()
    
