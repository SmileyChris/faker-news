# Library Usage

This guide covers using faker-news as a Python library with the Faker framework.

## Basic Setup

```python
from faker import Faker
from faker_news import NewsProvider

# Create Faker instance and add the provider
fake = Faker()
fake.add_provider(NewsProvider(fake))
```

## Generating Content

### Headlines

Generate standalone headlines:

```python
# Generate a random headline
headline = fake.news_headline()
print(headline)
# "Scientists Discover New Species in Deep Ocean"

# Generate multiple headlines
headlines = [fake.news_headline() for _ in range(5)]
```

### Introductions

Generate article introductions:

```python
# Generate intro for a specific headline
headline = "Tech Company Launches Revolutionary Product"
intro = fake.news_intro(headline=headline)
print(intro)
# "In a major announcement today, the company revealed..."

# Generate standalone intro (with auto-generated headline)
intro = fake.news_intro()
```

### Full Articles

Generate complete articles with markdown formatting:

```python
# Generate a ~500-word article
headline = "Climate Scientists Report Breakthrough Discovery"
article = fake.news_article(headline=headline, words=500)
print(article)

# Generate a longer article
long_article = fake.news_article(headline=headline, words=1000)

# Generate standalone article (with auto-generated headline)
article = fake.news_article()
```

## Consumption Modes

### Default Behavior (Consume)

By default, items are marked as "used" after fetching:

```python
# These mark items as used
headline1 = fake.news_headline()
headline2 = fake.news_headline()  # Different headline
headline3 = fake.news_headline()  # Different headline again

# Once all unused headlines are consumed, new ones are auto-generated
```

### Non-Consuming Mode

Fetch items without marking them as used:

```python
# Preview content without consuming
headline = fake.news_headline(consume=False)
intro = fake.news_intro(consume=False)
article = fake.news_article(consume=False)

# Useful for:
# - Testing/debugging
# - Previewing content before deciding to use it
# - Showing examples without depleting the pool
```

### Allow Used Items

Fetch from the entire pool (both used and unused):

```python
# Fetch from all items, not just unused
headline = fake.news_headline(allow_used=True)
article = fake.news_article(allow_used=True)

# Combine with consume=False for true random sampling
random_headline = fake.news_headline(allow_used=True, consume=False)
```

## Working with Related Content

Generate a complete article with matching headline, intro, and body:

```python
# Method 1: Generate piece by piece
headline = fake.news_headline()
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline, words=600)

print(f"{headline}\n\n{intro}\n\n{article}")

# Method 2: Generate all at once (more efficient)
headline = fake.news_headline()
# Batch generate intro and article
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline)
```

!!! tip "Performance Tip"
    When generating multiple complete articles, preload headlines first:

    ```python
    fake.news_preload_headlines(100)

    articles = []
    for _ in range(50):
        headline = fake.news_headline()
        intro = fake.news_intro(headline=headline)
        article = fake.news_article(headline=headline)
        articles.append((headline, intro, article))
    ```

## Preloading Content

For better performance, preload content in bulk:

```python
# Preload 100 headlines
fake.news_preload_headlines(100)

# Now fetching headlines is instant (no API calls)
headlines = [fake.news_headline() for _ in range(50)]

# Check what's in the cache
stats = fake.news_stats()
print(stats)
# {
#   'total': 100,
#   'with_intro': 0,
#   'with_article': 0,
#   'unused_headlines': 50,
#   'unused_intros': 0,
#   'unused_articles': 0
# }
```

## Custom Configuration

Customize the provider behavior:

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Configure LLM settings
llm_config = LLMClientConfig(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model_headlines="gpt-4o-mini",  # Fast model for headlines
    model_writing="gpt-4o"           # Better model for full articles
)

# Configure provider with custom settings
fake = Faker()
provider = NewsProvider(
    fake,
    llm_config=llm_config,
    db_path="/custom/path/cache.sqlite3",  # Custom cache location
    min_headline_pool=50,                   # Keep 50 unused headlines
    headline_batch=60,                      # Generate 60 at a time
    intro_batch=30,                         # Generate 30 intros at a time
    article_batch=15                        # Generate 15 articles at a time
)
fake.add_provider(provider)
```

## Error Handling

Handle errors gracefully:

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

try:
    headline = fake.news_headline()
    print(f"Generated: {headline}")
except Exception as e:
    print(f"Error generating content: {e}")
    # Possible errors:
    # - API key not configured
    # - Network connection issues
    # - LLM API errors
    # - Rate limiting
```

## Advanced Examples

### Generate Multiple Complete Articles

```python
def generate_news_articles(count=10):
    """Generate multiple complete news articles."""
    from faker import Faker
    from faker_news import NewsProvider

    fake = Faker()
    fake.add_provider(NewsProvider(fake))

    # Preload for performance
    fake.news_preload_headlines(count)

    articles = []
    for _ in range(count):
        headline = fake.news_headline()
        intro = fake.news_intro(headline=headline)
        article = fake.news_article(headline=headline, words=500)

        articles.append({
            'headline': headline,
            'intro': intro,
            'article': article
        })

    return articles

# Use it
articles = generate_news_articles(10)
for article in articles:
    print(article['headline'])
    print('-' * 70)
    print(article['intro'])
    print()
    print(article['article'])
    print('=' * 70)
    print()
```

### Populate Database for Testing

```python
from faker import Faker
from faker_news import NewsProvider

def populate_test_database():
    """Populate database with fake news for testing."""
    fake = Faker()
    fake.add_provider(NewsProvider(fake))

    # Generate 100 headlines
    print("Generating headlines...")
    fake.news_preload_headlines(100)

    # Generate intros and articles for 50 of them
    print("Generating articles...")
    for i in range(50):
        headline = fake.news_headline()
        fake.news_intro(headline=headline)
        fake.news_article(headline=headline, words=600)

        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1} complete articles...")

    # Show statistics
    stats = fake.news_stats()
    print(f"\nCache populated:")
    print(f"  Total items: {stats['total']}")
    print(f"  With intros: {stats['with_intro']}")
    print(f"  With articles: {stats['with_article']}")

# Run it
populate_test_database()
```

### Use with Custom Faker Providers

Combine with other Faker providers:

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# Generate a fake news article with fake author and date
article_data = {
    'headline': fake.news_headline(),
    'author': fake.name(),
    'date': fake.date_between(start_date='-30d', end_date='today'),
    'category': fake.random_element(['Politics', 'Technology', 'Science', 'Sports']),
    'intro': fake.news_intro(),
    'article': fake.news_article(words=500)
}

print(article_data)
```

## Next Steps

- [CLI Reference](cli-reference.md) - Use faker-news from the command line
- [Cache Management](cache-management.md) - Advanced cache management
- [API Reference](api-reference.md) - Complete API documentation
