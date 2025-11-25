import json
import time
from pathlib import Path
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md
from app.ingestion.config import RAW_HTML_DIR, TEXT_DIR, DOC_URLS


def ensure_dirs() -> None:
    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    
def fetch_html(url: str) -> str:
    print(f"Fetching: {url}")
    start_time = time.time()
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    end_time = time.time()
    print(f"Fetched {url} in {end_time - start_time:.2f} seconds")
    return resp.text

def save_raw_html(url: str, html: str) -> Path:
    # Make a filesystem-friendly name from the URL
    safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
    path = RAW_HTML_DIR / f"{safe_name}.html"
    path.write_text(html, encoding="utf-8")
    return path

def load_or_fetch_html(url: str) -> str:
    """
    Simple cache: if we've already downloaded this URL, read from disk.
    """
    safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
    path = RAW_HTML_DIR / f"{safe_name}.html"
    if path.exists():
        print(f"Using cached HTML for: {url}")
        return path.read_text(encoding="utf-8")

    try:
        html = fetch_html(url)
        save_raw_html(url, html)
        return html
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        raise

def clean_html_to_text(html: str) -> str:
    """
    Convert HTML to a roughly readable markdown-style text.
    We also strip some nav/footer sections using simple heuristics.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Optionally remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Convert the main body to markdown-ish text
    # (For scikit-learn docs, the main content is generally in <div role="main">)
    main = soup.find("div", {"role": "main"}) or soup.body
    if main is None:
        main = soup

    md = html_to_md(str(main))
    return md



def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """
    Very simple char-based chunking with overlap.
    Good enough for an MVP; you can later switch to paragraph/heading-aware chunking.
    """
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars to avoid infinite loops")

    print(f"Chunking text of length {len(text)}")
    chunks: List[str] = []
    start = 0
    n = len(text)
    
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, 0)

    print(f"Generated {len(chunks)} chunks")
    return chunks


def build_doc_chunks() -> List[Dict]:
    """
    For each URL:
      - download or load cached HTML
      - clean to text
      - chunk into pieces
    Returns a list of dicts representing doc chunks.
    """
    ensure_dirs()
    all_chunks: List[Dict] = []

    for url in DOC_URLS:
        html = load_or_fetch_html(url)
        text = clean_html_to_text(html)

        file_safe = url.replace("https://", "").replace("http://", "").replace("/", "_")
        base_id = file_safe

        chunks = chunk_text(text)
        print(f"  {url} -> {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            chunk_id = f"{base_id}__{i}"
            all_chunks.append(
                {
                    "id": chunk_id,
                    "url": url,
                    "source": file_safe,
                    "text": chunk,
                }
            )

    return all_chunks


def save_chunks_to_jsonl(chunks: List[Dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")


def main() -> None:
    ensure_dirs()
    chunks = build_doc_chunks()
    out_path = TEXT_DIR / "sklearn_doc_chunks.jsonl"
    save_chunks_to_jsonl(chunks, out_path)
    print(f"Saved {len(chunks)} chunks to {out_path}")


if __name__ == "__main__":
    main()
