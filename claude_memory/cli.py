"""CLI interface for Claude Memory System."""

import click
from pathlib import Path
from datetime import datetime

from claude_memory.memory import MemoryManager
from claude_memory.session import SessionTracker
from claude_memory.skills import SkillDetector, flag_skill_candidates
from claude_memory.models import MemoryScope, MemoryType
from claude_memory.utils import get_global_claude_dir, get_project_claude_dir
from claude_memory.viz.timeline import timeline_cmd
from claude_memory.viz.session import session_cmd
from claude_memory.viz.search import search_cmd
from claude_memory.viz.stats import stats_cmd
from claude_memory.viz.tags import tags_cmd
from claude_memory.viz.projects import projects_cmd
from claude_memory.viz.health import health_cmd


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Claude Memory System - Two-tier memory for Claude Code."""
    pass


@main.command()
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Scope to initialize",
)
def init(scope):
    """Initialize memory system."""
    cwd = Path.cwd()

    if scope in ["global", "both"]:
        global_dir = get_global_claude_dir()
        if global_dir.exists():
            click.echo(f"✓ Global memory already initialized at {global_dir}")
        else:
            manager = MemoryManager(cwd)
            click.echo(f"✓ Initialized global memory at {global_dir}")

    if scope in ["project", "both"]:
        project_dir = get_project_claude_dir(cwd)
        if not project_dir:
            click.echo("✗ Not in a project directory")
            return

        if project_dir.exists():
            click.echo(f"✓ Project memory already initialized at {project_dir}")
        else:
            manager = MemoryManager(cwd)
            click.echo(f"✓ Initialized project memory at {project_dir}")


@main.command()
@click.argument("task", required=False)
def start_session(task):
    """Start a new session."""
    manager = MemoryManager()
    session = manager.create_session()

    if task:
        session.update_task(task)

    click.echo(f"✓ Started session: {session.session_id}")
    if task:
        click.echo(f"  Task: {task}")
    click.echo(f"  Tracking at: {session.session_file}")


@main.command()
@click.option("--session-id", help="Session ID (uses latest if not provided)")
@click.option(
    "--scope",
    type=click.Choice(["global", "project"]),
    help="Save to global or project scope",
)
@click.option("--tags", help="Comma-separated tags")
@click.option("--summary", help="Session summary")
def save_session(session_id, scope, tags, summary):
    """Save current session to long-term memory."""
    manager = MemoryManager()

    # Find session
    if session_id:
        # Load specific session
        claude_dir = manager.project_dir or manager.global_dir
        session = SessionTracker(claude_dir, session_id)
    else:
        # Find most recent active session
        claude_dir = manager.project_dir or manager.global_dir
        active_sessions = SessionTracker.list_active_sessions(claude_dir)
        if not active_sessions:
            click.echo("✗ No active sessions found")
            return

        # Use most recent
        active_sessions.sort(key=lambda s: s.last_updated, reverse=True)
        session = SessionTracker(claude_dir, active_sessions[0].session_id)

    # Determine scope
    if not scope:
        # Auto-suggest based on context
        if manager.project_dir:
            scope_enum = MemoryScope.PROJECT
            click.echo("Auto-selected scope: project")
        else:
            scope_enum = MemoryScope.GLOBAL
            click.echo("Auto-selected scope: global")
    else:
        scope_enum = MemoryScope.GLOBAL if scope == "global" else MemoryScope.PROJECT

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Save to memory
    memory_entry = manager.save_session_to_memory(
        session, scope_enum, tags=tag_list, summary=summary
    )

    click.echo(f"✓ Saved session to {scope_enum.value} memory")
    click.echo(f"  Memory ID: {memory_entry.id}")
    click.echo(f"  Title: {memory_entry.title}")
    click.echo(f"  File: {memory_entry.file}")

    # Archive session
    session.archive()
    click.echo(f"✓ Archived session: {session.session_id}")


@main.command()
@click.argument("query")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Search scope",
)
@click.option("--tags", help="Filter by tags (comma-separated)")
@click.option(
    "--type",
    "memory_type",
    type=click.Choice(["session", "decision", "implementation", "pattern"]),
    help="Filter by memory type",
)
@click.option("--limit", type=int, default=10, help="Limit results")
def search(query, scope, tags, memory_type, limit):
    """Search memory."""
    manager = MemoryManager()

    # Parse filters
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    type_enum = MemoryType(memory_type) if memory_type else None
    scope_enum = None if scope == "both" else MemoryScope(scope)

    # Search
    results = manager.search_memory(query, tag_list, type_enum, scope_enum)

    if not results:
        click.echo("No results found.")
        return

    click.echo(f"Found {len(results)} results:\n")

    for i, memory in enumerate(results[:limit], 1):
        click.echo(f"{i}. [{memory.scope.value}] {memory.title}")
        click.echo(f"   ID: {memory.id}")
        click.echo(f"   Type: {memory.type.value}")
        click.echo(f"   Created: {memory.created.strftime('%Y-%m-%d')}")
        click.echo(f"   Tags: {', '.join(memory.tags)}")
        if memory.summary:
            click.echo(f"   Summary: {memory.summary[:100]}...")
        click.echo()


@main.command()
@click.argument("memory_id")
def show(memory_id):
    """Show details of a memory entry."""
    manager = MemoryManager()
    memory = manager.get_memory(memory_id)

    if not memory:
        click.echo(f"✗ Memory not found: {memory_id}")
        return

    click.echo(f"Title: {memory.title}")
    click.echo(f"ID: {memory.id}")
    click.echo(f"Type: {memory.type.value}")
    click.echo(f"Scope: {memory.scope.value}")
    click.echo(f"Created: {memory.created}")
    click.echo(f"Updated: {memory.updated}")
    click.echo(f"Tags: {', '.join(memory.tags)}")
    click.echo(f"\nSummary:\n{memory.summary}")
    click.echo(f"\nKeywords: {', '.join(memory.keywords)}")
    click.echo(f"Triggers: {', '.join(memory.triggers)}")

    if memory.files_modified:
        click.echo(f"\nFiles Modified:")
        for f in memory.files_modified:
            click.echo(f"  - {f}")

    if memory.decisions:
        click.echo(f"\nDecisions:")
        for d in memory.decisions:
            click.echo(f"  - {d}")

    click.echo(f"\nAccess Count: {memory.access.count}")
    if memory.access.last_accessed:
        click.echo(f"Last Accessed: {memory.access.last_accessed}")

    # Record this access
    manager.record_memory_access(memory_id)


@main.command()
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Scope to analyze",
)
@click.option("--min-occurrences", type=int, default=3, help="Minimum pattern occurrences")
@click.option("--days", type=int, default=90, help="Look back this many days")
def analyze_skills(scope, min_occurrences, days):
    """Analyze memory for skill candidates."""
    manager = MemoryManager()

    # Get memories
    scope_enum = None if scope == "both" else MemoryScope(scope)
    memories = manager.search_memory(scope=scope_enum)

    if not memories:
        click.echo("No memories to analyze.")
        return

    click.echo(f"Analyzing {len(memories)} memories...")

    # Detect candidates
    detector = SkillDetector(memories)
    candidates = detector.detect_candidates(min_occurrences, days)

    if not candidates:
        click.echo("No skill candidates detected.")
        return

    click.echo(f"\nFound {len(candidates)} skill candidates:\n")

    for candidate in candidates:
        click.echo(f"• {candidate['name']}")
        click.echo(f"  Type: {candidate['type']}")
        click.echo(f"  Confidence: {candidate['confidence']}")
        click.echo(f"  Occurrences: {candidate['occurrences']}")
        click.echo(f"  Suggested name: {candidate['suggested_skill_name']}")
        click.echo()

    # Generate report
    output_dir = manager.project_dir or manager.global_dir
    report_file = output_dir / "skill-candidates.md"
    detector.generate_report(candidates, report_file)
    click.echo(f"✓ Full report saved to: {report_file}")


@main.command()
@click.option(
    "--scope",
    type=click.Choice(["global", "project"]),
    default="project",
    help="Which index to rebuild",
)
def rebuild_index(scope):
    """Rebuild memory index from log entries."""
    manager = MemoryManager()

    if scope == "global":
        manager.global_index.rebuild_index()
        click.echo("✓ Rebuilt global index")
    else:
        if not manager.project_index:
            click.echo("✗ Not in a project")
            return
        manager.project_index.rebuild_index()
        click.echo("✓ Rebuilt project index")


@main.command()
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Which manifest to rebuild",
)
def rebuild_manifest(scope):
    """Rebuild memory manifest for lightweight loading."""
    from claude_memory.manifest import MemoryManifest
    from claude_memory.models import MemoryScope

    manager = MemoryManager()

    if scope in ["global", "both"]:
        # Rebuild global manifest
        global_index = manager.global_index.read_index(include_logs=True)
        manifest = MemoryManifest(manager.global_dir, MemoryScope.GLOBAL)
        manifest.rebuild(global_index)
        click.echo(f"✓ Rebuilt global manifest ({len(global_index.memories)} memories)")

    if scope in ["project", "both"]:
        if not manager.project_dir:
            click.echo("✗ Not in a project")
            return
        # Rebuild project manifest
        project_index = manager.project_index.read_index(include_logs=True)
        manifest = MemoryManifest(manager.project_dir, MemoryScope.PROJECT)
        manifest.rebuild(project_index)
        click.echo(f"✓ Rebuilt project manifest ({len(project_index.memories)} memories)")


@main.command()
@click.option("--hours", type=int, default=24, help="Hours of inactivity threshold")
@click.option("--auto-archive", is_flag=True, help="Automatically archive stale sessions")
def cleanup_sessions(hours, auto_archive):
    """Cleanup stale sessions."""
    manager = MemoryManager()

    for claude_dir in [manager.global_dir, manager.project_dir]:
        if not claude_dir:
            continue

        stale = SessionTracker.cleanup_stale_sessions(claude_dir, hours)

        if not stale:
            continue

        click.echo(f"\nFound {len(stale)} stale sessions in {claude_dir}:")

        for session_id in stale:
            click.echo(f"  - {session_id}")

            if auto_archive:
                session = SessionTracker(claude_dir, session_id)
                session.archive()
                click.echo(f"    ✓ Archived")


@main.command()
def list_sessions():
    """List active sessions."""
    manager = MemoryManager()

    # List global sessions
    global_sessions = SessionTracker.list_active_sessions(manager.global_dir)
    if global_sessions:
        click.echo("Global Sessions:")
        for session in global_sessions:
            click.echo(f"  - {session.session_id}")
            click.echo(f"    Task: {session.task or 'N/A'}")
            click.echo(f"    Started: {session.started}")
            click.echo()

    # List project sessions
    if manager.project_dir:
        project_sessions = SessionTracker.list_active_sessions(manager.project_dir)
        if project_sessions:
            click.echo("Project Sessions:")
            for session in project_sessions:
                click.echo(f"  - {session.session_id}")
                click.echo(f"    Task: {session.task or 'N/A'}")
                click.echo(f"    Started: {session.started}")
                click.echo()

    if not global_sessions and (not manager.project_dir or not project_sessions):
        click.echo("No active sessions.")


@main.command()
def stats():
    """Show memory statistics."""
    manager = MemoryManager()

    # Global stats
    global_index = manager.global_index.read_index(include_logs=True)
    click.echo("Global Memory:")
    click.echo(f"  Total memories: {len(global_index.memories)}")
    click.echo(f"  Total accesses: {sum(m.access.count for m in global_index.memories)}")

    if global_index.stats:
        click.echo(f"  By type:")
        for type_name, count in global_index.stats.get("by_type", {}).items():
            click.echo(f"    {type_name}: {count}")

    # Project stats
    if manager.project_index:
        project_index = manager.project_index.read_index(include_logs=True)
        click.echo("\nProject Memory:")
        click.echo(f"  Total memories: {len(project_index.memories)}")
        click.echo(f"  Total accesses: {sum(m.access.count for m in project_index.memories)}")

        if project_index.stats:
            click.echo(f"  By type:")
            for type_name, count in project_index.stats.get("by_type", {}).items():
                click.echo(f"    {type_name}: {count}")


@main.command()
@click.argument("action", type=click.Choice(["on", "off", "status"]))
def debug(action):
    """Toggle debug mode for context tracking.

    Actions:
      on      - Enable debug mode
      off     - Disable debug mode
      status  - Show current debug status
    """
    manager = MemoryManager()
    debug_flag = manager.global_dir / "sessions" / "debug.flag"

    if action == "on":
        debug_flag.parent.mkdir(parents=True, exist_ok=True)
        debug_flag.write_text(f"enabled at {datetime.now().isoformat()}")
        click.echo("✓ Debug mode enabled")
        click.echo("  Context tracking will be active in your next session")
        click.echo("  Say 'show context usage' to see breakdown")
    elif action == "off":
        if debug_flag.exists():
            debug_flag.unlink()
        click.echo("✓ Debug mode disabled")
    else:  # status
        if debug_flag.exists():
            click.echo("Debug mode: ON")
            content = debug_flag.read_text()
            click.echo(f"  {content}")
        else:
            click.echo("Debug mode: OFF")


@main.command()
def update_current_work():
    """Update CLAUDE.md with current work section."""
    manager = MemoryManager()
    manager.update_current_work()
    click.echo("✓ Updated CLAUDE.md with current work")


@main.group()
@click.pass_context
def viz(ctx):
    """Memory visualization commands."""
    # Create and pass MemoryManager to all subcommands
    ctx.obj = MemoryManager()


# Register viz subcommands
viz.add_command(timeline_cmd)
viz.add_command(session_cmd)
viz.add_command(search_cmd)
viz.add_command(stats_cmd)
viz.add_command(tags_cmd)
viz.add_command(projects_cmd)
viz.add_command(health_cmd)


@main.command()
@click.option("--port", default=8501, help="Port to run web server")
@click.option("--open/--no-open", default=True, help="Open browser automatically")
@click.option("--export", type=click.Path(), help="Export to static HTML file")
def web(port, open, export):
    """Launch interactive web dashboard."""
    if export:
        click.echo("✗ HTML export not yet implemented")
        click.echo("  Coming in Phase 3 - use the web UI for now")
        return

    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        click.echo("✗ Streamlit not installed")
        click.echo("  Install with: pip install -e '.[web]'")
        return

    # Launch Streamlit app
    import subprocess
    import webbrowser
    import time

    app_path = Path(__file__).parent / "web" / "app.py"

    click.echo(f"🚀 Launching Claude Memory Dashboard on port {port}...")
    click.echo(f"   App path: {app_path}")

    # Build streamlit command
    cmd = [
        "streamlit", "run",
        str(app_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]

    # Open browser if requested
    if open:
        click.echo(f"   Opening browser at http://localhost:{port}")
        # Delay browser open slightly to let server start
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}")

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    click.echo("\n   Press Ctrl+C to stop the server\n")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        click.echo("\n✓ Dashboard stopped")
    except FileNotFoundError:
        click.echo("✗ Streamlit command not found")
        click.echo("  Make sure streamlit is installed: pip install -e '.[web]'")


if __name__ == "__main__":
    main()
