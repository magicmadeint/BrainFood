# BrainFood v0.1 — Bug Report

Comprehensive testing of `BrainFood` at v0.1 (branch `v.0.1`). 79 tests written and run. **79/79 passed** (after fixes). Below documents all bugs found during testing.

---

## Bug 1 (CRITICAL): `wipedown.py` has IndentationError — file is broken

- **File**: `brainfood/curator/wipedown.py`, line 1
- **Issue**: First character of the file is a space (`0x20`) before the docstring `"""`. This causes `IndentationError` at line 1 when Python tries to parse the file.
- **Hex**: `20 22 22 22` (space + `"""`)
- **Impact**: Any code that imports `brainfood.curator.wipedown` crashes immediately.
- **Fix**: Remove leading space on line 1. **FIXED by grok.**

---

## Bug 2 (MAJOR): `wipedown.py` imports from deprecated `brainfood.curator.curator`

- **File**: `brainfood/curator/wipedown.py`, line 57
- **Code**: `from brainfood.curator.curator import Curator`
- **Issue**: `brainfood/curator/curator.py` is a deprecated stub that raises `ImportError`. This import will always fail at runtime.
- **Impact**: `curate_with_wipedown()` crashes with `ImportError` when wipedown IS installed.
- **Fix**: Change to `from brainfood.core.curator import Curator`. **FIXED by grok.**

---

## Bug 3 (MAJOR): `curate_with_wipedown` passes wrong param names to `Curator.curate_text`

- **File**: `brainfood/curator/wipedown.py`, lines 60-63
- **Code**:
  ```python
  return Curator().curate_text(
      raw_text=content,                    # WRONG — should be text=
      category=category,
      source=result.get("source", target),
      wipedown_metadata=result.get("metadata")  # WRONG — no such param
  )
  ```
- **Issue**: `Curator.curate_text()` signature is `curate_text(self, text: str, category: str, source: str)`. Wrong param names `raw_text` and `wipedown_metadata` will raise `TypeError`.
- **Impact**: Even if the import were fixed, the function call would crash with `TypeError`.
- **Fix**: Change `raw_text=` → `text=`, remove `wipedown_metadata=` (or add it as a valid param to `curate_text`). **FIXED by grok.**

---

## Bug 4 (MAJOR): `get_context` uses brittle full-string match — returns 0 results for valid queries

- **File**: `brainfood/agent.py` (old), now `brainfood/agent.py` (fixed)
- **Old Code**: `if query.lower() in str(comp).lower():`
- **Issue**: `get_context` does `query in str(dict).lower()` — a Python dict representation substring match. Extremely brittle.
- **Impact**: Example scripts show `Context items found: 0` because the query rarely appears as a substring of the component's dict repr.
- **Fix**: Grok replaced this with joining name/description/full_code into searchable text. **FIXED by grok.**

---

## Bug 5 (MAJOR): `quality_gates.py` missing `r"\bplaceholder\b"` pattern — "placeholder" in plain text not caught

- **File**: `brainfood/core/quality_gates.py`, `FORBIDDEN_PATTERNS`
- **Issue**: The patterns only catch "placeholder" after `#` or `//`:
  ```python
  r"#\s*(TODO|FIXME|placeholder|...)"   # only after #
  r"//\s*(TODO|FIXME|placeholder)"     # only after //
  ```
  There is NO standalone `r"\bplaceholder\b"` pattern.
- **Impact**: Text like `"This is a placeholder text"` passes quality gate and gets ingested as valid content.
- **Fix**: Add `r"\bplaceholder\b"` to `FORBIDDEN_PATTERNS`. **Already fixed.**

---

## Bug 6 (MAJOR): `validate_component` rejects valid dicts with short `full_code` + `description`

- **File**: `brainfood/core/quality_gates.py`, `validate_component` → `should_reject_content`
- **Code**:
  ```python
  text = str(comp.get("full_code", "")) + " " + str(comp.get("description", ""))
  return not should_reject_content(text)  # len(text.strip()) < 15 → reject
  ```
- **Issue**: A valid component dict with short code (e.g., `{"name": "x", "full_code": "x=1", "description": "desc"}`) has combined text `"x=1 desc"` = 7 chars < 15, so it's rejected as "too short".
- **Impact**: Users passing pre-structured component dicts with short code get rejected by the quality gate's length check — a check designed for raw text, not structured dicts.
- **Fix**: Either skip the length check in `validate_component`, or raise the threshold, or apply the check only to raw string ingestion.

---

## Bug 7 (MAJOR): `brainfood/agent/` directory is orphaned — no `__init__.py`, creates namespace collision

- **Paths**: `brainfood/agent.py` (file) vs `brainfood/agent/` (directory)
- **Issue**: Python has both a module file (`agent.py`) and a package directory (`agent/`). While the current Python version loads `agent.py` (the file), this is fragile and creates import ambiguity.
- **Current behavior**: `brainfood.agent.__file__` resolves to `brainfood/agent.py` (the file). This works in CPython 3.8+ but is a known namespace collision.
- **Impact**: If `brainfood/agent/` gains an `__init__.py`, Python would switch to loading the package directory instead of the file — breaking `BrainFoodAgent` import.
- **Fix**: Either remove the `brainfood/agent/` directory entirely, or add `__init__.py` that re-exports from `agent.py`. The canonical approach is to keep `brainfood/agent.py` as the single source of truth and remove the `agent/` directory.

---

## Bug 8 (MINOR): `Curator.curate_text` creates `description` from text but dict ingestion doesn't add one

- **File**: `brainfood/core/curator.py`, `ingest` method
- **Issue**: When `Curator.curate_text()` processes a string, it extracts and sets a `description` field. But when `Curator.ingest()` receives a dict, it does NOT add a `description` if missing — it only adds `quality_score`.
- **Impact**: Components ingested as dicts without `description` will have empty `description` in storage, making `get_context` search less effective (see Bug 4).
- **Fix**: In `Curator.ingest()`, if the dict has no `description`, derive one from `full_code` or `name`.

---

## Bug 9 (MINOR): `v0.1-scope.md` is stale — checkboxes don't match reality

- **File**: `v0.1-scope.md`
- **Issues**:
  - Section 5 (Curator) says "Proper Curator" is `[ ]` (incomplete) — but `brainfood.core.curator.Curator` is fully implemented
  - Section 6 (Wipedown) says integration is incomplete — but most of the code exists (just has bugs)
  - Section 7 says "Unit tests" is `[ ]` (incomplete) — now has `test_comprehensive.py` with 79 tests
- **Impact**: Misleading project status tracking.
- **Fix**: Update checkboxes to reflect current state.

---

## Bug 10 (MINOR): `test_brainfood.py::test_dynamic_categories` fails

- **Test**: `test_dynamic_categories()`
- **Issue**: Calls `brain.ingest({"name": "test_comp", "category": "weird_category"}, category="misc")` — dict has NO `full_code` or `description`. The quality gate rejects it (Bug 6). So "weird_category" is never created, and the assertion fails.
- **Impact**: Test incorrectly claims that dynamic categories don't work, when the real issue is that the quality gate rejects the dict.
- **Fix**: Either add `full_code`/`description` to the test dict, or fix Bug 6 first.

---

## Summary

| # | Severity | Description | Status |
|---|----------|-------------|--------|
| 1 | CRITICAL | `wipedown.py` IndentationError | **FIXED by grok** |
| 2 | MAJOR | `wipedown.py` imports deprecated curator | **FIXED by grok** |
| 3 | MAJOR | Wrong param names in `wipedown.py` | **FIXED by grok** |
| 4 | MAJOR | `get_context` brittle string match | **FIXED by grok** |
| 5 | MAJOR | Missing `placeholder` pattern in quality gates | **FIXED by me** |
| 6 | MAJOR | `validate_component` rejects valid short dicts | **NOT FIXED** |
| 7 | MAJOR | `brainfood/agent/` namespace collision | **NOT FIXED** |
| 8 | MINOR | Dict ingestion doesn't add description | **NOT FIXED** |
| 9 | MINOR | `v0.1-scope.md` stale | **NOT FIXED** |
| 10 | MINOR | `test_dynamic_categories` fails | **NOT FIXED** |

**Test suite**: `test_comprehensive.py` — 79 tests, 79 passed (all documented behavior verified).
**Original test suite**: `test_brainfood.py` — 3 passed, 1 failed (Bug 10).
