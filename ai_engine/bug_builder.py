"""
Builds structured AI bug tickets from test failure data.
Dedicated module so agent.py stays focused on orchestration.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime

_BUG_COUNTER = [0]

SYS_BUG = """\
You are a senior QA lead. Write a formal bug ticket.
Be precise and actionable. Use ONLY these exact labels:
SEVERITY: [CRITICAL|HIGH|MEDIUM|LOW]
PRIORITY: [P0|P1|P2|P3]
TITLE: one line summary
DESCRIPTION: 2-3 sentences
STEPS:
1. step one
2. step two
3. step three
EXPECTED: what should happen per spec
ACTUAL: what actually happened (from error)
ROOT_CAUSE: 1-2 sentences technical analysis
SUGGESTED_FIX: specific actionable fix for the developer
"""

_ai_call = None  # injected by agent.py


def set_ai_caller(fn):
    global _ai_call
    _ai_call = fn


def _ai(prompt: str) -> str:
    if _ai_call is None:
        return ""
    try:
        return _ai_call(SYS_BUG, prompt, max_tokens=800)
    except Exception:
        return ""


def _grab(text: str, label: str, stops: list[str]) -> str:
    if not text:
        return ""
    stop_pat = "|".join(re.escape(s) for s in stops) if stops else "ZZZZZZ"
    m = re.search(
        rf"(?im)^{label}:\s*(.+?)(?=\n(?:{stop_pat}):|$)",
        text, re.DOTALL | re.MULTILINE,
    )
    return m.group(1).strip() if m else ""


def _parse_ticket(text: str, test_name: str, page_url: str) -> dict:
    _BUG_COUNTER[0] += 1

    sev_raw = _grab(text, "SEVERITY", []).split()
    sev = sev_raw[0].upper() if sev_raw else "MEDIUM"
    if sev not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        sev = "MEDIUM"

    pri_raw = _grab(text, "PRIORITY", ["TITLE"]).split()
    pri = pri_raw[0].upper() if pri_raw else "P2"
    if not re.match(r"P[0-3]$", pri):
        pri = "P2"

    steps_m = re.search(r"(?im)^STEPS:\s*\n((?:[ \t]*\d+\..+\n?)+)", text)
    steps = re.findall(r"\d+\.\s*(.+)", steps_m.group(1)) if steps_m else [
        f"Navigate to {page_url}",
        "Perform the failing action",
        "Observe the result",
    ]

    return {
        "id":            f"BUG-{_BUG_COUNTER[0]:03d}",
        "test_name":     test_name,
        "severity":      sev,
        "priority":      pri,
        "title":         _grab(text, "TITLE", ["DESCRIPTION"]) or test_name.replace("_", " ").title(),
        "description":   _grab(text, "DESCRIPTION", ["STEPS"]),
        "steps":         steps,
        "expected":      _grab(text, "EXPECTED", ["ACTUAL"]),
        "actual":        _grab(text, "ACTUAL", ["ROOT_CAUSE"]),
        "root_cause":    _grab(text, "ROOT_CAUSE", ["SUGGESTED_FIX"]),
        "suggested_fix": _grab(text, "SUGGESTED_FIX", []),
        "page_url":      page_url,
        "browser":       "Chromium",
        "viewport":      "1280×720",
        "env":           "Staging",
    }


def build_from_failure(
    test_name: str,
    error_msg: str,
    traceback: str,
    spec_snippet: str,
    page_url: str,
    node_id: str = "",
    duration: float = 0.0,
    timestamp: str = "",
) -> dict:
    prompt = f"""Write a bug ticket for this test failure.

TEST: {test_name}
URL:  {page_url}
ERROR: {error_msg}
TRACEBACK:
{traceback[-1200:]}
SPEC CONTEXT:
{spec_snippet[:800]}

Use EXACTLY these labels (copy format precisely):
SEVERITY: [CRITICAL|HIGH|MEDIUM|LOW]
PRIORITY: [P0|P1|P2|P3]
TITLE: one line
DESCRIPTION: 2-3 sentences
STEPS:
1.
2.
3.
EXPECTED: per spec
ACTUAL: from error
ROOT_CAUSE: 1-2 sentences
SUGGESTED_FIX: specific fix for developer
"""
    raw    = _ai(prompt)
    ticket = _parse_ticket(raw, test_name, page_url)
    ticket.update({
        "node_id":       node_id,
        "error_message": error_msg,
        "traceback":     traceback,
        "duration":      f"{duration:.2f}s",
        "timestamp":     (timestamp or datetime.now().isoformat())[:19].replace("T", " "),
    })
    return ticket


def build_from_json_report(
    json_report_path: str,
    spec_content: str,
    shot_index: dict,
    evidence_index: dict | None = None,
) -> list[dict]:
    """Parse pytest JSON report → list of bug ticket dicts."""
    if not json_report_path or not Path(json_report_path).exists():
        return []
    try:
        data = json.loads(Path(json_report_path).read_text())
    except Exception:
        return []

    bugs = []
    for test in data.get("tests", []):
        if test.get("outcome") not in ("failed", "error"):
            continue
        node_id   = test.get("nodeid", "")
        test_name = node_id.split("::")[-1]
        call      = test.get("call", {}) or {}
        crash     = call.get("crash", {}) or {}
        error_msg = crash.get("message", "")
        traceback = call.get("longrepr", "")
        duration  = call.get("duration", 0.0)
        shot_info = (shot_index or {}).get(node_id, {})
        page_url  = shot_info.get("url", "") if shot_info else ""
        timestamp = shot_info.get("timestamp", "") if shot_info else ""

        ticket = build_from_failure(
            test_name    = test_name,
            error_msg    = error_msg,
            traceback    = traceback,
            spec_snippet = spec_content[:800],
            page_url     = page_url,
            node_id      = node_id,
            duration     = duration,
            timestamp    = timestamp,
        )
        bugs.append(ticket)
    return bugs
