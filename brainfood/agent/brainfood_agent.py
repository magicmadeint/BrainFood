from typing import Any, Dict, Optional, List
from brainfood.core.atomic_registry import AtomicRegistry
from brainfood.core.quality_gates import validate_component

class BrainFoodAgent:
    def __init__(self):
        self.registry = AtomicRegistry()

    def ingest(self, content: Dict[str, Any], category: str = "misc") -> bool:
        if validate_component(content):
            return self.registry.save(content, category)
        return False

    def get_atomic(self, category: str, name: str) -> Optional[Dict]:
        return self.registry.get(category, name)

    def get_context(self, query: str, max_items: int = 5) -> List[Dict]:
        results = []
        for cat in ["development", "misc"]:
            names = self.registry.list_components(cat)
            for name in names[:max_items]:
                comp = self.registry.get(cat, name)
                if comp:
                    results.append(comp)
        return results[:max_items]