# faker-news

**A Faker provider for generating fake news content using OpenAI-compatible LLM APIs.**

Generate realistic fake news headlines, article introductions, and full articles using any OpenAI-compatible LLM (OpenAI, Qwen, Azure, etc.) with intelligent caching and batch generation.

## Features

🎲 **Realistic Content Generation**
:   Generate fake news headlines, intros, and full articles that look authentic

💾 **Smart SQLite Caching**
:   Efficiently cache and reuse generated content with usage tracking

🔄 **Batch Generation**
:   Minimize API calls by generating content in optimized batches

🔌 **Multi-Provider Support**
:   Works with OpenAI, Alibaba Qwen, Azure OpenAI, and any OpenAI-compatible API

🎯 **Lazy Loading**
:   Content is generated only when needed, not upfront

♻️ **Reusable Content**
:   Track usage and reuse content as needed with flexible consumption modes

🔐 **Secure Credentials**
:   API keys stored securely in your system's credential manager (Keychain/Credential Manager/Secret Service)

## Quick Example

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# Generate a complete news article
headline = fake.news_headline()
intro = fake.news_intro(headline=headline)
article = fake.news_article(headline=headline, words=500)

print(f"{headline}\n\n{intro}\n\n{article}")
```

Or use the CLI:

```bash
# One-time setup
faker-news setup

# Generate content
faker-news headline
faker-news article --words 800
faker-news preload --n 50  # Preload for faster access
```

## How It Works

1. **Headlines** are pre-generated in bulk and cached locally in SQLite
2. **Intros and articles** are generated on-demand in batches when needed
3. Each item is **marked as used** after being fetched (configurable)
4. When the pool runs low, **new content is auto-generated** in the background
5. Content can be **reused** by resetting usage flags or fetching from the full pool

This lazy batch approach minimizes LLM API calls while ensuring content is always available.

## Why faker-news?

- **Testing**: Generate realistic test data for news applications
- **Demos**: Create convincing placeholder content for prototypes
- **Development**: Populate databases with fake articles during development
- **Privacy**: No real news data needed - generate everything on-demand

## Getting Started

Ready to generate fake news? Start with the [Installation Guide](getting-started.md) or jump to the [Quick Start](quick-start.md).

## License

MIT License - see the repository for details.
