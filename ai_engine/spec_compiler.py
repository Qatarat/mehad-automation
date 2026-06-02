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


def _prose_requirements(md_text: str) -> list[dict]:
    """Extract implicit requirements from prose bullet points when no REQ-XX format exists."""
    reqs: list[dict] = []
    seen: set[str] = set()
    # Strong requirement phrases
    patterns = [
        r"[-*]\s+((?:Must|Should|Ensure|Verify|Confirm|Validate|Check|System must|System should)[^\n]{10,100})",
        r"[-*]\s+((?:Maximum|Minimum|At least|No more than|Up to|Required|Only|Cannot)[^\n]{10,100})",
    ]
    # Also look for "### Validation" and similar sub-headers that imply requirements
    val_bullets = []
    for pat in patterns:
        val_bullets.extend(re.findall(pat, md_text, re.IGNORECASE | re.MULTILINE))
    for i, txt in enumerate(val_bullets[:15], 1):
        t = txt.strip()
        if t in seen or len(t) < 10:
            continue
        seen.add(t)
        reqs.append({"id": f"REQ-{i:02d}", "text": t})
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


def _prose_test_data(md_text: str) -> tuple[list[str], list[str]]:
    """Generate sensible test data from prose validation mentions."""
    valid: list[str] = []
    invalid: list[str] = []

    # Extract max-length values and generate boundary test data
    for m in re.finditer(r"maximum\s+(?:of\s+)?(\d+)\s+characters?", md_text, re.IGNORECASE):
        n = int(m.group(1))
        valid.append("A" * min(n, 30))           # valid: within limit
        invalid.append("A" * (n + 5))             # invalid: exceeds limit

    # Explicit **Credentials:** line — highest priority, extract real test values
    cred_m = re.search(r"\*\*Credentials?:\*\*\s*([^\n]+)", md_text, re.IGNORECASE)
    if cred_m:
        cred_raw = cred_m.group(1).strip()
        phone_m = re.search(r"\b(\d{7,12})\b", cred_raw)
        otp_m   = re.search(r"OTP\s+(\d{4,8})", cred_raw, re.IGNORECASE)
        if phone_m:
            valid.append(f"phone: {phone_m.group(1)}")
        if otp_m:
            valid.append(f"otp: {otp_m.group(1)}")

    # Inline message strings in BDD scenarios  e.g. "Hello teacher, I just booked..."
    msg_m = re.search(r'"(Hello[^"]{10,80})"', md_text)
    if msg_m:
        valid.append(f"message: {msg_m.group(1)[:60]}")

    # Page URL as a navigation test value for static / public pages
    if not valid:
        # Try **URL:** inline format first, then ## URL \n `path` block format
        url_m = re.search(r"\*\*URL[s]?:\*\*\s*`?(/[^\s`\)\n]{3,80})`?", md_text)
        if not url_m:
            url_m = re.search(r"##\s+URLs?\s*\n\s*`(/[^\s`\)]+)`", md_text)
        if url_m:
            valid.append(f"url: {url_m.group(1).split()[0]}")

    # Email fields
    if re.search(r"\bemail\b", md_text, re.IGNORECASE):
        valid.append("test@mehadedu.com")
        invalid.append("notanemail")

    # Phone fields
    if re.search(r"\bphone|whatsapp|mobile\b", md_text, re.IGNORECASE):
        valid.append("98976564")
        invalid.append("abc")

    # OTP fields
    if re.search(r"\botp|verification.?code\b", md_text, re.IGNORECASE):
        valid.append("123456")
        invalid.append("000000")

    return valid[:8], invalid[:8]


# ── Prose-format fallbacks (Mehad-style specs) ───────────────────────────────

def _prose_selectors(md_text: str) -> dict:
    """Infer selectors from prose field mentions when no UI Elements table exists."""
    elements: dict = {}
    # Patterns: "Enter your <field>", "<field>: enter/input...", "click <button>"
    field_patterns = [
        (r"(?:enter|type|fill|input)\s+(?:your\s+)?([a-zA-Z ]{3,30})(?:\s+field|\s+\(|:|\.|$)", "input"),
        (r"([a-zA-Z ]{3,25})\s+field\s*(?:\(|:|-|—)", "input"),
        (r"([a-zA-Z ]{3,25})\s+(?:input|textbox|text field)\s*(?:\(|:|$)", "input"),
        (r"click\s+(?:the\s+)?(?:on\s+)?[\"']?([a-zA-Z ]{3,30})[\"']?\s+button", "button"),
        (r"[\"']([a-zA-Z ]{3,30})[\"']\s+button", "button"),
        (r"click\s+(?:the\s+)?(?:on\s+)?[\"']?([a-zA-Z ]{3,30})[\"']\s+link", "link"),
    ]
    skip_words = {"your", "the", "a", "an", "this", "that", "any", "all", "no", "on",
                  "of", "in", "to", "by", "or", "and", "next", "back"}
    seen: set[str] = set()
    for pattern, kind in field_patterns:
        for m in re.finditer(pattern, md_text, re.IGNORECASE | re.MULTILINE):
            name = m.group(1).strip().lower()
            name = re.sub(r"\s+", " ", name)
            if name in skip_words or len(name) < 3 or name in seen:
                continue
            seen.add(name)
            key = _norm(name)
            if kind == "button":
                selector = f"button:has-text('{name.title()}')"
            elif kind == "link":
                selector = f"a:has-text('{name.title()}')"
            else:
                selector = _infer_selector(key, name)
            elements[key] = {"label": name.title(), "hint": name, "selector": selector}
            if len(elements) >= 20:
                break
        if len(elements) >= 20:
            break
    return elements


def _prose_url(md_text: str) -> str:
    """Extract URL from prose when no **URL:** field exists."""
    m = re.search(r"\*\*URL:\*\*\s*`?([^\s`\)]+)`?", md_text)
    if m:
        return m.group(1).strip()
    for line in md_text.splitlines()[:40]:
        m = re.search(r"https?://[^\s\]\)`),;]+", line)
        if m:
            return m.group(0).rstrip(".,;)")
    return ""


def _prose_flows(md_text: str, elements: dict) -> list[dict]:
    """Extract flows from ## Steps... sections in Mehad prose format."""
    flows: list[dict] = []
    # Match any second-level heading that looks like a step sequence
    pattern = re.compile(
        r"##\s+((?:Steps?[^\n]*|.*?Process[^\n]*|.*?Flow[^\n]*|.*?Booking[^\n]*))\n(.*?)(?=\n##\s|\Z)",
        re.DOTALL | re.IGNORECASE
    )
    for m in pattern.finditer(md_text):
        title = m.group(1).strip()[:60]
        block = m.group(2)
        # Prefer ### N. sub-headers, fall back to numbered list items
        sub = re.findall(r"###\s+\d+\.\s+(.+)", block)
        numbered = re.findall(r"^\d+\.\s+(.+)", block, re.MULTILINE)
        steps = (sub or numbered)[:10]
        if steps:
            compiled_steps = []
            for s in steps:
                step_dict = _flow_step(s, elements)
                compiled_steps.append(step_dict or s)
            flows.append({"name": title, "steps": compiled_steps})
    return flows


def _bdd_selectors(md_text: str) -> dict:
    """Extract selectors from BDD spec files.

    Handles three selector formats:
    1. 'Real Selectors Observed' markdown tables:
       | Search tutors input | `textbox[name="Search tutors..."]` |
    2. '**Selectors:**' bullet lists inside individual scenarios:
       - heading: `h1:has-text("Contact Us")`
    3. Inline key:value selector lines inside scenario blocks.
    """
    elements: dict = {}
    seen: set[str] = set()

    def _add(label: str, hint: str) -> None:
        hint = hint.strip("`").strip()
        if not hint or not label or len(label) < 2:
            return
        key = _norm(label)
        if key in seen or key.lower() in ("element", "selector", "field", "component", "url"):
            return
        seen.add(key)
        elements[key] = {"label": label, "hint": hint, "selector": hint}

    # Format 1: ## Real Selectors Observed table
    sel_section = re.search(
        r"##\s+Real\s+Selectors[^\n]*\n(.*?)(?=\n##\s|\Z)",
        md_text, re.DOTALL | re.IGNORECASE
    )
    if sel_section:
        for line in sel_section.group(1).splitlines():
            if "|" not in line or "---" in line:
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                _add(parts[0], parts[1])

    # Format 2: **Selectors:** bullet lists inside scenario blocks
    # Pattern: "- label: `selector`" or "- label: selector"
    for m in re.finditer(
        r"[-*]\s+([^:\n`]{2,40}):\s+`([^`]+)`",
        md_text
    ):
        _add(m.group(1).strip(), m.group(2).strip())

    # Format 3: bare "key: selector" lines without backticks (e.g. "- url: /en/...")
    for m in re.finditer(
        r"[-*]\s+([^:\n]{2,30}):\s+((?:button|input|a\[|h\d|p:|text=|`|\[role)[^\n]{3,80})",
        md_text
    ):
        _add(m.group(1).strip(), m.group(2).strip())

    return dict(list(elements.items())[:40])


def _bdd_flows(md_text: str, elements: dict) -> list[dict]:
    """Extract flows from BDD scenario blocks. Supports two scenario formats:

    Format A (#### Scenario N: title) — BDD steps inside ``` code fences:
        ```
        Given the student is on /en/find-tutors
        When the student clicks ...
        Then ...
        ```

    Format B (### XX-NN: title) — BDD steps as bold markdown lines:
        **Given** a user navigates to ...
        **When** the page finishes loading
        **Then** the heading is visible
    """
    flows: list[dict] = []

    # Combined scenario header pattern: matches both #### Scenario N: and ### XX-NN:
    scenario_iter = re.finditer(
        r"#{2,4}\s+(?:Scenario\s+\d+[:\s]+|[A-Z]{2,6}-\d+[:\s]+)([^\n]+)\n(.*?)"
        r"(?=\n#{2,4}\s+(?:Scenario\s+\d+|[A-Z]{2,6}-\d+)|\n##\s|\Z)",
        md_text, re.DOTALL | re.IGNORECASE
    )

    for m in scenario_iter:
        title = m.group(1).strip()[:60]
        block = m.group(2)
        raw_steps: list[str] = []

        for line in block.splitlines():
            stripped = line.strip()
            # Skip bare code fence markers
            if stripped in ("```", "```bdd", "```gherkin"):
                continue

            # Format A: plain "Given/When/Then/And ..." lines (inside code fences)
            bdd_plain = re.match(r"^(Given|When|Then|And)\s+(.+)", stripped, re.IGNORECASE)
            if bdd_plain:
                raw_steps.append(stripped)
                continue

            # Format B: "**Given** ...", "**When** ...", "**Then** ..." bold lines
            bdd_bold = re.match(r"^\*\*(Given|When|Then|And)\*\*\s+(.+)", stripped, re.IGNORECASE)
            if bdd_bold:
                raw_steps.append(f"{bdd_bold.group(1)} {bdd_bold.group(2)}")

        compiled_steps: list = []
        for step_text in raw_steps[:10]:
            sd = _flow_step(step_text, elements)
            compiled_steps.append(sd or step_text)

        if compiled_steps:
            flows.append({"name": title, "steps": compiled_steps})

    return flows


def _bdd_requirements(md_text: str) -> list[dict]:
    """Extract requirements from BDD 'Then'/'And' lines in both formats:

    Format A (plain): Then the heading "X" is visible
    Format B (bold):  **Then** the heading "X" is visible
    """
    reqs: list[dict] = []
    seen: set[str] = set()
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped in ("```", "```bdd", "```gherkin"):
            continue

        txt = None
        # Format A: plain Then/And
        m_a = re.match(r"^(?:Then|And)\s+(.+)", stripped, re.IGNORECASE)
        if m_a:
            txt = m_a.group(1).strip()
        else:
            # Format B: **Then** or **And** bold
            m_b = re.match(r"^\*\*(?:Then|And)\*\*\s+(.+)", stripped, re.IGNORECASE)
            if m_b:
                txt = m_b.group(1).strip()

        if not txt:
            continue
        if txt.startswith("#") or "<" in txt or len(txt) < 10:
            continue
        if txt in seen:
            continue
        seen.add(txt)
        reqs.append({"id": f"REQ-{len(reqs)+1:02d}", "text": txt})
        if len(reqs) >= 20:
            break
    return reqs


def _bdd_edge_cases(md_text: str) -> list[dict]:
    """Extract edge cases from Empty/Error States section in BDD specs."""
    cases: list[dict] = []
    ec_section = re.search(
        r"##\s+(?:Empty|Error|Edge)[^\n]*\n(.*?)(?=\n##\s|\Z)",
        md_text, re.DOTALL | re.IGNORECASE
    )
    if not ec_section:
        return cases
    block = ec_section.group(1)
    seen: set[str] = set()
    for line in block.splitlines():
        stripped = line.strip().lstrip("-*• ")
        if not stripped or len(stripped) < 10 or stripped in seen:
            continue
        seen.add(stripped)
        cases.append({
            "id": f"EC-{len(cases)+1:02d}",
            "scenario": stripped,
            "expected": "System shows appropriate empty/error state",
        })
        if len(cases) >= 10:
            break
    return cases


def _prose_edge_cases(md_text: str) -> list[dict]:
    """Extract edge cases from validation/bullet sections in prose format."""
    cases: list[dict] = []
    # Look for validation sections
    val_pattern = re.compile(
        r"(?:###?\s+)?(?:Validation|Input\s+Field\s+Validation|Edge\s+Cases?)[^\n]*\n(.*?)(?=\n###?\s|\n##\s|\Z)",
        re.DOTALL | re.IGNORECASE
    )
    seen: set[str] = set()
    for m in val_pattern.finditer(md_text):
        block = m.group(1)
        bullets = re.findall(r"[-*]\s+(.+)", block)
        for i, b in enumerate(bullets[:12], len(cases) + 1):
            txt = b.strip()
            if txt in seen or len(txt) < 10:
                continue
            seen.add(txt)
            cases.append({
                "id": f"EC-{i:02d}",
                "scenario": txt,
                "expected": "System shows appropriate error or prevents the action",
            })
    return cases[:15]


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

    # Mehad-style prose fallbacks when structured sections are absent
    if not elements:
        elements = _prose_selectors(md_text)
    # BDD-format: "Real Selectors Observed" table (highest fidelity)
    bdd_sels = _bdd_selectors(md_text)
    if bdd_sels:
        elements.update(bdd_sels)  # BDD selectors override inferred ones

    flows = _flows(flow_raw, elements)
    if not flows:
        flows = _prose_flows(md_text, elements)
    # BDD format: #### Scenario N: blocks with Given/When/Then
    if not flows:
        flows = _bdd_flows(md_text, elements)

    ecs = _edge_cases(ec_raw)
    if not ecs:
        ecs = _prose_edge_cases(md_text)
    # BDD format: Empty/Error States section
    if not ecs:
        ecs = _bdd_edge_cases(md_text)

    vd, inv  = _test_data(data_raw)
    if not vd:
        vd, inv_extra = _prose_test_data(md_text)
        inv = inv or inv_extra

    # Requirements: structured first, prose fallback, BDD Then-assertions last
    reqs = _requirements(req_raw)
    if not reqs:
        reqs = _prose_requirements(md_text)
    if not reqs:
        reqs = _bdd_requirements(md_text)

    # URL fallback for prose specs
    url = _url(md_text) or _prose_url(md_text)
    path_m = re.search(r"https?://[^/\s]+(/[^\s`\)]+)", url)
    path = path_m.group(1) if path_m else _path(md_text)

    return {
        "source":       source_file,
        "page":         _page_name(md_text),
        "url":          url,
        "path":         path,
        "selectors":    elements,
        "requirements": reqs,
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
