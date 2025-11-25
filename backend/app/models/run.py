from pydantic import BaseModel

class RunRequest(BaseModel):
    code: str
    timeout_seconds: int | None = None
    # later we can add: dataset stub, params, etc.

class RunResult(BaseModel):
    stdout: str
    stderr: str
    # later: structured_error, execution_time, etc.