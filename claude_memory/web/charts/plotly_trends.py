"""Activity trends and time series analysis using Plotly."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from claude_memory.models import MemoryEntry


def create_activity_trends(memories: list[MemoryEntry], days: int = 90) -> go.Figure:
    """Create line chart showing memory creation and access trends.

    Args:
        memories: List of MemoryEntry objects
        days: Number of days to analyze

    Returns:
        Plotly Figure object with trend lines
    """
    if not memories:
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
            height=400,
        )
        return fig

    # Build time series data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Count daily activities
    daily_created = defaultdict(int)
    daily_accesses = defaultdict(int)

    for mem in memories:
        # Count creations
        if mem.created:
            created_date = mem.created.date()
            if start_date <= created_date <= end_date:
                daily_created[created_date] += 1

        # Count accesses
        if mem.access.last_accessed:
            access_date = mem.access.last_accessed.date()
            if start_date <= access_date <= end_date:
                daily_accesses[access_date] += 1

    # Create complete date range
    dates = []
    created_counts = []
    access_counts = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        created_counts.append(daily_created[current_date])
        access_counts.append(daily_accesses[current_date])
        current_date += timedelta(days=1)

    # Calculate moving averages (7-day)
    window = 7
    created_ma = pd.Series(created_counts).rolling(window=window, min_periods=1).mean()
    access_ma = pd.Series(access_counts).rolling(window=window, min_periods=1).mean()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add creation trend
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=created_counts,
            name='Memories Created',
            mode='lines',
            line=dict(color='#636EFA', width=1),
            opacity=0.3,
        ),
        secondary_y=False,
    )

    # Add creation moving average
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=created_ma,
            name='Created (7-day avg)',
            mode='lines',
            line=dict(color='#636EFA', width=3),
        ),
        secondary_y=False,
    )

    # Add access trend
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=access_counts,
            name='Memory Accesses',
            mode='lines',
            line=dict(color='#EF553B', width=1),
            opacity=0.3,
        ),
        secondary_y=True,
    )

    # Add access moving average
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=access_ma,
            name='Accesses (7-day avg)',
            mode='lines',
            line=dict(color='#EF553B', width=3),
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Memories Created", secondary_y=False)
    fig.update_yaxes(title_text="Memory Accesses", secondary_y=True)

    fig.update_layout(
        title=f'Memory Activity Trends (Last {days} Days)',
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    return fig


def create_cumulative_growth(memories: list[MemoryEntry]) -> go.Figure:
    """Create cumulative growth chart showing memory accumulation over time.

    Args:
        memories: List of MemoryEntry objects

    Returns:
        Plotly Figure object showing cumulative growth
    """
    if not memories:
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
            height=300,
        )
        return fig

    # Sort memories by creation date
    sorted_memories = sorted(
        [m for m in memories if m.created],
        key=lambda m: m.created
    )

    if not sorted_memories:
        fig = go.Figure()
        fig.add_annotation(
            text="No creation dates available",
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
            height=300,
        )
        return fig

    # Build cumulative data
    dates = [m.created for m in sorted_memories]
    cumulative = list(range(1, len(sorted_memories) + 1))

    # Separate by scope
    global_dates = []
    global_cumulative = []
    project_dates = []
    project_cumulative = []

    global_count = 0
    project_count = 0

    for mem in sorted_memories:
        if mem.scope.value == 'global':
            global_count += 1
            global_dates.append(mem.created)
            global_cumulative.append(global_count)
        else:
            project_count += 1
            project_dates.append(mem.created)
            project_cumulative.append(project_count)

    # Create figure
    fig = go.Figure()

    # Total line
    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative,
        name='Total',
        mode='lines',
        line=dict(color='#00CC96', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 204, 150, 0.1)',
    ))

    # Global line
    if global_dates:
        fig.add_trace(go.Scatter(
            x=global_dates,
            y=global_cumulative,
            name='Global',
            mode='lines',
            line=dict(color='#636EFA', width=2, dash='dash'),
        ))

    # Project line
    if project_dates:
        fig.add_trace(go.Scatter(
            x=project_dates,
            y=project_cumulative,
            name='Project',
            mode='lines',
            line=dict(color='#EF553B', width=2, dash='dash'),
        ))

    fig.update_layout(
        title='Cumulative Memory Growth',
        xaxis_title='Date',
        yaxis_title='Total Memories',
        height=300,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    return fig


def create_type_trends(memories: list[MemoryEntry], days: int = 90) -> go.Figure:
    """Create stacked area chart showing memory type trends over time.

    Args:
        memories: List of MemoryEntry objects
        days: Number of days to analyze

    Returns:
        Plotly Figure object with stacked areas by type
    """
    if not memories:
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
            height=300,
        )
        return fig

    # Build time series by type
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Count by type and date
    type_data = defaultdict(lambda: defaultdict(int))

    for mem in memories:
        if mem.created:
            created_date = mem.created.date()
            if start_date <= created_date <= end_date:
                type_data[mem.type.value][created_date] += 1

    # Create complete date range
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    # Create figure
    fig = go.Figure()

    # Add trace for each type
    colors = {
        'session': '#636EFA',
        'decision': '#EF553B',
        'implementation': '#00CC96',
        'pattern': '#AB63FA',
    }

    for mem_type in sorted(type_data.keys()):
        counts = [type_data[mem_type][date] for date in dates]

        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            name=mem_type.capitalize(),
            mode='lines',
            stackgroup='one',
            line=dict(width=0.5, color=colors.get(mem_type, '#999')),
            fillcolor=colors.get(mem_type, '#999'),
        ))

    fig.update_layout(
        title=f'Memory Types Over Time (Last {days} Days)',
        xaxis_title='Date',
        yaxis_title='Memories Created',
        height=300,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    return fig
