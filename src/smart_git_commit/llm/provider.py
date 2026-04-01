"""LLM provider interface for Smart Git Commit.

This module defines the protocol/interface for LLM providers,
allowing for easy extension to different LLM backends.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM provider implementations.

    This protocol defines the interface that all LLM providers must implement.
    It allows for easy swapping of different LLM backends while maintaining
    a consistent API.

    Example:
        ```python
        class OpenAIProvider:
            def __init__(self, config: LLMConfig):
                self.config = config

            async def generate(self, prompt: str, context: dict) -> str:
                # Implementation
                return response

            def validate_config(self) -> bool:
                return bool(self.config.api_key)
        ```
    """

    async def generate(self, prompt: str, context: dict | None = None) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM
            context: Optional context dictionary with additional information

        Returns:
            The generated response string

        Raises:
            LLMError: If the generation fails
        """
        ...

    def validate_config(self) -> bool:
        """Validate that the provider configuration is valid.

        Returns:
            True if configuration is valid, False otherwise
        """
        ...

    def get_model_name(self) -> str:
        """Get the name of the model being used.

        Returns:
            The model name/identifier
        """
        ...
