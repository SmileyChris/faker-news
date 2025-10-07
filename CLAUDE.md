# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Faker provider for generating fake news content (headlines, intros, articles) using any OpenAI-compatible LLM API. The provider uses SQLite caching to store generated content and mark items as used/unused, enabling efficient batch generation and reuse.

Supports multiple LLM providers including:
- OpenAI (GPT-4, GPT-3.5-turbo, etc.)
- Alibaba Cloud Model Studio / Qwen (qwen-flash, qwen-plus, etc.)
- Azure OpenAI
- Any other OpenAI-compatible API

## Package Structure

```
src/faker_news/
├── __init__.py       # Public API exports
├── client.py         # LLMClient and LLMClientConfig
├── store.py          # NewsStore (SQLite layer)
├── provider.py       # NewsProvider (Faker provider implementation)
├── cli.py            # Command-line interface (Click-based)
└── setup.py          # Interactive setup script (Click-based)
```

## Core Architecture

**Three-layer architecture:**

1. **LLM Client (`LLMClient`)** - Located in `src/faker_news/client.py`
   - Wraps OpenAI-compatible API calls to any LLM provider
   - `generate_headlines()` - Batch generates fake news headlines
   - `generate_intros()` - Creates short intros for given headlines
   - `generate_articles()` - Writes full ~500 word articles with markdown subheadings
   - Uses JSON parsing with fallback logic to handle non-JSON prose from LLM
   - Auto-detects Qwen/DashScope vs OpenAI based on environment variables

2. **Storage Layer (`NewsStore`)** - Located in `src/faker_news/store.py`
   - SQLite database managing cached content
   - Single `items` table tracks: headline, intro, article, usage flags for each
   - Three separate usage flags: `used_headline`, `used_intro`, `used_article`
   - Items are fetched randomly and marked as used; can be reset to "reuse" or "clear"
   - Database file stored in platform-specific cache directory by default (uses `platformdirs`)

3. **Faker Provider (`NewsProvider`)** - Located in `src/faker_news/provider.py`
   - Public API implementing Faker provider interface
   - Auto-maintains a minimum pool of unused headlines (configurable threshold)
   - Batch-generates intros and articles on-demand when pool runs low
   - Each fetch operation marks item as used (single-use by default)

**Key Design Pattern:** Lazy batch generation
- Headlines pre-generated in bulk when pool drops below threshold
- Intros/articles generated in batches only when requested
- This minimizes API calls while ensuring content availability

## Environment Setup

**API Key Storage:**

The package uses secure credential storage via Python's `keyring` library:
- macOS: Keychain
- Windows: Credential Manager
- Linux: Secret Service (GNOME Keyring/KWallet)

**Setup Options:**

**Option A: Use setup wizard (Recommended)**
```bash
uv run faker-news setup
```
Stores API key securely in system keyring.

**Option B: Environment variables**
```bash
# For OpenAI
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # optional

# For Alibaba DashScope/Qwen
export DASHSCOPE_API_KEY="your-key"
export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # optional
```

**Key Lookup Order:**
1. System keyring (checked first via `keyring.get_password("faker-news", "openai")` or `"dashscope"`)
2. Environment variables (fallback for CI/CD)
3. Config passed to `LLMClientConfig`

The client auto-detects which provider you're using and automatically selects appropriate default models.

**Install dependencies:**
```bash
# Install package
pip install -e .

# For development:
pip install -e ".[dev]"
```

**Interactive API key setup:**
```bash
# Check for API keys and optionally configure them
uv run faker-news setup
```

## Common Commands

**Note:** Use `uv run` prefix for all commands (both `faker-news` CLI and `pytest`).

**Setup:**
```bash
# Interactive setup (checks API keys, helps configure, runs test)
uv run faker-news setup
```

**Build/Install:**
```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Build distribution
python -m build
```

**CLI Usage:**
```bash
# Generate single items (non-consuming by default)
uv run faker-news headline
uv run faker-news intro --headline "Some Headline"
uv run faker-news article --headline "Some Headline" --words 800

# Always generate fresh content (skip cache)
uv run faker-news headline --new
uv run faker-news intro --new
uv run faker-news article --new --words 800

# Mark items as used with --consume flag
uv run faker-news headline --consume
uv run faker-news article --consume

# Fetch from all items (used or unused) with --allow-used flag
uv run faker-news headline --allow-used
uv run faker-news article --allow-used --consume

# Preload cache
uv run faker-news preload --n 50
uv run faker-news preload --n 50 --with-intros --with-articles  # Preload with full content
uv run faker-news preload --n 50 --with-articles --words 800  # Custom article length
uv run faker-news preload --n 50 --populate  # Populate N headlines with full content (existing first, then new)

# View cache statistics
uv run faker-news stats

# Reset usage flags (reuse cached items)
uv run faker-news reset --mode reuse

# Clear all cached content
uv run faker-news reset --mode clear

# Use custom database file
uv run faker-news headline --db /path/to/custom.sqlite3
```

**Important:** CLI commands do NOT mark items as used by default. Use `--consume` flag if you want to mark items as used.

**--new flag:** Use `--new` to always generate fresh content, bypassing the cache. Useful for generating multiple variations or testing different outputs.

**Preload modes:**
- `preload --n 50` - Generate 50 new headlines only
- `preload --n 50 --with-intros --with-articles` - Generate 50 new headlines with full content
- `preload --n 50 --populate` - Ensure 50 unused headlines exist with full content (uses existing first, generates new only if needed)

**Library Usage** (as Faker provider):
```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
provider = NewsProvider(fake)
fake.add_provider(provider)

# Generate content (marks as used by default)
headline = fake.news_headline()
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline, words=500)

# Fetch without marking as used
headline = fake.news_headline(consume=False)
article = fake.news_article(consume=False)

# Fetch from ALL items (both used and unused)
headline = fake.news_headline(allow_used=True)

# Admin operations
fake.news_preload_headlines(50)
fake.news_stats()
fake.news_reset("reuse")  # or "clear"
```

**Custom Configuration:**
```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Configure for specific LLM provider
llm_config = LLMClientConfig(
    api_key="your-key",
    base_url="https://api.openai.com/v1",
    model_headlines="gpt-4o-mini",
    model_writing="gpt-4o"
)

fake = Faker()
provider = NewsProvider(fake, llm_config=llm_config)
fake.add_provider(provider)
```

## Configuration Knobs

`NewsProvider` constructor parameters:
- `db_path` - SQLite database file path (default: platform-specific cache directory via `platformdirs`)
  - Linux: `~/.cache/faker-news/cache.sqlite3`
  - macOS: `~/Library/Caches/faker-news/cache.sqlite3`
  - Windows: `%LOCALAPPDATA%\faker-news\cache\cache.sqlite3`
- `min_headline_pool` - Minimum unused headlines before auto-refill (default: 30)
- `headline_batch` - Headlines generated per batch (default: 40)
- `intro_batch` - Intros generated per batch (default: 20)
- `article_batch` - Articles generated per batch (default: 10)
- `llm_config` - `LLMClientConfig` object to customize model/API settings

`LLMClientConfig` parameters:
- `api_key` - API key (auto-detects from `OPENAI_API_KEY` or `DASHSCOPE_API_KEY`)
- `base_url` - API endpoint (auto-detects from `OPENAI_BASE_URL` or `DASHSCOPE_BASE_URL`)
- `model_headlines` - Model for headline generation (default: "gpt-4o-mini" for OpenAI, auto-switches to "qwen-flash" for DashScope)
- `model_writing` - Model for intro/article generation (default: "gpt-4o-mini" for OpenAI, auto-switches to "qwen-flash" for DashScope)

## Testing

**Run tests:**
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_store.py

# Run with coverage
uv run pytest --cov=faker_news --cov-report=html

# Run verbose
uv run pytest -v

# Skip slow/integration tests
uv run pytest -m "not integration and not slow"
```

**Test organization:**
- `tests/conftest.py` - Shared fixtures and environment cleanup (clears API keys)
- `tests/test_store.py` - NewsStore (SQLite layer) tests (16 tests)
- `tests/test_client.py` - LLMClient and config tests (13 tests)
- `tests/test_cli.py` - CLI command tests (17 tests)
- `tests/test_provider.py` - NewsProvider tests (16 tests)

All 62 tests are passing. Tests use pytest fixtures to clear environment variables and ensure isolated test execution.

## Documentation

**Build and preview documentation:**
```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve documentation locally (with live reload)
mkdocs serve

# Build documentation
mkdocs build
```

Documentation is built with MkDocs and Material theme. Visit http://localhost:8000 when running `mkdocs serve`.

**IMPORTANT: When making changes to the codebase, update relevant documentation:**
- **API changes** → Update `docs/api-reference.md`
- **CLI changes** → Update `docs/cli-reference.md`
- **Configuration changes** → Update `docs/configuration.md`
- **Architecture changes** → Update `docs/architecture.md`
- **New features** → Update relevant guides and examples

Documentation structure:
```
docs/
├── index.md                  # Homepage
├── getting-started.md        # Installation
├── quick-start.md            # Quick start guide
├── setup.md                  # Setup & configuration
├── library-usage.md          # Python API usage
├── cli-reference.md          # CLI command reference
├── cache-management.md       # Cache management guide
├── configuration.md          # Configuration options
├── llm-providers.md          # LLM provider guides
├── api-reference.md          # Complete API reference
├── architecture.md           # Architecture documentation
└── contributing.md           # Contributing guide
```

## Important Implementation Notes

- **Cache location:** Uses `platformdirs` to store the SQLite cache in the platform-specific user cache directory. This follows OS conventions and keeps the cache separate from project files. Users can override with a custom `db_path`.

- **Secure API key storage:** Uses Python's `keyring` library to store API keys in system-native credential managers (Keychain/Credential Manager/Secret Service). Keys are checked in order: keyring → environment variables → explicit config.

- **Multi-provider support:** The `LLMClientConfig.__post_init__()` method auto-detects which LLM provider to use based on keyring/environment variables and automatically selects appropriate default models.

- **Consume behavior:**
  - **Library usage:** Methods mark items as "used" by default (`consume=True`). Pass `consume=False` to fetch without marking as used.
  - **CLI usage:** Commands do NOT mark items as used by default (`consume=False`). Use `--consume` flag to mark items as used.
  - This allows CLI users to test/view content repeatedly without depleting the cache.

- **Fetching from used items:**
  - By default, methods only fetch from unused items (`allow_used=False`)
  - Pass `allow_used=True` to fetch from all items (both used and unused)
  - CLI: Use `--allow-used` flag
  - This is different from `news_reset("reuse")` which permanently marks ALL items as unused
  - `allow_used=True` temporarily expands the pool without changing usage flags (unless `consume=True`)

- **Two ways to reuse content:**
  1. **Reset usage flags:** `news_reset("reuse")` marks all items as unused (persistent change)
  2. **Allow used items:** `allow_used=True` fetches from both pools without resetting (temporary access)

- **Content matching:** When requesting intro/article for a specific headline, the code directly queries DB by headline string. LLM responses may paraphrase headlines slightly, so matching relies on LLM returning exact headlines.

- **Error handling:** `gen_json()` retries up to 2 times with 0.8s delay, attempting to extract JSON even if LLM adds prose around it.

- **Database schema:** The `items` table uses `COALESCE` in updates to prevent overwriting existing intros/articles if re-generated.

- **Random selection:** All fetch operations use `ORDER BY RANDOM()` to provide variety in returned content.

- **Populate mode:** The `--populate` flag intelligently manages content generation:
  1. **Prioritizes unused headlines missing intros/articles** (via `fetch_headlines_needing_content()`)
  2. Only fills with complete unused headlines if needed to reach N
  3. Only generates new headlines if there aren't enough unused ones
  4. Uses batch SQL queries to check metadata (1-2 queries total, not N individual queries)
  5. Generates only the missing content (intros/articles) for selected headlines

  This minimizes API usage by selecting headlines that actually need content generation.

- **LLM Connection Efficiency:** The OpenAI client is instantiated once per `LLMClient` instance and reused for all requests. The OpenAI Python SDK uses httpx with built-in HTTP connection pooling and keep-alive. All generation methods (headlines, intros, articles) batch their requests - each batch is sent in a single API call with all N items and receives all responses in one JSON array.
