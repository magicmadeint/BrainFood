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
        """
        Get relevant context using simple keyword matching.
        Scores components based on how many query words appear in name/title/content.
        """
        query_words = set(query.lower().split())
        scored = []

        for category in ["development", "misc"]:
            names = self.registry.list_components(category)
            for name in names:
                comp = self.registry.get(category, name)
                if not comp:
                    continue

                # Build searchable text
                text = " ".join([
                    str(comp.get("name", "")),
                    str(comp.get("title", "")),
                    str(comp.get("full_code", "")),
                    str(comp.get("description", ""))
                ]).lower()

                # Simple score = number of matching query words
                score = sum(1 for word in query_words if word in text)

                if score > 0:
                    scored.append((score, comp))

        # Sort by score descending and return top results
        scored.sort(key=lambda x: x[0], reverse=True)
        return [comp for score, comp in scored[:max_items]]