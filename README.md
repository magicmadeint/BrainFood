# BrainFood

**A lightweight, high-signal curation and atomic grounding layer for agent memory stacks.**

BrainFood protects your agent memory from noise, stubs, and low-quality content. It applies strict quality gates and maintains a clean **Atomic Registry** of trustworthy components.

---

## Installation

```bash
git clone https://github.com/magicmadeint/BrainFood.git
cd BrainFood
git checkout v.0.1

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **Optional:** Install `wipedown` (malleable-cli branch) for built-in security classification.

---

## Quick Start

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent()                    # Wipedown enabled by default

# Ingest structured components (recommended)
brain.ingest({
    "name": "retry_with_backoff",
    "category": "development",
    "full_code": "def retry_with_backoff(...): ...",
    "description": "Handles retries with exponential backoff"
})

# Or ingest raw text, files, or URLs
brain.ingest("Some clean documentation or code...", category="docs")

atomic = brain.get_atomic("development", "retry_with_backoff")
```

---

## BrainFoodAgent

```python
BrainFoodAgent(data_dir="~/.brainfood/registry", enable_wipedown=True)
```

| Method              | Description                                      |
|---------------------|--------------------------------------------------|
| `ingest()`          | Ingest dict, text, file, or URL                  |
| `get_atomic()`      | Retrieve a specific component                    |
| `get_context()`     | Search across all categories                     |
| `score_atomic()`    | Get quality score of a component                 |

**`enable_wipedown`** (default `True`): Runs security classification. Flagged content is routed to `flagged_for_review` instead of being rejected.

---

## For AI Agents

BrainFood is designed to be used by agents. Key behaviors:

- **Wipedown** is used only as a security classifier (not for sanitization).
- BrainFood **always curates the original content**.
- Flagged items go to `flagged_for_review` (never silently dropped).
- Categories are fully dynamic.
- Dict ingestion is first-class and now properly validated + scored.

Disable security checks when needed:
```python
brain = BrainFoodAgent(enable_wipedown=False)
```

---

## Quality Model

- Hard rejects obvious low-quality content (`TODO`, `placeholder`, `NotImplementedError`, etc.)
- Wipedown-flagged content is preserved under `flagged_for_review`
- Higher-scoring components are protected from being overwritten by lower-scoring ones

---

## Project Status (v0.1.1)

- Core functionality stable and well tested
- Strong support for both string and structured dict ingestion
- Clean Wipedown integration (status only)
- 79+ tests passing

See `SKILL.md` for detailed guidance aimed at AI agents.

---

## License

MIT
