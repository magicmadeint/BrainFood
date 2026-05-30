# BrainFood v0.1 Scope

This document outlines what v0.1 of BrainFood aims to deliver and the current status of each area.

## Goal of v0.1

Create a **minimal but functional and installable** version of BrainFood that demonstrates the core value:

- Easy to install and use
- Quality gates that protect against low-quality content
- Atomic Registry for clean, structured components
- Simple `BrainFoodAgent` interface that can be plugged into other stacks

v0.1 is **not** trying to be feature-complete. It is a foundation to validate the approach and enable local testing.

## Current Status

### 1. Package & Structure
- [x] Package installs cleanly with `pip install -e .`
- [x] Proper `pyproject.toml` and `__init__.py` files

### 2. BrainFoodAgent (Main Public Interface)
- [x] `BrainFoodAgent` class exists and is importable
- [x] `ingest(content, category)` works with validation
- [x] `get_atomic(category, name)` retrieves components
- [x] `get_context(query)` returns stored components with basic relevance scoring
- [x] `score_atomic(category, name)` returns quality score (0.0–1.0)

### 3. Quality Gates
- [x] Basic rejection of low-quality / stub / TODO content
- [x] `score_component()` for quality scoring (0.0–1.0)

### 4. Atomic Registry
- [x] File-based storage for atomic components
- [x] Save, retrieve, and list by category
- [x] Configurable `data_dir` via `BrainFoodAgent`

### 5. Curator & Ingestion Pipeline
- [ ] Proper Curator that converts raw input into structured components
- [ ] Support for text, files, and URLs

### 6. Wipedown Integration
- [ ] Optional, clean integration with Wipedown for safe ingestion
- [ ] Config toggle for Wipedown

### 7. Testing & Examples
- [x] Basic working example that proves the core loop
- [ ] Unit tests for core classes
- [ ] More examples showing different use cases

### 8. Documentation & Readiness
- [x] Positioning and philosophy documented
- [x] Local testing instructions added
- [x] `v0.1-scope.md` created with detailed checklist
- [ ] Full documentation and API docs
- [ ] README fully synced with current implementation

## Overall Assessment

**v0.1 has a working, installable foundation.**

The core loop (ingest → quality gates → atomic registry → retrieval) is functional and testable locally. Quality scoring has been added to both the gates and the agent interface.

Major areas that still need work before a polished release:
- Curator depth and raw input handling
- Wipedown integration
- Testing
- Documentation

This scope document will be updated as v0.1 progresses.
