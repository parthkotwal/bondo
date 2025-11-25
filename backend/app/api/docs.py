from fastapi import APIRouter
from app.models.docs import DocSearchRequest, DocSearchResponse, DocSnippet

router = APIRouter(prefix="/docs", tags=["docs"])

@router.post("/search", response_model=DocSearchResponse)
def docs_search(req: DocSearchRequest):
    fake_snippet = DocSnippet(
        id="stub-1",
        title="Stub: scikit-learn docs root",
        url="https://scikit-learn.org/stable/",
        text="Placeholder doc snippet.",
        score=1.0,
    )
    return DocSearchResponse(query=req.query, results=[fake_snippet])
