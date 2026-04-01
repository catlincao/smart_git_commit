"""Configuration module for Smart Git Commit.

This module provides configuration management including models,
loading/saving, and the interactive configuration wizard.
"""

from smart_git_commit.config.manager import ConfigManager, load_config
from smart_git_commit.config.models import (
    GLOBAL_CONFIG_PATH,
    PROJECT_CONFIG_NAME,
    BehaviorConfig,
    Config,
    LLMConfig,
    StyleConfig,
)

# Delay import of wizard to avoid circular imports
# Use: from smart_git_commit.config.wizard import ConfigurationWizard

__all__ = [
    "Config",
    "LLMConfig",
    "StyleConfig",
    "BehaviorConfig",
    "ConfigManager",
    "load_config",
    "GLOBAL_CONFIG_PATH",
    "PROJECT_CONFIG_NAME",
]
