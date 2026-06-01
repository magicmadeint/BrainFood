#!/usr/bin/env python3
"""
Curator - Converts raw input into validated, high-signal atomic components for BrainFood.

Wipedown is used *only* as a security status classifier.
BrainFood always curates the original content.
"""
import json
import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

try:
    from brainfood.core.quality_gates import should_reject_content, score_component, validate_component
    from brainfood.core.atomic_registry import AtomicRegistry
except ImportError:
    from quality_gates import should_reject_content, score_component, validate_component
    from atomic_registry import AtomicRegistry


class Curator:
    def __init__(self, registry: Optional[AtomicRegistry] = None, enable_wipedown: bool = True):
        self.registry = registry or AtomicRegistry()
        self.enable_wipedown = enable_wipedown
        self._wipedown = None

    def _get_wipedown(self):
        if self._wipedown is not None:
            return self._wipedown
        try:
            from wipedown import WipeDown
            self._wipedown = WipeDown()
        except ImportError:
            self._wipedown = False
        return self._wipedown

    def _run_security_check(self, text: str, is_url: bool = False, target: str = "") -> str:
        if not self.enable_wipedown:
            return None
        wipedown = self._get_wipedown()
        if not wipedown:
            return None
        try:
            if is_url:
                result = wipedown.wipe_url(target)
            else:
                result = wipedown.wipe_text(text)
            status = result.get("status", "success")
            if status and status.lower() not in ("success", "clean"):
                print(f"⚠️  WipeDown flagged content. Routing to 'flagged_for_review'.")
                return "flagged_for_review"
        except Exception as e:
            print(f"⚠️  WipeDown check failed (non-fatal): {e}")
        return None

    def curate_text(self, text: str, category: str = "misc", source: str = "unknown") -> Optional[Dict[str, Any]]:
        if not text or len(text.strip()) < 20:
            return None
        if should_reject_content(text):
            return None

        name = self._extract_name(text) or f"component_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        description = self._extract_description(text) or "No description extracted."
        code = self._extract_code_block(text)

        flagged_category = self._run_security_check(text)
        final_category = flagged_category or category

        component = {
            "name": name,
            "category": final_category,
            "description": description,
            "source": source,
            "full_code": code,
            "raw_text": text[:2000],
            "quality_score": score_component(text, code),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "wipedown_checked": self.enable_wipedown,
        }
        return component

    def curate_file(self, filepath: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        path = Path(filepath)
        if not path.exists():
            print(f"❌ Curator: File not found: {filepath}")
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"❌ Curator: Failed to read file {filepath}: {e}")
            return None

        flagged = self._run_security_check(text)
        final_cat = flagged or category
        return self.curate_text(text, category=final_cat, source=f"file:{filepath}")

    def curate_url(self, url: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        try:
            headers = {"User-Agent": "BrainFood-Curator/0.1"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            text = resp.text
        except Exception as e:
            print(f"❌ Curator: Failed to fetch URL {url}: {e}")
            return None

        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.I | re.S)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        flagged = self._run_security_check(text, is_url=True, target=url)
        final_cat = flagged or category
        return self.curate_text(text[:8000], category=final_cat, source=f"url:{url}")

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

    def ingest(self, content: Any, category: str = "misc", source: str = "unknown") -> bool:
        component = None

        if isinstance(content, dict):
            if not validate_component(content):
                return False
            component = dict(content)
            component.setdefault("category", category)
            if "quality_score" not in component:
                text_for_scoring = str(component.get("full_code", "")) + " " + str(component.get("description", ""))
                component["quality_score"] = score_component(text_for_scoring, component.get("full_code"))

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
