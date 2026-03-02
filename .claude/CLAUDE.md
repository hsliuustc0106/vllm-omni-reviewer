# vllm-omni-reviewer

MCP server for reviewing PRs on vllm-project/vllm-omni repository.

## Constraints

- **Max 5 inline comments** per PR
- **2-4 sentences** per comment
- **Only critical issues** - skip style, nitpicks
- **No generic praise** - "looks good", "nice work" banned

## Review Workflow

1. `fetch_pr(pr_number)` - Get PR metadata, diff, comments
2. `get_pr_type_guidance(pr_title)` - Get type-specific focus areas
3. Analyze diff against `rules/conventions.md` and `rules/pr-types.md`
4. Identify 0-5 critical issues (missing tests, unvalidated claims, security, design flaws)
5. Use context tools if needed: `fetch_file_context`, `fetch_symbol_definition`
6. `post_review_with_inline_comments()` - Post review
7. `save_review()` - Archive the review

## MCP Tools

| Tool | Purpose |
|------|---------|
| `fetch_pr` | Get PR data (metadata, diff, comments) |
| `post_review_with_inline_comments` | Post review with comments |
| `get_pr_type_guidance` | Get review focus by PR type |
| `fetch_file_context` | Get surrounding code for a line |
| `fetch_symbol_definition` | Find where symbol is defined |
| `save_review` | Archive review summary |

## Rules

| File | Purpose |
|------|---------|
| `rules/architecture.md` | vllm-omni architecture, layers, key directories |
| `rules/conventions.md` | Coding conventions, review guidelines, MRO pitfalls |
| `rules/code-patterns.md` | Async, distributed, KV cache patterns |
| `rules/pr-types.md` | Review focus areas by PR type |

## Reviews

See `review_history/` for archived PR reviews.
