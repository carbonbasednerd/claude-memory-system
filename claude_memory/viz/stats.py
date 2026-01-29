"""Statistics dashboard for memory visualization."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

import click
from rich.table import Table
from rich.text import Text

from claude_memory.memory import MemoryManager
from claude_memory.viz.utils import (
    console,
    create_progress_bar,
    format_access_count,
    format_date,
    print_header,
    print_section,
    truncate_text,
)
from claude_memory.viz.export import stats_to_json, export_to_markdown


def calculate_stats(memories: list) -> dict:
    """Calculate comprehensive statistics from memories."""
    stats = {
        "total": len(memories),
        "by_scope": Counter(),
        "by_type": Counter(),
        "total_accesses": 0,
        "accessed_count": defaultdict(int),
        "most_accessed": [],
        "never_accessed": [],
        "by_week": defaultdict(lambda: {"count": 0, "accesses": 0}),
        "tags": Counter(),
    }

    for memory in memories:
        # Scope and type counts
        stats["by_scope"][memory.scope.value] += 1
        stats["by_type"][memory.type.value] += 1

        # Access counts
        access_count = memory.access.count if memory.access else 0
        stats["total_accesses"] += access_count
        stats["accessed_count"][memory.type.value] += access_count

        # Track for most/never accessed
        if access_count > 0:
            stats["most_accessed"].append((memory, access_count))
        else:
            stats["never_accessed"].append(memory)

        # Activity by week
        if memory.created:
            # Calculate week number (0 = current week)
            days_old = (datetime.now() - memory.created).days
            week_num = days_old // 7

            if week_num < 13:  # Last 90 days = ~13 weeks
                week_key = f"Week {13 - week_num}"
                stats["by_week"][week_key]["count"] += 1
                stats["by_week"][week_key]["accesses"] += access_count

        # Tag counts
        if memory.tags:
            for tag in memory.tags:
                stats["tags"][tag] += 1

    # Sort most accessed
    stats["most_accessed"].sort(key=lambda x: x[1], reverse=True)

    # Sort never accessed by date (oldest first)
    stats["never_accessed"].sort(
        key=lambda m: m.created if m.created else datetime.max
    )

    return stats


def render_stats_dashboard(memories: list, scope_filter: Optional[str] = None):
    """Render statistics dashboard."""
    if not memories:
        console.print("No memories found.", style="yellow")
        return

    stats = calculate_stats(memories)

    # Overview section
    print_header("Memory Statistics")

    console.print("[bold]Overview:[/]")
    total_text = f"Total Memories: [bright_white]{stats['total']}[/]"

    if len(stats["by_scope"]) > 1:
        scope_breakdown = ", ".join(
            f"{scope}: {count}" for scope, count in sorted(stats["by_scope"].items())
        )
        total_text += f" ({scope_breakdown})"

    console.print(f"  {total_text}")
    console.print(f"  Total Accesses: [bright_white]{stats['total_accesses']}[/]")

    if stats["total"] > 0:
        avg_access = stats["total_accesses"] / stats["total"]
        console.print(f"  Average Access: [bright_white]{avg_access:.1f}[/] per memory")

    console.print()

    # By Type table
    if stats["by_type"]:
        print_section("By Type")

        type_table = Table()
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right")
        type_table.add_column("Accesses", justify="right")

        for type_name, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
            accesses = stats["accessed_count"][type_name]
            type_table.add_row(type_name.capitalize(), str(count), str(accesses))

        console.print(type_table)
        console.print()

    # Most Accessed
    if stats["most_accessed"]:
        print_section("Most Accessed (Top 10)")

        for i, (memory, count) in enumerate(stats["most_accessed"][:10], 1):
            title = memory.title or "Untitled"
            title_short = truncate_text(title, max_length=50)

            access_text = format_access_count(count, highlight_threshold=5)
            last_accessed = ""
            if memory.access and memory.access.last_accessed:
                last_accessed = f" (last: {format_date(memory.access.last_accessed)})"

            console.print(f"  {i:2d}. {title_short}")
            console.print(f"      {access_text}{last_accessed}", style="dim")

        console.print()

    # Never Accessed
    if stats["never_accessed"]:
        print_section(f"Never Accessed ({len(stats['never_accessed'])})")

        for memory in stats["never_accessed"][:10]:
            title = memory.title or "Untitled"
            title_short = truncate_text(title, max_length=50)

            created = ""
            if memory.created:
                days_old = (datetime.now() - memory.created).days
                created = f" (created {days_old}d ago)"

            console.print(f"  • {title_short}{created}", style="dim")

        if len(stats["never_accessed"]) > 10:
            console.print(f"  [dim]... and {len(stats['never_accessed']) - 10} more[/]")

        console.print()

    # Activity Timeline
    if stats["by_week"]:
        print_section("Activity Timeline (Last 90 days)")

        # Get weeks in order
        weeks = sorted(stats["by_week"].items(), key=lambda x: int(x[0].split()[1]))

        # Find max for scaling
        max_count = max(w["count"] for w in stats["by_week"].values())

        for week_label, week_data in weeks:
            bar = create_progress_bar(week_data["count"], max_count, width=16)
            session_text = f"{week_data['count']} session{'s' if week_data['count'] != 1 else ''}"
            access_text = f"{week_data['accesses']} access{'es' if week_data['accesses'] != 1 else ''}"
            console.print(f"  {week_label:7s}: {bar} {session_text} | {access_text}")

        console.print()

    # Top Tags
    if stats["tags"]:
        print_section("Top Tags")

        max_tag_count = max(stats["tags"].values())

        for tag, count in stats["tags"].most_common(15):
            bar = create_progress_bar(count, max_tag_count, width=12)
            console.print(f"  {tag:20s} {bar} {count}")

        console.print()


@click.command("stats")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Filter by scope",
)
@click.option(
    "--export",
    type=click.Choice(["json"]),
    help="Export statistics to specified format",
)
@click.pass_obj
def stats_cmd(manager: MemoryManager, scope: str, export: Optional[str]):
    """Display statistics dashboard."""
    # Search all memories
    memories = manager.search_memory()

    # Filter by scope
    if scope and scope != "both":
        memories = [m for m in memories if m.scope.value == scope]

    # Export if requested
    if export:
        stats = calculate_stats(memories)
        if export == "json":
            print(stats_to_json(stats))
        return

    # Render dashboard
    render_stats_dashboard(memories, scope_filter=scope)
