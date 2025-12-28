"""CLI module with Click commands."""

import asyncio
import click


@click.group()
def cli():
    """Hobo Code - Terminal-native AI coding assistant."""
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8765, type=int, help="Port to listen on")
def acp(host: str, port: int) -> None:
    """Start the ACP server for client connections."""
    from hobo_code.server.acp import ACPServer

    async def run_server():
        server = ACPServer(host=host, port=port)
        await server.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await server.stop()

    asyncio.run(run_server())


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8766, type=int, help="Port for headless API server")
def serve(host: str, port: int) -> None:
    """Start headless server mode for API access."""
    click.echo(f"Starting headless server on {host}:{port}")
    click.echo("Headless mode not yet implemented - coming in Phase 1")


@cli.command()
def chat() -> None:
    """Launch the interactive TUI chat interface."""
    from hobo_code.client.app import HoboApp

    app = HoboApp()
    app.run()


@cli.group()
def session() -> None:
    """Manage chat sessions."""
    pass


@session.command("list")
def session_list() -> None:
    """List all chat sessions."""
    from hobo_code.session.manager import SessionManager

    manager = SessionManager()
    sessions = manager.list_sessions()

    if not sessions:
        click.echo("No sessions found.")
        return

    click.echo("Sessions:")
    click.echo("-" * 80)
    for s in sessions:
        title = s.title[:40] if len(s.title) > 40 else s.title
        click.echo(f"{s.id[:8]}... | {title} | {len(s.messages)} messages | {s.updated_at[:10]}")


@session.command("resume")
@click.argument("session_id", type=str)
def session_resume(session_id: str) -> None:
    """Resume a specific session in the TUI."""
    from hobo_code.client.app import HoboApp

    app = HoboApp(session_id=session_id)
    app.run()


@session.command("delete")
@click.argument("session_id", type=str)
def session_delete(session_id: str) -> None:
    """Delete a session."""
    from hobo_code.session.manager import SessionManager

    manager = SessionManager()
    if manager.delete_session(session_id):
        click.echo(f"Session {session_id} deleted.")
    else:
        click.echo(f"Session {session_id} not found.")


@cli.command()
def stats() -> None:
    """Show usage statistics."""
    from hobo_code.session.manager import SessionManager

    manager = SessionManager()
    stats = manager.get_stats()

    click.echo("Hobo Code Statistics")
    click.echo("-" * 40)
    click.echo(f"Total Sessions: {stats['total_sessions']}")
    click.echo(f"Total Messages: {stats['total_messages']}")
    click.echo(f"Total Tokens: {stats['total_tokens']}")
    click.echo(f"Estimated Cost: ${stats['total_cost_estimate']:.4f}")


@cli.group()
def auth() -> None:
    """Manage API credentials."""
    pass


@auth.command("set")
@click.argument("provider", type=str)
@click.argument("key", type=str)
def auth_set(provider: str, key: str) -> None:
    """Set an API key for a provider."""
    from hobo_code.auth.credentials import CredentialStore

    store = CredentialStore()
    if store.save_key(provider, key):
        click.echo(f"API key saved for {provider}")
    else:
        click.echo("Failed to save API key")


@auth.command("list")
def auth_list() -> None:
    """List configured providers."""
    from hobo_code.auth.credentials import CredentialStore

    store = CredentialStore()
    providers = store.list_providers()

    if not providers:
        click.echo("No API keys configured.")
        return

    click.echo("Configured providers:")
    for p in providers:
        click.echo(f"  - {p}")


@auth.command("delete")
@click.argument("provider", type=str)
def auth_delete(provider: str) -> None:
    """Delete an API key for a provider."""
    from hobo_code.auth.credentials import CredentialStore

    store = CredentialStore()
    if store.delete_key(provider):
        click.echo(f"API key deleted for {provider}")
    else:
        click.echo(f"No API key found for {provider}")


@auth.command("github")
@click.argument("token", type=str)
def auth_github(token: str) -> None:
    """Set GitHub token."""
    from hobo_code.auth.credentials import CredentialStore

    store = CredentialStore()
    if store.save_github_token(token):
        click.echo("GitHub token saved")
    else:
        click.echo("Failed to save GitHub token")


@cli.group()
def models() -> None:
    """Manage model providers."""
    pass


@models.command("list")
@click.argument("provider", type=str, required=False)
def models_list(provider: str | None) -> None:
    """List available models."""
    from hobo_code.models.provider import ModelProvider

    mp = ModelProvider()
    if provider:
        models = mp.list_models(provider)
        click.echo(f"Models for {provider}:")
        for m in models:
            click.echo(f"  - {m}")
    else:
        providers = mp.list_providers()
        click.echo("Available providers:")
        for p in providers:
            click.echo(f"  - {p}")


@models.command("info")
@click.argument("model", type=str)
def models_info(model: str) -> None:
    """Show model information."""
    from hobo_code.models.provider import ModelProvider

    mp = ModelProvider()
    info = mp.get_model_info(model)

    click.echo(f"Model: {info['model']}")
    click.echo(f"Provider: {info['provider']}")
    click.echo(f"Cost per 1K tokens: ${info['cost_per_1k_tokens']:.4f}")
    click.echo(f"Context window: {info['context_window']} tokens")
    click.echo(f"Max output: {info['max_output_tokens']} tokens")


@cli.group()
def skills() -> None:
    """Manage AI skills."""
    pass


@skills.command("list")
def skills_list() -> None:
    """List available skills."""
    from hobo_code.skills.registry import SkillRegistry

    registry = SkillRegistry()
    skills = registry.list_skills()

    if not skills:
        click.echo("No skills found.")
        return

    click.echo("Available skills:")
    for s in skills:
        skill = registry.get_skill(s)
        if skill:
            desc = skill.description[:50] if len(skill.description) > 50 else skill.description
            click.echo(f"  - {s}: {desc}")


@skills.command("recommend")
@click.argument("task", type=str)
def skills_recommend(task: str) -> None:
    """Get skill recommendations for a task."""
    from hobo_code.skills.registry import SkillRegistry

    registry = SkillRegistry()
    recommendations = registry.get_recommended_skills(task)

    if not recommendations:
        click.echo("No matching skills found.")
        return

    click.echo(f"Skills matching '{task}':")
    for skill, score in recommendations[:5]:
        click.echo(f"  - {skill.name}: {score:.2f}")


def main():
    """Entry point for the CLI."""
    cli()
