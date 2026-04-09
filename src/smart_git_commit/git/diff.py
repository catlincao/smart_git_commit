"""Git diff extraction for Smart Git Commit.

This module provides functionality for extracting and analyzing staged changes.
"""

import re
from dataclasses import dataclass
from typing import Literal

from git import Repo
from git.diff import Diff
from git.exc import GitCommandError

from smart_git_commit.exceptions import GitError
from smart_git_commit.utils import ExitCode, get_logger

logger = get_logger()

ChangeType = Literal["added", "modified", "deleted", "renamed"]


@dataclass
class FileChange:
    """Represents a single file change.

    Attributes:
        path: Path to the file (relative to repo root)
        change_type: Type of change (added, modified, deleted, renamed)
        additions: Number of lines added
        deletions: Number of lines deleted
        diff_content: The actual diff content (optional)
    """

    path: str
    change_type: ChangeType
    additions: int
    deletions: int
    diff_content: str | None = None


class DiffExtractor:
    """Extracts and processes git diffs.

    This class handles extraction of staged changes and conversion
    to a format suitable for LLM analysis.

    Attributes:
        repo: The GitPython Repo instance
        max_size: Maximum diff size in bytes
    """

    def __init__(self, repo: Repo, max_size: int = 100_000) -> None:
        """Initialize the diff extractor.

        Args:
            repo: The GitPython Repo instance
            max_size: Maximum diff size in bytes before truncation
        """
        self.repo = repo
        self.max_size = max_size

    def get_staged_diff(self) -> str:
        """Get the staged diff as a string.

        Returns:
            The git diff of staged changes

        Raises:
            GitError: If failed to read staged diff
        """
        try:
            diff = self.repo.git.diff("--cached", "--no-color")
        except GitCommandError as e:
            raise GitError(
                f"Failed to read staged diff: {e}",
                suggestion="Make sure you have staged changes with: git add <files>",
                exit_code=ExitCode.NO_STAGED_CHANGES,
            ) from e

        if len(diff) > self.max_size:
            logger.warning(
                f"Diff size ({len(diff)}) exceeds maximum ({self.max_size}), truncating"
            )
            diff = diff[:self.max_size] + "\n\n... [diff truncated due to size]"

        return diff

    def get_file_changes(self) -> list[FileChange]:
        """Get detailed information about each changed file.

        Returns:
            List of FileChange objects for staged files
        """
        changes: list[FileChange] = []

        # Get diff between index and HEAD
        diffs = self.repo.index.diff("HEAD")

        for diff_item in diffs:
            change = self._parse_diff_item(diff_item)
            if change:
                changes.append(change)

        return changes

    def _get_line_stats(self, path: str) -> tuple[int, int]:
        """Get line addition/deletion stats for a file using git diff --stat.

        Args:
            path: Path to the file

        Returns:
            Tuple of (additions, deletions)
        """
        try:
            stat_output = self.repo.git.diff("--cached", "--no-color", "--", path, "--stat")
            # Parse output like: "1 file changed, 5 insertions(+), 2 deletions(-)"
            additions = 0
            deletions = 0
            if "insertion" in stat_output:
                match = re.search(r"(\d+)\s+insertion", stat_output)
                if match:
                    additions = int(match.group(1))
            if "deletion" in stat_output:
                match = re.search(r"(\d+)\s+deletion", stat_output)
                if match:
                    deletions = int(match.group(1))
            return additions, deletions
        except Exception:
            return 0, 0

    def _parse_diff_item(self, diff_item: Diff) -> FileChange | None:
        """Parse a git diff item into a FileChange.

        Args:
            diff_item: The git diff item to parse

        Returns:
            FileChange object or None if cannot be parsed
        """
        try:
            # Determine change type
            if diff_item.new_file:
                change_type: ChangeType = "added"
            elif diff_item.deleted_file:
                change_type = "deleted"
            elif diff_item.renamed:
                change_type = "renamed"
            else:
                change_type = "modified"

            # Get file path
            path = diff_item.a_path or diff_item.b_path or ""

            # Get line stats using git diff --stat
            additions, deletions = self._get_line_stats(path)

            # Get diff content for this file
            diff_content = self.repo.git.diff(
                "--cached", "--no-color", "--", path
            ) if not diff_item.deleted_file else None

            return FileChange(
                path=path,
                change_type=change_type,
                additions=additions,
                deletions=deletions,
                diff_content=diff_content,
            )
        except Exception as e:
            logger.warning(f"Failed to parse diff item: {e}")
            return None

    def get_summary(self) -> dict:
        """Get a summary of the staged changes.

        Returns:
            Dictionary with summary statistics
        """
        changes = self.get_file_changes()

        return {
            "files_changed": len(changes),
            "additions": sum(c.additions for c in changes),
            "deletions": sum(c.deletions for c in changes),
            "file_list": [c.path for c in changes],
        }
