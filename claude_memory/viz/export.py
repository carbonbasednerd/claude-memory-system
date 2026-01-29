"""Export utilities for visualization data."""

import json
from datetime import datetime
from io import StringIO
from typing import Any, Optional

from rich.console import Console


def export_to_json(data: Any, pretty: bool = True) -> str:
    """Export data to JSON format."""

    def json_serializer(obj):
        """Custom JSON serializer for datetime and other types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    if pretty:
        return json.dumps(data, indent=2, default=json_serializer)
    else:
        return json.dumps(data, default=json_serializer)


def export_to_markdown(title: str, sections: list[tuple[str, str]]) -> str:
    """Export data to Markdown format.

    Args:
        title: Document title
        sections: List of (section_title, content) tuples
    """
    lines = []

    # Title
    lines.append(f"# {title}\n")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Sections
    for section_title, content in sections:
        lines.append(f"\n## {section_title}\n")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def export_to_html(console_output: str, title: str = "Memory Visualization") -> str:
    """Export Rich console output to HTML format."""
    # Use Rich's HTML export
    from rich.console import Console

    string_io = StringIO()
    html_console = Console(file=string_io, record=True, force_terminal=True, width=120)

    # This is a simple wrapper - the actual rendering should be done by the command
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
        <pre>{console_output}</pre>
    </div>
</body>
</html>"""

    return html_template


def memories_to_json(memories: list) -> str:
    """Convert memory entries to JSON format."""
    data = []

    for memory in memories:
        entry = {
            "id": memory.id,
            "title": memory.title,
            "type": memory.type.value,
            "scope": memory.scope.value,
            "created": memory.created.isoformat() if memory.created else None,
            "updated": memory.updated.isoformat() if memory.updated else None,
            "tags": memory.tags,
            "summary": memory.summary,
            "keywords": memory.keywords,
            "files_modified": memory.files_modified,
            "decisions": memory.decisions,
            "access": {
                "count": memory.access.count if memory.access else 0,
                "last_accessed": memory.access.last_accessed.isoformat() if memory.access and memory.access.last_accessed else None,
                "first_accessed": memory.access.first_accessed.isoformat() if memory.access and memory.access.first_accessed else None,
            } if memory.access else None,
        }
        data.append(entry)

    return export_to_json(data)


def memories_to_markdown(memories: list, title: str = "Memory Search Results") -> str:
    """Convert memory entries to Markdown format."""
    sections = []

    # Summary section
    summary = f"Total memories: {len(memories)}"
    sections.append(("Summary", summary))

    # Memories section
    entries = []
    for i, memory in enumerate(memories, 1):
        entry_lines = [
            f"### {i}. {memory.title or 'Untitled'}",
            "",
            f"- **ID**: `{memory.id}`",
            f"- **Type**: {memory.type.value}",
            f"- **Scope**: {memory.scope.value}",
            f"- **Created**: {memory.created.strftime('%Y-%m-%d') if memory.created else 'Unknown'}",
        ]

        if memory.tags:
            entry_lines.append(f"- **Tags**: {', '.join(memory.tags)}")

        if memory.access:
            entry_lines.append(f"- **Access Count**: {memory.access.count}")
            if memory.access.last_accessed:
                entry_lines.append(f"- **Last Accessed**: {memory.access.last_accessed.strftime('%Y-%m-%d')}")

        if memory.summary:
            entry_lines.append("")
            entry_lines.append(f"**Summary**: {memory.summary}")

        if memory.files_modified:
            entry_lines.append("")
            entry_lines.append(f"**Files Modified ({len(memory.files_modified)})**:")
            for file in memory.files_modified[:10]:
                entry_lines.append(f"- `{file}`")
            if len(memory.files_modified) > 10:
                entry_lines.append(f"- *(and {len(memory.files_modified) - 10} more)*")

        if memory.decisions:
            entry_lines.append("")
            entry_lines.append(f"**Decisions ({len(memory.decisions)})**:")
            for j, decision in enumerate(memory.decisions[:5], 1):
                entry_lines.append(f"{j}. {decision}")
            if len(memory.decisions) > 5:
                entry_lines.append(f"*(and {len(memory.decisions) - 5} more)*")

        entries.append("\n".join(entry_lines))

    sections.append(("Memories", "\n\n".join(entries)))

    return export_to_markdown(title, sections)


def stats_to_json(stats: dict) -> str:
    """Convert statistics to JSON format."""
    # Convert Counter objects to dicts
    export_data = {
        "total": stats.get("total", 0),
        "by_scope": dict(stats.get("by_scope", {})),
        "by_type": dict(stats.get("by_type", {})),
        "total_accesses": stats.get("total_accesses", 0),
        "tags": dict(stats.get("tags", {}).most_common(20)) if "tags" in stats else {},
    }

    # Add most accessed
    if "most_accessed" in stats:
        export_data["most_accessed"] = [
            {
                "id": mem.id,
                "title": mem.title,
                "access_count": count,
            }
            for mem, count in stats["most_accessed"][:10]
        ]

    return export_to_json(export_data)
