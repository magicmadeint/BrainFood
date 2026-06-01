# BrainFood

**A lightweight, high-signal curation and atomic grounding layer for agent memory stacks.**

Most memory systems are good at storing information, but weak at protecting quality. They ingest noise, stubs, and low-signal content, which leads to context rot — especially painful in long-running coding agents and system work.

**BrainFood** fixes the upstream problem. It applies strict quality gates and maintains a clean **Atomic Registry** of structured, high-value components that agents can actually trust and use.

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

> **Optional but recommended:** `pip install wipedown` (from the malleable-cli branch) to enable security screening.

---

## Quick Start

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent()  # wipedown enabled by default

brain.ingest({
    "name": "retry_with_backoff",
    "category": "development",
    "full_code": "def retry_with_backoff(...): ..."
})

atomic = brain.get_atomic("development", "retry_with_backoff")
```

---

## BrainFoodAgent API

```python
BrainFoodAgent(data_dir="~/.brainfood/registry", enable_wipedown=True)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_wipedown` | `True` | Run WipeDown security check before curation. Flagged content goes to `flagged_for_review`. |

---

## For AI Agents (Integration Guide)

### How Wipedown + BrainFood Work Together

Wipedown is used **only as a security classifier**.

- BrainFood runs wipedown to get a simple status (clean vs flagged).
- **BrainFood always curates the original content** (not wipedown’s sanitized version).
- If wipedown flags something suspicious, the component is saved under the `flagged_for_review` category instead of being rejected.
- This allows you (or another agent) to still inspect it later.

You can disable it completely:

```python
brain = BrainFoodAgent(enable_wipedown=False)
```

### Recommended Patterns

```python
# Normal ingestion (wipedown runs by default)
brain.ingest(raw_text_or_url, category="development")

# Force a specific category even if flagged
brain.ingest(content, category="sensitive_research")

# Retrieve flagged items for review
flagged = brain.get_context("flagged_for_review")
```

### Quality & Rejection Rules

BrainFood will **hard reject** content containing obvious low-quality markers (`TODO`, `placeholder`, stubs, etc).

Wipedown-flagged content is **not rejected** — it is routed to `flagged_for_review` for later inspection.

---

## Project Philosophy

- Lean first
- Quality over volume
- Wipedown for security classification only
- Categories are fully dynamic

---

## License

MIT
