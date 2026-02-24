"""GitHub API client for vllm-project/vllm-omni."""

from __future__ import annotations

import os
import re
import subprocess

import httpx

REPO = "vllm-project/vllm-omni"
BASE = f"https://api.github.com/repos/{REPO}"
DIFF_CHAR_LIMIT = 200_000

# Patterns for linked refs in PR bodies
_REF_PATTERNS = [
    re.compile(r"(?:https?://github\.com/[\w\-]+/[\w\-]+/(?:issues|pull)/(\d+))"),
    re.compile(r"(?<!\w)#(\d+)"),
]


class GitHubClient:
    def __init__(self, token: str | None = None):
        if token is None:
            # First try to get token from gh CLI
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                token = result.stdout.strip()
            else:
                # Fall back to environment variable
                token = os.environ.get("GITHUB_TOKEN", "")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._http = httpx.Client(headers=headers, timeout=30)

    # -- PR metadata + diff + comments -----------------------------------

    def fetch_pr(self, number: int) -> dict:
        """Fetch PR metadata, diff, comments, and reviews."""
        pr = self._get(f"/pulls/{number}")
        diff = self.fetch_diff(number)
        comments = self._get(f"/issues/{number}/comments")
        review_comments = self._get(f"/pulls/{number}/comments")
        reviews = self._get(f"/pulls/{number}/reviews")
        files = self._get(f"/pulls/{number}/files")

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
        url = f"{BASE}/pulls/{number}"
        resp = self._http.get(url, headers={"Accept": "application/vnd.github.diff"})
        resp.raise_for_status()
        text = resp.text
        if len(text) > DIFF_CHAR_LIMIT:
            text = text[:DIFF_CHAR_LIMIT] + f"\n\n... diff truncated at {DIFF_CHAR_LIMIT} chars ..."
        return text

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
                # Try as PR first, fall back to issue
                data = self._get(f"/pulls/{num}")
                kind = "pull"
            except httpx.HTTPStatusError:
                try:
                    data = self._get(f"/issues/{num}")
                    kind = "issue"
                except httpx.HTTPStatusError:
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
        url = f"{BASE}/contents/{path}"
        resp = self._http.get(url, params={"ref": ref},
                              headers={"Accept": "application/vnd.github.raw+json"})
        resp.raise_for_status()
        return resp.text

    # -- List PRs --------------------------------------------------------

    def list_recent_prs(self, state: str = "open", limit: int = 10) -> list[dict]:
        """List recent PRs."""
        prs = self._get(f"/pulls", params={"state": state, "per_page": limit, "sort": "updated"})
        return [
            {
                "number": p["number"],
                "title": p["title"],
                "user": p["user"]["login"],
                "state": p["state"],
                "updated_at": p["updated_at"],
                "labels": [l["name"] for l in p.get("labels", [])],
            }
            for p in (prs if isinstance(prs, list) else [])
        ]

    # -- Post review -----------------------------------------------------

    def post_review_comment(self, pr_number: int, body: str, event: str = "COMMENT") -> dict:
        """Post a review on a PR via ``gh`` CLI. event: APPROVE, REQUEST_CHANGES, or COMMENT."""
        event_flag = {"APPROVE": "--approve", "REQUEST_CHANGES": "--request-changes"}.get(event, "--comment")
        result = subprocess.run(
            ["gh", "pr", "review", str(pr_number), "--repo", REPO, event_flag, "--body", body],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"gh pr review failed: {result.stderr.strip()}")
        return {"posted_via": "gh_cli", "pr_number": pr_number, "event": event}

    # -- Helpers ---------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        url = f"{BASE}{path}" if path.startswith("/") else path
        resp = self._http.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
