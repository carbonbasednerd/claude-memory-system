"""Shared utilities for memory visualization."""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.style import Style
from rich.text import Text

# Shared console instance
console = Console()

# Color scheme
COLORS = {
    "global": "blue",
    "project": "green",
    "session": "cyan",
    "decision": "yellow",
    "pattern": "magenta",
    "skill": "red",
    "highlight": "bold bright_white",
    "muted": "dim",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "accent": "bright_cyan",
}

# Styles
STYLES = {
    "global": Style(color="blue"),
    "project": Style(color="green"),
    "session": Style(color="cyan"),
    "decision": Style(color="yellow"),
    "pattern": Style(color="magenta"),
    "skill": Style(color="red"),
    "title": Style(bold=True, color="bright_white"),
    "subtitle": Style(color="bright_cyan"),
    "muted": Style(dim=True),
    "highlight": Style(bold=True, color="bright_white"),
    "tag": Style(color="bright_blue"),
    "accessed": Style(color="bright_green"),
}


def format_scope(scope: str) -> Text:
    """Format scope with color coding."""
    color = COLORS.get(scope, "white")
    return Text(scope, style=color)


def format_type(type_name: str) -> Text:
    """Format memory type with color coding."""
    color = COLORS.get(type_name, "white")
    return Text(type_name, style=color)


def format_date(date: datetime) -> str:
    """Format datetime as YYYY-MM-DD."""
    return date.strftime("%Y-%m-%d")


def format_datetime(date: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM."""
    return date.strftime("%Y-%m-%d %H:%M")


def format_access_count(count: int, highlight_threshold: int = 5) -> Text:
    """Format access count with visual indicator for high access."""
    if count == 0:
        return Text(f"{count}×", style="dim")
    elif count >= highlight_threshold:
        return Text(f"{count}× ⭐", style="bright_green bold")
    else:
        return Text(f"{count}×", style="bright_green")


def format_tags(tags: list[str], max_display: int = 5) -> Text:
    """Format tags with consistent styling."""
    if not tags:
        return Text("(no tags)", style="dim")

    display_tags = tags[:max_display]
    text = Text()

    for i, tag in enumerate(display_tags):
        text.append(tag, style="bright_blue")
        if i < len(display_tags) - 1:
            text.append(" | ", style="dim")

    if len(tags) > max_display:
        text.append(f" +{len(tags) - max_display} more", style="dim")

    return text


def format_relative_time(date: datetime) -> str:
    """Format datetime as relative time (e.g., '2 days ago')."""
    now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
    delta = now - date

    if delta.days == 0:
        if delta.seconds < 60:
            return "just now"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
    elif delta.days == 1:
        return "yesterday"
    elif delta.days < 7:
        return f"{delta.days}d ago"
    elif delta.days < 30:
        weeks = delta.days // 7
        return f"{weeks}w ago"
    elif delta.days < 365:
        months = delta.days // 30
        return f"{months}mo ago"
    else:
        years = delta.days // 365
        return f"{years}y ago"


def create_progress_bar(value: int, max_value: int, width: int = 20) -> str:
    """Create a simple ASCII progress bar."""
    if max_value == 0:
        return "█" * 0

    filled = int((value / max_value) * width)
    return "█" * filled


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_count(count: int) -> Text:
    """Format file count with styling."""
    if count == 0:
        return Text("0 files", style="dim")
    return Text(f"{count} file{'s' if count != 1 else ''}", style="cyan")


def format_decision_count(count: int) -> Text:
    """Format decision count with styling."""
    if count == 0:
        return Text("0 decisions", style="dim")
    return Text(f"{count} decision{'s' if count != 1 else ''}", style="yellow")


def print_header(title: str, subtitle: Optional[str] = None):
    """Print a formatted header."""
    console.print()
    console.print(title, style="bold bright_white")
    if subtitle:
        console.print(subtitle, style="dim")
    console.rule(style="dim")
    console.print()


def print_section(title: str):
    """Print a section header."""
    console.print()
    console.print(title, style="bold cyan")
