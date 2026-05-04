"""
Persistent memory — stores selector fixes, failure history, flaky patterns.
This is what makes the system learn between CI runs instead of starting fresh.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path("memory_store.json")

_DEFAULT: dict = {
    "selectors":              {},  # name → working selector string
    "failures":               {},  # test_name → list of failure records
    "fixes":                  {},  # selector_name → {selector, time}
    "flaky_tests":            [],  # test names known to be intermittently failing
    "known_good_selectors":   {},  # confirmed-working selectors
    "selector_attempts":      {},  # name → list of tried selectors
}


def load() -> dict:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {k: (type(v)() if isinstance(v, (dict, list)) else v) for k, v in _DEFAULT.items()}


def save(mem: dict) -> None:
    MEMORY_FILE.write_text(json.dumps(mem, indent=2, default=str), encoding="utf-8")


# ── Read helpers ──────────────────────────────────────────────────────────────

def get_selector(name: str) -> str | None:
    return load().get("selectors", {}).get(name)


def get_all_selectors() -> dict:
    return load().get("selectors", {})


def is_known_flaky(test_name: str) -> bool:
    return test_name in load().get("flaky_tests", [])


def summary() -> dict:
    mem = load()
    return {
        "fixed_selectors": len(mem.get("selectors", {})),
        "failure_records":  sum(len(v) for v in mem.get("failures", {}).values()),
        "flaky_tests":      len(mem.get("flaky_tests", [])),
    }


# ── Write helpers ─────────────────────────────────────────────────────────────

def record_failure(test_name: str, selector: str, error: str) -> None:
    mem = load()
    mem.setdefault("failures", {}).setdefault(test_name, []).append({
        "selector": selector,
        "error":    error,
        "time":     datetime.now().isoformat(),
    })
    save(mem)


def update_selector(name: str, new_selector: str) -> None:
    mem = load()
    mem.setdefault("selectors", {})[name] = new_selector
    mem.setdefault("fixes", {})[name] = {
        "selector": new_selector,
        "time": datetime.now().isoformat(),
    }
    save(mem)


def record_selector_attempt(name: str, selector: str) -> None:
    mem = load()
    attempts = mem.setdefault("selector_attempts", {}).setdefault(name, [])
    if selector not in attempts:
        attempts.append(selector)
    save(mem)


def mark_flaky(test_name: str) -> None:
    mem = load()
    flaky = mem.setdefault("flaky_tests", [])
    if test_name not in flaky:
        flaky.append(test_name)
    save(mem)


def confirm_selector(name: str, selector: str) -> None:
    mem = load()
    mem.setdefault("known_good_selectors", {})[name] = selector
    save(mem)
