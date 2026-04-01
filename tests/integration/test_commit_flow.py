"""Integration test for main commit flow."""

import tempfile
from pathlib import Path

import pytest
from git import Repo

from smart_git_commit.config import Config
from smart_git_commit.config.models import LLMConfig, StyleConfig


class TestCommitFlow:
    """Integration tests for the commit message generation flow."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository."""
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

            yield tmp_dir, repo

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return Config(
            llm=LLMConfig(
                base_url="https://api.openai.com/v1",
                model="gpt-4o-mini",
                api_key="sk-test-key",
            ),
            style=StyleConfig(
                use_semantic_commits=True,
            ),
        )

    def test_git_repository_detection(self, temp_git_repo) -> None:
        """Test that we can detect a valid git repository."""
        from smart_git_commit.git import GitRepository, RepositoryStatus

        repo_path, _ = temp_git_repo
        git_repo = GitRepository(path=Path(repo_path))

        # Initially no staged changes
        status = git_repo.validate()
        assert status == RepositoryStatus.NO_STAGED_CHANGES

    def test_staged_changes_detection(self, temp_git_repo) -> None:
        """Test detecting staged changes."""
        from smart_git_commit.git import GitRepository, RepositoryStatus

        repo_path, git_repo = temp_git_repo

        # Create and stage a new file
        test_file = Path(repo_path) / "new_file.py"
        test_file.write_text("print('hello')")
        git_repo.index.add(["new_file.py"])

        git_wrapper = GitRepository(path=Path(repo_path))
        status = git_wrapper.validate()

        assert status == RepositoryStatus.VALID
        assert git_wrapper.has_staged_changes()

    def test_diff_extraction(self, temp_git_repo) -> None:
        """Test extracting staged diff."""
        from smart_git_commit.git.diff import DiffExtractor

        repo_path, git_repo = temp_git_repo

        # Create and stage changes
        test_file = Path(repo_path) / "test.txt"
        test_file.write_text("modified content")
        git_repo.index.add(["test.txt"])

        extractor = DiffExtractor(git_repo)
        diff = extractor.get_staged_diff()

        assert isinstance(diff, str)
        assert "diff --git" in diff or diff == ""

    def test_commit_history_analysis(self, temp_git_repo) -> None:
        """Test analyzing commit history."""
        from smart_git_commit.git.history import analyze_commit_style

        _, git_repo = temp_git_repo

        style = analyze_commit_style(git_repo)

        assert isinstance(style, dict)
        assert "uses_semantic_commits" in style
        assert "examples" in style

    def test_config_loading(self) -> None:
        """Test configuration model defaults."""
        # Test Config model defaults directly (not loading from file which may have user overrides)
        config = Config()

        assert isinstance(config, Config)
        assert config.llm.model == "gpt-4o-mini"
        assert config.style.use_semantic_commits is True

    def test_token_truncation(self) -> None:
        """Test diff truncation."""
        from smart_git_commit.analyzer.tokenizer import truncate_diff

        # Create a large diff
        large_diff = "diff --git a/test.py b/test.py\n" + "+ line\n" * 10000

        truncated, was_truncated = truncate_diff(large_diff, max_tokens=100)

        assert was_truncated is True
        assert "truncated" in truncated.lower() or len(truncated) < len(large_diff)
