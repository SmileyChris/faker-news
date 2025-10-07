"""Tests for NewsStore."""
import tempfile
from pathlib import Path

import pytest

from faker_news.store import NewsStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def store(temp_db):
    """Create a NewsStore instance with temporary database."""
    return NewsStore(temp_db)


def test_store_initialization(store):
    """Test that store initializes correctly."""
    stats = store.stats()
    assert stats["total"] == 0
    assert stats["with_intro"] == 0
    assert stats["with_article"] == 0


def test_insert_headlines(store):
    """Test inserting headlines."""
    headlines = ["Headline 1", "Headline 2", "Headline 3"]
    store.insert_headlines(headlines)

    stats = store.stats()
    assert stats["total"] == 3
    assert stats["unused_headlines"] == 3


def test_fetch_headline_consume(store):
    """Test fetching headline with consume=True."""
    store.insert_headlines(["Test Headline"])

    headline = store.fetch_headline(consume=True)
    assert headline == "Test Headline"

    # Should be marked as used
    stats = store.stats()
    assert stats["unused_headlines"] == 0


def test_fetch_headline_no_consume(store):
    """Test fetching headline with consume=False."""
    store.insert_headlines(["Test Headline"])

    headline = store.fetch_headline(consume=False)
    assert headline == "Test Headline"

    # Should still be unused
    stats = store.stats()
    assert stats["unused_headlines"] == 1


def test_fetch_headline_allow_used(store):
    """Test fetching from used headlines with allow_used=True."""
    store.insert_headlines(["Test Headline"])

    # Consume it
    store.fetch_headline(consume=True)
    assert store.stats()["unused_headlines"] == 0

    # Should return None without allow_used
    headline = store.fetch_headline(consume=False, allow_used=False)
    assert headline is None

    # Should return headline with allow_used
    headline = store.fetch_headline(consume=False, allow_used=True)
    assert headline == "Test Headline"


def test_set_intros(store):
    """Test setting intros for headlines."""
    store.insert_headlines(["Headline 1", "Headline 2"])
    store.set_intros([("Headline 1", "Intro 1"), ("Headline 2", "Intro 2")])

    stats = store.stats()
    assert stats["with_intro"] == 2
    assert stats["unused_intros"] == 2


def test_fetch_intro(store):
    """Test fetching intros."""
    store.insert_headlines(["Headline 1"])
    store.set_intros([("Headline 1", "Intro 1")])

    headline, intro = store.fetch_intro(consume=True)
    assert headline == "Headline 1"
    assert intro == "Intro 1"

    stats = store.stats()
    assert stats["unused_intros"] == 0


def test_set_articles(store):
    """Test setting articles for headlines."""
    store.insert_headlines(["Headline 1"])
    store.set_articles([("Headline 1", "Article 1")])

    stats = store.stats()
    assert stats["with_article"] == 1
    assert stats["unused_articles"] == 1


def test_fetch_article(store):
    """Test fetching articles."""
    store.insert_headlines(["Headline 1"])
    store.set_articles([("Headline 1", "Article 1")])

    headline, article = store.fetch_article(consume=True)
    assert headline == "Headline 1"
    assert article == "Article 1"

    stats = store.stats()
    assert stats["unused_articles"] == 0


def test_reset_reuse(store):
    """Test reset with mode='reuse'."""
    store.insert_headlines(["Headline 1", "Headline 2"])

    # Consume both
    store.fetch_headline(consume=True)
    store.fetch_headline(consume=True)

    assert store.stats()["unused_headlines"] == 0

    # Reset to reuse
    store.reset("reuse")

    stats = store.stats()
    assert stats["total"] == 2
    assert stats["unused_headlines"] == 2


def test_reset_clear(store):
    """Test reset with mode='clear'."""
    store.insert_headlines(["Headline 1", "Headline 2"])
    assert store.stats()["total"] == 2

    # Clear everything
    store.reset("clear")

    stats = store.stats()
    assert stats["total"] == 0


def test_duplicate_headlines_ignored(store):
    """Test that duplicate headlines are ignored."""
    store.insert_headlines(["Headline 1", "Headline 1", "Headline 2"])

    stats = store.stats()
    assert stats["total"] == 2  # Only 2 unique headlines


def test_fetch_missing_intros(store):
    """Test fetching headlines that need intros."""
    store.insert_headlines(["H1", "H2", "H3"])
    store.set_intros([("H1", "I1")])

    missing = store.fetch_missing_intros(limit=10)
    assert len(missing) == 2
    assert "H2" in missing
    assert "H3" in missing


def test_fetch_headlines_needing_articles(store):
    """Test fetching headlines that need articles."""
    store.insert_headlines(["H1", "H2", "H3"])
    store.set_intros([("H1", "I1"), ("H2", "I2"), ("H3", "I3")])
    store.set_articles([("H1", "A1")])

    pairs = store.fetch_headlines_needing_articles(limit=10)
    assert len(pairs) == 2

    headlines_needing = [h for h, _ in pairs]
    assert "H2" in headlines_needing
    assert "H3" in headlines_needing


def test_mark_intro_used_for(store):
    """Test marking specific intro as used."""
    store.insert_headlines(["H1"])
    store.set_intros([("H1", "I1")])

    assert store.stats()["unused_intros"] == 1

    store.mark_intro_used_for("H1")

    assert store.stats()["unused_intros"] == 0


def test_mark_article_used_for(store):
    """Test marking specific article as used."""
    store.insert_headlines(["H1"])
    store.set_articles([("H1", "A1")])

    assert store.stats()["unused_articles"] == 1

    store.mark_article_used_for("H1")

    assert store.stats()["unused_articles"] == 0
