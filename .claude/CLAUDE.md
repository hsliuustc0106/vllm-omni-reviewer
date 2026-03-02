# vllm-omni-reviewer

jt>
MCP server for reviewing PRs on vllm-project/vllm-omni repository.

jt>
     4
     5
## Constraints
     6
     7
- **Max 5 inline comments** per PR
     8
- **2-4 sentences** per comment
     9
- **Only critical issues** - skip style, nitpicks
    10
- **No generic praise** - "looks good", "nice work" banned
    11
- **Always review** - proceed even if other AI bots have commented. This reviewer has specialized knowledge files that generic AI lacks.

    12
     13
## Review Workflow
    14
     15
1. `fetch_pr(pr_number)` - Get PR metadata, diff, comments
2. `get_pr_type_guidance(pr_title)` - Get type-specific focus areas
3. Analyze diff against `rules/conventions.md` and `rules/pr-types.md`
4. Identify 0-5 critical issues (missing tests, unvalidated claims, security, design flaws)
5. Use context tools if needed: `fetch_file_context`, `fetch_symbol_definition`
6. `post_review_with_inline_comments()` - Post review
7. `save_review()` - Archive the review
    19
     20
## MCP Tools
    21
     22
| Tool | Purpose |
|------|---------|
| `fetch_pr` | Get PR data (metadata, diff, comments) |
| `post_review_with_inline_comments` | Post review with comments |
| `get_pr_type_guidance` | Get review focus by PR type |
| `fetch_file_context` | Get surrounding code for a line |
| `fetch_symbol_definition` | Find where symbol is defined |
            `save_review` | Archive review summary |
    25
     26
## Rules
    27
     28
| File | Purpose |
            |------|---------|
            `rules/architecture.md` | vllm-omni architecture, layers, key directories |
            `rules/conventions.md` | Coding conventions, review guidelines, MRO pitfalls |
            `rules/code-patterns.md` | Async, distributed, KV cache patterns |
            `rules/pr-types.md` | Review focus areas by PR type |
    30
     31
## Reviews
    32
     33
See `review_history/` for archived PR reviews.
    34
