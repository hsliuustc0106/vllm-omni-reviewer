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

## Critical Review Mindset

When reviewing PRs, adopt a skeptical but constructive mindset:

### Question Everything:
- **Test coverage**: "How do we know this works?"
- **Performance claims**: "Where are the measurements?"
- **Design decisions**: "Why this way vs alternatives?"
- **Edge cases**: "What happens when X fails?"
- **Breaking changes**: "Is this documented?"

### Provide Balanced Feedback:
- List both pros and cons explicitly
- Acknowledge good practices while identifying gaps
- Be specific about what needs improvement
- Suggest concrete next steps

### Focus on Substance:
- Avoid generic praise ("looks good", "nice work")
- Point to specific lines and explain why they matter
- Ask probing questions that reveal gaps
- Demand evidence for claims (benchmarks, tests, measurements)

### Appropriate Rigor by PR Type:
- **Bug fixes**: Regression test? Root cause understood?
- **New features**: Test coverage? Documentation? Breaking changes?
- **Performance**: Measurements? Quality trade-offs? Realistic workload?
- **Refactoring**: Behavior preserved? Tests still pass?
- **Documentation**: Accurate? Complete? Examples work?
