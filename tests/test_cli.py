"""Tests for CLI commands."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from faker_news.cli import main


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_provider():
    """Mock Faker instance and provider methods."""
    with patch("faker_news.cli.Faker") as mock_faker:
        mock_instance = MagicMock()
        mock_faker.return_value = mock_instance

        # Mock provider methods
        mock_instance.news_headline.return_value = "Test Headline"
        mock_instance.news_intro.return_value = "Test Intro"
        mock_instance.news_article.return_value = "Test Article"
        mock_instance.news_stats.return_value = {
            "total": 10,
            "with_intro": 5,
            "with_article": 3,
            "unused_headlines": 7,
            "unused_intros": 3,
            "unused_articles": 2,
        }

        yield mock_faker


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "LLM-backed Faker News generator" in result.output


def test_headline_command(runner, temp_db, mock_provider):
    """Test headline command."""
    result = runner.invoke(main, ["headline", "--db", temp_db])
    assert result.exit_code == 0


def test_headline_with_consume(runner, temp_db, mock_provider):
    """Test headline command with --consume flag."""
    result = runner.invoke(main, ["headline", "--consume", "--db", temp_db])
    assert result.exit_code == 0


def test_headline_with_allow_used(runner, temp_db, mock_provider):
    """Test headline command with --allow-used flag."""
    result = runner.invoke(main, ["headline", "--allow-used", "--db", temp_db])
    assert result.exit_code == 0


def test_intro_command(runner, temp_db, mock_provider):
    """Test intro command."""
    result = runner.invoke(main, ["intro", "--db", temp_db])
    assert result.exit_code == 0


def test_intro_with_headline(runner, temp_db, mock_provider):
    """Test intro command with specific headline."""
    result = runner.invoke(main, ["intro", "--headline", "Test", "--db", temp_db])
    assert result.exit_code == 0


def test_article_command(runner, temp_db, mock_provider):
    """Test article command."""
    result = runner.invoke(main, ["article", "--db", temp_db])
    assert result.exit_code == 0


def test_article_with_words(runner, temp_db, mock_provider):
    """Test article command with --words option."""
    result = runner.invoke(main, ["article", "--words", "800", "--db", temp_db])
    assert result.exit_code == 0


def test_article_with_headline(runner, temp_db, mock_provider):
    """Test article command with specific headline."""
    result = runner.invoke(main, ["article", "--headline", "Test", "--db", temp_db])
    assert result.exit_code == 0


def test_preload_command(runner, temp_db, mock_provider):
    """Test preload command."""
    result = runner.invoke(main, ["preload", "--n", "10", "--db", temp_db])
    assert result.exit_code == 0
    assert "Preloaded" in result.output


def test_stats_command(runner, temp_db, mock_provider):
    """Test stats command."""
    result = runner.invoke(main, ["stats", "--db", temp_db])
    assert result.exit_code == 0
    # Should output JSON
    assert "{" in result.output


def test_reset_reuse(runner, temp_db, mock_provider):
    """Test reset command with reuse mode."""
    result = runner.invoke(main, ["reset", "--mode", "reuse", "--db", temp_db])
    assert result.exit_code == 0
    assert "reuse" in result.output.lower()


def test_reset_clear(runner, temp_db, mock_provider):
    """Test reset command with clear mode."""
    result = runner.invoke(main, ["reset", "--mode", "clear", "--db", temp_db])
    assert result.exit_code == 0
    assert "clear" in result.output.lower()


def test_setup_command_with_existing_key(runner):
    """Test setup command when API key exists."""
    with patch("faker_news.setup.keyring") as mock_keyring, patch("faker_news.setup.os") as mock_os:
        mock_os.getenv.return_value = "test-key"
        mock_keyring.get_password.return_value = None

        # Provide "n" to skip the test prompt
        result = runner.invoke(main, ["setup"], input="n\n")
        assert result.exit_code == 0
        assert "found" in result.output.lower()


def test_setup_command_interactive(runner):
    """Test setup command with interactive key input."""
    with patch("faker_news.setup.keyring") as mock_keyring, patch("faker_news.setup.os") as mock_os:
        mock_os.getenv.return_value = None
        mock_keyring.get_password.return_value = None

        # Simulate user choosing to load example data (option 2), then declining test
        result = runner.invoke(main, ["setup"], input="2\nn\n")
        assert result.exit_code == 0
        assert "example" in result.output.lower()


def test_custom_db_path(runner, temp_db, mock_provider):
    """Test that custom database path is respected."""
    custom_db = temp_db.replace(".sqlite3", "_custom.sqlite3")

    try:
        result = runner.invoke(main, ["headline", "--db", custom_db])
        assert result.exit_code == 0

        # Verify custom db was created
        assert Path(custom_db).exists()
    finally:
        Path(custom_db).unlink(missing_ok=True)


def test_command_error_handling(runner, temp_db):
    """Test that errors are handled gracefully."""
    # Try to use without API key and mock the error
    with patch("faker_news.cli.Faker") as mock_faker:
        mock_faker.return_value.news_headline.side_effect = RuntimeError("Test error")

        result = runner.invoke(main, ["headline", "--db", temp_db])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_headline_with_new_flag(runner, mock_provider):
    """Test headline command with --new flag."""
    result = runner.invoke(main, ["headline", "--new"])
    assert result.exit_code == 0
    assert "Test Headline" in result.output


def test_intro_with_new_flag(runner, mock_provider):
    """Test intro command with --new flag."""
    result = runner.invoke(main, ["intro", "--new"])
    assert result.exit_code == 0
    assert "Test Intro" in result.output


def test_article_with_new_flag(runner, mock_provider):
    """Test article command with --new flag."""
    result = runner.invoke(main, ["article", "--new"])
    assert result.exit_code == 0
    assert "Test Article" in result.output
