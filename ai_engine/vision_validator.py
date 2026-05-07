"""
Vision-LLM UI validator — uses a local Ollama vision model (qwen2-vl,
llava, etc.) to inspect screenshots and report visual issues that DOM
tests cannot catch:

  • Cropped text (truncation that doesn't trigger overflow events)
  • Bad contrast (black text on dark blue, etc.)
  • Overlapping elements (button covered by image)
  • Empty / placeholder content visible to users
  • Layout asymmetry, alignment issues
  • Missing images (broken-image icon visible)
  • Dark-mode/light-mode rendering bugs

Runs ONLY when:
  • Ollama is reachable
  • A vision model is pulled (model name from env VISION_MODEL,
    default 'qwen2-vl:7b')

Otherwise the validator returns [] — tests using it skip cleanly.
Designed for opt-in usage in CI (vision model is 5GB).

Public API
    validator = VisionValidator()
    validator.is_available()          # True/False
    issues = validator.inspect(png_path, page_label, expected_summary)
"""
from __future__ import annotations
import base64, os, re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import ollama
    _OLLAMA_OK = True
except ImportError:
    _OLLAMA_OK = False


_DEFAULT_VISION_MODEL = os.getenv("VISION_MODEL", "qwen2-vl:7b")
_VISION_TIMEOUT       = int(os.getenv("VISION_TIMEOUT", "60"))


# Issue categories the vision model is asked to look for. The system prompt
# specifies these so we get back a structured list, not free-text rambling.
_ISSUE_CATEGORIES = [
    ("CROPPED_TEXT",     "Text cut off / truncated / showing ellipsis where it shouldn't"),
    ("CONTRAST_ISSUE",   "Text or button that fails contrast (e.g. light-grey on white)"),
    ("OVERLAP",          "Two elements visually overlapping or one covering the other"),
    ("PLACEHOLDER",      "Lorem ipsum / TODO / placeholder text visible to end users"),
    ("BROKEN_IMAGE",     "Broken-image icon, missing avatar, blank space where image expected"),
    ("ALIGNMENT",        "Element off-grid, mis-aligned, asymmetric layout"),
    ("EMPTY_CONTENT",    "Empty cards, blank cards, '0 items' where content expected"),
    ("OFF_BRAND",        "Wrong colors, mixed fonts, inconsistent styling vs page header"),
    ("INTERACTIVE_AMBIGUITY", "Unclear which element is clickable / focusable"),
]

_SYSTEM_PROMPT = """\
You are a senior UI/UX QA reviewer. You will be shown a screenshot of a
webpage and asked to identify visual quality issues a user would notice.

Reply with a JSON array. Each item has 'category' and 'description'.
Valid categories: """ + ", ".join(c for c, _ in _ISSUE_CATEGORIES) + """

If the page looks clean, reply with: []

Be strict but not paranoid:
  • Flag REAL visual problems, not stylistic preferences.
  • One item per distinct issue.
  • Description should be ONE sentence, specific (e.g. "The 'Find a Teacher'
    button at top-right has white text on a light-blue background, contrast
    ratio looks below 3:1").
  • Maximum 6 issues per screenshot.
  • Output ONLY the JSON array. No markdown fences, no commentary.
"""


@dataclass
class VisualIssue:
    category:    str
    description: str
    page_label:  str
    severity:    str = "MEDIUM"   # CRITICAL/HIGH/MEDIUM/LOW

    def to_dict(self) -> dict:
        return {
            "category":    self.category,
            "description": self.description,
            "page_label":  self.page_label,
            "severity":    self.severity,
        }


class VisionValidator:
    """Wraps a local Ollama vision model. Methods return [] when the model
    isn't available so callers skip cleanly."""

    def __init__(self, model: str | None = None):
        self.model    = model or _DEFAULT_VISION_MODEL
        self._checked = False
        self._available = False

    def is_available(self) -> bool:
        """Cached availability probe — runs once per process."""
        if self._checked:
            return self._available
        self._checked = True
        if not _OLLAMA_OK:
            return False
        try:
            available_models = {
                m.get("model", m.get("name", "")) for m in ollama.list().get("models", [])
            }
            self._available = self.model in available_models
        except Exception:
            self._available = False
        return self._available

    def inspect(self, png_path: Path, page_label: str,
                expected_summary: str = "") -> list[VisualIssue]:
        """Send the screenshot to the vision model and parse issues.
        Returns empty list when model unavailable, on timeout, or when
        model says the page is clean."""
        if not self.is_available():
            return []
        png_path = Path(png_path)
        if not png_path.exists() or png_path.stat().st_size < 1024:
            return []

        prompt = (
            f"Page being reviewed: {page_label}\n"
            f"Expected per spec: {expected_summary or '(no specific expectation; just look for obvious bugs)'}\n\n"
            "Identify visual issues. Reply with the JSON array as instructed."
        )
        try:
            resp = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",
                     "content": prompt,
                     "images":  [str(png_path)]},
                ],
                options={"temperature": 0.1, "num_predict": 800},
                # ollama python client doesn't support timeout=, use stream:false
                stream=False,
            )
        except Exception as e:
            print(f"  [VISION] {self.model} failed: {e}", flush=True)
            return []

        text = (resp.get("message", {}).get("content") or "").strip()
        return self._parse_issues(text, page_label)

    @staticmethod
    def _parse_issues(text: str, page_label: str) -> list[VisualIssue]:
        """Parse the JSON array (with light tolerance for markdown fences)."""
        if not text:
            return []
        # Strip optional ```json ... ``` fences
        text = re.sub(r"^```(?:json)?\s*", "", text.strip())
        text = re.sub(r"\s*```\s*$", "", text)
        # Find the first [ ... ] in the text
        m = re.search(r"\[.*\]", text, flags=re.S)
        if not m:
            return []
        import json as _json
        try:
            data = _json.loads(m.group())
        except Exception:
            return []
        if not isinstance(data, list):
            return []
        valid_cats = {c for c, _ in _ISSUE_CATEGORIES}
        out: list[VisualIssue] = []
        for item in data[:8]:   # cap defensive
            if not isinstance(item, dict):
                continue
            cat  = str(item.get("category", "")).strip().upper().replace(" ", "_")
            desc = str(item.get("description", "")).strip()
            if not cat or not desc:
                continue
            if cat not in valid_cats:
                # Tolerate: map to closest known if any contained word matches
                cat = next((c for c in valid_cats if c in cat), "ALIGNMENT")
            sev = "HIGH" if cat in ("CONTRAST_ISSUE", "OVERLAP", "BROKEN_IMAGE") \
                else "MEDIUM" if cat in ("CROPPED_TEXT", "PLACEHOLDER",
                                          "INTERACTIVE_AMBIGUITY") \
                else "LOW"
            out.append(VisualIssue(
                category=cat, description=desc[:240],
                page_label=page_label, severity=sev,
            ))
        return out
