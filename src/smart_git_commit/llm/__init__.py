"""LLM module for Smart Git Commit.

This module provides LLM integration functionality including:
- Provider protocol for extensibility
- OpenAI SDK client implementation
- Prompt building and management
"""

from smart_git_commit.llm.client import OpenAIProvider, create_provider
from smart_git_commit.llm.prompts import PromptBuilder, PromptContext, create_prompt
from smart_git_commit.llm.provider import LLMProvider

__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "create_provider",
    "PromptContext",
    "PromptBuilder",
    "create_prompt",
]
