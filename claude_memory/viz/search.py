"""Search interface for memory visualization."""

from datetime import datetime, timedelta
from typing import Optional

import click
from rich.panel import Panel
from rich.text import Text

from claude_memory.memory import MemoryManager
from claude_memory.viz.utils import (
    COLORS,
    console,
    format_access_count,
    format_date,
    format_tags,
    print_header,
    truncate_text,
)
from claude_memory.viz.export import memories_to_json, memories_to_markdown


def sort_by_relevance(memories: list) -> list:
    """Sort memories by relevance (access count + recency)."""

    def relevance_score(memory):
        # Access count contributes to score
        access_score = memory.access.count if memory.access else 0

        # Recency contributes to score
        recency_score = 0
        if memory.created:
            days_old = (datetime.now() - memory.created).days
            # Newer memories get higher scores (max 10 points, decaying over 365 days)
            recency_score = max(0, 10 - (days_old / 36.5))

        return access_score * 2 + recency_score

    return sorted(memories, key=relevance_score, reverse=True)


def render_search_results(
    memories: list,
    query: str,
    scope_filter: Optional[str] = None,
    tags_filter: Optional[str] = None,
    days: Optional[int] = None,
):
    """Render search results."""
    # Build filter description
    filters = []
    if scope_filter and scope_filter != "both":
        filters.append(f"scope={scope_filter}")
    if tags_filter:
        filters.append(f"tags={tags_filter}")
    if days:
        filters.append(f"last {days} days")

    filter_text = " | ".join(filters) if filters else "no filters"

    # Print header
    print_header(f'Search Results: "{query}"', f"Filters: {filter_text}")

    if not memories:
        console.print("No matches found.", style="yellow")
        return

    console.print(f"Found {len(memories)} match{'es' if len(memories) != 1 else ''}")
    console.print()

    # Sort by relevance
    memories = sort_by_relevance(memories)

    # Display results
    for i, memory in enumerate(memories, 1):
        # Build result content
        content = []

        # Title line
        title = memory.title or "Untitled"
        title_short = truncate_text(title, max_length=70)
        content.append(f"[bold bright_white]{i}. {title_short}[/]")

        # Metadata line
        date_str = format_date(memory.created) if memory.created else "Unknown"
        scope_color = COLORS.get(memory.scope.value, "white")
        type_color = COLORS.get(memory.type.value, "white")
        meta = f"{date_str} | [{scope_color}]{memory.scope.value}[/] | [{type_color}]{memory.type.value}[/]"
        content.append(meta)

        # Tags
        if memory.tags:
            tags_text = format_tags(memory.tags, max_display=8)
            content.append(f"Tags: {tags_text}")

        # Access info with visual indicator
        if memory.access:
            access_text = format_access_count(memory.access.count, highlight_threshold=5)
            access_line = f"Accessed: {access_text}"

            # Add "Most accessed" indicator for highly accessed memories
            if memory.access.count >= 10:
                access_line += " [bold bright_green]⭐ Highly accessed[/]"

            if memory.access.last_accessed:
                last = format_date(memory.access.last_accessed)
                access_line += f" (last: {last})"

            content.append(access_line)

        # Summary
        if memory.summary:
            summary = truncate_text(memory.summary, max_length=200)
            content.append(f"[dim]{summary}[/]")

        # Create panel for this result
        panel = Panel(
            "\n".join(content),
            border_style="dim",
            padding=(0, 1),
        )
        console.print(panel)

    console.print()
    console.print("[dim]Tip: Use 'claude-memory viz session <id>' to view full details[/]")


@click.command("search")
@click.argument("query")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Filter by scope",
)
@click.option("--tags", "tags_filter", help="Filter by tags (comma-separated)")
@click.option("--days", type=int, help="Show only memories from the last N days")
@click.option("--accessed-after", help="Show only memories accessed after this date (YYYY-MM-DD)")
@click.option("--accessed-before", help="Show only memories accessed before this date (YYYY-MM-DD)")
@click.option("--min-accesses", type=int, help="Show only memories with N+ accesses")
@click.option("--max-accesses", type=int, help="Show only memories with ≤N accesses")
@click.option("--never-accessed", is_flag=True, help="Show only never-accessed memories")
@click.option(
    "--export",
    type=click.Choice(["json", "markdown"]),
    help="Export results to specified format (output to stdout)",
)
@click.pass_obj
def search_cmd(
    manager: MemoryManager,
    query: str,
    scope: str,
    tags_filter: Optional[str],
    days: Optional[int],
    accessed_after: Optional[str],
    accessed_before: Optional[str],
    min_accesses: Optional[int],
    max_accesses: Optional[int],
    never_accessed: bool,
    export: Optional[str],
):
    """Search memories by query and filters."""
    # Parse tags filter
    tags = [t.strip() for t in tags_filter.split(",")] if tags_filter else None

    # Search
    memories = manager.search_memory(
        query=query if query else None,
        tags=tags,
    )

    # Filter by scope
    if scope and scope != "both":
        memories = [m for m in memories if m.scope.value == scope]

    # Filter by creation date
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        memories = [m for m in memories if m.created and m.created >= cutoff_date]

    # Filter by access date
    if accessed_after:
        try:
            after_date = datetime.strptime(accessed_after, "%Y-%m-%d")
            memories = [
                m for m in memories
                if m.access and m.access.last_accessed and m.access.last_accessed >= after_date
            ]
        except ValueError:
            console.print(f"Invalid date format: {accessed_after}. Use YYYY-MM-DD", style="red")
            return

    if accessed_before:
        try:
            before_date = datetime.strptime(accessed_before, "%Y-%m-%d")
            memories = [
                m for m in memories
                if m.access and m.access.last_accessed and m.access.last_accessed <= before_date
            ]
        except ValueError:
            console.print(f"Invalid date format: {accessed_before}. Use YYYY-MM-DD", style="red")
            return

    # Filter by access count
    if never_accessed:
        memories = [m for m in memories if not m.access or m.access.count == 0]
    else:
        if min_accesses is not None:
            memories = [m for m in memories if m.access and m.access.count >= min_accesses]

        if max_accesses is not None:
            memories = [m for m in memories if m.access and m.access.count <= max_accesses]

    # Export if requested
    if export:
        if export == "json":
            print(memories_to_json(memories))
        elif export == "markdown":
            print(memories_to_markdown(memories, title=f'Search Results: "{query}"'))
        return

    # Render results
    render_search_results(memories, query, scope_filter=scope, tags_filter=tags_filter, days=days)
