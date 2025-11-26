from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.ingestion.config import VECTORSTORE_DIR, EMBED_MODEL_NAME
from app.models.docs import DocSnippet
from app.services.api_extraction import extract_api_tokens

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
    

def search_docs(query: str, top_k: int = 5, code: str | None=None) -> List[DocSnippet]:
    """
    Run semantic search over doc chunks and return top-k snippets.
    """
    _ensure_loaded()
    assert _index is not None
    assert _model is not None
    
    if top_k <= 0:
        return []
    
    api_tokens = extract_api_tokens(code) if code else []
    
    query_vec: np.ndarray = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
        
    k = min(max(top_k*3,10), _index.ntotal)
    semantic_scores, semantic_indices = _index.search(query_vec, k)
    
    scored_results = []

    for idx, base_score in zip(semantic_indices[0], semantic_scores[0]):
        if idx < 0 or idx >= len(_metadata):
            continue

        meta = _metadata[idx]
        text = meta.get("text", "")
        url = meta.get("url", "") or ""

        keyword_count = sum(tok.lower() in text.lower() for tok in api_tokens)
        keyword_score = keyword_count * 0.05

        url_boost_count = sum(tok.lower() in url.lower() for tok in api_tokens)
        metadata_boost = url_boost_count * 0.10

        final_score = (base_score * 0.75) + (keyword_score * 0.20) + (metadata_boost * 0.05)
        scored_results.append((final_score, idx))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    final_indices = [i for (_, i) in scored_results[:top_k]]

    results: List[DocSnippet] = []
    for i in final_indices:
        meta = _metadata[i]
        snippet = DocSnippet(
            id=meta.get("id", f"chunk-{i}"),
            title=meta.get("title", "scikit-learn docs"),
            url=meta.get("url"),
            text=meta.get("text", ""),
            score=float(1.0), 
        )
        results.append(snippet)

    return results