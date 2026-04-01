"""Unit tests for help text content."""

import subprocess
import sys

import pytest


class TestHelpCommand:
    """Tests for CLI help functionality."""

    def test_help_flag(self) -> None:
        """Test that --help displays usage information."""
        result = subprocess.run(
            [sys.executable, "-m", "smart_git_commit", "--help"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0

        # Should contain help text
        assert "AI-powered git commit message generator" in result.stdout or "sgc" in result.stdout

    def test_version_flag(self) -> None:
        """Test that --version displays version."""
        result = subprocess.run(
            [sys.executable, "-m", "smart_git_commit", "--version"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully
        assert result.returncode == 0

        # Should contain version
        assert "0.1.0" in result.stdout or "smart-git-commit" in result.stdout


class TestExitCodes:
    """Tests for CLI exit codes."""

    def test_success_exit_code(self) -> None:
        """Test that successful command returns 0."""
        result = subprocess.run(
            [sys.executable, "-m", "smart_git_commit", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_not_git_repo_exit_code(self, tmp_path) -> None:
        """Test exit code when not in a git repo."""
        result = subprocess.run(
            [sys.executable, "-m", "smart_git_commit"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should exit with code 2 (NOT_A_REPO)
        assert result.returncode == 2

    def test_no_staged_changes_exit_code(self, tmp_path) -> None:
        """Test exit code when no staged changes."""
        from git import Repo

        # Initialize empty git repo
        Repo.init(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "smart_git_commit"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should exit with code 3 (NO_STAGED_CHANGES) or 2 (NOT_A_REPO if no commits)
        assert result.returncode in [2, 3]
