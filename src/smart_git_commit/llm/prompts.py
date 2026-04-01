"""Prompt templates for Smart Git Commit.

This module provides prompt generation for LLM-based commit message generation.
"""

from dataclasses import dataclass
from typing import Optional

from smart_git_commit.analyzer.style import CommitStyle, CommitType
from smart_git_commit.utils import get_logger

logger = get_logger()


@dataclass
class PromptContext:
    """Context information for prompt generation.

    Attributes:
        diff_summary: Summary of the git diff
        files_changed: List of files that were changed
        total_additions: Total lines added
        total_deletions: Total lines deleted
        project_style: Detected project commit style
        was_truncated: Whether the diff was truncated
    """

    diff_summary: str
    files_changed: list[str]
    total_additions: int
    total_deletions: int
    project_style: CommitStyle
    was_truncated: bool = False

    def to_dict(self) -> dict:
        """Convert context to dictionary format."""
        return {
            "diff_summary": self.diff_summary,
            "files_changed": self.files_changed,
            "total_additions": self.total_additions,
            "total_deletions": self.total_deletions,
            "project_style": {
                "uses_semantic_commits": self.project_style.uses_semantic_commits,
                "common_types": [t.value for t in self.project_style.common_types],
                "common_scopes": self.project_style.common_scopes,
            },
            "was_truncated": self.was_truncated,
        }


class PromptBuilder:
    """Builds prompts for LLM commit message generation."""

    @staticmethod
    def build_system_message(style: CommitStyle) -> str:
        """Build the system message for the LLM.

        Args:
            style: The detected project commit style

        Returns:
            System message string
        """
        lines = [
            "You are a commit message generator. Your task is to analyze git diffs and generate clear, concise commit messages.",
            "",
            "Guidelines:",
            "- Write in the imperative mood (e.g., 'add feature' not 'added feature')",
            "- Keep the subject line under 72 characters",
            "- Be specific but concise",
            "- Focus on what changed and why",
        ]

        if style.uses_semantic_commits:
            lines.extend([
                "",
                "This project uses Semantic Commits format:",
                "<type>(<scope>): <subject>",
                "",
                "Common types:",
            ])
            for commit_type in style.suggested_types[:5]:
                lines.append(f"  - {commit_type.value}: {PromptBuilder._get_type_description(commit_type)}")

            if style.common_scopes:
                lines.extend([
                    "",
                    f"Common scopes: {', '.join(style.common_scopes[:5])}",
                ])

        return "\n".join(lines)

    @staticmethod
    def _get_type_description(commit_type: CommitType) -> str:
        """Get description for a commit type."""
        descriptions = {
            CommitType.FEAT: "A new feature",
            CommitType.FIX: "A bug fix",
            CommitType.DOCS: "Documentation only changes",
            CommitType.STYLE: "Changes that do not affect code meaning (formatting, etc.)",
            CommitType.REFACTOR: "Code change that neither fixes a bug nor adds a feature",
            CommitType.TEST: "Adding or correcting tests",
            CommitType.CHORE: "Changes to build process or auxiliary tools",
            CommitType.BUILD: "Changes affecting build system or dependencies",
            CommitType.CI: "Changes to CI configuration",
            CommitType.PERF: "Performance improvements",
        }
        return descriptions.get(commit_type, "Other changes")

    @staticmethod
    def build_user_message(context: PromptContext) -> str:
        """Build the user message with diff information.

        Args:
            context: The prompt context

        Returns:
            User message string
        """
        lines = [
            "Generate a commit message for the following changes:",
            "",
            f"Files changed: {len(context.files_changed)}",
            f"Additions: {context.total_additions}",
            f"Deletions: {context.total_deletions}",
        ]

        if context.files_changed:
            lines.extend([
                "",
                "Changed files:",
            ])
            for file in context.files_changed[:20]:  # Limit to 20 files
                lines.append(f"  - {file}")
            if len(context.files_changed) > 20:
                lines.append(f"  ... and {len(context.files_changed) - 20} more files")

        if context.was_truncated:
            lines.extend([
                "",
                "Note: The diff was truncated due to size. Focus on the file names and types of changes.",
            ])

        lines.extend([
            "",
            "Git Diff:",
            "```",
            context.diff_summary,
            "```",
            "",
            "Generate a commit message following the format specified above.",
        ])

        return "\n".join(lines)

    @staticmethod
    def build_prompt(context: PromptContext) -> tuple[str, dict]:
        """Build complete prompt with system and user messages.

        Args:
            context: The prompt context

        Returns:
            Tuple of (user_prompt, context_dict)
        """
        system_message = PromptBuilder.build_system_message(context.project_style)
        user_message = PromptBuilder.build_user_message(context)

        context_dict = {
            "system": system_message,
        }

        return user_message, context_dict


def create_prompt(
    diff: str,
    style: CommitStyle,
    files_changed: list[str],
    total_additions: int,
    total_deletions: int,
    was_truncated: bool = False,
) -> tuple[str, dict]:
    """Convenience function to create a prompt.

    Args:
        diff: The git diff content
        style: The detected project style
        files_changed: List of changed files
        total_additions: Total lines added
        total_deletions: Total lines deleted
        was_truncated: Whether diff was truncated

    Returns:
        Tuple of (user_prompt, context_dict)
    """
    context = PromptContext(
        diff_summary=diff,
        files_changed=files_changed,
        total_additions=total_additions,
        total_deletions=total_deletions,
        project_style=style,
        was_truncated=was_truncated,
    )

    builder = PromptBuilder()
    return builder.build_prompt(context)
