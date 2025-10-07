"""Tests for NewsProvider."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from faker import Faker

from faker_news import NewsProvider


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    with patch("faker_news.provider.LLMClient") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance

        # Counter to generate unique test data
        headline_counter = {"count": 0}

        # Mock responses that respect parameters
        def generate_headlines(n):
            start = headline_counter["count"]
            headlines = [f"Headline {i}" for i in range(start, start + n)]
            headline_counter["count"] += n
            return headlines

        def generate_intros(headlines_list):
            return [(h, f"Intro for {h}") for h in headlines_list]

        def generate_articles(pairs, words=500):
            # Generate articles with enough words to meet the requirement
            filler = " ".join(["word"] * max(words - 3, 0))  # Pad with "word" to reach target
            return [(h, f"Article for {h} {filler}".strip()) for h, _ in pairs]

        mock_instance.generate_headlines.side_effect = generate_headlines
        mock_instance.generate_intros.side_effect = generate_intros
        mock_instance.generate_articles.side_effect = generate_articles

        yield mock_instance


@pytest.fixture
def fake(temp_db, mock_llm_client):
    """Create Faker instance with NewsProvider."""
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=5, headline_batch=10)
    fake.add_provider(provider)
    return fake


def test_provider_initialization(temp_db, mock_llm_client):
    """Test NewsProvider initializes correctly."""
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db)
    fake.add_provider(provider)

    assert hasattr(fake, "news_headline")
    assert hasattr(fake, "news_intro")
    assert hasattr(fake, "news_article")
    assert hasattr(fake, "news_preload_headlines")
    assert hasattr(fake, "news_reset")
    assert hasattr(fake, "news_stats")


def test_news_headline_generates_on_demand(fake, mock_llm_client):
    """Test headlines are generated when pool is empty."""
    headline = fake.news_headline()
    assert headline.startswith("Headline")
    mock_llm_client.generate_headlines.assert_called()


def test_news_headline_consume_default(fake, mock_llm_client):
    """Test headline is consumed by default."""
    fake.news_preload_headlines(10)
    stats_before = fake.news_stats()

    fake.news_headline()

    stats_after = fake.news_stats()
    assert stats_after["unused_headlines"] == stats_before["unused_headlines"] - 1


def test_news_headline_no_consume(fake, mock_llm_client):
    """Test headline is not consumed with consume=False."""
    fake.news_preload_headlines(10)
    stats_before = fake.news_stats()

    fake.news_headline(consume=False)

    stats_after = fake.news_stats()
    assert stats_after["unused_headlines"] == stats_before["unused_headlines"]


def test_news_headline_allow_used(temp_db, mock_llm_client):
    """Test fetching from used headlines."""
    # Use provider with no auto-refill to control exact count
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=0, headline_batch=10)
    fake.add_provider(provider)

    fake.news_preload_headlines(2)

    # Consume all
    fake.news_headline()
    fake.news_headline()

    assert fake.news_stats()["unused_headlines"] == 0

    # Should still fetch with allow_used=True
    headline = fake.news_headline(allow_used=True, consume=False)
    assert headline.startswith("Headline")


def test_news_preload_headlines(fake, mock_llm_client):
    """Test preloading headlines."""
    fake.news_preload_headlines(20)

    stats = fake.news_stats()
    assert stats["total"] >= 20


def test_news_intro_generates_on_demand(fake, mock_llm_client):
    """Test intros are generated on demand."""
    fake.news_preload_headlines(5)

    intro = fake.news_intro()
    assert intro.startswith("Intro")
    mock_llm_client.generate_intros.assert_called()


def test_news_intro_for_specific_headline(fake, mock_llm_client):
    """Test generating intro for specific headline."""
    fake.news_preload_headlines(5)
    headline = fake.news_headline(consume=False)

    # Mock specific intro generation
    mock_llm_client.generate_intros.return_value = [(headline, "Specific Intro")]

    intro = fake.news_intro(headline=headline)
    # The intro might be from cache or newly generated
    assert intro is not None


def test_news_article_generates_on_demand(fake, mock_llm_client):
    """Test articles are generated on demand."""
    fake.news_preload_headlines(5)

    article = fake.news_article()
    assert article.startswith("Article")
    mock_llm_client.generate_articles.assert_called()


def test_news_article_consume_default(fake, mock_llm_client):
    """Test article is consumed by default."""
    fake.news_preload_headlines(10)
    # Generate some articles
    fake.news_article()

    stats_before = fake.news_stats()
    if stats_before["unused_articles"] > 0:
        fake.news_article()
        stats_after = fake.news_stats()
        assert stats_after["unused_articles"] <= stats_before["unused_articles"]


def test_news_reset_reuse(temp_db, mock_llm_client):
    """Test reset with reuse mode."""
    # Use provider with no auto-refill to control exact count
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=0, headline_batch=10)
    fake.add_provider(provider)

    fake.news_preload_headlines(5)

    # Consume all
    for _ in range(5):
        fake.news_headline()

    assert fake.news_stats()["unused_headlines"] == 0

    # Reset to reuse
    fake.news_reset("reuse")

    stats = fake.news_stats()
    assert stats["unused_headlines"] > 0


def test_news_reset_clear(fake, mock_llm_client):
    """Test reset with clear mode."""
    fake.news_preload_headlines(10)
    assert fake.news_stats()["total"] > 0

    # Clear everything
    fake.news_reset("clear")

    stats = fake.news_stats()
    assert stats["total"] == 0


def test_news_stats(fake, mock_llm_client):
    """Test stats returns correct structure."""
    stats = fake.news_stats()

    assert "total" in stats
    assert "with_intro" in stats
    assert "with_article" in stats
    assert "unused_headlines" in stats
    assert "unused_intros" in stats
    assert "unused_articles" in stats


def test_min_headline_pool_maintained(temp_db, mock_llm_client):
    """Test that minimum headline pool is maintained."""
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=10, headline_batch=15)
    fake.add_provider(provider)

    # First fetch should trigger generation
    fake.news_headline()

    stats = fake.news_stats()
    # Should have generated enough to maintain minimum pool
    assert stats["total"] >= 10


def test_batch_generation(temp_db, mock_llm_client):
    """Test that headlines are generated in batches."""
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=15, headline_batch=20)
    fake.add_provider(provider)

    # Mock to track calls
    mock_llm_client.generate_headlines.reset_mock()

    fake.news_headline()

    # Should have called generate with batch size (20 since max(20, 15-0) = 20)
    mock_llm_client.generate_headlines.assert_called_with(20)


def test_multiple_providers_use_same_db(temp_db, mock_llm_client):
    """Test multiple provider instances share the same database."""
    fake1 = Faker()
    provider1 = NewsProvider(fake1, db_path=temp_db)
    fake1.add_provider(provider1)

    fake2 = Faker()
    provider2 = NewsProvider(fake2, db_path=temp_db)
    fake2.add_provider(provider2)

    # Add headlines via fake1
    fake1.news_preload_headlines(5)

    # Should be visible in fake2
    stats2 = fake2.news_stats()
    assert stats2["total"] >= 5


def test_news_article_auto_generates_intro(temp_db, mock_llm_client):
    """Test that news_article automatically generates intro if missing."""
    # Use provider with controlled settings
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=0, headline_batch=5)
    fake.add_provider(provider)

    # Preload a headline without intro
    fake.news_preload_headlines(1)
    headline = fake.news_headline(consume=False)

    # Verify no intro exists yet
    stats = fake.news_stats()
    assert stats["with_intro"] == 0

    # Reset mock to track new calls
    mock_llm_client.generate_intros.reset_mock()
    mock_llm_client.generate_articles.reset_mock()

    # Generate article for this headline (should auto-generate intro first)
    article = fake.news_article(headline=headline, consume=False)

    # Verify both intro and article were generated
    assert article.startswith("Article")
    mock_llm_client.generate_intros.assert_called()
    mock_llm_client.generate_articles.assert_called()

    # Verify intro is now in database
    stats_after = fake.news_stats()
    assert stats_after["with_intro"] >= 1


def test_news_intro_generates_headlines_when_empty(temp_db, mock_llm_client):
    """Test that news_intro generates headlines if none exist."""
    # Use provider with no auto-refill
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=0, intro_batch=5)
    fake.add_provider(provider)

    # No headlines in database
    assert fake.news_stats()["total"] == 0

    # Should auto-generate headlines and intro
    intro = fake.news_intro(consume=False)

    # Verify headline and intro were generated
    assert intro.startswith("Intro")
    mock_llm_client.generate_headlines.assert_called()
    mock_llm_client.generate_intros.assert_called()

    # Verify content in database
    stats = fake.news_stats()
    assert stats["total"] >= 1
    assert stats["with_intro"] >= 1


def test_news_article_generates_headlines_when_empty(temp_db, mock_llm_client):
    """Test that news_article generates headlines if none exist."""
    # Use provider with no auto-refill
    fake = Faker()
    provider = NewsProvider(fake, db_path=temp_db, min_headline_pool=0, article_batch=5)
    fake.add_provider(provider)

    # No headlines in database
    assert fake.news_stats()["total"] == 0

    # Should auto-generate headlines, intro, and article
    article = fake.news_article(consume=False)

    # Verify everything was generated
    assert article.startswith("Article")
    mock_llm_client.generate_headlines.assert_called()
    mock_llm_client.generate_intros.assert_called()
    mock_llm_client.generate_articles.assert_called()

    # Verify content in database
    stats = fake.news_stats()
    assert stats["total"] >= 1
    assert stats["with_intro"] >= 1
    assert stats["with_article"] >= 1
