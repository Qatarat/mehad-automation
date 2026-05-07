"""
Consolidate Reports — merges results from ALL QA agents into one bug-report.html.

Reads:
  reports/summary.json                  — AI agent (agent.py / langgraph_agent.py)
  reports/result_test_*.json            — AI-generated per-spec pytest JSON
  reports/qa_agent_*/result_*.json      — Downloaded artifacts from CI QA agents
  reports/qa{N}_{group}_results.json    — Per-group JSON from hand-crafted tests

Writes:
  reports/bug-report.html               — Master consolidated report
  reports/consolidated_summary.json     — Machine-readable merged summary
"""
from __future__ import annotations
import base64, json, re, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from friendly import (
    friendly_actual, friendly_expected, friendly_description, friendly_steps,
    extract_docstrings, parse_parametrize_id, build_passed_test_entry,
)

REPORTS_DIR = ROOT / "reports"

# Screenshot index built by conftest.py — nodeid → {path, url, timestamp}
_SHOT_INDEX: dict = {}
_SHOT_INDEX_LOADED = False

# Cache for {test_function_name → docstring} — built lazily on first lookup
_DOCSTRING_CACHE: dict[str, str] | None = None


def _docstrings() -> dict[str, str]:
    """Lazy: parse all test files in the project to extract test docstrings."""
    global _DOCSTRING_CACHE
    if _DOCSTRING_CACHE is not None:
        return _DOCSTRING_CACHE
    test_files = list((ROOT / "tests").glob("test_*.py"))
    _DOCSTRING_CACHE = extract_docstrings(test_files)
    return _DOCSTRING_CACHE


def _load_shot_index() -> None:
    global _SHOT_INDEX, _SHOT_INDEX_LOADED
    if _SHOT_INDEX_LOADED:
        return
    _SHOT_INDEX_LOADED = True
    idx_path = REPORTS_DIR / "screenshots" / "_index.json"
    if idx_path.exists():
        try:
            _SHOT_INDEX = json.loads(idx_path.read_text(encoding="utf-8"))
        except Exception:
            pass


def _screenshot_b64(nodeid: str, fn_name: str) -> str:
    """Return base64 data-URI for the failure screenshot, or '' if not found."""
    _load_shot_index()
    # Try exact nodeid match first, then fn_name substring match
    entry = _SHOT_INDEX.get(nodeid)
    if not entry:
        for key, val in _SHOT_INDEX.items():
            if fn_name in key:
                entry = val
                break
    if not entry:
        return ""
    png_path = Path(entry.get("path", ""))
    if not png_path.exists():
        # Path might be relative to project root
        png_path = ROOT / png_path
    if not png_path.exists():
        return ""
    try:
        data = base64.b64encode(png_path.read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    except Exception:
        return ""


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _infer_severity(nodeid: str) -> tuple[str, str]:
    """Map test nodeid to (severity, priority). Heuristic mirrors bug_builder."""
    nl = nodeid.lower()
    if any(k in nl for k in ("security", "xss", "sqli", "injection", "csrf")):
        return "CRITICAL", "P0"
    if any(k in nl for k in ("hallucination", "auth", "login", "otp",
                              "session", "smoke", "checkout", "payment")):
        return "HIGH", "P1"
    if any(k in nl for k in ("seo", "meta", "i18n", "rtl", "arabic", "locale",
                              "visual", "cross_browser", "touch_target",
                              "responsive", "cookie", "storage")):
        return "LOW", "P3"
    return "MEDIUM", "P2"


def _bugs_from_pytest_json(data: dict, prefix: str, base_url: str) -> list:
    """Convert pytest-json-report failures into bug-ticket dicts.

    Uses friendly.py to translate cryptic Playwright errors into plain English
    and to build a step-by-step reproduction guide for non-engineers."""
    bugs = []
    docstrings = _docstrings()
    for t in data.get("tests", []):
        if t.get("outcome") not in ("failed", "error"):
            continue
        nodeid  = t.get("nodeid", "")
        fn_name = nodeid.split("::")[-1].split("[")[0]
        call    = t.get("call") or t.get("setup") or {}
        longrepr = call.get("longrepr", "") if isinstance(call, dict) else ""
        crash_msg = (call.get("crash") or {}).get("message", "") if isinstance(call, dict) else ""
        duration = call.get("duration", 0.0) if isinstance(call, dict) else 0.0
        lines    = [l for l in longrepr.splitlines() if l.strip()]
        short    = "\n".join(lines[-4:]) if lines else "Assertion failed"

        ds       = docstrings.get(fn_name, "")
        param    = parse_parametrize_id(nodeid)
        sev, pri = _infer_severity(nodeid)

        # Friendly fields — these are what non-engineers actually read
        f_desc = friendly_description(fn_name, ds, base_url)
        if param:
            f_desc += f" Test parameters: {param}."
        f_exp  = friendly_expected(fn_name, ds)
        f_act  = friendly_actual(crash_msg or short, longrepr)
        f_steps = friendly_steps(fn_name, ds, base_url, param)

        bugs.append({
            "id":            f"{prefix}-{len(bugs)+1:03d}",
            "severity":      sev,
            "priority":      pri,
            "title":         f"Failed: {fn_name.replace('_', ' ').strip().capitalize()}",
            "test_name":     fn_name,
            "page_url":      base_url,
            "description":   f_desc,
            "expected":      f_exp,
            "actual":        f_act,
            "steps":         f_steps,
            "test_data":     param,
            "docstring":     ds,
            "duration":      f"{duration:.2f}s" if duration else "",
            "error_message": short[:500],
            "traceback":     longrepr[:2000],
            "timestamp":     datetime.now().isoformat(),
            "screenshot_b64": _screenshot_b64(nodeid, fn_name),
            "browser":       "Chromium",
            "viewport":      "1280x720",
            "env":           "Staging",
        })
    return bugs


def _passed_from_pytest_json(data: dict) -> list:
    """Extract passed-test summary records (with docstring + parametrize ID).

    Used by the reporter to render an expandable 'Passed Tests' panel per
    group so users can see exactly which test cases ran and what data
    each one used."""
    docstrings = _docstrings()
    out = []
    for t in data.get("tests", []):
        outcome = t.get("outcome", "")
        if outcome != "passed":
            continue
        nodeid = t.get("nodeid", "")
        call   = t.get("call") or {}
        dur    = call.get("duration", 0.0) if isinstance(call, dict) else 0.0
        out.append(build_passed_test_entry(nodeid, dur, docstrings))
    return out


def _load_qa_group(json_path: Path, group_name: str, base_url: str) -> dict:
    """Load a qa{N}_results.json and return an all_results entry."""
    data = _load(json_path)
    s    = data.get("summary", {})
    p    = s.get("passed", 0)
    f    = s.get("failed", 0) + s.get("error", 0)
    t    = s.get("total",  p + f)
    return {
        "status":       "passed" if f == 0 and t > 0 else ("failed" if f > 0 else "no_data"),
        "passed":       p,
        "failed":       f,
        "total":        t,
        "bugs":         _bugs_from_pytest_json(data, group_name[:6].upper(), base_url),
        "passed_tests": _passed_from_pytest_json(data),
        "gaps":         "",
        "group":        group_name,
        "source":       str(json_path.name),
    }


def build_consolidated_results(base_url: str) -> dict:
    """Merge all available result sources into one all_results dict."""
    all_results: dict = {}

    # ── 1. AI agent results (agent.py / langgraph) ────────────────────────────
    summary  = _load(REPORTS_DIR / "summary.json")
    data_log = _load(REPORTS_DIR / "test_data_log.json")
    ai_specs = summary.get("specs_tested",
                           list(data_log.get("specs", {}).keys()))

    for spec_name in ai_specs:
        for stem in (f"result_test_{spec_name.replace('-','_')}",
                     f"result_{spec_name.replace('-','_')}"):
            p = REPORTS_DIR / f"{stem}.json"
            if p.exists():
                data = _load(p)
                s    = data.get("summary", {})
                passed = s.get("passed", 0)
                failed = s.get("failed", 0) + s.get("error", 0)
                total  = s.get("total",  passed + failed)
                prefix = f"BUG-{spec_name[:4].upper()}"
                all_results[spec_name] = {
                    "status":       "passed" if failed == 0 and total > 0 else "failed",
                    "passed":       passed,
                    "failed":       failed,
                    "total":        total,
                    "bugs":         _bugs_from_pytest_json(data, prefix, base_url),
                    "passed_tests": _passed_from_pytest_json(data),
                    "gaps":         "",
                    "group":        "AI Agent",
                    "source":       stem + ".json",
                }
                break

    # ── 2. Hand-crafted QA agent results ─────────────────────────────────────
    qa_groups = {
        "qa01_functional":    ("QA-01 Functional",      "QA01"),
        "qa02_edge":          ("QA-02 Edge Cases",       "QA02"),
        "qa03_security":      ("QA-03 Security",         "QA03"),
        "qa04_performance":   ("QA-04 Performance",      "QA04"),
        "qa05_hallucination": ("QA-05 Hallucination",    "QA05"),
        "qa06_api":           ("QA-06 API & Network",    "QA06"),
        "qa07_accessibility": ("QA-07 Accessibility",    "QA07"),
        "qa08_mobile":        ("QA-08 Mobile/Viewport",  "QA08"),
        "qa09_seo":           ("QA-09 SEO & Meta",       "QA09"),
        "qa10_i18n":          ("QA-10 i18n & RTL",       "QA10"),
    }

    for file_stem, (group_name, prefix) in qa_groups.items():
        # Try several file naming patterns
        candidates = [
            REPORTS_DIR / f"{file_stem}_results.json",
            REPORTS_DIR / f"result_{file_stem}.json",
            REPORTS_DIR / f"{file_stem}.json",
        ]
        # Also search in downloaded artifact directories
        for artifact_dir in REPORTS_DIR.glob("qa_agent_*"):
            if artifact_dir.is_dir():
                candidates += list(artifact_dir.glob("*.json"))

        for candidate in candidates:
            if candidate.exists() and candidate.stat().st_size > 10:
                entry = _load_qa_group(candidate, group_name, base_url)
                if entry["total"] > 0:
                    all_results[file_stem] = entry
                    break

    return all_results


def compute_totals(all_results: dict) -> dict:
    total_p = sum(r["passed"] for r in all_results.values())
    total_f = sum(r["failed"] for r in all_results.values())
    total_t = sum(r["total"]  for r in all_results.values())
    total_b = sum(len(r.get("bugs", [])) for r in all_results.values())
    return {
        "total_passed": total_p,
        "total_failed": total_f,
        "total_tests":  total_t,
        "total_bugs":   total_b,
        "pass_rate":    f"{total_p/total_t*100:.1f}%" if total_t else "N/A",
    }


def main():
    REPORTS_DIR.mkdir(exist_ok=True)

    summary  = _load(REPORTS_DIR / "summary.json")
    base_url = summary.get("base_url", "https://dev.mehadedu.com/en")
    model    = summary.get("model", "unknown")

    all_results = build_consolidated_results(base_url)

    if not all_results:
        print("[CONSOLIDATE] No result files found — creating placeholder")
        all_results = {"no_data": {
            "status": "no_data", "passed": 0, "failed": 0, "total": 0,
            "bugs": [], "gaps": "No test results collected yet.", "group": ""
        }}

    totals = compute_totals(all_results)

    print("[CONSOLIDATE] Results:")
    print(f"  {'Group':<30} {'Pass':>5} {'Fail':>5} {'Total':>6}")
    print(f"  {'-'*50}")
    for name, r in all_results.items():
        print(f"  {name:<30} {r['passed']:>5} {r['failed']:>5} {r['total']:>6}")
    print(f"  {'─'*50}")
    print(f"  {'TOTAL':<30} {totals['total_passed']:>5} {totals['total_failed']:>5} "
          f"{totals['total_tests']:>6}  (pass rate: {totals['pass_rate']})")

    # Write consolidated summary JSON
    cons_path = REPORTS_DIR / "consolidated_summary.json"
    cons_path.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "base_url":  base_url,
        "engine":    "consolidated",
        "sources":   list(all_results.keys()),
        **totals,
    }, indent=2), encoding="utf-8")

    # Update main summary.json so the existing HTML generator also works
    merged_summary = {**summary, **totals,
                      "specs_tested": list(all_results.keys())}
    (REPORTS_DIR / "summary.json").write_text(
        json.dumps(merged_summary, indent=2), encoding="utf-8")

    # Generate the consolidated HTML bug report
    from ai_engine.reporter import generate_report
    out = generate_report(all_results, base_url, model)
    print(f"[CONSOLIDATE] ✅ Master report → {out}")
    print(f"[CONSOLIDATE] ✅ Summary       → {cons_path}")


if __name__ == "__main__":
    main()
