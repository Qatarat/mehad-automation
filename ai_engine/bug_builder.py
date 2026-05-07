"""
Builds structured AI bug tickets from test failure data.

v2 — major reliability improvements:
  • AI is asked for STRICT JSON output (Ollama format='json' via ai_call).
  • Severity is inferred heuristically from test type (security → CRITICAL,
    accessibility → MEDIUM, smoke → HIGH, etc.) when AI omits it.
  • Schema validation rejects unparseable tickets and triggers an automatic
    retry with the validation error fed back to the model.
  • Fully degrades to a non-AI ticket builder if AI is unavailable, so reports
    never lose a failed test.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime

_BUG_COUNTER = [0]

SYS_BUG = """\
You are a senior QA lead. Convert a test failure into a structured bug ticket.
Output STRICT JSON only — NO markdown fences, NO prose. The JSON object MUST
contain exactly these keys (use empty strings if unknown):

{
  "severity":      "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "priority":      "P0" | "P1" | "P2" | "P3",
  "title":         "<one-line summary, <=80 chars>",
  "description":   "<2-3 sentences explaining the impact>",
  "steps":         ["step 1", "step 2", "step 3"],
  "expected":      "<what the spec says should happen>",
  "actual":        "<what actually happened, taken from the error>",
  "root_cause":    "<1-2 sentence technical analysis>",
  "suggested_fix": "<specific actionable fix the dev can apply>"
}

Severity rubric — choose strictly:
  CRITICAL = security breach, data loss, or auth completely broken
  HIGH     = core flow blocked, payment fails, or 5xx on main page
  MEDIUM   = secondary feature defect, minor data issue, single browser
  LOW      = cosmetic, console warning, accessibility improvement
"""

# Map test-type prefixes → default severity if AI omits the field.
# Used by `_infer_severity_from_test_name`. Order matters — first match wins.
_SEVERITY_BY_PREFIX: list[tuple[str, str, str]] = [
    # (substring in test name, severity, priority)
    # CRITICAL — security & data-integrity
    ("security",        "CRITICAL", "P0"),
    ("xss",             "CRITICAL", "P0"),
    ("sqli",            "CRITICAL", "P0"),
    ("injection",       "CRITICAL", "P0"),
    ("csrf",            "CRITICAL", "P0"),
    ("hallucination",   "HIGH",     "P1"),
    # HIGH — core flows
    ("auth",            "HIGH",     "P1"),
    ("login",           "HIGH",     "P1"),
    ("otp",             "HIGH",     "P1"),
    ("session",         "HIGH",     "P1"),
    ("smoke",           "HIGH",     "P1"),
    ("functional",      "HIGH",     "P1"),
    ("checkout",        "HIGH",     "P1"),
    ("payment",         "HIGH",     "P1"),
    # MEDIUM — secondary defects
    ("performance",     "MEDIUM",   "P2"),
    ("api",             "MEDIUM",   "P2"),
    ("network",         "MEDIUM",   "P2"),
    ("validation",      "MEDIUM",   "P2"),
    ("navigation",      "MEDIUM",   "P2"),
    ("accessibility",   "MEDIUM",   "P2"),
    ("a11y",            "MEDIUM",   "P2"),
    ("error_state",     "MEDIUM",   "P2"),
    ("console",         "MEDIUM",   "P2"),
    # LOW — cosmetic / locale / i18n
    ("seo",             "LOW",      "P3"),
    ("meta",            "LOW",      "P3"),
    ("i18n",            "LOW",      "P3"),
    ("rtl",             "LOW",      "P3"),
    ("arabic",          "LOW",      "P3"),
    ("locale",          "LOW",      "P3"),
    ("visual",          "LOW",      "P3"),
    ("cross_browser",   "LOW",      "P3"),
    ("touch_target",    "LOW",      "P3"),
    ("responsive",      "LOW",      "P3"),
    ("cookie",          "LOW",      "P3"),
    ("storage",         "LOW",      "P3"),
    # Class-name fallbacks (QA-XX prefixes)
    ("qa01",            "HIGH",     "P1"),
    ("qa02",            "MEDIUM",   "P2"),
    ("qa03",            "CRITICAL", "P0"),
    ("qa04",            "MEDIUM",   "P2"),
    ("qa05",            "HIGH",     "P1"),
    ("qa06",            "MEDIUM",   "P2"),
    ("qa07",            "MEDIUM",   "P2"),
    ("qa08",            "LOW",      "P3"),
    ("qa09",            "LOW",      "P3"),
    ("qa10",            "LOW",      "P3"),
]


def _infer_severity_from_test_name(test_name: str) -> tuple[str, str]:
    """Return (severity, priority) inferred from the test-name prefix."""
    nm = test_name.lower()
    for sub, sev, pri in _SEVERITY_BY_PREFIX:
        if sub in nm:
            return sev, pri
    return "MEDIUM", "P2"


_ai_call = None  # injected by agent.py


def set_ai_caller(fn):
    global _ai_call
    _ai_call = fn


# ─────────────────────────────────────────────────────────────────────────────
# JSON parsing & validation
# ─────────────────────────────────────────────────────────────────────────────

_REQUIRED_KEYS = {
    "severity", "priority", "title", "description", "steps",
    "expected", "actual", "root_cause", "suggested_fix",
}


def _validate_ticket_json(raw: str) -> tuple[bool, str]:
    """Validator passed to ai_call's feedback loop. Returns (ok, error_msg)."""
    text = (raw or "").strip()
    if not text:
        return False, "empty response"
    # Tolerate ```json fences if the model adds them anyway
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"not valid JSON: {e.msg} at line {e.lineno}"
    if not isinstance(obj, dict):
        return False, "JSON root must be an object"
    missing = _REQUIRED_KEYS - obj.keys()
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    if obj["severity"] not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        return False, f"severity must be CRITICAL/HIGH/MEDIUM/LOW, got {obj['severity']!r}"
    if not re.match(r"P[0-3]$", obj["priority"]):
        return False, f"priority must match P[0-3], got {obj['priority']!r}"
    if not isinstance(obj["steps"], list):
        return False, "steps must be a list of strings"
    return True, ""


def _parse_json_ticket(raw: str) -> dict | None:
    """Parse raw AI output into a ticket dict, or return None on failure."""
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    try:
        obj = json.loads(text)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    return obj


def _ai(prompt: str) -> str:
    """Call the wired AI with json_mode + ticket-schema validator."""
    if _ai_call is None:
        return ""
    try:
        # Best path: ai_call supports json_mode + validator (new agent.py).
        return _ai_call(SYS_BUG, prompt,
                        max_tokens=900,
                        json_mode=True,
                        validator=_validate_ticket_json)
    except TypeError:
        # Older signature: positional + max_tokens only. Fall back.
        try:
            return _ai_call(SYS_BUG, prompt, max_tokens=900)
        except Exception:
            return ""
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def _build_minimal_ticket(test_name: str, error_msg: str,
                          traceback: str, page_url: str) -> dict:
    """Deterministic ticket builder used when AI is unavailable. Always succeeds."""
    sev, pri = _infer_severity_from_test_name(test_name)

    # Try to pull the most useful single line from the traceback.
    err_line = ""
    for line in (traceback or "").splitlines()[-15:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("E ") or "Error" in s or "Exception" in s or "assert" in s:
            err_line = s.lstrip("E ").strip()
            break
    if not err_line:
        err_line = (error_msg or "test failed").splitlines()[0][:200]

    # Build minimal ticket from VERIFIABLE inputs only — no fabricated
    # text. Empty fields are EMPTY (not "no AI suggestion" placeholders);
    # the report renderer skips empty sections cleanly.
    return {
        "severity":      sev,
        "priority":      pri,
        "title":         f"{test_name.replace('_', ' ').title()} — {err_line[:60]}",
        "description":   f"Automated test {test_name!r} failed at {page_url or 'the target URL'}. "
                         f"Error: {err_line[:280]}",
        "steps": [
            f"Navigate to {page_url or 'the page under test'}",
            f"Run the test {test_name}",
            "Observe the failing assertion (see traceback below)",
        ],
        "expected":      "Test passes per the spec — no assertion failures.",
        "actual":        err_line[:300],
        # NO placeholder text — empty means "we don't have this info".
        # The reporter hides empty sections so users don't see fake text.
        "root_cause":    "",
        "suggested_fix": "",
    }


def _normalize_ticket(ticket: dict, fallback: dict) -> dict:
    """Coerce/clip AI ticket fields to expected types. fallback supplies defaults."""
    out = dict(fallback)
    for k in _REQUIRED_KEYS:
        v = ticket.get(k, fallback[k])
        if k == "steps":
            if isinstance(v, str):
                v = [s.strip() for s in re.split(r"\n|;|(?<=\.)\s", v) if s.strip()]
            elif not isinstance(v, list):
                v = fallback[k]
        elif not isinstance(v, str):
            v = str(v)
        out[k] = v

    # Re-validate enum fields after the AI's value is mixed in
    if out["severity"] not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        out["severity"] = fallback["severity"]
    if not re.match(r"P[0-3]$", out["priority"]):
        out["priority"] = fallback["priority"]
    return out


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
    """Generate one structured bug ticket from a single test failure."""
    _BUG_COUNTER[0] += 1
    bug_id = f"BUG-{_BUG_COUNTER[0]:03d}"

    minimal = _build_minimal_ticket(test_name, error_msg, traceback, page_url)

    prompt = f"""Generate a STRICT JSON bug ticket for this test failure.

TEST_NAME: {test_name}
PAGE_URL:  {page_url or '(not captured)'}
ERROR:     {(error_msg or '')[:300]}
TRACEBACK_TAIL:
{(traceback or '')[-1500:]}

SPEC_CONTEXT:
{(spec_snippet or '')[:800]}

Return only the JSON object — no prose, no markdown fences."""

    raw = _ai(prompt)
    ai_ticket = _parse_json_ticket(raw)

    if ai_ticket is not None:
        ticket_data = _normalize_ticket(ai_ticket, minimal)
    else:
        ticket_data = minimal  # AI failed completely → use deterministic ticket

    # Final assembled ticket includes test-run metadata
    return {
        "id":            bug_id,
        "test_name":     test_name,
        "severity":      ticket_data["severity"],
        "priority":      ticket_data["priority"],
        "title":         ticket_data["title"][:140],
        "description":   ticket_data["description"],
        "steps":         ticket_data["steps"][:8],
        "expected":      ticket_data["expected"],
        "actual":        ticket_data["actual"],
        "root_cause":    ticket_data["root_cause"],
        "suggested_fix": ticket_data["suggested_fix"],
        "page_url":      page_url,
        "browser":       "Chromium",
        "viewport":      "1280×720",
        "env":           "Staging",
        "node_id":       node_id,
        "error_message": error_msg,
        "traceback":     traceback,
        "duration":      f"{duration:.2f}s",
        "timestamp":     (timestamp or datetime.now().isoformat())[:19].replace("T", " "),
    }


def build_from_json_report(
    json_report_path: str,
    spec_content: str,
    shot_index: dict,
    evidence_index: dict | None = None,
) -> list[dict]:
    """Parse pytest JSON report → list of bug-ticket dicts."""
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

        bugs.append(build_from_failure(
            test_name    = test_name,
            error_msg    = error_msg,
            traceback    = traceback,
            spec_snippet = spec_content[:800],
            page_url     = page_url,
            node_id      = node_id,
            duration     = duration,
            timestamp    = timestamp,
        ))
    return bugs
