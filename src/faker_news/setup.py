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
        click.echo("API keys will be stored securely in your system keyring:")
        click.echo("  • macOS: Keychain")
        click.echo("  • Windows: Credential Manager")
        click.echo("  • Linux: Secret Service (GNOME Keyring/KWallet)")
        click.echo()

        if click.confirm("Would you like to set an API key now?"):
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

    click.echo()
    click.secho("=" * 50, fg="cyan")
    click.secho("Setup Complete!", fg="green", bold=True)
    click.secho("=" * 50, fg="cyan")
    click.echo()

    if api_key_found:
        click.echo("Quick test:")
        click.secho("  faker-news headline", fg="cyan")
        click.echo()

        if click.confirm("Would you like to test it now?"):
            click.echo()
            click.echo("Generating a test headline...")
            try:
                from faker import Faker
                from .provider import NewsProvider

                fake = Faker()
                provider = NewsProvider(fake)
                fake.add_provider(provider)
                headline = fake.news_headline()

                click.echo()
                click.secho("Success! Generated headline:", fg="green", bold=True)
                click.secho(f"  {headline}", fg="yellow")
                click.echo()
            except Exception as e:
                click.secho(f"✗ Test failed: {e}", fg="red")
                click.echo()
                click.echo("Please check your API key and try again.")

    click.echo("For more usage examples, see README.md")
    click.echo()


if __name__ == "__main__":
    main()
