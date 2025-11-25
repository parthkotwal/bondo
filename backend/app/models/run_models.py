from pydantic import BaseModel
from typing import List, Optional

class RunRequest(BaseModel):
    code: str
    # later we can add: dataset stub, params, etc.

class RunResult(BaseModel):
    stdout: str
    stderr: str
    # later: structured_error, execution_time, etc.