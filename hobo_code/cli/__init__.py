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


@cli.group()
def github() -> None:
    """Manage GitHub repositories."""
    pass


@github.command("clone")
@click.argument("repo_url", type=str)
@click.argument("path", type=str, required=False)
def github_clone(repo_url: str, path: str | None) -> None:
    """Clone a repository."""
    from hobo_code.github.client import GitHubClient

    try:
        client = GitHubClient()
        target = client.clone(repo_url, path)
        click.echo(f"Cloned to {target}")
    except Exception as e:
        click.echo(f"Error: {e}")


@github.command("status")
def github_status() -> None:
    """Show repository status."""
    from hobo_code.github.client import GitHubClient

    client = GitHubClient()
    info = client.get_repo_info()
    status = client.status()

    click.echo(f"Repository: {info.get('url', 'unknown')}")
    click.echo(f"Branch: {info.get('branch', 'unknown')}")
    click.echo(f"Commit: {info.get('commit', 'unknown')[:8]}")
    click.echo(f"Working tree: {'clean' if status['clean'] else 'dirty'}")


@github.command("branches")
def github_branches() -> None:
    """List branches."""
    from hobo_code.github.client import GitHubClient

    client = GitHubClient()
    branches = client.list_branches()
    current = client.current_branch()

    click.echo("Branches:")
    for b in branches:
        prefix = "*" if b == current else " "
        click.echo(f"  {prefix} {b}")


@cli.group()
def pr() -> None:
    """Manage pull requests."""
    pass


@pr.command("list")
@click.option("--state", default="open", type=click.Choice(["open", "closed", "all"]))
def pr_list(state: str) -> None:
    """List pull requests."""
    from hobo_code.github.pr import PRManager

    manager = PRManager()
    prs = manager.list_prs(state)

    if not prs:
        click.echo("No PRs found.")
        return

    click.echo(f"Pull Requests ({state}):")
    for pr in prs:
        click.echo(f"  #{pr['number']} - {pr['title']} (@{pr['author']})")


@pr.command("view")
@click.argument("pr_number", type=int)
def pr_view(pr_number: int) -> None:
    """View a pull request."""
    from hobo_code.github.pr import PRManager

    manager = PRManager()
    pr = manager.get_pr(pr_number)

    if not pr:
        click.echo(f"PR #{pr_number} not found.")
        return

    click.echo(f"#{pr['number']}: {pr['title']}")
    click.echo(f"Author: {pr['author']}")
    click.echo(f"State: {pr['state']}")
    click.echo(f"URL: {pr['url']}")
    click.echo(f"Files: {len(pr.get('files', []))}")


@pr.command("checkout")
@click.argument("pr_number", type=int)
def pr_checkout(pr_number: int) -> None:
    """Checkout a PR locally."""
    from hobo_code.github.pr import PRManager

    manager = PRManager()
    if manager.checkout_pr(pr_number):
        click.echo(f"Checked out PR #{pr_number}")
    else:
        click.echo(f"Failed to checkout PR #{pr_number}")


@pr.command("diff")
@click.argument("pr_number", type=int)
def pr_diff(pr_number: int) -> None:
    """Show PR diff."""
    from hobo_code.github.pr import PRManager

    manager = PRManager()
    diff = manager.get_pr_diff(pr_number)

    if diff:
        click.echo(diff)
    else:
        click.echo("No diff available.")


@pr.command("merge")
@click.argument("pr_number", type=int)
@click.option("--method", default="merge", type=click.Choice(["merge", "squash", "rebase"]))
def pr_merge(pr_number: int, method: str) -> None:
    """Merge a PR."""
    from hobo_code.github.pr import PRManager

    manager = PRManager()
    if manager.merge_pr(pr_number, method):
        click.echo(f"Merged PR #{pr_number}")
    else:
        click.echo(f"Failed to merge PR #{pr_number}")


@cli.group()
def issue() -> None:
    """Manage issues."""
    pass


@issue.command("list")
@click.option("--state", default="open", type=click.Choice(["open", "closed", "all"]))
def issue_list(state: str) -> None:
    """List issues."""
    from hobo_code.github.issues import IssueManager

    manager = IssueManager()
    issues = manager.list_issues(state)

    if not issues:
        click.echo("No issues found.")
        return

    click.echo(f"Issues ({state}):")
    for iss in issues:
        click.echo(f"  #{iss['number']} - {iss['title']} (@{iss['author']})")


@issue.command("create")
@click.argument("title", type=str)
@click.argument("body", type=str)
@click.option("--label", multiple=True)
def issue_create(title: str, body: str, label: tuple) -> None:
    """Create an issue."""
    from hobo_code.github.issues import IssueManager

    manager = IssueManager()
    result = manager.create_issue(title, body, list(label) if label else None)

    if result:
        click.echo(f"Created issue: {result['url']}")
    else:
        click.echo("Failed to create issue.")


@issue.command("close")
@click.argument("issue_number", type=int)
def issue_close(issue_number: int) -> None:
    """Close an issue."""
    from hobo_code.github.issues import IssueManager

    manager = IssueManager()
    if manager.close_issue(issue_number):
        click.echo(f"Closed issue #{issue_number}")
    else:
        click.echo(f"Failed to close issue #{issue_number}")


@issue.command("view")
@click.argument("issue_number", type=int)
def issue_view(issue_number: int) -> None:
    """View an issue."""
    from hobo_code.github.issues import IssueManager

    manager = IssueManager()
    issue = manager.get_issue(issue_number)

    if not issue:
        click.echo(f"Issue #{issue_number} not found.")
        return

    click.echo(f"#{issue['number']}: {issue['title']}")
    click.echo(f"Author: {issue['author']}")
    click.echo(f"State: {issue['state']}")
    click.echo(f"Labels: {', '.join(issue.get('labels', []))}")


def main():
    """Entry point for the CLI."""
    cli()
