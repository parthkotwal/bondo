from fastapi import APIRouter
from app.models.mentor import MentorHelpRequest, MentorHelpResponse
from app.services.mentor import mentor_help

router = APIRouter(prefix="/mentor", tags=["mentor"])

@router.post("/help", response_model=MentorHelpResponse)
def mentor_help_endpoint(req: MentorHelpRequest):
    library_name = "scikit-learn"
    
    return mentor_help(
        code=req.code,
        error=req.error,
        library_name=library_name,
    )