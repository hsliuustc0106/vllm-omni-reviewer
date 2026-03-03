# Enhanced Context Fetching for vllm-omni-reviewer

## Overview

Enhance `fetch_pr()` to automatically return related context from:
- Issues matching keywords from PR title/body
- Author's recent PRs
- PRs referenced in commit messages on modified files

This enables reviewers to identify recurring issues, author patterns, and incomplete previous fixes.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trigger | Always automatic | No manual intervention needed |
| Context types | Keywords, author PRs, commit history | Covers main patterns without file-based search |
| Exposure | Enhanced `fetch_pr()` | No new tools, always available |
| Detail level | Balanced (title + 200 char summary) | Sufficient context without token explosion |
| Implementation | GitHub Search API | No local state, leverages GitHub's ranking |

## Response Structure

```python
{
    # Existing fields unchanged
    "number": 1536,
    "title": "...",
    "body": "...",
    "diff": "...",
    "changed_files": [...],
    # ...

    # NEW: Related context
    "related_context": {
        "related_issues": [
            {"number": 1477, "title": "...", "summary": "first 200 chars", "state": "open"}
        ],
        "author_recent_prs": [
            {"number": 1471, "title": "...", "summary": "...", "state": "closed"}
        ],
        "referenced_prs_from_history": [
            {"number": 1468, "title": "...", "summary": "...", "state": "merged"}
        ]
    }
}
```

**Limits:** 5 items per category, summaries truncated to 200 characters.

## Keyword Extraction

**Sources:**
1. PR title - extract technical terms
2. PR body - extract from summary section (first 500 chars)
3. File paths - extract component names

**Extraction rules:**
- Remove PR type prefixes: `[Bugfix]`, `[Feat]`, `[Refactor]`, etc.
- Extract quoted identifiers: `num_cached_tokens`, `transformers 5.x`
- Extract from file paths: `omni_generation_scheduler.py` -> `OmniGenerationScheduler`
- Filter stop words: `fix`, `add`, `update`, `remove`, `the`, `for`, `with`
- Limit to 5 keywords maximum

**Example:**
```
Title: "[Bugfix] Fix transformers 5.x compat issues in online TTS serving"
Files: ["vllm_omni/core/sched/omni_generation_scheduler.py"]
→ Keywords: ["transformers 5.x", "TTS", "OmniGenerationScheduler"]
```

## API Implementation

### New Methods in `GitHubClient`

```python
def _extract_keywords(self, title: str, body: str, files: list[str]) -> list[str]:
    """Extract search keywords from PR metadata."""

def _search_related_issues(self, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search for issues matching keywords using GitHub Search API."""
    # Query: "keyword1 OR keyword2 repo:vllm-project/vllm-omni is:issue"

def _get_author_recent_prs(self, author: str, limit: int = 5) -> list[dict]:
    """Get author's recent PRs."""

def _get_prs_from_commit_history(self, files: list[str], limit: int = 5) -> list[dict]:
    """Extract PR numbers from commit messages on modified files."""
    # Parse commit messages for: "#1471", "PR #1471", "Fixes #123"
```

### Rate Limit Handling

- GitHub Search API: 30 requests/min (authenticated)
- Graceful degradation: if rate limited, return empty list for that category
- Individual failures don't fail the whole `fetch_pr()` call

## Prompt Updates

Update `review_pr_with_inline` prompt to:

1. **Analyze related context** after fetching PR
2. **Elevate issue scores** when patterns found:
   - Missing test alone → score 50
   - Missing test + same bug fixed twice → score 100
3. **Cite context** in comments when escalating

**Example comment:**
> Issue #1477 documented this crash. PR #1471 already attempted a fix in schedule(). This PR adds another fix in update_from_output() - why is a second fix needed?

## Files to Modify

| File | Changes |
|------|---------|
| `reviewer/github.py` | Add 4 new methods, modify `fetch_pr()` (~80 lines) |
| `server.py` | Update prompts to use related context (~20 lines) |

## Success Criteria

- Related context appears in `fetch_pr()` response
- Context includes relevant issues, author PRs, and commit history PRs
- Reviewer prompts use context to elevate issue scores when patterns found
- No breaking changes to existing `fetch_pr()` behavior
