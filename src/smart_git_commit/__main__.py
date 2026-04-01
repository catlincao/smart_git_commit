"""Entry point for running Smart Git Commit as a module.

This module allows the package to be executed with:
    python -m smart_git_commit

It simply delegates to the CLI module.
"""

import sys

from smart_git_commit.cli import app

if __name__ == "__main__":
    app()