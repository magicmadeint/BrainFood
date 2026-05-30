import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class AtomicRegistry:
    def __init__(self, data_dir: str = "~/.brainfood/registry"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, component: Dict[str, Any], category: str = "misc") -> bool:
        cat_dir = self.data_dir / category
        cat_dir.mkdir(exist_ok=True)
        name = component.get("name", "unknown_component")
        filepath = cat_dir / f"{name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(component, f, indent=2, ensure_ascii=False)
        return True

    def get(self, category: str, name: str) -> Optional[Dict]:
        filepath = self.data_dir / category / f"{name}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_components(self, category: str) -> List[str]:
        cat_dir = self.data_dir / category
        if not cat_dir.exists():
            return []
        return [p.stem for p in cat_dir.glob("*.json")]