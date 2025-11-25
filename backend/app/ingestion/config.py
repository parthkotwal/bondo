from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_HTML_DIR = DATA_DIR / "raw_html"
TEXT_DIR = DATA_DIR / "text"

VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Add more URLs later
DOC_URLS = [
    "https://scikit-learn.org/stable/user_guide.html",
    "https://scikit-learn.org/stable/api/index.html",
]

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def ensure_data_dirs() -> None:
    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)