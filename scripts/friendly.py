"""
Friendly translator + test-docstring extractor for the QA bug report.

Turns cryptic Playwright/pytest errors into plain English so non-engineers
can read the bug report. Also extracts test docstrings so passed tests can
show the user "what was checked" in human terms.

Used by scripts/consolidate_reports.py.
"""
from __future__ import annotations
import ast, re
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 1. Friendly error translation
# ─────────────────────────────────────────────────────────────────────────────

# Each rule: (regex pattern → human-readable plain-English explanation).
# Rules are tried in order; first match wins. The text is shown as the
# "Actual Behavior (Bug)" line in the report.
_ERROR_RULES: list[tuple[re.Pattern, str]] = [
    # — Playwright timeouts —
    (re.compile(r"Locator\.fill: Timeout (\d+)ms exceeded", re.I),
     "The test tried to type into a field, but the field was not enabled "
     "within {0}ms. The page may be slow, the field is disabled, or the "
     "wrong element was matched."),
    (re.compile(r"Locator\.click: Timeout (\d+)ms exceeded", re.I),
     "The test tried to click a button, but the button never became clickable "
     "within {0}ms. Often this means the button is hidden or covered by another "
     "element."),
    (re.compile(r"Locator\.wait_for: Timeout (\d+)ms exceeded", re.I),
     "The test waited for an element to appear, but it never showed up within "
     "{0}ms. The element may not exist on the page, or the page is loading "
     "very slowly."),
    (re.compile(r"Page\.wait_for_selector: Timeout (\d+)ms exceeded", re.I),
     "The test waited for an element to appear on the page, but it never "
     "appeared within {0}ms."),
    (re.compile(r"page\.goto: Timeout (\d+)ms exceeded", re.I),
     "The test could not load the page within {0}ms — the server is too slow "
     "or unreachable."),
    (re.compile(r'Expect ".*to_be_visible.*" with timeout (\d+)ms', re.I),
     "An element that should have been visible on the page was not visible "
     "within {0}ms."),
    (re.compile(r'Expect ".*to_be_enabled.*" with timeout', re.I),
     "An element that should have been clickable was disabled."),
    (re.compile(r'Expect ".*to_have_url.*" with timeout', re.I),
     "The page did not navigate to the URL the test expected."),
    (re.compile(r'Expect ".*to_have_text.*" with timeout', re.I),
     "An element on the page did not contain the text the test expected."),

    # — Network / response —
    (re.compile(r"Status code (\d{3})", re.I),
     "The server returned HTTP error {0} instead of a normal response."),
    (re.compile(r"net::ERR_INTERNET_DISCONNECTED", re.I),
     "The browser lost its internet connection during the test."),
    (re.compile(r"net::ERR_CONNECTION_REFUSED", re.I),
     "The browser could not reach the server (connection refused)."),

    # — Common assertion patterns — single-line capture only, no DOTALL
    (re.compile(r"AssertionError:\s*([^\n]+)"),
     "{0}"),  # passthrough — the assertion message author already wrote it cleanly

    # — JavaScript runtime errors —
    (re.compile(r"pageerror.*?:\s*(.+)", re.I),
     "The page itself threw a JavaScript error: {0}"),

    # — Catch-all —
    (re.compile(r"playwright\._impl\._errors\.(\w+):\s*(.+)", re.S),
     "Browser automation error ({0}): {1}"),
]


def _clean_pytest_lines(text: str) -> str:
    """Strip pytest's leading 'E ' / 'E   ' indicator from each line so we
    can pattern-match the real error message cleanly."""
    cleaned = []
    for line in (text or "").splitlines():
        # Pytest prefixes failure lines with 'E ' or 'E   '
        cleaned.append(re.sub(r"^E\s{1,3}", "", line))
    return "\n".join(cleaned)


def friendly_actual(error_msg: str, traceback: str) -> str:
    """Translate the failure signal into a single plain-English sentence."""
    haystack = _clean_pytest_lines((error_msg or "") + "\n" + (traceback or ""))[:4000]
    for pattern, template in _ERROR_RULES:
        m = pattern.search(haystack)
        if m:
            try:
                args = [(g or "").strip() for g in m.groups()]
                # If template is a passthrough ({0}), trim the captured text
                # to the meaningful part (drop pytest 'where ...' debug lines).
                if template == "{0}":
                    msg = args[0] if args else ""
                    msg = msg.split("\nE ")[0]   # stop at next 'E ' detail
                    msg = re.split(r"\s+\+\s+where\s+", msg)[0]  # drop "+ where x = ..."
                    return msg.strip()[:300]
                return template.format(*args).strip()
            except Exception:
                return template
    # Fallback — first non-trivial line
    for line in (error_msg or "").splitlines():
        s = re.sub(r"^E\s{1,3}", "", line).strip()
        if s and len(s) > 5 and "..." not in s:
            return s[:300]
    return "The test failed — see the error details below for the raw output."


def friendly_expected(test_name: str, docstring: str) -> str:
    """Generate a plain-English 'expected behavior' from the test name + docstring."""
    if docstring:
        ds = docstring.strip().splitlines()[0].strip()
        if ds:
            return ds
    # Synthesize from test name
    nm = test_name.replace("test_", "").replace("_", " ")
    nm = re.sub(r"\bqa\d+ ", "", nm, flags=re.I)
    nm = nm[0].upper() + nm[1:] if nm else "The test"
    return f"{nm} should work correctly."


def friendly_description(test_name: str, docstring: str, page_url: str) -> str:
    """Generate a plain-English description of WHAT was being tested."""
    if docstring:
        # Use the docstring as the description — it's usually already friendly
        ds = docstring.strip()
        if ds:
            # Strip the trailing period if present, then add context
            return f"{ds.rstrip('.')} — verified against {page_url or 'the staging site'}."
    # Synthesize from test name
    pretty = test_name.replace("test_", "").replace("_", " ")
    pretty = re.sub(r"\bqa\d+ ", "", pretty, flags=re.I)
    pretty = pretty[0].upper() + pretty[1:] if pretty else "Test"
    target = page_url or "the staging site"
    return (f"This test verifies that '{pretty}' works correctly on {target}. "
            f"It failed during the most recent CI run.")


def friendly_steps(test_name: str, docstring: str, page_url: str,
                   parametrize_id: str = "") -> list[str]:
    """Build step-by-step instructions a manual tester can follow."""
    target = page_url or "the test URL"
    nm = test_name.replace("test_", "").replace("_", " ")
    steps = [f"Open a browser and go to {target}"]
    # Hints from common test name patterns
    nl = test_name.lower()
    if "login" in nl or "modal" in nl:
        steps.append("Click the 'Log In' button in the page header")
    if "phone" in nl or "otp" in nl or "send_code" in nl:
        steps.append("Enter a phone number in the WhatsApp number field")
    if "send_code" in nl:
        steps.append("Click the 'Send Code' button")
    if "otp" in nl and "input" in nl:
        steps.append("Enter the OTP code that arrives via WhatsApp")
    if "search" in nl:
        steps.append("Use the search field on the page")
    if "navigation" in nl or "navigate" in nl:
        steps.append("Click the navigation link being tested")
    if "submit" in nl:
        steps.append("Click the submit button")
    if "rtl" in nl or "arabic" in nl or "i18n" in nl:
        steps.append("Switch the page language to Arabic (or load /ar)")
    if "mobile" in nl or "responsive" in nl:
        steps.append("Open the page on a mobile-sized viewport (≤ 414px wide)")
    if parametrize_id:
        steps.append(f"Use these parameters: {parametrize_id}")
    steps.append("Observe the result: it does NOT match what the test expected (see Actual Behavior)")
    return steps[:6]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Test docstring extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_docstrings(test_files: list[Path]) -> dict[str, str]:
    """Parse Python test files and return {function_name: docstring}.

    Walks each file's AST and pulls the first-line docstring of every
    function whose name starts with `test_`. Used to give passed tests a
    human-readable label."""
    out: dict[str, str] = {}
    for tf in test_files:
        try:
            src = tf.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:
            continue
        # Walk top-level functions AND class-method functions
        nodes_to_check = list(ast.walk(tree))
        for node in nodes_to_check:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("test_"):
                    continue
                ds = ast.get_docstring(node) or ""
                if ds:
                    out[node.name] = ds.strip()
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 3. Test data extraction (from parametrize ID like [chromium-foo-bar])
# ─────────────────────────────────────────────────────────────────────────────

def parse_parametrize_id(nodeid: str) -> str:
    """Extract the parametrize values from a pytest nodeid.

    `tests/x.py::TestY::test_z[chromium-foo-bar]` → 'foo, bar'
    `tests/x.py::test_z[chromium]` → '' (no params, only browser)
    """
    m = re.search(r"\[([^\]]+)\]$", nodeid)
    if not m:
        return ""
    parts = [p for p in m.group(1).split("-") if p and p.lower() != "chromium"]
    return ", ".join(parts) if parts else ""


# ─────────────────────────────────────────────────────────────────────────────
# 4. Passed-test summary builder
# ─────────────────────────────────────────────────────────────────────────────

def build_passed_test_entry(nodeid: str, duration: float,
                             docstring_map: dict[str, str]) -> dict:
    """Return one passed-test record for the report."""
    fn_name = nodeid.split("::")[-1].split("[")[0]
    return {
        "name":      fn_name,
        "nodeid":    nodeid,
        "duration":  duration,
        "docstring": docstring_map.get(fn_name, ""),
        "params":    parse_parametrize_id(nodeid),
    }
