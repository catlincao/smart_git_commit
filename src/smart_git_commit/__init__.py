"""Smart Git Commit - AI-powered git commit message generator.

This package provides a CLI tool that analyzes staged git changes and generates
semantic commit messages using LLMs, matching the project's historical style.
"""

__version__ = "0.1.0"
__author__ = "Smart Git Commit Contributors"
__license__ = "MIT"

from smart_git_commit.exceptions import (
    ConfigError,
    GitError,
    LLMError,
    SmartGitCommitError,
    ValidationError,
)
from smart_git_commit.utils import ExitCode, get_logger, setup_logging

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "SmartGitCommitError",
    "GitError",
    "ConfigError",
    "LLMError",
    "ValidationError",
    "ExitCode",
    "get_logger",
    "setup_logging",
]