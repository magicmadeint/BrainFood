# BrainFood

**A lightweight, high-signal curation and atomic grounding layer for local AI agent workflows.**

Most agent memory systems are good at storing information but weak at protecting quality. They often ingest noisy, low-signal, or stubby content, which leads to *context rot* over time. BrainFood addresses this by applying strict quality gates during ingestion and maintaining a clean **Atomic Registry** of structured, high-value components that agents can reliably use for code editing and system work.

BrainFood is designed to work as a layer alongside existing tools such as [Cognee](https://github.com/cognee-ai/cognee), QMD, and GBrain. It does not aim to replace full memory graphs. Instead, it focuses on **curation quality** and **atomic cleanliness**.

---

## Core Promise

> Feed your agents cleaner, more reliable, and better-structured context with significantly less noise and context rot.

## Default Ingestion

BrainFood includes **Wipedown** integration enabled by default. Wipedown serves as the zero-trust semantic scraping and prompt injection defense layer. Users can easily disable it via configuration if they prefer to use their own ingestion pipeline.

---

## Architecture Overview

### Core Philosophy

- Prioritize **quality curation** over volume
- Favor **atomic, structured components** over fuzzy chunks
- Treat Wipedown as the **recommended but optional** ingestion layer
- Keep BrainFood usable **with or without** Wipedown

### High-Level Architecture

```
                      AGENT LAYER
   (LangGraph, CrewAI, Cline, Aider, Custom, etc.)
          |
          v
+-------------------------------------------+
|           BrainFoodAgent                  |
|  (Public API)                             |
|  - get_context(query)                     |
|  - get_atomic(category, name)             |
|  - Simple and stable interface            |
+-------------------------------------------+
          |               |
          v               v
+---------------+  +-----------------+
| ATOMIC REGISTRY |  |  QUALITY GATES  |
| Clean components|  |  Pydantic-based |
| Schema validated|  |  Rejection logic|
+---------------+  +-----------------+
          |
          v
+------------------+    +------------------+
| Wipedown Layer   |    |   Direct / Custom|
| (Default: ON)    |    |   Ingestion      |
| - CLI integration|    | - Local folders  |
| - Toggleable     |    | - Markdown       |
| - Zero-trust     |    | - Other sources  |
+------------------+    +------------------+
```

### Wipedown Integration Rules

| Aspect | Decision |
|---|---|
| **Default state** | Wipedown integration enabled |
| **How to disable** | Config flag (`use_wipedown: false`) |
| **Primary integration** | Wipedown CLI |
| **Direct integration** | Supported as optional/advanced path |
| **Documentation** | Clearly explain both options |
| **Coupling** | Loose (CLI-based by default) |
| **Philosophy** | Wipedown as recommended companion, not hard dependency |

### Recommended Data Flow (Default)

1. Content is processed by Wipedown (zero-trust filtering)
2. Cleaned output is passed to BrainFood
3. BrainFood applies additional quality gates
4. High-signal data is written to the Atomic Registry
5. Agents retrieve clean context using `BrainFoodAgent`

Users who disable Wipedown can point BrainFood directly at folders or other sources.

---

## Detailed Build Plan

### Phase 0: Foundations

- Initialize clean repository structure
- Create strong README with positioning
- Define `brainfood.yaml` configuration schema (including Wipedown toggle)
- Set up packaging and basic CLI entrypoint
- Add MIT license and contribution guidelines

### Phase 1: Core + Wipedown Integration (Priority)

**Goals:**

- Deliver working curation and atomic registry
- Make Wipedown CLI the default ingestion path
- Allow users to disable Wipedown easily

**Key Deliverables:**

#### Configuration System

```yaml
use_wipedown: true        # Default: enabled
wipedown_path: "/path/to/wipedown"  # Configurable path to Wipedown binary
```

#### Wipedown Integration Module

- **Location:** `brainfood/integrations/wipedown.py`
- Primary support for Wipedown CLI
- Optional direct Python mode for advanced users
- Good error handling and diagnostics

#### BrainFoodAgent Interface

- Clean, stable public API
- Works regardless of Wipedown setting

#### Quality Gates + Atomic Registry

- Pydantic-based schemas and rejection logic
- Clean component storage and retrieval

#### Ingestion Support

- Handle output from Wipedown
- Fallback support for direct folder ingestion

#### Phase 1 Success Criteria

A user can install BrainFood, use it with Wipedown enabled by default, and disable Wipedown with one configuration change while retaining full functionality.

### Phase 2: Polish & Usability

- Improve CLI commands (`brainfood ingest`, `status`, etc.)
- Add clear documentation and examples for:
  - Default flow (Wipedown + BrainFood)
  - BrainFood without Wipedown
  - Integration with Cognee, LangGraph, etc.
- Enhance logging around the Wipedown step
- Add optional lightweight graph capabilities

### Phase 3: Ecosystem & Distribution

- Publish to PyPI
- Create example repositories showing both flows
- Strengthen recommended stack messaging (Wipedown + BrainFood)
- Prepare contribution and integration guides

---

## Quick Start

```bash
# Install BrainFood
pip install brainfood

# Configure (Wipedown enabled by default)
# Edit ~/.config/brainfood/brainfood.yaml
```

## Configuration

```yaml
# brainfood.yaml
use_wipedown: true
wipedown_path: "/usr/local/bin/wipedown"
data_dir: "~/.brainfood/data"
```

## License

MIT License — see [LICENSE](LICENSE) for details.