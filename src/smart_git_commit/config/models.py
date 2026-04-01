"""Configuration models for Smart Git Commit.

This module defines Pydantic models for configuration management,
including LLM settings, style preferences, and behavior settings.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class LLMConfig(BaseModel):
    """LLM API configuration settings.

    Attributes:
        base_url: Base URL for the LLM API endpoint
        model: Name of the model to use (e.g., "gpt-4o-mini")
        api_key: API key for authentication (masked in output)
        timeout_seconds: Request timeout in seconds (5-300)
    """

    model_config = ConfigDict(frozen=False)

    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the LLM API",
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="Model name to use for generation",
    )
    api_key: SecretStr = Field(
        default=SecretStr(""),
        description="API key for LLM authentication",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate the base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")


class StyleConfig(BaseModel):
    """Commit style preferences.

    Attributes:
        language: Language code for commit messages (e.g., "en_US")
        use_semantic_commits: Whether to enforce semantic commit format
        max_diff_tokens: Maximum tokens to send in diff (1000-8000)
    """

    model_config = ConfigDict(frozen=False)

    language: str = Field(
        default="en_US",
        pattern=r"^[a-z]{2}_[A-Z]{2}$",
        description="Language code for commit messages",
    )
    use_semantic_commits: bool = Field(
        default=True,
        description="Whether to use semantic commit format",
    )
    max_diff_tokens: int = Field(
        default=4000,
        ge=1000,
        le=8000,
        description="Maximum tokens for diff analysis",
    )


class BehaviorConfig(BaseModel):
    """Behavioral settings for the tool.

    Attributes:
        auto_commit_silence: Whether to auto-commit in silence mode
        confirm_before_commit: Whether to confirm before committing
        show_token_count: Whether to display token usage info
    """

    model_config = ConfigDict(frozen=False)

    auto_commit_silence: bool = Field(
        default=False,
        description="Auto-commit without confirmation in silence mode",
    )
    confirm_before_commit: bool = Field(
        default=True,
        description="Confirm before executing git commit",
    )
    show_token_count: bool = Field(
        default=False,
        description="Display token usage information",
    )


class Config(BaseModel):
    """Root configuration model.

    This is the main configuration class that combines all settings.
    Supports environment variable overrides with SGC_ prefix.

    Attributes:
        llm: LLM API configuration
        style: Commit style preferences
        behavior: Behavioral settings
    """

    model_config = ConfigDict(
        env_prefix="SGC_",
        env_nested_delimiter="__",
    )

    llm: LLMConfig = Field(default_factory=LLMConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)

    def is_configured(self) -> bool:
        """Check if the configuration is complete.

        Returns:
            True if api_key is set, False otherwise
        """
        return bool(self.llm.api_key.get_secret_value())


# Default config file paths
GLOBAL_CONFIG_PATH = Path.home() / ".smart-git-commit.yaml"
PROJECT_CONFIG_NAME = ".smart-git-commit.yaml"
