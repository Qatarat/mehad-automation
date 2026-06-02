"""
Parses a structured .md spec file into sections the AI can process
one focused chunk at a time — prevents token overflow.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedSpec:
    page_name: str
    slug: str                        # e.g. "login", "reset-password"
    url: str
    path: str                        # e.g. "/login"
    requirements: list[str]
    flows: list[dict]                # [{name, steps:[str]}]
    edge_cases: list[dict]           # [{id, scenario, expected}]
    validation_rules: list[str]
    test_data_valid: list[str]
    test_data_invalid: list[str]
    security_inputs: list[str]
    api_endpoints: list[dict]        # [{method, endpoint, trigger}]
    languages: list[str] = field(default_factory=list)  # e.g. ["en", "ar"]
    raw: str = ""                    # full original text (for fallback)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _between(text: str, start_heading: str, stop_headings: list[str]) -> str:
    """Extract text between start_heading and the next matching stop heading."""
    pattern = re.escape(start_heading)
    starts = list(re.finditer(pattern, text, re.IGNORECASE))
    if not starts:
        return ""
    pos = starts[0].end()
    chunk = text[pos:]
    for stop in stop_headings:
        m = re.search(r"^#{1,3}\s+" + re.escape(stop), chunk, re.MULTILINE | re.IGNORECASE)
        if m:
            chunk = chunk[: m.start()]
    return chunk.strip()


def _lines(text: str) -> list[str]:
    return [l.strip() for l in text.splitlines() if l.strip()]


# ── Parser ────────────────────────────────────────────────────────────────────

def parse(spec_path: Path) -> ParsedSpec:
    raw = spec_path.read_text()
    slug = spec_path.stem
    page_name = slug.replace("-", " ").title()

    # ── URL / path ────────────────────────────────────────────────────────────
    url_match = re.search(r"\*\*URL:\*\*\s*`(.+?)`", raw)
    url = url_match.group(1).strip() if url_match else ""
    if not url:
        # Fallback: first http(s) URL anywhere in the first 30 lines.
        # Handles spec styles like `[https://...]`, bare URL lines, and
        # `Open the website: https://...`.
        for line in raw.splitlines()[:30]:
            m = re.search(r"https?://[^\s\]\)`]+", line)
            if m:
                url = m.group(0).rstrip(".,;)")
                break
    path_match = re.search(r"https?://[^/]+(/[^\s`\)]+)", url)
    path = path_match.group(1) if path_match else f"/{slug}"

    # ── Language / locale detection ───────────────────────────────────────────
    # Locale codes must be the FIRST path segment of an http(s) URL — that's
    # the actual semantics of locale-prefixed routes (e.g. /en/foo, /ar/bar).
    # Also accept an explicit `**Locale:**` declaration line.
    KNOWN_LOCALES = {"en", "ar", "fr", "es", "de", "pt", "it", "tr", "zh",
                      "ja", "ko", "ru", "hi", "ur", "bn", "id", "ms", "vi",
                      "th", "nl", "pl", "sv", "fi", "no", "da", "el", "he", "fa"}
    languages: list[str] = []
    seen = set()
    locale_line = re.search(r"\*\*Locale[s]?:\*\*\s*([^\n]+)", raw, re.IGNORECASE)
    if locale_line:
        for code in re.findall(r"`?/([a-z]{2})`?", locale_line.group(1).lower()):
            if code in KNOWN_LOCALES and code not in seen:
                seen.add(code); languages.append(code)
    # URL-anchored: only match when /xx is the first path segment of a URL.
    # Avoids false positives like RTL/LTR, AND/OR, etc.
    for m in re.finditer(r"https?://[^/\s]+/([a-z]{2})(?=[/`\s\]\)]|$)", raw):
        code = m.group(1)
        if code in KNOWN_LOCALES and code not in seen:
            seen.add(code); languages.append(code)
    # Cap — too many languages = noisy tests
    languages = languages[:6]

    # ── Requirements ──────────────────────────────────────────────────────────
    requirements = re.findall(r"(REQ-[A-Z\-\d]+:.+)", raw)
    # Also treat numbered validation/check bullets as implicit requirements
    if not requirements:
        req_bullets = re.findall(
            r"[-*]\s+((?:Ensure|Verify|Confirm|Check|Validate|Must|Should)[^\n]{10,80})",
            raw, re.IGNORECASE
        )
        for i, txt in enumerate(req_bullets[:15], 1):
            requirements.append(f"REQ-{i:02d}: {txt.strip()}")
    # BDD format: extract "Then ..." assertions as requirements
    # Handles both plain "Then ..." and bold "**Then** ..." formats
    if not requirements:
        then_lines: list[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped in ("```", "```bdd", "```gherkin"):
                continue
            # Plain format
            mp = re.match(r"^(?:Then|And)\s+(.{10,120})", stripped, re.IGNORECASE)
            if mp:
                then_lines.append(mp.group(1).strip())
                continue
            # Bold format
            mb = re.match(r"^\*\*(?:Then|And)\*\*\s+(.{10,120})", stripped, re.IGNORECASE)
            if mb:
                then_lines.append(mb.group(1).strip())
        for i, txt in enumerate(then_lines[:15], 1):
            if txt and "<" not in txt:
                requirements.append(f"REQ-{i:02d}: {txt}")

    # ── User flows ────────────────────────────────────────────────────────────
    # Support three formats:
    #   1. Markopolo format: ## User Flows → ### Flow N → numbered steps
    #   2. Mehad step format: ## Steps to Reproduce... → numbered list
    #   3. BDD format: #### Scenario N: ... → Given/When/Then blocks
    flows_section = _between(raw, "## User Flows", ["## Validation", "## Edge", "## Expected", "## Test Data", "## API"])
    flow_blocks = re.split(r"###\s+Flow\s+\d+", flows_section, flags=re.IGNORECASE)
    flows = []
    for i, block in enumerate(flow_blocks):
        if not block.strip():
            continue
        title_m = re.match(r":?\s*(.+)", block.strip())
        title = title_m.group(1).split("\n")[0].strip() if title_m else f"Flow {i}"
        steps = re.findall(r"\d+\.\s+(.+)", block)
        if steps:
            flows.append({"name": title[:60], "steps": steps[:10]})

    # Mehad-style: "## Steps to Reproduce...", "## Steps for...", "# ... Process"
    if not flows:
        step_sections = re.finditer(
            r"##\s+(Steps[^\n]*|.*Process[^\n]*|.*Flow[^\n]*|.*Booking[^\n]*)\n(.*?)(?=\n##\s|\Z)",
            raw, re.DOTALL | re.IGNORECASE
        )
        for m in step_sections:
            title = m.group(1).strip()[:60]
            block = m.group(2)
            steps = re.findall(r"\d+\.\s+(.+)", block)
            sub_steps = re.findall(r"###\s+\d+\.\s+(.+)", block)
            all_steps = (sub_steps or steps)[:10]
            if all_steps:
                flows.append({"name": title, "steps": all_steps})

    # BDD format: #### Scenario N: or ### XX-NN: blocks with Given/When/Then
    if not flows:
        scenario_blocks = re.finditer(
            r"#{2,4}\s+(?:Scenario\s+\d+[:\s]+|[A-Z]{2,6}-\d+[:\s]+)([^\n]+)\n"
            r"(.*?)(?=\n#{2,4}\s+(?:Scenario\s+\d+|[A-Z]{2,6}-\d+)|\n##\s|\Z)",
            raw, re.DOTALL | re.IGNORECASE
        )
        for m in scenario_blocks:
            title = m.group(1).strip()[:60]
            block = m.group(2)
            steps: list[str] = []
            for line in block.splitlines():
                stripped = line.strip()
                if stripped in ("```", "```bdd", "```gherkin"):
                    continue
                # Plain: "Given/When/Then/And ..."
                mp = re.match(r"^(Given|When|Then|And)\s+(.+)", stripped, re.IGNORECASE)
                if mp:
                    steps.append(" ".join(mp.group(0).split())[:100])
                    continue
                # Bold: "**Given** ..." / "**Then** ..."
                mb = re.match(r"^\*\*(Given|When|Then|And)\*\*\s+(.+)", stripped, re.IGNORECASE)
                if mb:
                    steps.append(" ".join(f"{mb.group(1)} {mb.group(2)}".split())[:100])
            steps = steps[:8]
            if steps:
                flows.append({"name": title, "steps": steps})

    # ── Edge cases (table) ────────────────────────────────────────────────────
    edge_cases = []
    for row in re.finditer(
        r"\|\s*(EC-[A-Z\-\d]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", raw
    ):
        edge_cases.append({
            "id":       row.group(1),
            "scenario": row.group(2).strip(),
            "expected": row.group(3).strip(),
        })
    # Mehad-style: bullet points with "should not", "must not", negative scenarios
    if not edge_cases:
        ec_bullets = re.findall(
            r"[-*]\s+((?:Empty|Invalid|Wrong|Incorrect|Duplicate|Missing|No |Over|Exceed|Max|Min)[^\n]{5,80})",
            raw, re.IGNORECASE
        )
        for i, txt in enumerate(ec_bullets[:12], 1):
            edge_cases.append({
                "id": f"EC-{i:02d}",
                "scenario": txt.strip(),
                "expected": "System shows appropriate error or prevents the action",
            })

    # ── Validation rules ──────────────────────────────────────────────────────
    val_section = _between(raw, "## Validation Rules", ["## Edge", "## Expected", "## Test Data", "## API"])
    validation_rules = [l for l in _lines(val_section) if l.startswith("-") or re.match(r"###|Must|Should|Required", l)]

    # ── Test data ─────────────────────────────────────────────────────────────
    td_section = _between(raw, "## Test Data", ["## API", "## Related", "## Coverage"])
    valid_block   = _between(td_section, "### Valid",   ["### Invalid", "### Malformed", "### Injection"])
    invalid_block = _between(td_section, "### Invalid", ["### Injection", "### Security", "---"])
    security_block= _between(td_section, "### Injection", ["---", "##"])
    if not security_block:
        security_block = _between(td_section, "### Security", ["---", "##"])

    td_valid    = [l for l in _lines(valid_block)   if l.startswith(("email:", "password:", "name:", "username:"))]
    td_invalid  = [l for l in _lines(invalid_block) if l.startswith(("email:", "password:", "name:"))]
    td_security = [l for l in _lines(security_block) if l.startswith(("email:", "name:", "password:"))]

    # BDD / phone-OTP specs: extract credentials from **Credentials:** line
    if not td_valid:
        cred_m = re.search(r"\*\*Credentials?:\*\*\s*([^\n]+)", raw, re.IGNORECASE)
        if cred_m:
            cred_raw = cred_m.group(1).strip()
            # e.g. "+880 98976564 / OTP 123456"
            phone_m = re.search(r"(\+?\d[\d\s]{7,14})", cred_raw)
            if phone_m:
                td_valid.append(f"phone: {phone_m.group(1).strip()}")
            otp_m = re.search(r"OTP\s+(\d{4,8})", cred_raw, re.IGNORECASE)
            if otp_m:
                td_valid.append(f"otp: {otp_m.group(1)}")

    # ── API endpoints ─────────────────────────────────────────────────────────
    api_endpoints = []
    for row in re.finditer(r"\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`?.+?`?)\s*\|", raw):
        api_endpoints.append({
            "method":   row.group(1),
            "endpoint": row.group(2).strip("`").strip(),
        })

    return ParsedSpec(
        page_name=page_name,
        slug=slug,
        url=url,
        path=path,
        requirements=requirements[:20],
        flows=flows[:8],
        edge_cases=edge_cases[:15],
        validation_rules=validation_rules[:15],
        test_data_valid=td_valid[:5],
        test_data_invalid=td_invalid[:8],
        security_inputs=td_security[:5],
        api_endpoints=api_endpoints[:6],
        languages=languages,
        raw=raw,
    )


# ── Section summaries for focused AI prompts ──────────────────────────────────

def flows_prompt_section(spec: ParsedSpec) -> str:
    if not spec.flows:
        return ""
    lines = [f"PAGE: {spec.page_name}  URL: {spec.url}\n"]
    for i, f in enumerate(spec.flows, 1):
        lines.append(f"FLOW {i}: {f['name']}")
        for s in f["steps"]:
            lines.append(f"  {s}")
    return "\n".join(lines)


def edge_cases_prompt_section(spec: ParsedSpec) -> str:
    if not spec.edge_cases:
        return ""
    lines = [f"PAGE: {spec.page_name}  URL: {spec.url}\n", "EDGE CASES:"]
    for ec in spec.edge_cases:
        lines.append(f"  {ec['id']}: Input={ec['scenario'][:80]} → Expected={ec['expected'][:80]}")
    return "\n".join(lines)


def validation_prompt_section(spec: ParsedSpec) -> str:
    parts = [f"PAGE: {spec.page_name}  URL: {spec.url}\n"]
    if spec.validation_rules:
        parts.append("VALIDATION RULES:")
        for r in spec.validation_rules[:10]:
            parts.append(f"  {r}")
    if spec.test_data_invalid:
        parts.append("\nINVALID TEST INPUTS:")
        for t in spec.test_data_invalid:
            parts.append(f"  {t}")
    return "\n".join(parts)


def security_prompt_section(spec: ParsedSpec) -> str:
    parts = [f"PAGE: {spec.page_name}  URL: {spec.url}\n", "SECURITY TEST INPUTS:"]
    inputs = spec.security_inputs or [
        "email: <script>alert(1)</script>@test.com",
        "email: ' OR '1'='1'--@test.com",
        "name: <img src=x onerror=alert(1)>",
    ]
    for s in inputs:
        parts.append(f"  {s}")
    return "\n".join(parts)
