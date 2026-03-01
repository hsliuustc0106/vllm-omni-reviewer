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

**Red Flag in Tests:** If test mocks inherit only from the mixin (not `nn.Module`), they won't catch this bug.

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

## Known Dependencies
- `diffusers` - already in common.txt
- `einops` - inherited from vLLM, do NOT flag as missing
