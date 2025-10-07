# Installation

This guide will help you install faker-news and get it running on your system.

## Requirements

- Python 3.9 or higher
- pip or uv package manager
- An API key for an OpenAI-compatible LLM service

## Installation Methods

### Using pip (Standard)

Install the package directly from source:

```bash
pip install -e .
```

For development with testing tools:

```bash
pip install -e ".[dev]"
```

For documentation building:

```bash
pip install -e ".[docs]"
```

### Using uv (Recommended for Development)

If you're using [uv](https://github.com/astral-sh/uv) for faster package management:

```bash
uv pip install -e .
```

## Verifying Installation

After installation, verify that the CLI is available:

```bash
faker-news --help
```

You should see the help menu with all available commands.

## Next Steps

Once installed, you'll need to configure your LLM API key. Continue to:

1. [Setup & Configuration](setup.md) - Configure your API keys
2. [Quick Start](quick-start.md) - Start generating content right away

## Uninstallation

To remove faker-news:

```bash
pip uninstall faker-news
```

!!! note "Cache Files"
    Uninstalling won't remove the SQLite cache file. To completely remove all data:

    ```bash
    # On Linux
    rm ~/.cache/faker-news/cache.sqlite3

    # On macOS
    rm ~/Library/Caches/faker-news/cache.sqlite3

    # On Windows
    del %LOCALAPPDATA%\faker-news\cache\cache.sqlite3
    ```

## Troubleshooting

### Command not found

If `faker-news` command is not found after installation, ensure your Python scripts directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors

If you get import errors when using the library, ensure you installed the package:

```python
pip install -e .
```

### Permission errors

On some systems, you may need to install with `--user`:

```bash
pip install --user -e .
```
