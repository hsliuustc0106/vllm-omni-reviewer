# vllm-omni-reviewer

An MCP server for reviewing pull requests in [vllm-project/vllm-omni](https://github.com/vllm-project/vllm-omni). It gives Claude direct access to PR diffs, linked issues, file contents, and a persistent knowledge base of project conventions and past reviews.

## Features

- Fetch PR metadata, diffs, comments, and reviews from GitHub
- Resolve linked issues and PRs referenced in PR descriptions
- Read file contents from the repo at any git ref
- Maintain a local knowledge base of architecture notes, coding conventions, and review history
- Post review comments back to GitHub

## Setup

Requires Python 3.10+.

### Authentication (choose one)

The server uses GitHub API for most operations. Authentication is handled in this priority order:

1. **GitHub CLI (`gh`)** — Default, recommended. Run `gh auth login` to authenticate.
2. **Environment variable** — Fallback. Set `GITHUB_TOKEN` with a [personal access token](https://github.com/settings/tokens).

### Installation

```bash
pip install -e .
```

## Usage

### As an MCP server

Add the server to your MCP client config (e.g. `.mcp.json`):

```json
{
  "mcpServers": {
    "vllm-omni-reviewer": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/vllm-omni-reviewer"
    }
  }
}
```

If using `GITHUB_TOKEN` instead of `gh` CLI, add the environment variable:

```json
{
  "mcpServers": {
    "vllm-omni-reviewer": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/vllm-omni-reviewer",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Standalone

```bash
python server.py
```

## MCP Tools

| Tool | Description |
|---|---|
| `fetch_pr` | Get PR metadata, diff, comments, and reviews |
| `fetch_linked_refs` | Parse and fetch all issues/PRs referenced in a PR body |
| `fetch_file` | Get a file's contents from the repo at a given ref |
| `list_recent_prs` | List recent PRs by state |
| `get_knowledge` | Load knowledge base files |
| `save_review` | Persist a review summary for future context |
| `add_knowledge` | Add or update a knowledge base note |
| `post_review_comment` | Post a review comment on a PR (APPROVE, REQUEST_CHANGES, or COMMENT) |

## Review Workflow

The server includes a `review_pr` prompt template that guides the full workflow:

1. Fetch the PR with diff and discussion
2. Resolve linked issues/PRs for context
3. Load project conventions and past reviews
4. Fetch additional file context as needed
5. Provide a structured review (bugs, logic, performance, security, style, tests)
6. Save the review summary to the knowledge base
7. Optionally post comments to GitHub

## Project Structure

```
├── server.py              # MCP server entry point and tool definitions
├── reviewer/
│   ├── github.py          # GitHub API client (httpx + gh CLI)
│   └── knowledge.py       # Knowledge base read/write operations
├── .knowledge/            # Persistent knowledge base (markdown files)
│   ├── architecture.md
│   ├── conventions.md
│   └── reviews/
└── pyproject.toml
```
