# CLI Reference

Complete reference for the faker-news command-line interface.

## Global Options

All commands support these global options:

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--db PATH` | Custom database file path |

## Commands

### setup

Interactive setup wizard for configuring API keys.

```bash
faker-news setup
```

**What it does:**

1. Checks for existing API keys (keyring and environment)
2. Guides you through provider selection
3. Securely stores your API key in system keyring
4. Tests the connection with a sample generation
5. Confirms everything works

**Example:**

```bash
$ faker-news setup
Checking for API keys...
✓ Found API key in keyring

Testing connection...
✓ Successfully generated test headline

Your setup is complete!
```

---

### headline

Generate a fake news headline.

```bash
faker-news headline [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--consume` | Mark the headline as used | `False` |
| `--allow-used` | Fetch from all items (used or unused) | `False` |
| `--new` | Always generate a new headline (skip cache) | `False` |
| `--db PATH` | Custom database path | Platform default |

**Examples:**

```bash
# Generate a headline (can repeat)
faker-news headline

# Generate and mark as used
faker-news headline --consume

# Always generate a fresh headline
faker-news headline --new

# Generate multiple variations
faker-news headline --new  # First variation
faker-news headline --new  # Different variation

# Fetch from all items (including used ones)
faker-news headline --allow-used

# Use custom database
faker-news headline --db /tmp/cache.sqlite3
```

---

### intro

Generate a fake news article introduction.

```bash
faker-news intro [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--headline TEXT` | Specific headline to use | Auto-generated |
| `--consume` | Mark the intro as used | `False` |
| `--allow-used` | Fetch from all items | `False` |
| `--new` | Always generate a new intro (skip cache) | `False` |
| `--db PATH` | Custom database path | Platform default |

**Examples:**

```bash
# Generate an intro (with auto-generated headline)
faker-news intro

# Generate intro for specific headline
faker-news intro --headline "Scientists Make Breakthrough Discovery"

# Always generate a fresh intro
faker-news intro --new

# Generate new intro for existing headline
faker-news intro --headline "Breaking News" --new

# Generate and consume
faker-news intro --consume

# Use with custom headline and consume
faker-news intro --headline "Breaking News" --consume
```

---

### article

Generate a complete fake news article with markdown formatting.

```bash
faker-news article [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--headline TEXT` | Specific headline to use | Auto-generated |
| `--words INT` | Target article length in words | `500` |
| `--consume` | Mark the article as used | `False` |
| `--allow-used` | Fetch from all items | `False` |
| `--longest` | Fetch the longest available article | `False` |
| `--new` | Always generate a new article (skip cache) | `False` |
| `--db PATH` | Custom database path | Platform default |

**Examples:**

```bash
# Generate a ~500 word article
faker-news article

# Generate a longer article
faker-news article --words 1000

# Always generate a fresh article
faker-news article --new

# Generate multiple variations
faker-news article --new --words 800  # First variation
faker-news article --new --words 800  # Different variation

# Generate for specific headline
faker-news article --headline "Tech Giant Announces New Product"

# Generate new article for existing headline
faker-news article --headline "Tech Giant Announces New Product" --new

# Generate, consume, and use custom length
faker-news article --words 800 --consume

# Fetch from any item (including used)
faker-news article --allow-used

# Get the longest available article
faker-news article --longest
```

---

### preload

Preload the cache with headlines and optionally full content.

```bash
faker-news preload [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--n INT` | Number of headlines to generate | Required |
| `--with-intros` | Also generate intros | `False` |
| `--with-articles` | Also generate articles | `False` |
| `--words INT` | Article length (if generating) | `500` |
| `--populate` | Smart populate mode | `False` |
| `--db PATH` | Custom database path | Platform default |

**Modes:**

=== "Basic Preload"

    Generate N new headlines only:

    ```bash
    faker-news preload --n 50
    ```

=== "Preload with Content"

    Generate N new headlines with full content:

    ```bash
    faker-news preload --n 50 --with-intros --with-articles
    ```

=== "Populate Mode"

    Ensure N unused headlines exist with full content (smart mode):

    ```bash
    faker-news preload --n 50 --populate
    ```

    This mode:

    - Prioritizes unused headlines missing intros/articles
    - Uses existing complete unused headlines if available
    - Generates new headlines only if needed
    - Minimizes API calls

**Examples:**

```bash
# Generate 100 headlines
faker-news preload --n 100

# Generate 50 complete articles
faker-news preload --n 50 --with-intros --with-articles

# Generate longer articles
faker-news preload --n 20 --with-articles --words 1000

# Smart populate: ensure 50 ready-to-use articles exist
faker-news preload --n 50 --populate

# Populate with custom article length
faker-news preload --n 50 --populate --words 800
```

---

### stats

Display cache statistics.

```bash
faker-news stats [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--db PATH` | Custom database path | Platform default |

**Example:**

```bash
$ faker-news stats
Cache Statistics:
  Total items: 150
  With intros: 75
  With articles: 50
  Unused headlines: 100
  Unused intros: 60
  Unused articles: 40
```

---

### reset

Reset usage flags or clear the cache entirely.

```bash
faker-news reset [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--mode MODE` | Reset mode: `reuse` or `clear` | Required |
| `--db PATH` | Custom database path | Platform default |

**Modes:**

=== "Reuse"

    Mark all items as unused (keep content):

    ```bash
    faker-news reset --mode reuse
    ```

    This marks all headlines, intros, and articles as "unused" so they can be fetched again. The content remains in the cache.

=== "Clear"

    Delete all cached content:

    ```bash
    faker-news reset --mode clear
    ```

    This completely empties the cache database. Next fetch will trigger new generation.

**Examples:**

```bash
# Mark all items as unused
faker-news reset --mode reuse

# Clear all content
faker-news reset --mode clear

# Reuse with custom database
faker-news reset --mode reuse --db /tmp/cache.sqlite3
```

---

## Common Workflows

### First-Time Setup

```bash
# 1. Run interactive setup
faker-news setup

# 2. Preload content for better performance
faker-news preload --n 100

# 3. Check what's cached
faker-news stats
```

### Generate Complete Articles

```bash
# Ensure cache is populated
faker-news preload --n 50 --populate

# Generate a complete article
headline=$(faker-news headline --consume)
faker-news intro --headline "$headline" --consume
faker-news article --headline "$headline" --consume
```

### Testing Without Consuming

```bash
# View content without marking as used
faker-news headline
faker-news intro
faker-news article

# Same command can be run multiple times
faker-news headline  # Might show same headline
faker-news headline  # Might show same headline
```

### Generating Multiple Variations

Use the `--new` flag to generate fresh content every time, bypassing the cache:

```bash
# Generate 5 different headlines
for i in {1..5}; do
  faker-news headline --new
done

# Generate 3 different article variations for testing
faker-news article --new --words 500 > article1.txt
faker-news article --new --words 500 > article2.txt
faker-news article --new --words 500 > article3.txt

# Create multiple intros for the same headline
headline="Breaking: Scientists Discover New Planet"
faker-news intro --headline "$headline" --new > intro1.txt
faker-news intro --headline "$headline" --new > intro2.txt
faker-news intro --headline "$headline" --new > intro3.txt
```

### Batch Generation Script

```bash
#!/bin/bash
# Generate 20 complete articles

faker-news preload --n 20 --populate

for i in {1..20}; do
  headline=$(faker-news headline --consume)
  intro=$(faker-news intro --headline "$headline" --consume)
  article=$(faker-news article --headline "$headline" --consume)

  echo "===== Article $i ====="
  echo "$headline"
  echo ""
  echo "$intro"
  echo ""
  echo "$article"
  echo ""
  echo ""
done
```

### Reset and Start Fresh

```bash
# Option 1: Reuse existing content
faker-news reset --mode reuse
faker-news stats  # All items now unused

# Option 2: Clear everything and start over
faker-news reset --mode clear
faker-news preload --n 50 --populate
faker-news stats
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (API error, missing config, etc.) |
| `2` | Invalid arguments |

## Using with Scripts

The CLI outputs only the generated content to stdout, making it easy to use in scripts:

```bash
# Capture output
headline=$(faker-news headline)
echo "Generated: $headline"

# Use in loops
for i in {1..5}; do
  faker-news headline
done

# Redirect to file
faker-news article --words 1000 > article.txt
```

## Next Steps

- [Cache Management](cache-management.md) - Advanced cache management strategies
- [Library Usage](library-usage.md) - Use faker-news in Python
- [Configuration](configuration.md) - Customize behavior
