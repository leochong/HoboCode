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


def main():
    """Entry point for the CLI."""
    cli()
