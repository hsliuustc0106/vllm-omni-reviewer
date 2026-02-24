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


# -- Entry point ---------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
