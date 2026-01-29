"""Interactive timeline chart using Plotly."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from claude_memory.models import MemoryEntry
from claude_memory.web.utils.transformers import memories_to_dataframe


def create_timeline_chart(memories: list[MemoryEntry]) -> go.Figure:
    """Create interactive Plotly timeline scatter plot.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Plotly Figure object with interactive timeline
    """
    if not memories:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No memories to display",
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
            height=400,
        )
        return fig

    df = memories_to_dataframe(memories)

    # Create color scale based on access count
    max_access = df['access_count'].max() if df['access_count'].max() > 0 else 1

    # Create hover text
    df['hover_text'] = df.apply(
        lambda row: (
            f"<b>{row['title']}</b><br>"
            f"Type: {row['type']}<br>"
            f"Scope: {row['scope']}<br>"
            f"Tags: {', '.join(row['tags']) if row['tags'] else 'None'}<br>"
            f"Accesses: {row['access_count']}<br>"
            f"Created: {row['created'].strftime('%Y-%m-%d %H:%M')}"
        ),
        axis=1
    )

    # Create scatter plot
    fig = px.scatter(
        df,
        x='created',
        y='type',
        color='access_count',
        size='access_count',
        hover_data={'hover_text': True, 'created': False, 'type': False, 'access_count': False},
        color_continuous_scale='Viridis',
        size_max=20,
        title='Memory Timeline',
    )

    # Update hover template to use our custom hover text
    fig.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>',
        customdata=df[['hover_text']].values,
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Created Date',
        yaxis_title='Memory Type',
        height=500,
        hovermode='closest',
        showlegend=False,
        coloraxis_colorbar=dict(
            title="Access<br>Count",
            thicknessmode="pixels",
            thickness=15,
        ),
    )

    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
    )
    fig.update_yaxes(
        categoryorder='total ascending',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
    )

    return fig


def create_mini_timeline(memories: list[MemoryEntry], height: int = 200) -> go.Figure:
    """Create a compact timeline for overview tab.

    Args:
        memories: List of MemoryEntry objects
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    if not memories:
        fig = go.Figure()
        fig.add_annotation(
            text="No memories",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        return fig

    df = memories_to_dataframe(memories)

    # Simple line chart showing memory creation over time
    df_daily = df.groupby(df['created'].dt.date).size().reset_index(name='count')
    df_daily.columns = ['date', 'count']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily['date'],
        y=df_daily['count'],
        mode='lines+markers',
        name='Memories',
        line=dict(color='#636EFA', width=2),
        marker=dict(size=6),
        hovertemplate='%{x}<br>Memories created: %{y}<extra></extra>',
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis_title='',
        yaxis_title='Count',
        showlegend=False,
        hovermode='x unified',
    )

    return fig
