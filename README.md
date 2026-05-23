# LookAlike

LookAlike (anciennement FaceMatch) est une application propulsée par l'IA qui trouve votre sosie le plus proche parmi une base de données de célébrités, de personnages de dessins animés (cartoon) ou d'animés. 

L'application utilise l'état de l'art en matière de reconnaissance faciale (ArcFace via DeepFace) combiné à une recherche vectorielle ultra-rapide (FAISS) pour analyser vos traits du visage et retourner instantanément vos "jumeaux numériques" avec un score de similarité.

## Fonctionnalités Principales
- **Trois Catégories** : Humains célèbres, personnages Cartoon, et personnages d'Anime.
- **Recherche Instantanée** : Utilisation d'index vectoriels FAISS pour des performances $O(1)$.
- **Upload Optimisé** : Compression intelligente des images côté client (redimensionnement et compression JPEG) pour économiser la bande passante.
- **Sécurisé** : Limite stricte de taille d'upload (10 MB) côté frontend et backend.
- **Interface Premium** : Interface React moderne avec mode sombre, glassmorphism et support du drag & drop.

## Stack Technique
- **Backend** : FastAPI, Python, DeepFace (ArcFace), FAISS, OpenCV.
- **Frontend** : React, Vite, TypeScript.

## Installation & Démarrage

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt

# Générer les embeddings de base (optionnel si déjà fait)
python download_anime.py
python download_disney.py
python download_missing.py
python preprocess.py

# Lancer le serveur
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Ouvrez `http://localhost:5173` dans votre navigateur pour tester l'application !

## Documentation
- Consultez [backend_architecture.md](backend_architecture.md) pour plus de détails sur le fonctionnement interne du backend.
