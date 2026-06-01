 """
brainfood/curator/curator.py

Basic Curator with support for wipedown_metadata.
"""

from typing import Optional, Dict, Any

try:
    from brainfood.core.quality_gates import should_reject_content, validate_component, score_component
except ImportError:
    def should_reject_content(text: str) -> bool:
        return False
    def validate_component(component: Dict[str, Any]) -> bool:
        return bool(component.get("name"))
    def score_component(component: Dict[str, Any]) -> float:
        return 0.8

try:
    from brainfood.core.atomic_registry import AtomicRegistry
except ImportError:
    AtomicRegistry = None


MIN_QUALITY_THRESHOLD = 0.75


class Curator:
    def __init__(self, data_dir: Optional[str] = None):
        if AtomicRegistry:
            self.registry = AtomicRegistry(data_dir=data_dir) if data_dir else AtomicRegistry()
        else:
            self.registry = None

    def curate_text(
        self,
        raw_text: str,
        category: str = "misc",
        source: str = "text-input",
        force_name: Optional[str] = None,
        wipedown_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:

        if not raw_text or len(raw_text.strip()) < 15:
            return None

        # Basic extraction (you can expand this)
        name = force_name or self._guess_name(raw_text)
        description = self._guess_description(raw_text)

        component = {
            "name": name,
            "category": category.lower(),
            "description": description,
            "full_code": raw_text,
            "language": "markdown",
            "metadata": {
                "char_count": len(raw_text),
                "source": source
            }
        }

        if wipedown_metadata:
            component["wipedown_metadata"] = wipedown_metadata

        if should_reject_content(raw_text):
            print(f"\ud83d\udeab Curator rejected content")
            return None

        if not validate_component(component):
            return None

        component["quality_score"] = round(score_component(component), 3)

        if component["quality_score"] < MIN_QUALITY_THRESHOLD:
            return None

        if self.registry:
            self.registry.save(component, category=category)

        print(f"\u2705 Curator accepted: {name} [{category}]")
        return component

    def _guess_name(self, text: str) -> str:
        for line in text.splitlines()[:10]:
            clean = line.strip()
            if clean.startswith("#"):
                return clean.lstrip("# ").lower().replace(" ", "_")[:50]
        return "unnamed_component"

    def _guess_description(self, text: str) -> str:
        for line in text.splitlines():
            if len(line.strip()) > 40:
                return line.strip()[:200]
        return "Component curated via WipeDown + BrainFood"
