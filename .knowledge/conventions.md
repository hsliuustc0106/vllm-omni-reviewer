# vllm-omni Project Conventions

## PR Process
- PRs should reference related issues with `#<number>` or full GitHub URLs
- PRs require at least one approving review before merge
- CI must pass before merge
- Large PRs should be broken into smaller, reviewable chunks

## Coding Style
- Python 3.10+ with type annotations
- Follow existing code patterns in the module being modified
- Use `from __future__ import annotations` for modern type syntax
- Docstrings for public APIs
- Tests for new functionality

## Labels
- `bug` — bug fixes
- `enhancement` — new features
- `documentation` — docs changes
- `breaking-change` — backwards-incompatible changes
- `WIP` — work in progress, not ready for review

## Common Pitfalls

### Mixin + nn.Module MRO Issue

When a mixin class is listed **after** `nn.Module` in inheritance, the mixin's `__init__` will **not** be called because `nn.Module.__init__()` doesn't call `super().__init__()`.

**Problem:**
```python
class MyModel(nn.Module, SomeMixin):  # Mixin after nn.Module
    def __init__(self):
        super().__init__()  # Only calls nn.Module.__init__!
        self.mixin_method()  # CRASH: mixin attributes not initialized
```

**Solution - Lazy Initialization:**
```python
class SomeMixin:
    @property
    def _internal_state(self) -> set:
        if not hasattr(self, '_internal_state_storage'):
            self._internal_state_storage = set()
        return self._internal_state_storage
```

**Red Flag in Tests:** If test mocks inherit only from the mixin (not `nn.Module`), they won't catch this bug.

---

## Review Guidelines

### Review Philosophy
- **Inline comments are the review** - no summary needed
- Each comment targets a specific critical issue at a specific line
- Maximum 5 comments per review - only critical issues

### Comment Limits
- Inline comments: 2-4 sentences maximum each
- Maximum 5 inline comments per PR
- A small doc fix should have 0 comments
- A large feature should have 3-5 comments on critical gaps

### Banned Phrases (generic praise)
- "solid", "generally", "looks good", "well done", "nice work", "great job"
- "comprehensive", "well structured", "good implementation"
- Any phrase that doesn't reference specific code locations

### Priority Order
1. **Missing tests** - highest priority
2. **Unvalidated claims** - demand measurements/evidence
3. **Security concerns** - input validation, resource exhaustion
4. **Design flaws** - architectural issues, race conditions
5. **Breaking changes** - undocumented API changes

**Skip:** Minor style issues, nitpicks, nice-to-haves, linter-covered issues

---

## Review Checklist

### Red Flags (Must Check)
- [ ] **Missing tests for new API**: New endpoint/method without test coverage?
- [ ] **Missing tests for new models**: New model implementation without test?
- [ ] **Unvalidated claims**: Performance claims without benchmarks?
- [ ] **MRO issues**: Mixins after nn.Module with `__init__` that sets attributes?
- [ ] **Breaking changes**: API changes without documentation?

### Most Common PR Issues
1. **New API without tests** - Every new endpoint needs test coverage
2. **New model without tests** - Every model needs correctness validation

### By PR Type
- **Bug fixes**: Regression test? Root cause understood?
- **New features**: Test coverage? Documentation?
- **Refactoring**: Behavior preserved? Tests still pass?
- **Performance**: Measurements? Quality trade-offs?
- **Model code**: Correctness validated? Memory requirements documented?

---

## Example Comments

**Good (Demands Evidence):**
```
Where are the memory measurements? The PR claims "50% reduction" but provides no before/after data. Run benchmarks with realistic workloads and report peak VRAM usage.
```

**Good (Missing Tests):**
```
Missing regression test for this bug fix. Add a test that reproduces the original issue and verifies this fix prevents it.
```

**Good (Design Question):**
```
Hard-coding 16 steps will break with future model variants. Add config validation or make the implementation flexible.
```

**Bad (Generic):**
```
The implementation looks good. Consider adding tests.
```

---

## Context Fetching

**When to fetch additional context:**
- New imports with performance/compatibility implications
- 3-line diff context isn't enough
- Code changes that might require config updates

**Tools:**
- `fetch_file_context(path, line, context_lines=30)` - get surrounding code
- `fetch_symbol_definition("SymbolName")` - find where something is defined
- `check_related_config_files(pr_number)` - find related configs

**Limits:** 3-5 context fetches per review, 20-50 lines each

---

## Known Dependencies
- `diffusers` - already in common.txt
- `einops` - inherited from vLLM, do NOT flag as missing
