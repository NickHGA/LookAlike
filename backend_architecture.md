# Architecture Backend de LookAlike

Le backend de LookAlike est conçu pour être rapide, robuste et modulaire. Il repose sur FastAPI pour l'API REST et utilise DeepFace (modèle ArcFace) couplé à FAISS pour la recherche faciale.

## 📂 Structure du projet

```text
backend/
├── main.py                # Point d'entrée de l'API (FastAPI)
├── matcher.py             # Moteur de recherche et d'extraction d'embeddings
├── preprocess.py          # Script pour générer les embeddings depuis la base d'images
├── image_utils.py         # Utilitaires de traitement d'images (filtres cartoon, etc.)
├── download_*.py          # Scripts de scraping pour peupler la base de données
└── requirements.txt       # Dépendances Python (fastapi, deepface, faiss-cpu...)
```

## 🧠 Le Moteur de Recherche (`matcher.py`)

C'est le cœur de l'application. 
1. **Extraction (DeepFace/ArcFace)** : Lorsqu'une image est reçue, le backend utilise ArcFace pour extraire un vecteur mathématique (embedding) de 512 dimensions qui représente de manière unique le visage.
2. **Recherche Vectorielle (FAISS)** : Plutôt que de comparer le vecteur extrait à chaque image de la base une par une (ce qui serait lent sur de grosses bases de données), le système utilise **FAISS (Facebook AI Similarity Search)**. FAISS indexe les vecteurs en mémoire et utilise le produit scalaire (Inner Product) sur des vecteurs normalisés pour calculer la similarité Cosinus de manière quasi instantanée.
3. **Mise en cache** : Au démarrage du serveur, le fichier `embeddings.pkl` est chargé en mémoire et un index FAISS est créé par catégorie (human, cartoon, anime).

## 🚀 Le Serveur API (`main.py`)

Géré par **FastAPI**, il expose les routes principales :
- `GET /health` : Vérification du statut du serveur.
- `POST /upload` : Reçoit l'image de l'utilisateur. 
  - **Validation** : Vérifie le type MIME (`image/*`) et la taille du fichier (limité à 10 MB).
  - **Traitement** : Sauvegarde temporairement l'image, applique éventuellement un filtre "cartoonify" (via OpenCV), puis passe l'image au moteur de recherche.
  - **Nettoyage** : Supprime systématiquement l'image temporaire une fois le traitement terminé (bloc `finally`), pour éviter de saturer le disque.

## ⚙️ Préparation des données (`preprocess.py`)

Ce script est exécuté de manière asynchrone par rapport au serveur (souvent une seule fois). Il scanne le dossier `data/database/`, extrait les visages de toutes les images via ArcFace, et sauvegarde les résultats sous forme de dictionnaire dans `data/embeddings/embeddings.pkl`. Ce fichier est ensuite lu par le backend au démarrage.

## 🛡️ Gestion des erreurs

L'architecture gère proprement les erreurs pour ne jamais crasher silencieusement :
- Si aucun visage n'est détecté, DeepFace lève une exception qui est capturée et renvoyée au client sous forme d'erreur HTTP 400 (`"Aucun visage détecté..."`).
- Les catégories vides ou l'absence de base de données génèrent des erreurs claires signalant à l'administrateur de relancer `preprocess.py`.
- Les fichiers dépassant 10 MB sont rejetés immédiatement (erreur HTTP 413) sans être écrits sur le disque.
