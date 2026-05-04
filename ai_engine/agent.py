"""
Markopolo Autonomous AI Test Agent
------------------------------------
No API keys. No manual scripts. No hardcoded selectors.
The AI reads MD specs, thinks, plans, generates, executes, fixes, and reports.

Local:  python ai_engine/agent.py
CI/CD:  Triggered automatically on push via GitHub Actions
"""

import os
import sys
import json
import ast
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime

import ollama

# ── Configuration ────────────────────────────────────────────────────────────
BASE_URL   = os.getenv("BASE_URL",  "https://beta-stg.markopolo.ai")
AI_MODEL   = os.getenv("AI_MODEL",  "qwen2.5-coder:1.5b")
SPECS_DIR  = Path("specs")
TESTS_DIR  = Path("tests")
REPORTS_DIR = Path("reports")
MAX_GEN_RETRIES = 3
MAX_FIX_RETRIES = 2

# ── System Prompt ─────────────────────────────────────────────────────────────
# This is the "intelligence" — what the AI knows about how to test
SYSTEM_PROMPT = """You are a world-class QA automation engineer. You write Playwright (Python/pytest) tests.

WHAT YOU KNOW:
- You understand web application testing deeply: UI flows, API contracts, validation rules, security
- You know how to find bugs that manual testers miss: timing issues, race conditions, edge inputs
- You know that good tests are independent, deterministic, and meaningful — not just happy-path coverage

PLAYWRIGHT RULES YOU ALWAYS FOLLOW:
1. Imports at top: import os, import time, import pytest, from playwright.sync_api import Page, expect
2. BASE_URL = os.getenv("BASE_URL", "https://beta-stg.markopolo.ai")
3. Test functions start with test_
4. Use pytest `page: Page` fixture (built-in from pytest-playwright)
5. Navigation: page.goto(url) then page.wait_for_load_state("networkidle")
6. Selectors priority (best → worst):
   page.get_by_role("button", name="Sign in")
   page.get_by_label("Email")
   page.get_by_placeholder("Enter your email")
   page.locator('input[type="email"]')
   page.locator('[data-testid="email"]')
7. Assertions: expect(locator).to_be_visible(), expect(page).to_have_url(), expect(locator).to_contain_text()
8. Waits: page.wait_for_load_state(), expect(locator).to_be_visible(timeout=10000)
9. For unique emails in tests: f"qa_{int(time.time())}@mailinator.com"
10. Each test cleans up after itself — no shared state

TEST TYPES YOU GENERATE:
- Functional: every user flow, every button, every link
- Validation: empty fields, format errors, length limits, required fields
- Edge Cases: special chars, XSS strings, SQL strings, very long inputs, spaces-only
- Security: XSS in inputs, SQL injection — verify they don't crash and show safe errors
- Navigation: all internal links lead to correct pages
- Error States: wrong credentials, network errors, expired tokens
- Accessibility: labels exist, tab order is logical, aria attributes present
- Responsive: test at 375px (mobile) viewport

OUTPUT FORMAT:
- Output ONLY valid Python code
- No markdown fences (no ```python blocks)
- No explanation text before or after the code
- Every function must have a clear docstring of ONE sentence max
"""

# ── AI Thinking ───────────────────────────────────────────────────────────────

def ai_think(prompt: str, context: str = "") -> str:
    """Call Ollama locally — zero API keys, zero cost, fully private."""
    full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}" if context else prompt
    try:
        response = ollama.chat(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": full_prompt},
            ],
            options={"temperature": 0.05, "num_predict": 4096},
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"  [AI ERROR] Ollama call failed: {e}")
        return ""


def clean_code(raw: str) -> str:
    """Strip markdown fences and leading/trailing whitespace from AI output."""
    raw = raw.strip()
    # Remove ```python or ``` fences
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()


def is_valid_python(code: str) -> tuple[bool, str]:
    """Return (is_valid, error_message)."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError line {e.lineno}: {e.msg}"


# ── Test Generation ───────────────────────────────────────────────────────────

def build_generation_prompt(spec_content: str, page_name: str) -> str:
    return f"""
Read the following specification for the "{page_name}" page.
Generate a COMPLETE pytest + Playwright test file.

REQUIRED COVERAGE (do not skip any):
1. ALL User Flows listed in the spec — every numbered step
2. ALL Edge Cases listed in the Edge Cases table — every EC-XX row
3. ALL Validation Rules — test both valid and invalid inputs for each rule
4. ALL Error States — verify correct error messages appear
5. ALL Navigation links — verify each link reaches the correct URL
6. Security inputs from Test Data section — verify safe handling
7. At least one mobile viewport test (375px wide) using page.set_viewport_size

IMPORTANT NOTES:
- For tests that need a real account (e.g. login), use placeholder credentials and mark with @pytest.mark.skip if credentials are unknown
- For signup tests, always generate unique emails using: f"qa_{{int(time.time())}}@mailinator.com"
- Never hardcode passwords — use: os.getenv("TEST_PASSWORD", "Test@1234!")
- If the page redirects after success, assert the new URL
- Every test must be completely independent

SPECIFICATION:
{spec_content}

Write the complete test file now. Python code only, no explanation.
"""


def build_fix_prompt(test_code: str, failure_output: str) -> str:
    return f"""
The following Playwright tests have failures. Analyze each failure and fix the root cause.

FAILURE REASONS TO CHECK:
1. Wrong selector → switch to a more flexible one (role > label > placeholder > CSS)
2. Element not visible yet → add expect(locator).to_be_visible(timeout=15000) before interacting
3. Wrong URL → double-check BASE_URL usage
4. Wrong assertion text → update to match what the app actually shows
5. Timeout → slow network, add wait_for_load_state("networkidle") after navigation
6. Test order dependency → make each test navigate fresh

FAILED TEST CODE:
{test_code}

FAILURE OUTPUT:
{failure_output[:3000]}

Rewrite the COMPLETE test file with ALL fixes applied. Python code only.
"""


def generate_test_file(spec_path: Path) -> str | None:
    """AI generates a test file from a spec. Returns valid Python code or None."""
    spec_content = spec_path.read_text()
    page_name = spec_path.stem
    prompt = build_generation_prompt(spec_content, page_name)

    for attempt in range(1, MAX_GEN_RETRIES + 1):
        print(f"    [GENERATE] Attempt {attempt}/{MAX_GEN_RETRIES}...")
        raw = ai_think(prompt)
        code = clean_code(raw)

        if not code:
            print(f"    [GENERATE] Empty response, retrying...")
            continue

        valid, err = is_valid_python(code)
        if valid:
            print(f"    [GENERATE] ✅ Valid Python generated ({len(code.splitlines())} lines)")
            return code
        else:
            print(f"    [GENERATE] ❌ Syntax error: {err}")
            # Ask AI to fix syntax
            prompt = f"Fix the Python syntax error in this code.\nError: {err}\n\nCode:\n{code}\n\nReturn corrected code only."

    return None


def fix_test_file(test_code: str, failure_output: str) -> str | None:
    """AI rewrites tests to fix failures. Returns valid Python or None."""
    prompt = build_fix_prompt(test_code, failure_output)

    for attempt in range(1, MAX_FIX_RETRIES + 1):
        print(f"    [FIX] Fix attempt {attempt}/{MAX_FIX_RETRIES}...")
        raw = ai_think(prompt)
        code = clean_code(raw)

        valid, err = is_valid_python(code)
        if valid:
            print(f"    [FIX] ✅ Fixed code generated")
            return code
        else:
            print(f"    [FIX] ❌ Fix attempt had syntax error: {err}")

    return None


# ── Test Execution ────────────────────────────────────────────────────────────

def run_tests(test_file: Path) -> dict:
    """Execute pytest and return structured results."""
    json_report = REPORTS_DIR / f"result_{test_file.stem}.json"
    html_report = REPORTS_DIR / f"result_{test_file.stem}.html"

    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--no-header",
        "--json-report",
        f"--json-report-file={json_report}",
        f"--html={html_report}",
        "--self-contained-html",
        "--timeout=60",
    ]

    env = os.environ.copy()
    env["BASE_URL"] = BASE_URL
    env["PWDEBUG"] = "0"

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, env=env, timeout=600
        )
        output = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "total": 0, "passed": 0, "failed": 1,
                "output": "Test execution timed out after 600s", "returncode": -1}

    passed = failed = total = 0

    if json_report.exists():
        try:
            data = json.loads(json_report.read_text())
            s = data.get("summary", {})
            passed = s.get("passed", 0)
            failed = s.get("failed", 0) + s.get("error", 0)
            total  = s.get("total", 0)
        except Exception:
            pass

    # Fallback parse from stdout
    if total == 0:
        for line in output.splitlines():
            nums = re.findall(r"(\d+) (passed|failed|error)", line)
            for num, status in nums:
                if status == "passed":    passed = int(num)
                elif status in ("failed", "error"): failed += int(num)
            total = passed + failed

    return {
        "status": "passed" if proc.returncode == 0 else "failed",
        "total":  total,
        "passed": passed,
        "failed": failed,
        "output": output,
        "html_report": str(html_report),
        "returncode": proc.returncode,
    }


# ── Gap Detection ─────────────────────────────────────────────────────────────

def detect_gaps(spec_content: str, test_code: str, results: dict) -> str:
    """AI identifies what the generated tests missed."""
    prompt = f"""
You are a senior QA engineer reviewing test coverage.
Compare the specification requirements against the actual test code and execution results.

FIND ALL GAPS — things that should be tested but are NOT in the test code:
1. User flows not covered
2. Edge cases from the spec not tested
3. Validation rules not verified
4. Error states not asserted
5. Security scenarios missing
6. Accessibility not checked

FORMAT your response as a bullet list:
- [MISSING] <what> — <why it matters> — <how to test it>

SPECIFICATION:
{spec_content[:3000]}

TEST CODE WRITTEN:
{test_code[:2000]}

TEST RESULTS:
Passed: {results.get('passed', 0)}, Failed: {results.get('failed', 0)}, Total: {results.get('total', 0)}

List every gap you find. Be specific.
"""
    return ai_think(prompt)


# ── Main Agent ────────────────────────────────────────────────────────────────

class AutonomousTestAgent:

    def __init__(self):
        self.all_results: dict[str, dict] = {}
        TESTS_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)

    def run(self):
        self._print_banner()
        specs = sorted(SPECS_DIR.glob("*.md"))
        if not specs:
            print("[ERROR] No .md spec files found in specs/")
            sys.exit(1)

        for spec_path in specs:
            self._process_spec(spec_path)

        self._final_summary()

    # ── Per-spec pipeline ─────────────────────────────────────────────────────

    def _process_spec(self, spec_path: Path):
        page_name = spec_path.stem
        print(f"\n{'━'*60}")
        print(f"  SPEC: {spec_path.name}")
        print(f"{'━'*60}")

        spec_content = spec_path.read_text()
        test_file = TESTS_DIR / f"test_{page_name.replace('-', '_')}.py"

        # ── Phase 1: Think + Generate ─────────────────────────────────────────
        print("\n  [THINK] AI is reading spec and planning tests...")
        test_code = generate_test_file(spec_path)

        if test_code is None:
            print(f"  [ERROR] Could not generate valid code for {page_name}")
            self.all_results[page_name] = {
                "status": "generation_failed", "total": 0, "passed": 0, "failed": 0,
                "output": "AI code generation failed after all retries.", "gaps": ""
            }
            return

        # Ensure required imports are present
        test_code = self._ensure_imports(test_code)
        test_file.write_text(test_code)
        print(f"  [SAVE] {test_file}")

        # ── Phase 2: Execute ──────────────────────────────────────────────────
        print("\n  [EXECUTE] Running generated tests...")
        results = run_tests(test_file)
        self._print_run_summary(results)

        # ── Phase 3: Reflect + Fix ────────────────────────────────────────────
        if results["failed"] > 0:
            print(f"\n  [REFLECT] {results['failed']} failure(s) — AI is analyzing and fixing...")
            fixed_code = fix_test_file(test_code, results["output"])

            if fixed_code:
                test_file.write_text(self._ensure_imports(fixed_code))
                print("  [EXECUTE] Re-running fixed tests...")
                results = run_tests(test_file)
                test_code = fixed_code
                self._print_run_summary(results)

                if results["failed"] == 0:
                    print("  [FIX] ✅ All failures resolved by AI!")
                else:
                    print(f"  [FIX] ⚠️  {results['failed']} test(s) still failing after fix attempt")
            else:
                print("  [FIX] ⚠️  AI could not generate a valid fix")

        # ── Phase 4: Detect Gaps ──────────────────────────────────────────────
        print("\n  [ANALYZE] Detecting coverage gaps...")
        gaps = detect_gaps(spec_content, test_code, results)
        gaps_file = REPORTS_DIR / f"gaps_{page_name}.md"
        gaps_file.write_text(f"# Coverage Gaps — {page_name}\n\nGenerated: {datetime.now().isoformat()}\n\n{gaps}")
        print(f"  [GAPS] Saved → {gaps_file}")

        results["gaps"] = gaps
        results["spec_name"] = page_name
        self.all_results[page_name] = results

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _ensure_imports(self, code: str) -> str:
        """Guarantee essential imports are present at the top."""
        header_lines = []
        if "import os" not in code:
            header_lines.append("import os")
        if "import time" not in code:
            header_lines.append("import time")
        if "import pytest" not in code:
            header_lines.append("import pytest")
        if "from playwright.sync_api" not in code:
            header_lines.append("from playwright.sync_api import Page, expect")
        if f'BASE_URL = os.getenv("BASE_URL"' not in code and "BASE_URL" not in code:
            header_lines.append(f'BASE_URL = os.getenv("BASE_URL", "{BASE_URL}")')

        if header_lines:
            return "\n".join(header_lines) + "\n\n" + code
        return code

    def _print_run_summary(self, r: dict):
        icon = "✅" if r["status"] == "passed" else "❌"
        print(f"  {icon} Results — Passed: {r['passed']}  Failed: {r['failed']}  Total: {r['total']}")

    def _print_banner(self):
        print("\n" + "═"*60)
        print("  🤖 Markopolo Autonomous AI Test Agent")
        print(f"  Model  : {AI_MODEL}")
        print(f"  Target : {BASE_URL}")
        print(f"  Specs  : {len(list(SPECS_DIR.glob('*.md')))} files")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("═"*60)

    def _final_summary(self):
        total_p = sum(r.get("passed", 0) for r in self.all_results.values())
        total_f = sum(r.get("failed", 0) for r in self.all_results.values())
        total_t = sum(r.get("total",  0) for r in self.all_results.values())

        print("\n" + "═"*60)
        print("  FINAL SUMMARY")
        print("═"*60)
        print(f"  {'Page':<25} {'Passed':>8} {'Failed':>8} {'Total':>8}")
        print(f"  {'-'*49}")
        for name, r in self.all_results.items():
            icon = "✅" if r.get("failed", 1) == 0 else "❌"
            print(f"  {icon} {name:<23} {r.get('passed',0):>8} {r.get('failed',0):>8} {r.get('total',0):>8}")
        print(f"  {'-'*49}")
        print(f"  {'TOTAL':<25} {total_p:>8} {total_f:>8} {total_t:>8}")
        print("═"*60)

        # Write summary JSON for CI
        summary = {
            "timestamp": datetime.now().isoformat(),
            "model": AI_MODEL,
            "base_url": BASE_URL,
            "total_passed": total_p,
            "total_failed": total_f,
            "total_tests": total_t,
            "pages": self.all_results,
        }
        summary_file = REPORTS_DIR / "summary.json"
        # Remove non-serializable items for JSON
        clean_summary = json.loads(json.dumps(summary, default=str))
        summary_file.write_text(json.dumps(clean_summary, indent=2))
        print(f"\n  Report → {REPORTS_DIR}/")

        if total_f > 0:
            sys.exit(1)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = AutonomousTestAgent()
    agent.run()
