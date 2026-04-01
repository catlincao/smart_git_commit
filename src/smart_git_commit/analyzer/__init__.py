"""Analyzer module for Smart Git Commit.

This module provides functionality for analyzing git diffs and commit history
to detect project conventions and manage token limits.
"""

from smart_git_commit.analyzer.style import (
    CommitStyle,
    CommitType,
    StyleDetector,
    detect_style,
)
from smart_git_commit.analyzer.tokenizer import (
    DiffTruncator,
    TokenCounter,
    count_tokens,
    truncate_diff,
)

__all__ = [
    "CommitStyle",
    "CommitType",
    "StyleDetector",
    "detect_style",
    "TokenCounter",
    "DiffTruncator",
    "count_tokens",
    "truncate_diff",
]
