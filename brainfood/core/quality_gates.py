from typing import Any, Dict
import re

def should_reject_content(text: str) -> bool:
    if not isinstance(text, str):
        return True
    forbidden_patterns = [r'#\s*todo', r'#\s*placeholder', r'\bpass\s*#', r'insert logic here', r'todo:', r'\\TODO', r'not implemented']
    return any(re.search(p, text, re.IGNORECASE) for p in forbidden_patterns)

def validate_component(component: Dict[str, Any]) -> bool:
    if not isinstance(component, dict):
        return False
    if not component.get("name"):
        return False
    text_to_check = ""
    if "full_code" in component:
        text_to_check += str(component["full_code"])
    if "description" in component:
        text_to_check += str(component["description"])
    if should_reject_content(text_to_check):
        return False
    return True