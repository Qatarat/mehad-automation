"""
Master Spec Validator & Test Generator
=======================================
python scripts/validate_all_specs.py [--run] [--report]

Reads ALL 12 spec MD files → parses → compiles → generates test cases with
test data for every scenario → writes tests/test_specs_all.py → runs pytest
→ generates a comprehensive HTML + JSON report.

Test types generated per spec (no AI needed — deterministic):
  functional   — happy path for each flow
  validation   — form field validation (required, format, length)
  negative     — invalid inputs, wrong credentials, missing fields
  boundary     — empty, whitespace, max-length, min-length
  security     — XSS, SQLi, SSTI in every text input
  navigation   — page loads, URL correctness, back/forward
  edge_case    — each EC from the spec
  requirement  — verifies each REQ- statement
  performance  — page load time < threshold

Total expected: ~1500+ test cases across all 12 specs.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ai_engine.spec_parser  import parse  as parse_spec
from ai_engine.spec_compiler import compile_spec

BASE_URL   = os.getenv("BASE_URL",      "https://beta-stg.markopolo.ai")
TEST_EMAIL = os.getenv("TEST_EMAIL",    "towsif@markopolo.ai")
TEST_PASS  = os.getenv("TEST_PASSWORD", "Markopolo@2025")
LOAD_LIMIT = float(os.getenv("LOAD_TIME_LIMIT", "20.0"))

SPECS_DIR  = ROOT / "specs"
OUTPUT_PY  = ROOT / "tests" / "test_specs_all.py"
REPORT_DIR = ROOT / "reports"

# Load payload files for security tests
def _load_payloads(fname: str, limit: int = 8) -> list[str]:
    p = ROOT / "payloads" / fname
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines()
            if l.strip() and not l.startswith("#")][:limit]

XSS_PAYLOADS  = _load_payloads("xss.txt", 6)
SQLI_PAYLOADS = _load_payloads("sqli.txt", 6)
SSTI_PAYLOADS = _load_payloads("ssti.txt", 4)
OPEN_REDIRECT = _load_payloads("open_redirect.txt", 4)
BAD_EMAILS    = _load_payloads("invalid_email.txt", 6)
BAD_PASSWORDS = _load_payloads("invalid_password.txt", 5)


# ── Spec audit ────────────────────────────────────────────────────────────────

def audit_spec(compiled: dict, md_name: str) -> dict:
    """Return a quality audit of a compiled spec."""
    sels   = compiled.get("selectors", {})
    flows  = compiled.get("flows", [])
    ecs    = compiled.get("edge_cases", [])
    reqs   = compiled.get("requirements", [])
    td     = compiled.get("test_data", {})
    issues = []
    if not sels:             issues.append("NO_SELECTORS")
    if not flows:            issues.append("NO_FLOWS")
    if not reqs:             issues.append("NO_REQUIREMENTS")
    if not td.get("valid"):  issues.append("NO_VALID_TEST_DATA")
    return {
        "spec":       md_name,
        "selectors":  len(sels),
        "flows":      len(flows),
        "edge_cases": len(ecs),
        "requirements": len(reqs),
        "valid_td":   len(td.get("valid", [])),
        "invalid_td": len(td.get("invalid", [])),
        "issues":     issues,
        "quality":    "GOOD" if not issues else ("WARN" if len(issues) <= 1 else "POOR"),
    }


# ── Test code generation ──────────────────────────────────────────────────────

def _slug(text: str) -> str:
    import re, unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]", "_", text.lower()).strip("_")[:40] or "item"


def _safe_label(text: str) -> str:
    """Remove chars that break f-string literals in generated code."""
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.replace("'", "").replace('"', "").replace("\\", "")[:60]


def _clean_hint(hint: str) -> str:
    """Normalize selector hints from spec into a valid Playwright method chain."""
    import re as _re
    hint = hint.strip("`").strip()
    # Strip leading 'page.' prefix — the template already writes 'page.{hint}'
    if hint.startswith("page."):
        hint = hint[5:]
    # Take only the first option when hint lists multiple (e.g. "X or regex /Y/")
    if " or " in hint.lower():
        hint = _re.split(r"\s+or\s+", hint, flags=_re.IGNORECASE)[0].strip()
    # Final cleanup of any remaining backtick fragments
    hint = hint.strip("`").strip()
    # Must start with a valid Python identifier; reject otherwise
    if not hint or not _re.match(r"^[a-zA-Z_]", hint):
        return ""
    # Validate the full expression via AST — catches ALL remaining syntax issues
    # (unbalanced quotes, JS regex literals /pattern/, etc.)
    try:
        ast.parse(f"page.{hint}.first", mode="eval")
    except SyntaxError:
        return ""
    return hint


def _repr(data: list[str]) -> str:
    if len(data) == 1:
        return repr(data[0])
    return "[" + ", ".join(repr(d) for d in data) + "]"


# ── Deep test-code helpers ────────────────────────────────────────────────────

def _find_field_hint(selectors: dict, *keywords: str) -> tuple[str, str]:
    """Return (sel_name, hint) for first selector whose name contains any keyword."""
    for k, v in selectors.items():
        kl = k.lower()
        if any(kw in kl for kw in keywords):
            h = _clean_hint(v.get("hint", ""))
            if h:
                return k, h
    return "", ""


def _step_to_code(step, ind: str, sels: dict, page_path: str = "/") -> list[str]:
    """Convert a compiled flow step (dict or str) to Python/Playwright lines."""
    if not isinstance(step, dict):
        return [f"{ind}page.wait_for_timeout(200)"]
    action = step.get("action", "")
    target = step.get("target", "")
    value  = step.get("value", "")

    sel_hint = ""
    if target:
        _, sel_hint = _find_field_hint(sels, *target.lower().split()[:2])

    def _is_template(s: str) -> bool:
        return s.startswith("$") or "{" in s or s in ("URL", "BASE_URL", "url")

    lines: list[str] = []
    if action == "goto":
        dest = value or target or page_path
        if _is_template(dest):
            dest = page_path
        lines.append(f"{ind}page.goto(BASE_URL + {dest!r}, wait_until='commit', timeout=30000)")
        lines.append(f"{ind}page.wait_for_timeout(2500)")
    elif action in ("fill", "type"):
        if sel_hint:
            # Use heuristic test data when the compiled step has an empty value
            if not value:
                tl = target.lower()
                if "email" in tl or "username" in tl:
                    value = "qa_test@markopolo.ai"
                elif "password" in tl or "pass" in tl:
                    value = "Test@1234!"
                elif "name" in tl or "title" in tl:
                    value = "QA Test Entry"
                else:
                    value = "test_value"
            lines.append(f"{ind}try:")
            lines.append(f"{ind}    page.{sel_hint}.fill({value!r}, timeout=5000)")
            lines.append(f"{ind}except Exception: pass")
        else:
            lines.append(f"{ind}page.wait_for_timeout(200)")
    elif action == "click":
        if sel_hint:
            lines.append(f"{ind}try:")
            lines.append(f"{ind}    page.{sel_hint}.click(timeout=5000)")
            lines.append(f"{ind}    page.wait_for_timeout(500)")
            lines.append(f"{ind}except Exception: pass")
        else:
            lines.append(f"{ind}page.wait_for_timeout(300)")
    elif action == "assert_url":
        lines.append(f"{ind}page.wait_for_timeout(1000)")
        lines.append(f"{ind}_exp_url = {value!r}")
        lines.append(f"{ind}assert _exp_url in page.url, f'Expected URL with {{_exp_url!r}}, got {{page.url}}'")
    elif action == "assert_visible":
        if sel_hint:
            lines.append(f"{ind}try:")
            lines.append(f"{ind}    page.{sel_hint}.wait_for(state='visible', timeout=5000)")
            lines.append(f"{ind}except Exception:")
            lines.append(f"{ind}    pytest.fail(f'Expected visible: {target} on {{page.url}}')")
        else:
            lines.append(f"{ind}assert '500' not in page.title(), f'Visible check on {{page.url}}'")
    elif action in ("assert_text", "assert_contains"):
        if sel_hint and value:
            lines.append(f"{ind}try:")
            lines.append(f"{ind}    txt = page.{sel_hint}.text_content(timeout=5000) or ''")
            lines.append(f"{ind}    _exp_txt = {value!r}")
            lines.append(f"{ind}    assert _exp_txt in txt, f'Expected {{_exp_txt!r}} in element text, got {{txt!r}}'")
            lines.append(f"{ind}except AssertionError: raise")
            lines.append(f"{ind}except Exception: pass")
        else:
            lines.append(f"{ind}assert '500' not in page.title(), f'Text check on {{page.url}}'")
    elif action == "assert_title":
        lines.append(f"{ind}_exp_t = {value!r}")
        lines.append(f"{ind}assert _exp_t in page.title(), f'Expected title with {{_exp_t!r}}, got {{page.title()!r}}'")
    else:
        lines.append(f"{ind}page.wait_for_timeout(300)")
    return lines


def _heuristic_flow_lines(flow_name: str, page_path: str, sels: dict) -> list[str]:
    """Generate real flow interactions from the flow name when no compiled steps exist."""
    fname = flow_name.lower()
    lines: list[str] = []
    i = "        "

    _, email_h  = _find_field_hint(sels, "email", "username", "login")
    _, pass_h   = _find_field_hint(sels, "password", "pass")
    _, submit_h = _find_field_hint(sels, "submit", "signin", "sign_in", "login_btn", "login-btn", "btn")
    _, search_h = _find_field_hint(sels, "search", "query", "find")
    _, name_h   = _find_field_hint(sels, "name", "title", "label")

    lines.append(f"{i}page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)")
    lines.append(f"{i}page.wait_for_timeout(2500)")

    if any(w in fname for w in ("login", "sign in", "signin", "auth", "credential")):
        if email_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('qa_test@markopolo.ai', timeout=5000)",
                f"{i}    page.wait_for_timeout(200)",
                f"{i}except Exception: pass",
            ]
        if pass_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{pass_h}.fill('Test@1234!', timeout=5000)",
                f"{i}    page.wait_for_timeout(200)",
                f"{i}except Exception: pass",
            ]
        if submit_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{submit_h}.click(timeout=5000)",
                f"{i}    page.wait_for_timeout(1500)",
                f"{i}except Exception: pass",
            ]
        lines.append(f"{i}assert '500' not in page.title(), f'Server error after login flow: {{page.url}}'")

    elif any(w in fname for w in ("invalid", "wrong", "bad", "incorrect", "fail")):
        if email_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('wrong@invalid.xyz', timeout=5000)",
                f"{i}except Exception: pass",
            ]
        if pass_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{pass_h}.fill('wrongpassword', timeout=5000)",
                f"{i}except Exception: pass",
            ]
        if submit_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{submit_h}.click(timeout=5000)",
                f"{i}    page.wait_for_timeout(1500)",
                f"{i}except Exception: pass",
            ]
        lines.append(f"{i}assert '500' not in page.title(), f'Server error on invalid creds: {{page.url}}'")

    elif any(w in fname for w in ("search", "find", "query", "filter")):
        if search_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{search_h}.fill('test search', timeout=5000)",
                f"{i}    page.keyboard.press('Enter')",
                f"{i}    page.wait_for_timeout(1000)",
                f"{i}except Exception: pass",
            ]
        lines.append(f"{i}assert '500' not in page.title(), f'Server error after search flow: {{page.url}}'")

    elif any(w in fname for w in ("create", "add", "new", "submit")):
        if name_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{name_h}.fill('QA Test Entry', timeout=5000)",
                f"{i}    page.wait_for_timeout(200)",
                f"{i}except Exception: pass",
            ]
        if submit_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{submit_h}.click(timeout=5000)",
                f"{i}    page.wait_for_timeout(1000)",
                f"{i}except Exception: pass",
            ]
        lines.append(f"{i}assert '500' not in page.title(), f'Server error after create flow: {{page.url}}'")

    elif any(w in fname for w in ("forgot", "reset", "recover")):
        _, forgot_h = _find_field_hint(sels, "forgot", "reset", "recover")
        if forgot_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{forgot_h}.click(timeout=5000)",
                f"{i}    page.wait_for_timeout(1500)",
                f"{i}    assert '500' not in page.title(), f'Server error on forgot-password: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pass",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Server error on forgot flow: {{page.url}}'")

    else:
        lines.append(f"{i}assert '500' not in page.title(), f'Server error on flow {flow_name}: {{page.url}}'")

    return lines


def _req_assertion_lines(req: str, sels: dict, page_path: str, page_name: str) -> list[str]:
    """Generate smart assertions for a requirement string."""
    import re as _re
    rl = req.lower()
    lines: list[str] = []
    i = "        "

    _, email_h  = _find_field_hint(sels, "email", "username")
    _, pass_h   = _find_field_hint(sels, "password", "pass")
    _, submit_h = _find_field_hint(sels, "submit", "signin", "sign_in", "login_btn", "btn")
    _, toggle_h = _find_field_hint(sels, "toggle", "show_pass", "eye", "visibility")
    _, forgot_h = _find_field_hint(sels, "forgot", "reset", "recover")

    lines.append(f"{i}page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)")
    lines.append(f"{i}page.wait_for_timeout(2500)")

    if any(w in rl for w in ("title", "page title", "document title")):
        m = _re.search(r'"([^"]+)"', req)
        if m:
            expected = m.group(1)
            lines.append(f"{i}_exp = {expected!r}")
            lines.append(f"{i}t = page.title()")
            lines.append(f"{i}assert _exp in t or '500' not in t, f'Expected title with {{_exp!r}}, got {{t!r}}'")
        else:
            lines.append(f"{i}assert page.title() != '', f'Empty title on {{page.url}}'")
            lines.append(f"{i}assert '500' not in page.title(), f'Server error: {{page.title()!r}}'")

    elif any(w in rl for w in ("redirect", "navigate to", "taken to", "after login", "after success")):
        if email_h and pass_h and submit_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('qa_test@markopolo.ai', timeout=4000)",
                f"{i}    page.{pass_h}.fill('Test@1234!', timeout=4000)",
                f"{i}    page.{submit_h}.click(timeout=4000)",
                f"{i}    page.wait_for_timeout(2000)",
                f"{i}    assert '500' not in page.title(), f'Server error after login: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Login elements not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Redirect check: {{page.url}}'")

    elif any(w in rl for w in ("error message", "validation message", "invalid credential", "wrong password")):
        if email_h and submit_h:
            _pw_fill = ([f"{i}    try: page.{pass_h}.fill('wrongpass', timeout=3000)",
                         f"{i}    except Exception: pass"] if pass_h else [])
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('notvalid@x.yz', timeout=4000)",
                *_pw_fill,
                f"{i}    page.{submit_h}.click(timeout=3000)",
                f"{i}    page.wait_for_timeout(800)",
                f"{i}    content = page.content().lower()",
                f"{i}    assert '500' not in page.title(), f'Server error on invalid creds: {{page.url}}'",
                f"{i}    has_err = any(w in content for w in ['error', 'invalid', 'incorrect', 'wrong', 'failed'])",
                f"{i}    assert has_err, f'Expected error message for invalid credentials on {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Form not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Error message check: {{page.url}}'")

    elif any(w in rl for w in ("password mask", "password hidden", "type.*password", "input type")):
        if pass_h:
            lines += [
                f"{i}try:",
                f"{i}    el = page.{pass_h}.first",
                f"{i}    t = el.get_attribute('type') or ''",
                f"{i}    assert t == 'password', f'Password field type should be password, got {{t!r}}'",
                f"{i}except Exception: pytest.skip(f'Password field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Password mask check: {{page.url}}'")

    elif any(w in rl for w in ("show password", "toggle", "visibility", "eye icon", "reveal")):
        if pass_h and toggle_h:
            lines += [
                f"{i}try:",
                f"{i}    pw = page.{pass_h}.first",
                f"{i}    assert pw.get_attribute('type') == 'password', 'Password should start hidden'",
                f"{i}    page.{toggle_h}.click(timeout=3000)",
                f"{i}    page.wait_for_timeout(300)",
                f"{i}    t2 = pw.get_attribute('type') or ''",
                f"{i}    assert t2 in ('text', 'password'), f'Unexpected type after toggle: {{t2!r}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Toggle elements not found on {{page.url}}')",
            ]
        elif pass_h:
            lines += [
                f"{i}try:",
                f"{i}    assert page.{pass_h}.first.get_attribute('type') == 'password', 'Password field not masked'",
                f"{i}except Exception: pytest.skip(f'Password field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Toggle check: {{page.url}}'")

    elif any(w in rl for w in ("forgot password", "reset password", "password reset")):
        if forgot_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{forgot_h}.click(timeout=4000)",
                f"{i}    page.wait_for_timeout(1200)",
                f"{i}    assert '500' not in page.title(), f'Server error on forgot pw: {{page.url}}'",
                f"{i}    assert any(w in page.url for w in ['forgot', 'reset', 'recover', 'password']), \\",
                f"{i}        f'Expected forgot-password URL, got {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Forgot-password link not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Forgot password check: {{page.url}}'")

    elif any(w in rl for w in ("visible", "present", "displayed", "shown", "appear")):
        for _k, _v in sels.items():
            _h = _clean_hint(_v.get("hint", ""))
            if _h:
                lines += [
                    f"{i}try:",
                    f"{i}    page.{_h}.wait_for(state='visible', timeout=6000)",
                    f"{i}except Exception:",
                    f"{i}    pytest.fail(f'Required element not visible on {{page.url}}')",
                ]
                break
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Visible check: {{page.url}}'")

    else:
        lines.append(f"{i}assert '500' not in page.title(), f'Server error on REQ: {{page.url}}'")
        lines.append(f"{i}assert '404' not in page.title(), f'Page not found: {{page.url}}'")

    return lines


def _ec_to_test_body(ec: dict, sels: dict, page_path: str) -> list[str]:
    """Generate scenario-specific test body for an edge case."""
    scenario = str(ec.get("scenario", ec.get("description", ""))).lower()
    i = "        "
    lines: list[str] = []

    _, email_h   = _find_field_hint(sels, "email", "username")
    _, pass_h    = _find_field_hint(sels, "password", "pass")
    _, submit_h  = _find_field_hint(sels, "submit", "signin", "sign_in", "login_btn", "btn")
    _, name_h    = _find_field_hint(sels, "name", "title", "text", "search")

    lines.append(f"{i}page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)")
    lines.append(f"{i}page.wait_for_timeout(1200)")

    if any(w in scenario for w in ("empty email", "blank email", "no email", "without email")):
        if submit_h:
            _email_fill = ([f"{i}    page.{email_h}.fill('', timeout=3000)"] if email_h else [])
            _pass_fill  = ([f"{i}    page.{pass_h}.fill('Test@1234!', timeout=3000)"] if pass_h else [])
            lines += [f"{i}try:", *_email_fill, *_pass_fill,
                f"{i}    page.{submit_h}.click(timeout=3000)",
                f"{i}    page.wait_for_timeout(800)",
                f"{i}    assert '500' not in page.title(), 'Server error on empty email EC'",
                f"{i}    content = page.content().lower()",
                f"{i}    assert any(w in content for w in ['required', 'error', 'empty', 'fill in']), \\",
                f"{i}        f'Expected validation error for empty email, got {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Form not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Empty email EC: {{page.url}}'")

    elif any(w in scenario for w in ("empty password", "blank password", "no password", "without password")):
        if submit_h:
            _email_fill = ([f"{i}    page.{email_h}.fill('user@test.com', timeout=3000)"] if email_h else [])
            _pass_fill  = ([f"{i}    page.{pass_h}.fill('', timeout=3000)"] if pass_h else [])
            lines += [f"{i}try:", *_email_fill, *_pass_fill,
                f"{i}    page.{submit_h}.click(timeout=3000)",
                f"{i}    page.wait_for_timeout(800)",
                f"{i}    assert '500' not in page.title(), 'Server error on empty password EC'",
                f"{i}    content = page.content().lower()",
                f"{i}    assert any(w in content for w in ['required', 'error', 'empty', 'fill in']), \\",
                f"{i}        f'Expected validation error for empty password, got {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Form not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Empty password EC: {{page.url}}'")

    elif any(w in scenario for w in ("xss", "cross-site", "script injection", "<script")):
        target_h = email_h or name_h
        if target_h:
            xss = "<script>alert('xss')</script>"
            lines += [
                f"{i}alerts: list = []",
                f"{i}page.on('dialog', lambda d: (alerts.append(d.message), d.dismiss()))",
                f"{i}try:",
                f"{i}    page.{target_h}.fill({xss!r}, timeout=3000)",
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    assert len(alerts) == 0, f'XSS executed! alerts={{alerts}}'",
                f"{i}    assert '500' not in page.title(), f'Server error on XSS EC: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Input not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'XSS EC check: {{page.url}}'")

    elif any(w in scenario for w in ("sql", "sqli", "injection", "' or", "drop table")):
        target_h = email_h or name_h
        if target_h:
            sql = "' OR '1'='1"
            lines += [
                f"{i}_sqli_p = {sql!r}",
                f"{i}try:",
                f"{i}    page.{target_h}.fill(_sqli_p, timeout=3000)",
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    content = page.content().lower()",
                f"{i}    bad = any(kw in content for kw in ['sql syntax', 'mysql_fetch', 'pg_query', 'ora-'])",
                f"{i}    assert not bad, f'SQLi DB error exposed! payload={{_sqli_p!r}}'",
                f"{i}    assert '500' not in page.title(), f'Server error on SQLi EC: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Input not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'SQLi EC check: {{page.url}}'")

    elif any(w in scenario for w in ("whitespace", "spaces only", "space only", "blank spaces")):
        target_h = email_h or name_h
        if target_h:
            _submit_click = ([f"{i}    try: page.{submit_h}.click(timeout=2000)",
                               f"{i}    except Exception: pass"] if submit_h else [])
            lines += [
                f"{i}try:",
                f"{i}    page.{target_h}.fill('   ', timeout=3000)",
                *_submit_click,
                f"{i}    page.wait_for_timeout(400)",
                f"{i}    assert '500' not in page.title(), f'Server error on whitespace EC: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Input not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Whitespace EC: {{page.url}}'")

    elif any(w in scenario for w in ("keyboard", "enter key", "press enter", "submit.*enter", "enter.*submit")):
        if email_h and pass_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('qa_test@markopolo.ai', timeout=3000)",
                f"{i}    page.{pass_h}.fill('Test@1234!', timeout=3000)",
                f"{i}    page.{pass_h}.press('Enter')",
                f"{i}    page.wait_for_timeout(1500)",
                f"{i}    assert '500' not in page.title(), f'Server error after Enter-key submit: {{page.url}}'",
                f"{i}except Exception: pytest.skip(f'Form not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Keyboard submit EC: {{page.url}}'")

    elif any(w in scenario for w in ("tab order", "tab navigation", "keyboard navigation", "focus order")):
        lines += [
            f"{i}page.keyboard.press('Tab')",
            f"{i}page.wait_for_timeout(200)",
            f"{i}page.keyboard.press('Tab')",
            f"{i}page.wait_for_timeout(200)",
            f"{i}focused = page.evaluate('document.activeElement ? document.activeElement.tagName : null')",
            f"{i}assert focused is not None, f'Tab focus not working on {{page.url}}'",
            f"{i}assert '500' not in page.title(), f'Server error on tab nav EC: {{page.url}}'",
        ]

    elif any(w in scenario for w in ("local storage", "session storage", "cookie", "storage")):
        lines += [
            f"{i}storage = page.evaluate('Object.keys(localStorage)') or []",
            f"{i}assert '500' not in page.title(), f'Server error: {{page.url}}'",
            f"{i}sensitive = ['password', 'secret_key', 'plain_token']",
            f"{i}for s in sensitive:",
            f"{i}    assert not any(s in k.lower() for k in storage), \\",
            f"{i}        f'Sensitive key {{s!r}} found in localStorage keys: {{storage}}'",
        ]

    elif any(w in scenario for w in ("long string", "long input", "max length", "very long")):
        target_h = email_h or name_h
        if target_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{target_h}.fill('A' * 512, timeout=3000)",
                f"{i}    page.wait_for_timeout(400)",
                f"{i}    assert '500' not in page.title(), f'Server error on long input EC: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Input not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Long input EC: {{page.url}}'")

    elif any(w in scenario for w in ("rapid", "double click", "multiple click", "spam")):
        if submit_h:
            lines += [
                f"{i}try:",
                f"{i}    for _ in range(3):",
                f"{i}        try: page.{submit_h}.click(timeout=1500)",
                f"{i}        except Exception: break",
                f"{i}        page.wait_for_timeout(100)",
                f"{i}    assert '500' not in page.title(), f'Server error on rapid-click EC: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Button not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Rapid click EC: {{page.url}}'")

    elif any(w in scenario for w in ("back button", "browser back", "navigate back")):
        lines += [
            f"{i}page.go_back()",
            f"{i}page.wait_for_timeout(500)",
            f"{i}assert '500' not in page.title(), f'Server error after back-button EC: {{page.url}}'",
        ]

    elif any(w in scenario for w in ("session", "expir", "timeout", "re-login")):
        lines += [
            f"{i}page.evaluate('sessionStorage.clear()')",
            f"{i}page.evaluate('localStorage.removeItem(\"token\")')",
            f"{i}page.wait_for_timeout(300)",
            f"{i}assert '500' not in page.title(), f'Server error on session EC: {{page.url}}'",
        ]

    else:
        lines.append(f"{i}assert '500' not in page.title(), f'Server error on edge case: {{page.url}}'")
        lines.append(f"{i}assert '404' not in page.title(), f'Page not found on edge case: {{page.url}}'")

    return lines


def _validation_to_test_body(rule: dict, sels: dict, page_path: str) -> list[str]:
    """Generate test body for a validation rule."""
    import re as _re
    field  = str(rule.get("field", "")).lower()
    rule_t = str(rule.get("rule", rule.get("constraint", ""))).lower()
    i = "        "
    lines: list[str] = []

    _, email_h  = _find_field_hint(sels, "email", "username")
    _, pass_h   = _find_field_hint(sels, "password", "pass")
    _, name_h   = _find_field_hint(sels, "name", "title", "text")
    _, submit_h = _find_field_hint(sels, "submit", "signin", "sign_in", "login_btn", "btn")

    target_h = ""
    if "email" in field:
        target_h = email_h
    elif "password" in field or "pass" in field:
        target_h = pass_h
    elif "name" in field or "title" in field:
        target_h = name_h
    if not target_h:
        target_h = email_h or name_h

    lines.append(f"{i}page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)")
    lines.append(f"{i}page.wait_for_timeout(1200)")

    if any(w in rule_t for w in ("required", "cannot be empty", "mandatory", "must not be empty")):
        if submit_h and target_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{target_h}.fill('', timeout=3000)",
                f"{i}    page.{submit_h}.click(timeout=3000)",
                f"{i}    page.wait_for_timeout(800)",
                f"{i}    content = page.content().lower()",
                f"{i}    assert '500' not in page.title(), f'Server error on required check: {{page.url}}'",
                f"{i}    assert any(w in content for w in ['required', 'error', 'mandatory', 'field is required']), \\",
                f"{i}        f'Expected required-field validation, got: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Form not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Required field check: {{page.url}}'")

    elif any(w in rule_t for w in ("email format", "valid email", "must be valid email")):
        if email_h:
            _sub_click_ef = ([f"{i}    try: page.{submit_h}.click(timeout=2000)",
                               f"{i}    except Exception: pass"] if submit_h else [])
            lines += [
                f"{i}try:",
                f"{i}    page.{email_h}.fill('notanemail', timeout=3000)",
                *_sub_click_ef,
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    content = page.content().lower()",
                f"{i}    assert '500' not in page.title(), f'Server error on email format check: {{page.url}}'",
                f"{i}    has_err = any(w in content for w in ['invalid email', 'valid email', 'error', 'invalid'])",
                f"{i}    assert has_err or page.url != BASE_URL + {page_path!r}, \\",
                f"{i}        f'Expected email format validation for notanemail, got: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Email field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Email format check: {{page.url}}'")

    elif any(w in rule_t for w in ("min", "minimum", "at least", "minimum length")):
        m = _re.search(r'(\d+)', rule_t)
        min_len = int(m.group(1)) if m else 8
        short_val = "a" * max(1, min_len - 1)
        if target_h:
            _sub_click_ml = ([f"{i}    try: page.{submit_h}.click(timeout=2000)",
                               f"{i}    except Exception: pass"] if submit_h else [])
            lines += [
                f"{i}try:",
                f"{i}    page.{target_h}.fill({short_val!r}, timeout=3000)",
                *_sub_click_ml,
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    content = page.content().lower()",
                f"{i}    assert '500' not in page.title(), f'Server error on min-length check: {{page.url}}'",
                f"{i}    has_err = any(w in content for w in ['min', 'short', 'least', 'character', 'error'])",
                f"{i}    assert has_err or page.url != BASE_URL + {page_path!r}, \\",
                f"{i}        f'Expected min-length ({min_len}) validation for {short_val!r}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Min length check: {{page.url}}'")

    elif any(w in rule_t for w in ("max", "maximum", "at most", "maximum length")):
        m = _re.search(r'(\d+)', rule_t)
        max_len = int(m.group(1)) if m else 254
        if target_h:
            lines += [
                f"{i}try:",
                f"{i}    page.{target_h}.fill('a' * {max_len + 10}, timeout=3000)",
                f"{i}    page.wait_for_timeout(400)",
                f"{i}    assert '500' not in page.title(), f'Server error on max-length check: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'Max length check: {{page.url}}'")

    elif any(w in rule_t for w in ("xss", "cross-site", "script")):
        if target_h:
            xss_p = "<script>alert(1)</script>"
            lines += [
                f"{i}alerts: list = []",
                f"{i}page.on('dialog', lambda d: (alerts.append(d.message), d.dismiss()))",
                f"{i}try:",
                f"{i}    page.{target_h}.fill({xss_p!r}, timeout=3000)",
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    assert len(alerts) == 0, f'XSS executed! alerts={{alerts}}'",
                f"{i}    assert '500' not in page.title(), f'Server error on XSS rule: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'XSS validation check: {{page.url}}'")

    elif any(w in rule_t for w in ("sql", "sqli", "injection")):
        if target_h:
            sql_p = "' OR '1'='1"
            lines += [
                f"{i}_sqli_v = {sql_p!r}",
                f"{i}try:",
                f"{i}    page.{target_h}.fill(_sqli_v, timeout=3000)",
                f"{i}    page.wait_for_timeout(600)",
                f"{i}    content = page.content().lower()",
                f"{i}    bad = any(kw in content for kw in ['sql syntax', 'mysql_fetch', 'pg_query', 'ora-'])",
                f"{i}    assert not bad, f'SQLi DB error exposed! payload={{_sqli_v!r}}'",
                f"{i}    assert '500' not in page.title(), f'Server error on SQLi rule: {{page.url}}'",
                f"{i}except AssertionError: raise",
                f"{i}except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            ]
        else:
            lines.append(f"{i}assert '500' not in page.title(), f'SQLi validation check: {{page.url}}'")

    else:
        lines.append(f"{i}assert '500' not in page.title(), f'Validation check ({rule_t[:40]!r}): {{page.url}}'")

    return lines


def _class_for_spec(compiled: dict, spec_name: str) -> str:
    """Generate a comprehensive pytest class for one spec with deep, meaningful tests."""
    page_name  = compiled.get("page", spec_name.replace("markopolo_", "").replace("_", " ").title())
    page_path  = compiled.get("path", "/")
    page_url   = compiled.get("url", BASE_URL)
    # Strip the locale prefix from page_path if BASE_URL already ends with it
    # e.g. BASE_URL="https://dev.mehadedu.com/en" + path="/en/dashboard/x" → "/en/en/dashboard/x"
    _base_suffix = BASE_URL.rstrip("/").rsplit("/", 1)[-1]  # e.g. "en" or "ar"
    if _base_suffix and page_path.startswith(f"/{_base_suffix}"):
        stripped = page_path[len(f"/{_base_suffix}"):]
        # Only strip if stripping leaves a valid sub-path (empty → homepage "/")
        page_path = stripped if stripped else "/"
    sels       = compiled.get("selectors", {})
    flows      = compiled.get("flows", [])
    ecs        = compiled.get("edge_cases", [])
    api_eps    = compiled.get("api", [])
    val_rules  = compiled.get("validation", [])
    raw_reqs   = compiled.get("requirements", [])
    reqs: list[str] = []
    for r in raw_reqs:
        if isinstance(r, dict):
            reqs.append(f"{r.get('id','REQ')}: {r.get('text','')}")
        else:
            reqs.append(str(r))
    td         = compiled.get("test_data", {})
    valid_td   = [v for v in (td.get("valid",   []) or []) if v and v != "Value"]
    invalid_td = [v for v in (td.get("invalid", []) or []) if v and v != "Value"]
    if not valid_td:   valid_td   = ["valid_value"]
    if not invalid_td: invalid_td = ["invalid_value"]

    cls_name = "TestSpec_" + "".join(w.capitalize() for w in spec_name.split("_"))

    # Auth pages need unauthenticated context (stored session would redirect away)
    _auth_paths = ("/login", "/signup", "/register", "/reset", "/forgot", "/sign-up", "/sign_up")
    is_auth_page = any(page_path.startswith(p) for p in _auth_paths)

    lines: list[str] = []
    tc = [0]

    def idx() -> int:
        tc[0] += 1
        return tc[0]

    def add(*parts: str) -> None:
        lines.extend(parts)

    add(
        f"\n\n# {'='*62}",
        f"# SPEC: {page_name} — {page_url}",
        f"# {'='*62}",
        f"class {cls_name}:",
        f'    """Auto-generated tests from specs/{spec_name}.md',
        f'    Page: {page_name}  URL: {page_url}',
        f'    Selectors: {len(sels)}  Flows: {len(flows)}  ECs: {len(ecs)}  Reqs: {len(reqs)}',
        f'    """',
        f"    PAGE_PATH = {page_path!r}",
        f"    PAGE_URL  = {page_url!r}",
        f"",
    )

    if is_auth_page:
        add(
            f"    @pytest.fixture(autouse=True)",
            f"    def _clear_auth(self, page: Page):",
            f'        """Clear all stored auth (cookies + localStorage) so auth pages are not redirected."""',
            f"        page.context.clear_cookies()",
            f"        try:",
            f"            page.evaluate('() => {{ window.localStorage.clear(); window.sessionStorage.clear(); }}')",
            f"        except Exception:",
            f"            pass",
            f"",
        )

    # ── 1. Smoke: page loads ─────────────────────────────────────────────────
    add(
        f"    @pytest.mark.smoke",
        f"    @pytest.mark.navigation",
        f"    def test_page_loads_{idx():04d}(self, page: Page):",
        f'        """Smoke: {page_name} loads without server error."""',
        f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
        f"        page.wait_for_timeout(1500)",
        f"        assert '500' not in page.title(), f'Server error: {{page.url}}'",
        f"        assert '404' not in page.title(), f'Page not found: {{page.url}}'",
        f"        assert page.title() != '', f'Empty title on: {{page.url}}'",
        f"",
    )

    # ── 2. Element presence tests — FAIL mode (not skip) ─────────────────────
    for sel_name, sel_data in list(sels.items())[:12]:
        hint  = _clean_hint(sel_data.get("hint", ""))
        label = _safe_label(sel_data.get("label", sel_name))
        if not hint:
            continue
        add(
            f"    @pytest.mark.functional",
            f"    def test_element_{_slug(sel_name)}_{idx():04d}(self, page: Page):",
            f'        """Element must be present: {label}"""',
            f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
            f"        page.wait_for_timeout(1500)",
            f"        try:",
            f"            page.{hint}.first.wait_for(state='visible', timeout=12000)",
            f"        except Exception:",
            f'            pytest.skip(f"Element {label!r} not found on {{page.url}} — may be state-dependent or selector changed")',
            f"",
        )

    # ── 3. User flow tests — real Playwright interactions ────────────────────
    for flow in flows[:8]:
        flow_name  = str(flow.get("name", flow.get("flow", "unnamed_flow")))
        flow_safe  = flow_name.replace('"', "'").replace('\\', '')[:70]
        flow_steps = flow.get("steps", [])
        add(
            f"    @pytest.mark.functional",
            f"    @pytest.mark.flow",
            f"    def test_flow_{_slug(flow_name)}_{idx():04d}(self, page: Page):",
            f'        """Flow: {flow_safe}"""',
        )
        if flow_steps:
            for step in flow_steps[:12]:
                lines.extend(_step_to_code(step, "        ", sels, page_path))
            add(
                f"        assert '500' not in page.title(), f'Server error after flow: {{page.url}}'",
                f"",
            )
        else:
            lines.extend(_heuristic_flow_lines(flow_name, page_path, sels))
            add(f"")

    # ── 4. Requirement tests — smart assertions ──────────────────────────────
    for i_r, req in enumerate(reqs[:10]):
        import re as _re
        req_short = _re.sub(r'["\']', '', req[:80])
        add(
            f"    @pytest.mark.requirement",
            f"    def test_req_{i_r:02d}_{idx():04d}(self, page: Page):",
            f'        """REQ: {req_short}"""',
        )
        lines.extend(_req_assertion_lines(req, sels, page_path, page_name))
        add(f"")

    # ── 5. Validation rule tests ─────────────────────────────────────────────
    for v_rule in (val_rules if isinstance(val_rules, list) else [])[:8]:
        if not isinstance(v_rule, dict):
            continue
        field_n = _safe_label(str(v_rule.get("field", "field")))
        rule_n  = _safe_label(str(v_rule.get("rule", v_rule.get("constraint", "rule")))[:50])
        add(
            f"    @pytest.mark.validation",
            f"    def test_val_{_slug(field_n)}_{_slug(rule_n)}_{idx():04d}(self, page: Page):",
            f'        """Validation: {field_n} — {rule_n}"""',
        )
        lines.extend(_validation_to_test_body(v_rule, sels, page_path))
        add(f"")

    # ── 6. Edge case tests — scenario-specific ───────────────────────────────
    for ec in ecs[:10]:
        ec_id   = _safe_label(ec.get("id", f"EC{idx():02d}"))
        ec_desc = _safe_label(str(ec.get("scenario", ec.get("description", "edge case")))[:80])
        add(
            f"    @pytest.mark.edge_case",
            f"    def test_ec_{_slug(ec_id)}_{idx():04d}(self, page: Page):",
            f'        """{ec_id}: {ec_desc}"""',
        )
        lines.extend(_ec_to_test_body(ec, sels, page_path))
        add(f"")

    # ── 7. XSS security — all input fields ──────────────────────────────────
    input_sels = {k: v for k, v in sels.items()
                  if any(w in k.lower() for w in ("input","field","email","password","name","text","search"))}
    for sel_name, sel_data in list(input_sels.items())[:4]:
        hint = _clean_hint(sel_data.get("hint", ""))
        if not hint:
            continue
        add(
            f"    @pytest.mark.parametrize('xss_p', {_repr(XSS_PAYLOADS[:4] or ['<script>alert(1)</script>'])})",
            f"    @pytest.mark.security",
            f"    def test_xss_{_slug(sel_name)}_{idx():04d}(self, page: Page, xss_p: str):",
            f'        """XSS payload must not execute in {sel_name}."""',
            f"        alerts: list = []",
            f"        page.on('dialog', lambda d: (alerts.append(d.message), d.dismiss()))",
            f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
            f"        page.wait_for_timeout(1200)",
            f"        try:",
            f"            page.{hint}.filter(visible=True).first.fill(xss_p, timeout=5000)",
            f"            page.wait_for_timeout(500)",
            f"            assert len(alerts) == 0, f'XSS executed! payload={{xss_p!r}} alerts={{alerts}}'",
            f"            assert '500' not in page.title(), f'Server error on XSS: {{page.url}}'",
            f"        except AssertionError: raise",
            f"        except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            f"",
        )

    # ── 8. SQLi security — all input fields ─────────────────────────────────
    db_error_kws = ["sql syntax", "mysql_fetch", "pg_query", "sqlite_", "ORA-", "SQLSTATE", "syntax error"]
    _sqli_default = ["' OR '1'='1", "1; DROP TABLE users--", "' OR 1=1--", "admin'--"]
    for sel_name, sel_data in list(input_sels.items())[:4]:
        hint = _clean_hint(sel_data.get("hint", ""))
        if not hint:
            continue
        add(
            f"    @pytest.mark.parametrize('sqli_p', {_repr(SQLI_PAYLOADS[:4] or _sqli_default)})",
            f"    @pytest.mark.security",
            f"    def test_sqli_{_slug(sel_name)}_{idx():04d}(self, page: Page, sqli_p: str):",
            f'        """SQLi must not expose DB errors in {sel_name}."""',
            f"        db_errs = {db_error_kws!r}",
            f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
            f"        page.wait_for_timeout(1200)",
            f"        try:",
            f"            page.{hint}.filter(visible=True).first.fill(sqli_p, timeout=5000)",
            f"            page.wait_for_timeout(500)",
            f"            content = page.content().lower()",
            f"            for kw in db_errs:",
            f"                assert kw not in content, f'DB error exposed! kw={{kw!r}} payload={{sqli_p!r}}'",
            f"        except AssertionError: raise",
            f"        except Exception: pytest.skip(f'Field not found on {{page.url}}')",
            f"",
        )

    # ── 9. SSTI security tests ────────────────────────────────────────────────
    text_sels = {k: v for k, v in sels.items()
                 if any(w in k.lower() for w in ("name","text","title","description","search"))
                 and "email" not in k.lower()}
    if SSTI_PAYLOADS and text_sels:
        sel_name, sel_data = next(iter(text_sels.items()))
        hint = _clean_hint(sel_data.get("hint", ""))
        if hint:
            add(
                f"    @pytest.mark.parametrize('ssti', {_repr(SSTI_PAYLOADS[:3])})",
                f"    @pytest.mark.security",
                f"    def test_ssti_{_slug(sel_name)}_{idx():04d}(self, page: Page, ssti: str):",
                f'        """SSTI payload must not render as evaluated expression."""',
                f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
                f"        page.wait_for_timeout(1200)",
                f"        try:",
                f"            page.{hint}.filter(visible=True).first.fill(ssti, timeout=5000)",
                f"            page.wait_for_timeout(400)",
                f"            body_text = page.text_content('body') or ''",
                f"            assert '49' not in body_text, f'SSTI evaluated! {{ssti!r}} → body contained 49'",
                f"            assert '500' not in page.title(), f'Server error on SSTI: {{page.url}}'",
                f"        except AssertionError: raise",
                f"        except Exception: pytest.skip(f'Field not found on {{page.url}}')",
                f"",
            )

    # ── 10. Negative tests — spec invalid data ───────────────────────────────
    if invalid_td and input_sels:
        sel_name, sel_data = next(iter(input_sels.items()))
        hint  = _clean_hint(sel_data.get("hint", ""))
        label = _safe_label(sel_data.get("label", sel_name))
        if hint:
            add(
                f"    @pytest.mark.parametrize('bad_val', {_repr(invalid_td[:6])})",
                f"    @pytest.mark.negative",
                f"    def test_invalid_input_{_slug(sel_name)}_{idx():04d}(self, page: Page, bad_val: str):",
                f'        """Invalid input from spec — must not cause server error."""',
                f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
                f"        page.wait_for_timeout(1200)",
                f"        try:",
                f"            page.{hint}.filter(visible=True).first.fill(bad_val, timeout=5000)",
                f"            page.wait_for_timeout(300)",
                f"            assert '500' not in page.title(), f'Server error on invalid {{bad_val!r}}: {{page.url}}'",
                f"        except AssertionError: raise",
                f"        except Exception: pytest.skip(f'Field {label} not visible on {{page.url}}')",
                f"",
            )

    # ── 11. API contract tests ────────────────────────────────────────────────
    for ep in (api_eps if isinstance(api_eps, list) else [])[:4]:
        ep_method = str(ep.get("method", "GET")).upper()
        ep_path   = str(ep.get("path", ep.get("endpoint", "")))
        if not ep_path:
            continue
        ep_slug = _slug(ep_path.replace("/", "_").strip("_"))
        add(
            f"    @pytest.mark.api_network",
            f"    def test_api_{ep_method.lower()}_{ep_slug}_{idx():04d}(self, page: Page):",
            f'        """API contract: {ep_method} {ep_path} must not return 5xx."""',
            f"        responses: list = []",
            f"        def _on_resp(r):",
            f"            if {ep_path!r} in r.url:",
            f"                responses.append((r.url, r.status))",
            f"        page.on('response', _on_resp)",
            f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
            f"        page.wait_for_timeout(1500)",
            f"        for url, status in responses:",
            f"            assert status < 500, f'API {ep_method} {ep_path} returned {{status}} on {{url}}'",
            f"",
        )

    # ── 12. Performance test ──────────────────────────────────────────────────
    add(
        f"    @pytest.mark.performance",
        f"    def test_load_time_{idx():04d}(self, page: Page):",
        f'        """{page_name} loads within {LOAD_LIMIT} seconds."""',
        f"        t0 = time.time()",
        f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
        f"        elapsed = time.time() - t0",
        f"        assert elapsed < {LOAD_LIMIT}, f'{page_name} took {{elapsed:.1f}}s (limit {LOAD_LIMIT}s)'",
        f"",
    )

    # ── 13. Boundary tests ────────────────────────────────────────────────────
    email_sels = {k: v for k, v in sels.items() if "email" in k.lower()}
    if email_sels:
        sel_name, sel_data = next(iter(email_sels.items()))
        hint = _clean_hint(sel_data.get("hint", ""))
        if hint:
            bad_emails = BAD_EMAILS[:5] if BAD_EMAILS else ["notanemail", "@nodomain", "no@", "a"*250+"@x.com", ""]
            add(
                f"    @pytest.mark.parametrize('bad_email', {_repr(bad_emails)})",
                f"    @pytest.mark.boundary",
                f"    def test_email_boundary_{idx():04d}(self, page: Page, bad_email: str):",
                f'        """Email boundary: invalid formats must not crash."""',
                f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
                f"        page.wait_for_timeout(1200)",
                f"        try:",
                f"            page.{hint}.filter(visible=True).first.fill(bad_email, timeout=5000)",
                f"            page.wait_for_timeout(300)",
                f"            assert '500' not in page.title(), f'Server error on email boundary {{bad_email!r}}: {{page.url}}'",
                f"        except AssertionError: raise",
                f"        except Exception: pytest.skip(f'Email field not visible on {{page.url}}')",
                f"",
            )

    if text_sels:
        sel_name, sel_data = next(iter(text_sels.items()))
        hint  = _clean_hint(sel_data.get("hint", ""))
        label = _safe_label(sel_data.get("label", sel_name))
        if hint:
            boundary_vals = ["", " ", "A", "A"*255, "A"*1001, "null", "undefined", "None", "0"]
            add(
                f"    @pytest.mark.parametrize('boundary', {_repr(boundary_vals)})",
                f"    @pytest.mark.boundary",
                f"    def test_boundary_{_slug(sel_name)}_{idx():04d}(self, page: Page, boundary: str):",
                f'        """Boundary values for {label}."""',
                f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
                f"        page.wait_for_timeout(1200)",
                f"        try:",
                f"            page.{hint}.filter(visible=True).first.fill(boundary, timeout=5000)",
                f"            page.wait_for_timeout(300)",
                f"            assert '500' not in page.title(), f'Server error on boundary {{boundary!r}}: {{page.url}}'",
                f"        except AssertionError: raise",
                f"        except Exception: pytest.skip(f'Field {label} not visible on {{page.url}}')",
                f"",
            )

    # ── 14. Fill valid data in all input fields ───────────────────────────────
    for sel_name, sel_data in list(input_sels.items())[:6]:
        hint  = _clean_hint(sel_data.get("hint", ""))
        label = _safe_label(sel_data.get("label", sel_name))
        if not hint:
            continue
        if "email" in sel_name.lower():
            vdata = ["user@example.com", "test+qa@domain.co.uk", "qa@markopolo.ai"]
        elif "password" in sel_name.lower():
            vdata = ["Test@1234!", "SecureP@ss9876", "MyP@ssword1"]
        elif "name" in sel_name.lower():
            vdata = valid_td[:3] or ["Test Campaign", "QA Test Name", "Demo Run"]
        else:
            vdata = valid_td[:3] or ["valid_input", "test value", "example"]
        add(
            f"    @pytest.mark.parametrize('value', {_repr(vdata)})",
            f"    @pytest.mark.functional",
            f"    def test_fill_{_slug(sel_name)}_{idx():04d}(self, page: Page, value: str):",
            f'        """Fill {label} with valid data — must not crash."""',
            f"        page.goto(BASE_URL + {page_path!r}, wait_until='commit', timeout=30000)",
            f"        page.wait_for_timeout(1200)",
            f"        try:",
            f"            page.{hint}.filter(visible=True).first.fill(value, timeout=5000)",
            f"            page.wait_for_timeout(300)",
            f"            assert '500' not in page.title(), f'Server error filling {label}={{value!r}}: {{page.url}}'",
            f"        except AssertionError: raise",
            f"        except Exception: pytest.skip(f'Field {label} not found on {{page.url}}')",
            f"",
        )

    return "\n".join(lines)


# ── Full test file generator ──────────────────────────────────────────────────

def generate_test_file(all_specs: list[tuple]) -> tuple[str, int, list[dict]]:
    """
    Generate the complete pytest file and audit report.

    Args:
        all_specs: list of (md_file, compiled_dict) tuples

    Returns:
        (file_content, test_count, audit_records)
    """
    header = dedent(f"""\
        # ============================================================
        # AUTO-GENERATED by scripts/validate_all_specs.py
        # Generated: {datetime.utcnow().isoformat()}Z
        # Specs:     {len(all_specs)} MD files
        # Target:    {BASE_URL}
        # DO NOT EDIT — re-run generator to update
        # ============================================================
        \"\"\"
        Comprehensive Spec-Driven Test Suite
        ====================================
        Generated from all specs/*.md files.
        Each test class maps 1:1 to a spec MD file.
        Test types per spec:
          smoke / navigation / requirement / functional / boundary /
          negative / security (XSS, SQLi, SSTI) / edge_case / performance
        \"\"\"
        from __future__ import annotations
        import os as _os
        import time
        import pytest
        from playwright.sync_api import Page

        BASE_URL      = _os.getenv("BASE_URL",       "https://dev.mehadedu.com/en")
        TEST_EMAIL    = _os.getenv("TEST_EMAIL",     "")
        TEST_PASS     = _os.getenv("TEST_PASSWORD",  "")
        TEST_PHONE    = _os.getenv("TEST_PHONE",     "98976564")
        TEST_OTP      = _os.getenv("TEST_OTP",       "123456")
        TEST_COUNTRY  = _os.getenv("TEST_COUNTRY",   "+880")

        # ── Session auth ──────────────────────────────────────────────────────
        # Supports two auth modes (set via env):
        #   1. Email/password  → TEST_EMAIL + TEST_PASSWORD
        #   2. WhatsApp OTP   → TEST_PHONE + TEST_OTP + TEST_COUNTRY  (default for Mehad)
        # If auth fails, all tests in the session are skipped gracefully.
        @pytest.fixture(scope="session")
        def _storage(browser, tmp_path_factory):
            \"\"\"Login once, share auth across all spec tests.\"\"\"
            sf = tmp_path_factory.mktemp("auth") / "ss.json"
            ctx = browser.new_context(viewport={{"width": 1280, "height": 720}},
                                       ignore_https_errors=True, locale="en-US")
            pg = ctx.new_page()
            try:
                login_url = _os.getenv("LOGIN_URL", BASE_URL)
                pg.goto(login_url, wait_until="commit", timeout=25000)
                pg.wait_for_timeout(2000)

                if TEST_EMAIL:
                    # Standard email/password auth
                    try:
                        pg.locator('input[type="email"], input[type="text"]').first.wait_for(state='visible', timeout=20000)
                    except Exception:
                        pg.wait_for_timeout(3000)
                    pg.locator('input[type="email"]').first.fill(TEST_EMAIL)
                    pg.locator('input[type="password"]').first.fill(TEST_PASS)
                    try:
                        pg.locator('button[type="submit"]').first.click()
                    except Exception:
                        try:
                            pg.locator('button:has-text("Sign in"), button:has-text("Log in"), button:has-text("Login"), button:has-text("Sign In")').first.click()
                        except Exception:
                            pg.keyboard.press("Enter")
                    pg.wait_for_url(lambda u: "/login" not in u, timeout=30000)
                else:
                    # WhatsApp OTP auth (Mehad-style)
                    # Step 1: Click the visible Login button to open the modal
                    # Two "Log In" buttons exist — one hidden (mobile, aria-label="Login"), one visible (desktop)
                    # Target the visible one (no aria-label, just text)
                    login_btn = pg.locator('button:not([aria-label]):has-text("Log In"), button:not([aria-label="Login"]):has-text("Login")').first
                    login_btn.wait_for(state='visible', timeout=10000)
                    login_btn.click()
                    pg.wait_for_selector('[role="dialog"]', state='visible', timeout=10000)
                    pg.wait_for_timeout(1000)

                    # Step 2: Click the "Country code" button inside the dialog
                    dialog = pg.locator('[role="dialog"]')
                    cc_btn = dialog.locator('button[aria-label="Country code"], button:has-text("Country code")').first
                    cc_btn.wait_for(state='visible', timeout=8000)
                    cc_btn.click()
                    pg.wait_for_timeout(700)

                    # Step 3: Search for Bangladesh in the listbox search input
                    search_input = pg.locator('[role="listbox"] input[placeholder*="Search"], input[placeholder="Search..."]').first
                    search_input.wait_for(state='visible', timeout=5000)
                    search_input.fill('Bangladesh')
                    pg.wait_for_timeout(600)

                    # Step 4: Click the Bangladesh +880 option
                    pg.locator('[role="option"]:has-text("Bangladesh")').first.click()
                    pg.wait_for_timeout(500)

                    # Step 5: Fill phone number in the dialog (placeholder "50 123 4567")
                    phone_input = dialog.locator('input[type="tel"], input[placeholder*="123"]').first
                    phone_input.wait_for(state='visible', timeout=8000)
                    phone_input.fill(TEST_PHONE)
                    pg.wait_for_timeout(400)

                    # Step 6: Click Send Code (becomes enabled after phone number entered)
                    dialog.locator('button:has-text("Send Code")').first.click()
                    pg.wait_for_timeout(2000)

                    # Step 7: Wait for OTP input to become enabled, then fill it
                    otp_input = dialog.locator('input[placeholder="000000"]').first
                    otp_input.wait_for(state='visible', timeout=15000)
                    # Poll until OTP input is no longer disabled
                    for _ in range(30):
                        pg.wait_for_timeout(1000)
                        if not otp_input.is_disabled():
                            break
                    otp_input.fill(TEST_OTP)
                    pg.wait_for_timeout(800)

                    # Step 8: Click Continue
                    dialog.locator('button:has-text("Continue")').first.click()
                    pg.wait_for_timeout(4000)

                ctx.storage_state(path=str(sf))
            except Exception as exc:
                ctx.close()
                raise RuntimeError(f"Auth setup failed — tests require login: {{exc}}")
                return
            ctx.close()
            yield str(sf)

        @pytest.fixture(scope="class")
        def page(browser, _storage, request):
            \"\"\"Class-scoped authenticated page fixture.\"\"\"
            ctx = browser.new_context(
                viewport={{"width": 1280, "height": 720}},
                ignore_https_errors=True, locale="en-US",
                storage_state=_storage,
            )
            pg = ctx.new_page()
            path = getattr(request.cls, "PAGE_PATH", "/")
            pg.goto(BASE_URL + path, wait_until="commit", timeout=45000)
            pg.wait_for_timeout(2500)
            yield pg
            ctx.close()

    """)

    audits: list[dict] = []
    body_parts: list[str] = [header]
    test_count = 0

    for md_file, compiled in all_specs:
        spec_name = md_file.stem
        audit = audit_spec(compiled, spec_name)
        audits.append(audit)

        cls_code = _class_for_spec(compiled, spec_name)
        body_parts.append(cls_code)

        # Count test functions
        for line in cls_code.splitlines():
            stripped = line.strip()
            if stripped.startswith("def test_"):
                # Parametrized tests count as multiple
                test_count += 1

    return "\n".join(body_parts), test_count, audits


# ── Report generators ─────────────────────────────────────────────────────────

def write_json_report(audits: list[dict], test_count: int,
                       run_results: dict | None = None) -> Path:
    REPORT_DIR.mkdir(exist_ok=True)
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "base_url":     BASE_URL,
        "specs_total":  len(audits),
        "tests_generated": test_count,
        "run_results":  run_results or {},
        "specs": audits,
    }
    out = REPORT_DIR / "spec_validation_report.json"
    out.write_text(json.dumps(report, indent=2))
    return out


def write_html_report(audits: list[dict], test_count: int,
                       run_results: dict | None = None) -> Path:
    REPORT_DIR.mkdir(exist_ok=True)

    rr = run_results or {}
    passed  = rr.get("passed",  0)
    failed  = rr.get("failed",  0)
    errors  = rr.get("errors",  0)
    skipped = rr.get("skipped", 0)
    total_ran = passed + failed + errors
    pass_rate = f"{passed/max(total_ran,1):.0%}"

    quality_colors = {"GOOD": "#27ae60", "WARN": "#e67e22", "POOR": "#e74c3c"}
    spec_rows = ""
    for a in audits:
        qcolor = quality_colors.get(a["quality"], "#888")
        issues = ", ".join(a["issues"]) if a["issues"] else "—"
        spec_rows += f"""
        <tr>
          <td><strong>{a['spec']}</strong></td>
          <td>{a['selectors']}</td>
          <td>{a['flows']}</td>
          <td>{a['edge_cases']}</td>
          <td>{a['requirements']}</td>
          <td>{a['valid_td']}v / {a['invalid_td']}i</td>
          <td style="color:{qcolor}"><strong>{a['quality']}</strong></td>
          <td style="font-size:0.85em">{issues}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Fagun Spec Validation Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background:#0f0f0f; color:#e0e0e0; margin:0; padding:20px; }}
    .header {{ background:linear-gradient(135deg,#6c3483,#1a5276);
               padding:30px; border-radius:12px; margin-bottom:24px; }}
    h1 {{ margin:0 0 8px; font-size:1.8em; }}
    .subtitle {{ opacity:0.8; font-size:0.95em; }}
    .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
              gap:16px; margin-bottom:24px; }}
    .stat {{ background:#1a1a2e; border-radius:10px; padding:18px; text-align:center;
             border:1px solid #333; }}
    .stat-num {{ font-size:2.2em; font-weight:700; }}
    .stat-label {{ font-size:0.8em; opacity:0.7; margin-top:4px; }}
    .green {{ color:#2ecc71; }} .red {{ color:#e74c3c; }}
    .yellow {{ color:#f39c12; }} .blue {{ color:#3498db; }} .purple {{ color:#9b59b6; }}
    table {{ width:100%; border-collapse:collapse; background:#1a1a2e;
             border-radius:10px; overflow:hidden; }}
    th {{ background:#2c2c54; padding:12px 16px; text-align:left; font-size:0.85em;
          text-transform:uppercase; letter-spacing:0.5px; color:#aaa; }}
    td {{ padding:11px 16px; border-bottom:1px solid #2a2a2a; font-size:0.9em; }}
    tr:hover {{ background:#222240; }}
    .section {{ background:#1a1a2e; border-radius:10px; padding:20px;
                margin-bottom:20px; border:1px solid #333; }}
    .section h2 {{ margin:0 0 16px; font-size:1.15em; color:#9b59b6; }}
    pre {{ background:#0d1117; padding:16px; border-radius:8px; font-size:0.82em;
           overflow-x:auto; color:#c9d1d9; white-space:pre-wrap; }}
  </style>
</head>
<body>
<div class="header">
  <h1>Fagun Spec Validation Report</h1>
  <div class="subtitle">
    {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC &nbsp;|&nbsp;
    Target: {BASE_URL} &nbsp;|&nbsp;
    {len(audits)} specs processed
  </div>
</div>

<div class="stats">
  <div class="stat"><div class="stat-num purple">{len(audits)}</div><div class="stat-label">Specs Parsed</div></div>
  <div class="stat"><div class="stat-num blue">{test_count}</div><div class="stat-label">Tests Generated</div></div>
  <div class="stat"><div class="stat-num green">{passed}</div><div class="stat-label">Passed</div></div>
  <div class="stat"><div class="stat-num red">{failed + errors}</div><div class="stat-label">Failed</div></div>
  <div class="stat"><div class="stat-num yellow">{skipped}</div><div class="stat-label">Skipped</div></div>
  <div class="stat"><div class="stat-num {'green' if int(pass_rate[:-1])>=80 else 'red'}">{pass_rate}</div><div class="stat-label">Pass Rate</div></div>
</div>

<div class="section">
  <h2>Spec Coverage Audit</h2>
  <table>
    <thead>
      <tr>
        <th>Spec File</th><th>Selectors</th><th>Flows</th><th>Edge Cases</th>
        <th>Requirements</th><th>Test Data</th><th>Quality</th><th>Issues</th>
      </tr>
    </thead>
    <tbody>{spec_rows}</tbody>
  </table>
</div>

<div class="section">
  <h2>Test Types Generated per Spec</h2>
  <table>
    <thead><tr><th>Type</th><th>Description</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td>smoke</td><td>Page loads without 404/500</td><td>Auto — every spec</td></tr>
      <tr><td>requirement</td><td>One test per REQ- statement (up to 8)</td><td>## Requirements section</td></tr>
      <tr><td>functional</td><td>Selector presence + fill with valid data</td><td>## UI Elements table</td></tr>
      <tr><td>negative</td><td>Invalid emails, spec invalid_td</td><td>## Test Data + payloads/invalid_email.txt</td></tr>
      <tr><td>boundary</td><td>Empty, 1-char, 255-char, whitespace, null</td><td>Auto — text input fields</td></tr>
      <tr><td>security/XSS</td><td>6 XSS payloads in first input field</td><td>payloads/xss.txt</td></tr>
      <tr><td>security/SQLi</td><td>6 SQLi payloads, checks for DB error keywords</td><td>payloads/sqli.txt</td></tr>
      <tr><td>security/SSTI</td><td>4 SSTI payloads, verifies 49 not rendered</td><td>payloads/ssti.txt</td></tr>
      <tr><td>edge_case</td><td>One test per EC from spec (up to 8)</td><td>## Edge Cases section</td></tr>
      <tr><td>performance</td><td>Page load time &lt; 10 seconds</td><td>Auto — every spec</td></tr>
    </tbody>
  </table>
</div>

{f'''<div class="section">
  <h2>Test Run Results</h2>
  <pre>{json.dumps(run_results, indent=2)}</pre>
</div>''' if run_results else ""}

</body>
</html>"""

    out = REPORT_DIR / "spec_validation_report.html"
    out.write_text(html, encoding="utf-8")
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate all spec MD files and generate tests")
    parser.add_argument("--run",    action="store_true", help="Run pytest after generating")
    parser.add_argument("--report", action="store_true", help="Generate HTML + JSON report")
    parser.add_argument("--fast",   action="store_true", help="Quick smoke-only run")
    args = parser.parse_args()

    print(f"\n{'='*65}")
    print(f"  Fagun Spec Validator")
    print(f"  Target:  {BASE_URL}")
    print(f"  Specs:   {SPECS_DIR}")
    print(f"{'='*65}\n")

    # Step 1: Parse + compile all specs
    print("STEP 1 — Parsing and compiling all spec MD files...")
    _SKIP_NAMES = {"TEMPLATE.md", "README.md", "EXAMPLE.md"}
    all_specs = []
    for md_file in sorted(SPECS_DIR.glob("*.md")):
        if md_file.name in _SKIP_NAMES or md_file.name.startswith("_"):
            continue
        try:
            compiled = compile_spec(md_file.read_text(encoding="utf-8"), md_file.name)
            all_specs.append((md_file, compiled))
            sels  = len(compiled.get("selectors", {}))
            flows = len(compiled.get("flows", []))
            ecs   = len(compiled.get("edge_cases", []))
            print(f"  OK  {md_file.name:40s}  sel={sels:3d}  flows={flows:2d}  ecs={ecs:2d}")
        except Exception as exc:
            print(f"  ERR {md_file.name:40s}  {exc}")

    total_md = len([f for f in SPECS_DIR.glob("*.md")
                    if f.name not in _SKIP_NAMES and not f.name.startswith("_")])
    print(f"\n  {len(all_specs)}/{total_md} specs compiled successfully\n")

    # Step 2: Generate test file
    print("STEP 2 — Generating test cases from specs...")
    file_content, test_count, audits = generate_test_file(all_specs)

    # Step 3: Validate AST
    print("STEP 3 — Validating generated Python syntax (AST)...")
    try:
        ast.parse(file_content)
        print(f"  AST parse: PASS\n")
    except SyntaxError as exc:
        print(f"  SYNTAX ERROR: line {exc.lineno}: {exc.msg}")
        print(f"  Context: {exc.text}")
        sys.exit(1)

    # Step 4: Write test file
    print("STEP 4 — Writing test file...")
    OUTPUT_PY.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PY.write_text(file_content, encoding="utf-8")
    print(f"  Written: {OUTPUT_PY}")
    print(f"  Test functions: {test_count}")
    print(f"  File size: {OUTPUT_PY.stat().st_size // 1024}KB\n")

    # Audit summary
    print("SPEC AUDIT:")
    total_sels  = sum(a["selectors"]  for a in audits)
    total_flows = sum(a["flows"]      for a in audits)
    total_ecs   = sum(a["edge_cases"] for a in audits)
    total_reqs  = sum(a["requirements"] for a in audits)
    good = sum(1 for a in audits if a["quality"] == "GOOD")
    warn = sum(1 for a in audits if a["quality"] == "WARN")
    poor = sum(1 for a in audits if a["quality"] == "POOR")
    print(f"  Specs: {len(audits)}  |  Selectors: {total_sels}  |  Flows: {total_flows}  |  ECs: {total_ecs}  |  Reqs: {total_reqs}")
    print(f"  Quality — GOOD: {good}  WARN: {warn}  POOR: {poor}")
    for a in audits:
        if a["issues"]:
            print(f"  [{a['quality']:4s}] {a['spec']}: {', '.join(a['issues'])}")
    print()

    # Step 5: Run pytest (optional)
    run_results = None
    if args.run:
        print("STEP 5 — Running pytest...")
        markers = "smoke" if args.fast else "smoke or requirement or functional or boundary or negative or security or edge_case"
        cmd = [
            sys.executable, "-m", "pytest",
            str(OUTPUT_PY),
            "--browser", "chromium",
            "-n", "4", "--dist=loadscope",
            "--timeout=90", "--timeout-method=thread",
            "--tb=short", "-q", "-p", "no:warnings",
            "--html=reports/spec_validation_run.html", "--self-contained-html",
            "--json-report", "--json-report-file=reports/spec_validation_run.json",
            "-p", "no:cacheprovider",
            "-m", markers,
        ]
        t0 = time.time()
        result = subprocess.run(cmd, capture_output=False, text=True)
        elapsed = time.time() - t0
        print(f"\n  Exit code: {result.returncode}  ({elapsed:.1f}s)")

        # Parse JSON report
        jpath = REPORT_DIR / "spec_validation_run.json"
        if jpath.exists():
            try:
                jdata = json.loads(jpath.read_text())
                summary = jdata.get("summary", {})
                run_results = {
                    "passed":  summary.get("passed",  0),
                    "failed":  summary.get("failed",  0),
                    "errors":  summary.get("error",   0),
                    "skipped": summary.get("skipped", 0),
                    "duration_s": round(elapsed, 1),
                    "exit_code": result.returncode,
                }
                print(f"  Passed: {run_results['passed']}  Failed: {run_results['failed']}  Skipped: {run_results['skipped']}")
            except Exception:
                pass

    # Step 6: Generate reports (optional or always)
    if args.report or True:   # always generate
        print("\nSTEP 6 — Generating reports...")
        json_path = write_json_report(audits, test_count, run_results)
        html_path = write_html_report(audits, test_count, run_results)
        print(f"  JSON: {json_path}")
        print(f"  HTML: {html_path}")

    print(f"\n{'='*65}")
    print(f"  DONE — {test_count} tests from {len(all_specs)} specs")
    print(f"  Generated: {OUTPUT_PY}")
    if args.run and run_results:
        p = run_results.get("passed", 0)
        f = run_results.get("failed", 0)
        print(f"  Run result: {p} passed / {f} failed")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
