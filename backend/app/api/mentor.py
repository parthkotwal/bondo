from fastapi import APIRouter
from app.models.mentor import MentorHelpRequest, MentorHelpResponse
from app.models.docs import DocSnippet

router = APIRouter(prefix="/mentor", tags=["mentor"])

@router.post("/help", response_model=MentorHelpResponse)
def mentor_help(req: MentorHelpRequest):
    explanation_parts = []

    if req.error:
        explanation_parts.append(f"I see an error: `{req.error}`.")
    if req.question:
        explanation_parts.append(f"You asked: '{req.question}'.")
    explanation_parts.append("In the real system, I will use scikit-learn docs and your code to explain what's happening.")

    explanation = " ".join(explanation_parts)

    fake_doc = DocSnippet(
        id="stub-mentor-1",
        title="Stub: Supervised Learning Intro",
        url="https://scikit-learn.org/stable/supervised_learning.html",
        text="Real RAG snippet goes here.",
        score=0.9,
    )

    return MentorHelpResponse(
        explanation=explanation,
        suggested_fix="# TODO: real suggested fix.",
        doc_references=[fake_doc],
    )
