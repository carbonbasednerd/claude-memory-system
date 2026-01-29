"""Formatting utilities for web dashboard."""

from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime], format: str = '%Y-%m-%d %H:%M') -> str:
    """Format datetime object to string.

    Args:
        dt: Datetime object
        format: strftime format string

    Returns:
        Formatted datetime string, or 'Never' if dt is None
    """
    if dt is None:
        return 'Never'
    return dt.strftime(format)


def format_date_short(dt: Optional[datetime]) -> str:
    """Format datetime to short date (YYYY-MM-DD)."""
    return format_datetime(dt, '%Y-%m-%d')


def format_date_long(dt: Optional[datetime]) -> str:
    """Format datetime to long format (Mon DD, YYYY HH:MM)."""
    return format_datetime(dt, '%b %d, %Y %H:%M')


def format_tags(tags: list[str]) -> str:
    """Format tag list as comma-separated string.

    Args:
        tags: List of tag strings

    Returns:
        Comma-separated tag string, or 'None' if empty
    """
    if not tags:
        return 'None'
    return ', '.join(tags)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with '...' if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'
