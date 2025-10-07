"""Setup script for faker-news."""
import os

import click
import keyring


SERVICE_NAME = "faker-news"


@click.command()
def main():
    """Interactive setup for API key configuration and testing."""

    click.secho("=" * 50, fg="cyan")
    click.secho("faker-news Setup", fg="cyan", bold=True)
    click.secho("=" * 50, fg="cyan")
    click.echo()

    # Check for API keys in keyring and environment
    click.echo("Checking for API keys...")
    api_key_found = False

    # Check keyring
    if keyring.get_password(SERVICE_NAME, "openai"):
        click.secho("✓ OpenAI API key found in system keyring", fg="green")
        api_key_found = True

    if keyring.get_password(SERVICE_NAME, "dashscope"):
        click.secho("✓ DashScope API key found in system keyring", fg="green")
        api_key_found = True

    # Check environment variables
    if os.getenv("OPENAI_API_KEY"):
        click.secho("✓ OPENAI_API_KEY found in environment", fg="green")
        api_key_found = True

    if os.getenv("DASHSCOPE_API_KEY"):
        click.secho("✓ DASHSCOPE_API_KEY found in environment", fg="green")
        api_key_found = True

    if not api_key_found:
        click.echo()
        click.secho("⚠ No API key found.", fg="yellow")
        click.echo()
        click.echo("You have two options:")
        click.echo()
        click.echo("1. Configure an API key for live generation")
        click.echo("   API keys will be stored securely in your system keyring:")
        click.echo("   • macOS: Keychain")
        click.echo("   • Windows: Credential Manager")
        click.echo("   • Linux: Secret Service (GNOME Keyring/KWallet)")
        click.echo()
        click.echo("2. Load example data (100 pre-generated articles)")
        click.echo("   Try the package without an API key")
        click.echo()

        choice = click.prompt(
            "What would you like to do?",
            type=click.Choice(["1", "2"], case_sensitive=False),
            default="2",
        )

        if choice == "1":
            provider = click.prompt(
                "Which provider?",
                type=click.Choice(["openai", "dashscope"], case_sensitive=False),
                default="openai",
            )
            api_key = click.prompt(f"Enter your {provider.upper()} API key", hide_input=True)

            # Store in system keyring
            try:
                keyring.set_password(SERVICE_NAME, provider.lower(), api_key)
                click.echo()
                click.secho(f"✓ {provider.upper()} API key saved to system keyring", fg="green")
                click.echo()
                api_key_found = True
            except Exception as e:
                click.secho(f"✗ Failed to save to keyring: {e}", fg="red")
                click.echo()
                click.echo("You can set it via environment variable instead:")
                if provider.lower() == "openai":
                    click.secho("  export OPENAI_API_KEY='your-key'", fg="cyan")
                else:
                    click.secho("  export DASHSCOPE_API_KEY='your-key'", fg="cyan")
        else:
            # Load example data
            click.echo()
            click.echo("Loading example data...")
            try:
                from .store import NewsStore

                store = NewsStore()
                loaded = store.load_example_data()
                click.echo()
                click.secho(f"✓ Loaded {loaded} example articles", fg="green")
                click.echo()
            except Exception as e:
                click.secho(f"✗ Failed to load example data: {e}", fg="red")
                click.echo()

    click.echo()
    click.secho("=" * 50, fg="cyan")
    click.secho("Setup Complete!", fg="green", bold=True)
    click.secho("=" * 50, fg="cyan")
    click.echo()

    # Offer to test regardless of whether API key is configured
    click.echo("Quick test:")
    click.secho("  faker-news headline", fg="cyan")
    click.echo()

    if click.confirm("Would you like to test it now?"):
        click.echo()
        click.echo("Fetching a headline...")
        try:
            from faker import Faker
            from .provider import NewsProvider

            fake = Faker()
            provider = NewsProvider(fake)
            fake.add_provider(provider)
            headline = fake.news_headline(consume=False)

            click.echo()
            click.secho("Success! Got headline:", fg="green", bold=True)
            click.secho(f"  {headline}", fg="yellow")
            click.echo()
        except Exception as e:
            click.secho(f"✗ Test failed: {e}", fg="red")
            click.echo()
            if not api_key_found:
                click.echo("You can load example data or configure an API key to try again.")
            else:
                click.echo("Please check your API key and try again.")

    click.echo("For more usage examples, see README.md")
    click.echo()


if __name__ == "__main__":
    main()
