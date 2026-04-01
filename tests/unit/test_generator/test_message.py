"""Unit tests for GeneratedMessage formatting."""

import pytest

from smart_git_commit.analyzer.style import CommitType
from smart_git_commit.generator.engine import GeneratedMessage


class TestGeneratedMessage:
    """Tests for GeneratedMessage dataclass."""

    def test_simple_message(self) -> None:
        """Test generating a simple commit message."""
        message = GeneratedMessage(subject="Add new feature")

        assert message.to_full_message() == "Add new feature"
        assert message.to_one_line() == "Add new feature"

    def test_semantic_commit_message(self) -> None:
        """Test generating a semantic commit message."""
        message = GeneratedMessage(
            commit_type=CommitType.FEAT,
            scope="auth",
            subject="add OAuth2 login support",
        )

        assert message.to_full_message() == "feat(auth): add OAuth2 login support"
        assert message.to_one_line() == "feat(auth): add OAuth2 login support"

    def test_message_with_body(self) -> None:
        """Test generating a commit message with body."""
        message = GeneratedMessage(
            commit_type=CommitType.FEAT,
            subject="add new feature",
            body="- Implementation details\n- More context",
        )

        expected = "feat: add new feature\n\n- Implementation details\n- More context"
        assert message.to_full_message() == expected

    def test_message_with_breaking_change(self) -> None:
        """Test generating a message with breaking change."""
        message = GeneratedMessage(
            commit_type=CommitType.FEAT,
            scope="api",
            subject="update API endpoints",
            body="Updated all endpoints to v2",
            breaking_change="Old endpoints no longer work",
        )

        result = message.to_full_message()
        assert "feat(api): update API endpoints" in result
        assert "Updated all endpoints to v2" in result
        assert "BREAKING CHANGE: Old endpoints no longer work" in result

    def test_message_without_type(self) -> None:
        """Test message without commit type."""
        message = GeneratedMessage(
            subject="some minor changes",
            body="Just some updates",
        )

        expected = "some minor changes\n\nJust some updates"
        assert message.to_full_message() == expected

    def test_all_commit_types(self) -> None:
        """Test all semantic commit types."""
        types = [
            (CommitType.FEAT, "feat"),
            (CommitType.FIX, "fix"),
            (CommitType.DOCS, "docs"),
            (CommitType.STYLE, "style"),
            (CommitType.REFACTOR, "refactor"),
            (CommitType.TEST, "test"),
            (CommitType.CHORE, "chore"),
            (CommitType.BUILD, "build"),
            (CommitType.CI, "ci"),
            (CommitType.PERF, "perf"),
        ]

        for commit_type, expected_prefix in types:
            message = GeneratedMessage(
                commit_type=commit_type,
                subject="test message",
            )
            assert message.to_one_line() == f"{expected_prefix}: test message"
