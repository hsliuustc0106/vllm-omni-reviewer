# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM-Omni project

"""MCP server for reviewing vllm-omni PRs."""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from reviewer.github import GitHubClient
from reviewer.knowledge import KnowledgeBase

mcp = FastMCP("vllm-omni-reviewer")

_gh = GitHubClient()
_kb = KnowledgeBase(Path(__file__).parent / ".knowledge")


# -- Tools ---------------------------------------------------------------


@mcp.tool()
def fetch_pr(pr_number: int) -> dict:
    """Fetch PR metadata, diff, comments, and reviews for a given PR number."""
    return _gh.fetch_pr(pr_number)


@mcp.tool()
def fetch_linked_refs(pr_body: str, exclude_number: int | None = None) -> list[dict]:
    """Parse and fetch all issues/PRs referenced in a PR body."""
    return _gh.fetch_linked_refs(pr_body, exclude_number)


@mcp.tool()
def fetch_file(path: str, ref: str = "main") -> str:
    """Fetch a file's contents from the repo at a given ref."""
    return _gh.fetch_file(path, ref)


@mcp.tool()
def list_recent_prs(state: str = "open", limit: int = 10) -> list[dict]:
    """List recent PRs for browsing."""
    return _gh.list_recent_prs(state, limit)


@mcp.tool()
def get_knowledge(filename: str | None = None) -> dict | str:
    """Load all knowledge base files, or a specific one by name."""
    if filename:
        return _kb.load_file(filename)
    return _kb.load_all()


@mcp.tool()
def save_review(pr_number: int, title: str, summary: str) -> str:
    """Save a review summary to the knowledge base."""
    path = _kb.save_review(pr_number, title, summary)
    return f"Review saved to {path}"


@mcp.tool()
def add_knowledge(filename: str, content: str) -> str:
    """Add or update a knowledge base note (e.g., conventions, architecture)."""
    path = _kb.add_note(filename, content)
    return f"Knowledge note saved to {path}"


@mcp.tool()
def post_review_comment(pr_number: int, body: str, event: str = "COMMENT") -> dict:
    """Post a review comment on a PR. Event: APPROVE, REQUEST_CHANGES, or COMMENT."""
    return _gh.post_review_comment(pr_number, body, event)


@mcp.tool()
def post_inline_comment(pr_number: int, path: str, line: int, body: str) -> dict:
    """Post a line-specific comment on a PR file.

    Args:
        pr_number: PR number
        path: File path in the repo (e.g., "src/file.py")
        line: Line number to comment on
        body: Comment text

    Note: Posts a comment with formatted file:line reference.
    """
    return _gh.post_inline_comment(pr_number, path, line, body)


@mcp.tool()
def parse_diff_for_review_lines(diff: str) -> list[dict]:
    """Parse a diff and extract lines suitable for inline comments.

    Returns list of dicts with path, line, content, and context for each added line.
    Useful for identifying specific lines that may need review comments.

    Args:
        diff: Unified diff text (from fetch_pr)

    Returns:
        List of dicts with keys: path, line, content, context
    """
    return _gh.parse_diff_for_review_lines(diff)


@mcp.tool()
def post_review_with_inline_comments(
    pr_number: int,
    summary: str,
    inline_comments: list[dict],
    event: str = "COMMENT",
) -> dict:
    """Post a review summary followed by inline comments one-by-one.

    This orchestrates the complete review posting workflow:
    1. Posts the summary as a general review comment
    2. Posts each inline comment sequentially
    3. Continues posting even if individual comments fail
    4. Returns detailed status for each operation

    Args:
        pr_number: PR number
        summary: Brief overall review summary (3-5 sentences)
        inline_comments: List of dicts with keys: path, line, body
        event: Review event - COMMENT, APPROVE, or REQUEST_CHANGES

    Returns:
        Dict with summary_posted, inline_comments list, successful/failed counts
    """
    return _gh.post_review_with_inline_comments(pr_number, summary, inline_comments, event)


# -- Prompt template -----------------------------------------------------


@mcp.prompt()
def review_pr(pr_number: int) -> str:
    """Review a vllm-omni PR with full context."""
    return f"""Review PR #{pr_number} from vllm-project/vllm-omni.

Steps:
1. Call fetch_pr to get the PR diff, metadata, and discussion
2. Call fetch_linked_refs to get context from referenced issues/PRs
3. Call get_knowledge to load project conventions and past review notes
4. If any changed files need more surrounding context, use fetch_file
5. Provide a structured review covering: bugs, logic errors, performance,
   security, style, and test coverage
6. Call save_review to persist a summary for future context
7. Ask if I want to post any comments to the PR on GitHub"""


@mcp.prompt()
def review_pr_with_inline(pr_number: int) -> str:
    """Review a PR and post concise summary with inline comments."""
    return f"""Review PR #{pr_number} with inline comments workflow:

1. Call fetch_pr to get PR metadata and diff
2. Call parse_diff_for_review_lines to identify lines needing comments
3. Call fetch_linked_refs to get context from referenced issues/PRs
4. Call get_knowledge to load project conventions and past review notes
5. Analyze the diff critically and generate:

   **IMPORTANT: Inline comments can ONLY be posted on lines returned by parse_diff_for_review_lines.**
   These are lines that were added or modified in the PR. You cannot comment on unchanged lines
   or lines not in the diff. If you need to mention issues with unchanged code, include them in
   the summary instead.

   **Summary Structure (required):**
   - Brief overview of what the PR does
   - **Pros:** List specific strengths (e.g., good test coverage, clean design, backward compatible)
   - **Cons:** List concerns and issues (e.g., missing tests, unclear edge cases, performance questions)
   - Overall assessment

   **Inline Comments:**
   - Post as many comments as needed based on actual issues found (not a fixed number)
   - Be critical and question assumptions
   - Focus on substantive issues, not just praise

6. Format inline comments as a list of dicts with keys: path, line, body
   **CRITICAL: Only use path and line values from parse_diff_for_review_lines output.**
   Do not invent line numbers or comment on files/lines not in that list.
7. Call post_review_with_inline_comments to post everything
8. Call save_review to persist the review summary

**Critical Review Guidelines:**

**Test Coverage (HIGH PRIORITY):**
- Does the PR include tests for new functionality?
- Are edge cases tested?
- For bug fixes: Is there a regression test?
- For performance claims: Are there benchmarks with before/after data?
- For new features: Are error paths tested?
- Question: "What happens if X fails?" "How is Y validated?"

**Performance Claims:**
- If PR claims performance improvement, demand measurements
- Look for: memory usage data, latency numbers, throughput comparisons
- Question vague claims like "significant improvement" without data
- Check if benchmarks are realistic (not toy examples)

**Design & Architecture:**
- Does this fit the existing architecture?
- Are there simpler alternatives?
- Is this over-engineered or under-engineered?
- Question: "Why this approach vs X?" "What's the trade-off?"

**Correctness & Edge Cases:**
- What edge cases are not handled?
- Are error messages helpful?
- Is input validation sufficient?
- Are there race conditions or concurrency issues?

**Documentation & Type Safety:**
- Are type annotations complete and correct?
- Is user-facing documentation updated?
- Are breaking changes documented?

**Code Quality:**
- Are there code smells (duplication, complexity, unclear naming)?
- Does it follow project conventions?
- Are there security concerns?

**Be Specific:**
- Instead of "Good implementation" → "The lock timeout calculation at line X correctly prevents deadlocks"
- Instead of "Nice test coverage" → "Tests cover the happy path but missing validation for empty input"
- Instead of "Well done" → Point out actual issues or ask probing questions

**Number of Comments:**
- Post as many inline comments as there are substantive issues
- A small doc fix might need 0-2 comments
- A large feature might need 8-12 comments
- Don't artificially limit or pad the number of comments"""


# -- Entry point ---------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
