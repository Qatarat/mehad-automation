"""
Spec Compiler — converts .md spec files into deterministic JSON spec objects.

Pipeline: login.md → login.spec.json → test_generator.py

Key insight: AI should NEVER interpret raw Markdown. The compiler extracts
selectors, flows, and edge cases into a structured format first. This removes
ambiguity and prevents AI hallucination of selectors/structure.

Usage:
  python ai_engine/spec_compiler.py specs/login.md
  # → produces specs/login.spec.json
"""
from __future__ import annotations
import re, json, sys
from pathlib import Path
from urllib.parse import urlparse


# ── Helpers ───────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return re.sub(r"[^\w]", "_", text.lower().strip()).strip("_")


def _section(md: str, heading: str) -> str:
    """Return aggregated content of all ## sections whose heading starts with 'heading'.
    Handles compound headings like '## UI Elements — Header / Navigation'.
    """
    pat = rf"##\s+{re.escape(heading)}[^\n]*\n(.*?)(?=\n##\s|\Z)"
    matches = re.findall(pat, md, re.DOTALL | re.IGNORECASE)
    return "\n".join(m.strip() for m in matches) if matches else ""


# ── Meta ──────────────────────────────────────────────────────────────────────

def _page_name(md: str) -> str:
    m = re.search(r"^#\s+Page:\s*(.+)", md, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+)", md, re.MULTILINE)
    return m.group(1).strip() if m else "unknown"


def _url(md: str) -> str:
    m = re.search(r"\*\*URL:\*\*\s*`([^`]+)`", md)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?i)URL[:\s]+`?([^\s`]+)`?", md)
    return m.group(1).strip() if m else ""


def _path(md: str) -> str:
    raw = _url(md)
    return urlparse(raw).path if raw else ""


# ── Selector inference ────────────────────────────────────────────────────────

_SELECTOR_RULES = [
    # Auth — OTP / phone-based (checked before email so phone wins for "phone number")
    (r"otp|one.time.code|verification.code",  "input[autocomplete='one-time-code']"),
    (r"send.?code",                           "button:has-text('Send Code')"),
    (r"continue.?btn|verify.?btn",            "button:has-text('Continue')"),
    (r"country.?code|country.?selector",      "[aria-label='Country code']"),
    (r"phone.?number|whatsapp.?number|tel",   "input[type='tel']"),
    (r"login.?btn|log.?in.?btn",              "[aria-label='Login']"),
    (r"modal|dialog",                         "[role='dialog']"),
    # Auth — traditional email/password
    (r"email",     "input[type='email']"),
    (r"password",  "input[type='password']"),
    (r"submit|cta|sign.in.btn",               "button[type='submit']"),
    (r"forgot|reset",                         "a[href*='reset']"),
    (r"sign.?up|register|create.acc",         "a[href*='signup']"),
    # Misc
    (r"checkbox|remember",  "input[type='checkbox']"),
    (r"logo|brand",         "a.logo, a[aria-label*='logo']"),
    (r"error|alert",        "[role='alert'], .error-message, .toast"),
    (r"name",               "input[name='name']"),
    (r"phone",              "input[type='tel']"),
    (r"search",             "input[type='search']"),
]

def _infer_selector(key: str, hint: str) -> str:
    # 1. Direct aria-label extraction (most precise)
    aria_m = re.search(r'aria-label=["\']([^"\']+)["\']', hint, re.IGNORECASE)
    if aria_m:
        return f"[aria-label='{aria_m.group(1)}']"

    # 2. Direct text= extraction → Playwright has-text selector
    text_m = re.search(r'\btext=["\']([^"\']+)["\']', hint)
    if text_m:
        txt = text_m.group(1)
        return f"button:has-text('{txt}')" if len(txt) < 40 else f":has-text('{txt}')"

    # 3. Role-based rules against key + hint
    combined = f"{key} {hint}".lower()
    for pattern, selector in _SELECTOR_RULES:
        if re.search(pattern, combined):
            return selector

    return f"[data-testid='{key}']"


def _ui_elements(section: str) -> dict:
    elements = {}
    for line in section.splitlines():
        if "|" not in line or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        name = parts[0]
        if name.lower() in ("element", "field", "component", "name", "ui element"):
            continue
        key  = _norm(name)
        hint = parts[1] if len(parts) > 1 else ""
        # Use hint's selector hint if present, else infer
        sel_m = re.search(r'type=["\']?(\w+)["\']?', hint.lower())
        if sel_m:
            selector = f"input[type='{sel_m.group(1)}']"
        else:
            selector = _infer_selector(key, hint)
        elements[key] = {"label": name, "hint": hint, "selector": selector}
    return elements


# ── Requirements ──────────────────────────────────────────────────────────────

def _requirements(section: str) -> list[dict]:
    reqs = []
    for line in section.splitlines():
        m = re.match(r"[-*|\s]*(REQ-[A-Z0-9\-]+)\s*[|—:–\-]\s*(.+)", line)
        if m:
            reqs.append({"id": m.group(1).strip(), "text": m.group(2).strip()})
    return reqs


# ── Flow step parser ──────────────────────────────────────────────────────────

def _flow_step(line: str, elements: dict) -> dict | None:
    ll = line.lower().strip()
    if not ll or ll.startswith("#") or ll.startswith("|"):
        return None

    # Navigation
    if re.search(r"navigate|go to|visit|opens?\s+the|page loads|browser navigates", ll):
        return {"action": "goto", "value": "$URL"}

    # Fill — check element keys first
    for key, meta in elements.items():
        words = key.split("_")
        if any(w in ll for w in words):
            if re.search(r"enter|type|fill|input|provide|sets?\s+the", ll):
                return {"action": "fill", "target": key, "selector": meta["selector"]}

    # Generic fill patterns
    if re.search(r"enter.{0,15}email|fill.{0,15}email|type.{0,15}email", ll):
        return {"action": "fill", "target": "email_input", "selector": "input[type='email']"}
    if re.search(r"enter.{0,15}password|fill.{0,15}password", ll):
        return {"action": "fill", "target": "password_input", "selector": "input[type='password']"}

    # Click — check element keys
    for key, meta in elements.items():
        words = key.split("_")
        if any(w in ll for w in words):
            if re.search(r"click|press|submit|tap|select", ll):
                return {"action": "click", "target": key, "selector": meta["selector"]}

    # Generic click patterns
    if re.search(r"click.{0,15}login|click.{0,15}submit|submits?\s+form|clicks?\s+login", ll):
        return {"action": "click", "target": "login_button", "selector": "button[type='submit']"}
    if re.search(r"click.{0,15}sign.?up|click.{0,15}register", ll):
        return {"action": "click", "target": "signup_button", "selector": "button[type='submit']"}

    # Assertions
    if re.search(r"redirect|lands?\s+on|navigate.?to|arrive", ll):
        dest = re.search(r"(?:dashboard|home|profile|reset|signup|login|register|success)", ll)
        return {"action": "assert_url", "value": f"/{dest.group(0)}" if dest else ""}
    if re.search(r"error|toast|message|alert|displays?\s+an?\s+error", ll):
        return {"action": "assert_visible", "target": "error_message",
                "selector": "[role='alert'], .error-message, .toast"}
    if re.search(r"email\s+sent|check.{0,20}inbox", ll):
        return {"action": "assert_text", "value": "email sent"}

    return None


def _flows(section: str, elements: dict) -> list[dict]:
    flows = []
    current: dict | None = None

    for line in section.splitlines():
        s = line.strip()

        # Flow/Scenario header
        is_header = (
            re.match(r"###?\s+", s) or
            re.match(r"(?i)(flow|scenario|test\s+case)\s+\d", s)
        )
        if is_header:
            if current and current.get("steps"):
                flows.append(current)
            name = re.sub(r"^#+\s*", "", s).strip()
            current = {"name": name, "steps": []}
        elif current is not None:
            step = _flow_step(s, elements)
            if step:
                current["steps"].append(step)

    if current and current.get("steps"):
        flows.append(current)
    return flows


# ── Edge cases ────────────────────────────────────────────────────────────────

def _edge_cases(section: str) -> list[dict]:
    cases = []
    for line in section.splitlines():
        if "EC-" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        ec_id = ec_idx = None
        for i, p in enumerate(parts):
            m = re.match(r"(EC-[A-Z0-9\-]+)", p)
            if m:
                ec_id = m.group(1)
                ec_idx = i
                break
        if ec_id is not None and ec_idx is not None:
            scenario = parts[ec_idx + 1] if ec_idx + 1 < len(parts) else ""
            expected = parts[ec_idx + 2] if ec_idx + 2 < len(parts) else ""
            if scenario:
                cases.append({"id": ec_id, "scenario": scenario, "expected": expected})
    return cases


# ── Validation rules ──────────────────────────────────────────────────────────

def _validation(section: str) -> list[str]:
    rules = []
    for line in section.splitlines():
        l = line.strip().lstrip("•*-–|")
        if l and len(l) > 8 and not re.match(r"^#+", l):
            rules.append(l.strip())
    return rules[:15]


# ── API contract ──────────────────────────────────────────────────────────────

def _api(section: str) -> list[dict]:
    endpoints = []
    for line in section.splitlines():
        m = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)", line, re.IGNORECASE)
        if m:
            endpoints.append({"method": m.group(1).upper(), "endpoint": m.group(2)})
    return endpoints


# ── Test data ─────────────────────────────────────────────────────────────────

def _test_data(section: str) -> tuple[list[str], list[str]]:
    valid, invalid = [], []
    in_valid = in_invalid = False
    for line in section.splitlines():
        ll = line.lower().strip()
        if re.match(r"#+.*valid", ll) and "invalid" not in ll:
            in_valid = True; in_invalid = False; continue
        if re.match(r"#+.*invalid", ll):
            in_invalid = True; in_valid = False; continue
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 2 and parts[0].lower() not in ("field", "type", "input"):
                if in_valid:   valid.append(parts[1])
                if in_invalid: invalid.append(parts[1])
    return valid[:10], invalid[:10]


# ── Master compiler ───────────────────────────────────────────────────────────

def compile_spec(md_text: str, source_file: str = "") -> dict:
    ui_raw    = _section(md_text, "UI Elements")
    req_raw   = _section(md_text, "Requirements")
    flow_raw  = _section(md_text, "User Flows")
    ec_raw    = _section(md_text, "Edge Cases")
    val_raw   = _section(md_text, "Validation")
    api_raw   = _section(md_text, "API Contract")
    data_raw  = _section(md_text, "Test Data")
    # Also parse Login Modal and any Modal-specific sections
    modal_raw = _section(md_text, "Login Modal")

    elements = _ui_elements(ui_raw)
    elements.update(_ui_elements(modal_raw))   # merge modal selectors in
    flows    = _flows(flow_raw, elements)
    ecs      = _edge_cases(ec_raw)
    vd, inv  = _test_data(data_raw)

    return {
        "source":       source_file,
        "page":         _page_name(md_text),
        "url":          _url(md_text),
        "path":         _path(md_text),
        "selectors":    elements,
        "requirements": _requirements(req_raw),
        "flows":        flows,
        "edge_cases":   ecs,
        "validation":   _validation(val_raw),
        "api":          _api(api_raw),
        "test_data":    {"valid": vd, "invalid": inv},
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_engine/spec_compiler.py specs/login.md")
        sys.exit(1)
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"File not found: {md_path}")
        sys.exit(1)
    spec = compile_spec(md_path.read_text(encoding="utf-8"), str(md_path))
    out  = md_path.with_suffix(".spec.json")
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Compiled → {out}")
    print(f"   Page: {spec['page']}  |  URL: {spec['url']}")
    print(f"   Selectors: {len(spec['selectors'])}  |  Flows: {len(spec['flows'])}  "
          f"|  Edge cases: {len(spec['edge_cases'])}  |  Requirements: {len(spec['requirements'])}")
