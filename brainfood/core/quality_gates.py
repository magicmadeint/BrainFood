#!/usr/bin/env python3
"""
Quality Gates for BrainFood.

- should_reject_content(): For raw text (applies length + forbidden patterns)
- validate_component(): For structured dicts (more lenient, structure-focused)
"""
import re
from typing import Optional, Any, Dict


FORBIDDEN_PATTERNS = [
    # Stub markers
    r"\braise\s+NotImplementedError\b",
    r"pass\s*#\s*(logic|TODO|placeholder|implement)",
    # TODO/FIXME patterns (code comments)
    r"#\s*(TODO|FIXME|insert logic|logic to find|rest of|implement)",
    r"//\s*(TODO|FIXME)",
    r"\bTODO\b[:\s]",
    r"\bFIXME\b\s*[:\s]",
    # Placeholder markers (bracketed or standalone, not prose)
    r"\[placeholder\]",
    r"^\s*#\s*placeholder\s*$",
    # Template boilerplate
    r"your (code|logic|implementation) here",
]


def should_reject_content(text: str) -> bool:
    """For raw text ingestion. Applies both length and pattern checks."""
    if not text:
        return True
    lowered = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return True
    if len(text.strip()) < 15:
        return True
    return False


def validate_component(component: Any) -> bool:
    """
    For dict ingestion. More lenient than should_reject_content.
    Only rejects if:
    - Not a dict
    - Missing name
    - Contains obvious forbidden patterns
    Does NOT apply the 15-char length check.
    """
    if not isinstance(component, dict):
        return False
    if not component.get("name"):
        return False

    text = str(component.get("full_code", "")) + " " + str(component.get("description", ""))
    lowered = text.lower()

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return False

    return True


def score_component(text: str, code: Optional[str] = None) -> float:
    if not text:
        return 0.0
    score = 0.5
    if code and len(code) > 50:
        score += 0.25
    if len(text) > 200:
        score += 0.1
    if "def " in text or "class " in text:
        score += 0.1
    if text.count("example") > 3:
        score -= 0.05
    return max(0.0, min(1.0, round(score, 2)))
