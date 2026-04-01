"""Unit tests for Config model validation."""

import pytest
from pydantic import ValidationError

from smart_git_commit.config.models import (
    BehaviorConfig,
    Config,
    LLMConfig,
    StyleConfig,
)


class TestLLMConfig:
    """Tests for LLMConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = LLMConfig()

        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-4o-mini"
        assert config.timeout_seconds == 30

    def test_base_url_validation(self) -> None:
        """Test base URL validation."""
        # Valid URLs
        LLMConfig(base_url="https://api.openai.com/v1")
        LLMConfig(base_url="http://localhost:8080/v1")
        LLMConfig(base_url="https://example.com/path/")

        # Invalid URLs
        with pytest.raises(ValidationError):
            LLMConfig(base_url="not-a-url")

        with pytest.raises(ValidationError):
            LLMConfig(base_url="ftp://invalid.com")

    def test_timeout_validation(self) -> None:
        """Test timeout value validation."""
        # Valid timeouts
        LLMConfig(timeout_seconds=5)
        LLMConfig(timeout_seconds=300)
        LLMConfig(timeout_seconds=60)

        # Invalid timeouts
        with pytest.raises(ValidationError):
            LLMConfig(timeout_seconds=4)

        with pytest.raises(ValidationError):
            LLMConfig(timeout_seconds=301)

        with pytest.raises(ValidationError):
            LLMConfig(timeout_seconds=0)

    def test_api_key_masking(self) -> None:
        """Test that API key is properly masked."""
        config = LLMConfig(api_key="sk-secret-key")

        # Should be masked in string representation
        assert "secret" not in str(config)
        assert config.api_key.get_secret_value() == "sk-secret-key"


class TestStyleConfig:
    """Tests for StyleConfig model."""

    def test_default_values(self) -> None:
        """Test default style configuration."""
        config = StyleConfig()

        assert config.language == "en_US"
        assert config.use_semantic_commits is True
        assert config.max_diff_tokens == 4000

    def test_language_validation(self) -> None:
        """Test language code validation."""
        # Valid codes
        StyleConfig(language="en_US")
        StyleConfig(language="zh_CN")
        StyleConfig(language="de_DE")

        # Invalid codes
        with pytest.raises(ValidationError):
            StyleConfig(language="invalid")

        with pytest.raises(ValidationError):
            StyleConfig(language="EN_us")

        with pytest.raises(ValidationError):
            StyleConfig(language="english")

    def test_max_tokens_validation(self) -> None:
        """Test max_diff_tokens validation."""
        # Valid values
        StyleConfig(max_diff_tokens=1000)
        StyleConfig(max_diff_tokens=8000)
        StyleConfig(max_diff_tokens=4000)

        # Invalid values
        with pytest.raises(ValidationError):
            StyleConfig(max_diff_tokens=999)

        with pytest.raises(ValidationError):
            StyleConfig(max_diff_tokens=8001)


class TestBehaviorConfig:
    """Tests for BehaviorConfig model."""

    def test_default_values(self) -> None:
        """Test default behavior configuration."""
        config = BehaviorConfig()

        assert config.auto_commit_silence is False
        assert config.confirm_before_commit is True
        assert config.show_token_count is False


class TestConfig:
    """Tests for root Config model."""

    def test_default_configuration(self) -> None:
        """Test complete default configuration."""
        config = Config()

        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.style, StyleConfig)
        assert isinstance(config.behavior, BehaviorConfig)

    def test_is_configured_check(self) -> None:
        """Test is_configured method."""
        # Not configured without API key
        config = Config()
        assert config.is_configured() is False

        # Configured with API key
        config = Config(llm=LLMConfig(api_key="sk-test"))
        assert config.is_configured() is True

    def test_nested_configuration(self) -> None:
        """Test nested configuration updates."""
        config = Config(
            llm=LLMConfig(
                base_url="https://custom.api.com",
                model="gpt-4",
                api_key="sk-test",
            ),
            style=StyleConfig(
                use_semantic_commits=False,
                language="de_DE",
            ),
        )

        assert config.llm.base_url == "https://custom.api.com"
        assert config.llm.model == "gpt-4"
        assert config.style.use_semantic_commits is False
        assert config.style.language == "de_DE"
