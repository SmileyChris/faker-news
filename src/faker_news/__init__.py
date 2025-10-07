"""Faker provider for generating fake news content using OpenAI-compatible LLM APIs."""

from .client import LLMClient, LLMClientConfig
from .provider import NewsProvider
from .store import NewsStore

__version__ = "0.1.0"

__all__ = [
    "NewsProvider",
    "LLMClient",
    "LLMClientConfig",
    "NewsStore",
]
