from fastapi import APIRouter
from app.models.run import RunResult, RunRequest
from app.services.executor import run_user_code, DEFAULT_TIMEOUT_SECONDS

router = APIRouter(prefix="/run", tags=["run"])

@router.post("", response_model=RunResult)
def run_code(req: RunRequest):
    # Stub: will later run sklearn code in sandbox
    timeout = req.timeout_seconds or DEFAULT_TIMEOUT_SECONDS
    
    stdout, stderr = run_user_code(
        code = req.code,
        timeout_seconds = timeout
    )
    
    return RunResult(stdout=stdout, stderr=stderr)