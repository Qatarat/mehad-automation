"""
Coverage gap analysis — compares spec requirements against generated tests.
Identifies what's missing so the team knows what to add next.
"""
from __future__ import annotations
import re
from pathlib import Path

SYS_ANALYST = """\
You are a senior QA engineer. Identify test coverage gaps concisely.
Format each gap exactly as: [MISSING] <what> — <why it matters> — <how to add it>
Maximum 15 items. Bullet points only. No prose, no headers.\
"""

_ai_call = None  # injected by agent.py


def set_ai_caller(fn):
    global _ai_call
    _ai_call = fn


def _ai(prompt: str) -> str:
    if _ai_call is None:
        return "Gap analysis unavailable — no AI model connected."
    try:
        return _ai_call(SYS_ANALYST, prompt, max_tokens=1200)
    except Exception as e:
        return f"Gap analysis failed: {e}"


def detect_gaps(spec, test_code: str, results: dict) -> str:
    reqs = "\n".join(spec.requirements[:12]) if spec.requirements else "  (none extracted)"
    ecs  = "\n".join(
        f"  {e['id']}: {e['scenario']}" for e in spec.edge_cases[:10]
    ) if spec.edge_cases else "  (none extracted)"

    test_names = re.findall(r"def (test_\w+)", test_code)
    tested = "\n".join(f"  {t}" for t in test_names) if test_names else "  (no tests generated)"

    prompt = f"""Identify coverage gaps for {spec.page_name}.

SPEC REQUIREMENTS:
{reqs}

SPEC EDGE CASES:
{ecs}

TESTS WRITTEN ({results.get('total', 0)} total, {results.get('passed', 0)} passed, {results.get('failed', 0)} failed):
{tested}

List ONLY what is genuinely missing — skip anything already covered above.
"""
    return _ai(prompt)


def save_gaps_report(page_name: str, gaps_text: str, reports_dir: Path) -> None:
    from datetime import datetime
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"gaps_{page_name}.md").write_text(
        f"# Coverage Gaps — {page_name}\n\n"
        f"Generated: {datetime.now().isoformat()}\n\n{gaps_text}"
    )
