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

## Review Focus Areas
- Correctness of the implementation
- Performance implications (especially for inference hot paths)
- API compatibility and backwards compatibility
- Test coverage for new code paths
- Documentation for user-facing changes
