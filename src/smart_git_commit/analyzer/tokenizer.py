"""Token counting and diff truncation for Smart Git Commit.

This module provides functionality for counting tokens using tiktoken
and truncating diffs to stay within token limits.
"""

from typing import Optional

from smart_git_commit.utils import get_logger

logger = get_logger()


class TokenCounter:
    """Counts tokens in text using tiktoken.

    This class provides token counting functionality for various
    text inputs to ensure they stay within LLM token limits.

    Attributes:
        encoding: The tiktoken encoding instance
        model: The model name for encoding selection
    """

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the token counter.

        Args:
            model: The model name to use for encoding (default: gpt-4o)
        """
        self.model = model
        self._encoding: Optional[object] = None

    def _get_encoding(self) -> Optional[object]:
        """Get or create the tiktoken encoding.

        Returns:
            The tiktoken encoding instance or None if tiktoken not available
        """
        if self._encoding is None:
            try:
                import tiktoken

                # Try to get encoding for the model
                try:
                    self._encoding = tiktoken.encoding_for_model(self.model)
                except KeyError:
                    # Fall back to cl100k_base (used by GPT-4, GPT-3.5-turbo)
                    self._encoding = tiktoken.get_encoding("cl100k_base")
            except ImportError:
                logger.warning("tiktoken not installed, using approximate token count")
                return None
        return self._encoding

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens in the text
        """
        encoding = self._get_encoding()
        if encoding is None:
            # Fallback: approximate 4 characters per token
            return len(text) // 4

        try:
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using approximation")
            return len(text) // 4

    def truncate(self, text: str, max_tokens: int, add_ellipsis: bool = True) -> str:
        """Truncate text to fit within token limit.

        Args:
            text: The text to truncate
            max_tokens: Maximum number of tokens allowed
            add_ellipsis: Whether to add ellipsis when truncated

        Returns:
            Truncated text
        """
        current_tokens = self.count(text)

        if current_tokens <= max_tokens:
            return text

        encoding = self._get_encoding()

        if encoding is None:
            # Fallback: truncate by characters
            chars = max_tokens * 4
            result = text[:chars]
        else:
            try:
                tokens = encoding.encode(text)
                truncated_tokens = tokens[:max_tokens]
                result = encoding.decode(truncated_tokens)
            except Exception as e:
                logger.warning(f"Token truncation failed: {e}, using char truncation")
                chars = max_tokens * 4
                result = text[:chars]

        if add_ellipsis:
            result += "\n\n... [diff truncated due to token limit]"

        return result


class DiffTruncator:
    """Truncates diffs while preserving important information.

    This class handles intelligent truncation of git diffs to ensure
    they fit within token limits while keeping the most relevant parts.

    Attributes:
        max_tokens: Maximum tokens allowed for the diff
        counter: TokenCounter instance
    """

    def __init__(self, max_tokens: int = 4000, model: str = "gpt-4o") -> None:
        """Initialize the diff truncator.

        Args:
            max_tokens: Maximum tokens allowed (default: 4000)
            model: Model name for token counting
        """
        self.max_tokens = max_tokens
        self.counter = TokenCounter(model)

    def truncate(self, diff: str) -> tuple[str, bool]:
        """Truncate diff if it exceeds token limit.

        Args:
            diff: The git diff to truncate

        Returns:
            Tuple of (truncated_diff, was_truncated)
        """
        token_count = self.counter.count(diff)

        if token_count <= self.max_tokens:
            return diff, False

        logger.info(f"Truncating diff from {token_count} to ~{self.max_tokens} tokens")

        # Strategy: Keep the file summary and truncate the actual diff content
        lines = diff.split("\n")
        result_lines = []
        current_tokens = 0
        header_buffer = []

        for line in lines:
            line_tokens = self.counter.count(line + "\n")

            # Always keep file headers
            if line.startswith("diff --git") or line.startswith("index "):
                header_buffer.append(line)
                continue

            # Keep mode lines
            if line.startswith(("--- ", "+++ ", "@@ ")):
                header_buffer.append(line)
                continue

            # Check if adding this line would exceed limit
            if current_tokens + line_tokens > self.max_tokens - 50:  # Reserve space for ellipsis
                break

            # Flush header buffer
            if header_buffer:
                for header_line in header_buffer:
                    result_lines.append(header_line)
                    current_tokens += self.counter.count(header_line + "\n")
                header_buffer = []

            result_lines.append(line)
            current_tokens += line_tokens

        result = "\n".join(result_lines)
        result += "\n\n... [diff truncated due to token limit]"

        return result, True


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Convenience function to count tokens.

    Args:
        text: Text to count tokens for
        model: Model name for encoding

    Returns:
        Number of tokens
    """
    counter = TokenCounter(model)
    return counter.count(text)


def truncate_diff(diff: str, max_tokens: int = 4000, model: str = "gpt-4o") -> tuple[str, bool]:
    """Convenience function to truncate a diff.

    Args:
        diff: Git diff to truncate
        max_tokens: Maximum tokens allowed
        model: Model name for token counting

    Returns:
        Tuple of (truncated_diff, was_truncated)
    """
    truncator = DiffTruncator(max_tokens, model)
    return truncator.truncate(diff)
