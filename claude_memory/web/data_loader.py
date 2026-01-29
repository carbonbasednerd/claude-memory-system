"""Data loading with caching for web dashboard."""

import streamlit as st
from typing import Optional

from claude_memory.memory import MemoryManager
from claude_memory.models import MemoryEntry
from claude_memory.viz.stats import calculate_stats
from claude_memory.viz.tags import calculate_tag_stats


@st.cache_data(ttl=300)
def load_memory_data(
    scope: str = "both",
    type_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
) -> list[MemoryEntry]:
    """Load memory data from MemoryManager with caching.

    Data is cached for 5 minutes (TTL=300s) to improve performance.

    Args:
        scope: Memory scope - 'global', 'project', or 'both'
        type_filter: Optional memory type filter
        tag_filter: Optional tag filter

    Returns:
        List of MemoryEntry objects matching filters
    """
    from claude_memory.models import MemoryScope, MemoryType

    manager = MemoryManager()

    # Convert scope string to enum
    scope_enum = None
    if scope == "global":
        scope_enum = MemoryScope.GLOBAL
    elif scope == "project":
        scope_enum = MemoryScope.PROJECT

    # Convert type string to enum if provided
    type_enum = None
    if type_filter:
        type_enum = MemoryType(type_filter)

    # Convert tag string to list if provided
    tags_list = [tag_filter] if tag_filter else None

    memories = manager.search_memory(
        query="",
        tags=tags_list,
        memory_type=type_enum,
        scope=scope_enum,
    )
    return memories


def get_stats(memories: list[MemoryEntry]) -> dict:
    """Calculate statistics for memories.

    Note: Not cached because calculate_stats returns non-serializable objects
    (defaultdict with lambdas). The memory data itself is cached, so this is fast.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Dictionary with calculated statistics in web-friendly format
    """
    # Get raw stats from viz module
    raw_stats = calculate_stats(memories)

    # Convert to web-friendly format
    stats = {
        'total_memories': raw_stats.get('total', 0),
        'total_accesses': raw_stats.get('total_accesses', 0),
        'total_tags': len(raw_stats.get('tags', {})),
        'scope_breakdown': dict(raw_stats.get('by_scope', {})),
        'by_type': dict(raw_stats.get('by_type', {})),
        'most_accessed': raw_stats.get('most_accessed', []),
        'never_accessed': raw_stats.get('never_accessed', []),
    }

    return stats


def get_tag_stats(memories: list[MemoryEntry]) -> dict:
    """Calculate tag statistics.

    Note: Not cached to avoid serialization issues with Counter objects.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Dictionary with tag statistics
    """
    return calculate_tag_stats(memories)


def clear_cache():
    """Clear all cached data to force reload."""
    st.cache_data.clear()
