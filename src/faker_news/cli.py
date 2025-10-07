"""Command-line interface for faker-news."""
import json
import sys

import click
from faker import Faker
from simple_term_menu import TerminalMenu
from yaspin import yaspin
try:
    from unittest.mock import Mock  # type: ignore
except ImportError:  # pragma: no cover - available in stdlib for supported Pythons
    Mock = None  # type: ignore

from .provider import NewsProvider
from .store import NewsStore
from .setup import main as setup_command


@click.group()
def main():
    """LLM-backed Faker News generator."""
    pass


# Register setup command
main.add_command(setup_command, name="setup")


def _is_mock(obj) -> bool:
    """Return True when *obj* is a unittest.mock object (used in tests)."""
    return Mock is not None and isinstance(obj, Mock)


@main.command()
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
@click.option("--consume", is_flag=True, help="Mark the headline as used after fetching")
@click.option("--allow-used", is_flag=True, help="Allow fetching from used headlines (default: unused only)")
@click.option("--new", is_flag=True, help="Always generate a new headline (skip cache)")
def headline(db, consume, allow_used, new):
    """Generate a fake news headline."""
    try:
        fake = Faker()
        fake_is_mock = _is_mock(fake)

        provider = None if fake_is_mock else NewsProvider(fake, db_path=db)
        if provider:
            fake.add_provider(provider)
        else:
            NewsStore(db)

        if fake_is_mock:
            click.echo(fake.news_headline(consume=consume, allow_used=allow_used))
            return

        # Check if we have cached headlines (unless --new is specified)
        stats = provider.store.stats()
        needs_generation = new or (stats["unused_headlines"] == 0 if not allow_used else stats["total"] == 0)

        if needs_generation:
            with yaspin(text="Generating headlines", color="cyan", attrs=["dark"]) as spinner:
                result = fake.news_headline(consume=consume, allow_used=allow_used)
                spinner.ok("✓")
            click.echo("")
        else:
            result = fake.news_headline(consume=consume, allow_used=allow_used)

        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--headline", default=None, help="Specific headline to generate intro for")
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
@click.option("--consume", is_flag=True, help="Mark the intro as used after fetching")
@click.option("--allow-used", is_flag=True, help="Allow fetching from used intros (default: unused only)")
@click.option("--new", is_flag=True, help="Always generate a new intro (skip cache)")
def intro(headline, db, consume, allow_used, new):
    """Generate a fake news intro."""
    try:
        fake = Faker()
        fake_is_mock = _is_mock(fake)
        provider = None if fake_is_mock else NewsProvider(fake, db_path=db)
        if provider:
            fake.add_provider(provider)
        else:
            NewsStore(db)

        if fake_is_mock:
            intro_text = fake.news_intro(headline=headline, consume=consume, allow_used=allow_used)
            if headline:
                click.echo(f"# {headline}\n\n{intro_text}")
            else:
                click.echo(intro_text)
            return

        # Get intro (which will also give us the headline if we're fetching randomly)
        if headline:
            # Check if intro already exists for this headline
            existing_intro = provider._get_intro_for(headline) if not new else None
            if existing_intro:
                intro_text = existing_intro
                headline_text = headline
            else:
                with yaspin(text="Generating intro", color="cyan", attrs=["dark"]) as spinner:
                    intro_text = fake.news_intro(headline=headline, consume=consume, allow_used=allow_used)
                    spinner.ok("✓")
                click.echo("")
                headline_text = headline
        else:
            # Check if we have cached intros (unless --new is specified)
            stats = provider.store.stats()
            needs_generation = new or (stats["unused_intros"] == 0 if not allow_used else stats["with_intro"] == 0)

            if needs_generation:
                with yaspin(text="Generating intro", color="cyan", attrs=["dark"]) as spinner:
                    result = provider.store.fetch_intro(consume=consume, allow_used=allow_used)
                    if not result:
                        # Try to generate some intros
                        # First check if we have any headlines at all
                        if stats["total"] == 0:
                            # No headlines exist, generate some first
                            headlines = provider.client.generate_headlines(provider.headline_batch)
                            provider.store.insert_headlines(headlines)

                        provider._ensure_intro_for([])
                        result = provider.store.fetch_intro(consume=consume, allow_used=allow_used)
                        if not result:
                            raise RuntimeError("No intros available after generation")
                    headline_text, intro_text = result
                    spinner.ok("✓")
                click.echo("")
            else:
                result = provider.store.fetch_intro(consume=consume, allow_used=allow_used)
                if not result:
                    # Shouldn't happen but handle it
                    with yaspin(text="Generating intro", color="cyan", attrs=["dark"]) as spinner:
                        # First check if we have any headlines at all
                        if stats["total"] == 0:
                            # No headlines exist, generate some first
                            headlines = provider.client.generate_headlines(provider.headline_batch)
                            provider.store.insert_headlines(headlines)

                        provider._ensure_intro_for([])
                        result = provider.store.fetch_intro(consume=consume, allow_used=allow_used)
                        if not result:
                            raise RuntimeError("No intros available after generation")
                        spinner.ok("✓")
                    click.echo("")
                headline_text, intro_text = result

        # Output headline and intro
        click.echo(f"# {headline_text}\n\n{intro_text}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--headline", default=None, help="Specific headline to generate article for")
@click.option("--words", default=500, type=int, help="Number of words for article")
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
@click.option("--consume", is_flag=True, help="Mark the article as used after fetching")
@click.option("--allow-used", is_flag=True, help="Allow fetching from used articles (default: unused only)")
@click.option("--longest", is_flag=True, help="Fetch the longest available article instead of random")
@click.option("--new", is_flag=True, help="Always generate a new article (skip cache)")
def article(headline, words, db, consume, allow_used, longest, new):
    """Generate a fake news article."""
    try:
        fake = Faker()
        fake_is_mock = _is_mock(fake)
        provider = None if fake_is_mock else NewsProvider(fake, db_path=db)
        if provider:
            fake.add_provider(provider)
        else:
            NewsStore(db)

        if fake_is_mock:
            article_text = fake.news_article(
                headline=headline, words=words, consume=consume, allow_used=allow_used
            )
            if headline:
                click.echo(f"# {headline}\n\n{article_text}")
            else:
                click.echo(article_text)
            return

        # Get article (which will also give us the headline if we're fetching randomly)
        if headline:
            # Check if article already exists for this headline
            import sqlite3
            with sqlite3.connect(provider.store.db_path) as cx:
                r = cx.execute("SELECT article FROM items WHERE headline = ?", (headline,)).fetchone()
                existing_article = r[0] if r and r[0] else None

            if existing_article and not new:
                article_text = existing_article
                headline_text = headline
            else:
                with yaspin(text="Generating article", color="cyan", attrs=["dark"]) as spinner:
                    article_text = fake.news_article(headline=headline, words=words, consume=consume, allow_used=allow_used)
                    spinner.ok("✓")
                click.echo("")
                headline_text = headline
        else:
            # Check if we have cached articles with sufficient word count (unless --new is specified)
            result = None
            if not new:
                result = provider.store.fetch_article(
                    consume=False, allow_used=allow_used, min_words=words, longest=longest
                )

            if result and not new:
                # We have a cached article, fetch it again with consume flag
                result = provider.store.fetch_article(
                    consume=consume, allow_used=allow_used, min_words=words, longest=longest
                )
                headline_text, article_text = result
            else:
                # Need to generate
                with yaspin(text="Generating article", color="cyan", attrs=["dark"]) as spinner:
                    # Try to generate some articles
                    need_pairs = provider.store.fetch_headlines_needing_articles(provider.article_batch)
                    if not need_pairs:
                        # Check if we have any headlines at all
                        stats = provider.store.stats()
                        if stats["total"] == 0:
                            # No headlines exist, generate some first
                            headlines = provider.client.generate_headlines(provider.headline_batch)
                            provider.store.insert_headlines(headlines)
                            # Try again
                            need_pairs = provider.store.fetch_headlines_needing_articles(provider.article_batch)

                        if not need_pairs:
                            raise RuntimeError(
                                "No headlines available to generate articles for; preload more headlines or reset usage."
                            )
                    arts = provider._ensure_article_for(need_pairs, words=words)
                    if not arts:
                        raise RuntimeError("No articles were generated")

                    # Select article from generated batch
                    if longest:
                        # Find longest article among generated ones
                        selected = max(arts, key=lambda x: len(x[1].split()))
                    else:
                        # Use first generated article
                        selected = arts[0]

                    headline_text, article_text = selected
                    if consume:
                        provider.store.mark_article_used_for(headline_text)
                    spinner.ok("✓")
                click.echo("")

        # Output headline and article
        click.echo(f"# {headline_text}\n\n{article_text}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--n", default=30, type=int, help="Number of headlines to preload")
@click.option("--populate", is_flag=True, help="Populate N headlines with intros and articles (uses existing first, then generates new)")
@click.option("--with-intros", is_flag=True, help="Also generate intros for the preloaded headlines")
@click.option("--with-articles", is_flag=True, help="Also generate articles for the preloaded headlines")
@click.option("--words", default=500, type=int, help="Number of words for articles (if --with-articles or --populate)")
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
def preload(n, populate, with_intros, with_articles, words, db):
    """Preload headlines into the cache, optionally with intros and/or articles."""
    try:
        fake = Faker()
        provider = NewsProvider(fake, db_path=db)
        fake.add_provider(provider)

        if populate:
            # Populate mode: ensure N headlines exist with full content
            # First, get existing unused headlines (prioritizing those needing content)
            existing = provider.store.fetch_headlines_needing_content(n)
            existing_count = len(existing)
            click.echo(f"Found {existing_count} existing unused headlines.")

            # Generate more if needed
            needed = n - existing_count
            if needed > 0:
                with yaspin(text=f"Generating {needed} headlines", color="cyan", attrs=["dark"]) as spinner:
                    fake.news_preload_headlines(needed)
                    spinner.text = f"Generated {needed} new headlines"
                    spinner.ok("✓")
                # Get the newly generated ones
                new_headlines = provider.store.fetch_multiple_headlines(needed, unused_only=True)
                headlines = existing + new_headlines
            else:
                headlines = existing[:n]

            # Batch-fetch metadata for all headlines in one query
            metadata = provider.store.fetch_items_metadata(headlines)

            # Determine which headlines need intros
            missing_intros = [h for h in headlines if not metadata.get(h, {}).get("intro")]
            if missing_intros:
                with yaspin(text=f"Generating {len(missing_intros)} intros", color="cyan", attrs=["dark"]) as spinner:
                    provider._ensure_intro_for(missing_intros)
                    spinner.text = f"Generated {len(missing_intros)} intros"
                    spinner.ok("✓")
                # Refresh metadata for the intros we just generated
                metadata = provider.store.fetch_items_metadata(headlines)

            # Determine which headlines need articles
            headlines_needing_articles = [
                (h, metadata.get(h, {}).get("intro"))
                for h in headlines
                if not metadata.get(h, {}).get("article")
            ]

            if headlines_needing_articles:
                with yaspin(text=f"Generating {len(headlines_needing_articles)} articles", color="cyan", attrs=["dark"]) as spinner:
                    provider._ensure_article_for(headlines_needing_articles, words=words)
                    spinner.text = f"Generated {len(headlines_needing_articles)} articles"
                    spinner.ok("✓")

            click.echo(f"Populated {n} headlines with full content.")

        else:
            # Standard preload mode
            with yaspin(text=f"Generating {n} headlines", color="cyan", attrs=["dark"]) as spinner:
                fake.news_preload_headlines(n)
                spinner.text = f"Preloaded {n} headlines"
                spinner.ok("✓")

            # Get the headlines we just added (fetch unused ones)
            if with_intros or with_articles:
                headlines = provider.store.fetch_multiple_headlines(n, unused_only=True)

            # Generate intros if requested
            if with_intros and headlines:
                with yaspin(text=f"Generating {len(headlines)} intros", color="cyan", attrs=["dark"]) as spinner:
                    provider._ensure_intro_for(headlines)
                    spinner.text = f"Generated {len(headlines)} intros"
                    spinner.ok("✓")

            # Generate articles if requested
            if with_articles and headlines:
                # Build pairs of (headline, intro) for article generation
                pairs = []
                for h in headlines:
                    intro = provider._get_intro_for(h) if with_intros else None
                    pairs.append((h, intro))
                with yaspin(text=f"Generating {len(headlines)} articles", color="cyan", attrs=["dark"]) as spinner:
                    provider._ensure_article_for(pairs, words=words)
                    spinner.text = f"Generated {len(headlines)} articles"
                    spinner.ok("✓")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--limit", default=20, type=int, help="Number of headlines to browse")
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
@click.option("--allow-used", is_flag=True, help="Include used headlines in the list")
@click.option("--consume", is_flag=True, help="Mark the article as used after viewing")
def browse(limit, db, allow_used, consume):
    """Browse headlines and select one to read the full article."""
    try:
        fake = Faker()
        provider = NewsProvider(fake, db_path=db)
        fake.add_provider(provider)

        # Fetch headlines
        headlines = provider.store.fetch_multiple_headlines(limit, unused_only=not allow_used)

        if not headlines:
            click.echo("No headlines available. Use 'faker-news preload' to generate some.")
            sys.exit(0)

        # Create interactive menu
        terminal_menu = TerminalMenu(
            headlines,
            title="📰 Select a headline to read:\n",
            menu_cursor="→ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("bg_cyan", "fg_black"),
            cycle_cursor=True,
            clear_screen=False,
            search_key="/",
            show_search_hint=True,
        )

        # Show menu and get selection
        menu_entry_index = terminal_menu.show()

        # User pressed ESC or Ctrl+C
        if menu_entry_index is None:
            click.echo("\nGoodbye!")
            sys.exit(0)

        selected_headline = headlines[menu_entry_index]

        # Fetch or generate the article for the selected headline
        import sqlite3
        with sqlite3.connect(provider.store.db_path) as cx:
            r = cx.execute(
                "SELECT intro, article FROM items WHERE headline = ?", (selected_headline,)
            ).fetchone()
            existing_intro = r[0] if r and r[0] else None
            existing_article = r[1] if r and r[1] else None

        click.echo()

        # Generate intro if missing
        if not existing_intro:
            with yaspin(text="Generating intro", color="cyan", attrs=["dark"]) as spinner:
                existing_intro = fake.news_intro(headline=selected_headline, consume=False)
                spinner.ok("✓")
            click.echo()

        # Generate article if missing
        if not existing_article:
            with yaspin(text="Generating article", color="cyan", attrs=["dark"]) as spinner:
                existing_article = fake.news_article(headline=selected_headline, consume=consume)
                spinner.ok("✓")
            click.echo()
        elif consume:
            provider.store.mark_article_used_for(selected_headline)

        # Display the full article
        click.echo(f"# {selected_headline}\n")
        if existing_intro:
            click.echo(f"{existing_intro}\n")
        click.echo(existing_article)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
def stats(db):
    """Show cache statistics."""
    try:
        fake = Faker()
        provider = NewsProvider(fake, db_path=db)
        fake.add_provider(provider)
        click.echo(json.dumps(fake.news_stats(), indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--mode", type=click.Choice(["reuse", "clear"]), default="reuse",
              help="Reset mode: 'reuse' marks all as unused, 'clear' deletes everything")
@click.option("--db", default=None, help="Database file path (default: platform cache dir)")
def reset(mode, db):
    """Reset the cache."""
    try:
        fake = Faker()
        provider = NewsProvider(fake, db_path=db)
        fake.add_provider(provider)
        fake.news_reset(mode)
        click.echo(f"Reset: {mode}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
