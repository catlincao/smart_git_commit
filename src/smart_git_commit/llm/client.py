"""OpenAI LLM client for Smart Git Commit.

This module provides an OpenAI SDK-based implementation of the LLMProvider protocol.
"""

from typing import Optional

from openai import AsyncOpenAI, OpenAIError

from smart_git_commit.config.models import LLMConfig
from smart_git_commit.exceptions import LLMError
from smart_git_commit.llm.provider import LLMProvider
from smart_git_commit.utils import get_logger

logger = get_logger()


class OpenAIProvider:
    """OpenAI API provider implementation.

    This class implements the LLMProvider protocol using the OpenAI SDK.
    It supports any OpenAI-compatible API endpoint.

    Attributes:
        config: LLM configuration settings
        client: AsyncOpenAI client instance
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize the OpenAI provider.

        Args:
            config: LLM configuration with API settings
        """
        self.config = config
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create the OpenAI client.

        Returns:
            Configured AsyncOpenAI client
        """
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key.get_secret_value(),
                timeout=self.config.timeout_seconds,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        context: Optional[dict] = None,
    ) -> str:
        """Generate a response using OpenAI API.

        Args:
            prompt: The prompt to send
            context: Optional context information

        Returns:
            Generated response text

        Raises:
            LLMError: If API call fails
        """
        client = self._get_client()

        messages = [{"role": "user", "content": prompt}]

        # Add system message if context provided
        if context and "system" in context:
            messages.insert(0, {"role": "system", "content": context["system"]})

        try:
            response = await client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=500,  # Reasonable limit for commit messages
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMError("LLM returned empty response")

            return content.strip()

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMError(
                f"LLM API error: {e}",
                exit_code=5,
                suggestion="Check your API key and network connection",
            ) from e

    def validate_config(self) -> bool:
        """Check if configuration is valid.

        Returns:
            True if API key is set
        """
        return bool(self.config.api_key.get_secret_value())

    def get_model_name(self) -> str:
        """Get the configured model name.

        Returns:
            Model identifier
        """
        return self.config.model

    async def test_connection(self) -> bool:
        """Test the API connection.

        Returns:
            True if connection successful
        """
        try:
            client = self._get_client()
            # Make a simple request to test connection
            await client.models.list()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Type alias for protocol compliance
LLMProvider.register(OpenAIProvider)


def create_provider(config: LLMConfig) -> LLMProvider:
    """Factory function to create an LLM provider.

    Args:
        config: LLM configuration

    Returns:
        Configured LLM provider
    """
    return OpenAIProvider(config)
