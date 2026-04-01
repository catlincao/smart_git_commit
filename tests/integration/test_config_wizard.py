"""Integration tests for the configuration wizard flow."""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from smart_git_commit.config import Config
from smart_git_commit.config.manager import ConfigManager
from smart_git_commit.config.models import LLMConfig, StyleConfig
from smart_git_commit.config.wizard import ConfigurationWizard, run_wizard


class TestConfigurationWizard:
    """Integration tests for ConfigurationWizard."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def console(self) -> Console:
        """Create a Rich Console for testing."""
        return Console()

    def test_wizard_initialization(self) -> None:
        """Test wizard initializes with default or provided manager."""
        wizard = ConfigurationWizard()

        assert isinstance(wizard.manager, ConfigManager)
        assert isinstance(wizard.config, Config)

    def test_wizard_with_existing_config(self) -> None:
        """Test wizard loads existing configuration."""
        existing_config = Config(
            llm=LLMConfig(
                base_url="https://custom.api.com",
                model="gpt-4",
                api_key="sk-existing-key",
            ),
            style=StyleConfig(
                use_semantic_commits=False,
                language="de_DE",
            ),
        )
        manager = ConfigManager()
        manager.config = existing_config

        wizard = ConfigurationWizard(manager)

        assert wizard.config.llm.base_url == "https://custom.api.com"
        assert wizard.config.llm.model == "gpt-4"
        assert wizard.config.style.use_semantic_commits is False

    def test_config_manager_save_and_load(self, temp_dir: Path) -> None:
        """Test saving and loading configuration."""
        config = Config(
            llm=LLMConfig(
                base_url="https://api.openai.com/v1",
                model="gpt-4o-mini",
                api_key="sk-test-key-123",
            ),
            style=StyleConfig(
                use_semantic_commits=True,
                language="en_US",
            ),
        )

        manager = ConfigManager()
        manager.config = config

        # Save to temp path
        save_path = temp_dir / ".smart-git-commit.yaml"
        manager.save(path=save_path)

        # Verify file was created
        assert save_path.exists()

        # Load into new manager
        new_manager = ConfigManager()
        new_manager._load_from_file(save_path)

        assert new_manager.config.llm.base_url == "https://api.openai.com/v1"
        assert new_manager.config.llm.model == "gpt-4o-mini"
        assert new_manager.config.style.use_semantic_commits is True
        assert new_manager.config.style.language == "en_US"

    def test_config_loading_respects_defaults(self) -> None:
        """Test that Config model has correct defaults."""
        # Test defaults directly without file loading (which may have user overrides)
        config = Config()

        assert config.llm.base_url == "https://api.openai.com/v1"
        assert config.llm.model == "gpt-4o-mini"
        assert config.style.language == "en_US"
        assert config.style.use_semantic_commits is True

    def test_is_configured_check(self) -> None:
        """Test is_configured method for detection."""
        # Not configured without API key
        config_without_key = Config()
        assert config_without_key.is_configured() is False

        # Configured with API key
        config_with_key = Config(llm=LLMConfig(api_key="sk-test"))
        assert config_with_key.is_configured() is True

    def test_global_config_path_resolution(self) -> None:
        """Test that global config path is correctly resolved."""
        from smart_git_commit.config.models import GLOBAL_CONFIG_PATH

        assert GLOBAL_CONFIG_PATH.name == ".smart-git-commit.yaml"
        assert GLOBAL_CONFIG_PATH.parent == Path.home()

    @patch("smart_git_commit.config.wizard.OpenAIProvider")
    def test_wizard_connection_test_success(
        self, mock_provider_class: MagicMock, temp_dir: Path
    ) -> None:
        """Test wizard connection test with valid credentials."""
        # Setup mock
        mock_provider = MagicMock()
        mock_provider.validate_config.return_value = True
        mock_provider_class.return_value = mock_provider

        config = Config(
            llm=LLMConfig(
                api_key="sk-valid-key",
            ),
        )
        manager = ConfigManager()
        manager.config = config

        wizard = ConfigurationWizard(manager)

        # Test connection
        result = wizard._test_connection()

        assert result is True
        mock_provider.validate_config.assert_called_once()

    @patch("smart_git_commit.config.wizard.OpenAIProvider")
    def test_wizard_connection_test_failure(
        self, mock_provider_class: MagicMock, temp_dir: Path
    ) -> None:
        """Test wizard connection test with invalid credentials."""
        # Setup mock to raise exception
        mock_provider = MagicMock()
        mock_provider.validate_config.side_effect = Exception("Invalid API key")
        mock_provider_class.return_value = mock_provider

        config = Config(
            llM=LLMConfig(
                api_key="sk-invalid-key",
            ),
        )
        manager = ConfigManager()
        manager.config = config

        wizard = ConfigurationWizard(manager)

        # Test connection
        result = wizard._test_connection()

        assert result is False

    def test_wizard_connection_skips_without_api_key(self) -> None:
        """Test connection test is skipped when no API key."""
        config = Config()  # No API key
        manager = ConfigManager()
        manager.config = config

        wizard = ConfigurationWizard(manager)

        result = wizard._test_connection()

        assert result is False


class TestRunWizard:
    """Tests for the run_wizard convenience function."""

    @patch("smart_git_commit.config.wizard.ConfigurationWizard.run")
    def test_run_wizard_calls_wizard_run(
        self, mock_run: MagicMock
    ) -> None:
        """Test run_wizard calls ConfigurationWizard.run."""
        mock_run.return_value = Config()

        result = run_wizard()

        mock_run.assert_called_once()
        assert isinstance(result, Config)


class TestConfigPersistence:
    """Tests for configuration file persistence."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_yaml_serialization(self, temp_dir: Path) -> None:
        """Test configuration is correctly serialized to YAML."""
        import yaml

        config = Config(
            llm=LLMConfig(
                base_url="https://api.openai.com/v1",
                model="gpt-4o-mini",
                api_key="sk-test-key",
            ),
        )

        manager = ConfigManager()
        manager.config = config

        save_path = temp_dir / "config.yaml"
        manager.save(path=save_path)

        # Read and parse YAML
        with open(save_path) as f:
            data = yaml.safe_load(f)

        assert data["llm"]["base_url"] == "https://api.openai.com/v1"
        assert data["llm"]["model"] == "gpt-4o-mini"
        # API key should be masked with env var reference
        assert "OPENAI_API_KEY" in data["llm"]["api_key"]

    def test_env_var_substitution(self, temp_dir: Path) -> None:
        """Test environment variable substitution in config."""
        os.environ["TEST_API_KEY"] = "sk-test-from-env"

        config = Config(
            llm=LLMConfig(
                api_key="${TEST_API_KEY}",
            ),
        )

        manager = ConfigManager()
        manager.config = config

        # Get raw dict with SecretStr converted to string
        raw_data = {
            "llm": {
                "base_url": config.llm.base_url,
                "api_key": config.llm.api_key.get_secret_value(),
            }
        }

        # Process env vars
        data = manager._substitute_env_vars(raw_data)

        assert data["llm"]["api_key"] == "sk-test-from-env"

        # Cleanup
        del os.environ["TEST_API_KEY"]

    def test_env_var_substitution_with_default(
        self, temp_dir: Path
    ) -> None:
        """Test env var substitution with default value."""
        # Ensure var is not set
        if "NONEXISTENT_VAR" in os.environ:
            del os.environ["NONEXISTENT_VAR"]

        # Create data dict manually to avoid SecretStr issues
        raw_data = {
            "llm": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "${NONEXISTENT_VAR:-default-key}",
            }
        }

        manager = ConfigManager()

        # Process env vars
        data = manager._substitute_env_vars(raw_data)

        assert data["llm"]["api_key"] == "default-key"
