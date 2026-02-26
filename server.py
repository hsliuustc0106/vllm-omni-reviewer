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


def _extract_section(markdown: str, heading: str) -> str:
    """Extract content under a specific heading from markdown."""
    lines = markdown.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        if line.startswith("## ") and line[3:].strip() == heading:
            in_section = True
            continue
        elif line.startswith("## ") and in_section:
            # Hit next section, stop
            break
        elif in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


@mcp.tool()
def get_pr_type_guidance(pr_title: str) -> dict:
    """Extract PR type from title and return type-specific review guidance.

    Args:
        pr_title: PR title (e.g., "[Bugfix] Fix race condition")

    Returns:
        {
            "pr_type": "bugfix" | "feature" | ... | None,
            "guidance": "Type-specific review focus areas...",
            "detected_from": "[Bugfix]" (the actual prefix found),
            "all_types": [("bugfix", "[Bugfix]")] (for multi-type PRs)
        }
    """
    from reviewer.github import detect_pr_types

    # Detect all types (supports multi-type PRs)
    all_types = detect_pr_types(pr_title)

    if not all_types:
        return {
            "pr_type": None,
            "guidance": "No specific PR type detected. Use general review guidelines from conventions.md.",
            "detected_from": None,
            "all_types": []
        }

    # Use primary type (first detected)
    primary_type, detected_prefix = all_types[0]

    # Load type-specific guidance from knowledge base
    try:
        guidance = _kb.load_file(f"pr-types/{primary_type}.md")
    except FileNotFoundError:
        guidance = f"Type '{primary_type}' detected but guidance file not found. Use general guidelines."

    return {
        "pr_type": primary_type,
        "guidance": guidance,
        "detected_from": detected_prefix,
        "all_types": all_types
    }


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
3. Call get_pr_type_guidance with the PR title to get type-specific review focus
4. Call get_knowledge to load project conventions, architecture, and vllm-omni concepts
5. If any changed files need more surrounding context, use fetch_file
6. Provide a CONCISE, CRITICAL review with this EXACT structure:

   **Summary (2-3 sentences max):**
   What does this PR do? What's the core change?

   **Red Flags (mandatory checklist):**
   - Missing tests: [yes/no + specifics]
   - Unvalidated claims: [yes/no + specifics]
   - Missing error handling: [yes/no + specifics]
   - Breaking changes: [yes/no + specifics]
   - Security concerns: [yes/no + specifics]

   **Pros (2-4 bullets max):**
   - [Specific strength with file:line reference]
   - MUST reference actual code locations
   - NO generic praise - be specific or stay silent

   **Cons (3-8 bullets):**
   - [Specific issue with file:line reference]
   - Focus on gaps, missing evidence, unvalidated assumptions
   - Demand concrete measurements for all performance claims
   - Question design decisions that lack justification

   **Verdict (1 sentence):**
   Approve / Request changes / Needs discussion

   TOTAL LENGTH: 150-250 words maximum

7. Call save_review to persist a summary for future context
8. Ask if I want to post any comments to the PR on GitHub

**CRITICAL CONSTRAINTS:**
- Summary MUST be 150-250 words maximum
- Each Pro/Con bullet MUST reference specific file:line locations
- BANNED PHRASES: "solid", "generally", "looks good", "well done", "nice work", "great job", "comprehensive", "well structured"
- Every sentence must add new information - no fluff or repetition

**EVIDENCE REQUIREMENTS (mandatory):**
- Any performance claim → Ask: "Where are the measurements showing X?"
- Any new feature → Ask: "Where are the tests covering X?"
- Any bug fix → Ask: "Where is the regression test preventing X?"
- Any design decision → Ask: "Why this approach vs [specific alternative]?"

Use direct language: "Missing tests for X" not "It would be beneficial to add tests"

IMPORTANT: Read vllm-omni-concepts.md from the knowledge base to understand:
- Omni vs AsyncOmni (sync vs async_chunk execution)
- Multi-stage pipeline architecture and stage-level concurrency
- OmniChunkTransferAdapter and SharedMemoryConnector
- Shared infrastructure between online serving and offline inference
- Memory management patterns and risks
- Example code vs production code expectations

**Type-Specific Review Focus:**
- Apply the guidance from get_pr_type_guidance to prioritize review areas
- Use linked issue context to validate the PR addresses the problem correctly
- For [Bugfix]: Check if issue describes reproduction steps, verify tests cover them
- For [Feat]: Check if issue describes requirements, verify implementation matches
- For [Quantization]: Check if issue mentions target metrics, verify measurements provided
- Combine type-specific focus with general vllm-omni architecture knowledge
- If no type detected, use general review guidelines

Use this knowledge to provide context-aware reviews that understand vllm-omni's
unique architecture and avoid over-engineering comments on example code."""


@mcp.prompt()
def review_pr_with_inline(pr_number: int) -> str:
    """Review a PR and post concise summary with inline comments."""
    return f"""Review PR #{pr_number} with inline comments workflow:

1. Call fetch_pr to get PR metadata and diff
2. Call parse_diff_for_review_lines to identify lines needing comments
3. Call fetch_linked_refs to get context from referenced issues/PRs
4. Call get_pr_type_guidance with the PR title to get type-specific review focus
5. Call get_knowledge to load project conventions, architecture, and vllm-omni concepts
6. Analyze the diff critically and generate:

   **IMPORTANT: Read vllm-omni-concepts.md to understand:**
   - Omni vs AsyncOmni (sync vs async_chunk execution)
   - Multi-stage pipeline architecture and stage-level concurrency
   - Shared infrastructure between online serving and offline inference
   - Memory management patterns and risks
   - Example code vs production code expectations

   Use this knowledge to provide context-aware reviews and avoid over-engineering
   comments on example code (e.g., don't ask about trio/curio, Jupyter edge cases).

   **Type-Specific Review Focus:**
   - Apply the guidance from get_pr_type_guidance to prioritize review areas
   - Cross-reference with linked issues to understand the problem being solved
   - For [Bugfix]: Verify the fix addresses the exact issue described, check for regression tests
   - For [Feat]: Verify implementation matches feature requirements from the issue
   - For [Quantization]: Check if measurements match expectations from the issue
   - For [Model]: Verify model-specific requirements from the issue are met
   - For other types: Follow the specific guidance provided
   - Use issue context to validate PR scope and completeness

   **IMPORTANT: Inline comments can ONLY be posted on lines returned by parse_diff_for_review_lines.**
   These are lines that were added or modified in the PR. You cannot comment on unchanged lines
   or lines not in the diff. If you need to mention issues with unchanged code, include them in
   the summary instead.

   **Summary Structure (ULTRA-BRIEF):**
   - What this PR does: 1 sentence
   - Key strengths: 1-2 bullets with file:line (NO generic praise)
   - Critical issues: 2-3 bullets with file:line (focus on blockers)
   - Verdict: 1 sentence
   - TOTAL: 50-100 words maximum (the inline comments are the real review)
   - BANNED: "solid", "generally", "looks good", "well done", "nice", "great", "comprehensive"

   The summary is just context - the inline comments are where you provide the real critical analysis.

   **Inline Comments (MAXIMUM 5 - THIS IS THE REAL REVIEW):**
   - Post 0-5 comments ONLY for the MOST CRITICAL issues
   - Prioritize: missing tests > unvalidated claims > security > design flaws > style
   - Each comment MUST be 2-4 sentences maximum
   - Each comment MUST demand specific action or evidence
   - Skip minor issues - only flag blockers and high-impact problems
   - If there are no critical issues, post 0 comments (don't pad)

   **The inline comments are where you do the critical analysis. The summary is just brief context.**

7. Format inline comments as a list of dicts with keys: path, line, body
   **CRITICAL: Only use path and line values from parse_diff_for_review_lines output.**
   Do not invent line numbers or comment on files/lines not in that list.
8. Call post_review_with_inline_comments to post everything
9. Call save_review to persist the review summary

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

**Avoid Over-Engineering:**
- Don't ask about extremely rare alternatives (trio/curio vs asyncio)
- Don't worry about edge cases in example/demo code (Jupyter event loops, etc.)
- Focus on real production risks, not theoretical concerns
- Example scripts using asyncio.run() don't need event loop management suggestions

**Number of Comments (STRICT LIMIT):**
- Maximum 5 inline comments per review
- Only post comments for CRITICAL issues that block merge
- Prioritize: missing tests, unvalidated performance claims, security risks, major design flaws
- A small doc fix should have 0 comments
- A large feature should have 3-5 comments on the most critical gaps
- Do NOT post comments on minor style issues or nice-to-haves"""


# -- Entry point ---------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
