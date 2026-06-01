import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class AtomicRegistry:
    def __init__(self, data_dir: str = "~/.brainfood/registry"):
        self.base_path = Path(data_dir).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        for category in ["development", "quant_finance", "biophysics_health", "misc"]:
            (self.base_path / category).mkdir(exist_ok=True)

    def _get_path(self, component: Dict[str, Any]) -> Path:
        category = component.get("category", "misc")
        name = component.get("name", "unnamed")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return self.base_path / category / f"{safe_name}.json"

    def save(self, component: Dict[str, Any]) -> bool:
        """
        Save component. Returns True on success.
        Refuses to overwrite if existing component has significantly higher quality score.
        """
        filepath = self._get_path(component)

        if filepath.exists():
            try:
                existing = json.loads(filepath.read_text(encoding="utf-8"))
                existing_score = float(existing.get("quality_score", 0.0))
                new_score = float(component.get("quality_score", 0.0))

                if existing_score > new_score + 0.15:
                    print(
                        f"⚠️  AtomicRegistry: Skipping write for '{component.get('name')}'. "
                        f"Existing score ({existing_score:.2f}) is significantly higher than new score ({new_score:.2f})."
                    )
                    return False
            except Exception:
                print(f"⚠️  AtomicRegistry: Could not read existing file at {filepath}. Proceeding with write.")

        # Add metadata
        component = dict(component)
        component.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        component["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            filepath.write_text(
                json.dumps(component, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            return True
        except Exception as e:
            print(f"❌ AtomicRegistry: Failed to write {filepath}: {e}")
            return False

    def get(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        filepath = self.base_path / category / f"{safe_name}.json"
        if not filepath.exists():
            return None
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        cat_path = self.base_path / category
        results = []
        for f in cat_path.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                results.append(data)
            except Exception:
                continue
        return results

    def score_atomic(self, category: str, name: str) -> float:
        comp = self.get(category, name)
        if comp:
            return float(comp.get("quality_score", 0.0))
        return 0.0
