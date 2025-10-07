# Architecture

Understanding the internal architecture of faker-news.

## Overview

faker-news uses a three-layer architecture:

```
┌─────────────────────────────────────┐
│      NewsProvider (Faker API)       │  ← User-facing API
├─────────────────────────────────────┤
│   LLMClient (API Communication)     │  ← LLM integration
├─────────────────────────────────────┤
│   NewsStore (SQLite Storage)        │  ← Data persistence
└─────────────────────────────────────┘
```

Each layer has a specific responsibility and can be used independently.

## Layer 1: NewsProvider

**Location:** `src/faker_news/provider.py`

**Responsibility:** Faker provider interface and high-level content management

### Key Features

- Implements Faker provider interface
- Manages minimum pool thresholds
- Auto-refills pool when it runs low
- Lazy batch generation strategy
- User-facing API methods

### How It Works

```python
class NewsProvider(BaseProvider):
    def news_headline(self, consume=True, allow_used=False):
        # 1. Check pool size
        stats = self.store.get_stats()
        if stats['unused_headlines'] < self.min_headline_pool:
            # 2. Auto-refill if needed
            headlines = self.client.generate_headlines(self.headline_batch)
            self.store.add_headlines(headlines)

        # 3. Fetch from cache
        return self.store.fetch_headline(mark_used=consume, allow_used=allow_used)
```

### Design Pattern: Lazy Loading

Content is generated only when needed:

1. **Headlines**: Pre-generated in bulk when pool drops below threshold
2. **Intros**: Generated in batches only when first requested
3. **Articles**: Generated in batches only when first requested

This minimizes API calls while ensuring content availability.

---

## Layer 2: LLMClient

**Location:** `src/faker_news/client.py`

**Responsibility:** LLM API communication and content generation

### Key Features

- OpenAI-compatible API client
- Batch generation for efficiency
- JSON parsing with fallback logic
- Auto-detects provider (OpenAI vs DashScope)
- Retry logic with exponential backoff

### How It Works

```python
class LLMClient:
    def generate_headlines(self, count):
        # 1. Build prompt
        prompt = f"Generate {count} fake news headlines..."

        # 2. Call LLM API
        response = self.client.chat.completions.create(
            model=self.config.model_headlines,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )

        # 3. Parse JSON response
        content = response.choices[0].message.content
        headlines = self._parse_json(content)

        return headlines
```

### Batch Generation

All generation methods batch requests:

| Method | Batch Size | API Calls |
|--------|-----------|-----------|
| `generate_headlines(40)` | 40 | 1 |
| `generate_intros(20)` | 20 | 1 |
| `generate_articles(10)` | 10 | 1 |

Each batch is sent in a **single API call** and receives all responses at once.

### Error Handling

```python
def gen_json(self, prompt, model):
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = self.client.chat.completions.create(...)
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(0.8 * (attempt + 1))  # Exponential backoff
```

### Connection Efficiency

- OpenAI client instantiated once per `LLMClient`
- httpx connection pooling with keep-alive
- Persistent connections reused across requests

---

## Layer 3: NewsStore

**Location:** `src/faker_news/store.py`

**Responsibility:** SQLite database management and content storage

### Database Schema

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headline TEXT NOT NULL UNIQUE,
    intro TEXT,
    article TEXT,
    used_headline BOOLEAN DEFAULT 0,
    used_intro BOOLEAN DEFAULT 0,
    used_article BOOLEAN DEFAULT 0
);
```

### Key Features

- Three separate usage flags per item
- Random selection with `ORDER BY RANDOM()`
- Atomic updates with COALESCE
- Efficient batch inserts
- Platform-specific cache directory

### How It Works

```python
class NewsStore:
    def fetch_headline(self, mark_used=True, allow_used=False):
        # Build query based on parameters
        if allow_used:
            query = "SELECT headline FROM items ORDER BY RANDOM() LIMIT 1"
        else:
            query = """
                SELECT headline FROM items
                WHERE used_headline = 0
                ORDER BY RANDOM() LIMIT 1
            """

        # Fetch item
        row = self.conn.execute(query).fetchone()
        if not row:
            return None

        # Mark as used if requested
        if mark_used:
            self.conn.execute(
                "UPDATE items SET used_headline = 1 WHERE headline = ?",
                (row[0],)
            )
            self.conn.commit()

        return row[0]
```

### Usage Tracking

Three independent usage flags:

- `used_headline`: Headline has been consumed
- `used_intro`: Intro has been consumed
- `used_article`: Article has been consumed

This allows:
- Fetching the same headline multiple times with different intros
- Reusing headlines while consuming intros/articles
- Flexible content reuse strategies

### Atomic Updates

```python
def add_intro(self, headline, intro):
    # Only update if intro is NULL (don't overwrite existing)
    self.conn.execute("""
        UPDATE items
        SET intro = COALESCE(intro, ?)
        WHERE headline = ?
    """, (intro, headline))
```

---

## Data Flow

### Generating a Complete Article

```
User calls: fake.news_article(headline="Breaking News")
    │
    ├──> NewsProvider.news_article()
    │       │
    │       ├──> Check if article exists in cache
    │       │    ├─[YES]─> NewsStore.fetch_article()
    │       │    │              └──> Return cached article
    │       │    │
    │       │    └─[NO]──> Need to generate
    │       │                │
    │       │                ├──> LLMClient.generate_articles([headline])
    │       │                │       │
    │       │                │       ├──> Build prompt
    │       │                │       ├──> Call OpenAI API
    │       │                │       ├──> Parse JSON response
    │       │                │       └──> Return [article]
    │       │                │
    │       │                ├──> NewsStore.add_article(headline, article)
    │       │                └──> NewsStore.fetch_article(headline)
    │       │
    │       └──> Return article
    │
    └──> Article returned to user
```

### Auto-Refill Process

```
User calls: fake.news_headline()
    │
    ├──> NewsProvider.news_headline()
    │       │
    │       ├──> NewsStore.get_stats()
    │       │       └──> { unused_headlines: 25 }
    │       │
    │       ├──> Check: 25 < 30 (min_headline_pool)?
    │       │    └─[YES]─> Auto-refill needed
    │       │                │
    │       │                ├──> LLMClient.generate_headlines(40)
    │       │                │       └──> [... 40 headlines ...]
    │       │                │
    │       │                └──> NewsStore.add_headlines(headlines)
    │       │
    │       └──> NewsStore.fetch_headline()
    │               └──> Return headline
    │
    └──> Headline returned to user
```

---

## Performance Optimizations

### 1. Lazy Batch Generation

Instead of generating all content upfront:

- Headlines pre-generated in bulk
- Intros/articles generated only when needed
- Batched to minimize API calls

### 2. SQLite Caching

All content cached locally:

- No repeated API calls for same content
- Random selection for variety
- Usage tracking to avoid repetition

### 3. Connection Pooling

HTTP connections reused:

- Single OpenAI client instance
- httpx connection pooling
- Keep-alive for persistent connections

### 4. Batch API Calls

All generation happens in batches:

```python
# Inefficient: 40 API calls
for i in range(40):
    headline = generate_one_headline()

# Efficient: 1 API call
headlines = generate_headlines(40)
```

### 5. Smart Populate Mode

Populating efficiently:

```python
def populate(n):
    # 1. Get unused headlines missing content
    incomplete = fetch_headlines_needing_content(limit=n)

    # 2. Use existing complete unused headlines
    if len(incomplete) < n:
        complete = fetch_complete_unused_headlines(limit=n - len(incomplete))
        incomplete.extend(complete)

    # 3. Generate new only if still needed
    if len(incomplete) < n:
        new_count = n - len(incomplete)
        generate_new_headlines_with_content(new_count)
```

---

## Code Organization

```
src/faker_news/
├── __init__.py       # Public API exports
├── client.py         # LLMClient and LLMClientConfig
├── store.py          # NewsStore (SQLite layer)
├── provider.py       # NewsProvider (Faker provider)
├── cli.py            # Command-line interface
└── setup.py          # Interactive setup script
```

### Module Dependencies

```
cli.py ──────┐
             ├──> provider.py ──> client.py
setup.py ────┤                       │
             └──────────────> store.py
```

- `cli.py` and `setup.py` depend on all modules
- `provider.py` orchestrates `client.py` and `store.py`
- `client.py` and `store.py` are independent

---

## Design Decisions

### Why SQLite?

- ✅ Zero configuration required
- ✅ Platform-independent
- ✅ ACID transactions
- ✅ Efficient random sampling
- ✅ No external dependencies
- ✅ Easy backup/migration

### Why Three Usage Flags?

Allows flexible content reuse:

```python
# Use same headline with different intros
headline = fake.news_headline(consume=False)
intro1 = fake.news_intro(headline=headline)  # Consumes intro
intro2 = fake.news_intro(headline=headline)  # Different intro

# Headline still available (wasn't consumed)
same_headline = fake.news_headline()  # Might get same headline
```

### Why Lazy Loading?

Minimizes upfront cost:

- Don't generate articles if user only needs headlines
- Don't generate intros if user only needs articles
- Generate only what's actually used

### Why Batch Generation?

Efficiency:

- 1 API call for 40 headlines vs. 40 API calls
- Lower latency (parallel processing by LLM)
- Lower cost (fewer API round trips)

---

## Extension Points

### Custom Storage Backend

Replace SQLite with another backend:

```python
class RedisStore:
    """Custom storage using Redis."""

    def fetch_headline(self, mark_used=True, allow_used=False):
        # Implement using Redis
        pass

# Use custom store
provider = NewsProvider(fake)
provider.store = RedisStore()
```

### Custom LLM Provider

Use a different LLM library:

```python
class CustomLLMClient:
    """Custom LLM client using different library."""

    def generate_headlines(self, count):
        # Use custom implementation
        pass

provider = NewsProvider(fake)
provider.client = CustomLLMClient()
```

### Custom Content Types

Extend to generate other content:

```python
class ExtendedProvider(NewsProvider):
    def news_summary(self, headline=None):
        """Generate article summaries."""
        # Implementation
        pass
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Contributing](contributing.md) - Contributing to the codebase
