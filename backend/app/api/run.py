from fastapi import APIRouter
from app.models.run_models import RunResult, RunRequest


router = APIRouter(prefix="/run", tags=["run"])

@router.post("", response_model=RunResult)
def run_code(req: RunRequest):
    # Stub: will later run sklearn code in sandbox
    return RunResult(
        stdout=f"[stub] You sent {len(req.code)} characters of code.",
        stderr=""
    )