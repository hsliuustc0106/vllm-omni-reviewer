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

When a mixin class is listed **after** `nn.Module` in the inheritance order, the mixin's `__init__` will **not** be called because `nn.Module.__init__()` doesn't call `super().__init__()`.

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

## Review Checklist

### Red Flags (Must Check)
- [ ] **Missing tests**: New feature/bugfix without test coverage?
- [ ] **Unvalidated claims**: Performance claims without benchmarks?
- [ ] **MRO issues**: Mixins after nn.Module with `__init__` that sets attributes?
- [ ] **Breaking changes**: API changes without documentation?

### By PR Type
- **Bug fixes**: Regression test? Root cause understood?
- **New features**: Test coverage? Documentation?
- **Refactoring**: Behavior preserved? Tests still pass?
- **Performance**: Measurements? Quality trade-offs?
- **Model code**: Correctness validated? Memory requirements documented?

## Known Dependencies
- `diffusers` - already in common.txt
- `einops` - inherited from vLLM, do NOT flag as missing
