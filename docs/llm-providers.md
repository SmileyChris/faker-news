# LLM Providers

faker-news works with any OpenAI-compatible LLM API. This guide provides detailed setup instructions for popular providers.

## OpenAI

### Setup

=== "Using Setup Wizard"

    ```bash
    faker-news setup
    # Select "OpenAI" when prompted
    ```

=== "Using Environment Variables"

    ```bash
    export OPENAI_API_KEY="sk-..."
    export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
    ```

=== "Using Python Config"

    ```python
    from faker_news import LLMClientConfig

    llm_config = LLMClientConfig(
        api_key="sk-...",
        base_url="https://api.openai.com/v1",
        model_headlines="gpt-4o-mini",
        model_writing="gpt-4o"
    )
    ```

### Recommended Models

| Purpose | Model | Speed | Quality | Cost |
|---------|-------|-------|---------|------|
| Headlines | `gpt-4o-mini` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 |
| Headlines | `gpt-3.5-turbo` | ⚡⚡⚡ | ⭐⭐ | 💰 |
| Articles | `gpt-4o-mini` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 |
| Articles (Quality) | `gpt-4o` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 |
| Articles (Quality) | `gpt-4-turbo` | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰💰 |

### Example Configuration

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Balanced setup (recommended)
llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Fast and cheap
    model_writing="gpt-4o-mini"     # Good quality
)

# Quality-focused setup
llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Headlines don't need premium
    model_writing="gpt-4o"          # Best quality for articles
)

fake = Faker()
fake.add_provider(NewsProvider(fake, llm_config=llm_config))
```

### Getting an API Key

1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Navigate to API keys
3. Create a new secret key
4. Copy and store securely

---

## Alibaba DashScope (Qwen)

### Setup

=== "Using Setup Wizard"

    ```bash
    faker-news setup
    # Select "Alibaba DashScope/Qwen" when prompted
    ```

=== "Using Environment Variables"

    ```bash
    export DASHSCOPE_API_KEY="sk-..."
    export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # Optional
    ```

=== "Using Python Config"

    ```python
    from faker_news import LLMClientConfig

    llm_config = LLMClientConfig(
        api_key="sk-...",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        model_headlines="qwen-flash",
        model_writing="qwen-plus"
    )
    ```

### Recommended Models

| Purpose | Model | Speed | Quality | Cost |
|---------|-------|-------|---------|------|
| Headlines | `qwen-flash` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 |
| Headlines | `qwen-turbo` | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 |
| Articles | `qwen-flash` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 |
| Articles (Quality) | `qwen-plus` | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 |
| Articles (Quality) | `qwen-max` | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 |

### Example Configuration

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Balanced setup
llm_config = LLMClientConfig(
    model_headlines="qwen-flash",  # Fast and cheap
    model_writing="qwen-plus"      # Better quality
)

fake = Faker()
fake.add_provider(NewsProvider(fake, llm_config=llm_config))
```

### Getting an API Key

1. Sign up at [Alibaba Cloud Model Studio](https://bailian.console.alibabacloud.com/)
2. Enable DashScope API
3. Create an API key
4. Use international endpoint for global access

---

## Azure OpenAI

### Setup

```python
from faker_news import LLMClientConfig

llm_config = LLMClientConfig(
    api_key="your-azure-api-key",
    base_url="https://{your-resource-name}.openai.azure.com/openai/deployments/{deployment-name}",
    model_headlines="gpt-4o-mini",  # Your deployment name
    model_writing="gpt-4"           # Your deployment name
)
```

### Example Configuration

```python
from faker import Faker
from faker_news import NewsProvider, LLMClientConfig

# Azure OpenAI setup
llm_config = LLMClientConfig(
    api_key="abc123...",
    base_url="https://my-openai.openai.azure.com/openai/deployments/gpt-4o-mini",
    model_headlines="gpt-4o-mini",
    model_writing="gpt-4"
)

fake = Faker()
fake.add_provider(NewsProvider(fake, llm_config=llm_config))
```

!!! note "Deployment Names"
    Use your Azure deployment names as the model names. These may differ from OpenAI's model names.

### Getting Started with Azure OpenAI

1. Create an Azure account
2. Create an Azure OpenAI resource
3. Deploy models (e.g., gpt-4o-mini, gpt-4)
4. Get API key and endpoint from Azure portal

---

## Other OpenAI-Compatible APIs

faker-news works with any API that implements the OpenAI chat completions interface.

### Generic Setup

```python
from faker_news import LLMClientConfig

llm_config = LLMClientConfig(
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com/v1",
    model_headlines="your-fast-model",
    model_writing="your-quality-model"
)
```

### Compatible Providers

These providers have OpenAI-compatible APIs:

- **Anthropic** (via compatibility layer)
- **Groq** - Ultra-fast inference
- **Together.ai** - Multiple open models
- **Perplexity** - Search-augmented models
- **Anyscale** - Llama and Mistral models
- **DeepSeek** - Chinese LLM provider
- **Local models** (via LM Studio, Ollama, vLLM, etc.)

### Example: Local LLM with Ollama

```python
from faker_news import LLMClientConfig

# Run Ollama locally (ollama serve)
llm_config = LLMClientConfig(
    api_key="not-needed",  # Ollama doesn't require API key
    base_url="http://localhost:11434/v1",
    model_headlines="llama3.1",
    model_writing="llama3.1"
)
```

### Example: Groq

```python
from faker_news import LLMClientConfig

llm_config = LLMClientConfig(
    api_key="gsk_...",
    base_url="https://api.groq.com/openai/v1",
    model_headlines="llama-3.1-70b-versatile",
    model_writing="llama-3.1-70b-versatile"
)
```

---

## Choosing a Provider

### By Use Case

| Use Case | Recommended Provider | Why |
|----------|---------------------|-----|
| Production | OpenAI | Best reliability and quality |
| Development | OpenAI (gpt-4o-mini) | Good balance of cost/quality |
| High-volume | Alibaba Qwen | Cost-effective for bulk |
| Local/Offline | Ollama + local models | No API costs, privacy |
| Fast inference | Groq | Ultra-fast responses |
| Budget-conscious | Alibaba Qwen | Lowest cost per token |

### By Region

| Region | Recommended Provider |
|--------|---------------------|
| North America | OpenAI, Azure OpenAI |
| Europe | OpenAI, Azure OpenAI |
| Asia-Pacific | Alibaba DashScope |
| China | Alibaba DashScope |
| Global | OpenAI |

### By Requirements

**Need best quality?** → OpenAI GPT-4o

**Need lowest cost?** → Alibaba Qwen Flash

**Need fastest speed?** → Groq with Llama

**Need privacy?** → Local models (Ollama)

**Need reliability?** → OpenAI or Azure OpenAI

---

## Cost Optimization

### Model Selection Strategy

```python
from faker_news import LLMClientConfig

# Cost-optimized: use cheapest models
llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Cheap for simple headlines
    model_writing="gpt-4o-mini"     # Still good quality
)

# Quality-optimized: use better model for articles only
llm_config = LLMClientConfig(
    model_headlines="gpt-4o-mini",  # Cheap for headlines
    model_writing="gpt-4o"          # Premium for articles
)
```

### Batch Size Tuning

Larger batches = fewer API calls = lower cost:

```python
from faker_news import NewsProvider

# Cost-optimized setup
provider = NewsProvider(
    fake,
    llm_config=llm_config,
    headline_batch=200,  # Large batches
    article_batch=50
)
```

### Caching Strategy

Maximize cache reuse to minimize API calls:

```python
from faker import Faker
from faker_news import NewsProvider

fake = Faker()
fake.add_provider(NewsProvider(fake))

# Preload once, use many times
fake.news_preload_headlines(1000)

# Reuse content
headlines = [fake.news_headline() for _ in range(500)]
fake.news_reset("reuse")
headlines = [fake.news_headline() for _ in range(500)]  # No new API calls
```

---

## Troubleshooting

### API Key Not Working

1. Verify key format matches provider
2. Check environment variables: `echo $OPENAI_API_KEY`
3. Test with curl:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Connection Errors

1. Verify base URL is correct
2. Check network connectivity
3. Verify API endpoint is accessible
4. Check for firewall/proxy issues

### Rate Limiting

If you hit rate limits:

1. Reduce batch sizes
2. Add delays between generations
3. Upgrade to higher tier
4. Switch to provider with higher limits

### Model Not Found

If you get "model not found" errors:

1. Verify model name is correct
2. Check if you have access to that model
3. For Azure: use deployment name, not model name

---

## Next Steps

- [Configuration](configuration.md) - Customize batch sizes and settings
- [API Reference](api-reference.md) - Complete API documentation
