"""
Playwright pytest configuration.
Captures full-page screenshots on every test failure and writes an
index file so agent.py can embed them in the HTML bug report.
"""

import re
import json
import pytest
from pathlib import Path
from datetime import datetime

SCREENSHOTS_DIR = Path("reports/screenshots")
_SCREENSHOT_INDEX: dict[str, dict] = {}   # nodeid → {path, timestamp}


# ── Browser / context defaults ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "locale": "en-US",
        "record_video_dir": None,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": True,
        "slow_mo": 0,
    }


# ── Screenshot capture on failure ─────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is None:
            return

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        # Sanitise nodeid → safe filename
        safe = re.sub(r"[^\w\-]", "_", item.nodeid)[:120]
        shot_path = SCREENSHOTS_DIR / f"{safe}.png"

        try:
            page.screenshot(path=str(shot_path), full_page=True)
            _SCREENSHOT_INDEX[item.nodeid] = {
                "path": str(shot_path),
                "url":  page.url,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            print(f"\n  [SCREENSHOT] Could not capture for {item.nodeid}: {exc}")


# ── Write index at session end ────────────────────────────────────────────────

def pytest_sessionfinish(session, exitstatus):
    if _SCREENSHOT_INDEX:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        index_file = SCREENSHOTS_DIR / "_index.json"
        index_file.write_text(json.dumps(_SCREENSHOT_INDEX, indent=2))
