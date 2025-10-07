# Cache Management

faker-news uses a SQLite database to cache generated content. This guide covers advanced cache management strategies.

## Understanding the Cache

### Cache Structure

The cache stores three types of content:

- **Headlines**: Short news headlines
- **Intros**: Article introductions (linked to headlines)
- **Articles**: Full article bodies (linked to headlines)

Each item tracks three usage flags:

- `used_headline`: Whether the headline has been consumed
- `used_intro`: Whether the intro has been consumed
- `used_article`: Whether the article has been consumed

### Cache Location

Default cache locations by platform:

| Platform | Location |
|----------|----------|
| Linux | `~/.cache/faker-news/cache.sqlite3` |
| macOS | `~/Library/Caches/faker-news/cache.sqlite3` |
| Windows | `%LOCALAPPDATA%\faker-news\cache\cache.sqlite3` |

## Viewing Cache Statistics

### Using Python

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

stats = fake.news_stats()
print(stats)
# {
#   'total': 150,
#   'with_intro': 75,
#   'with_article': 50,
#   'unused_headlines': 100,
#   'unused_intros': 60,
#   'unused_articles': 40
# }
```

### Using CLI

```bash
faker-news stats
```

### Understanding the Statistics

| Stat | Description |
|------|-------------|
| `total` | Total number of items (headlines) in cache |
| `with_intro` | Number of headlines that have intros |
| `with_article` | Number of headlines that have articles |
| `unused_headlines` | Headlines not marked as used |
| `unused_intros` | Intros not marked as used |
| `unused_articles` | Articles not marked as used |

## Consumption Strategies

### Default: Single-Use

By default, items are marked as "used" after fetching (in Python):

```python
# Each fetch marks item as used
headline1 = fake.news_headline()  # Marks as used
headline2 = fake.news_headline()  # Different headline
```

!!! note "CLI Difference"
    CLI commands do NOT mark items as used by default. Use `--consume` flag to mark as used.

### Strategy 1: Non-Consuming Fetches

Fetch items without marking as used (useful for testing):

```python
# View content without depleting pool
headline = fake.news_headline(consume=False)
article = fake.news_article(consume=False)

# Same item might be fetched multiple times
```

### Strategy 2: Allow Used Items

Fetch from the entire pool (both used and unused):

```python
# Fetch from any item
headline = fake.news_headline(allow_used=True)

# Combine: fetch from any pool without consuming
headline = fake.news_headline(allow_used=True, consume=False)
```

### Strategy 3: Reset and Reuse

Mark all items as unused:

```python
# Mark everything as unused
fake.news_reset("reuse")

# Now all items are available again
headline = fake.news_headline()  # Can fetch any item
```

Or via CLI:

```bash
faker-news reset --mode reuse
```

## Preloading Strategies

### Basic Preload

Generate headlines only:

```python
# Generate 100 headlines
fake.news_preload_headlines(100)

# Fetching is now instant (no API calls)
headlines = [fake.news_headline() for _ in range(50)]
```

### Full Content Preload

Generate complete articles (less efficient):

```bash
# Generate 50 new items with full content
faker-news preload --n 50 --with-intros --with-articles
```

!!! warning "Not Recommended for Large Batches"
    This generates N new items even if you have unused items. Use populate mode instead.

### Smart Populate (Recommended)

Ensure N unused items exist with full content:

```bash
# Ensure 50 unused articles exist
faker-news preload --n 50 --populate
```

This is more efficient because it:

1. **Prioritizes** unused headlines missing intros/articles
2. **Reuses** existing complete unused headlines
3. **Generates** new headlines only if needed
4. **Minimizes** API calls by using what's already there

**Example:**

```python
# Current cache: 30 unused headlines, 10 with full content

# Smart populate to ensure 50 with full content
fake.news_populate_headlines(50)

# Result:
# - 10 items already complete (reused)
# - 20 items get intros/articles generated
# - 20 new headlines generated with full content
# Total API calls: 20 intros + 20 articles + 20 headlines = 60
# vs. 150 if we generated 50 from scratch
```

## Resetting the Cache

### Reuse Content

Mark all items as unused (keep content):

```python
fake.news_reset("reuse")
```

```bash
faker-news reset --mode reuse
```

**When to use:**

- You've consumed all content but want to reuse it
- Testing scenarios where you need repeatable data
- Cycling through content multiple times

### Clear Content

Delete all cached items:

```python
fake.news_reset("clear")
```

```bash
faker-news reset --mode clear
```

**When to use:**

- Starting fresh with new content
- Cache has stale/unwanted content
- Freeing up disk space

## Advanced Techniques

### Maintain a Ready-to-Use Pool

Keep a pool of N complete articles ready:

```python
from faker import Faker
from faker_news import NewsProvider

def ensure_article_pool(size=50):
    """Ensure at least 'size' unused articles exist."""
    fake = Faker()
    fake.add_provider(NewsProvider(fake))

    stats = fake.news_stats()
    current = stats['unused_articles']

    if current < size:
        needed = size - current
        print(f"Generating {needed} articles...")

        # Use populate mode
        # (This is conceptual - not in current API)
        # For now, use preload with populate flag via CLI

ensure_article_pool(100)
```

### Separate Caches for Different Use Cases

Use different databases for different purposes:

```python
from faker import Faker
from faker_news import NewsProvider

# Production cache
prod_provider = NewsProvider(fake, db_path="/var/cache/faker-news.sqlite3")

# Test cache
test_provider = NewsProvider(fake, db_path="/tmp/test-news.sqlite3")

# Development cache (default location)
dev_provider = NewsProvider(fake)
```

### Batch Processing

Process content in batches efficiently:

```python
from faker import Faker
from faker_news import NewsProvider

def generate_batch(count=100):
    """Generate a batch of complete articles."""
    fake = Faker()
    fake.add_provider(NewsProvider(fake))

    # Preload headlines
    fake.news_preload_headlines(count)

    articles = []
    for i in range(count):
        headline = fake.news_headline()
        intro = fake.news_intro(headline=headline)
        article = fake.news_article(headline=headline, words=500)

        articles.append({
            'headline': headline,
            'intro': intro,
            'article': article
        })

        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{count}...")

    return articles

# Generate 100 complete articles
articles = generate_batch(100)
```

### Monitoring Cache Growth

Track how the cache grows over time:

```python
import time
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# Initial state
print("Initial:", fake.news_stats())

# Generate content
for i in range(50):
    fake.news_headline()
    if i % 10 == 0:
        stats = fake.news_stats()
        print(f"After {i} fetches:", stats)
        time.sleep(0.1)
```

## Custom Database Path

### Python

```python
from faker import Faker
from faker_news import NewsProvider

# Custom location
provider = NewsProvider(fake, db_path="/custom/path/cache.sqlite3")
fake.add_provider(provider)
```

### CLI

```bash
# Use custom database for all operations
faker-news preload --n 50 --db /custom/path/cache.sqlite3
faker-news headline --db /custom/path/cache.sqlite3
faker-news stats --db /custom/path/cache.sqlite3
```

### Environment Variable

Set a default custom path (not currently implemented, but could be):

```bash
export FAKER_NEWS_DB="/custom/path/cache.sqlite3"
faker-news headline  # Uses custom path
```

## Cache Maintenance

### Checking Cache Size

```bash
# Linux/macOS
du -h ~/.cache/faker-news/cache.sqlite3

# Windows
dir %LOCALAPPDATA%\faker-news\cache\cache.sqlite3
```

### Backing Up Cache

```bash
# Linux/macOS
cp ~/.cache/faker-news/cache.sqlite3 ~/backup-cache.sqlite3

# Restore
cp ~/backup-cache.sqlite3 ~/.cache/faker-news/cache.sqlite3
```

### Vacuuming Database

After many deletions, vacuum the database to reclaim space:

```python
import sqlite3
from pathlib import Path
from platformdirs import user_cache_dir

cache_dir = Path(user_cache_dir("faker-news"))
db_path = cache_dir / "cache.sqlite3"

conn = sqlite3.connect(db_path)
conn.execute("VACUUM")
conn.close()
```

## Best Practices

1. **Preload before batch operations** - Preload headlines before generating many articles
2. **Use populate mode** - More efficient than generating from scratch
3. **Monitor your pool** - Check stats regularly to ensure enough unused items
4. **Reset periodically** - Use `reuse` mode to cycle through content
5. **Separate environments** - Use different databases for prod/dev/test
6. **Backup important caches** - If you've generated a lot of content

## Next Steps

- [Configuration](configuration.md) - Customize batch sizes and thresholds
- [API Reference](api-reference.md) - Complete API documentation
