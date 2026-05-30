from typing import Dict, Any
import re

def should_reject_content(text: str) -> bool:
    if not isinstance(text, str):
        return True
    forbidden = [r'#\s*todo', r'#\s*placeholder', r'\bpass\s*#', 
                 r'insert logic here', r'todo:', r'\\TODO', r'not implemented']
    return any(re.search(p, text, re.IGNORECASE) for p in forbidden)

def validate_component(component: Dict[str, Any]) -> bool:
    if not isinstance(component, dict):
        return False
    if not component.get("name"):
        return False
    text = str(component.get("full_code", "")) + str(component.get("description", ""))
    return not should_reject_content(text)

def score_component(component: Dict[str, Any]) -> float:
    """
    Returns a quality score between 0.0 and 1.0.
    Higher = better quality component.
    """
    if not isinstance(component, dict):
        return 0.0

    score = 0.0
    max_score = 5.0

    if component.get("name"):
        score += 1.0

    full_code = str(component.get("full_code", ""))
    if full_code and len(full_code) > 20:
        score += 2.0
        if len(full_code) > 100:
            score += 0.5

    if component.get("description") or component.get("title"):
        score += 1.0

    if component.get("dependencies"):
        score += 0.5

    if len(full_code) < 10:
        score -= 1.0

    return max(0.0, min(1.0, score / max_score))
