import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class AtomicRegistry:
    def __init__(self, data_dir: str = "~/.brainfood/registry"):
        self.base_path = Path(data_dir).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _validate_category(self, category: str) -> str:
        """Validate category name to prevent path traversal."""
        if not category:
            raise ValueError("Category name cannot be empty")
        clean = category.strip("/\\")
        if ".." in clean:
            raise ValueError(f"Invalid category name: {category!r}")
        return clean

    def _ensure_category(self, category: str) -> Path:
        """Ensure category directory exists (supports nested categories with /)."""
        self._validate_category(category)
        cat_path = (self.base_path / category).resolve()
        if not str(cat_path).startswith(str(self.base_path.resolve())):
            raise ValueError(f"Invalid category name: {category!r}")
        cat_path.mkdir(parents=True, exist_ok=True)
        return cat_path

    def _get_path(self, component: Dict[str, Any]) -> Path:
        category = component.get("category", "misc")
        name = component.get("name", "unnamed")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        cat_path = self._ensure_category(category)
        resolved = (cat_path / f"{safe_name}.json").resolve()
        if not str(resolved).startswith(str(self.base_path.resolve())):
            raise ValueError(f"Invalid category or name in component")
        return resolved

    def save(self, component: Dict[str, Any]) -> bool:
        filepath = self._get_path(component)

        if filepath.exists():
            try:
                existing = json.loads(filepath.read_text(encoding="utf-8"))
                existing_score = float(existing.get("quality_score", 0.0))
                new_score = float(component.get("quality_score", 0.0))

                if existing_score > new_score + 0.15:
                    print(f"⚠️  AtomicRegistry: Skipping write for '{component.get('name')}'. Existing score higher ({existing_score} vs {new_score}).")
                    return False

                # Preserve existing fields that aren't in the new component.
                # This prevents accidental loss of manually added metadata,
                # notes, or custom keys when overwriting a higher-scoring version.
                for key, value in existing.items():
                    if key not in component:
                        component[key] = value
            except Exception:
                pass

        component = dict(component)
        component.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        component["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            filepath.write_text(json.dumps(component, indent=2, ensure_ascii=False), encoding="utf-8")
            return True
        except Exception as e:
            print(f"❌ AtomicRegistry save failed: {e}")
            return False

    def get(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        self._validate_category(category)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        cat_path = (self.base_path / category)
        filepath = cat_path / f"{safe_name}.json"
        if not filepath.exists():
            return None
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        self._validate_category(category)
        cat_path = self.base_path / category
        if not cat_path.exists():
            return []
        results = []
        for f in cat_path.glob("*.json"):
            try:
                results.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return results

    def list_categories(self) -> List[str]:
        if not self.base_path.exists():
            return []
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]

    def score_atomic(self, category: str, name: str) -> float:
        comp = self.get(category, name)
        return float(comp.get("quality_score", 0.0)) if comp else 0.0
