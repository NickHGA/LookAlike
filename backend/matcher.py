import numpy as np
from deepface import DeepFace
from pathlib import Path
import pickle
from typing import List, Dict

try:
    import faiss
except ImportError:
    faiss = None

BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_FILE = BASE_DIR / 'data' / 'embeddings' / 'embeddings.pkl'

# ── Load embeddings + build FAISS indexes at startup ─────────────────────────
embeddings = {}
# Per-category FAISS index and ordered key list
_faiss_indexes: Dict[str, object] = {}
_faiss_keys: Dict[str, List[str]] = {}

try:
    with open(EMBEDDINGS_FILE, 'rb') as f:
        embeddings = pickle.load(f)
    print(f"Loaded {len(embeddings)} embeddings from database.")
except FileNotFoundError:
    print("Embeddings file not found. Run preprocess.py first.")

def _build_faiss_indexes():
    """Build one FAISS index per category for fast similarity search."""
    if faiss is None or not embeddings:
        return

    # Group embeddings by category
    by_category: Dict[str, List] = {}
    for key, data in embeddings.items():
        cat = data['category']
        by_category.setdefault(cat, []).append((key, data['embedding']))

    for cat, items in by_category.items():
        keys = [k for k, _ in items]
        vectors = np.array([emb for _, emb in items], dtype=np.float32)
        # Normalize for cosine similarity via inner product
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        _faiss_indexes[cat] = index
        _faiss_keys[cat] = keys
        print(f"  FAISS index built for '{cat}': {len(keys)} vectors, dim={dim}")

_build_faiss_indexes()

if _faiss_indexes:
    print("FAISS search enabled — near-instant queries.")
else:
    if faiss is None:
        print("FAISS not installed — falling back to brute-force search.")
    else:
        print("No embeddings to index — FAISS indexes empty.")


def _search_faiss(query_embedding: np.ndarray, mode: str, top_k: int) -> List[Dict[str, object]]:
    """Search using FAISS index (O(1)-ish)."""
    index = _faiss_indexes[mode]
    keys = _faiss_keys[mode]

    query = query_embedding.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(query)
    scores, indices = index.search(query, min(top_k, len(keys)))

    matches = []
    for i in range(indices.shape[1]):
        idx = indices[0][i]
        if idx == -1:
            continue
        key = keys[idx]
        data = embeddings[key]
        matches.append({
            "name": data['name'],
            "score": float(scores[0][i]),
            "image_url": f"/static/{data['file_path']}",
            "category": data['category']
        })
    return matches


def _search_brute(query_embedding: np.ndarray, mode: str, top_k: int) -> List[Dict[str, object]]:
    """Fallback brute-force search when FAISS is unavailable."""
    query = query_embedding.reshape(1, -1)
    q_norm = query / (np.linalg.norm(query) + 1e-10)

    similarities = {}
    for name, data in embeddings.items():
        if data['category'] != mode:
            continue
        db_vec = data['embedding'].reshape(1, -1)
        db_norm = db_vec / (np.linalg.norm(db_vec) + 1e-10)
        sim = float(np.dot(q_norm, db_norm.T)[0][0])
        similarities[name] = sim

    sorted_matches = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

    matches = []
    for name, score in sorted_matches:
        data = embeddings[name]
        matches.append({
            "name": data['name'],
            "score": score,
            "image_url": f"/static/{data['file_path']}",
            "category": data['category']
        })
    return matches


def find_matches(image_path: str, mode: str, top_k: int = 3) -> List[Dict[str, object]]:
    if not embeddings:
        raise ValueError("La base de données d'embeddings est vide. Exécutez preprocess.py d'abord.")

    # Check if we have any embeddings for this mode
    mode_count = sum(1 for data in embeddings.values() if data['category'] == mode)
    if mode_count == 0:
        raise ValueError(f"Aucune image trouvée dans la catégorie '{mode}'. Ajoutez des images et relancez preprocess.py.")

    enforce_det = (mode == 'human')

    try:
        result = DeepFace.represent(
            img_path=image_path,
            model_name='ArcFace',
            enforce_detection=enforce_det
        )
        query_embedding = np.array(result[0]['embedding'])
    except ValueError as e:
        raise ValueError("Aucun visage détecté dans l'image. Essayez avec une photo plus nette où le visage est bien visible.") from e
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'analyse de l'image : {e}") from e

    # Use FAISS if available for this category, otherwise brute-force
    if mode in _faiss_indexes:
        return _search_faiss(query_embedding, mode, top_k)
    else:
        return _search_brute(query_embedding, mode, top_k)
