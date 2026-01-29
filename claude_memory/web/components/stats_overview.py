"""Stats overview component for dashboard."""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional

from claude_memory.models import MemoryEntry
from claude_memory.web.data_loader import get_stats
from claude_memory.web.utils.transformers import get_type_counts


def render(memories: list[MemoryEntry]):
    """Render statistics overview with metrics and charts.

    Args:
        memories: List of MemoryEntry objects
    """
    if not memories:
        st.info("No memories found. Start using `claude-memory` to create memories!")
        return

    stats = get_stats(memories)

    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Memories", stats['total_memories'])

    with col2:
        st.metric("Total Accesses", stats['total_accesses'])

    with col3:
        avg_access = stats['total_accesses'] / stats['total_memories'] if stats['total_memories'] > 0 else 0
        st.metric("Avg Accesses", f"{avg_access:.1f}")

    with col4:
        st.metric("Unique Tags", stats['total_tags'])

    st.divider()

    # Second row of metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Global Memories", stats['scope_breakdown'].get('global', 0))

    with col2:
        st.metric("Project Memories", stats['scope_breakdown'].get('project', 0))

    with col3:
        never_accessed = sum(1 for m in memories if m.access.count == 0)
        st.metric("Never Accessed", never_accessed)

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Memory Types")
        type_counts = get_type_counts(memories)
        if type_counts:
            fig = go.Figure(data=[
                go.Bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    marker_color='#636EFA',
                )
            ])
            fig.update_layout(
                height=300,
                margin=dict(l=40, r=20, t=20, b=60),
                xaxis_title='',
                yaxis_title='Count',
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No type data available")

    with col2:
        st.subheader("Access Distribution")
        # Create histogram of access counts
        access_counts = [m.access.count for m in memories]
        fig = go.Figure(data=[
            go.Histogram(
                x=access_counts,
                nbinsx=20,
                marker_color='#EF553B',
            )
        ])
        fig.update_layout(
            height=300,
            margin=dict(l=40, r=20, t=20, b=60),
            xaxis_title='Access Count',
            yaxis_title='# of Memories',
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Most accessed memories
    st.subheader("Most Accessed Memories")
    top_memories = sorted(memories, key=lambda m: m.access.count, reverse=True)[:10]

    if top_memories:
        data = []
        for mem in top_memories:
            data.append({
                'Title': mem.title,
                'Type': mem.type,
                'Scope': mem.scope,
                'Accesses': mem.access.count,
                'Tags': ', '.join(mem.tags[:3]) if mem.tags else 'None',
            })
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("No memories with access data")
