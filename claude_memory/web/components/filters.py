"""Filter sidebar component for dashboard."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional

from claude_memory.models import MemoryEntry


def render_filter_sidebar(all_memories: list[MemoryEntry]) -> dict:
    """Render filter sidebar and return filter configuration.

    Args:
        all_memories: All available memories (for extracting filter options)

    Returns:
        Dictionary with filter configuration
    """
    st.sidebar.header("Filters")

    # Scope filter
    scope = st.sidebar.selectbox(
        "Scope",
        options=["both", "global", "project"],
        index=0,
        help="Filter by memory scope"
    )

    # Type filter
    available_types = sorted(set(m.type for m in all_memories))
    selected_types = st.sidebar.multiselect(
        "Memory Types",
        options=available_types,
        default=[],
        help="Select memory types to include (empty = all)"
    )

    # Tag filter
    all_tags = sorted(set(tag for m in all_memories for tag in m.tags))
    selected_tags = st.sidebar.multiselect(
        "Tags",
        options=all_tags,
        default=[],
        help="Select tags to filter by (empty = all)"
    )

    # Date range filter
    st.sidebar.subheader("Date Range")

    if all_memories:
        min_date = min(m.created for m in all_memories).date()
        max_date = max(m.created for m in all_memories).date()
    else:
        min_date = datetime.now().date() - timedelta(days=90)
        max_date = datetime.now().date()

    date_preset = st.sidebar.selectbox(
        "Preset",
        options=["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"],
        index=0,
    )

    if date_preset == "Custom":
        date_from = st.sidebar.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
        )
        date_to = st.sidebar.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
        )
    elif date_preset == "Last 7 Days":
        date_from = datetime.now().date() - timedelta(days=7)
        date_to = datetime.now().date()
    elif date_preset == "Last 30 Days":
        date_from = datetime.now().date() - timedelta(days=30)
        date_to = datetime.now().date()
    elif date_preset == "Last 90 Days":
        date_from = datetime.now().date() - timedelta(days=90)
        date_to = datetime.now().date()
    else:  # All Time
        date_from = None
        date_to = None

    # Access count filter
    st.sidebar.subheader("Access Count")

    if all_memories:
        max_accesses = max(m.access.count for m in all_memories)
    else:
        max_accesses = 0

    access_preset = st.sidebar.selectbox(
        "Preset",
        options=["All", "Never Accessed", "Accessed (1+)", "Popular (5+)", "Very Popular (10+)", "Custom Range"],
        index=0,
    )

    if access_preset == "Custom Range":
        min_accesses = st.sidebar.number_input(
            "Min Accesses",
            min_value=0,
            max_value=max_accesses,
            value=0,
        )
        max_accesses_filter = st.sidebar.number_input(
            "Max Accesses",
            min_value=0,
            max_value=max_accesses,
            value=max_accesses,
        )
    elif access_preset == "Never Accessed":
        min_accesses = 0
        max_accesses_filter = 0
    elif access_preset == "Accessed (1+)":
        min_accesses = 1
        max_accesses_filter = max_accesses
    elif access_preset == "Popular (5+)":
        min_accesses = 5
        max_accesses_filter = max_accesses
    elif access_preset == "Very Popular (10+)":
        min_accesses = 10
        max_accesses_filter = max_accesses
    else:  # All
        min_accesses = 0
        max_accesses_filter = max_accesses

    # Refresh button
    st.sidebar.divider()
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        from claude_memory.web.data_loader import clear_cache
        clear_cache()
        st.rerun()

    return {
        'scope': scope,
        'types': selected_types,
        'tags': selected_tags,
        'date_from': date_from,
        'date_to': date_to,
        'min_accesses': min_accesses,
        'max_accesses': max_accesses_filter,
    }


def apply_filters(memories: list[MemoryEntry], config: dict) -> list[MemoryEntry]:
    """Apply filter configuration to memories.

    Args:
        memories: List of MemoryEntry objects
        config: Filter configuration from render_filter_sidebar()

    Returns:
        Filtered list of memories
    """
    filtered = memories

    # Apply type filter
    if config['types']:
        filtered = [m for m in filtered if m.type in config['types']]

    # Apply tag filter
    if config['tags']:
        filtered = [m for m in filtered if any(tag in m.tags for tag in config['tags'])]

    # Apply date range filter
    if config['date_from']:
        date_from = datetime.combine(config['date_from'], datetime.min.time())
        filtered = [m for m in filtered if m.created >= date_from]

    if config['date_to']:
        date_to = datetime.combine(config['date_to'], datetime.max.time())
        filtered = [m for m in filtered if m.created <= date_to]

    # Apply access count filter
    filtered = [
        m for m in filtered
        if config['min_accesses'] <= m.access.count <= config['max_accesses']
    ]

    return filtered
