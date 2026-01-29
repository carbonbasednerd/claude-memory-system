"""Session detail view for memory visualization."""

from typing import Optional

import click
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from claude_memory.memory import MemoryManager, MemoryEntry
from claude_memory.viz.utils import (
    COLORS,
    console,
    format_access_count,
    format_datetime,
    format_tags,
    truncate_text,
)


def find_related_sessions(manager: MemoryManager, memory: MemoryEntry, max_results: int = 5) -> list:
    """Find sessions with overlapping tags."""
    if not memory.tags:
        return []

    all_memories = manager.search_memory()
    related = []

    for other in all_memories:
        if other.id == memory.id:
            continue

        if other.tags:
            overlap = set(memory.tags) & set(other.tags)
            if overlap:
                related.append((other, len(overlap)))

    # Sort by overlap count, then by date
    related.sort(
        key=lambda x: (
            x[1],
            x[0].created if x[0].created else None,
        ),
        reverse=True,
    )

    return [r[0] for r in related[:max_results]]


def render_session_detail(manager: MemoryManager, session_id: str):
    """Render detailed view of a session."""
    # Load the memory entry
    memory = manager.get_memory(session_id)
    if not memory:
        console.print(f"Session not found: {session_id}", style="red")
        return

    # Record this access
    manager.record_memory_access(session_id)

    console.print()

    # Title
    title = memory.title or "Untitled"
    console.print(f"[bold bright_white]{title}[/]", style="bold")
    console.print()

    # Basic info
    scope_color = COLORS.get(memory.scope.value, "white")
    type_color = COLORS.get(memory.type.value, "white")

    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="dim", justify="right", width=12)
    info_table.add_column()

    info_table.add_row("Scope:", f"[{scope_color}]{memory.scope.value}[/]")
    info_table.add_row("Type:", f"[{type_color}]{memory.type.value}[/]")
    info_table.add_row("ID:", f"[dim]{session_id}[/]")

    if memory.created:
        info_table.add_row("Created:", format_datetime(memory.created))
    if memory.updated:
        info_table.add_row("Updated:", format_datetime(memory.updated))

    console.print(info_table)
    console.print()

    # ACCESS TRACKING SECTION (PROMINENT)
    if memory.access and memory.access.count > 0:
        console.print("[bold bright_cyan]Access Tracking[/]", style="bold")
        access_table = Table.grid(padding=(0, 2))
        access_table.add_column(style="dim", justify="right", width=12)
        access_table.add_column()

        access_count_text = format_access_count(memory.access.count, highlight_threshold=5)
        access_table.add_row("Accessed:", str(access_count_text))

        if memory.access.first_accessed:
            access_table.add_row("First:", format_datetime(memory.access.first_accessed))

        if memory.access.last_accessed:
            access_table.add_row("Last:", format_datetime(memory.access.last_accessed))

        if memory.access.recent_searches:
            searches = ", ".join(f'"{s}"' for s in list(memory.access.recent_searches)[:3])
            access_table.add_row("Queries:", searches)

        console.print(access_table)
        console.print()
    else:
        console.print("[dim]No access tracking data[/]")
        console.print()

    # Tags
    if memory.tags:
        tags_text = format_tags(memory.tags, max_display=15)
        console.print(f"[bold]Tags:[/] {tags_text}")
        console.print()

    # Summary
    if memory.summary:
        console.print("[bold]Summary[/]", style="bold")
        summary_text = truncate_text(memory.summary, max_length=500)
        console.print(summary_text)
        console.print()

    # Files modified
    if memory.files_modified:
        console.print(f"[bold]Files Modified ({len(memory.files_modified)})[/]", style="bold")
        for i, file_path in enumerate(memory.files_modified[:15]):
            console.print(f"  • {file_path}")
        if len(memory.files_modified) > 15:
            console.print(f"  [dim]... and {len(memory.files_modified) - 15} more[/]")
        console.print()

    # Decisions
    if memory.decisions:
        console.print(f"[bold]Decisions ({len(memory.decisions)})[/]", style="bold")
        for i, decision in enumerate(memory.decisions[:10], 1):
            decision_text = truncate_text(decision, max_length=120)
            console.print(f"  {i}. {decision_text}")
        if len(memory.decisions) > 10:
            console.print(f"  [dim]... and {len(memory.decisions) - 10} more[/]")
        console.print()

    # Related sessions
    related = find_related_sessions(manager, memory, max_results=5)
    if related:
        console.print(f"[bold]Related Sessions ({len(related)})[/]", style="bold")
        for other in related:
            other_title = other.title or "Untitled"
            other_title_short = truncate_text(other_title, max_length=60)
            overlap_tags = set(memory.tags or []) & set(other.tags or [])
            tags_str = ", ".join(sorted(overlap_tags)[:3])
            console.print(f"  • [cyan]{other.id[:16]}...[/] - {other_title_short}")
            console.print(f"    [dim]Shared tags: {tags_str}[/]")
        console.print()


@click.command("session")
@click.argument("session_id")
@click.pass_obj
def session_cmd(manager: MemoryManager, session_id: str):
    """Display detailed information about a session."""
    render_session_detail(manager, session_id)
