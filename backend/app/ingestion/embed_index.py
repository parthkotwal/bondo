import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from app.ingestion.config import (
    TEXT_DIR,
    VECTORSTORE_DIR,
    EMBED_MODEL_NAME,
    ensure_data_dirs,
)

# Input chunks file from the previous step
CHUNKS_FILE = TEXT_DIR / "sklearn_doc_chunks.jsonl"

# Output paths
EMBEDDINGS_FILE = VECTORSTORE_DIR / "sklearn_doc_embeddings.npy"
METADATA_FILE = VECTORSTORE_DIR / "sklearn_doc_metadata.jsonl"
FAISS_INDEX_FILE = VECTORSTORE_DIR / "sklearn_doc_index.faiss"


def load_chunks(path: Path) -> List[Dict]:
    """
    Load doc chunks from the JSONL file produced by fetch_and_chunk.py.
    Each line is a JSON object with keys like: id, url, source, text.
    """
    chunks: List[Dict] = []
    print(f"Loading chunks from {path} ...")
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
            
    print(f"Loaded {len(chunks)} chunks.")
    return chunks


def compute_embeddings(texts: List[str]) -> np.ndarray:
    """
    Compute embeddings for a list of texts using SentenceTransformer.
    """
    print(f"Loading embedding model: {EMBED_MODEL_NAME}")
    model = SentenceTransformer(EMBED_MODEL_NAME)
    
    print(f"Computing embeddings for {len(texts)} texts...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS index for the given embeddings.
    We use an inner-product index with normalized embeddings (cosine similarity).
    """
    dim = embeddings.shape[1]
    print(f"Building FAISS index (dim={dim})...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"FAISS index contains {index.ntotal} vectors.")
    return index


def save_embeddings(embeddings: np.ndarray, path: Path) -> None:
    print(f"Saving embeddings to {path} ...")
    np.save(path, embeddings)
    
    
def save_metadata(chunks: List[Dict], path: Path) -> None:
    print(f"Saving metadata to {path} ...")
    with path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")


def save_faiss_index(index: faiss.Index, path: Path) -> None:
    print(f"Saving FAISS index to {path} ...")
    faiss.write_index(index, str(path))
    

def main() -> None:
    ensure_data_dirs()
    
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_FILE}. "
            "Run fetch_and_chunk.py first."
        )
        
    # 1. Load chunks
    chunks = load_chunks(CHUNKS_FILE)
    texts = [c["text"] for c in chunks]

    # 2. Compute embeddings
    embeddings = compute_embeddings(texts)

    # 3. Build FAISS index
    index = build_faiss_index(embeddings)

    # 4. Save everything
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    save_embeddings(embeddings, EMBEDDINGS_FILE)
    save_metadata(chunks, METADATA_FILE)
    save_faiss_index(index, FAISS_INDEX_FILE)
    
    print("Done building vector store.")
    print(f"  Embeddings: {EMBEDDINGS_FILE}")
    print(f"  Metadata:   {METADATA_FILE}")
    print(f"  Index:      {FAISS_INDEX_FILE}")


if __name__ == "__main__":
    main()