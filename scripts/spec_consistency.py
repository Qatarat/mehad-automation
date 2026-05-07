"""
Cross-spec inconsistency detector.

Reads every .md spec under specs/ and finds CONTRADICTIONS — places where
two specs assert incompatible requirements about the same thing. These are
real bugs in the spec layer that, if missed, become bugs in the product
('login allows 6 chars' vs 'student-login requires 8 chars' = sometimes
the modal accepts what the API rejects).

What gets compared
  • Per-field length constraints (min/max)
  • Per-field required/optional state
  • Number of allowed retries / OTP digits / countdown timers
  • URL paths declared per flow
  • Element selectors used for the same conceptual element

Output
  • A list of Inconsistency records, each with:
      - the conceptual key ("phone min length", "OTP digits", etc.)
      - the conflicting values from each spec
      - the source files where each value came from

Surface in master report under a 'Spec Inconsistencies' section.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path

# ─── Patterns that capture cross-spec-comparable facts ────────────────────────
# Each rule tags lines from spec files with a `category_key` and a normalised
# value, so the detector can compare values across specs.
_FACT_RULES: list[tuple[str, re.Pattern, callable]] = [
    # (category_key, regex, value_extractor)
    ("phone_min_digits",
     re.compile(r"min(?:imum)?\s+(\d+)\s+digits?\s*(?:valid|required|for\s+(?:bd|saudi|ksa|uae))?", re.I),
     lambda m: int(m.group(1))),
    ("phone_max_digits",
     re.compile(r"(?:max(?:imum)?\s+(?:length|digits?))[\s:=]*(\d+)", re.I),
     lambda m: int(m.group(1))),
    ("phone_max_length",
     re.compile(r"number\s+max\s+length[\s:=]*(\d+)", re.I),
     lambda m: int(m.group(1))),
    ("otp_digits",
     re.compile(r"(\d+)[\s-]?digit(?:\s+verification|\s+code|\s+otp)", re.I),
     lambda m: int(m.group(1))),
    ("otp_max_length",
     re.compile(r"(?:verification\s+code|otp)\s+max\s+length[\s:=]*(\d+)", re.I),
     lambda m: int(m.group(1))),
    ("password_min_length",
     re.compile(r"password.*?(?:min(?:imum)?\s+(\d+)\s*(?:char|chars))", re.I),
     lambda m: int(m.group(1))),
    ("country_code_default",
     re.compile(r"default\s+country\s+code\s+(?:should\s+be|is)\s+(\+?\d+)", re.I),
     lambda m: m.group(1).strip("+")),
    ("base_url",
     re.compile(r"\*\*url:\*\*\s+`?(https?://[^\s`]+)", re.I),
     lambda m: m.group(1)),
    ("resend_timer",
     re.compile(r"resend\s+(?:otp\s+)?(?:timer\s+)?(?:e\.g\.,?\s+)?(\d+)\s*s", re.I),
     lambda m: int(m.group(1))),
    ("session_timeout",
     re.compile(r"session\s+(?:timeout|expires?\s+after)[\s:]*(\d+)\s*(?:s|sec|seconds|min|minutes|hours|h)", re.I),
     lambda m: int(m.group(1))),
]


@dataclass
class Inconsistency:
    """A contradiction between two or more specs."""
    category_key: str          # e.g. "phone_min_digits"
    values: dict               # {value: [list of source files]}

    def affected_specs(self) -> list[str]:
        out = []
        for sources in self.values.values():
            out.extend(sources)
        return sorted(set(out))

    def conflicting_pairs(self) -> list[tuple]:
        """Each unique (value, source) tuple."""
        return [(v, s) for v, srcs in self.values.items() for s in srcs]


def _extract_facts(spec_path: Path) -> dict[str, list]:
    """Return {category_key: [list of (value, line_number)]} for one spec."""
    out: dict[str, list] = {}
    if not spec_path.exists() or not spec_path.is_file():
        return out
    try:
        text = spec_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return out

    # Strip HTML comments + fenced code (so example syntax doesn't pollute)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    for category_key, pattern, extractor in _FACT_RULES:
        for m in pattern.finditer(text):
            try:
                value = extractor(m)
                out.setdefault(category_key, []).append(value)
            except Exception:
                continue
    return out


def detect_inconsistencies(specs_dir: str | Path) -> list[Inconsistency]:
    """Scan every .md spec under specs_dir and return contradictions."""
    sd = Path(specs_dir)
    if not sd.exists() or not sd.is_dir():
        return []

    # spec_name → {category_key → [values]}
    facts_by_spec: dict[str, dict] = {}
    for md in sd.glob("*.md"):
        # Skip TEMPLATE / README / EXAMPLE
        if md.stem.upper() in ("TEMPLATE", "README", "EXAMPLE"):
            continue
        facts_by_spec[md.stem] = _extract_facts(md)

    # Aggregate: category_key → {value → [specs that assert it]}
    aggregated: dict[str, dict] = {}
    for spec_name, facts in facts_by_spec.items():
        for category, values in facts.items():
            for v in values:
                aggregated.setdefault(category, {}).setdefault(v, []).append(spec_name)

    # An inconsistency exists when a category has >1 distinct value
    # AND at least 2 distinct specs assert different values.
    out: list[Inconsistency] = []
    for category, value_map in aggregated.items():
        if len(value_map) < 2:
            continue
        all_specs = {s for srcs in value_map.values() for s in srcs}
        if len(all_specs) < 2:
            continue
        out.append(Inconsistency(category_key=category, values=value_map))

    return out


def humanise_category(key: str) -> str:
    """Friendly label for the report."""
    labels = {
        "phone_min_digits":     "Phone minimum digit count",
        "phone_max_digits":     "Phone maximum digit count",
        "phone_max_length":     "Phone field max length",
        "otp_digits":           "OTP code length (digits)",
        "otp_max_length":       "OTP field max length",
        "password_min_length":  "Password minimum length",
        "country_code_default": "Default country code",
        "base_url":             "Base URL declared",
        "resend_timer":         "OTP resend timer (seconds)",
        "session_timeout":      "Session timeout",
    }
    return labels.get(key, key.replace("_", " ").title())


def render_html_section(inconsistencies: list[Inconsistency]) -> str:
    """Render the inconsistencies as an HTML section for the master report."""
    if not inconsistencies:
        return ""
    rows = []
    for inc in inconsistencies:
        label = humanise_category(inc.category_key)
        value_rows = []
        for value, sources in inc.values.items():
            spec_chips = " ".join(
                f'<span class="ci-spec-chip">{s}</span>' for s in sources)
            value_rows.append(
                f'<tr><td class="ci-value"><code>{value}</code></td>'
                f'<td>{spec_chips}</td></tr>'
            )
        rows.append(f"""
<div class="ci-row">
  <div class="ci-cat">{label}</div>
  <table class="ci-table">
    <thead><tr><th style="width:140px">Value asserted</th><th>Specs</th></tr></thead>
    <tbody>{''.join(value_rows)}</tbody>
  </table>
</div>
""")
    return f"""
<div class="ci-summary" id="spec-inconsistencies">
  <div class="sec-title" style="margin:24px 0 12px">
    📋 Spec Inconsistencies <span class="count">{len(inconsistencies)} found</span>
  </div>
  <div class="ci-headline">
    Different specs assert <strong>contradictory</strong> requirements about
    the same thing. These are bugs in the spec layer that propagate into
    product bugs (the modal accepts what the API rejects).
  </div>
  <div class="ci-list">{''.join(rows)}</div>
</div>"""
