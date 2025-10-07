# API Reference

Complete API reference for faker-news.

## NewsProvider

The main Faker provider for generating news content.

### Constructor

```python
NewsProvider(
    generator,
    db_path=None,
    min_headline_pool=30,
    headline_batch=40,
    intro_batch=20,
    article_batch=10,
    llm_config=None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `generator` | `Faker` | Required | Faker instance |
| `db_path` | `str | None` | Platform-specific | SQLite database file path |
| `min_headline_pool` | `int` | `30` | Minimum unused headlines before auto-refill |
| `headline_batch` | `int` | `40` | Headlines generated per batch |
| `intro_batch` | `int` | `20` | Intros generated per batch |
| `article_batch` | `int` | `10` | Articles generated per batch |
| `llm_config` | `LLMClientConfig | None` | `None` | LLM client configuration |

**Example:**

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
provider = NewsProvider(
    fake,
    db_path="/custom/cache.sqlite3",
    min_headline_pool=50,
    headline_batch=60
)
fake.add_provider(provider)
```

---

### news_headline()

Generate a fake news headline.

```python
news_headline(consume=True, allow_used=False) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `consume` | `bool` | `True` | Mark headline as used after fetching |
| `allow_used` | `bool` | `False` | Fetch from all items (used or unused) |

**Returns:** `str` - A fake news headline

**Example:**

```python
# Generate and mark as used
headline = fake.news_headline()

# Generate without consuming
headline = fake.news_headline(consume=False)

# Fetch from all items
headline = fake.news_headline(allow_used=True)
```

---

### news_intro()

Generate a fake news article introduction.

```python
news_intro(headline=None, consume=True, allow_used=False) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headline` | `str | None` | `None` | Specific headline to use (auto-generated if None) |
| `consume` | `bool` | `True` | Mark intro as used after fetching |
| `allow_used` | `bool` | `False` | Fetch from all items (used or unused) |

**Returns:** `str` - A fake news intro

**Example:**

```python
# Generate intro with auto-generated headline
intro = fake.news_intro()

# Generate intro for specific headline
intro = fake.news_intro(headline="Breaking: Major Discovery Announced")

# Generate without consuming
intro = fake.news_intro(consume=False)
```

---

### news_article()

Generate a complete fake news article with markdown formatting.

```python
news_article(headline=None, words=500, consume=True, allow_used=False) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headline` | `str | None` | `None` | Specific headline to use (auto-generated if None) |
| `words` | `int` | `500` | Target article length in words |
| `consume` | `bool` | `True` | Mark article as used after fetching |
| `allow_used` | `bool` | `False` | Fetch from all items (used or unused) |

**Returns:** `str` - A fake news article with markdown formatting

**Example:**

```python
# Generate ~500 word article
article = fake.news_article()

# Generate longer article
article = fake.news_article(words=1000)

# Generate for specific headline
article = fake.news_article(headline="Scientists Discover New Species")

# Generate without consuming
article = fake.news_article(consume=False)
```

---

### news_preload_headlines()

Preload headlines in bulk for better performance.

```python
news_preload_headlines(count) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | `int` | Required | Number of headlines to generate |

**Example:**

```python
# Preload 100 headlines
fake.news_preload_headlines(100)

# Now fetching is instant
headlines = [fake.news_headline() for _ in range(50)]
```

---

### news_stats()

Get cache statistics.

```python
news_stats() -> dict
```

**Returns:** `dict` with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `total` | `int` | Total number of items in cache |
| `with_intro` | `int` | Items that have intros |
| `with_article` | `int` | Items that have articles |
| `unused_headlines` | `int` | Unused headlines available |
| `unused_intros` | `int` | Unused intros available |
| `unused_articles` | `int` | Unused articles available |

**Example:**

```python
stats = fake.news_stats()
print(f"Total: {stats['total']}")
print(f"Unused headlines: {stats['unused_headlines']}")
```

---

### news_reset()

Reset usage flags or clear the cache.

```python
news_reset(mode) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `str` | Required | Reset mode: `"reuse"` or `"clear"` |

**Modes:**

- `"reuse"`: Mark all items as unused (keep content)
- `"clear"`: Delete all cached content

**Example:**

```python
# Mark all items as unused
fake.news_reset("reuse")

# Clear all cached content
fake.news_reset("clear")
```

---

## LLMClientConfig

Configuration for the LLM client.

### Constructor

```python
LLMClientConfig(
    api_key=None,
    base_url=None,
    model_headlines=None,
    model_writing=None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str | None` | Auto-detected | LLM API key |
| `base_url` | `str | None` | Auto-detected | API endpoint URL |
| `model_headlines` | `str | None` | Provider-specific | Model for headline generation |
| `model_writing` | `str | None` | Provider-specific | Model for intro/article generation |

**Auto-Detection:**

If parameters are not specified, they are auto-detected from:

1. System keyring (for `api_key`)
2. Environment variables (`OPENAI_API_KEY`, `DASHSCOPE_API_KEY`, etc.)
3. Default values based on detected provider

**Example:**

```python
from faker_news import LLMClientConfig

# Explicit configuration
llm_config = LLMClientConfig(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
    model_headlines="gpt-4o-mini",
    model_writing="gpt-4o"
)

# Auto-detect from environment
llm_config = LLMClientConfig()
```

---

## LLMClient

Low-level client for LLM API calls (not typically used directly).

### Constructor

```python
LLMClient(config=None)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `LLMClientConfig | None` | Auto-detected | LLM client configuration |

---

### generate_headlines()

Generate multiple headlines in one batch.

```python
generate_headlines(count) -> list[str]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | `int` | Required | Number of headlines to generate |

**Returns:** `list[str]` - List of generated headlines

**Example:**

```python
from faker_news import LLMClient

client = LLMClient()
headlines = client.generate_headlines(10)
```

---

### generate_intros()

Generate multiple intros for given headlines.

```python
generate_intros(headlines) -> list[str]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headlines` | `list[str]` | Required | Headlines to generate intros for |

**Returns:** `list[str]` - List of generated intros

**Example:**

```python
headlines = ["Breaking News", "Tech Update"]
intros = client.generate_intros(headlines)
```

---

### generate_articles()

Generate multiple articles for given headlines.

```python
generate_articles(headlines, words=500) -> list[str]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headlines` | `list[str]` | Required | Headlines to generate articles for |
| `words` | `int` | `500` | Target article length |

**Returns:** `list[str]` - List of generated articles

**Example:**

```python
headlines = ["Breaking News"]
articles = client.generate_articles(headlines, words=800)
```

---

## NewsStore

Low-level SQLite storage layer (not typically used directly).

### Constructor

```python
NewsStore(db_path=None)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str | None` | Platform-specific | SQLite database file path |

---

### add_headlines()

Store headlines in the database.

```python
add_headlines(headlines) -> None
```

---

### fetch_headline()

Fetch a random headline.

```python
fetch_headline(mark_used=True, allow_used=False) -> str | None
```

---

### fetch_intro()

Fetch a random intro.

```python
fetch_intro(headline=None, mark_used=True, allow_used=False) -> str | None
```

---

### fetch_article()

Fetch a random article.

```python
fetch_article(headline=None, mark_used=True, allow_used=False) -> str | None
```

---

### get_stats()

Get cache statistics.

```python
get_stats() -> dict
```

---

### reset_usage()

Reset all usage flags.

```python
reset_usage() -> None
```

---

### clear_all()

Delete all cached items.

```python
clear_all() -> None
```

---

## Exceptions

### APIError

Raised when LLM API calls fail.

```python
from faker_news.client import APIError

try:
    headline = fake.news_headline()
except APIError as e:
    print(f"API error: {e}")
```

### ConfigurationError

Raised when configuration is invalid or missing.

```python
from faker_news.client import ConfigurationError

try:
    provider = NewsProvider(fake)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Type Hints

faker-news includes type hints for all public APIs:

```python
from typing import Optional
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

def setup_provider(
    fake: Faker,
    api_key: Optional[str] = None
) -> NewsProvider:
    """Setup news provider with optional API key."""
    llm_config = LLMClientConfig(api_key=api_key) if api_key else None
    return NewsProvider(fake, llm_config=llm_config)
```

---

## Next Steps

- [Library Usage](library-usage.md) - Detailed usage examples
- [Architecture](architecture.md) - Understanding the internal architecture
- [Contributing](contributing.md) - Contributing to faker-news
