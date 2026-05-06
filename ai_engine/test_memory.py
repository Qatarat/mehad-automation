"""
Test Memory — caches generated and validated Playwright test code.

When a spec is processed and tests pass (or have acceptable failures),
the test code is stored. On the next run, if the spec has not changed
and the BASE_URL is the same, the cached code is reused directly,
skipping the AI generation step entirely.

Cache key = sha256(spec_md + base_url)[:20]
Storage   = cache/tests/{slug}.json
"""
from __future__ import annotations
import hashlib, json, time, re
from pathlib import Path
from typing import Optional

CACHE_DIR = Path("cache/tests")


class TestMemory:
    """File-based cache for generated Playwright test code."""

    def __init__(self, cache_dir: str | Path = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _key(self, spec_md: str, base_url: str) -> str:
        raw = (spec_md.strip() + "|" + base_url.strip()).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:20]

    def _path(self, slug: str) -> Path:
        return self.cache_dir / f"{slug}.json"

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, slug: str, spec_md: str, base_url: str) -> Optional[dict]:
        """
        Return cached entry if the spec+url combo matches, else None.
        Entry dict has keys: code, test_count, passed, failed, saved_at, base_url
        """
        path = self._path(slug)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("key") != self._key(spec_md, base_url):
                return None  # spec or URL changed — invalidate
            # Quick sanity: code must still be valid Python
            code = data.get("code", "")
            if not code or code.count("def test_") == 0:
                return None
            compile(code, "<cache>", "exec")
            return data
        except Exception:
            return None  # corrupt or changed — regenerate

    def save(self, slug: str, spec_md: str, base_url: str,
             code: str, results: dict) -> None:
        """Persist test code + run results for future reuse."""
        path = self._path(slug)
        path.write_text(json.dumps({
            "slug":       slug,
            "key":        self._key(spec_md, base_url),
            "code":       code,
            "test_count": code.count("def test_"),
            "tests":      re.findall(r"def (test_\w+)", code),
            "passed":     results.get("passed", 0),
            "failed":     results.get("failed", 0),
            "total":      results.get("total", 0),
            "saved_at":   time.strftime("%Y-%m-%dT%H:%M:%S"),
            "base_url":   base_url,
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    def invalidate(self, slug: str) -> None:
        """Remove a cache entry (e.g. spec was deleted)."""
        p = self._path(slug)
        if p.exists():
            p.unlink()

    def list_entries(self) -> list[dict]:
        """Return metadata for all cached specs (for diagnostics)."""
        entries = []
        for p in sorted(self.cache_dir.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                entries.append({
                    "slug":       d.get("slug", p.stem),
                    "test_count": d.get("test_count", 0),
                    "passed":     d.get("passed", 0),
                    "failed":     d.get("failed", 0),
                    "saved_at":   d.get("saved_at", ""),
                    "base_url":   d.get("base_url", ""),
                })
            except Exception:
                pass
        return entries

    def stats(self) -> dict:
        entries = self.list_entries()
        return {
            "total_cached_specs": len(entries),
            "total_cached_tests": sum(e["test_count"] for e in entries),
            "entries":            entries,
        }
