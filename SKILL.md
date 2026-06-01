# BrainFood — Agent Skill Guide

This document is written for AI agents and coding assistants. It explains how to use BrainFood correctly and effectively.

## What BrainFood Is

BrainFood is a **lightweight, high-signal curation and atomic registry** for agent memory stacks.

Its job is to protect your context from low-quality, stubby, or noisy content before it enters long-term memory.

It sits between raw ingestion and your knowledge base / vector store.

## Core Design Principles

- **Quality over volume** — Aggressive filtering of TODOs, placeholders, and low-signal content.
- **Wipedown for security only** — Used strictly as a classifier. BrainFood always curates the original content.
- **Categories are fully dynamic** — Use whatever taxonomy makes sense for your workflow.
- **Flagged content is not discarded** — It goes to `flagged_for_review` for later inspection.
- **Lean by design** — Minimal dependencies. Wipedown is optional.

## Primary Interface

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent(
    data_dir="~/.brainfood/registry",   # optional
    enable_wipedown=True                # default = True
)
```

### Key Methods

| Method | Purpose |
|--------|---------|
| `ingest(content, category="misc")` | Main entry point. Accepts dict, raw text, file path, or URL. |
| `get_atomic(category, name)` | Retrieve one specific component. |
| `get_context(query, max_items=5)` | Keyword search across all categories. |
| `score_atomic(category, name)` | Get quality score of a stored component. |

## Ingestion Rules (Important)

### 1. Preferred Input: Structured Dict

```python
brain.ingest({
    "name": "retry_with_backoff",
    "category": "development",
    "full_code": "def retry_with_backoff(...): ...",
    "description": "Handles retries with exponential backoff"
})
```

### 2. Raw Text / Markdown / Code

```python
brain.ingest(some_markdown_or_code_block, category="prompt_engineering")
```

### 3. From File or URL

```python
brain.ingest("/path/to/component.md", category="infra")
brain.ingest("https://example.com/article", category="research")
```

## Wipedown Integration (Security)

- Wipedown runs **by default** (`enable_wipedown=True`).
- It is used **only** to determine security status.
- BrainFood **always curates the original content**, never wipedown’s sanitized version.
- If content is flagged:
  - It is **not rejected**.
  - It is saved under the category `flagged_for_review`.
- You can disable it with `enable_wipedown=False`.

## Category Strategy

Categories are **completely dynamic**. Do not limit yourself to any predefined list.

Good examples:
- `development`, `backend`, `frontend`, `devops`
- `trading`, `mev`, `quant_finance`
- `health`, `biohacking`, `light`
- `research`, `papers`, `ideas`

## Quality & Rejection Model

BrainFood hard-rejects content that contains:
- Obvious placeholder language (`TODO`, `FIXME`, `placeholder`, `insert logic here`, etc.)
- Very short or empty content

Flagged security content goes to `flagged_for_review` instead of being dropped.

## Recommended Agent Patterns

### Pattern 1: High-Signal Component Storage

When you produce good code, prompts, or logic, immediately ingest it:

```python
brain.ingest({
    "name": "my_new_utility",
    "category": "development",
    "full_code": code,
    "description": description
})
```

### Pattern 2: Retrieving Context

```python
relevant = brain.get_context("error handling and retries", max_items=6)
```

### Pattern 3: Reviewing Flagged Items

```python
flagged = brain.get_context("flagged_for_review")
for item in flagged:
    print(item["name"], item.get("source"))
```

## Data Location

By default: `~/.brainfood/registry/`

You can override this when creating the agent.

## When to Use BrainFood

Use it when you want:
- Clean, high-signal atomic components
- Protection against stubby or low-quality ingestion
- A simple registry you can query later
- Optional security classification without losing original content

## When NOT to Use BrainFood

Do not use it as a full vector database or long-term memory system. It is a **curation + atomic registry layer** meant to sit in front of tools like Cognee, Mem0, or your own vector store.

## Summary for Agents

- Always prefer structured dicts when ingesting.
- Let wipedown run by default (it only affects category).
- Use dynamic categories that match your actual workflow.
- Review `flagged_for_review` periodically.
- BrainFood protects quality. It does not replace your main memory system.
