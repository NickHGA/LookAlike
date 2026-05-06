# Plan d'implémentation - LookAlike

Développement d'une application de reconnaissance faciale pour trouver son "jumeau numérique" parmi une base de données de célébrités et personnages.

## Objectifs clés
- Prototype rapide avec `FastAPI` + `DeepFace`.
- Traitement d'images local et recherche de similarité rapide.
- Interface moderne avec `React` + `Vite`.
- Préparation d'une architecture extensible pour FAISS et des bases plus grandes.

## Phase 1 : Configuration et préparation des données
- [ ] Initialisation de l'environnement virtuel Python.
- [ ] Installation des dépendances (FastAPI, DeepFace, OpenCV, NumPy, python-multipart).
- [ ] Création de la structure de dossiers :
  - `data/database/` pour les images de référence.
  - `data/embeddings/` pour les vecteurs précalculés.
  - `data/temp/` pour les uploads temporaires.
- [ ] Script de prétraitement : générer et stocker les embeddings de la base de données pour des recherches instantanées.
- [ ] Prévoir une routine de mise à jour des embeddings si la base est enrichie.

## Phase 2 : Cœur de l'IA (recherche de similarité)
- [ ] Choix recommandé du modèle : `ArcFace` pour la précision et la robustesse.
- [ ] Implémentation de la détection et de l'alignement des visages (`MTCNN` ou `RetinaFace` si besoin).
- [ ] Extraction des embeddings faciaux.
- [ ] Calcul de similarité avec `cosine similarity` (meilleur pour les embeddings faciaux).
- [ ] Chargement des embeddings en mémoire pour accélérer les recherches.
- [ ] Validation du top 3 et du score de confiance.

## Phase 3 : Backend API (FastAPI)
- [ ] Route `POST /upload` : accepter une image, détecter le visage, retourner le top 3 des sosies.
- [ ] Route `GET /health` pour vérifier que le service est opérationnel.
- [ ] Route `GET /dataset` ou `GET /stats` pour lister le nombre d'images et la disponibilité des embeddings.
- [ ] Gestion du stockage temporaire des images uploadées et nettoyage après traitement.
- [ ] Séparation claire des modules : `backend/preprocess.py`, `backend/matcher.py`, `backend/api.py`.

## Phase 4 : Frontend UI (React)
- [ ] Création de l'application React avec Vite.
- [ ] Interface avec upload Drag & Drop, aperçu de l'image et animations de scan.
- [ ] Affichage du top 3 en grille avec scores, noms et éventuel tag de catégorie.
- [ ] Mode sombre et transitions fluides pour un rendu premium.
- [ ] Intégration avec l'API backend et gestion des erreurs.

## Phase 5 : Polissage et optimisation
- [ ] Optimisation de la vitesse de recherche : utiliser FAISS lorsque la base dépasse quelques centaines d'images.
- [ ] Mise en cache des embeddings et chargement paresseux si nécessaire.
- [ ] Ajout de fonctionnalités fun : "Quel personnage de film êtes-vous ?", filtres de catégories, partages sociaux.
- [ ] Tests de robustesse sur des images variées (luminosité, pose, tailles différentes).

