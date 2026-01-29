"""Memory health check utilities."""

from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import click
from rich.table import Table

from claude_memory.memory import MemoryManager
from claude_memory.viz.utils import console, print_header, print_section, truncate_text


def check_index_integrity(manager: MemoryManager) -> dict:
    """Check index file integrity."""
    issues = []

    # Check global index
    if manager.global_dir:
        index_file = manager.global_dir / "memory" / "index.json"
        if not index_file.exists():
            issues.append("Global index file missing")
        else:
            try:
                manager.global_index.read_index()
            except Exception as e:
                issues.append(f"Global index corrupted: {e}")

    # Check project index
    if manager.project_dir:
        index_file = manager.project_dir / "memory" / "index.json"
        if not index_file.exists():
            issues.append("Project index file missing")
        else:
            try:
                manager.project_index.read_index()
            except Exception as e:
                issues.append(f"Project index corrupted: {e}")

    return {"status": "OK" if not issues else "WARNING", "issues": issues}


def check_session_files(manager: MemoryManager) -> dict:
    """Check session file validity."""
    issues = []

    for claude_dir in [manager.global_dir, manager.project_dir]:
        if not claude_dir:
            continue

        active_dir = claude_dir / "sessions" / "active"
        if active_dir.exists():
            for session_file in active_dir.glob("*.json"):
                try:
                    import json
                    with open(session_file) as f:
                        json.load(f)
                except Exception as e:
                    issues.append(f"Invalid session file: {session_file.name} - {e}")

    return {"status": "OK" if not issues else "ERROR", "issues": issues}


def check_markdown_archives(manager: MemoryManager) -> dict:
    """Check markdown archive readability."""
    issues = []

    for claude_dir in [manager.global_dir, manager.project_dir]:
        if not claude_dir:
            continue

        memory_dir = claude_dir / "memory" / "sessions"
        if memory_dir.exists():
            for md_file in memory_dir.glob("*.md"):
                try:
                    md_file.read_text()
                except Exception as e:
                    issues.append(f"Unreadable archive: {md_file.name} - {e}")

    return {"status": "OK" if not issues else "WARNING", "issues": issues}


def find_untagged_sessions(memories: list) -> list:
    """Find sessions with no tags."""
    return [m for m in memories if not m.tags or len(m.tags) == 0]


def find_never_accessed(memories: list) -> list:
    """Find memories that have never been accessed."""
    return [m for m in memories if not m.access or m.access.count == 0]


def find_potential_duplicates(memories: list, similarity_threshold: float = 0.8) -> list:
    """Find memories with very similar titles."""
    duplicates = []

    for i, mem1 in enumerate(memories):
        for mem2 in memories[i + 1 :]:
            title1 = mem1.title or ""
            title2 = mem2.title or ""

            if not title1 or not title2:
                continue

            similarity = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
            if similarity >= similarity_threshold:
                duplicates.append((mem1, mem2, similarity))

    return duplicates


def find_stale_sessions(memories: list, days_threshold: int = 180) -> list:
    """Find old sessions with zero accesses."""
    cutoff_date = datetime.now() - timedelta(days=days_threshold)

    stale = []
    for m in memories:
        if not m.created:
            continue

        is_old = m.created < cutoff_date
        is_unaccessed = not m.access or m.access.count == 0

        if is_old and is_unaccessed:
            stale.append(m)

    return stale


def render_health_check(memories: list, manager: MemoryManager):
    """Render health check report."""
    print_header("Memory Health Check")

    # Check integrity
    console.print("[bold]System Integrity[/]")

    index_check = check_index_integrity(manager)
    status_color = "green" if index_check["status"] == "OK" else "yellow"
    console.print(f"  Index integrity: [{status_color}]{index_check['status']}[/{status_color}]")
    for issue in index_check["issues"]:
        console.print(f"    [yellow]⚠[/yellow] {issue}")

    session_check = check_session_files(manager)
    status_color = "green" if session_check["status"] == "OK" else "red"
    console.print(f"  Session files: [{status_color}]{session_check['status']}[/{status_color}]")
    for issue in session_check["issues"]:
        console.print(f"    [red]✗[/red] {issue}")

    md_check = check_markdown_archives(manager)
    status_color = "green" if md_check["status"] == "OK" else "yellow"
    console.print(f"  Markdown archives: [{status_color}]{md_check['status']}[/{status_color}]")
    for issue in md_check["issues"]:
        console.print(f"    [yellow]⚠[/yellow] {issue}")

    console.print()

    # Quality checks
    warnings = []

    # Untagged sessions
    untagged = find_untagged_sessions(memories)
    if untagged:
        warnings.append(("Untagged Sessions", untagged, "Add tags for better searchability"))

    # Never accessed
    never_accessed = find_never_accessed(memories)
    if never_accessed:
        warnings.append(("Never Accessed", never_accessed, "May be outdated or unused"))

    # Potential duplicates
    duplicates = find_potential_duplicates(memories)
    if duplicates:
        warnings.append(("Potential Duplicates", duplicates, "Check if they should be merged"))

    # Stale sessions
    stale = find_stale_sessions(memories, days_threshold=180)
    if stale:
        warnings.append(("Stale Sessions", stale, "Consider archiving or deleting"))

    # Display warnings
    if warnings:
        console.print("[bold yellow]⚠ Warnings[/bold yellow]")
        console.print()

        for warning_type, items, suggestion in warnings:
            if warning_type == "Potential Duplicates":
                print_section(f"{warning_type} ({len(items)} pair{'s' if len(items) != 1 else ''})")
                for mem1, mem2, similarity in items[:5]:
                    title1 = truncate_text(mem1.title or "Untitled", 40)
                    title2 = truncate_text(mem2.title or "Untitled", 40)
                    console.print(f'  • "{title1}" vs "{title2}" ({similarity:.0%} similar)')

                if len(items) > 5:
                    console.print(f"  [dim]... and {len(items) - 5} more pairs[/]")

                console.print(f"  [dim]→ {suggestion}[/]")
                console.print()

            else:
                print_section(f"{warning_type} ({len(items)})")

                for item in items[:10]:
                    title = truncate_text(item.title or "Untitled", 60)

                    # Add context based on warning type
                    context = ""
                    if warning_type == "Never Accessed" and item.created:
                        days_old = (datetime.now() - item.created).days
                        context = f" (created {days_old}d ago)"
                    elif warning_type == "Stale Sessions" and item.created:
                        days_old = (datetime.now() - item.created).days
                        context = f" ({days_old}d old, 0 accesses)"

                    console.print(f"  • {title}{context}")

                if len(items) > 10:
                    console.print(f"  [dim]... and {len(items) - 10} more[/]")

                console.print(f"  [dim]→ {suggestion}[/]")
                console.print()

    else:
        console.print("[bold green]✓ No warnings found[/bold green]")
        console.print()

    # Recommendations
    if warnings:
        print_section("Recommendations")

        rec_num = 1
        if untagged:
            console.print(f"  {rec_num}. Tag {len(untagged)} untagged sessions for better organization")
            rec_num += 1

        if never_accessed:
            console.print(f"  {rec_num}. Review or delete {len(never_accessed)} never-accessed memories")
            rec_num += 1

        if stale:
            console.print(f"  {rec_num}. Archive or delete {len(stale)} stale sessions (>6 months old, unused)")
            rec_num += 1

        if duplicates:
            console.print(f"  {rec_num}. Check {len(duplicates)} potential duplicate{'s' if len(duplicates) != 1 else ''} for merging")
            rec_num += 1

        console.print()


@click.command("health")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Filter by scope",
)
@click.pass_obj
def health_cmd(manager: MemoryManager, scope: str):
    """Check memory system health."""
    # Search all memories
    memories = manager.search_memory()

    # Filter by scope
    if scope and scope != "both":
        memories = [m for m in memories if m.scope.value == scope]

    # Render health check
    render_health_check(memories, manager)
