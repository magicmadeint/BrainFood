#!/usr/bin/env python3
"""
Quality Gates for BrainFood.
"""
import re
from typing import Optional, Any, Dict


FORBIDDEN_PATTERNS = [
    r"#\s*(TODO|FIXME|placeholder|insert logic|logic to find|rest of|implement)",
    r"//\s*(TODO|FIXME|placeholder)",
    r"\bTODO\b[:\s]",           # catches raw "TODO:" patterns
    r"\bFIXME\b",
    r"pass\s*#\s*(logic|TODO|placeholder)",
    r"raise NotImplementedError",
    r"your (code|logic|implementation) here",
]


def should_reject_content(text: str) -> bool:
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
    """More lenient: only rejects if name is missing or obvious low-quality markers are present."""
    if not isinstance(component, dict):
        return False
    if not component.get("name"):
        return False
    text = str(component.get("full_code", "")) + " " + str(component.get("description", ""))
    return not should_reject_content(text)


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
