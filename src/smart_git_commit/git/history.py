"""Git commit history analysis for Smart Git Commit.

This module provides functionality for analyzing recent commit history
to detect project commit style conventions.
"""

import re
from collections import Counter
from typing import Optional

from git import Repo
from git.objects.commit import Commit

from smart_git_commit.utils import get_logger

logger = get_logger()


class CommitStyleAnalyzer:
    """Analyzes commit history to detect project conventions.

    This class examines recent commits to determine:
    - Whether the project uses semantic commits
    - Common commit types and scopes
    - Average commit message length
    - Language patterns

    Attributes:
        repo: The GitPython Repo instance
        max_commits: Maximum number of commits to analyze
    """

    # Semantic commit types
    SEMANTIC_TYPES = [
        "feat", "fix", "docs", "style", "refactor",
        "test", "chore", "build", "ci", "perf",
    ]

    def __init__(self, repo: Repo, max_commits: int = 50) -> None:
        """Initialize the style analyzer.

        Args:
            repo: The GitPython Repo instance
            max_commits: Maximum number of commits to analyze (default: 50)
        """
        self.repo = repo
        self.max_commits = max_commits

    def analyze(self) -> dict:
        """Analyze commit history and return style information.

        Returns:
            Dictionary containing detected style information:
            - uses_semantic_commits: bool
            - common_types: list of common commit types
            - common_scopes: list of common scopes
            - average_length: average message length
            - examples: list of example commit messages
        """
        commits = self._get_recent_commits()

        if not commits:
            return self._default_style()

        messages = [c.message.split("\n")[0] for c in commits if c.message]

        return {
            "uses_semantic_commits": self._detect_semantic_commits(messages),
            "common_types": self._extract_common_types(messages),
            "common_scopes": self._extract_common_scopes(messages),
            "average_length": self._calculate_average_length(messages),
            "examples": messages[:10],
        }

    def _get_recent_commits(self) -> list[Commit]:
        """Get recent commits from the repository.

        Returns:
            List of recent Commit objects
        """
        try:
            return list(self.repo.iter_commits("HEAD", max_count=self.max_commits))
        except Exception as e:
            logger.warning(f"Failed to get commit history: {e}")
            return []

    def _detect_semantic_commits(self, messages: list[str]) -> bool:
        """Detect if the project uses semantic commits.

        Args:
            messages: List of commit message subjects

        Returns:
            True if semantic commits are detected
        """
        if not messages:
            return False

        semantic_pattern = re.compile(
            r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf)"
            r"(\(.+\))?!?:\s.+"
        )

        semantic_count = sum(
            1 for msg in messages if semantic_pattern.match(msg)
        )

        # Consider it semantic if > 50% of commits follow the pattern
        return semantic_count / len(messages) > 0.5

    def _extract_common_types(self, messages: list[str]) -> list[str]:
        """Extract common commit types from messages.

        Args:
            messages: List of commit message subjects

        Returns:
            List of common commit types (top 5)
        """
        type_pattern = re.compile(r"^(\w+)(?:\(.+\))?!?:")
        types = []

        for msg in messages:
            match = type_pattern.match(msg)
            if match:
                commit_type = match.group(1).lower()
                if commit_type in self.SEMANTIC_TYPES:
                    types.append(commit_type)

        counter = Counter(types)
        return [t for t, _ in counter.most_common(5)]

    def _extract_common_scopes(self, messages: list[str]) -> list[str]:
        """Extract common scopes from messages.

        Args:
            messages: List of commit message subjects

        Returns:
            List of common scopes (top 5)
        """
        scope_pattern = re.compile(r"^\w+\(([^)]+)\)!?:")
        scopes = []

        for msg in messages:
            match = scope_pattern.match(msg)
            if match:
                scopes.append(match.group(1).lower())

        counter = Counter(scopes)
        return [s for s, _ in counter.most_common(5)]

    def _calculate_average_length(self, messages: list[str]) -> int:
        """Calculate average commit message length.

        Args:
            messages: List of commit message subjects

        Returns:
            Average length in characters
        """
        if not messages:
            return 50

        return int(sum(len(m) for m in messages) / len(messages))

    def _default_style(self) -> dict:
        """Return default style when no history is available.

        Returns:
            Dictionary with default style values
        """
        return {
            "uses_semantic_commits": True,
            "common_types": ["feat", "fix", "docs"],
            "common_scopes": [],
            "average_length": 50,
            "examples": [],
        }


def analyze_commit_style(repo: Repo, max_commits: int = 50) -> dict:
    """Convenience function to analyze commit style.

    Args:
        repo: The GitPython Repo instance
        max_commits: Maximum number of commits to analyze

    Returns:
        Dictionary containing detected style information
    """
    analyzer = CommitStyleAnalyzer(repo, max_commits)
    return analyzer.analyze()
