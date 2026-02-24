# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM-Omni project

"""Knowledge base for storing and retrieving review context."""

from __future__ import annotations

from pathlib import Path


class KnowledgeBase:
    def __init__(self, root: Path):
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)
        (self._root / "reviews").mkdir(exist_ok=True)

    def load_all(self) -> dict[str, str]:
        """Load all markdown files from the knowledge base."""
        result: dict[str, str] = {}
        for p in sorted(self._root.rglob("*.md")):
            key = str(p.relative_to(self._root))
            result[key] = p.read_text()
        return result

    def load_file(self, name: str) -> str:
        """Load a specific knowledge base file."""
        path = self._root / name
        if not path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {name}")
        return path.read_text()

    def save_review(self, pr_number: int, title: str, summary: str) -> str:
        """Save a review summary for a PR."""
        path = self._root / "reviews" / f"pr-{pr_number}.md"
        content = f"# PR #{pr_number}: {title}\n\n{summary}\n"
        path.write_text(content)
        return str(path)

    def add_note(self, filename: str, content: str) -> str:
        """Create or update a knowledge base note."""
        if not filename.endswith(".md"):
            filename += ".md"
        path = self._root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def list_files(self) -> list[str]:
        """List all files in the knowledge base."""
        return sorted(
            str(p.relative_to(self._root)) for p in self._root.rglob("*.md")
        )
