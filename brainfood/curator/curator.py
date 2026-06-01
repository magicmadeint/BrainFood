"""
DEPRECATED / REMOVED

This file contained a broken, duplicate implementation of Curator
with an IndentationError and different semantics.

It has been replaced by the canonical implementation in:
    brainfood.core.curator.Curator

Please migrate to:
    from brainfood.core.curator import Curator
    or use BrainFoodAgent
"""
raise ImportError(
    "brainfood.curator.curator is deprecated and was broken. "
    "Use 'from brainfood.core.curator import Curator' instead."
)
