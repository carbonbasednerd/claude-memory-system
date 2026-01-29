"""Tag network graph using NetworkX and Plotly."""

import networkx as nx
import plotly.graph_objects as go
from collections import defaultdict

from claude_memory.models import MemoryEntry


def create_tag_network(memories: list[MemoryEntry], min_cooccurrence: int = 2) -> go.Figure:
    """Create force-directed tag network graph showing relationships.

    Args:
        memories: List of MemoryEntry objects
        min_cooccurrence: Minimum co-occurrence count to show edge

    Returns:
        Plotly Figure object with network graph
    """
    if not memories:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No memories to visualize",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=600,
        )
        return fig

    # Build tag co-occurrence graph
    G = nx.Graph()

    # Count tag frequencies for node sizing
    tag_freq = defaultdict(int)
    for mem in memories:
        for tag in mem.tags:
            tag_freq[tag] += 1
            G.add_node(tag, frequency=tag_freq[tag])

    # Count tag co-occurrences for edges
    cooccurrence = defaultdict(int)
    for mem in memories:
        if len(mem.tags) < 2:
            continue
        tags_sorted = sorted(mem.tags)
        for i in range(len(tags_sorted)):
            for j in range(i + 1, len(tags_sorted)):
                pair = (tags_sorted[i], tags_sorted[j])
                cooccurrence[pair] += 1

    # Add edges for significant co-occurrences
    for (tag1, tag2), count in cooccurrence.items():
        if count >= min_cooccurrence:
            G.add_edge(tag1, tag2, weight=count)

    # If graph is empty or has no edges, show message
    if len(G.nodes()) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No tags found in memories",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=600,
        )
        return fig

    if len(G.edges()) == 0:
        # Show nodes without edges (isolated tags)
        fig = go.Figure()
        fig.add_annotation(
            text=f"No tag co-occurrences ≥ {min_cooccurrence}\nTry lowering the threshold",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=600,
        )
        return fig

    # Use spring layout for positioning
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

    # Create edge traces
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2].get('weight', 1)

        # Edge line
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=min(weight * 0.5, 5),  # Scale width by weight
                color='rgba(125, 125, 125, 0.3)'
            ),
            hoverinfo='none',
            showlegend=False,
        )
        edge_traces.append(edge_trace)

    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Get node data
        freq = G.nodes[node].get('frequency', 0)
        connections = len(list(G.neighbors(node)))

        node_text.append(
            f"<b>{node}</b><br>"
            f"Frequency: {freq}<br>"
            f"Connections: {connections}"
        )

        # Size by frequency
        node_size.append(10 + freq * 3)

        # Color by number of connections
        node_color.append(connections)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Connections",
                thickness=15,
                xanchor='left',
            ),
            line=dict(width=2, color='white'),
        ),
        text=[node for node in G.nodes()],
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=node_text,
        showlegend=False,
    )

    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title=dict(
            text=f'Tag Network Graph ({len(G.nodes())} tags, {len(G.edges())} connections)',
            x=0.5,
            xanchor='center',
        ),
        showlegend=False,
        hovermode='closest',
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig


def create_simple_tag_network(memories: list[MemoryEntry], max_tags: int = 30) -> go.Figure:
    """Create a simplified tag network showing only top tags.

    Args:
        memories: List of MemoryEntry objects
        max_tags: Maximum number of tags to show

    Returns:
        Plotly Figure object
    """
    # Get tag frequencies
    tag_freq = defaultdict(int)
    for mem in memories:
        for tag in mem.tags:
            tag_freq[tag] += 1

    # Get top tags
    top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:max_tags]
    top_tag_names = {tag for tag, _ in top_tags}

    # Filter memories to only include top tags
    filtered_memories = []
    for mem in memories:
        filtered_tags = [t for t in mem.tags if t in top_tag_names]
        if len(filtered_tags) >= 1:
            # Create a copy with filtered tags
            filtered_mem = mem.model_copy()
            filtered_mem.tags = filtered_tags
            filtered_memories.append(filtered_mem)

    return create_tag_network(filtered_memories, min_cooccurrence=1)
