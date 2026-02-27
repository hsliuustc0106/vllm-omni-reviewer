# Smart Context Fetching for PR Reviews

## Overview

The vllm-omni-reviewer now supports smart, demand-driven context fetching to improve review quality without causing context explosion.

## New MCP Tools

### 1. `extract_imports_from_diff(pr_number, file_path=None)`
Extracts import statements from changed lines in a PR diff.

**Returns:**
```python
{
    "imports_by_file": {
        "path/to/file.py": {
            "added_imports": ["from x import y", "import z"],
            "removed_imports": ["import old"],
            "modules": ["x", "z"]
        }
    }
}
```

**Use case:** Identify new dependencies that might have performance or compatibility implications.

### 2. `fetch_file_context(path, line, context_lines=20, ref="main")`
Fetches surrounding context for a specific line (not the whole file).

**Returns:**
```python
{
    "path": str,
    "line": int,
    "start_line": int,
    "end_line": int,
    "content": str,
    "total_file_lines": int
}
```

**Use case:** Get surrounding code when the 3-line diff context isn't enough to understand a change.

### 3. `fetch_symbol_definition(symbol_name, search_paths=None, ref="main")`
Searches for a symbol (function/class) definition in the codebase.

**Returns:**
```python
{
    "symbol": str,
    "found": bool,
    "locations": [
        {"path": str, "line": int, "context": str}
    ]
}
```

**Use case:** Understand what imported functions/classes do before commenting on their usage.

### 4. `check_related_config_files(pr_number)`
Identifies configuration files that might be affected by PR changes.

**Returns:**
```python
{
    "relevant_configs": [
        {"path": str, "reason": str, "exists": bool}
    ]
}
```

**Use case:** Check if config files need updates based on code changes.

## Usage Philosophy

**Lazy, Demand-Driven Fetching:**
- Only fetch context when posting a critical inline comment
- Limit to 3-5 context fetches per review
- Prefer targeted fetches (line ranges) over full files
- Skip fetching if context isn't critical for the comment

## Integration

The tools are integrated into the `review_pr_with_inline` prompt with guidance on:
- When to fetch context (import changes, unclear code, config concerns)
- How to use each tool effectively
- Strict limits to avoid context explosion

## Documentation

See `.knowledge/review-guidelines.md` for detailed examples of when and how to use these tools during reviews.

## Testing

All four tools have been tested with real PRs and work correctly:
- Import extraction identifies new dependencies
- File context fetching retrieves surrounding code
- Symbol search finds definitions (when available via GitHub API)
- Config file detection identifies relevant configuration files
