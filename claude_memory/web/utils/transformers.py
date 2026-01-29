"""Data transformation utilities for web dashboard."""

import pandas as pd
from datetime import datetime
from typing import Any

from claude_memory.models import MemoryEntry


def memories_to_dataframe(memories: list[MemoryEntry]) -> pd.DataFrame:
    """Convert list of MemoryEntry objects to pandas DataFrame.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        DataFrame with columns: id, title, type, scope, created, tags,
        access_count, last_accessed, file_path
    """
    if not memories:
        return pd.DataFrame(columns=[
            'id', 'title', 'type', 'scope', 'created', 'tags',
            'access_count', 'last_accessed', 'file_path'
        ])

    data = []
    for mem in memories:
        data.append({
            'id': mem.id,
            'title': mem.title,
            'type': mem.type,
            'scope': mem.scope,
            'created': mem.created,
            'tags': mem.tags,
            'access_count': mem.access.count,
            'last_accessed': mem.access.last_accessed,
            'file_path': mem.file,
        })

    df = pd.DataFrame(data)

    # Ensure created is datetime
    if not df.empty and 'created' in df.columns:
        df['created'] = pd.to_datetime(df['created'])
        if 'last_accessed' in df.columns:
            df['last_accessed'] = pd.to_datetime(df['last_accessed'])

    return df


def memory_to_dict(memory: MemoryEntry) -> dict[str, Any]:
    """Convert a single MemoryEntry to a dictionary for display.

    Args:
        memory: MemoryEntry object

    Returns:
        Dictionary with formatted fields
    """
    return {
        'ID': memory.id,
        'Title': memory.title,
        'Type': memory.type,
        'Scope': memory.scope,
        'Created': memory.created.strftime('%Y-%m-%d %H:%M'),
        'Tags': ', '.join(memory.tags) if memory.tags else 'None',
        'Access Count': memory.access.count,
        'Last Accessed': memory.access.last_accessed.strftime('%Y-%m-%d %H:%M') if memory.access.last_accessed else 'Never',
        'File Path': memory.file,
    }


def get_tag_frequencies(memories: list[MemoryEntry]) -> dict[str, int]:
    """Calculate tag frequencies across all memories.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Dictionary mapping tag -> frequency count
    """
    tag_counts = {}
    for mem in memories:
        for tag in mem.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))


def get_type_counts(memories: list[MemoryEntry]) -> dict[str, int]:
    """Calculate memory type frequencies.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Dictionary mapping type -> count
    """
    type_counts = {}
    for mem in memories:
        type_counts[mem.type] = type_counts.get(mem.type, 0) + 1

    return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
