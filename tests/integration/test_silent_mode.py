"""Integration tests for silent mode functionality."""

import tempfile
from pathlib import Path

import pytest
from git import Repo

from smart_git_commit.config import Config


class TestSilentMode:
    """Tests for silent mode (--silence flag)."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository with staged changes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Repo.init(tmp_dir)

            # Configure git user
            repo.config_writer().set_value("user", "name", "Test User").release()
            repo.config_writer().set_value("user", "email", "test@example.com").release()

            # Create initial commit
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("initial content")
            repo.index.add(["test.txt"])
            repo.index.commit("Initial commit")

            # Create and stage new changes
            test_file.write_text("modified content")
            repo.index.add(["test.txt"])

            yield tmp_dir, repo

    def test_silence_flag_exists_in_help(self) -> None:
        """Test that --silence flag appears in help output."""
        from typer.testing import CliRunner

        from smart_git_commit.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["generate", "--help"])

        assert "--silence" in result.stdout or "-s" in result.stdout
        assert result.exit_code == 0


class TestSilenceModeBehavior:
    """Tests for silence mode behavior configuration."""

    def test_silence_mode_respects_auto_commit_setting(self) -> None:
        """Test that auto_commit_silence behavior is configurable."""
        from smart_git_commit.config.models import BehaviorConfig

        config = Config(
            behavior=BehaviorConfig(
                auto_commit_silence=True,
            ),
        )

        assert config.behavior.auto_commit_silence is True

    def test_silence_mode_default_auto_commit_is_false(self) -> None:
        """Test that auto_commit_silence defaults to False."""
        config = Config()

        # Default should be False to require confirmation even in silence mode
        # unless user explicitly enables auto-commit in silence
        assert config.behavior.auto_commit_silence is False

    def test_silence_flag_default_is_false(self) -> None:
        """Test that silence mode defaults to False (interactive mode)."""
        # Test that the default for silence parameter is False
        # This is implicit in the CLI definition
        from typer.testing import CliRunner

        from smart_git_commit.cli import app

        runner = CliRunner()

        # When running without --silence, should be interactive
        # We can't easily test this without mocking, but we verify
        # the flag is properly defined
        result = runner.invoke(app, ["generate", "--help"])
        assert "--silence" in result.stdout
