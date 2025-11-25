from fastapi import APIRouter
from app.models.docs import DocSearchRequest, DocSearchResponse
from app.services.rag import search_docs

router = APIRouter(prefix="/docs", tags=["docs"])

@router.post("/search", response_model=DocSearchResponse)
def docs_search(req: DocSearchRequest):
    try:
        snippets = search_docs(req.query, top_k=req.top_k)
    except RuntimeError as e:
        # Log and return no results instead of crashing
        print(f"[docs/search] Error: {e}")
        snippets = []
    
    return DocSearchResponse(
        query=req.query, 
        results=snippets
    )
