#!/usr/bin/env python3
"""
Curator - Converts raw input into validated, high-signal atomic components for BrainFood.

Design goals:
- Pure Python core (no mandatory LLM dependency)
- Early zero-trust rejection of low-quality / stub content
- Working curate_file() and curate_url() implementations
- More robust extraction than pure line-length guessing
"""
import json
import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

try:
    from brainfood.core.quality_gates import should_reject_content, score_component
    from brainfood.core.atomic_registry import AtomicRegistry
except ImportError:
    # Fallback for direct execution
    from quality_gates import should_reject_content, score_component
    from atomic_registry import AtomicRegistry


class Curator:
    def __init__(self, registry: Optional[AtomicRegistry] = None):
        self.registry = registry or AtomicRegistry()

    # ------------------------------------------------------------------
    # Core text curation
    # ------------------------------------------------------------------
    def curate_text(
        self,
        text: str,
        category: str = "misc",
        source: str = "unknown"
    ) -> Optional[Dict[str, Any]]:
        """
        Main entry point. Takes raw text and returns a structured component dict
        or None if rejected.
        """
        if not text or len(text.strip()) < 20:
            return None

        if should_reject_content(text):
            return None

        # Extract best-effort name and description
        name = self._extract_name(text) or f"component_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        description = self._extract_description(text) or "No description extracted."

        # Try to extract code if present
        code = self._extract_code_block(text)

        component = {
            "name": name,
            "category": category,
            "description": description,
            "source": source,
            "full_code": code,
            "raw_text": text[:2000],
            "quality_score": score_component(text, code),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if should_reject_content(json.dumps(component)):
            return None

        return component

    # ------------------------------------------------------------------
    # File and URL support (fixed from broken stubs)
    # ------------------------------------------------------------------
    def curate_file(self, filepath: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        """Read a local file and curate it."""
        path = Path(filepath)
        if not path.exists():
            print(f"❌ Curator: File not found: {filepath}")
            return None

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"❌ Curator: Failed to read file {filepath}: {e}")
            return None

        return self.curate_text(text, category=category, source=f"file:{filepath}")

    def curate_url(self, url: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        """Fetch URL content and curate it (basic, no JS rendering)."""
        try:
            headers = {"User-Agent": "BrainFood-Curator/0.1"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            text = resp.text
        except Exception as e:
            print(f"❌ Curator: Failed to fetch URL {url}: {e}")
            return None

        # Very basic HTML stripping
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.I | re.S)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return self.curate_text(text[:8000], category=category, source=f"url:{url}")

    # ------------------------------------------------------------------
    # Improved extraction
    # ------------------------------------------------------------------
    def _extract_name(self, text: str) -> Optional[str]:
        for pattern in [r"^#\s+(.{3,60})$", r"^##\s+(.{3,60})$"]:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()

        for line in text.splitlines():
            line = line.strip()
            if 5 < len(line) < 80 and not line.startswith(("#", "-", "*", "`", "def ", "class ")):
                return line
        return None

    def _extract_description(self, text: str) -> Optional[str]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            return None
        start_idx = 1 if len(lines) > 1 else 0
        for i in range(start_idx, min(start_idx + 4, len(lines))):
            if len(lines[i]) > 30:
                return lines[i][:300]
        return None

    def _extract_code_block(self, text: str) -> Optional[str]:
        match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def ingest(
        self,
        content: Any,
        category: str = "misc",
        source: str = "unknown"
    ) -> bool:
        component = None

        if isinstance(content, dict):
            component = content
            component.setdefault("category", category)
        elif isinstance(content, str):
            if content.startswith(("http://", "https://")):
                component = self.curate_url(content, category)
            elif Path(content).exists():
                component = self.curate_file(content, category)
            else:
                component = self.curate_text(content, category, source)
        else:
            return False

        if not component:
            return False

        return self.registry.save(component)
