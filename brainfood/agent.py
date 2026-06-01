#!/usr/bin/env python3
"""
BrainFoodAgent
"""
from typing import Optional, Dict, Any, List

try:
    from brainfood.core.atomic_registry import AtomicRegistry
    from brainfood.core.curator import Curator
except ImportError:
    from core.atomic_registry import AtomicRegistry
    from core.curator import Curator


class BrainFoodAgent:
    def __init__(self, data_dir: str = "~/.brainfood/registry", enable_wipedown: bool = True):
        self.registry = AtomicRegistry(data_dir)
        self.curator = Curator(registry=self.registry, enable_wipedown=enable_wipedown)

    def ingest(self, content: Any, category: str = "misc") -> bool:
        return self.curator.ingest(content, category=category)

    def get_atomic(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        return self.registry.get(category, name)

    def get_context(self, query: str, max_items: int = 5) -> List[Dict[str, Any]]:
        if not query:
            results = []
            for cat in self.registry.list_categories():
                results.extend(self.registry.list_by_category(cat)[:max_items])
            return results[:max_items]

        q = query.lower()
        scored = []
        for cat in self.registry.list_categories():
            for comp in self.registry.list_by_category(cat):
                text = " ".join([
                    str(comp.get("name", "")),
                    str(comp.get("description", "")),
                    str(comp.get("full_code", ""))
                ]).lower()
                if q in text:
                    scored.append(comp)

        return scored[:max_items]

    def score_atomic(self, category: str, name: str) -> float:
        return self.registry.score_atomic(category, name)
