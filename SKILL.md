# BrainFood — Agent Skill Guide (v0.1)

**Written specifically for AI agents, coding assistants, and autonomous systems.**

This is your canonical reference for using BrainFood correctly and efficiently.

---

## What BrainFood Is

BrainFood is a **lightweight, high-signal atomic registry** for agent memory.  
It filters out noise, stubs, and low-quality content while storing clean, executable components in a structured filesystem registry.

---

## Architecture Map

```
BrainFood/                          ← repo root
├── brainfood/
│   ├── __init__.py                 ← package init (__version__ = "0.1.1")
│   ├── agent.py                    ← BrainFoodAgent (main public API)
│   ├── core/
│   │   ├── atomic_registry.py      ← Persistent JSON storage + quality protection
│   │   ├── curator.py              ← Ingestion, quality gates, wipedown integration
│   │   └── quality_gates.py        ← Rejection rules + scoring logic
│   └── curator/
│       └── wipedown.py             ← Wipedown SDK bridge (optional dependency)
├── test_comprehensive.py           ← Full test suite (run from repo root)
├── SKILL.md                        ← This file
├── BUGS.md                         ← Bug tracker (all fixes committed to v.0.1)
└── README.md
```

**Default Data Location:** `~/.brainfood/registry/<category>/<sanitized_name>.json`

Each stored component is a JSON object containing:
- `name`, `category`, `quality_score`
- `full_code`, `description`, `source`, `raw_text` (truncated to 2000 chars)
- `created_at` (ISO 8601 UTC), `wipedown_checked` (bool)

---

## Core Design Principles (Internalize These)

- **Quality over volume** — Aggressive rejection of stubs and low-signal content.
- **Wipedown = Security Classifier Only** — BrainFood runs WipeDown for status only. It **always** curates the **original** content, never the sanitized version.
- **Categories are fully dynamic** — No hardcoded list. Create whatever you need.
- **Flagged content** → routed to `flagged_for_review` category (never silently dropped).
- **Dict ingestion is preferred** — More reliable and predictable than raw text ingestion.

---

## Primary API

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent(
    data_dir="~/.brainfood/registry",   # optional, default is ~/.brainfood/registry
    enable_wipedown=True                # default = True
)
```

### Key Methods

| Method | Parameters | Purpose |
|--------|-----------|---------|
| `ingest(content, category=...)` | `content` (dict, str, file path, or URL) | Main entry point. Ingestion priority: Dict > String > File > URL |
| `get_atomic(category, name)` | `category`, `name` | Retrieve exact component by key |
| `get_context(query, max_items=5)` | `query` (string), `max_items` (int) | Keyword search across all categories |
| `score_atomic(category, name)` | `category`, `name` | Get quality score (0.0–1.0) |
| `registry.list_categories()` | — | List all category names in the registry |

### Ingestion: Structured Dict (Preferred)

```python
brain.ingest({
    "name": "retry_with_backoff",
    "category": "development",
    "full_code": "def retry_with_backoff(func): ...",
    "description": "Exponential backoff retry decorator"
})
```

Also supports raw strings, local file paths, and URLs.

---

## Quality & Rejection Rules

### FORBIDDEN_PATTERNS (from `brainfood/core/quality_gates.py`)

BrainFood hard-rejects content containing **any** of these (case-insensitive):

```
\bplaceholder\b
#\s*(TODO|FIXME|insert logic|logic to find|rest of|implement)
//\s*(TODO|FIXME)
\bTODO\b[:\s]
\bFIXME\b
pass\s*#\s*(logic|TODO|placeholder)
raise NotImplementedError
your (code|logic|implementation) here
```

### Length Rule (raw text only)

- Content < 15 chars after stripping → rejected
- **Note:** This check applies to *raw text* ingestion, **not** dict ingestion. Structured dicts bypass the length check.

### Dict Validation (`validate_component`)

Dicts are validated differently — only rejected if:
- Not a dict
- Missing `name`
- Contains forbidden patterns in `full_code` or `description`

**Important:** Dicts do **not** get a length check. A valid dict with short code (e.g., `{"name": "x", "full_code": "x=1"}`) will be accepted.

---

## Wipedown Behavior

| Scenario | Behavior |
|----------|----------|
| `enable_wipedown=True` + WipeDown installed | Security classification runs; flagged → `flagged_for_review` |
| `enable_wipedown=True` + WipeDown **not** installed | Gracefully skips (no crash). Category unchanged. |
| `enable_wipedown=False` | Security check disabled entirely. Category unchanged. |

**Key:** BrainFood **always** curates the **original** content, never WipeDown's sanitized version. WipeDown only affects the category assignment.

---

## Known Gotchas

1. **Dict ingestion does NOT auto-derive description** — `curate_text()` extracts a description from text input, but `ingest(dict)` does not add one if missing. Provide `"description"` in your dict if you want one.

2. **Short but valid code snippets are accepted via dict** — The 15-char length check only applies to raw text, not structured dicts.

3. **Run tests after changes:** `python3 test_comprehensive.py`

4. **Namespace collision was fixed** — The old `brainfood/agent/` directory has been removed to prevent import ambiguity.

---

## Testing & Verification

```bash
cd /home/devmode/magic/BrainFood
python3 test_comprehensive.py
```

Always run this after modifying BrainFood.

---

## When NOT to Use BrainFood

- **Raw long-form documents** — Use a vector DB instead
- **Low-quality/exploratory notes** — BrainFood rejects stubby content
- **One-off scripts** that don't need long-term grounding

---

## Summary for Agents

- Always prefer structured dicts when ingesting (more reliable than text).
- Let WipeDown run by default (graceful skip if not installed).
- Use dynamic categories matching your workflow.
- Review `flagged_for_review` periodically.
- BrainFood protects quality at ingestion time. It does not replace your main memory system.
