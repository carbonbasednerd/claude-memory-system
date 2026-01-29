"""Tag cloud and tag statistics component."""

import streamlit as st
import plotly.graph_objects as go

from claude_memory.models import MemoryEntry
from claude_memory.web.utils.transformers import get_tag_frequencies


def render(memories: list[MemoryEntry]):
    """Render tag cloud and tag statistics.

    Args:
        memories: List of MemoryEntry objects
    """
    if not memories:
        st.info("No memories to analyze tags from")
        return

    tag_freq = get_tag_frequencies(memories)

    if not tag_freq:
        st.info("No tags found in memories")
        return

    st.subheader(f"Tag Statistics ({len(tag_freq)} unique tags)")

    # Tag frequency bar chart
    st.markdown("### Most Common Tags")

    # Show top 20 tags
    top_tags = dict(list(tag_freq.items())[:20])

    fig = go.Figure(data=[
        go.Bar(
            x=list(top_tags.values()),
            y=list(top_tags.keys()),
            orientation='h',
            marker_color='#636EFA',
        )
    ])

    fig.update_layout(
        height=max(400, len(top_tags) * 25),
        margin=dict(l=150, r=20, t=20, b=40),
        xaxis_title='Frequency',
        yaxis_title='',
        showlegend=False,
        yaxis=dict(autorange='reversed'),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tag statistics table
    st.markdown("### All Tags")

    # Create table data
    table_data = []
    for tag, count in tag_freq.items():
        percentage = (count / len(memories)) * 100
        table_data.append({
            'Tag': tag,
            'Count': count,
            'Memories %': f"{percentage:.1f}%",
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True, height=400)

    # Tag co-occurrence section
    st.divider()
    st.markdown("### Tag Co-occurrence")

    # Find common tag pairs
    tag_pairs = {}
    for mem in memories:
        if len(mem.tags) < 2:
            continue
        tags_sorted = sorted(mem.tags)
        for i in range(len(tags_sorted)):
            for j in range(i + 1, len(tags_sorted)):
                pair = (tags_sorted[i], tags_sorted[j])
                tag_pairs[pair] = tag_pairs.get(pair, 0) + 1

    if tag_pairs:
        # Sort by frequency
        sorted_pairs = sorted(tag_pairs.items(), key=lambda x: x[1], reverse=True)[:15]

        pair_data = []
        for (tag1, tag2), count in sorted_pairs:
            pair_data.append({
                'Tag 1': tag1,
                'Tag 2': tag2,
                'Co-occurrence Count': count,
            })

        st.dataframe(pair_data, use_container_width=True, hide_index=True)
    else:
        st.info("No tag co-occurrences found (memories need 2+ tags)")
