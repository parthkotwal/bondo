import os
import sys
import tempfile
import subprocess
from typing import Tuple

DEFAULT_TIMEOUT_SECONDS = 5
MAX_OUTPUT_CHARS = 8000

def run_user_code(code: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Tuple[str, str]:
    """
    Run user-provided Python code in a temporary directory using a subprocess.

    This is a minimal, "safe-ish" sandbox:
      - Executes in an isolated temp directory
      - Enforces a wall-clock timeout
      - Captures stdout/stderr
      - Truncates very long outputs

    NOTE: This is NOT secure enough for arbitrary untrusted users on the open internet.
    """
    
    safe_stdout = ""
    safe_stderr = ""
    
    # Create a temp dir so the user can't touch project files
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "main.py")
        
        # Write user's code to the file
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            # Run the script
            proc = subprocess.run(
                [sys.executable, script_path],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            safe_stdout = _truncate_output(proc.stdout)
            safe_stderr = _truncate_output(proc.stderr)
        
        except subprocess.TimeoutExpired:
            safe_stdout = ""
            safe_stderr = (
               f"Execution timed out after {timeout_seconds} seconds. "
                "Try simplifying your code or using smaller data." 
            )
            
        except Exception as e:
            safe_stdout = ""
            safe_stderr = f"Internal execution error: {e!r}"
    
    return safe_stdout, safe_stderr

def _truncate_output(s: str) -> str:
    if not s:
        return ""
    if len(s) <= MAX_OUTPUT_CHARS:
        return s
    return s[:MAX_OUTPUT_CHARS] + "\n...[truncated]..."