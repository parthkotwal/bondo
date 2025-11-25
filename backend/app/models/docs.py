from pydantic import BaseModel
from typing import List, Optional

class DocSearchRequest(BaseModel):
    query: str
    top_k: int = 5

class DocSnippet(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    text: str
    score: float

class DocSearchResponse(BaseModel):
    query: str
    results: List[DocSnippet]
