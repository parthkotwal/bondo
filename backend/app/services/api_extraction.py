import re
from typing import List, Set

API_TOKEN_REGEXES = [
    r"from\s+([\w\.]+)\s+import\s+([\w\*, ]+)",
    r"import\s+([\w\.]+)",
    r"([\w\.]+)\(",
    r"\b([\w\.]+)\b",
]

def extract_api_tokens(code: str) -> List[str]:
    """
    Extract potential API identifiers from user code.
    This is library-agnostic and catches:
      - class names (LinearRegression)
      - function calls (train_test_split)
      - module imports (sklearn.linear_model)
      - attribute access
    
    Returns unique tokens.
    """
    found: Set[str] = set()

    for pattern in API_TOKEN_REGEXES:
        matches = re.findall(pattern, code)
        for m in matches:
            if isinstance(m, tuple):
                for part in m:
                    found.update(_split_tokens(part))
            else:
                found.update(_split_tokens(m))

    # Filter out junk / short tokens
    return [tok for tok in found if len(tok) > 2]


def _split_tokens(text: str) -> List[str]:
    """
    Helper to split tokens by dots, commas, spaces, etc.
    """
    cleaned = re.split(r"[\s,\.\(\)\[\]]+", text)
    return [c.strip() for c in cleaned if c.strip()]

