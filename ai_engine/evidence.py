"""
Evidence loader — reads per-test evidence files for HTML bug report.
Provides: screenshot base64, network log, console errors, performance timing.
"""
from __future__ import annotations
import json, base64
from pathlib import Path

_ROOT           = Path(__file__).parent.parent
EVIDENCE_DIR    = _ROOT / "reports" / "evidence"
SCREENSHOTS_DIR = _ROOT / "reports" / "screenshots"


def load_screenshot_index() -> dict:
    idx = SCREENSHOTS_DIR / "_index.json"
    try:
        return json.loads(idx.read_text()) if idx.exists() else {}
    except Exception:
        return {}


def load_evidence_index() -> dict:
    idx = EVIDENCE_DIR / "_index.json"
    try:
        return json.loads(idx.read_text()) if idx.exists() else {}
    except Exception:
        return {}


def load_evidence_for(node_id: str, evidence_index: dict | None = None) -> dict:
    if evidence_index is None:
        evidence_index = load_evidence_index()
    path = evidence_index.get(node_id)
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def screenshot_to_b64(path: str) -> str | None:
    if not path:
        return None
    candidates = [
        Path(path),                          # stored absolute path
        _ROOT / path,                        # relative to project root
        SCREENSHOTS_DIR / Path(path).name,   # just the filename in screenshots dir
    ]
    for p in candidates:
        try:
            data = base64.b64encode(p.read_bytes()).decode()
            return f"data:image/png;base64,{data}"
        except Exception:
            continue
    return None


def enrich_bug(bug: dict, shot_index: dict, evidence_index: dict | None = None) -> dict:
    """Attach screenshot (base64) + evidence data to a bug dict in-place."""
    node_id   = bug.get("node_id", "")
    shot_info = shot_index.get(node_id, {})
    evidence  = load_evidence_for(node_id, evidence_index or {})

    if shot_info:
        bug["screenshot_b64"]  = screenshot_to_b64(shot_info.get("path", ""))
        bug["screenshot_path"] = shot_info.get("path", "")
        if not bug.get("page_url"):
            bug["page_url"] = shot_info.get("url", "")
        if not bug.get("timestamp"):
            bug["timestamp"] = shot_info.get("timestamp", "")[:19].replace("T", " ")

    if evidence:
        bug["network_log"] = evidence.get("network", [])[-20:]
        bug["console_log"] = evidence.get("console", [])
        bug["error_log"]   = evidence.get("errors", [])
        bug["performance"] = evidence.get("performance", {})

    return bug
