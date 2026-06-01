#!/usr/bin/env python3
"""
BrainFoodAgent - Main public interface for BrainFood v0.1

Lightweight high-signal curation layer for agent memory stacks.
"""
from typing import Optional, Dict, Any, List

try:
    from brainfood.core.atomic_registry import AtomicRegistry
    from brainfood.core.curator import Curator
except ImportError:
    from core.atomic_registry import AtomicRegistry
    from core.curator import Curator


class BrainFoodAgent:
    def __init__(self, data_dir: str = "~/.brainfood/registry"):
        self.registry = AtomicRegistry(data_dir)
        self.curator = Curator(registry=self.registry)

    def ingest(self, content: Any, category: str = "misc") -> bool:
        """Ingest raw text, dict, file path, or URL. Returns True on success."""
        return self.curator.ingest(content, category=category)

    def get_atomic(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        return self.registry.get(category, name)

    def get_context(self, query: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """Dynamically searches across all existing categories."""
        results = []
        for cat in self.registry.list_categories():
            for comp in self.registry.list_by_category(cat):
                if query.lower() in str(comp).lower():
                    results.append(comp)
                    if len(results) >= max_items:
                        return results
        return results

    def score_atomic(self, category: str, name: str) -> float:
        return self.registry.score_atomic(category, name)
