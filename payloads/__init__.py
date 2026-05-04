"""Security payload loader for authorized testing of your own application."""
from pathlib import Path

_DIR = Path(__file__).parent

def load(name: str) -> list[str]:
    """Load payloads from a txt file. Returns list of non-empty lines."""
    f = _DIR / f"{name}.txt"
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text().splitlines()
            if l.strip() and not l.startswith("#")]

XSS      = load("xss")
SQLI     = load("sqli")
BOUNDARY = load("boundary")

# Top payloads for quick CI runs (subset of each)
XSS_QUICK      = XSS[:5]
SQLI_QUICK     = SQLI[:5]
