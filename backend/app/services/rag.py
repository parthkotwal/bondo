from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.ingestion.config import VECTORSTORE_DIR, EMBED_MODEL_NAME
from app.models.docs import DocSnippet

METADATA_FILE = VECTORSTORE_DIR / "sklearn_doc_metadata.jsonl"
FAISS_INDEX_FILE = VECTORSTORE_DIR / "sklearn_doc_index.faiss"

_index: Optional[faiss.Index] = None
_metadata: List[Dict] = []
_model: Optional[SentenceTransformer] = None

def _load_metadata(path: Path) -> List[Dict]:
    chunks: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks

def _ensure_loaded() -> None:
    """
    Lazily load FAISS index, metadata, and embedding model into memory.
    Called automatically before search.
    """
    global _index, _metadata, _model

    if _index is not None and _metadata and _model is not None:
        return

    if not METADATA_FILE.exists():
        raise RuntimeError(f"Metadata file not found: {METADATA_FILE}")
    if not FAISS_INDEX_FILE.exists():
        raise RuntimeError(f"FAISS index file not found: {FAISS_INDEX_FILE}")

    # Load metadata
    print(f"[RAG] Loading metadata from {METADATA_FILE}")
    _metadata = _load_metadata(METADATA_FILE)
    print(f"[RAG] Loaded {len(_metadata)} metadata entries.")

    # Load FAISS index
    print(f"[RAG] Loading FAISS index from {FAISS_INDEX_FILE}")
    _index = faiss.read_index(str(FAISS_INDEX_FILE))
    print(f"[RAG] FAISS index ntotal = {_index.ntotal}")

    if len(_metadata) != _index.ntotal:
        # Not fatal, but good to know
        print(
            f"[RAG] WARNING: metadata count ({len(_metadata)}) "
            f"!= index.ntotal ({_index.ntotal})"
        )

    # Load embedding model
    print(f"[RAG] Loading embedding model: {EMBED_MODEL_NAME}")
    _model = SentenceTransformer(EMBED_MODEL_NAME)
    

def search_docs(query: str, top_k: int = 5) -> List[DocSnippet]:
    """
    Run semantic search over scikit-learn doc chunks and return top-k snippets.
    """
    _ensure_loaded()
    assert _index is not None
    assert _model is not None
    
    if top_k <= 0:
        return []
    
    query_vec: np.ndarray = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
        
    k = min(top_k, _index.ntotal)
    scores, indices = _index.search(query_vec, k)
    
    results: List[DocSnippet] = []
    for idx, score in zip(indices[0], scores[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        meta = _metadata[idx]

        # Build a usable title: use 'source' or URL or a fallback
        title = meta.get("source") or meta.get("url") or "scikit-learn docs"

        snippet = DocSnippet(
            id=meta.get("id", f"chunk-{idx}"),
            title=title,
            url=meta.get("url"),
            text=meta.get("text", ""),
            score=float(score),
        )
        results.append(snippet)
        
    return results