# BrainFood

**A lightweight, high-signal curation and atomic grounding layer for agent memory stacks.**

Most memory systems are good at storing information, but weak at protecting quality. They ingest noise, stubs, and low-signal content, which leads to context rot — especially painful in long-running coding agents and system work.

**BrainFood** fixes the upstream problem. It applies strict quality gates and maintains a clean **Atomic Registry** of structured, high-value components that agents can actually trust and use.

### The Goal

BrainFood is built as a **thin, optional layer** — not another full memory platform. It’s designed to be **easy to drop into existing stacks** (Cognee, QMD, GBrain, LangGraph, custom agents, etc.) with minimal friction.

You don’t have to rip out what you already have. You just get better quality and cleaner atomic components on top.

---

## Installation

bash
git clone https://github.com/magicmadeint/BrainFood.git
cd BrainFood
git checkout v.0.1

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

Quick Start
Pythonfrom brainfood.agent import BrainFoodAgent

brain = BrainFoodAgent()

# Ingest a clean component
component = {
    "name": "retry_with_backoff",
    "category": "development",
    "language": "python",
    "full_code": "def retry_with_backoff(...): ...",
    "description": "Handles retries with exponential backoff"
}

brain.ingest(component, category="development")

# Retrieve it directly
atomic = brain.get_atomic("development", "retry_with_backoff")

# Get relevant context
context = brain.get_context("error handling and retries")

# Check quality score of a component
score = brain.score_atomic("development", "retry_with_backoff")

BrainFoodAgent API
BrainFoodAgent(data_dir="~/.brainfood/registry")
Create an agent. You can optionally pass a custom data_dir to change where atomic components are stored.
ingest(content: dict, category: str = "misc") -> bool
Ingest a component. It will be validated through Quality Gates before being saved.
get_atomic(category: str, name: str) -> dict | None
Retrieve a specific atomic component by category and name.
get_context(query: str, max_items: int = 5) -> list[dict]
Get relevant components using basic keyword-based relevance scoring.
score_atomic(category: str, name: str) -> float
Get the quality score (0.0 – 1.0) of a stored component. Higher = better.

Current Development Status
For the latest checklist of what’s built vs what’s still in progress, see:
→ v0.1-scope.md

Project Philosophy

Lean first — We optimize for easy integration over building everything ourselves.
Quality over volume — We aggressively filter noise.
Malleable by design — You should be able to use as much or as little as you want.
Reference, not replacement — Works with (not instead of) tools like Cognee, QMD, and GBrain.


License
MIT
text
