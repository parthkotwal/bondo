from pydantic import BaseModel
from typing import List, Optional
from app.models.docs_models import DocSnippet

class MentorHelpRequest(BaseModel):
    code: str
    error: Optional[str] = None
    question: Optional[str] = None

class MentorHelpResponse(BaseModel):
    explanation: str
    suggested_fix: Optional[str] = None
    doc_references: List[DocSnippet]
