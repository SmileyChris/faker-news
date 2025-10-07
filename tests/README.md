# Test Suite

## Test Coverage

### ✅ All Tests Passing (68 tests)

#### `test_store.py` (16 tests)
Tests for the SQLite storage layer:
- Database initialization and schema
- Inserting and fetching headlines/intros/articles
- `consume` parameter behavior (mark as used after fetching)
- `allow_used` parameter behavior (fetch from all items)
- Reset modes (`reuse` vs `clear`)
- Duplicate headline handling
- Usage tracking and statistics
- Batch metadata fetching
- Platform-specific cache directory
- Example data loading from fixtures

#### `test_client.py` (13 tests)
Tests for the LLM client:
- Config auto-detection from environment variables
- Config loading from system keyring
- Priority order: explicit config > keyring > environment
- LLM client initialization
- JSON generation with retry logic and prose extraction
- Headline/intro/article generation
- DashScope vs OpenAI model auto-selection

#### `test_cli.py` (20 tests)
Tests for CLI commands:
- Help command
- Content generation commands (headline, intro, article)
- Command-line options (--consume, --allow-used, --words, --db, --new)
- `--new` flag for always generating fresh content (skipping cache)
- Preload with --populate flag
- Reset and stats commands
- Setup command with keyring integration and example data loading
- Error handling

#### `test_provider.py` (19 tests)
Tests for NewsProvider integration:
- Provider initialization and method registration
- Headline/intro/article generation on demand
- Automatic content pipeline (headlines → intros → articles)
- Auto-generating missing intros when requesting articles
- Auto-generating headlines when cache is empty
- Consume and allow_used behavior (including edge cases with auto-refill)
- Preload functionality
- Reset modes
- Cache statistics
- Batch generation with configurable pool sizes
- Multiple provider instances sharing database

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_store.py

# Run with coverage
uv run pytest --cov=faker_news --cov-report=html

# Run with verbose output
uv run pytest -v
```

## Test Organization

- `tests/conftest.py` - Shared fixtures and environment cleanup
- `tests/test_store.py` - NewsStore (SQLite layer) tests
- `tests/test_client.py` - LLMClient and config tests
- `tests/test_cli.py` - CLI command tests
- `tests/test_provider.py` - NewsProvider tests (some skipped)
