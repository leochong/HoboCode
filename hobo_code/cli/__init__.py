"""CLI module with Click commands."""

import asyncio
import click
import threading
import time
from hobo_code.server.acp import ACPServer


def _check_credentials() -> bool:
    """Check if API credentials are configured."""
    try:
        from hobo_code.auth.credentials import CredentialStore

        store = CredentialStore()
        providers = store.list_providers()
        return len(providers) > 0
    except Exception:
        return False


def _start_embedded_server(
    host: str = "127.0.0.1", port: int = 8765
) -> tuple[threading.Thread, int]:
    """Start the ACP server in a background thread and return (thread, port)."""
    server = ACPServer(host=host, port=port)

    async def run_server():
        await server.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await server.stop()

    thread = threading.Thread(target=lambda: asyncio.run(run_server()), daemon=True)
    thread.start()
    time.sleep(0.5)  # Give server time to start
    return thread, port


@click.group(invoke_without_command=True)
@click.option("--server", is_flag=True, help="Start with embedded server (default)")
@click.option("--no-server", is_flag=True, help="Start without embedded server")
@click.pass_context
def cli(ctx: click.Context, server: bool, no_server: bool) -> None:
    """Hobo Code - Terminal-native AI coding assistant."""
    ctx.ensure_object(dict)
    ctx.obj["start_server"] = not no_server and not server

    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def chat(ctx: click.Context, args: tuple) -> None:
    """Launch the interactive TUI chat interface."""
    from hobo_code.client.app import HoboApp
    from hobo_code.auth.credentials import CredentialStore

    store = CredentialStore()
    providers = store.list_providers()

    if not providers:
        click.echo("Welcome to Hobo Code!")
        click.echo("-" * 40)
        click.echo("No API keys configured. Let's set up your LLM provider.")
        click.echo("")
        click.echo("Available providers: openai, anthropic, google, deepseek, mistral, etc.")
        provider = click.prompt("Enter provider name", type=str, default="openai")
        api_key = click.prompt(f"Enter API key for {provider}", type=str, hide_input=True)

        if store.save_key(provider, api_key):
            click.echo(f"API key saved for {provider}")
        else:
            click.echo("Failed to save API key")
            return

    start_server = ctx.obj.get("start_server", True)

    if start_server:
        click.echo("Starting embedded server...")
        _start_embedded_server()

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
def config() -> None:
    """Manage user configuration."""
    pass


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    from hobo_code.auth.preferences import UserPreferences

    prefs = UserPreferences()
    click.echo("Hobo Code Configuration")
    click.echo("-" * 40)
    click.echo("Auto-Switch:")
    click.echo(f"  enabled: {prefs.auto_switch_enabled}")
    click.echo(f"  min_confidence: {prefs.min_confidence}")
    click.echo(f"  debounce_seconds: {prefs.debounce_seconds}")
    click.echo(f"  show_notifications: {prefs.show_notifications}")
    click.echo(f"  locked_skill: {prefs.locked_skill or '(none)'}")


@config.command("auto-switch")
@click.argument("state", type=click.Choice(["on", "off"]))
def config_auto_switch(state: str) -> None:
    """Enable or disable auto-switching of skills."""
    from hobo_code.auth.preferences import UserPreferences

    prefs = UserPreferences()
    prefs.auto_switch_enabled = state == "on"
    click.echo(f"Auto-switch {'enabled' if prefs.auto_switch_enabled else 'disabled'}")


@config.command("min-confidence")
@click.argument("value", type=float)
def config_min_confidence(value: float) -> None:
    """Set minimum confidence threshold for auto-switching (0.0-1.0)."""
    if not 0.0 <= value <= 1.0:
        click.echo("Error: value must be between 0.0 and 1.0")
        return

    from hobo_code.auth.preferences import UserPreferences

    prefs = UserPreferences()
    prefs.min_confidence = value
    click.echo(f"Minimum confidence set to {value:.2f}")


@config.command("lock")
@click.argument("skill_name", type=str, required=False)
def config_lock(skill_name: str | None) -> None:
    """Lock skill to prevent auto-switching. Omit skill name to unlock."""
    from hobo_code.auth.preferences import UserPreferences
    from hobo_code.skills.registry import SkillRegistry

    prefs = UserPreferences()
    if skill_name:
        registry = SkillRegistry()
        skill = registry.get_skill(skill_name)
        if skill:
            prefs.locked_skill = skill_name
            click.echo(f"Skill locked to '{skill_name}'")
        else:
            click.echo(f"Skill '{skill_name}' not found")
    else:
        prefs.locked_skill = None
        click.echo("Skill unlocked")


@config.command("debounce")
@click.argument("seconds", type=float)
def config_debounce(seconds: float) -> None:
    """Set debounce time in seconds (minimum 0.5)."""
    from hobo_code.auth.preferences import UserPreferences

    if seconds < 0.5:
        click.echo("Error: debounce must be at least 0.5 seconds")
        return

    prefs = UserPreferences()
    prefs.debounce_seconds = seconds
    click.echo(f"Debounce time set to {seconds} seconds")


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


@skills.command("add")
@click.argument("skill_name", type=str)
@click.option("--repo", default="leochong/HoboCode", help="GitHub repository (owner/repo)")
def skills_add(skill_name: str, repo: str) -> None:
    """Add a skill from a GitHub repository."""
    from hobo_code.skills.discovery import SkillDiscovery
    from hobo_code.skills.registry import SkillRegistry
    from pathlib import Path

    project_dir = Path.cwd()
    skills_dir = project_dir / "skills"

    if not skills_dir.exists():
        click.echo(
            "Error: No skills directory found. Run 'hobo init' first or run from project directory."
        )
        return

    discovery = SkillDiscovery()
    skill_path = discovery.find_skill(skill_name, skills_dir, repo)

    if skill_path and skill_path.exists():
        registry = SkillRegistry(project_dir=str(project_dir))
        if registry.add_skill(skill_path):
            click.echo(f"Skill '{skill_name}' added successfully.")
        else:
            click.echo(f"Failed to add skill '{skill_name}'.")
    else:
        click.echo(f"Skill '{skill_name}' not found in {repo}")


@skills.command("sync")
@click.option("--repo", default="leochong/HoboCode", help="GitHub repository (owner/repo)")
def skills_sync(repo: str) -> None:
    """Sync all available skills from a GitHub repository."""
    from hobo_code.skills.discovery import SkillDiscovery
    from pathlib import Path

    project_dir = Path.cwd()
    skills_dir = project_dir / "skills"

    if not skills_dir.exists():
        click.echo(
            "Error: No skills directory found. Run 'hobo init' first or run from project directory."
        )
        return

    discovery = SkillDiscovery()
    all_skills = discovery.list_all_available_skills(repo)

    if not all_skills:
        click.echo(f"No skills found in {repo}")
        return

    click.echo(f"Available skills in {repo}:")
    for skill in all_skills:
        name = skill.get("name", "")
        source_type = skill.get("source_type", "")
        click.echo(f"  - {name} ({source_type})")

    click.echo(f"\nTotal: {len(all_skills)} skills")


@skills.command("search")
@click.argument("query", type=str)
@click.option("--repo", default="leochong/HoboCode", help="GitHub repository (owner/repo)")
def skills_search(query: str, repo: str) -> None:
    """Search for skills matching a query."""
    from hobo_code.skills.discovery import SkillDiscovery

    discovery = SkillDiscovery()
    results = discovery.search_skills(query, repo)

    if not results:
        click.echo(f"No skills matching '{query}' found.")
        return

    click.echo(f"Skills matching '{query}':")
    for skill in results[:20]:
        name = skill.get("name", "")
        source = skill.get("source", "")
        source_type = skill.get("source_type", "")
        click.echo(f"  - {name} ({source_type}: {source})")

    if len(results) > 20:
        click.echo(f"  ... and {len(results) - 20} more")


@skills.command("info")
@click.argument("skill_name", type=str)
def skills_info(skill_name: str) -> None:
    """Show detailed information about a skill."""
    from hobo_code.skills.registry import SkillRegistry

    registry = SkillRegistry()
    skill = registry.get_skill(skill_name)

    if not skill:
        click.echo(f"Skill '{skill_name}' not found.")
        return

    click.echo(f"Skill: {skill.name}")
    click.echo(f"Description: {skill.description}")

    if skill.keywords:
        click.echo(f"Keywords: {', '.join(skill.keywords)}")

    if skill.when_to_use:
        click.echo("When to use:")
        for item in skill.when_to_use:
            click.echo(f"  - {item}")

    if skill.tools:
        click.echo(f"Tools: {', '.join(skill.tools)}")


@skills.command("classify")
@click.argument("message", type=str)
@click.option("--llm/--no-llm", default=True, help="Use LLM classification (default: yes)")
def skills_classify(message: str, llm: bool) -> None:
    """Classify a message and detect which skill to use.

    Uses both keyword matching and LLM classification to suggest the best skill.
    """
    from hobo_code.skills.classifier import SkillClassifier
    from hobo_code.skills.detection import SkillDetectionEngine

    click.echo(f'Classifying: "{message}"')
    click.echo("-" * 50)

    if llm:
        classifier = SkillClassifier()
        result = classifier.classify(message, use_llm_fallback=True)

        click.echo(f"Method: {result.get('method', 'unknown')}")
        click.echo(f"Skill: {result.get('skill') or '(none)'}")
        click.echo(f"Confidence: {result.get('confidence', 0):.2%}")

        if result.get("intent"):
            click.echo(f"Intent: {result['intent']}")
        if result.get("reasoning"):
            click.echo(f"Reasoning: {result['reasoning']}")
    else:
        engine = SkillDetectionEngine()
        skill_name, confidence = engine.detect_skill(message)

        click.echo("Method: keyword")
        click.echo(f"Skill: {skill_name or '(none)'}")
        click.echo(f"Confidence: {confidence:.2%}")


@skills.command("detect")
@click.argument("message", type=str)
@click.option("--top", "-t", default=3, help="Show top N recommendations")
def skills_detect(message: str, top: int) -> None:
    """Get skill detection details for a message.

    Shows how the detection engine analyzes your message and matches skills.
    """
    from hobo_code.skills.classifier import SkillClassifier
    from hobo_code.skills.detection import SkillDetectionEngine

    click.echo(f'Detecting skills for: "{message}"')
    click.echo("=" * 50)

    engine = SkillDetectionEngine()
    recommendations = engine.detect_skills_ranked(message, top)

    click.echo("\nKeyword Detection:")
    if recommendations:
        for skill, score in recommendations:
            click.echo(f"  - {skill}: {score:.2%}")
    else:
        click.echo("  No matches found")

    classifier = SkillClassifier()
    llm_recommendations = classifier.get_recommendations(message, top)

    click.echo("\nLLM Classification:")
    if llm_recommendations:
        for rec in llm_recommendations:
            method = rec.get("method", "unknown")
            click.echo(f"  - {rec['skill']}: {rec['confidence']:.2%} ({method})")
    else:
        click.echo("  No LLM recommendations (API not configured)")


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


@cli.group()
def export() -> None:
    """Export session data for SFT training."""
    pass


@export.command("session")
@click.argument("session_id", type=str)
@click.option("--output", "-o", type=str, default="export.jsonl", help="Output file path")
@click.option("--skill", type=str, default=None, help="Skill name to include")
def export_session(session_id: str, output: str, skill: str | None) -> None:
    """Export a single session as JSONL training data."""
    from hobo_code.session.manager import SessionManager
    from hobo_code.export.formatter import JSONLFormatter
    from hobo_code.skills.registry import SkillRegistry

    manager = SessionManager()
    session = manager.get_session(session_id)

    if not session:
        click.echo(f"Session {session_id} not found.")
        return

    registry = SkillRegistry()
    system_prompt = registry.get_system_prompt(skill)

    formatter = JSONLFormatter()
    lines = formatter.format_session(session, system_prompt, skill)

    count = formatter.export_to_file(lines, output)
    click.echo(f"Exported {count} training examples to {output}")


@export.command("all")
@click.option("--output", "-o", type=str, default="all_sessions.jsonl", help="Output file path")
def export_all(output: str) -> None:
    """Export all sessions as JSONL training data."""
    from hobo_code.session.manager import SessionManager
    from hobo_code.export.formatter import JSONLFormatter
    from hobo_code.skills.registry import SkillRegistry

    manager = SessionManager()
    sessions = manager.list_sessions()

    if not sessions:
        click.echo("No sessions found.")
        return

    registry = SkillRegistry()
    formatter = JSONLFormatter()
    all_lines = []

    for session in sessions:
        skill = session.model
        system_prompt = registry.get_system_prompt(skill)
        lines = formatter.format_session(session, system_prompt, skill)
        all_lines.extend(lines)

    count = formatter.export_to_file(all_lines, output)
    click.echo(f"Exported {count} training examples from {len(sessions)} sessions to {output}")


@export.command("stats")
def export_stats() -> None:
    """Show export statistics."""
    from hobo_code.session.manager import SessionManager
    from hobo_code.export.formatter import JSONLFormatter

    manager = SessionManager()
    sessions = manager.list_sessions()

    if not sessions:
        click.echo("No sessions found.")
        return

    formatter = JSONLFormatter()
    all_lines = []
    for session in sessions:
        lines = formatter.format_session(session, "You are a coding assistant.", None)
        all_lines.extend(lines)

    stats = formatter.get_stats(all_lines)

    click.echo("Export Statistics")
    click.echo("-" * 40)
    click.echo(f"Total training examples: {stats['total_examples']}")
    click.echo(f"Success rate: {stats['success_rate'] * 100:.1f}%")
    click.echo(f"Avg input tokens: {stats['avg_tokens_input']}")
    click.echo(f"Avg output tokens: {stats['avg_tokens_output']}")
    click.echo(f"Task types: {', '.join(stats['task_types'].keys())}")
    click.echo(f"Skills used: {', '.join(stats['skills_used'])}")


@export.command("dry-run")
@click.option("--sample", type=int, default=10, help="Number of samples to preview")
def export_dry_run(sample: int) -> None:
    """Preview export without saving."""
    from hobo_code.session.manager import SessionManager
    from hobo_code.export.formatter import JSONLFormatter

    manager = SessionManager()
    sessions = manager.list_sessions()

    if not sessions:
        click.echo("No sessions found.")
        return

    formatter = JSONLFormatter()
    all_lines = []
    for session in sessions[:sample]:
        lines = formatter.format_session(session, "You are a coding assistant.", None)
        all_lines.extend(lines)

    click.echo(f"Preview ({min(sample, len(all_lines))} examples):")
    for i, line in enumerate(all_lines[:sample]):
        import json

        data = json.loads(line)
        click.echo(f"\n--- Example {i + 1} ---")
        click.echo(f"Task: {data.get('task', 'unknown')}")
        click.echo(f"Skill: {data.get('skill', 'none')}")
        click.echo(f"Messages: {len(data.get('messages', []))}")
        click.echo(f"Success: {data.get('success', True)}")


@export.command("sample")
@click.option(
    "--output", "-o", type=str, default="data/sample_export.jsonl", help="Output file path"
)
def export_sample(output: str) -> None:
    """Create a sample JSONL export file."""
    from hobo_code.export.formatter import JSONLFormatter

    formatter = JSONLFormatter()
    count = formatter.create_sample_export(output)
    click.echo(f"Created sample export with {count} examples at {output}")


@cli.command("donate")
@click.option("--dataset", "-d", type=str, required=True, help="Dataset name on HF")
@click.option("--private", is_flag=True, help="Make dataset private")
@click.option("--token", type=str, help="HF token (or use HF_TOKEN env var)")
def donate(dataset: str, private: bool, token: str | None) -> None:
    """Donate training data to HuggingFace datasets."""
    from hobo_code.session.manager import SessionManager
    from hobo_code.export.formatter import JSONLFormatter
    from hobo_code.export.huggingface import HuggingFaceExporter

    manager = SessionManager()
    sessions = manager.list_sessions()

    if not sessions:
        click.echo("No sessions found to donate.")
        return

    formatter = JSONLFormatter()
    all_lines = []
    for session in sessions:
        lines = formatter.format_session(session, "You are a coding assistant.", None)
        all_lines.extend(lines)

    if not all_lines:
        click.echo("No training examples found.")
        return

    exporter = HuggingFaceExporter(token=token)
    result = exporter.export_with_metadata(
        all_lines,
        dataset_name=dataset,
        description=f"Hobo Code training data - {len(all_lines)} examples",
        private=private,
    )

    if result.get("success"):
        click.echo(f"Successfully pushed to {result['url']}")
    else:
        click.echo(f"Failed to push: {result.get('error')}")


@cli.command()
@click.argument("project_name", type=str)
@click.argument("description", type=str, required=False)
@click.option(
    "--path", "-p", type=str, default=None, help="Project path (default: current directory)"
)
@click.option(
    "--github-token", "-t", type=str, default=None, help="GitHub token for skill downloads"
)
def init(project_name: str, description: str, path: str | None, github_token: str | None) -> None:
    """Initialize a new Hobo Code project with default skills."""
    from hobo_code.skills.init import init_project
    from pathlib import Path

    base_path = Path(path) if path else Path.cwd()
    result = init_project(project_name, base_path, description or "", github_token)

    click.echo(f"Project created at: {result['project_path']}")
    click.echo(f"Skills directory: {result['skills_dir']}")
    click.echo(f"Downloaded skills: {', '.join(result['downloaded_skills'])}")
    click.echo("\nNext steps:")
    click.echo("  1. cd into the project directory")
    click.echo("  2. Add more skills: hobo skills add <skill-name>")
    click.echo("  3. Start coding: hobo chat")


def main():
    """Entry point for the CLI."""
    cli()
