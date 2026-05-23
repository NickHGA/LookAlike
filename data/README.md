# Dataset Preparation

Pour tester l'application, ajoutez des images de célébrités ou personnages dans le dossier `data/database/`.

## Instructions
1. Placez des images JPG/PNG dans `data/database/`.
2. Nommez les fichiers avec le nom de la personne (ex: `emma_watson.jpg`).
3. Lancez le script de prétraitement : `python backend/preprocess.py`.
4. Cela générera les embeddings dans `data/embeddings/embeddings.pkl`.

## Exemple de dataset
- Téléchargez des images publiques de célébrités depuis Unsplash ou autres sources libres.
- Pour un test rapide, ajoutez 5-10 images.

Si vous n'avez pas d'images, l'application retournera une liste vide.