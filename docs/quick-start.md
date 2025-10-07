# Quick Start

Get started with faker-news in minutes! This guide assumes you've already [installed](getting-started.md) the package and [configured your API key](setup.md).

## Using as a Faker Provider

The primary way to use faker-news is as a Faker provider:

```python
from faker import Faker
from faker_news import NewsProvider

# Create Faker instance and add provider
fake = Faker()
fake.add_provider(NewsProvider(fake))

# Generate a headline
headline = fake.news_headline()
print(headline)
# Output: "Tech Giant Announces Revolutionary AI Breakthrough"

# Generate an intro for that headline
intro = fake.news_intro(headline=headline)
print(intro)
# Output: "In a surprising move today, the company unveiled..."

# Generate a full article
article = fake.news_article(headline=headline, words=500)
print(article)
```

## Using the CLI

Prefer command-line tools? Use the faker-news CLI:

```bash
# Generate a headline
faker-news headline

# Generate an intro (with auto-generated headline)
faker-news intro

# Generate a full article
faker-news article

# Generate a longer article
faker-news article --words 800

# Generate content for a specific headline
faker-news intro --headline "Breaking: New Discovery Announced"
faker-news article --headline "Breaking: New Discovery Announced"

# Always generate fresh content (skip cache)
faker-news headline --new
faker-news article --new --words 500
```

## Understanding Consumption

By default, items behave differently in the library vs CLI:

**Library (Python)**: Items are marked as "used" after fetching

```python
# These mark items as used
headline1 = fake.news_headline()
headline2 = fake.news_headline()  # Different headline

# Fetch without marking as used
headline3 = fake.news_headline(consume=False)
headline4 = fake.news_headline(consume=False)  # Could be same as headline3
```

**CLI**: Items are NOT marked as used (for easier testing)

```bash
# These don't mark as used - you can repeat the command
faker-news headline
faker-news headline  # Might show the same headline

# Mark as used with --consume flag
faker-news headline --consume
faker-news headline --consume  # Different headline
```

## Preloading Content

For better performance, preload headlines in bulk:

```python
# Preload 100 headlines
fake.news_preload_headlines(100)

# Now fetching is instant (no API calls)
headlines = [fake.news_headline() for _ in range(50)]
```

Or via CLI:

```bash
# Preload 50 headlines
faker-news preload --n 50

# Preload with full content (intros + articles)
faker-news preload --n 50 --with-intros --with-articles

# Smart populate: ensure 50 unused headlines exist with full content
# (reuses existing, generates new only if needed)
faker-news preload --n 50 --populate
```

## Checking Cache Status

See what's in your cache:

```python
stats = fake.news_stats()
print(stats)
# {
#   'total': 100,
#   'with_intro': 50,
#   'with_article': 30,
#   'unused_headlines': 75,
#   'unused_intros': 40,
#   'unused_articles': 25
# }
```

Or via CLI:

```bash
faker-news stats
```

## Complete Example

Here's a complete example generating a full news article:

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# Preload for performance
fake.news_preload_headlines(50)

# Generate a complete article
headline = fake.news_headline()
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline, words=600)

# Print formatted output
print("=" * 70)
print(headline)
print("=" * 70)
print()
print(intro)
print()
print(article)
print()
print("=" * 70)
```

## Next Steps

- [Library Usage](library-usage.md) - Detailed guide on using the Python API
- [CLI Reference](cli-reference.md) - Complete CLI command reference
- [Cache Management](cache-management.md) - Advanced cache management techniques
- [Configuration](configuration.md) - Customize batch sizes, models, and more
