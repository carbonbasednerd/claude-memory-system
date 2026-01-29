"""Timeline view for memory visualization."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import click
from rich.tree import Tree

from claude_memory.memory import MemoryManager
from claude_memory.models import MemoryType, MemoryScope
from claude_memory.viz.utils import (
    COLORS,
    console,
    create_progress_bar,
    format_access_count,
    format_date,
    format_decision_count,
    format_file_count,
    format_relative_time,
    format_scope,
    format_tags,
    format_type,
    print_header,
)


def group_by_month(memories: list) -> dict[str, list]:
    """Group memories by year-month."""
    grouped = defaultdict(list)
    for memory in memories:
        if memory.created:
            month_key = memory.created.strftime("%Y-%m")
            grouped[month_key].append(memory)
    return dict(sorted(grouped.items(), reverse=True))


def render_timeline(
    memories: list,
    scope_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    days: Optional[int] = None,
    min_accesses: Optional[int] = None,
    never_accessed: bool = False,
):
    """Render timeline view of memories."""
    # Filter by date if specified
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        memories = [
            m
            for m in memories
            if m.created and m.created >= cutoff_date
        ]

    # Filter by scope
    if scope_filter and scope_filter != "both":
        memories = [m for m in memories if m.scope.value == scope_filter]

    # Filter by type
    if type_filter:
        memories = [m for m in memories if m.type.value == type_filter]

    # Filter by access count
    if never_accessed:
        memories = [m for m in memories if not m.access or m.access.count == 0]
    elif min_accesses is not None:
        memories = [m for m in memories if m.access and m.access.count >= min_accesses]

    if not memories:
        console.print("No memories found matching the criteria.", style="yellow")
        return

    # Group by month
    grouped = group_by_month(memories)

    # Calculate max sessions for progress bar scaling
    max_sessions = max(len(sessions) for sessions in grouped.values()) if grouped else 1

    # Build the timeline tree
    for month_key, month_memories in grouped.items():
        # Month header with progress bar
        bar = create_progress_bar(len(month_memories), max_sessions, width=20)
        month_text = f"{month_key} {bar} {len(month_memories)} session{'s' if len(month_memories) != 1 else ''}"
        console.print(month_text, style="bold bright_white")

        # Sort by date within month (newest first)
        month_memories.sort(
            key=lambda m: m.created if m.created else datetime.min,
            reverse=True,
        )

        # Create tree for this month
        tree = Tree("", hide_root=True)

        for memory in month_memories:
            # Build memory summary line
            date_str = format_date(memory.created) if memory.created else "Unknown"
            scope_text = f"[{COLORS[memory.scope.value]}]{memory.scope.value}[/]"
            title = memory.title or "Untitled"

            # Access info
            access = ""
            if memory.access:
                access_count = format_access_count(memory.access.count)
                last_accessed = ""
                if memory.access.last_accessed:
                    last_accessed = f" (last: {format_date(memory.access.last_accessed)})"
                access = f" | {access_count}{last_accessed}"

            # File and decision counts
            file_count = len(memory.files_modified) if memory.files_modified else 0
            decision_count = len(memory.decisions) if memory.decisions else 0
            counts = f"Files: {file_count} | Decisions: {decision_count}"

            # Build the tree node
            node_label = f"[{date_str}] {title} ({scope_text})"
            node = tree.add(node_label)

            # Add details as sub-items
            if memory.tags:
                tags_text = format_tags(memory.tags)
                node.add(f"Tags: {tags_text}")

            node.add(counts + access)

        console.print(tree)
        console.print()


@click.command("timeline")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Filter by scope",
)
@click.option("--days", type=int, help="Show only memories from the last N days")
@click.option("--type", "type_filter", help="Filter by memory type (session, decision, pattern, skill)")
@click.option("--min-accesses", type=int, help="Show only memories with N+ accesses")
@click.option("--never-accessed", is_flag=True, help="Show only never-accessed memories")
@click.pass_obj
def timeline_cmd(
    manager: MemoryManager,
    scope: str,
    days: Optional[int],
    type_filter: Optional[str],
    min_accesses: Optional[int],
    never_accessed: bool,
):
    """Display memory timeline grouped by month."""
    # Print header
    days_text = f" (Last {days} days)" if days else ""
    scope_text = f" - {scope.capitalize()}" if scope != "both" else ""
    type_text = f" - {type_filter.capitalize()}" if type_filter else ""

    print_header(f"Memory Timeline{days_text}{scope_text}{type_text}")

    # Search all memories
    memories = manager.search_memory()

    # Render timeline
    render_timeline(
        memories,
        scope_filter=scope,
        type_filter=type_filter,
        days=days,
        min_accesses=min_accesses,
        never_accessed=never_accessed,
    )
