"""Commit style analysis for Smart Git Commit.

This module provides high-level style analysis functionality that combines
git history analysis with configuration settings.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from git import Repo

from smart_git_commit.config.models import StyleConfig
from smart_git_commit.git.history import analyze_commit_style
from smart_git_commit.utils import get_logger

logger = get_logger()


class CommitType(Enum):
    """Semantic commit types following Conventional Commits specification."""

    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    BUILD = "build"
    CI = "ci"
    PERF = "perf"


@dataclass
class CommitStyle:
    """Represents detected project commit style conventions.

    Attributes:
        uses_semantic_commits: Whether the project uses semantic commits
        common_types: List of commonly used commit types
        common_scopes: List of commonly used scopes
        average_subject_length: Average length of commit subjects
        examples: List of example commit messages from history
    """

    uses_semantic_commits: bool
    common_types: list[CommitType]
    common_scopes: list[str]
    average_subject_length: int
    examples: list[str]

    @property
    def suggested_types(self) -> list[CommitType]:
        """Get suggested commit types based on project history.

        Returns:
            List of suggested commit types (up to 5)
        """
        if self.common_types:
            return self.common_types[:5]
        return [CommitType.FEAT, CommitType.FIX, CommitType.DOCS]

    def to_prompt_context(self) -> str:
        """Convert style to a string for LLM prompts.

        Returns:
            String describing the project style
        """
        lines = []

        if self.uses_semantic_commits:
            lines.append("This project uses Semantic Commits (Conventional Commits).")
            lines.append(f"Common commit types: {[t.value for t in self.suggested_types]}")
        else:
            lines.append("This project uses simple commit messages.")

        if self.common_scopes:
            lines.append(f"Common scopes: {self.common_scopes}")

        lines.append(f"Average subject length: {self.average_subject_length} characters")

        return "\n".join(lines)


class StyleDetector:
    """Detects and manages commit style for a project.

    This class combines automatic detection from git history with
    user configuration preferences.

    Attributes:
        repo: The GitPython Repo instance
        config: User style configuration
    """

    def __init__(self, repo: Repo, config: Optional[StyleConfig] = None) -> None:
        """Initialize the style detector.

        Args:
            repo: The GitPython Repo instance
            config: Optional user style configuration
        """
        self.repo = repo
        self.config = config or StyleConfig()

    def detect(self) -> CommitStyle:
        """Detect the project commit style.

        Analyzes git history and combines with configuration
        to produce the final style.

        Returns:
            CommitStyle representing the detected conventions
        """
        logger.debug("Detecting commit style from history")

        # Analyze git history
        history_style = analyze_commit_style(self.repo)

        # Apply configuration overrides
        uses_semantic = (
            self.config.use_semantic_commits
            if history_style.get("uses_semantic_commits")
            else False
        )

        # Convert common types strings to CommitType enums
        common_types = []
        for type_str in history_style.get("common_types", []):
            try:
                common_types.append(CommitType(type_str))
            except ValueError:
                continue

        return CommitStyle(
            uses_semantic_commits=uses_semantic,
            common_types=common_types,
            common_scopes=history_style.get("common_scopes", []),
            average_subject_length=history_style.get("average_length", 50),
            examples=history_style.get("examples", []),
        )


def detect_style(repo: Repo, config: Optional[StyleConfig] = None) -> CommitStyle:
    """Convenience function to detect commit style.

    Args:
        repo: The GitPython Repo instance
        config: Optional user style configuration

    Returns:
        CommitStyle representing detected conventions
    """
    detector = StyleDetector(repo, config)
    return detector.detect()
