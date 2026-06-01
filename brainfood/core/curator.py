#!/usr/bin/env python3
"""
Curator
"""
import json
import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any
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

    def _run_security_check(self, text: str, is_url: bool = False, target: str = "") -> Optional[str]:
        if not self.enable_wipedown:
            return None
        wipedown = self._get_wipedown()
        if not wipedown:
            return None
        try:
            result = wipedown.wipe_url(target) if is_url else wipedown.wipe_text(text)
            if result.get("status", "success").lower() not in ("success", "clean"):
                return "flagged_for_review"
        except Exception:
            pass
        return None

    def curate_text(self, text: str, category: str = "misc", source: str = "unknown") -> Optional[Dict[str, Any]]:
        if not text or len(text.strip()) < 15:
            return None
        if should_reject_content(text):
            return None

        name = self._extract_name(text) or f"component_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        description = self._extract_description(text) or "No description extracted."
        code = self._extract_code_block(text)

        final_category = self._run_security_check(text) or category

        return {
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

    def curate_file(self, filepath: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        path = Path(filepath)
        if not path.exists():
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None
        return self.curate_text(text, category=category, source=f"file:{filepath}")

    def curate_url(self, url: str, category: str = "misc") -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(url, headers={"User-Agent": "BrainFood/0.1"}, timeout=15)
            resp.raise_for_status()
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()[:8000]
        except Exception:
            return None
        return self.curate_text(text, category=category, source=f"url:{url}")

    def _extract_name(self, text: str) -> Optional[str]:
        for pattern in [r"^#\s+(.{3,60})$", r"^##\s+(.{3,60})$"]:
            m = re.search(pattern, text, re.MULTILINE)
            if m: return m.group(1).strip()
        for line in text.splitlines():
            line = line.strip()
            if 5 < len(line) < 80 and not line[0] in "#-*`d":
                return line
        return None

    def _extract_description(self, text: str) -> Optional[str]:
        for line in text.splitlines():
            if len(line.strip()) > 30:
                return line.strip()[:300]
        return None

    def _extract_code_block(self, text: str) -> Optional[str]:
        m = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        return m.group(1).strip() if m else None

    def ingest(self, content: Any, category: str = "misc") -> bool:
        if isinstance(content, dict):
            if not content or not validate_component(content):
                return False
            comp = dict(content)
            comp.setdefault("category", category)

            # Auto-derive description if missing
            if not comp.get("description"):
                if comp.get("full_code"):
                    comp["description"] = comp["full_code"].split("\n")[0][:120].strip()
                else:
                    comp["description"] = comp.get("name", "No description")

            if "quality_score" not in comp:
                txt = str(comp.get("full_code", "")) + " " + str(comp.get("description", ""))
                comp["quality_score"] = score_component(txt, comp.get("full_code"))

            return self.registry.save(comp)

        if isinstance(content, str):
            if content.startswith(("http://", "https://")):
                comp = self.curate_url(content, category)
            else:
                p = Path(content)
                comp = self.curate_file(content, category) if p.exists() else self.curate_text(content, category=category)
            return bool(comp and self.registry.save(comp))

        return False
