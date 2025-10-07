# Contributing

Thank you for your interest in contributing to faker-news! This guide will help you get started.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/smileychris/faker-news.git
cd faker-news
```

### 2. Install Dependencies

Install the package in development mode with all dependencies:

```bash
pip install -e ".[dev]"
```

This installs:
- Core dependencies (faker, openai, click, etc.)
- Development tools (pytest, ruff)
- Documentation tools (mkdocs, mkdocs-material)

### 3. Configure API Key

Run the setup wizard to configure your LLM API key:

```bash
uv run faker-news setup
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
```

### 4. Verify Installation

Run the tests to verify everything works:

```bash
uv run pytest
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=faker_news --cov-report=html

# Run specific test file
uv run pytest tests/test_provider.py

# Run verbose
uv run pytest -v

# Skip slow/integration tests
uv run pytest -m "not integration and not slow"
```

### Code Formatting

We use Ruff for code formatting:

```bash
# Format all code
ruff format src/ tests/

# Check without modifying
ruff format --check src/ tests/
```

### Linting

We use Ruff for linting:

```bash
# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Building Documentation

Build and preview the documentation locally:

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

Then visit http://localhost:8000 to view the docs.

## Code Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints for all public APIs
- Maximum line length: 120 characters
- Use Ruff for formatting (automated)

### Documentation

- Add docstrings to all public functions/classes
- Include examples in docstrings
- Update relevant documentation when changing APIs
- **IMPORTANT:** When changing APIs, update:
  - `docs/api-reference.md` - For Python API changes
  - `docs/cli-reference.md` - For CLI command changes
  - Other relevant docs as needed

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Mark slow tests with `@pytest.mark.slow`
- Mark integration tests with `@pytest.mark.integration`

### Example Test

```python
import pytest
from faker import Faker
from faker_news import NewsProvider


def test_news_headline(fake):
    """Test headline generation."""
    fake.add_provider(NewsProvider(fake))

    headline = fake.news_headline()

    assert isinstance(headline, str)
    assert len(headline) > 0


@pytest.mark.integration
def test_full_article_generation(fake):
    """Test complete article generation (requires API key)."""
    fake.add_provider(NewsProvider(fake))

    headline = fake.news_headline()
    intro = fake.news_intro(headline=headline)
    article = fake.news_article(headline=headline)

    assert headline in intro or intro.startswith(headline)
    assert len(article) > len(intro)
```

## Project Structure

```
faker-news/
├── src/faker_news/
│   ├── __init__.py       # Public API exports
│   ├── client.py         # LLMClient and LLMClientConfig
│   ├── store.py          # NewsStore (SQLite layer)
│   ├── provider.py       # NewsProvider (Faker provider)
│   ├── cli.py            # Command-line interface
│   └── setup.py          # Interactive setup script
├── tests/
│   ├── conftest.py       # Shared fixtures
│   ├── test_client.py    # LLMClient tests
│   ├── test_store.py     # NewsStore tests
│   ├── test_provider.py  # NewsProvider tests
│   └── test_cli.py       # CLI tests
├── docs/                 # MkDocs documentation
│   ├── index.md
│   ├── getting-started.md
│   ├── api-reference.md
│   └── ...
├── pyproject.toml        # Project configuration
├── mkdocs.yml            # Documentation configuration
├── README.md             # Quick reference
└── CLAUDE.md             # Developer guide (for Claude Code)
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write code following the guidelines above
- Add tests for new functionality
- Update documentation if needed
- Format code with Black
- Lint code with Ruff

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Check coverage
uv run pytest --cov=faker_news
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add feature: your feature description"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Areas for Contribution

### Features

- Support for additional LLM providers
- New content types (summaries, captions, etc.)
- Advanced caching strategies
- Performance optimizations
- CLI enhancements

### Documentation

- More usage examples
- Tutorials for specific use cases
- Translation to other languages
- Video walkthroughs
- API documentation improvements

### Testing

- Increase test coverage
- Add integration tests
- Performance benchmarks
- Stress tests

### Bug Fixes

Check the [issues page](https://github.com/smileychris/faker-news/issues) for reported bugs.

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description**: What happened vs. what you expected
2. **Steps to reproduce**: Exact steps to trigger the bug
3. **Environment**:
   - Python version
   - faker-news version
   - Operating system
   - LLM provider being used
4. **Code sample**: Minimal code to reproduce the issue
5. **Error messages**: Full error output

### Feature Requests

When requesting features, include:

1. **Use case**: Why you need this feature
2. **Proposed solution**: How you envision it working
3. **Alternatives**: Other approaches you've considered
4. **Examples**: Similar features in other tools

## Code Review Process

1. **Automated checks**: CI runs tests and linting
2. **Manual review**: Maintainer reviews code
3. **Feedback**: Suggestions for improvements
4. **Approval**: Once approved, PR is merged

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. Build distribution: `python -m build`
5. Publish to PyPI: `twine upload dist/*`
6. Create GitHub release

## Community Guidelines

- Be respectful and inclusive
- Help others in issues and discussions
- Follow the code of conduct
- Give credit where due

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/smileychris/faker-news/issues)
- **Discussions**: [GitHub Discussions](https://github.com/smileychris/faker-news/discussions)
- **Email**: smileychris@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- CONTRIBUTORS.md (coming soon)

Thank you for contributing to faker-news! 🎉
