"""Tests for LLM client."""
import os
from unittest.mock import MagicMock, patch

import pytest

from faker_news.client import LLMClient, LLMClientConfig


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch("faker_news.client.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_keyring():
    """Mock keyring."""
    with patch("faker_news.client.keyring") as mock:
        mock.get_password.return_value = None
        yield mock


def test_config_from_env_openai(mock_keyring):
    """Test config auto-detects OpenAI from environment."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        config = LLMClientConfig()
        assert config.api_key == "test-key"
        assert config.model_headlines == "gpt-4o-mini"
        assert config.model_writing == "gpt-4o-mini"


def test_config_from_env_dashscope(mock_keyring):
    """Test config auto-detects DashScope from environment."""
    with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-key"}, clear=True):
        config = LLMClientConfig()
        assert config.api_key == "test-key"
        assert "dashscope" in config.base_url.lower()
        # Should auto-select Qwen models
        assert config.model_headlines == "qwen-flash"
        assert config.model_writing == "qwen-flash"


def test_config_from_keyring():
    """Test config loads from keyring."""
    with patch("faker_news.client.keyring") as mock_keyring, patch.dict(os.environ, {}, clear=True):
        mock_keyring.get_password.side_effect = lambda service, username: (
            "keyring-key" if username == "openai" else None
        )

        config = LLMClientConfig()
        assert config.api_key == "keyring-key"
        mock_keyring.get_password.assert_called()


def test_config_priority_keyring_over_env():
    """Test keyring takes priority over environment."""
    with patch("faker_news.client.keyring") as mock_keyring, patch.dict(
        os.environ, {"OPENAI_API_KEY": "env-key"}
    ):
        mock_keyring.get_password.side_effect = lambda service, username: (
            "keyring-key" if username == "openai" else None
        )

        config = LLMClientConfig()
        assert config.api_key == "keyring-key"


def test_config_explicit_key_takes_priority():
    """Test explicitly passed key takes priority."""
    with patch("faker_news.client.keyring") as mock_keyring, patch.dict(
        os.environ, {"OPENAI_API_KEY": "env-key"}
    ):
        mock_keyring.get_password.return_value = "keyring-key"

        config = LLMClientConfig(api_key="explicit-key")
        assert config.api_key == "explicit-key"


def test_client_initialization(mock_openai, mock_keyring):
    """Test LLMClient initializes with config."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = LLMClient()
        assert client.config.api_key == "test-key"
        mock_openai.assert_called_once()


def test_client_raises_without_api_key(mock_openai, mock_keyring):
    """Test client raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="API key is not set"):
            LLMClient()


def test_gen_json_success(mock_openai, mock_keyring):
    """Test successful JSON generation."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '["headline1", "headline2"]'
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        result = client.gen_json("gpt-4o-mini", "system", "user")

        assert result == ["headline1", "headline2"]


def test_gen_json_extracts_from_prose(mock_openai, mock_keyring):
    """Test JSON extraction from prose."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        # Mock response with prose around JSON
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Here are the results:\n["headline1", "headline2"]\nEnjoy!'
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        result = client.gen_json("gpt-4o-mini", "system", "user")

        assert result == ["headline1", "headline2"]


def test_gen_json_retries_on_error(mock_openai, mock_keyring):
    """Test that gen_json retries on failure."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        mock_instance = mock_openai.return_value
        # First call fails, second succeeds
        mock_response_bad = MagicMock()
        mock_response_bad.choices[0].message.content = "not json"

        mock_response_good = MagicMock()
        mock_response_good.choices[0].message.content = '["success"]'

        mock_instance.chat.completions.create.side_effect = [mock_response_bad, mock_response_good]

        client = LLMClient()
        result = client.gen_json("gpt-4o-mini", "system", "user", max_retries=1)

        assert result == ["success"]
        assert mock_instance.chat.completions.create.call_count == 2


def test_generate_headlines(mock_openai, mock_keyring):
    """Test headline generation."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '["Headline 1", "Headline 2"]'
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        headlines = client.generate_headlines(2)

        assert len(headlines) == 2
        assert "Headline 1" in headlines
        assert "Headline 2" in headlines


def test_generate_intros(mock_openai, mock_keyring):
    """Test intro generation."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            '[{"headline": "H1", "intro": "I1"}, {"headline": "H2", "intro": "I2"}]'
        )
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        intros = client.generate_intros(["H1", "H2"])

        assert len(intros) == 2
        assert ("H1", "I1") in intros
        assert ("H2", "I2") in intros


def test_generate_articles(mock_openai, mock_keyring):
    """Test article generation."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            '[{"headline": "H1", "article": "A1"}, {"headline": "H2", "article": "A2"}]'
        )
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        articles = client.generate_articles([("H1", "I1"), ("H2", "I2")], words=500)

        assert len(articles) == 2
        assert ("H1", "A1") in articles
        assert ("H2", "A2") in articles
