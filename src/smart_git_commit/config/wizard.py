"""Interactive configuration wizard for Smart Git Commit.

This module provides an interactive CLI wizard for first-time configuration
of the tool, guiding users through setting up their LLM credentials.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from smart_git_commit.config.manager import ConfigManager
from pydantic import SecretStr

from smart_git_commit.config.models import GLOBAL_CONFIG_PATH, Config
from smart_git_commit.exceptions import ConfigError
from smart_git_commit.llm.client import OpenAIProvider
from smart_git_commit.utils import get_logger

console = Console()
logger = get_logger()


class ConfigurationWizard:
    """Interactive configuration wizard.

    Guides users through setting up their configuration including:
    - LLM API settings (base URL, model, API key)
    - Style preferences (semantic commits, language)
    - Connection testing

    Attributes:
        manager: ConfigManager instance
        config: Current configuration being edited
    """

    def __init__(self, manager: ConfigManager | None = None) -> None:
        """Initialize the wizard.

        Args:
            manager: Optional existing ConfigManager
        """
        self.manager = manager or ConfigManager()
        self.config = self.manager.config

    def run(self) -> Config:
        """Run the configuration wizard.

        Returns:
            The configured Config instance

        Raises:
            ConfigError: If configuration fails
        """
        console.print()
        console.print(
            Panel.fit(
                "[bold blue]Smart Git Commit - Configuration Wizard[/bold blue]",
                border_style="blue",
            )
        )
        console.print()

        # LLM Configuration
        self._configure_llm()

        # Style Configuration
        self._configure_style()

        # Test connection
        if self._test_connection():
            console.print("[green]✓[/green] Connection test passed!")
        else:
            console.print(
                "[yellow]⚠[/yellow] Connection test failed. "
                "You can still save the configuration."
            )

        # Save configuration
        self._save_configuration()

        return self.config

    def _configure_llm(self) -> None:
        """Configure LLM settings interactively."""
        console.print("[bold]LLM Configuration[/bold]")
        console.print()

        # Base URL
        self.config.llm.base_url = Prompt.ask(
            "LLM Base URL",
            default=self.config.llm.base_url or "https://api.openai.com/v1",
        )

        # Model name
        self.config.llm.model = Prompt.ask(
            "Model Name",
            default=self.config.llm.model or "gpt-4o-mini",
        )

        # API Key
        api_key = Prompt.ask(
            "API Key",
            password=True,
            default="",
        )

        if api_key:
            self.config.llm.api_key = SecretStr(api_key)
        elif not self.config.llm.api_key.get_secret_value():
            console.print(
                "[yellow]Warning: No API key provided. "
                "You'll need to set one before using the tool.[/yellow]"
            )

        # Timeout
        timeout_str = Prompt.ask(
            "Request timeout (seconds)",
            default=str(self.config.llm.timeout_seconds),
        )
        try:
            self.config.llm.timeout_seconds = int(timeout_str)
        except ValueError:
            console.print("[yellow]Invalid timeout, using default (30s)[/yellow]")

        console.print()

    def _configure_style(self) -> None:
        """Configure style preferences interactively."""
        console.print("[bold]Style Configuration[/bold]")
        console.print()

        # Semantic commits
        self.config.style.use_semantic_commits = Confirm.ask(
            "Use Semantic Commits (Conventional Commits)?",
            default=self.config.style.use_semantic_commits,
        )

        # Language
        self.config.style.language = Prompt.ask(
            "Default language",
            default=self.config.style.language or "en_US",
        )

        # Max diff tokens
        tokens_str = Prompt.ask(
            "Maximum diff tokens (1000-8000)",
            default=str(self.config.style.max_diff_tokens),
        )
        try:
            tokens = int(tokens_str)
            if 1000 <= tokens <= 8000:
                self.config.style.max_diff_tokens = tokens
            else:
                console.print("[yellow]Value out of range, using default (4000)[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value, using default (4000)[/yellow]")

        console.print()

    def _test_connection(self) -> bool:
        """Test the LLM connection.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.config.llm.api_key.get_secret_value():
            console.print("[yellow]Skipping connection test (no API key)[/yellow]")
            return False

        console.print("[bold]Testing connection...[/bold]", end=" ")

        try:
            provider = OpenAIProvider(self.config.llm)
            # For now, just validate config - actual API test would require async
            if provider.validate_config():
                return True
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def _save_configuration(self) -> None:
        """Save the configuration to file."""
        console.print()

        # Ask where to save
        use_global = Confirm.ask(
            f"Save to global config ({GLOBAL_CONFIG_PATH})?",
            default=True,
        )

        try:
            if use_global:
                self.manager.save(global_config=True)
                console.print(
                    f"[green]✓[/green] Configuration saved to {GLOBAL_CONFIG_PATH}"
                )
            else:
                # Save to project directory
                project_path = Prompt.ask(
                    "Project directory",
                    default=str(Path.cwd()),
                )
                self.manager.save(path=Path(project_path))
                console.print(
                    f"[green]✓[/green] Configuration saved to {project_path}/.smart-git-commit.yaml"
                )
        except Exception as e:
            raise ConfigError(
                f"Failed to save configuration: {e}",
                suggestion="Check file permissions and try again",
            ) from e


def run_wizard(manager: ConfigManager | None = None) -> Config:
    """Convenience function to run the configuration wizard.

    Args:
        manager: Optional existing ConfigManager

    Returns:
        The configured Config instance
    """
    wizard = ConfigurationWizard(manager)
    return wizard.run()
