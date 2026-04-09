"""CLI interface for Smart Git Commit.

This module provides the Typer-based command-line interface for the tool,
including the main command, configuration wizard, and help text.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from pydantic import SecretStr
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from smart_git_commit import __version__
from smart_git_commit.config import Config, ConfigManager
from smart_git_commit.config.models import GLOBAL_CONFIG_PATH
from smart_git_commit.exceptions import ConfigError, GitError, LLMError, SmartGitCommitError
from smart_git_commit.generator import generate_commit_message
from smart_git_commit.git import GitRepository, RepositoryStatus
from smart_git_commit.llm.client import OpenAIProvider
from smart_git_commit.utils import ExitCode, get_logger, setup_logging

if TYPE_CHECKING:
    from smart_git_commit.generator.engine import GeneratedMessage

app = typer.Typer(
    name="sgc",
    help="AI-powered git commit message generator",
    no_args_is_help=False,
)
console = Console()
logger = get_logger()


def version_callback(value: bool) -> None:
    """Handle --version flag."""
    if value:
        console.print(f"smart-git-commit {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Smart Git Commit - AI-powered commit message generator."""
    pass


@app.command()
def generate(
    silence: bool = typer.Option(
        False,
        "--silence",
        "-s",
        help="Skip interactive prompts and commit directly",
    ),
    config_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--config-file",
        "-c",
        help="Path to custom configuration file",
    ),
    verbose: bool = typer.Option(  # noqa: B008
        False,
        "--verbose",
        help="Enable verbose logging",
    ),
) -> None:
    """Generate a commit message for staged changes."""
    setup_logging(verbose=verbose)

    try:
        asyncio.run(_generate_commit(silence, config_path))
    except SmartGitCommitError as e:
        _display_error(e)
        raise typer.Exit(code=e.exit_code) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(code=ExitCode.USER_CANCELLED) from None


async def _generate_commit(silence: bool, config_path: Path | None) -> None:
    """Main commit generation logic."""
    # Step 1: Load configuration (silence mode requires existing config)
    config = _load_configuration(config_path, silence=silence)

    # Step 2: Validate git repository
    repo = GitRepository()
    status = repo.validate()

    if status == RepositoryStatus.NOT_A_REPO:
        raise GitError(
            "Not a Git Repository",
            exit_code=ExitCode.NOT_A_REPO,
            suggestion=(
                "Initialize a repository with: git init\n"
                "Or navigate to an existing git repository"
            ),
        )
    elif status == RepositoryStatus.NO_COMMITS:
        raise GitError(
            "Repository Has No Commits",
            exit_code=ExitCode.NOT_A_REPO,
            suggestion="Create an initial commit manually before using this tool",
        )
    elif status == RepositoryStatus.NO_STAGED_CHANGES:
        raise GitError(
            "No Staged Changes",
            exit_code=ExitCode.NO_STAGED_CHANGES,
            suggestion="Stage files with: git add <files>\nCheck status with: git status",
        )

    # Step 3: Generate commit message
    with console.status("[bold green]Analyzing staged changes..."):
        pass  # Status will be updated below

    with console.status("[bold green]Generating commit message..."):
        try:
            from git import Repo

            git_repo = Repo()
            message = await generate_commit_message(git_repo, config)
        except GitError:
            raise
        except LLMError:
            raise
        except Exception as e:
            logger.exception("Unexpected error during commit generation")
            raise GitError(
                f"Unexpected error: {e}",
                suggestion="Try again or check git status",
            ) from e

    # Step 4: Display message (skip in silence mode)
    if not silence:
        _display_message(message.to_full_message())

    # Step 5: Handle silence mode or interactive mode
    if silence:
        # True silent mode: skip all prompts, commit directly
        # Only check auto_commit_silence setting
        if config.behavior.auto_commit_silence:
            console.print("[dim]Auto-committing in silence mode...[/dim]")
    else:
        # Interactive mode: allow editing
        if Confirm.ask("Edit message?", default=False):
            message = _edit_message(message)
            _display_message(message.to_full_message())

        if not Confirm.ask("Proceed with commit?", default=True):
            console.print("[yellow]Commit cancelled[/yellow]")
            return

    # Step 6: Execute commit
    try:
        repo.commit(message.to_full_message())
        console.print(f"[green]✓[/green] Committed: {message.to_one_line()}")
    except Exception as e:
        raise GitError(
            f"Failed to create commit: {e}",
            suggestion="Check git status and try again",
        ) from e


def _load_configuration(config_path: Path | None, silence: bool = False) -> Config:
    """Load configuration, running wizard if needed.

    Args:
        config_path: Optional custom config file path
        silence: If True, require existing config (don't run wizard)

    Returns:
        Loaded configuration

    Raises:
        ConfigError: If no config found in silence mode
    """
    manager = ConfigManager()

    if config_path:
        if not config_path.exists():
            raise ConfigError(
                f"Configuration file not found: {config_path}",
                suggestion="Check the file path or run without --config-file to use defaults",
            )
        manager._load_from_file(config_path)
        return manager.config

    # Try to load existing configuration
    try:
        config = manager.load()
        if config.is_configured():
            return config
    except ConfigError:
        pass

    # No valid configuration found
    if silence:
        raise ConfigError(
            "No configuration found",
            suggestion="Run 'sgc --config' to set up configuration first",
        )

    # Run wizard (interactive mode only)
    console.print("[yellow]No configuration found. Let's set up Smart Git Commit.[/yellow]\n")
    return _run_config_wizard(manager)


def _run_config_wizard(manager: ConfigManager) -> Config:
    """Run interactive configuration wizard."""
    console.print(Panel.fit("Smart Git Commit - Configuration", style="bold blue"))

    # LLM Configuration
    console.print("\n[bold]LLM Configuration[/bold]")

    base_url = Prompt.ask(
        "LLM Base URL",
        default="https://api.openai.com/v1",
    )

    model = Prompt.ask(
        "Model Name",
        default="gpt-4o-mini",
    )

    api_key = Prompt.ask(
        "API Key",
        password=True,
    )

    if not api_key:
        raise ConfigError(
            "API key is required",
            suggestion="Provide a valid API key for your LLM provider",
        )

    # Style Configuration
    console.print("\n[bold]Style Configuration[/bold]")

    use_semantic = Confirm.ask(
        "Use Semantic Commits?",
        default=True,
    )

    # Update configuration
    manager.config.llm.base_url = base_url
    manager.config.llm.model = model
    manager.config.llm.api_key = SecretStr(api_key)
    manager.config.style.use_semantic_commits = use_semantic

    # Test connection
    console.print("\n[bold]Testing connection...[/bold]", end=" ")
    try:
        provider = OpenAIProvider(manager.config.llm)
        # Simple test - just validate config
        if not provider.validate_config():
            raise ConfigError("Invalid API configuration")
        console.print("[green]✓[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/red]")
        if not Confirm.ask("Save configuration anyway?", default=False):
            raise typer.Exit() from None

    # Save configuration
    manager.save(global_config=True)
    console.print(f"\n[green]Configuration saved to {GLOBAL_CONFIG_PATH}[/green]")

    return manager.config


@app.command(name="config")
def config_command() -> None:
    """Run the configuration wizard."""
    manager = ConfigManager()

    # Load existing config if available
    try:
        manager.load()
        console.print("[blue]Current configuration loaded. Edit as needed.[/blue]\n")
    except ConfigError:
        console.print("[yellow]No existing configuration found. Creating new...[/yellow]\n")

    try:
        _run_config_wizard(manager)
        console.print("\n[green]Configuration updated successfully![/green]")
    except SmartGitCommitError as e:
        _display_error(e)
        raise typer.Exit(code=e.exit_code) from None


def _display_message(message: str) -> None:
    """Display the generated commit message in a panel."""
    console.print()
    console.print(
        Panel(
            message,
            title="Generated Commit Message",
            border_style="green",
        )
    )
    console.print()


def _edit_message(message) -> GeneratedMessage:
    """Open editor to edit the commit message."""
    # Get editor from environment
    editor = os.environ.get("EDITOR", "vim")

    # Create temp file with current message
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        f.write(message.to_full_message())
        temp_path = f.name

    try:
        # Open editor
        subprocess.run([editor, temp_path], check=True)

        # Read edited message
        with open(temp_path) as f:
            edited_text = f.read().strip()

        # Parse edited message
        lines = edited_text.split("\n")
        new_message = GeneratedMessage(subject=lines[0] if lines else "")

        if len(lines) > 1:
            new_message.body = "\n".join(lines[1:]).strip()

        return new_message
    except subprocess.CalledProcessError:
        console.print("[yellow]Editor closed without saving. Using original message.[/yellow]")
        return message
    except Exception as e:
        console.print(f"[red]Error editing message: {e}[/red]")
        return message
    finally:
        # Cleanup
        from contextlib import suppress

        with suppress(OSError):
            os.unlink(temp_path)


def _display_error(error: SmartGitCommitError) -> None:
    """Display an error message with Rich formatting."""
    error_text = Text()
    error_text.append(f"Error: {error.message}\n", style="bold red")

    if error.suggestion:
        error_text.append("\nSuggestions:\n", style="bold yellow")
        for line in error.suggestion.split("\n"):
            error_text.append(f"  • {line}\n", style="yellow")

    console.print()
    console.print(Panel(error_text, border_style="red"))
    console.print()


if __name__ == "__main__":
    app()
