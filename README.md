# faker-news

Faker provider that turns any OpenAI-compatible LLM into a fake news generator with caching and reuse controls.

## Features
- Generate headlines, intros, and full articles on demand
- Keep content in a SQLite cache with per-item usage tracking
- Batch requests to minimize API calls and latency
- Works with OpenAI, Azure OpenAI, Qwen/DashScope, and other OpenAI-compatible APIs

## Installation
```bash
pip install faker-news
```

## Quick Start

Try it without installation using uvx:
```bash
# Set up your API key / load example data
uvx faker-news setup

# Browse generated articles
uvx faker-news browse
```

Use as a library:
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

## Documentation
Full guides, API reference, and CLI details live in the `docs/` directory. Start with `docs/quick-start.md` or `docs/cli-reference.md`.

## Contributing
See `docs/contributing.md` for the development workflow and guidelines.

## License
MIT
