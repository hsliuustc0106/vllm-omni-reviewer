# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM-Omni project

"""GitHub API client for vllm-project/vllm-omni using gh CLI."""

from __future__ import annotations

import json
import re
import subprocess

REPO = "vllm-project/vllm-omni"
DIFF_CHAR_LIMIT = 200_000

# Patterns for linked refs in PR bodies
_REF_PATTERNS = [
    re.compile(r"(?:https?://github\.com/[\w\-]+/[\w\-]+/(?:issues|pull)/(\d+))"),
    re.compile(r"(?<!\w)#(\d+)"),
]

# PR type patterns - maps regex patterns to normalized type names
_PR_TYPE_PATTERNS = [
    (re.compile(r"\[(?:Bugfix|BugFix|Bug Fix|Bug)\]", re.IGNORECASE), "bugfix"),
    (re.compile(r"\[(?:Feat|Feature)\]", re.IGNORECASE), "feature"),
    (re.compile(r"\[(?:Model|New Reward Model)\]", re.IGNORECASE), "model"),
    (re.compile(r"\[Quantization\]", re.IGNORECASE), "quantization"),
    (re.compile(r"\[Doc\]", re.IGNORECASE), "documentation"),
    (re.compile(r"\[(?:CI|CI/Build|Test)\]", re.IGNORECASE), "ci"),
    (re.compile(r"\[(?:NPU|XPU|ROCM)\]", re.IGNORECASE), "platform"),
    (re.compile(r"\[Performance\]", re.IGNORECASE), "performance"),
    (re.compile(r"\[(?:API|Frontend)\]", re.IGNORECASE), "api"),
    (re.compile(r"\[(?:Refactor|Chore|Misc)\]", re.IGNORECASE), "refactor"),
    (re.compile(r"\[(?:WIP|DO NOT MERGE THIS)\]", re.IGNORECASE), "wip"),
]


def _run_gh_api(endpoint: str, *args: str, paginate: bool = False) -> dict | list:
    """Run gh api command and return parsed JSON result."""
    cmd = ["gh", "api", endpoint] + list(args)
    if paginate:
        cmd.append("--paginate")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _run_gh(*args: str) -> str:
    """Run gh command and return stdout."""
    result = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr.strip()}")
    return result.stdout


def extract_pr_type(title: str) -> str | None:
    """Extract PR type from title prefix like [Bugfix], [Feat], etc.

    Returns normalized type (lowercase) or None if no recognized prefix found.

    Examples:
        "[Bugfix] Fix race condition" -> "bugfix"
        "[Feat]: Add async support" -> "feature"
        "[Quantization] FP8 for VAE" -> "quantization"
        "Fix typo" -> None
    """
    for pattern, type_name in _PR_TYPE_PATTERNS:
        if pattern.search(title):
            return type_name
    return None


def detect_pr_types(title: str) -> list[tuple[str, str]]:
    """Detect all PR types in title (supports multiple types).

    Returns list of (normalized_type, matched_prefix) tuples.

    Examples:
        "[Bugfix][NPU] Fix crash" -> [("bugfix", "[Bugfix]"), ("platform", "[NPU]")]
    """
    results = []
    for pattern, type_name in _PR_TYPE_PATTERNS:
        match = pattern.search(title)
        if match:
            results.append((type_name, match.group(0)))
    return results


class GitHubClient:
    """GitHub API client using gh CLI for authentication."""

    # -- PR metadata + diff + comments -----------------------------------

    def fetch_pr(self, number: int) -> dict:
        """Fetch PR metadata, diff, comments, and reviews."""
        # Get PR metadata
        pr = _run_gh_api(f"repos/{REPO}/pulls/{number}")

        # Get diff using gh pr view
        try:
            diff = _run_gh("pr", "view", str(number), "--repo", REPO, "--json", "diff", "--jq", ".diff")
        except RuntimeError:
            diff = ""

        if len(diff) > DIFF_CHAR_LIMIT:
            diff = diff[:DIFF_CHAR_LIMIT] + f"\n\n... diff truncated at {DIFF_CHAR_LIMIT} chars ..."

        # Get comments, reviews, and files
        comments = _run_gh_api(f"repos/{REPO}/issues/{number}/comments")
        review_comments = _run_gh_api(f"repos/{REPO}/pulls/{number}/comments")
        reviews = _run_gh_api(f"repos/{REPO}/pulls/{number}/reviews")
        files = _run_gh_api(f"repos/{REPO}/pulls/{number}/files")

        changed_files = [f["filename"] for f in files] if isinstance(files, list) else []

        return {
            "number": pr["number"],
            "title": pr["title"],
            "body": pr.get("body") or "",
            "state": pr["state"],
            "user": pr["user"]["login"],
            "labels": [l["name"] for l in pr.get("labels", [])],
            "base_ref": pr["base"]["ref"],
            "head_ref": pr["head"]["ref"],
            "head_sha": pr["head"]["sha"],
            "diff": diff,
            "changed_files": changed_files,
            "comments": [
                {"user": c["user"]["login"], "body": c["body"]}
                for c in (comments if isinstance(comments, list) else [])
            ],
            "review_comments": [
                {
                    "user": c["user"]["login"],
                    "path": c.get("path", ""),
                    "body": c["body"],
                }
                for c in (review_comments if isinstance(review_comments, list) else [])
            ],
            "reviews": [
                {
                    "user": r["user"]["login"],
                    "state": r["state"],
                    "body": r.get("body") or "",
                }
                for r in (reviews if isinstance(reviews, list) else [])
            ],
        }

    def fetch_diff(self, number: int) -> str:
        """Fetch raw unified diff for a PR."""
        try:
            diff = _run_gh("pr", "view", str(number), "--repo", REPO, "--json", "diff", "--jq", ".diff")
        except RuntimeError:
            diff = ""
        if len(diff) > DIFF_CHAR_LIMIT:
            diff = diff[:DIFF_CHAR_LIMIT] + f"\n\n... diff truncated at {DIFF_CHAR_LIMIT} chars ..."
        return diff

    # -- Linked references -----------------------------------------------

    def fetch_linked_refs(self, body: str, exclude_number: int | None = None) -> list[dict]:
        """Parse #refs and GitHub URLs from a PR body, fetch each."""
        numbers: set[int] = set()
        for pat in _REF_PATTERNS:
            for m in pat.finditer(body):
                numbers.add(int(m.group(1)))
        if exclude_number:
            numbers.discard(exclude_number)

        results = []
        for num in sorted(numbers):
            try:
                # Try as PR first
                data = _run_gh_api(f"repos/{REPO}/pulls/{num}")
                kind = "pull"
            except RuntimeError:
                try:
                    data = _run_gh_api(f"repos/{REPO}/issues/{num}")
                    kind = "issue"
                except RuntimeError:
                    continue
            results.append({
                "number": num,
                "kind": kind,
                "title": data["title"],
                "body": data.get("body") or "",
                "state": data["state"],
                "user": data["user"]["login"],
            })
        return results

    # -- File contents ---------------------------------------------------

    def fetch_file(self, path: str, ref: str = "main") -> str:
        """Fetch a file's contents from the repo at a given ref."""
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO}/contents/{path}?ref={ref}",
             "-H", "Accept: application/vnd.github.raw+json"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch file: {result.stderr.strip()}")
        return result.stdout

    # -- List PRs --------------------------------------------------------

    def list_recent_prs(self, state: str = "open", limit: int = 10, sort: str = "updated") -> list[dict]:
        """List recent PRs.

        Args:
            state: PR state filter (open, closed, all)
            limit: Maximum number of PRs to return
            sort: Sort field - "updated" (last activity) or "created" (newest first)
        """
        prs = _run_gh_api(f"repos/{REPO}/pulls", "-F", f"state={state}", "-F", f"per_page={limit}", "-F", f"sort={sort}")
        return [
            {
                "number": p["number"],
                "title": p["title"],
                "user": p["user"]["login"],
                "state": p["state"],
                "created_at": p.get("created_at"),
                "updated_at": p["updated_at"],
                "labels": [l["name"] for l in p.get("labels", [])],
            }
            for p in (prs if isinstance(prs, list) else [])
        ]

    # -- Post review -----------------------------------------------------

    def post_review_comment(self, pr_number: int, body: str, event: str = "COMMENT") -> dict:
        """Post a comment on a PR via ``gh`` CLI.
        event: APPROVE, REQUEST_CHANGES, or COMMENT."""
        result = subprocess.run(
            ["gh", "pr", "comment", str(pr_number), "--repo", REPO, "--body", body],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"gh pr comment failed: {result.stderr.strip()}")
        return {"posted_via": "gh_cli_comment", "pr_number": pr_number, "event": event}

    def post_inline_comment(self, pr_number: int, path: str, line: int, body: str, position: int | None = None, max_retries: int = 5) -> dict:
        """Post an inline comment on a specific line of a PR file.

        Uses GitHub's API with `commit_id` and `line` parameters.

        Args:
            pr_number: PR number
            path: File path in the repo
            line: Line number to comment on (in the new/head version of the file)
            body: Comment text
            position: Position in the diff (optional, deprecated parameter)
            max_retries: Maximum number of retry attempts (default: 5)

        Returns:
            dict with comment details
        """
        import time

        commit_id = self._get_pr_head_sha(pr_number)

        # If position not provided, try to find it by parsing the diff
        if position is None:
            pr = self.fetch_pr(pr_number)
            review_lines = self.parse_diff_for_review_lines(pr['diff'])
            matching = [rl for rl in review_lines if rl['path'] == path and rl['line'] == line]
            if matching:
                position = matching[0]['position']
            else:
                # Line not in diff, fallback to regular comment
                formatted_body = f"**{path}:{line}**\n\n{body}"
                result = subprocess.run(
                    ["gh", "pr", "comment", str(pr_number), "--repo", REPO, "--body", formatted_body],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(f"gh pr comment failed: {result.stderr.strip()}")
                return {"posted_via": "gh_cli_fallback", "pr_number": pr_number, "path": path, "line": line, "error": "Line not in diff"}

        # Retry with exponential backoff
        for attempt in range(max_retries):
            # Post inline comment using gh api with line parameter (new API)
            result = subprocess.run([
                "gh", "api", f"repos/{REPO}/pulls/{pr_number}/comments",
                "-X", "POST",
                "-f", f"body={body}",
                "-f", f"path={path}",
                "-F", f"line={line}",
                "-f", f"commit_id={commit_id}",
                "-f", "side=RIGHT",
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return {"posted_via": "gh_api_inline", "pr_number": pr_number, "path": path, "line": line, "position": position, "attempts": attempt + 1}

            error_msg = result.stderr.strip()

            # If it's a validation error (HTTP 422), try with position parameter
            if "422" in error_msg or "Validation Failed" in error_msg:
                # Fall back to position-based comment
                result = subprocess.run([
                    "gh", "api", f"repos/{REPO}/pulls/{pr_number}/comments",
                    "-X", "POST",
                    "-f", f"body={body}",
                    "-f", f"path={path}",
                    "-F", f"position={position}",
                    "-f", f"commit_id={commit_id}",
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    return {"posted_via": "gh_api_inline_position", "pr_number": pr_number, "path": path, "line": line, "position": position, "attempts": attempt + 1}

                break

            # For other errors, retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                time.sleep(wait_time)
                continue

        # All retries failed or validation error - fallback to formatted comment
        error_msg = result.stderr.strip()
        formatted_body = f"**{path}:{line}**\n\n{body}\n\n---\n*Note: Could not post as inline comment. Error: {error_msg}*"
        result = subprocess.run(
            ["gh", "pr", "comment", str(pr_number), "--repo", REPO, "--body", formatted_body],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"gh pr comment failed: {result.stderr.strip()}")
        return {"posted_via": "gh_cli_fallback", "pr_number": pr_number, "path": path, "line": line, "error": error_msg, "attempts": max_retries}

    def _get_pr_head_sha(self, pr_number: int) -> str:
        """Get the head commit SHA of a PR."""
        pr = _run_gh_api(f"repos/{REPO}/pulls/{pr_number}")
        return pr["head"]["sha"]

    # -- Inline comment workflow -----------------------------------------

    def parse_diff_for_review_lines(self, diff: str) -> list[dict]:
        """Parse a diff and extract lines suitable for inline comments.

        Returns list of dicts with:
        - path: file path
        - line: line number in the new version
        - position: position in the diff (for GitHub API)
        - content: actual line content
        - context: surrounding lines for context (3 before/after)

        Focuses on added lines (+ prefix) in the diff.
        """
        lines = diff.split("\n")
        results = []
        current_file = None
        current_line = 0
        diff_position = 0  # Track position in diff for GitHub API
        context_buffer = []

        for i, line in enumerate(lines):
            # Track file being modified
            if line.startswith("diff --git"):
                # Extract file path from "diff --git a/path b/path"
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove "b/" prefix
                context_buffer = []
                diff_position = 0  # Reset position for new file
                continue

            # Track line numbers from hunk headers
            if line.startswith("@@"):
                # Parse @@ -old_start,old_count +new_start,new_count @@
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line = int(match.group(1))
                context_buffer = []
                diff_position += 1  # Hunk header counts as a position
                continue

            # Skip if we don't have a file context yet
            if current_file is None:
                continue

            # Increment diff position for all lines in the hunk
            if not line.startswith("\\"):  # Skip "\ No newline at end of file"
                diff_position += 1

            # Track added lines
            if line.startswith("+") and not line.startswith("+++"):
                # Get context (last 3 lines from buffer)
                context_before = context_buffer[-3:] if len(context_buffer) >= 3 else context_buffer[:]

                # Get context after (next 3 lines)
                context_after = []
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j]
                    if next_line.startswith("@@") or next_line.startswith("diff --git"):
                        break
                    if not next_line.startswith("---") and not next_line.startswith("+++"):
                        context_after.append(next_line)

                results.append({
                    "path": current_file,
                    "line": current_line,
                    "position": diff_position,
                    "content": line[1:],  # Remove + prefix
                    "context": "\n".join(context_before + [line] + context_after),
                })
                current_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                # Deleted line, don't increment line counter
                context_buffer.append(line)
            elif not line.startswith("\\"):
                # Context line (no prefix) or other content
                if not line.startswith("+++") and not line.startswith("---"):
                    context_buffer.append(line)
                    current_line += 1

        return results

    def post_review_with_inline_comments(
        self,
        pr_number: int,
        summary: str,
        inline_comments: list[dict],
        event: str = "COMMENT",
    ) -> dict:
        """Post a review summary followed by inline comments one-by-one.

        Args:
            pr_number: PR number
            summary: Brief overall review summary
            inline_comments: List of dicts with keys: path, line, body
            event: Review event (COMMENT, APPROVE, REQUEST_CHANGES)

        Returns:
            Dict with summary of posted comments and success/failure status
        """
        # Deduplicate comments by (path, line) to prevent posting the same comment twice
        seen = set()
        deduplicated_comments = []
        duplicates_removed = 0

        for comment in inline_comments:
            key = (comment.get("path"), comment.get("line"))
            if key not in seen:
                seen.add(key)
                deduplicated_comments.append(comment)
            else:
                duplicates_removed += 1

        results = {
            "summary_posted": False,
            "summary_error": None,
            "inline_comments": [],
            "total": len(inline_comments),
            "deduplicated_total": len(deduplicated_comments),
            "duplicates_removed": duplicates_removed,
            "successful": 0,
            "failed": 0,
        }

        # Post summary first
        try:
            self.post_review_comment(pr_number, summary, event)
            results["summary_posted"] = True
        except Exception as e:
            results["summary_error"] = str(e)
            # Continue with inline comments even if summary fails

        # Post inline comments one-by-one (deduplicated)
        for comment in deduplicated_comments:
            try:
                path = comment["path"]
                line = comment["line"]
                body = comment["body"]

                result = self.post_inline_comment(pr_number, path, line, body)
                results["inline_comments"].append({
                    "path": path,
                    "line": line,
                    "status": "success",
                    "result": result,
                })
                results["successful"] += 1
            except Exception as e:
                results["inline_comments"].append({
                    "path": comment.get("path", "unknown"),
                    "line": comment.get("line", 0),
                    "status": "failed",
                    "error": str(e),
                })
                results["failed"] += 1

        return results

    # -- Smart Context Fetching ------------------------------------------

    def extract_imports_from_diff(self, diff: str, file_path: str | None = None) -> dict:
        """Extract import statements from changed lines in a diff.

        Returns:
            {
                "imports_by_file": {
                    "path/to/file.py": {
                        "added_imports": ["from x import y", "import z"],
                        "removed_imports": ["import old"],
                        "modules": ["x", "z"]
                    }
                }
            }
        """
        imports_by_file = {}
        lines = diff.split("\n")
        current_file = None

        for line in lines:
            # Track current file
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove "b/" prefix
                    if file_path and current_file != file_path:
                        current_file = None
                        continue
                    imports_by_file[current_file] = {
                        "added_imports": [],
                        "removed_imports": [],
                        "modules": []
                    }

            if not current_file:
                continue

            # Extract imports from added lines
            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:].strip()
                if re.match(r'^(from\s+[\w.]+\s+import|import\s+[\w.,\s]+)', content):
                    imports_by_file[current_file]["added_imports"].append(content)
                    # Extract module name
                    if content.startswith("from "):
                        match = re.match(r'from\s+([\w.]+)', content)
                        if match:
                            imports_by_file[current_file]["modules"].append(match.group(1))
                    elif content.startswith("import "):
                        match = re.match(r'import\s+([\w.]+)', content)
                        if match:
                            imports_by_file[current_file]["modules"].append(match.group(1))

            # Extract imports from removed lines
            elif line.startswith("-") and not line.startswith("---"):
                content = line[1:].strip()
                if re.match(r'^(from\s+[\w.]+\s+import|import\s+[\w.,\s]+)', content):
                    imports_by_file[current_file]["removed_imports"].append(content)

        # Remove files with no imports
        imports_by_file = {k: v for k, v in imports_by_file.items() if v["added_imports"] or v["removed_imports"]}

        # Limit to first 50 imports to avoid explosion
        for file_data in imports_by_file.values():
            file_data["added_imports"] = file_data["added_imports"][:50]
            file_data["modules"] = list(set(file_data["modules"]))[:20]

        return {"imports_by_file": imports_by_file}

    def fetch_file_context(
        self,
        path: str,
        line: int,
        context_lines: int = 20,
        ref: str = "main"
    ) -> dict:
        """Fetch surrounding context for a specific line in a file.

        Args:
            path: File path in repo
            line: Target line number
            context_lines: Lines before/after to fetch (default: 20, max: 50)
            ref: Git ref (default: "main")

        Returns:
            {
                "path": str,
                "line": int,
                "start_line": int,
                "end_line": int,
                "content": str,
                "total_file_lines": int
            }
        """
        # Cap context_lines at 50
        context_lines = min(context_lines, 50)

        # Fetch full file
        content = self.fetch_file(path, ref)
        lines = content.split("\n")
        total_lines = len(lines)

        # Calculate range
        start_line = max(1, line - context_lines)
        end_line = min(total_lines, line + context_lines)

        # Extract context (1-indexed)
        context_content = "\n".join(lines[start_line-1:end_line])

        return {
            "path": path,
            "line": line,
            "start_line": start_line,
            "end_line": end_line,
            "content": context_content,
            "total_file_lines": total_lines
        }

    def fetch_symbol_definition(
        self,
        symbol_name: str,
        search_paths: list[str] | None = None,
        ref: str = "main"
    ) -> dict:
        """Search for a symbol definition in the codebase.

        Args:
            symbol_name: Function/class name to find
            search_paths: Optional list of paths to search
            ref: Git ref (default: "main")

        Returns:
            {
                "symbol": str,
                "found": bool,
                "locations": [
                    {"path": str, "line": int, "context": str}
                ]
            }
        """
        # Use GitHub Code Search API via gh api
        query = f"{symbol_name} repo:{REPO}"
        if search_paths:
            query += f" path:{search_paths[0]}"

        try:
            results = _run_gh_api("search/code", "-F", f"q={query}", "-F", "per_page=3")

            locations = []
            for item in results.get("items", [])[:3]:
                # Fetch file content to find exact line
                try:
                    content = self.fetch_file(item["path"], ref)
                    lines = content.split("\n")

                    # Search for definition
                    for i, line_content in enumerate(lines, 1):
                        if f"def {symbol_name}" in line_content or f"class {symbol_name}" in line_content:
                            # Get 10-line context
                            start = max(0, i-5)
                            end = min(len(lines), i+5)
                            context = "\n".join(lines[start:end])

                            locations.append({
                                "path": item["path"],
                                "line": i,
                                "context": context
                            })
                            break
                except Exception:
                    continue

            return {
                "symbol": symbol_name,
                "found": len(locations) > 0,
                "locations": locations
            }
        except Exception:
            return {
                "symbol": symbol_name,
                "found": False,
                "locations": []
            }

    def check_related_config_files(self, changed_files: list[str]) -> dict:
        """Identify configuration files that might be affected by code changes.

        Args:
            changed_files: List of changed file paths from PR

        Returns:
            {
                "relevant_configs": [
                    {"path": str, "reason": str, "exists": bool}
                ]
            }
        """
        relevant_configs = []

        # Check for Python dependency changes
        if any("requirements" in f or "setup.py" in f or "pyproject.toml" in f for f in changed_files):
            relevant_configs.append({
                "path": "pyproject.toml",
                "reason": "Python dependencies changed",
                "exists": True
            })

        # Check for model changes
        if any("models/" in f for f in changed_files):
            relevant_configs.append({
                "path": "vllm/model_executor/models/__init__.py",
                "reason": "Model registry might need updates",
                "exists": True
            })

        # Check for config file changes
        if any("config" in f.lower() for f in changed_files):
            for f in changed_files:
                if "config" in f.lower() and f.endswith((".yaml", ".yml", ".json", ".toml")):
                    relevant_configs.append({
                        "path": f,
                        "reason": "Configuration file modified",
                        "exists": True
                    })

        # Check for CI/build changes
        if any(".github/" in f or "Dockerfile" in f or "Makefile" in f for f in changed_files):
            relevant_configs.append({
                "path": ".github/workflows/",
                "reason": "CI/build configuration changed",
                "exists": True
            })

        # Verify existence (simplified - skip for directories)
        for config in relevant_configs:
            try:
                if not config["path"].endswith("/"):
                    self.fetch_file(config["path"])
                config["exists"] = True
            except Exception:
                config["exists"] = False

        return {"relevant_configs": relevant_configs}
