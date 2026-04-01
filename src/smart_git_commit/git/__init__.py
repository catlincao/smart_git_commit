"""Git operations module for Smart Git Commit.

This module provides functionality for interacting with git repositories,
including repository validation, diff extraction, and commit history analysis.
"""

from smart_git_commit.git.diff import DiffExtractor, FileChange
from smart_git_commit.git.history import CommitStyleAnalyzer, analyze_commit_style
from smart_git_commit.git.repository import GitRepository, RepositoryStatus

__all__ = [
    "GitRepository",
    "RepositoryStatus",
    "DiffExtractor",
    "FileChange",
    "CommitStyleAnalyzer",
    "analyze_commit_style",
]
