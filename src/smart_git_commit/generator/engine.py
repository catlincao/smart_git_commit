"""Commit message generation engine for Smart Git Commit.

This module provides the main orchestration logic for generating commit messages
by combining git analysis, LLM generation, and project style detection.
"""

import re
from dataclasses import dataclass

from git import Repo

from smart_git_commit.analyzer.style import CommitStyle, CommitType, detect_style
from smart_git_commit.analyzer.tokenizer import truncate_diff
from smart_git_commit.config.models import Config
from smart_git_commit.exceptions import LLMError, ValidationError
from smart_git_commit.git.diff import DiffExtractor
from smart_git_commit.llm.client import OpenAIProvider
from smart_git_commit.llm.prompts import create_prompt
from smart_git_commit.utils import get_logger

logger = get_logger()


@dataclass
class GeneratedMessage:
    """Represents a generated commit message.

    Attributes:
        commit_type: The type of commit (feat, fix, etc.)
        scope: Optional scope of the commit
        subject: The subject line
        body: Optional body/description
        breaking_change: Optional breaking change notice
        raw_message: The raw generated message
    """

    commit_type: CommitType | None = None
    scope: str | None = None
    subject: str = ""
    body: str | None = None
    breaking_change: str | None = None
    raw_message: str = ""

    def to_full_message(self) -> str:
        """Convert to full git commit message format.

        Returns:
            Formatted commit message string
        """
        lines = []

        # Build subject line
        subject = ""
        if self.commit_type:
            subject = self.commit_type.value
            if self.scope:
                subject += f"({self.scope})"
            subject += ": "
        subject += self.subject
        lines.append(subject)

        # Add body if present
        if self.body:
            lines.append("")
            lines.append(self.body)

        # Add breaking change if present
        if self.breaking_change:
            lines.append("")
            lines.append(f"BREAKING CHANGE: {self.breaking_change}")

        return "\n".join(lines)

    def to_one_line(self) -> str:
        """Return a one-line representation.

        Returns:
            Short commit message
        """
        prefix = ""
        if self.commit_type:
            prefix = self.commit_type.value
            if self.scope:
                prefix += f"({self.scope})"
            prefix += ": "
        return f"{prefix}{self.subject}"


class MessageGenerator:
    """Main engine for generating commit messages.

    This class orchestrates the entire generation process:
    1. Extract git diff
    2. Detect project style
    3. Build prompt
    4. Call LLM
    5. Parse response

    Attributes:
        repo: The GitPython Repo instance
        config: Application configuration
        provider: LLM provider instance
    """

    def __init__(self, repo: Repo, config: Config) -> None:
        """Initialize the message generator.

        Args:
            repo: The GitPython Repo instance
            config: Application configuration
        """
        self.repo = repo
        self.config = config
        self.provider = OpenAIProvider(config.llm)

    async def generate(self) -> GeneratedMessage:
        """Generate a commit message for staged changes.

        Returns:
            GeneratedMessage with parsed commit information

        Raises:
            LLMError: If LLM generation fails
            ValidationError: If response parsing fails
        """
        logger.debug("Starting commit message generation")

        # Step 1: Extract diff
        diff_extractor = DiffExtractor(self.repo, max_size=100_000)
        diff = diff_extractor.get_staged_diff()

        # Step 2: Get file changes summary
        summary = diff_extractor.get_summary()

        # Step 3: Detect project style
        style = detect_style(self.repo, self.config.style)
        logger.debug(f"Detected style: semantic={style.uses_semantic_commits}")

        # Step 4: Truncate diff if needed
        truncated_diff, was_truncated = truncate_diff(
            diff,
            max_tokens=self.config.style.max_diff_tokens,
            model=self.config.llm.model,
        )

        if was_truncated:
            logger.info("Diff was truncated to fit token limit")

        # Step 5: Build prompt
        prompt, context = create_prompt(
            diff=truncated_diff,
            style=style,
            files_changed=summary["file_list"],
            total_additions=summary["additions"],
            total_deletions=summary["deletions"],
            was_truncated=was_truncated,
        )

        # Step 6: Generate with LLM
        try:
            raw_response = await self.provider.generate(prompt, context)
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(
                f"Failed to generate commit message: {e}",
                suggestion="Check your API configuration and try again",
            ) from e

        # Step 7: Parse response
        message = self._parse_response(raw_response, style)
        message.raw_message = raw_response

        logger.debug(f"Generated message: {message.to_one_line()}")

        return message

    def _parse_response(self, response: str, style: CommitStyle) -> GeneratedMessage:
        """Parse LLM response into structured message.

        Args:
            response: Raw LLM response
            style: Detected project style

        Returns:
            Parsed GeneratedMessage

        Raises:
            ValidationError: If parsing fails
        """
        lines = response.strip().split("\n")
        subject_line = lines[0] if lines else ""

        message = GeneratedMessage()

        # Try to parse semantic commit format
        # Pattern: type(scope): subject
        semantic_pattern = r"^(\w+)(?:\(([^)]+)\))?!?:\s*(.+)$"
        match = re.match(semantic_pattern, subject_line)

        if match:
            type_str, scope, subject = match.groups()

            # Try to parse commit type
            try:
                message.commit_type = CommitType(type_str.lower())
            except ValueError:
                # Unknown type, treat as plain subject
                message.subject = subject_line
            else:
                message.scope = scope
                message.subject = subject
        else:
            # Plain subject
            message.subject = subject_line

        # Parse body (everything after subject line)
        if len(lines) > 1:
            body_lines = []
            in_breaking_change = False

            for line in lines[1:]:
                # Check for breaking change marker
                if line.startswith("BREAKING CHANGE:"):
                    message.breaking_change = line[16:].strip()
                    in_breaking_change = True
                elif in_breaking_change:
                    message.breaking_change += "\n" + line
                elif line.strip():
                    body_lines.append(line)

            if body_lines:
                message.body = "\n".join(body_lines).strip()

        # Validate subject
        if not message.subject:
            raise ValidationError(
                "Generated message has empty subject",
                suggestion="Try regenerating the message",
            )

        # Enforce semantic commits if project uses them
        if style.uses_semantic_commits and not message.commit_type:
            logger.warning("Project uses semantic commits but generated message doesn't match")

        return message


async def generate_commit_message(repo: Repo, config: Config) -> GeneratedMessage:
    """Convenience function to generate a commit message.

    Args:
        repo: The GitPython Repo instance
        config: Application configuration

    Returns:
        Generated commit message
    """
    generator = MessageGenerator(repo, config)
    return await generator.generate()
