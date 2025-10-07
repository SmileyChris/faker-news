# faker-news

Faker provider that turns any OpenAI-compatible LLM into a fake news generator with caching and reuse controls.

## Features
- Generate headlines, intros, and full articles on demand
- Keep content in a SQLite cache with per-item usage tracking
- Batch requests to minimize API calls and latency
- Works with OpenAI, Azure OpenAI, Qwen/DashScope, and other OpenAI-compatible APIs

## Installation
```bash
pip install -e .
# Development extras
pip install -e ".[dev]"
```

## Quick Start
```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
provider = NewsProvider(fake)
fake.add_provider(provider)

headline = fake.news_headline()
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline, words=500)
```

## CLI
```bash
uv run faker-news headline
uv run faker-news article --words 800
uv run faker-news preload --n 50 --with-intros --with-articles
uv run faker-news stats
```

## Documentation
Full guides, API reference, and CLI details live in the `docs/` directory. Start with `docs/quick-start.md` or `docs/cli-reference.md`.

## Contributing
See `docs/contributing.md` for the development workflow and guidelines.

## License
MIT
