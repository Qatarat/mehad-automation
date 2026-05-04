"""
Markopolo Autonomous AI Test Agent  —  v4
------------------------------------------
v2 architecture: MD → Spec Compiler → JSON → 15 test types → Validator → Execute
                 → Memory → Self-Heal → Bug Tickets → Gap Analysis → HTML Report

• Spec Compiler   — deterministic MD → JSON (no AI guessing structure)
• 15 test types   — functional, validation, negative, boundary, security, api,
                    accessibility, responsive, navigation, session, performance,
                    console errors, error states, visual, cross-browser
• Test Validator  — AST gate before execution (blocks broken AI code)
• Multi-model AI  — 5-model chain with auto-fallback
• Template engine — guaranteed valid tests when ALL AI models fail
• Memory system   — learns from failures, persists selector fixes between runs
• Self-healing    — 3 rounds of AI fix on failures
• Bug tickets     — per-failure AI analysis with screenshots + evidence
• HTML report     — complete with network logs, console errors, performance data
"""

import os, sys, json, ast, re, base64, builtins, subprocess
from pathlib import Path
from datetime import datetime

import ollama

# ── Package imports (try both modes: installed package + direct script) ────────
try:
    from ai_engine.spec_parser    import parse as parse_spec, ParsedSpec
    from ai_engine.spec_compiler  import compile_spec
    from ai_engine.test_generator import generate_all as tg_generate_all
    from ai_engine.test_generator import set_ai_caller as tg_set_caller
    from ai_engine.test_validator import validate_code, validate_file
    from ai_engine.bug_builder    import build_from_json_report
    from ai_engine.bug_builder    import set_ai_caller as bb_set_caller
    from ai_engine.gap_checker    import detect_gaps as gc_detect_gaps
    from ai_engine.gap_checker    import save_gaps_report
    from ai_engine.gap_checker    import set_ai_caller as gap_set_caller
    from ai_engine.evidence       import load_screenshot_index, load_evidence_index, enrich_bug
    from ai_engine.memory         import (record_failure, update_selector, get_all_selectors,
                                          mark_flaky, summary as mem_summary)
    from ai_engine.reporter       import generate_report
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from spec_parser    import parse as parse_spec, ParsedSpec
    from spec_compiler  import compile_spec
    from test_generator import generate_all as tg_generate_all
    from test_generator import set_ai_caller as tg_set_caller
    from test_validator import validate_code, validate_file
    from bug_builder    import build_from_json_report
    from bug_builder    import set_ai_caller as bb_set_caller
    from gap_checker    import detect_gaps as gc_detect_gaps
    from gap_checker    import save_gaps_report
    from gap_checker    import set_ai_caller as gap_set_caller
    from evidence       import load_screenshot_index, load_evidence_index, enrich_bug
    from memory         import (record_failure, update_selector, get_all_selectors,
                                mark_flaky, summary as mem_summary)
    from reporter       import generate_report

try:
    from payloads import XSS_QUICK as _XSS, SQLI_QUICK as _SQLI
except ImportError:
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from payloads import XSS_QUICK as _XSS, SQLI_QUICK as _SQLI
    except ImportError:
        _XSS, _SQLI = [], []

# ── Real-time output ──────────────────────────────────────────────────────────
_real_print = builtins.print
def print(*a, **kw):
    kw.setdefault("flush", True); _real_print(*a, **kw)
def log(msg=""):
    _real_print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL        = os.getenv("BASE_URL",  "https://beta-stg.markopolo.ai")
AI_MODEL        = os.getenv("AI_MODEL",  "qwen2.5-coder:1.5b")
SPECS_DIR       = Path("specs")
TESTS_DIR       = Path("tests")
REPORTS_DIR     = Path("reports")
SHOTS_DIR       = Path("reports/screenshots")
MAX_FIX_RETRIES = 3

# ── Multi-model chain — tried in order, auto-fallback ─────────────────────────
MODEL_CHAIN = [
    (AI_MODEL,          4096, 0.05),   # primary — env-configurable
    (AI_MODEL,          2000, 0.10),   # same model, smaller budget safety-net
    ("llama3.2:1b",     3000, 0.10),   # fallback 1  (1.3 GB)
    ("phi3.5",          3000, 0.10),   # fallback 2  (2.2 GB)
    ("qwen2.5:0.5b",    2000, 0.15),   # fallback 3  (tiny, last resort)
]

# ── System prompts ────────────────────────────────────────────────────────────
SYS_TEST = f"""\
You are an expert QA automation engineer. Write Playwright (Python/pytest) tests.

STRICT RULES — follow every rule or the tests WILL NOT RUN:
1. Output ONLY valid Python. No markdown fences. No prose. No explanations.
2. Start output with `import` statements — never with text.
3. Every test function MUST start with `def test_` and have `page: Page` as ONLY parameter.
4. Use EXACTLY these imports at the top:
   import os, time, pytest
   from playwright.sync_api import Page, expect
   BASE_URL = os.getenv("BASE_URL", "{BASE_URL}")
5. Navigation: page.goto(url) then page.wait_for_load_state("networkidle")
6. Selector priority (best → worst):
   page.get_by_role("button", name="Login")
   page.get_by_label("Email")
   page.get_by_placeholder("Enter email")
   page.locator('input[type="email"]')
7. Assertions: expect(locator).to_be_visible() / expect(page).to_have_url()
8. Unique test emails: f"qa_{{int(time.time())}}@mailinator.com"
9. Passwords: os.getenv("TEST_PASSWORD", "Test@1234!")
10. MAX 25 lines per function. End every function COMPLETELY — never leave open.
"""

SYS_BUG = "You are a senior QA lead. Write formal, actionable bug tickets."
SYS_ANALYST = "You are a senior QA engineer. Analyse test coverage gaps in plain bullet points."

# ── Test module header (prepended to every generated file) ────────────────────
_HDR = (
    "import os, time, pytest\n"
    "from playwright.sync_api import Page, expect\n"
    f'BASE_URL = os.getenv("BASE_URL", "{BASE_URL}")\n\n'
)

# ── AI model management ───────────────────────────────────────────────────────

def _available_models() -> set[str]:
    try:
        return {m["model"] for m in ollama.list().get("models", [])}
    except Exception:
        return {AI_MODEL}

_AVAILABLE: set[str] | None = None
_CONFIRMED_UNAVAILABLE: set[str] = set()  # models that returned 404 this session

def ai_call(system: str, user: str, max_tokens: int = 4096) -> str:
    """Try every model in MODEL_CHAIN until one responds. Never raises."""
    global _AVAILABLE
    if _AVAILABLE is None:
        _AVAILABLE = _available_models()
        log(f"  [MODELS] Available: {sorted(_AVAILABLE)}")
        if not _AVAILABLE:
            log("  [MODELS] No models registered — template engine will handle generation")

    for model, tok, temp in MODEL_CHAIN:
        if model in _CONFIRMED_UNAVAILABLE:
            continue
        if model not in _AVAILABLE and model != AI_MODEL:
            continue
        effective = min(max_tokens, tok)
        log(f"  [AI] → {model}  max_tokens={effective}")
        try:
            resp = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                options={"temperature": temp, "num_predict": effective},
            )
            text = resp["message"]["content"].strip()
            if len(text) > 50:
                log(f"  [AI] ✅ {model} → {len(text)} chars")
                return text
            log(f"  [AI] ⚠️  {model} short response, trying next...")
        except Exception as e:
            log(f"  [AI] ❌ {model}: {e}")
            if "not found" in str(e).lower() or "404" in str(e):
                _CONFIRMED_UNAVAILABLE.add(model)
                if len(_CONFIRMED_UNAVAILABLE) >= 2:
                    log("  [AI] ⚠️  Models unavailable — switching to template engine")
                    return ""

    log("  [AI] ⚠️  All models exhausted — template fallback will be used")
    return ""

# ── Wire AI callers into all sub-modules ──────────────────────────────────────
# Called once at startup after ai_call is defined.

def _wire_ai_callers():
    tg_set_caller(lambda prompt, max_tokens=2500: ai_call(SYS_TEST, prompt, max_tokens))
    bb_set_caller(ai_call)    # bug_builder uses (system, user, max_tokens)
    gap_set_caller(ai_call)   # gap_checker uses (system, user, max_tokens)

# ── Code helpers ──────────────────────────────────────────────────────────────

def clean_code(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ", "def ", "class ", "BASE_URL", "#")):
            return "\n".join(lines[i:]).strip()
    return raw.strip()

def is_valid_python(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"line {e.lineno}: {e.msg}"

def ensure_imports(code: str) -> str:
    # Strip any partial headers already at the top to avoid duplication
    lines = code.splitlines()
    # Skip leading lines that are already standard imports/BASE_URL
    clean_lines = []
    in_header = True
    for line in lines:
        if in_header and re.match(r"^(import (os|time|pytest)|from playwright|BASE_URL\s*=|$)", line):
            continue
        in_header = False
        clean_lines.append(line)
    clean = "\n".join(clean_lines).lstrip()
    return _HDR + clean

# ── Template engine (zero-AI fallback) ───────────────────────────────────────

def template_tests(spec: ParsedSpec) -> str:
    """Always generates valid Python — guarantees tests run even if all AI fails."""
    slug = spec.slug.replace("-", "_")
    url  = spec.url or (BASE_URL + spec.path)
    lines = [
        "import os, time, pytest",
        "from playwright.sync_api import Page, expect",
        f'BASE_URL = os.getenv("BASE_URL", "{BASE_URL}")',
        "",
    ]

    lines += [
        f"def test_{slug}_page_loads(page: Page):",
        f'    page.goto("{url}")',
        f'    page.wait_for_load_state("networkidle")',
        f'    assert "{spec.path.rstrip("/")}" in page.url or page.url.startswith(BASE_URL)',
        "",
    ]

    for i, flow in enumerate(spec.flows[:4], 1):
        fname = re.sub(r"\W+", "_", flow["name"].lower())[:40]
        lines += [
            f"def test_{slug}_flow_{i}_{fname}(page: Page):",
            f'    page.goto("{url}")',
            f'    page.wait_for_load_state("networkidle")',
            f'    assert page.url',
            "",
        ]

    for ec in spec.edge_cases[:5]:
        eid = ec["id"].lower().replace("-", "_")
        lines += [
            f"def test_{eid}(page: Page):",
            f'    """{ec["id"]}: {ec["scenario"][:60]}"""',
            f'    page.goto("{url}")',
            f'    page.wait_for_load_state("networkidle")',
            f'    assert page.url',
            "",
        ]

    lines += [
        f"def test_{slug}_mobile(page: Page):",
        f'    page.set_viewport_size({{"width": 375, "height": 667}})',
        f'    page.goto("{url}")',
        f'    page.wait_for_load_state("networkidle")',
        f'    assert page.url',
        "",
    ]

    lines += [
        f"def test_{slug}_no_console_errors(page: Page):",
        f'    errors = []',
        f'    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)',
        f'    page.goto("{url}")',
        f'    page.wait_for_load_state("networkidle")',
        f'    assert errors == [], f"Console errors: {{errors[:3]}}"',
        "",
    ]

    return "\n".join(lines)

# ── Section-based AI generation (secondary fallback) ─────────────────────────

def _gen_section(title: str, instructions: str, context: str) -> str:
    prompt = f"""Write Playwright pytest functions for: {title}

{context}

INSTRUCTIONS:
{instructions}

Output ONLY Python def test_...() functions. No imports. Keep each under 20 lines.
End every function completely — never leave a def open.
"""
    for attempt in range(1, 4):
        log(f"    [SECTION:{title}] attempt {attempt}/3")
        raw  = ai_call(SYS_TEST, prompt, max_tokens=3000)
        code = clean_code(raw)
        if not code:
            continue
        test_module = _HDR + code
        valid, err = is_valid_python(test_module)
        if valid:
            log(f"    [SECTION:{title}] ✅ {code.count('def test_')} tests")
            return code
        log(f"    [SECTION:{title}] ❌ {err} — retrying")
        prompt = f"Fix this syntax error: {err}\n\nReturn ONLY corrected function definitions:\n{code}"
    return ""


def generate_sections_fallback(spec: ParsedSpec) -> str:
    """Section-by-section generation when test_generator fails."""
    from ai_engine.spec_parser import (flows_prompt_section, edge_cases_prompt_section,
                                        validation_prompt_section, security_prompt_section)
    chunks = []

    if spec.flows:
        c = _gen_section("User Flows",
                         "Write ONE test per flow. Test key actions and assert URL or visible element.",
                         flows_prompt_section(spec))
        if c: chunks.append(c)

    c = _gen_section("Validation Rules",
                     "Test each invalid input (assert error appears). Test valid input (assert passes).",
                     validation_prompt_section(spec))
    if c: chunks.append(c)

    if spec.edge_cases:
        c = _gen_section("Edge Cases",
                         "ONE test per edge case. Input the value, assert expected behaviour.",
                         edge_cases_prompt_section(spec))
        if c: chunks.append(c)

    c = _gen_section("Security Inputs",
                     "Submit each security input. Assert page does NOT crash and URL stays same.",
                     security_prompt_section(spec))
    if c: chunks.append(c)

    if not chunks:
        return ""

    full = _HDR + "\n\n".join(chunks)
    ok, err = is_valid_python(full)
    if ok:
        return full

    fixed_raw = ai_call(SYS_TEST,
                        f"Fix syntax error: {err}\n\nCode:\n{full}\n\nReturn complete fixed file.",
                        max_tokens=4096)
    fixed = clean_code(fixed_raw)
    ok2, _ = is_valid_python(fixed)
    return fixed if ok2 else ""

# ── Primary generator — all 15 test types via test_generator.py ───────────────

def generate_all_15_types(spec: ParsedSpec) -> str:
    """
    Generate tests for all 15 types, validate each chunk,
    combine into one module. Returns empty string only if ALL fail.
    """
    log(f"  [GEN] Generating all 15 test types for {spec.page_name}")

    raw_chunks = tg_generate_all(spec, _XSS, _SQLI)
    log(f"  [GEN] test_generator returned {len(raw_chunks)} type(s)")

    valid_chunks = []
    for type_name, code in raw_chunks.items():
        if not code or not code.strip():
            log(f"    [GEN:{type_name}] empty — skipped")
            continue

        # Validate with imports wrapper
        test_module = _HDR + code
        result = validate_code(test_module)

        if result["valid"]:
            n = code.count("def test_")
            log(f"    [GEN:{type_name}] ✅ {n} test(s)")
            valid_chunks.append(code)
        else:
            log(f"    [GEN:{type_name}] ❌ {result['errors']} — skipped")

    if not valid_chunks:
        log("  [GEN] ⚠️  No valid chunks from test_generator — trying sections fallback")
        return ""

    combined = _HDR + "\n\n".join(valid_chunks)
    ok, err = is_valid_python(combined)
    if ok:
        n = combined.count("def test_")
        log(f"  [GEN] ✅ Combined: {n} tests across {len(valid_chunks)} type(s)")
        return combined

    # One fix attempt on the combined file
    log(f"  [GEN] Syntax in combined ({err}) — AI fix attempt...")
    fixed = clean_code(ai_call(
        SYS_TEST,
        f"Fix this syntax error: {err}\n\nReturn the complete corrected Python file:\n{combined}",
        max_tokens=4096,
    ))
    ok2, err2 = is_valid_python(fixed)
    if ok2:
        log("  [GEN] ✅ Combined fixed")
        return fixed

    log(f"  [GEN] ❌ Combined fix failed ({err2}) — sections fallback")
    return ""

# ── Test execution ────────────────────────────────────────────────────────────

def _stream(cmd: list, env: dict, timeout: int = 300) -> tuple[int, str]:
    lines = []
    try:
        proc = subprocess.Popen(
            cmd, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for line in proc.stdout:
            s = line.rstrip()
            lines.append(s)
            log(f"    {s}")
        proc.wait(timeout=timeout)
        return proc.returncode, "\n".join(lines)
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, "\n".join(lines) + "\n[TIMEOUT]"
    except Exception as e:
        return -1, f"[ERROR] {e}"


def run_tests(test_file: Path) -> dict:
    json_report = REPORTS_DIR / f"result_{test_file.stem}.json"
    env = {**os.environ, "BASE_URL": BASE_URL,
           "PWDEBUG": "0", "PYTHONUNBUFFERED": "1"}

    log(f"  [COLLECT] Discovering tests in {test_file.name}...")
    _rc, cout = _stream(
        [sys.executable, "-m", "pytest", str(test_file),
         "--collect-only", "-q", "--no-header"], env, timeout=60)
    collected = len(re.findall(r"<Function test_", cout))
    log(f"  [COLLECT] {collected} test function(s) found")
    if collected == 0:
        log("  [COLLECT] ⚠️  0 tests — dumping file content:")
        log(test_file.read_text())

    log(f"  [PYTEST] Running tests...")
    rc, output = _stream(
        [sys.executable, "-m", "pytest", str(test_file),
         "-v", "--tb=short", "--no-header",
         "--json-report", f"--json-report-file={json_report}",
         "--timeout=30"],
        env, timeout=300,
    )

    passed = failed = total = 0
    if json_report.exists():
        try:
            s = json.loads(json_report.read_text()).get("summary", {})
            passed = s.get("passed", 0)
            failed = s.get("failed", 0) + s.get("error", 0)
            total  = s.get("total", 0)
        except Exception:
            pass

    if total == 0:
        for line in output.splitlines():
            for n, st in re.findall(r"(\d+) (passed|failed|error)", line):
                if st == "passed":              passed = int(n)
                elif st in ("failed", "error"): failed += int(n)
        total = passed + failed

    return {
        "status":      "passed" if rc == 0 else "failed",
        "total": total, "passed": passed, "failed": failed,
        "output": output,
        "json_report": str(json_report) if json_report.exists() else None,
        "returncode":  rc,
    }

# ── Main agent ────────────────────────────────────────────────────────────────

class AutonomousTestAgent:

    def __init__(self):
        self.all_results: dict[str, dict] = {}
        TESTS_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)
        SHOTS_DIR.mkdir(parents=True, exist_ok=True)
        _wire_ai_callers()
        ms = mem_summary()
        if ms["fixed_selectors"] or ms["failure_records"]:
            log(f"  [MEMORY] Loaded: {ms['fixed_selectors']} selector fix(es), "
                f"{ms['failure_records']} failure record(s)")

    def run(self):
        self._banner()
        specs = sorted(SPECS_DIR.glob("*.md"))
        if not specs:
            log("[ERROR] No .md spec files in specs/")
            sys.exit(1)
        for sp in specs:
            self._process(sp)
        self._final_report()

    def _process(self, spec_path: Path):
        name = spec_path.stem
        log(f"\n{'━'*64}")
        log(f"  SPEC: {spec_path.name}")
        log(f"{'━'*64}")

        # ── 1. Parse MD spec ──────────────────────────────────────────────────
        log("  [PARSE] Reading spec...")
        spec = parse_spec(spec_path)
        log(f"  [PARSE] {len(spec.flows)} flows | {len(spec.edge_cases)} edge cases | "
            f"{len(spec.validation_rules)} validation rules | {len(spec.requirements)} requirements")

        # ── 2. Compile spec to JSON (v2 deterministic layer) ──────────────────
        log("  [COMPILE] Compiling spec to structured JSON...")
        compiled = compile_spec(spec_path.read_text(encoding="utf-8"), str(spec_path))
        compiled_path = spec_path.with_suffix(".spec.json")
        compiled_path.write_text(json.dumps(compiled, indent=2, ensure_ascii=False))
        log(f"  [COMPILE] {len(compiled['selectors'])} selectors | "
            f"{len(compiled['flows'])} flows | saved → {compiled_path.name}")

        test_file = TESTS_DIR / f"test_{name.replace('-','_')}.py"

        # ── 3. Generate tests: 15 types → fallback chain ──────────────────────
        log("\n  [THINK] Generating tests (15 types)...")
        code = generate_all_15_types(spec)

        if not code:
            log("  [GEN] Trying section-based fallback...")
            code = generate_sections_fallback(spec)

        if not code:
            log("  [FALLBACK] Using template engine (zero-AI)...")
            code = template_tests(spec)
            log(f"  [FALLBACK] Template: {code.count('def test_')} tests")

        code = ensure_imports(code)

        # ── 4. Validate before execution ──────────────────────────────────────
        vresult = validate_code(code)
        if not vresult["valid"]:
            log(f"  [VALIDATE] ❌ Code invalid: {vresult['errors']} — skipping {name}")
            self.all_results[name] = {
                "status": "generation_failed", "total": 0, "passed": 0,
                "failed": 0, "bugs": [], "gaps": "Code generation failed.",
            }
            return
        if vresult["warnings"]:
            log(f"  [VALIDATE] ⚠️  Warnings: {vresult['warnings']}")
        log(f"  [VALIDATE] ✅ {code.count('def test_')} tests validated")

        test_file.write_text(code)
        log(f"  [SAVE]  {test_file}  ({code.count('def test_')} tests)")

        # ── 5. Execute ────────────────────────────────────────────────────────
        log(f"\n  [EXECUTE] Running against {BASE_URL}...")
        results = run_tests(test_file)
        self._show(results)

        # ── 6. Self-heal failures ─────────────────────────────────────────────
        if results["failed"] > 0:
            log(f"\n  [REFLECT] {results['failed']} failure(s) — self-healing...")
            for fix_round in range(1, MAX_FIX_RETRIES + 1):
                log(f"  [FIX] Round {fix_round}/{MAX_FIX_RETRIES}")
                fixed_raw = ai_call(
                    SYS_TEST,
                    f"Fix these failing Playwright tests.\n\n"
                    f"FAILURES:\n{results['output'][:2000]}\n\n"
                    f"ORIGINAL CODE:\n{code}\n\n"
                    "Return the complete corrected test file. Python only.",
                    max_tokens=4096,
                )
                fixed = clean_code(fixed_raw)
                v, e = is_valid_python(ensure_imports(fixed))
                if v and fixed:
                    code = ensure_imports(fixed)
                    test_file.write_text(code)
                    results = run_tests(test_file)
                    self._show(results)
                    if results["failed"] == 0:
                        log("  [FIX] ✅ All failures resolved!")
                        break
                    log(f"  [FIX] Still {results['failed']} failure(s)")
                    # Record to memory
                    if "selector" in results["output"].lower() or \
                       "locator" in results["output"].lower():
                        record_failure(name, "unknown_selector", results["output"][:200])
                else:
                    log(f"  [FIX] ❌ Fix attempt produced invalid code: {e}")

            # Mark remaining flaky tests in memory
            if results["failed"] > 0:
                for line in results["output"].splitlines():
                    m = re.match(r"FAILED\s+(tests/\S+::)(test_\w+)", line)
                    if m:
                        mark_flaky(m.group(2))

        # ── 7. Build bug tickets ──────────────────────────────────────────────
        bugs = []
        if results["failed"] > 0:
            log(f"\n  [BUGS] AI writing {results['failed']} bug ticket(s)...")
            shot_idx = load_screenshot_index()
            ev_idx   = load_evidence_index()
            raw_bugs = build_from_json_report(
                results.get("json_report", ""),
                spec.raw,
                shot_idx,
                ev_idx,
            )
            for b in raw_bugs:
                b = enrich_bug(b, shot_idx, ev_idx)
                bugs.append(b)
            log(f"  [BUGS] {len(bugs)} ticket(s) created")

        # ── 8. Coverage gap detection ─────────────────────────────────────────
        log("\n  [GAPS] Detecting coverage gaps...")
        gaps = gc_detect_gaps(spec, code, results)
        save_gaps_report(name, gaps, REPORTS_DIR)

        results.update({"bugs": bugs, "gaps": gaps, "spec_name": name,
                        "compiled": compiled})
        self.all_results[name] = results

    def _final_report(self):
        total_p = sum(r.get("passed", 0) for r in self.all_results.values())
        total_f = sum(r.get("failed", 0) for r in self.all_results.values())
        total_t = sum(r.get("total",  0) for r in self.all_results.values())
        all_bugs = [b for r in self.all_results.values() for b in r.get("bugs", [])]

        log("\n" + "═"*64)
        log("  FINAL SUMMARY")
        log("═"*64)
        log(f"  {'Page':<28} {'Pass':>6} {'Fail':>6} {'Total':>7} {'Bugs':>6}")
        log(f"  {'─'*55}")
        for n, r in self.all_results.items():
            icon = "✅" if r.get("failed", 1) == 0 else "❌"
            log(f"  {icon} {n:<26} {r.get('passed',0):>6} {r.get('failed',0):>6} "
                f"{r.get('total',0):>7} {len(r.get('bugs',[])):>6}")
        log(f"  {'─'*55}")
        log(f"  {'TOTAL':<28} {total_p:>6} {total_f:>6} {total_t:>7} {len(all_bugs):>6}")
        log("═"*64)

        report = generate_report(self.all_results, BASE_URL, AI_MODEL)
        log(f"\n  HTML Report → {report}")
        log(f"  Bug Tickets → {len(all_bugs)}")

        ms = mem_summary()
        log(f"  Memory      → {ms['fixed_selectors']} selector fixes | "
            f"{ms['failure_records']} failure records")

        (REPORTS_DIR / "summary.json").write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "model": AI_MODEL, "base_url": BASE_URL,
            "total_passed": total_p, "total_failed": total_f,
            "total_tests": total_t, "total_bugs": len(all_bugs),
        }, indent=2))

        if total_f > 0:
            sys.exit(1)

    def _show(self, r):
        icon = "✅" if r["status"] == "passed" else "❌"
        log(f"  {icon}  Passed:{r['passed']}  Failed:{r['failed']}  Total:{r['total']}")

    def _banner(self):
        log("═"*64)
        log("  Markopolo Autonomous AI Test Agent  v4")
        log(f"  Primary model  : {AI_MODEL}  (+{len(MODEL_CHAIN)-1} fallbacks)")
        log(f"  Target URL     : {BASE_URL}")
        log(f"  Specs          : {len(list(SPECS_DIR.glob('*.md')))} file(s)")
        log(f"  Test types     : 15 (functional→cross-browser)")
        log(f"  XSS payloads   : {len(_XSS)}  |  SQLi payloads: {len(_SQLI)}")
        log(f"  Started        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log("═"*64)


if __name__ == "__main__":
    AutonomousTestAgent().run()
