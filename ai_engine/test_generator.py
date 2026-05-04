"""
Generates tests for all 15 testing types from a parsed spec.
Each type produces a short, focused prompt → small token budget → no truncation.
"""

from __future__ import annotations
import os, sys
from pathlib import Path

# Allow import both as package and as script
try:
    from ai_engine.spec_parser import ParsedSpec
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_engine.spec_parser import ParsedSpec

BASE_URL = os.getenv("BASE_URL", "https://beta-stg.markopolo.ai")

# ── Shared AI caller (injected by agent.py) ───────────────────────────────────
_ai_call = None   # set by agent before use

def set_ai_caller(fn):
    global _ai_call
    _ai_call = fn

def _ai(prompt: str, max_tokens: int = 2500) -> str:
    if _ai_call is None:
        raise RuntimeError("Call set_ai_caller() before using test_generator")
    return _ai_call(prompt, max_tokens)


# ── Shared system context injected into every prompt ─────────────────────────
_RULES = f"""
PLAYWRIGHT PYTHON RULES (follow exactly):
- Output ONLY def test_...() functions. No imports. No module-level code.
- Every function signature: def test_NAME(page: Page):
- Navigation: page.goto(URL) then page.wait_for_load_state("networkidle")
- Selectors: get_by_role > get_by_label > get_by_placeholder > locator('input[type=...]')
- Assertions: expect(locator).to_be_visible() / expect(page).to_have_url() / expect(locator).to_contain_text()
- For unique email: f"qa_{{int(time.time())}}@mailinator.com"
- For passwords: os.getenv("TEST_PASSWORD", "Test@1234!")
- BASE_URL = os.getenv("BASE_URL", "{BASE_URL}")
- Keep every function under 20 lines. End every def completely — never leave open.
- No markdown. No prose. Functions only.
"""


# ─────────────────────────────────────────────────────────────────────────────
# 1. FUNCTIONAL — every user flow
# ─────────────────────────────────────────────────────────────────────────────
def functional(spec: ParsedSpec) -> str:
    if not spec.flows:
        return ""
    flows_text = ""
    for i, f in enumerate(spec.flows[:6], 1):
        steps = "\n  ".join(f["steps"][:6])
        flows_text += f"\nFLOW {i}: {f['name']}\n  {steps}\n"

    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write ONE pytest+Playwright test per user flow below.
Each test navigates to the page, performs the flow steps, and asserts the outcome.
{flows_text}
Write the test functions now:""", 3000)


# ─────────────────────────────────────────────────────────────────────────────
# 2. VALIDATION — form field rules
# ─────────────────────────────────────────────────────────────────────────────
def validation(spec: ParsedSpec) -> str:
    rules = "\n".join(f"  - {r}" for r in spec.validation_rules[:10])
    invalid = "\n".join(f"  {t}" for t in spec.test_data_invalid[:6])
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write validation tests. For EACH rule: test invalid input (assert error appears)
AND valid input (assert it passes).

RULES:
{rules}

INVALID TEST INPUTS:
{invalid}

Write the test functions now:""", 2500)


# ─────────────────────────────────────────────────────────────────────────────
# 3. NEGATIVE — wrong/bad inputs
# ─────────────────────────────────────────────────────────────────────────────
def negative(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write NEGATIVE tests — inputs that should be REJECTED.
Each test fills in a wrong value, submits, and asserts a user-facing error appears
(not a crash, not a 500, not a blank page).

Test cases to cover:
- Wrong/invalid credentials (if login page)
- Unregistered email
- Mismatched confirm password (if signup)
- Submitting empty form
- Each required field left empty one at a time

Write the test functions now:""", 2500)


# ─────────────────────────────────────────────────────────────────────────────
# 4. BOUNDARY — min/max/empty/overflow
# ─────────────────────────────────────────────────────────────────────────────
def boundary(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write BOUNDARY tests for form fields:
- Minimum valid length (e.g. password = 8 chars) → should pass
- One below minimum (7 chars) → should show error
- Maximum valid length (255 chars email) → should pass or graceful error
- Over maximum (300 chars) → graceful error, no crash
- Only spaces → should be rejected or trimmed
- Single character where minimum is 2 → rejected

For passwords use exact character counts, for emails construct long valid-format strings.
Write the test functions now:""", 2500)


# ─────────────────────────────────────────────────────────────────────────────
# 5. SECURITY — XSS, SQLi, injection
# ─────────────────────────────────────────────────────────────────────────────
def security(spec: ParsedSpec, xss_payloads: list[str], sqli_payloads: list[str]) -> str:
    xss_list  = "\n".join(f'    "{p}"' for p in xss_payloads[:6])
    sqli_list = "\n".join(f'    "{p}"' for p in sqli_payloads[:6])

    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}
PATH: {spec.path}

Write SECURITY tests for authorized testing of this application.

For each XSS payload: enter it in the email/name/input field, submit,
assert page.url does NOT change unexpectedly AND no alert dialog appears
AND the raw script is NOT visible as executed HTML.

For each SQLi payload: enter in email/password field, assert login FAILS
with a user-facing error (not a DB error, not a 500).

XSS payloads to test:
{xss_list}

SQLi payloads to test:
{sqli_list}

Use page.on("dialog", lambda d: d.dismiss()) to auto-dismiss any alerts (they are bugs).
Track if dialog fired with a flag. Assert the flag is False at the end.
Write the test functions now:""", 3000)


# ─────────────────────────────────────────────────────────────────────────────
# 6. API / NETWORK — request + response validation
# ─────────────────────────────────────────────────────────────────────────────
def api_network(spec: ParsedSpec) -> str:
    endpoints = "\n".join(
        f"  {e.get('method','POST')} {e.get('endpoint','')}"
        for e in spec.api_endpoints[:4]
    )
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write API/NETWORK tests using Playwright's request interception.
Use page.expect_request() or page.expect_response() context managers.

For each API call triggered by form submission:
1. Intercept the request → assert method is correct (POST/GET)
2. Intercept the response → assert status code (200, 201, 401, 409 as spec says)
3. Assert response body contains expected fields

API ENDPOINTS FROM SPEC:
{endpoints if endpoints else '  POST /api/auth/login or similar authentication endpoint'}

Example pattern:
  with page.expect_response(lambda r: "/api/" in r.url) as resp_info:
      page.click('button[type="submit"]')
  resp = resp_info.value
  assert resp.status in (200, 201, 401)

Write the test functions now:""", 2500)


# ─────────────────────────────────────────────────────────────────────────────
# 7. ACCESSIBILITY — ARIA, labels, keyboard, contrast
# ─────────────────────────────────────────────────────────────────────────────
def accessibility(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write ACCESSIBILITY tests:

1. test_all_inputs_have_labels: every input on the page has an associated <label>
   Use page.locator('input:not([type="hidden"])') and for each check get_by_label exists.

2. test_submit_button_accessible: submit button has accessible name
   expect(page.get_by_role("button", name=/.+/)).to_be_visible()

3. test_keyboard_navigation: tab through form fields in logical order
   page.keyboard.press("Tab") multiple times, check focus moves correctly.

4. test_no_axe_violations: inject axe-core and run scan
   Use:
     axe_script = page.evaluate("() => {{ ... }}")  # see pattern below
   Pattern to run axe via CDN:
     page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.0/axe.min.js")
     results = page.evaluate("async () => await axe.run()")
     violations = results.get("violations", [])
     assert len(violations) == 0, f"axe violations: {{violations}}"

5. test_error_messages_aria: after triggering error, check aria-describedby or role="alert"

Write the test functions now:""", 2500)


# ─────────────────────────────────────────────────────────────────────────────
# 8. RESPONSIVE — 375px, 768px, 1280px
# ─────────────────────────────────────────────────────────────────────────────
def responsive(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write RESPONSIVE tests at 3 viewports.
For each: set viewport, navigate, assert key form elements are visible and not overlapping.

def test_mobile_375(page: Page):
    page.set_viewport_size({{"width": 375, "height": 667}})
    ...

def test_tablet_768(page: Page):
    page.set_viewport_size({{"width": 768, "height": 1024}})
    ...

def test_desktop_1280(page: Page):
    page.set_viewport_size({{"width": 1280, "height": 720}})
    ...

For each viewport assert:
- Email input is visible
- Password input is visible
- Submit button is visible and clickable (not hidden behind keyboard)
- No horizontal scrollbar (page width == viewport width)

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 9. NAVIGATION — internal links
# ─────────────────────────────────────────────────────────────────────────────
def navigation(spec: ParsedSpec) -> str:
    related = spec.raw[spec.raw.find("## Related"):spec.raw.find("## Related")+400] \
              if "## Related" in spec.raw else ""
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write NAVIGATION tests for all internal links on this page.
For each link: click it, assert the URL changes to the expected destination,
assert the new page loaded (wait_for_load_state).

Links that typically exist on {spec.page_name}:
- "Forgot Password" → /reset-pass
- "Sign Up" / "Create account" → /signup
- "Log In" / "Back to Login" → /login
- Logo/brand link → home page

RELATED PAGES FROM SPEC:
{related[:300]}

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 10. SESSION / AUTH — token, redirect, already-logged-in
# ─────────────────────────────────────────────────────────────────────────────
def session_auth(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write SESSION/AUTH tests:

1. test_already_authenticated_redirected: if storage_state has auth token,
   visiting /login should redirect away. Use page.context.add_cookies() or
   page.evaluate("localStorage.setItem('token','fake')") then navigate.
   Assert page.url does NOT contain "/login".

2. test_protected_route_redirects_to_login: navigate to /dashboard (or any
   protected page) without auth, assert redirect to /login.

3. test_session_storage_cleared_on_bad_login: after failed login attempt,
   assert no auth token in localStorage.
   After page.click(submit), page.evaluate("localStorage.getItem('token')")
   should return None or empty string.

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 11. PERFORMANCE — page load timing
# ─────────────────────────────────────────────────────────────────────────────
def performance(spec: ParsedSpec) -> str:
    js_timing = "() => { const t = window.performance.timing; return { dom: t.domContentLoadedEventEnd - t.navigationStart, load: t.loadEventEnd - t.navigationStart, ttfb: t.responseStart - t.navigationStart }; }"
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write 3 PERFORMANCE tests:

1. test_page_load_under_3s: time page.goto() + wait_for_load_state, assert elapsed < 3000ms
2. test_dom_content_loaded_fast: use page.evaluate() with JS timing API, assert DOMContentLoaded < 2000ms
   JS snippet to use: '{js_timing}'
3. test_no_large_blocking_resources: page.on("response") to collect script/stylesheet sizes > 500KB,
   assert none found

Keep each function under 20 lines. Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 12. CONSOLE ERRORS — no JS errors on normal usage
# ─────────────────────────────────────────────────────────────────────────────
def console_errors(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write CONSOLE ERROR tests. Use page.on("console") to capture errors.

def test_no_console_errors_on_load(page: Page):
    errors = []
    page.on("console", lambda msg: errors.append(msg.text)
            if msg.type == "error" else None)
    page.goto("{spec.url}")
    page.wait_for_load_state("networkidle")
    assert errors == [], f"Console errors on load: {{errors}}"

def test_no_console_errors_on_form_interaction(page: Page):
    errors = []
    page.on("console", lambda msg: errors.append(msg.text)
            if msg.type == "error" else None)
    page.goto("{spec.url}")
    page.wait_for_load_state("networkidle")
    # Interact with form
    try:
        page.locator('input[type="email"]').fill("test@example.com")
        page.locator('input[type="password"]').fill("Test@1234!")
    except Exception:
        pass
    assert errors == [], f"Console errors during interaction: {{errors}}"

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 13. ERROR STATE — graceful errors, no stack traces exposed
# ─────────────────────────────────────────────────────────────────────────────
def error_states(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write ERROR STATE tests:

1. test_no_stack_trace_exposed: after any failed action, assert the page
   does NOT contain common error strings: "Traceback", "Exception", "at Object.",
   "Internal Server Error", "undefined is not", "Cannot read property"

2. test_network_error_handled: use page.route() to abort an API request
   and assert a friendly user message appears (not a blank page):
   page.route("**/api/**", lambda r: r.abort())
   then trigger form submission — assert some visible error text appears.

3. test_404_not_shown_to_user: navigate to a non-existent sub-path,
   assert the application shows a proper error page (not raw Nginx/Apache 404).

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 14. VISUAL / LAYOUT — no broken layout
# ─────────────────────────────────────────────────────────────────────────────
def visual(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write VISUAL/LAYOUT tests (no screenshot comparison, use DOM assertions):

1. test_form_elements_within_viewport: assert all form inputs have
   bounding box within viewport width. No element should overflow horizontally.
   box = page.locator('form').bounding_box()
   assert box["x"] >= 0 and (box["x"] + box["width"]) <= page.viewport_size["width"]

2. test_no_overlapping_elements: check submit button and first input
   don't have identical bounding boxes (overlap check).

3. test_page_title_set: assert page.title() is not empty and not "undefined".

4. test_favicon_loads: assert response to favicon request is 200.
   with page.expect_response("**favicon**") as r:
       page.goto("{spec.url}")
   assert r.value.status == 200

Write the test functions now:""", 2000)


# ─────────────────────────────────────────────────────────────────────────────
# 15. CROSS-BROWSER MARKERS — tag tests to run on multiple browsers
# ─────────────────────────────────────────────────────────────────────────────
def cross_browser(spec: ParsedSpec) -> str:
    return _ai(f"""{_RULES}
PAGE: {spec.page_name}  URL: {spec.url}

Write 2 CROSS-BROWSER smoke tests tagged with @pytest.mark.parametrize
so they run on multiple browsers. These are smoke tests only — does the
page load and is the submit button visible?

Use @pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
but DO NOT include browser_name in the test signature — just write normal (page: Page) tests.
Tag them so testers know these are cross-browser candidates.

Write just 2 short functions tagged with a comment # cross-browser smoke:""", 1500)


# ─────────────────────────────────────────────────────────────────────────────
# Master runner — all 15 types
# ─────────────────────────────────────────────────────────────────────────────

ALL_TYPES = [
    ("functional",    functional),
    ("validation",    validation),
    ("negative",      negative),
    ("boundary",      boundary),
    ("api_network",   api_network),
    ("accessibility", accessibility),
    ("responsive",    responsive),
    ("navigation",    navigation),
    ("session_auth",  session_auth),
    ("performance",   performance),
    ("console_errors",console_errors),
    ("error_states",  error_states),
    ("visual",        visual),
    ("cross_browser", cross_browser),
]


def generate_all(spec: ParsedSpec,
                 xss_payloads: list[str] | None = None,
                 sqli_payloads: list[str] | None = None) -> dict[str, str]:
    """
    Returns {type_name: function_code_string} for every test type.
    Each value contains only def test_...() blocks (no imports).
    """
    xss  = xss_payloads  or []
    sqli = sqli_payloads or []
    results: dict[str, str] = {}

    for name, fn in ALL_TYPES:
        try:
            if name == "security":
                code = security(spec, xss, sqli)
            else:
                code = fn(spec)
            results[name] = code or ""
        except Exception as e:
            results[name] = ""
            print(f"  [GEN:{name}] error: {e}", flush=True)

    # Security is separate — call it explicitly
    results["security"] = security(spec, xss, sqli)

    return results
