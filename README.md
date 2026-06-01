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

---

## Quick Start

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent()

# Ingest from structured dict (recommended)
brain.ingest({
    "name": "retry_with_backoff",
    "category": "development",
    "full_code": "def retry_with_backoff(...): ...",
    "description": "Handles retries with exponential backoff"
})

# Ingest raw text
brain.ingest("Useful markdown or code snippet...", category="development")

# Ingest from local file
brain.ingest("/path/to/component.md", category="development")

# Ingest from URL (basic fetching + cleaning)
brain.ingest("https://example.com/article", category="misc")

# Retrieve
atomic = brain.get_atomic("development", "retry_with_backoff")
score = brain.score_atomic("development", "retry_with_backoff")
context = brain.get_context("error handling")
```

---

## BrainFoodAgent API

```python
BrainFoodAgent(data_dir="~/.brainfood/registry")
```

### Core Methods

| Method | Description |
|--------|-------------|
| `ingest(content, category="misc")` | Ingests dict, raw text, file path, or URL. Runs quality gates automatically. |
| `get_atomic(category, name)` | Retrieve a specific high-signal component. |
| `get_context(query, max_items=5)` | Basic keyword-based retrieval of relevant components. |
| `score_atomic(category, name)` | Returns quality score (0.0–1.0) of a stored component. |

---

## For AI Agents (Integration Guide)

> **Read this section carefully.** This is the intended interface for agentic systems.

BrainFood is designed as a **thin, trustworthy filter** you can place in front of (or alongside) your existing memory systems. Its job is to protect you from low-quality, stubby, or placeholder content.

### Core Principles for Agents

1. **Prefer structured dict input** when possible. This gives the highest signal.
2. **Use `ingest()` as the single entry point** — it handles text, files, and URLs automatically.
3. **Always check quality** before trusting retrieved components (`score_atomic` or inspect `quality_score`).
4. **Treat BrainFood as a high-precision Atomic Registry**, not a full RAG system.

### Recommended Usage Patterns

#### Pattern 1: Structured Component Ingestion (Best)
```python
component = {
    "name": "unique_component_name",
    "category": "development",           # or quant_finance, biophysics_health, misc
    "full_code": "...",                    # full working code when available
    "description": "One-sentence purpose",
    "quality_score": 0.92                  # optional, will be calculated if missing
}
brain.ingest(component)
```

#### Pattern 2: Raw Text / Markdown Ingestion
```python
brain.ingest(raw_markdown_or_code, category="development")
```

#### Pattern 3: Retrieving for Grounding
```python
# Get exact component
comp = brain.get_atomic("development", "retry_with_backoff")

# Get relevant context for a task
context_pieces = brain.get_context("retry logic and error handling", max_items=5)
```

### Quality & Rejection Rules

BrainFood will **hard reject** content containing:
- `TODO`, `FIXME`, `placeholder`, `insert logic here`, `not implemented`, etc.
- Very short or empty-looking content

It will also refuse to overwrite a significantly higher-quality component with a lower-quality one.

### Data Directory

By default components are stored in `~/.brainfood/registry/`. You can override this:

```python
brain = BrainFoodAgent(data_dir="/custom/path/registry")
```

### Categories

Use these category names for best results:
- `development`
- `quant_finance`
- `biophysics_health`
- `misc`

---

## Project Philosophy

- **Lean first** — Easy to drop into existing stacks with minimal dependencies.
- **Quality over volume** — Aggressive filtering of noise and stubs.
- **Malleable by design** — Use as much or as little as you need.
- **Reference, not replacement** — Works alongside Cognee, QMD, GBrain, LangGraph, etc.

---

## Current Status

See `v0.1-scope.md` for the latest checklist of implemented vs planned features.

**Recently hardened (v0.1.1):**
- `AtomicRegistry.save()` now properly protects higher-quality components
- `curate_file()` and `curate_url()` are fully functional
- Improved name/description/code extraction
- Cleaner quality scoring with early rejection

---

## License

MIT
