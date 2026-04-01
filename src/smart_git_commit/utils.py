"""Shared utilities for Smart Git Commit.

This module contains common utilities used across the application,
including logging setup, exit code definitions, and helper functions.
"""

import logging
import sys
from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for the CLI application.

    These codes follow standard conventions and allow scripts to
    handle different error conditions appropriately.

    Attributes:
        SUCCESS: Command executed successfully (0)
        GENERAL_ERROR: General/unknown error (1)
        NOT_A_REPO: Not a git repository (2)
        NO_STAGED_CHANGES: No staged changes to commit (3)
        CONFIG_ERROR: Configuration error (4)
        LLM_ERROR: LLM API error (5)
        USER_CANCELLED: User cancelled operation (130)
    """

    SUCCESS = 0
    GENERAL_ERROR = 1
    NOT_A_REPO = 2
    NO_STAGED_CHANGES = 3
    CONFIG_ERROR = 4
    LLM_ERROR = 5
    USER_CANCELLED = 130


def setup_logging(
    verbose: bool = False,
    log_file: str | None = None,
) -> logging.Logger:
    """Configure logging for the application.

    Sets up console logging with appropriate formatting and level.
    Optionally also logs to a file.

    Args:
        verbose: If True, set logging level to DEBUG; otherwise INFO
        log_file: Optional path to log file for file logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("smart_git_commit")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Get the application logger.

    Returns:
        The configured logger instance
    """
    return logging.getLogger("smart_git_commit")
