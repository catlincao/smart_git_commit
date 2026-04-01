"""Custom exceptions for Smart Git Commit.

This module defines the exception hierarchy used throughout the application
to provide meaningful error messages and proper error handling.
"""

from typing import Optional


class SmartGitCommitError(Exception):
    """Base exception for all Smart Git Commit errors.

    Attributes:
        message: Human-readable error message
        exit_code: Exit code to use when exiting the program
        suggestion: Optional suggestion for how to resolve the error
    """

    def __init__(
        self,
        message: str,
        exit_code: int = 1,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            exit_code: Exit code to use when exiting (default: 1)
            suggestion: Optional suggestion for resolution
        """
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.suggestion = suggestion

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.suggestion:
            return f"{self.message}\n\nSuggestion: {self.suggestion}"
        return self.message


class GitError(SmartGitCommitError):
    """Exception raised for git-related errors.

    This includes errors like:
    - Not a git repository
    - No staged changes
    - Git command failures
    """

    def __init__(
        self,
        message: str,
        exit_code: int = 2,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the git error.

        Args:
            message: Human-readable error message
            exit_code: Exit code (default: 2 for git errors)
            suggestion: Optional suggestion for resolution
        """
        super().__init__(message, exit_code, suggestion)


class ConfigError(SmartGitCommitError):
    """Exception raised for configuration errors.

    This includes errors like:
    - Missing configuration file
    - Invalid configuration values
    - Missing required settings (API key, etc.)
    """

    def __init__(
        self,
        message: str,
        exit_code: int = 4,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the config error.

        Args:
            message: Human-readable error message
            exit_code: Exit code (default: 4 for config errors)
            suggestion: Optional suggestion for resolution
        """
        super().__init__(message, exit_code, suggestion)


class LLMError(SmartGitCommitError):
    """Exception raised for LLM API errors.

    This includes errors like:
    - API authentication failures
    - Rate limiting
    - Timeout errors
    - Invalid responses
    """

    def __init__(
        self,
        message: str,
        exit_code: int = 5,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the LLM error.

        Args:
            message: Human-readable error message
            exit_code: Exit code (default: 5 for LLM errors)
            suggestion: Optional suggestion for resolution
        """
        super().__init__(message, exit_code, suggestion)


class ValidationError(SmartGitCommitError):
    """Exception raised for validation errors.

    This includes errors like:
    - Invalid commit message format
    - Invalid configuration values
    """

    def __init__(
        self,
        message: str,
        exit_code: int = 1,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            message: Human-readable error message
            exit_code: Exit code (default: 1)
            suggestion: Optional suggestion for resolution
        """
        super().__init__(message, exit_code, suggestion)
