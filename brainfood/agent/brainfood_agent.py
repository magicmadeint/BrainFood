from typing import Any, Dict, Optional, List
from brainfood.core.atomic_registry import AtomicRegistry
from brainfood.core.quality_gates import validate_component, score_component

class BrainFoodAgent:
    def __init__(self, data_dir: str = "~/.brainfood/registry"):
        self.registry = AtomicRegistry(data_dir=data_dir)

    def ingest(self, content: Dict[str, Any], category: str = "misc") -> bool:
        if validate_component(content):
            return self.registry.save(content, category)
        return False

    def get_atomic(self, category: str, name: str) -> Optional[Dict]:
        return self.registry.get(category, name)

    def get_context(self, query: str, max_items: int = 5) -> List[Dict]:
        query_words = set(query.lower().split())
        scored = []

        for cat in ["development", "misc"]:
            for name in self.registry.list_components(cat):
                comp = self.registry.get(cat, name)
                if not comp:
                    continue
                text = " ".join([
                    str(comp.get("name", "")),
                    str(comp.get("title", "")),
                    str(comp.get("full_code", "")),
                    str(comp.get("description", ""))
                ]).lower()
                score = sum(1 for word in query_words if word in text)
                if score > 0:
                    scored.append((score, comp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [comp for score, comp in scored[:max_items]]

    def score_atomic(self, category: str, name: str) -> float:
        """Return quality score (0.0 - 1.0) for a stored component."""
        comp = self.registry.get(category, name)
        if not comp:
            return 0.0
        return score_component(comp)
