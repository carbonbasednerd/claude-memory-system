"""Export functionality for web dashboard."""

import json
import io
from datetime import datetime
from pathlib import Path

from claude_memory.models import MemoryEntry


def export_to_json(memories: list[MemoryEntry]) -> str:
    """Export memories to JSON format.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        JSON string
    """
    data = []
    for mem in memories:
        data.append({
            'id': mem.id,
            'title': mem.title,
            'type': mem.type.value,
            'scope': mem.scope.value,
            'created': mem.created.isoformat() if mem.created else None,
            'updated': mem.updated.isoformat() if mem.updated else None,
            'tags': mem.tags,
            'summary': mem.summary,
            'keywords': mem.keywords,
            'triggers': mem.triggers,
            'file': mem.file,
            'access_count': mem.access.count,
            'last_accessed': mem.access.last_accessed.isoformat() if mem.access.last_accessed else None,
            'files_modified': mem.files_modified,
            'decisions': mem.decisions,
        })

    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_memories': len(memories),
        'memories': data,
    }

    return json.dumps(export_data, indent=2)


def export_to_markdown(memories: list[MemoryEntry]) -> str:
    """Export memories to Markdown format.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Markdown string
    """
    lines = []

    # Header
    lines.append("# Memory Export")
    lines.append(f"\n**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total Memories:** {len(memories)}\n")
    lines.append("---\n")

    # Memories
    for i, mem in enumerate(sorted(memories, key=lambda m: m.created, reverse=True), 1):
        lines.append(f"## {i}. {mem.title}\n")
        lines.append(f"- **ID:** `{mem.id}`")
        lines.append(f"- **Type:** {mem.type.value}")
        lines.append(f"- **Scope:** {mem.scope.value}")
        lines.append(f"- **Created:** {mem.created.strftime('%Y-%m-%d %H:%M') if mem.created else 'N/A'}")
        lines.append(f"- **Access Count:** {mem.access.count}")

        if mem.access.last_accessed:
            lines.append(f"- **Last Accessed:** {mem.access.last_accessed.strftime('%Y-%m-%d %H:%M')}")

        if mem.tags:
            lines.append(f"- **Tags:** {', '.join(mem.tags)}")

        if mem.summary:
            lines.append(f"\n**Summary:**\n{mem.summary}")

        if mem.keywords:
            lines.append(f"\n**Keywords:** {', '.join(mem.keywords)}")

        if mem.files_modified:
            lines.append(f"\n**Files Modified:** {len(mem.files_modified)}")
            for f in mem.files_modified[:5]:  # Show first 5
                lines.append(f"  - `{f}`")
            if len(mem.files_modified) > 5:
                lines.append(f"  - *...and {len(mem.files_modified) - 5} more*")

        if mem.decisions:
            lines.append(f"\n**Decisions:**")
            for decision in mem.decisions:
                lines.append(f"  - {decision}")

        lines.append("\n---\n")

    return '\n'.join(lines)


def export_to_csv(memories: list[MemoryEntry]) -> str:
    """Export memories to CSV format.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        CSV string
    """
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'ID',
        'Title',
        'Type',
        'Scope',
        'Created',
        'Updated',
        'Tags',
        'Access Count',
        'Last Accessed',
        'Summary',
        'Keywords',
        'File',
    ])

    # Data
    for mem in sorted(memories, key=lambda m: m.created, reverse=True):
        writer.writerow([
            mem.id,
            mem.title,
            mem.type.value,
            mem.scope.value,
            mem.created.isoformat() if mem.created else '',
            mem.updated.isoformat() if mem.updated else '',
            ', '.join(mem.tags) if mem.tags else '',
            mem.access.count,
            mem.access.last_accessed.isoformat() if mem.access.last_accessed else '',
            mem.summary[:200] + ('...' if len(mem.summary) > 200 else ''),  # Truncate
            ', '.join(mem.keywords) if mem.keywords else '',
            mem.file,
        ])

    return output.getvalue()


def export_stats_to_json(stats: dict) -> str:
    """Export statistics to JSON format.

    Args:
        stats: Statistics dictionary

    Returns:
        JSON string
    """
    # Convert non-serializable parts
    export_stats = {
        'export_date': datetime.now().isoformat(),
        'total_memories': stats.get('total_memories', 0),
        'total_accesses': stats.get('total_accesses', 0),
        'total_tags': stats.get('total_tags', 0),
        'scope_breakdown': stats.get('scope_breakdown', {}),
        'by_type': stats.get('by_type', {}),
    }

    return json.dumps(export_stats, indent=2)
