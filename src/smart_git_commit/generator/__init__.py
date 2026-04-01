"""Generator module for Smart Git Commit.

This module provides the commit message generation engine that orchestrates
the entire process from git diff analysis to LLM-based message generation.
"""

from smart_git_commit.generator.engine import (
    GeneratedMessage,
    MessageGenerator,
    generate_commit_message,
)

__all__ = [
    "GeneratedMessage",
    "MessageGenerator",
    "generate_commit_message",
]
