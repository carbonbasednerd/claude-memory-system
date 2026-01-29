"""Project map visualization."""

from collections import Counter
from pathlib import Path
from typing import Optional

import click
from rich.tree import Tree

from claude_memory.memory import MemoryManager
from claude_memory.models import MemoryScope
from claude_memory.viz.utils import (
    console,
    format_access_count,
    format_date,
    print_header,
    truncate_text,
)


def find_all_projects() -> list[Path]:
    """Find all directories containing .claude folders."""
    projects = []

    # Start from home directory and common code directories
    search_paths = [
        Path.home(),
        Path.home() / "git",
        Path.home() / "projects",
        Path.home() / "code",
        Path.home() / "dev",
        Path.home() / "workspace",
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Find .claude directories (limit depth to avoid scanning entire filesystem)
        try:
            for claude_dir in search_path.rglob(".claude"):
                if claude_dir.is_dir() and (claude_dir.parent not in projects):
                    projects.append(claude_dir.parent)
        except (PermissionError, OSError):
            # Skip directories we can't access
            continue

    return sorted(projects)


def analyze_project(project_path: Path) -> Optional[dict]:
    """Analyze a single project's memory."""
    claude_dir = project_path / ".claude"
    if not claude_dir.exists():
        return None

    # Create memory manager for this project
    try:
        manager = MemoryManager(project_path)
        if not manager.project_index:
            return None

        # Search project memories only
        memories = [m for m in manager.search_memory() if m.scope == MemoryScope.PROJECT]

        if not memories:
            return None

        # Calculate stats
        total_sessions = len(memories)
        total_accesses = sum(m.access.count if m.access else 0 for m in memories)
        total_decisions = sum(len(m.decisions) if m.decisions else 0 for m in memories)

        # Find most recent
        most_recent = max(memories, key=lambda m: m.created if m.created else m.updated)

        # Find most accessed
        most_accessed = max(memories, key=lambda m: m.access.count if m.access else 0)

        # Top tags
        all_tags = []
        for m in memories:
            if m.tags:
                all_tags.extend(m.tags)
        top_tags = Counter(all_tags).most_common(5)

        return {
            "path": project_path,
            "total_sessions": total_sessions,
            "total_accesses": total_accesses,
            "total_decisions": total_decisions,
            "most_recent": most_recent,
            "most_accessed": most_accessed,
            "top_tags": top_tags,
        }

    except Exception:
        # Skip projects with corrupted or incompatible memory
        return None


def render_project_map():
    """Render project memory map."""
    print_header("Project Memory Map", "Scanning for .claude directories...")

    # Find all projects
    projects = find_all_projects()

    if not projects:
        console.print("No projects with memory found.", style="yellow")
        return

    # Analyze each project
    project_stats = []
    for project in projects:
        stats = analyze_project(project)
        if stats:
            project_stats.append(stats)

    if not project_stats:
        console.print("No projects with valid memory found.", style="yellow")
        return

    # Sort by most recent activity
    project_stats.sort(key=lambda p: p["most_recent"].created, reverse=True)

    console.print(f"Found {len(project_stats)} active project{'s' if len(project_stats) != 1 else ''} with memory")
    console.print()

    # Build tree
    tree = Tree("[bold]Projects[/]", hide_root=True)

    total_sessions = 0
    total_accesses = 0

    for stats in project_stats:
        # Project node
        project_name = stats["path"].name
        project_path_str = str(stats["path"])

        # Shorten path if too long
        if len(project_path_str) > 60:
            project_path_str = "..." + project_path_str[-57:]

        node_label = f"[bold bright_cyan]{project_name}[/] [dim]({project_path_str})[/]"
        project_node = tree.add(node_label)

        # Stats
        sessions = stats["total_sessions"]
        accesses = stats["total_accesses"]
        decisions = stats["total_decisions"]

        total_sessions += sessions
        total_accesses += accesses

        stats_text = f"Sessions: {sessions} | Decisions: {decisions} | Total Accesses: {accesses}"
        project_node.add(stats_text)

        # Most recent
        recent = stats["most_recent"]
        recent_title = truncate_text(recent.title or "Untitled", 50)
        recent_date = format_date(recent.created) if recent.created else "Unknown"
        project_node.add(f"Most recent: {recent_date} - {recent_title}")

        # Most accessed
        accessed = stats["most_accessed"]
        if accessed.access and accessed.access.count > 0:
            accessed_title = truncate_text(accessed.title or "Untitled", 50)
            access_text = format_access_count(accessed.access.count)
            project_node.add(f"Most accessed: {accessed_title} ({access_text})")

        # Top tags
        if stats["top_tags"]:
            tags_str = ", ".join(f"{tag} ({count})" for tag, count in stats["top_tags"])
            project_node.add(f"Top tags: {tags_str}")

    console.print(tree)
    console.print()

    # Summary
    console.print(f"[bold]Total:[/] {len(project_stats)} projects | {total_sessions} sessions | {total_accesses} accesses")
    console.print()


@click.command("projects")
@click.pass_obj
def projects_cmd(manager: MemoryManager):
    """Display project memory map."""
    render_project_map()
