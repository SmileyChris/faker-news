# Setup & Configuration

This guide will walk you through setting up your LLM API credentials and configuring faker-news.

## Interactive Setup (Recommended)

The easiest way to configure faker-news is using the interactive setup wizard:

```bash
faker-news setup
```

This wizard will:

1. ✅ Check if you already have API keys configured (in keyring or environment)
2. 🔑 Guide you through selecting and configuring an LLM provider
3. 💾 Securely store your API key in your system's credential manager
4. 🧪 Test the connection with a sample generation
5. ✨ Confirm everything is working

## Secure API Key Storage

faker-news uses Python's `keyring` library to store API keys securely in your system's native credential manager:

| Platform | Storage Location |
|----------|-----------------|
| macOS | Keychain |
| Windows | Credential Manager |
| Linux | Secret Service (GNOME Keyring/KWallet) |

This is more secure than environment variables or config files, as the credentials are encrypted and managed by your OS.

## Manual Configuration

If you prefer to configure manually, you have three options:

### Option 1: System Keyring (Secure)

Set your API key in the system keyring using Python:

```python
import keyring

# For OpenAI
keyring.set_password("faker-news", "openai", "sk-your-api-key-here")

# For Alibaba DashScope/Qwen
keyring.set_password("faker-news", "dashscope", "sk-your-api-key-here")
```

### Option 2: Environment Variables

Set environment variables (less secure, but useful for CI/CD):

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY="sk-your-api-key-here"
    export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
    ```

=== "Alibaba DashScope/Qwen"

    ```bash
    export DASHSCOPE_API_KEY="sk-your-api-key-here"
    export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # Optional
    ```

=== "Azure OpenAI"

    ```bash
    export OPENAI_API_KEY="your-azure-api-key"
    export OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
    ```

### Option 3: Programmatic Configuration

Pass credentials directly in your code:

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Configure LLM client
llm_config = LLMClientConfig(
    api_key="sk-your-api-key-here",
    base_url="https://api.openai.com/v1",  # Optional
    model_headlines="gpt-4o-mini",         # Optional
    model_writing="gpt-4o-mini"            # Optional
)

# Create provider with config
fake = Faker()
provider = NewsProvider(fake, llm_config=llm_config)
fake.add_provider(provider)
```

## API Key Lookup Order

faker-news searches for API keys in this order:

1. **System keyring** (checked first via `keyring.get_password()`)
2. **Environment variables** (`OPENAI_API_KEY` or `DASHSCOPE_API_KEY`)
3. **Explicit config** (passed to `LLMClientConfig`)

This allows you to use the secure keyring for local development while using environment variables in CI/CD pipelines.

## Testing Your Configuration

After configuring your API key, test it:

### Using the CLI

```bash
# The setup wizard includes a test
faker-news setup

# Or manually test by generating a headline
faker-news headline
```

### Using Python

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# This will fail if credentials are not configured
try:
    headline = fake.news_headline()
    print(f"✅ Success! Generated: {headline}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Database Location

By default, faker-news stores the cache in platform-specific directories:

| Platform | Cache Location |
|----------|---------------|
| Linux | `~/.cache/faker-news/cache.sqlite3` |
| macOS | `~/Library/Caches/faker-news/cache.sqlite3` |
| Windows | `%LOCALAPPDATA%\faker-news\cache\cache.sqlite3` |

### Using a Custom Database Location

You can override the default location:

**Via Python:**

```python
provider = NewsProvider(fake, db_path="/custom/path/cache.sqlite3")
```

**Via CLI:**

```bash
faker-news headline --db /custom/path/cache.sqlite3
```

## Troubleshooting

### API Key Not Found

If you get "API key not configured" errors:

1. Run `faker-news setup` to check your configuration
2. Verify environment variables: `echo $OPENAI_API_KEY`
3. Check keyring: Run the Python snippet above to view stored keys

### Connection Errors

If you get connection errors:

1. Verify your API key is correct
2. Check your internet connection
3. Verify the `base_url` is correct for your provider
4. Check if your LLM provider is experiencing downtime

### Keyring Issues on Linux

If keyring doesn't work on Linux, you may need to install a secret service backend:

```bash
# Ubuntu/Debian
sudo apt-get install gnome-keyring

# Fedora
sudo dnf install gnome-keyring
```

Or use environment variables as a fallback.

## Next Steps

- [Quick Start](quick-start.md) - Start generating content
- [LLM Providers](llm-providers.md) - Detailed guides for specific LLM providers
- [Configuration](configuration.md) - Customize models, batch sizes, and more
