# Configuration

This guide covers all configuration options for customizing faker-news behavior.

## Provider Configuration

### NewsProvider Parameters

Configure the provider when creating it:

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

fake = Faker()
provider = NewsProvider(
    fake,
    db_path="/custom/path/cache.sqlite3",  # Custom cache location
    min_headline_pool=50,                   # Minimum unused headlines threshold
    headline_batch=60,                      # Headlines per batch
    intro_batch=30,                         # Intros per batch
    article_batch=15,                       # Articles per batch
    llm_config=None                         # LLM configuration (optional)
)
fake.add_provider(provider)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | Platform-specific | SQLite database file path |
| `min_headline_pool` | `int` | `30` | Minimum unused headlines before auto-refill |
| `headline_batch` | `int` | `40` | Headlines generated per batch |
| `intro_batch` | `int` | `20` | Intros generated per batch |
| `article_batch` | `int` | `10` | Articles generated per batch |
| `llm_config` | `LLMClientConfig` | `None` | LLM client configuration |

### Default Database Paths

If `db_path` is not specified, platform-specific defaults are used:

| Platform | Default Path |
|----------|-------------|
| Linux | `~/.cache/faker-news/cache.sqlite3` |
| macOS | `~/Library/Caches/faker-news/cache.sqlite3` |
| Windows | `%LOCALAPPDATA%\faker-news\cache\cache.sqlite3` |

## LLM Configuration

### LLMClientConfig Parameters

Configure the LLM client:

```python
from faker_news import LLMClientConfig

llm_config = LLMClientConfig(
    api_key="sk-your-api-key",              # API key
    base_url="https://api.openai.com/v1",   # API endpoint
    model_headlines="gpt-4o-mini",          # Model for headlines
    model_writing="gpt-4o-mini"             # Model for intros/articles
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | Auto-detected | LLM API key |
| `base_url` | `str` | Auto-detected | API endpoint URL |
| `model_headlines` | `str` | Provider-specific | Model for headline generation |
| `model_writing` | `str` | Provider-specific | Model for intro/article generation |

### Auto-Detection

If not specified, values are auto-detected:

1. **API Key**: Checked in order:
   - System keyring (`keyring.get_password("faker-news", "openai")`)
   - Environment variable (`OPENAI_API_KEY` or `DASHSCOPE_API_KEY`)
   - Explicit config

2. **Base URL**: Checked in order:
   - Environment variable (`OPENAI_BASE_URL` or `DASHSCOPE_BASE_URL`)
   - Default based on detected provider

3. **Models**: Auto-selected based on provider:
   - OpenAI: `gpt-4o-mini`
   - DashScope/Qwen: `qwen-flash`

## Configuration Examples

### Development Setup

Fast, cheap models for development:

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Fast and cheap
    model_writing="gpt-4o-mini"
)

fake = Faker()
provider = NewsProvider(
    fake,
    llm_config=llm_config,
    min_headline_pool=20,      # Lower threshold
    headline_batch=30,         # Smaller batches
    db_path="/tmp/dev-cache.sqlite3"
)
fake.add_provider(provider)
```

### Production Setup

Better models for production:

```python
llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Fast for headlines
    model_writing="gpt-4o"          # Better quality for articles
)

fake = Faker()
provider = NewsProvider(
    fake,
    llm_config=llm_config,
    min_headline_pool=100,     # Larger buffer
    headline_batch=150,        # Bigger batches
    db_path="/var/cache/faker-news/cache.sqlite3"
)
fake.add_provider(provider)
```

### High-Volume Setup

Optimized for generating lots of content:

```python
provider = NewsProvider(
    fake,
    min_headline_pool=200,     # Large buffer
    headline_batch=250,        # Large batches
    intro_batch=50,
    article_batch=25,
    db_path="/data/faker-news-cache.sqlite3"
)
```

### Testing Setup

Isolated environment for testing:

```python
import tempfile
from pathlib import Path

# Use temporary database
temp_db = Path(tempfile.mkdtemp()) / "test-cache.sqlite3"

provider = NewsProvider(
    fake,
    db_path=str(temp_db),
    min_headline_pool=10,      # Small for tests
    headline_batch=15
)
```

### Multi-Model Setup

Use different models for different content types:

```python
llm_config = LLMClientConfig(
    api_key="sk-...",
    model_headlines="gpt-4o-mini",  # Fast, simple model for headlines
    model_writing="gpt-4o"          # Better model for full articles
)

provider = NewsProvider(fake, llm_config=llm_config)
```

## Tuning Performance

### Batch Sizes

Larger batches = fewer API calls but longer waits:

| Use Case | Batch Size | Pros | Cons |
|----------|-----------|------|------|
| Development | 20-40 | Fast feedback | More API calls |
| Production | 100-200 | Fewer API calls | Longer waits |
| High-volume | 200+ | Optimal efficiency | Memory usage |

```python
# Conservative (more API calls, but faster feedback)
provider = NewsProvider(
    fake,
    headline_batch=30,
    intro_batch=15,
    article_batch=8
)

# Aggressive (fewer API calls, but longer waits)
provider = NewsProvider(
    fake,
    headline_batch=200,
    intro_batch=50,
    article_batch=30
)
```

### Pool Threshold

Controls when auto-refill happens:

```python
# Low threshold (more frequent refills)
provider = NewsProvider(fake, min_headline_pool=10)
# Refills when < 10 unused headlines

# High threshold (less frequent refills, but larger buffer)
provider = NewsProvider(fake, min_headline_pool=100)
# Refills when < 100 unused headlines
```

**Recommendations:**

- **Interactive use**: Low threshold (10-30)
- **Batch processing**: High threshold (50-200)
- **Background jobs**: Very high threshold (200+)

### Memory Considerations

Large batches use more memory during generation:

```python
# Memory-efficient (smaller batches)
provider = NewsProvider(
    fake,
    headline_batch=40,
    article_batch=10
)

# Memory-intensive (larger batches)
provider = NewsProvider(
    fake,
    headline_batch=500,
    article_batch=100
)
```

## Provider-Specific Configuration

### OpenAI

```python
llm_config = LLMClientConfig(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
    model_headlines="gpt-4o-mini",
    model_writing="gpt-4o"
)
```

### Alibaba DashScope/Qwen

```python
llm_config = LLMClientConfig(
    api_key="sk-...",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    model_headlines="qwen-flash",   # Fast model
    model_writing="qwen-plus"       # Better quality
)
```

### Azure OpenAI

```python
llm_config = LLMClientConfig(
    api_key="your-azure-key",
    base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment",
    model_headlines="gpt-4o-mini",
    model_writing="gpt-4"
)
```

### Custom OpenAI-Compatible API

```python
llm_config = LLMClientConfig(
    api_key="your-api-key",
    base_url="https://custom-api.example.com/v1",
    model_headlines="custom-model-fast",
    model_writing="custom-model-quality"
)
```

## Environment Variables

### Setting Credentials

Instead of hardcoding, use environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional

# DashScope
export DASHSCOPE_API_KEY="sk-..."
export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # Optional
```

Then use without explicit config:

```python
from faker import Faker
from faker_news import NewsProvider

# Auto-detects from environment
fake = Faker()
fake.add_provider(NewsProvider(fake))
```

## Advanced Configuration

### Multiple Providers

Use different configurations for different purposes:

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Fast provider for headlines only
fast_config = LLMClientConfig(model_headlines="gpt-4o-mini")
fast_provider = NewsProvider(
    Faker(),
    llm_config=fast_config,
    db_path="/tmp/headlines.sqlite3"
)

# Quality provider for articles
quality_config = LLMClientConfig(model_writing="gpt-4o")
quality_provider = NewsProvider(
    Faker(),
    llm_config=quality_config,
    db_path="/tmp/articles.sqlite3"
)
```

### Dynamic Configuration

Adjust configuration at runtime:

```python
def create_provider(env="development"):
    """Create provider based on environment."""
    if env == "production":
        return NewsProvider(
            fake,
            min_headline_pool=100,
            headline_batch=200,
            db_path="/var/cache/faker-news.sqlite3"
        )
    else:
        return NewsProvider(
            fake,
            min_headline_pool=20,
            headline_batch=30,
            db_path="/tmp/dev-cache.sqlite3"
        )

# Use it
provider = create_provider(env="production")
fake.add_provider(provider)
```

## Next Steps

- [LLM Providers](llm-providers.md) - Detailed guides for specific LLM providers
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - Understanding the internal architecture
