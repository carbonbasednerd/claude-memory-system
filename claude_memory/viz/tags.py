"""Tag network and cloud visualization."""

from collections import Counter, defaultdict
from typing import Optional

import click
from rich.table import Table
from rich.tree import Tree

from claude_memory.memory import MemoryManager
from claude_memory.viz.utils import (
    console,
    create_progress_bar,
    print_header,
    print_section,
)


def calculate_tag_stats(memories: list) -> dict:
    """Calculate tag frequency and co-occurrence statistics."""
    stats = {
        "frequency": Counter(),
        "co_occurrence": defaultdict(lambda: Counter()),
        "access_by_tag": defaultdict(lambda: {"total": 0, "count": 0}),
        "memories_by_tag": defaultdict(list),
    }

    for memory in memories:
        if not memory.tags:
            continue

        access_count = memory.access.count if memory.access else 0

        # Track frequency
        for tag in memory.tags:
            stats["frequency"][tag] += 1
            stats["memories_by_tag"][tag].append(memory)
            stats["access_by_tag"][tag]["total"] += access_count
            stats["access_by_tag"][tag]["count"] += 1

        # Track co-occurrence
        for i, tag1 in enumerate(memory.tags):
            for tag2 in memory.tags[i + 1 :]:
                stats["co_occurrence"][tag1][tag2] += 1
                stats["co_occurrence"][tag2][tag1] += 1

    return stats


def render_tag_cloud(memories: list, min_count: int = 1):
    """Render tag cloud and network visualization."""
    if not memories:
        console.print("No memories found.", style="yellow")
        return

    stats = calculate_tag_stats(memories)

    if not stats["frequency"]:
        console.print("No tags found in memories.", style="yellow")
        return

    # Filter by min count
    filtered_tags = {tag: count for tag, count in stats["frequency"].items() if count >= min_count}

    if not filtered_tags:
        console.print(f"No tags with {min_count}+ occurrences found.", style="yellow")
        return

    print_header(f"Tag Analysis (min count: {min_count})", f"Total unique tags: {len(filtered_tags)}")

    # Tag Cloud (frequency)
    print_section("Tag Cloud (size = frequency)")

    max_count = max(filtered_tags.values())
    sorted_tags = sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True)

    for tag, count in sorted_tags[:20]:  # Show top 20
        bar = create_progress_bar(count, max_count, width=12)
        console.print(f"  {tag:25s} {bar} {count}")

    if len(sorted_tags) > 20:
        console.print(f"  [dim]... and {len(sorted_tags) - 20} more tags[/]")

    console.print()

    # Access statistics by tag
    print_section("Most Accessed Tags (avg accesses per memory)")

    access_stats = []
    for tag in filtered_tags:
        tag_data = stats["access_by_tag"][tag]
        if tag_data["count"] > 0:
            avg_access = tag_data["total"] / tag_data["count"]
            access_stats.append((tag, avg_access, tag_data["total"], tag_data["count"]))

    access_stats.sort(key=lambda x: x[1], reverse=True)

    for tag, avg, total, count in access_stats[:10]:
        console.print(f"  {tag:25s} avg {avg:4.1f}× per memory ({total} total across {count} memories)")

    console.print()

    # Co-occurrence Network
    print_section("Tag Relationships (co-occurrence)")

    # Build tree showing top tags and their most common pairs
    tree = Tree("[bold]Top Tags[/]", hide_root=True)

    for tag, count in sorted_tags[:10]:  # Top 10 tags
        tag_node = tree.add(f"[bright_cyan]{tag}[/] ({count} occurrences)")

        # Find most common co-occurrences
        if tag in stats["co_occurrence"]:
            co_occurring = stats["co_occurrence"][tag].most_common(3)
            if co_occurring:
                tag_node.add(
                    f"[dim]Often paired with:[/] {', '.join(f'{t} ({c}×)' for t, c in co_occurring)}"
                )

                # Show example memory
                example = stats["memories_by_tag"][tag][0]
                example_title = (example.title or "Untitled")[:50]
                tag_node.add(f"[dim]Example: \"{example_title}\"[/]")

    console.print(tree)
    console.print()

    # Orphaned tags (never co-occur)
    orphaned = [tag for tag, count in filtered_tags.items() if not stats["co_occurrence"][tag]]
    if orphaned:
        print_section(f"Orphaned Tags ({len(orphaned)}) - Never appear with other tags")
        for tag in orphaned[:10]:
            count = filtered_tags[tag]
            console.print(f"  • {tag} ({count} occurrence{'s' if count != 1 else ''})")
        if len(orphaned) > 10:
            console.print(f"  [dim]... and {len(orphaned) - 10} more[/]")
        console.print()


@click.command("tags")
@click.option("--min-count", type=int, default=1, help="Minimum tag occurrences to display")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    default="both",
    help="Filter by scope",
)
@click.pass_obj
def tags_cmd(manager: MemoryManager, min_count: int, scope: str):
    """Display tag cloud and relationship network."""
    # Search all memories
    memories = manager.search_memory()

    # Filter by scope
    if scope and scope != "both":
        memories = [m for m in memories if m.scope.value == scope]

    # Render tag cloud and network
    render_tag_cloud(memories, min_count=min_count)
