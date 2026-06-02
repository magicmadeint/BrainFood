"""
brainfood/curator/wipedown.py

Native integration with WipeDown SDK (from malleable-cli branch).
Updated to use canonical Curator.
"""

from pathlib import Path
from typing import Optional, Dict, Any

try:
    from wipedown.engine import WipeDown
except ImportError:
    WipeDown = None


def curate_with_wipedown(
    target: str,
    category: str = "misc",
    registry=None,
    enable_wipedown: bool = True,
) -> Optional[Dict[str, Any]]:
    """Curate content through WipeDown security classification.

    Args:
        target: URL or local file path to curate.
        category: Target category (may be overridden to 'flagged_for_review').
        registry: Optional pre-configured AtomicRegistry. If None, uses the
            default ``~/.brainfood/registry``. Passing a custom registry ensures
            the output lands in the user's configured data directory.
        enable_wipedown: Whether to run WipeDown classification (default True).
    """
    if not WipeDown:
        print("\u274c 'wipedown' package not found.")
        return None

    try:
        firewall = WipeDown()

        if target.startswith(("http://", "https://")):
            result = firewall.wipe_url(target)
        else:
            path = Path(target).expanduser().resolve()
            if not path.exists():
                print(f"\u274c File not found: {path}")
                return None
            with open(path, "r", encoding="utf-8") as f:
                file_text = f.read()
            result = firewall.wipe_text(file_text)

        if result.get("error"):
            print(f"\u274c WipeDown error: {result.get('error')}")
            return None

        if result.get("status") == "flagged":
            category = "flagged_for_review"

        content = result.get("content", "")

        from brainfood.core.curator import Curator

        return Curator(registry=registry, enable_wipedown=enable_wipedown).curate_text(
            text=content,
            category=category,
            source=result.get("source", target),
        )

    except Exception as e:
        print(f"\u274c Unexpected error in curate_with_wipedown: {e}")
        return None
