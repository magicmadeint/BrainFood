# BrainFood

**A lightweight, high-signal curation and atomic grounding layer for agent memory stacks.**

Most memory systems are good at storing information, but weak at protecting quality. They ingest noise, stubs, and low-signal content, which leads to context rot — especially painful in long-running coding agents and system work.

**BrainFood** fixes the upstream problem. It applies strict quality gates and maintains a clean **Atomic Registry** of structured, high-value components that agents can actually trust and use.

### The Goal

BrainFood is built as a **thin, optional layer** — not another full memory platform. It’s designed to be **easy to drop into existing stacks** (Cognee, QMD, GBrain, LangGraph, custom agents, etc.) with minimal friction.

You don’t have to rip out what you already have. You just get better quality and cleaner atomic components on top.

---

## BrainFoodAgent — The Easy Plug-in

The main way to use BrainFood is through a simple, stable interface:

```python
from brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent()

# Get high-signal context
context = brain.get_context("How should error handling work here?")

# Pull a clean atomic component directly
component = brain.get_atomic("development", "error_handling")
```

This is intentionally lightweight so agents can start using it with almost zero setup.

---

## How It Fits In Your Stack

BrainFood works **alongside** your existing tools:

| Your Current Stack     | How BrainFood Helps                              |
|------------------------|--------------------------------------------------|
| Cognee                 | Adds quality curation + atomic components        |
| QMD                    | Adds structured/atomic retrieval                 |
| GBrain / Custom        | Adds a clean quality + atomic layer              |
| LangGraph / CrewAI     | Drop `BrainFoodAgent` into your agent loop       |

Use it standalone, as a pre-filter, or as an extra high-signal source. Your choice.

---

## Core Concepts

| Concept             | What It Does                                      | Why It Matters |
|---------------------|---------------------------------------------------|----------------|
| **Quality Gates**   | Rejects low-quality, stubby, or noisy content     | Prevents context rot |
| **Atomic Registry** | Stores clean, structured, production-ready components | Reliable grounding for code work |
| **BrainFoodAgent**  | Simple public interface (`get_context`, `get_atomic`) | Easy to plug into any agent |
| **Optional Layers** | Wipedown, custom ingestion, graph — all toggleable | High adaptability |

---

## Project Philosophy

- **Lean first** — We optimize for easy integration over building everything ourselves.
- **Quality over volume** — We aggressively filter noise.
- **Malleable by design** — You should be able to use as much or as little as you want.
- **Reference, not replacement** — Works with (not instead of) tools like Cognee, QMD, and GBrain.

---

## Status

Early development. Core ideas and structure are being built now.

More documentation and examples coming as we ship the first usable version.

---

## License

MIT