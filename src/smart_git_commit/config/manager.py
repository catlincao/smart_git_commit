"""Configuration manager for Smart Git Commit.

This module handles loading and saving configuration from multiple sources,
following a cascading priority: environment variables > project > global > defaults.
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from smart_git_commit.config.models import (
    PROJECT_CONFIG_NAME,
    Config,
    GLOBAL_CONFIG_PATH,
)
from smart_git_commit.exceptions import ConfigError
from smart_git_commit.utils import get_logger

logger = get_logger()


class ConfigManager:
    """Manages configuration loading and saving.

    Configuration is loaded from multiple sources in order of priority
    (highest to lowest):
    1. Environment variables (SGC_*)
    2. Project-level .smart-git-commit.yaml
    3. Global ~/.smart-git-commit.yaml
    4. Built-in defaults

    Attributes:
        config: The loaded configuration
        project_path: Path to the project config file (if found)
    """

    def __init__(self) -> None:
        """Initialize the config manager with default settings."""
        self.config = Config()
        self.project_path: Optional[Path] = None

    def load(self, project_dir: Optional[Path] = None) -> Config:
        """Load configuration from all sources.

        Loads configuration following the priority order:
        defaults -> global -> project -> environment variables

        Args:
            project_dir: Optional directory to look for project config

        Returns:
            The loaded configuration

        Raises:
            ConfigError: If configuration is invalid
        """
        # Start with defaults (already set in __init__)
        logger.debug("Starting with default configuration")

        # Load global config (lowest priority after defaults)
        if GLOBAL_CONFIG_PATH.exists():
            logger.debug(f"Loading global config from {GLOBAL_CONFIG_PATH}")
            self._load_from_file(GLOBAL_CONFIG_PATH)

        # Load project config
        if project_dir is None:
            project_dir = Path.cwd()
        project_config = project_dir / PROJECT_CONFIG_NAME

        if project_config.exists():
            logger.debug(f"Loading project config from {project_config}")
            self.project_path = project_config
            self._load_from_file(project_config)

        # Environment variables have highest priority
        self._load_from_env()

        return self.config

    def _load_from_file(self, path: Path) -> None:
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file

        Raises:
            ConfigError: If the file cannot be read or parsed
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data:
                # Process environment variable substitutions
                data = self._substitute_env_vars(data)

                # Update config with file values
                self.config = self.config.model_copy(update=data)

        except yaml.YAMLError as e:
            raise ConfigError(
                f"Failed to parse config file {path}: {e}",
                suggestion="Check YAML syntax in the configuration file",
            )
        except ValidationError as e:
            raise ConfigError(
                f"Invalid configuration in {path}: {e}",
                suggestion="Review configuration values against the schema",
            )
        except OSError as e:
            raise ConfigError(
                f"Cannot read config file {path}: {e}",
                suggestion="Check file permissions",
            )

    def _load_from_env(self) -> None:
        """Load configuration from environment variables.

        Environment variables with prefix SGC_ override config file values.
        Nested values use double underscore separator (e.g., SGC_LLM__MODEL).
        """
        env_vars = {}
        prefix = "SGC_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to nested dict
                config_key = key[len(prefix) :].lower()
                env_vars[config_key] = value

        if env_vars:
            logger.debug(f"Loading {len(env_vars)} environment variables")
            try:
                self.config = Config(**env_vars)
            except ValidationError as e:
                raise ConfigError(
                    f"Invalid environment variable configuration: {e}",
                    suggestion="Check SGC_* environment variables",
                )

    def _substitute_env_vars(self, data: dict) -> dict:
        """Substitute environment variables in config values.

        Supports ${VAR} and ${VAR:-default} syntax.

        Args:
            data: Configuration dictionary

        Returns:
            Dictionary with environment variables substituted
        """
        import re

        def substitute(value):
            if isinstance(value, str):
                # Match ${VAR} or ${VAR:-default}
                pattern = r"\$\{([^}]+)\}"

                def replace(match):
                    var_expr = match.group(1)
                    if ":-" in var_expr:
                        var_name, default = var_expr.split(":-", 1)
                        return os.environ.get(var_name, default)
                    else:
                        return os.environ.get(var_expr, match.group(0))

                return re.sub(pattern, replace, value)
            elif isinstance(value, dict):
                return {k: substitute(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute(item) for item in value]
            return value

        return substitute(data)

    def save(self, path: Optional[Path] = None, global_config: bool = False) -> None:
        """Save configuration to a file.

        Args:
            path: Optional custom path to save to
            global_config: If True, save to global config path

        Raises:
            ConfigError: If the file cannot be written
        """
        if path:
            save_path = path
        elif global_config:
            save_path = GLOBAL_CONFIG_PATH
        elif self.project_path:
            save_path = self.project_path
        else:
            save_path = GLOBAL_CONFIG_PATH

        # Prepare data for saving (exclude secrets from direct storage)
        data = self.config.model_dump(exclude_none=True)

        # Convert SecretStr to string for YAML
        if "llm" in data and "api_key" in data["llm"]:
            # Keep as environment variable reference if it was one
            api_key = self.config.llm.api_key.get_secret_value()
            if api_key.startswith("${"):
                data["llm"]["api_key"] = api_key
            else:
                # Mask the actual key in comments
                data["llm"]["api_key"] = "${OPENAI_API_KEY}"

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.debug(f"Configuration saved to {save_path}")
        except OSError as e:
            raise ConfigError(
                f"Cannot write config file {save_path}: {e}",
                suggestion="Check directory permissions",
            )

    def exists(self) -> bool:
        """Check if any configuration file exists.

        Returns:
            True if global or project config exists
        """
        return GLOBAL_CONFIG_PATH.exists() or (
            self.project_path is not None and self.project_path.exists()
        )


def load_config(project_dir: Optional[Path] = None) -> Config:
    """Convenience function to load configuration.

    Args:
        project_dir: Optional directory to look for project config

    Returns:
        The loaded configuration
    """
    manager = ConfigManager()
    return manager.load(project_dir)
