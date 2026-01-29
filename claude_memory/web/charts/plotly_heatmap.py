"""Access heatmap visualization using Plotly."""

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from claude_memory.models import MemoryEntry


def create_access_heatmap(memories: list[MemoryEntry], days: int = 90) -> go.Figure:
    """Create heatmap showing memory access patterns over time.

    Args:
        memories: List of MemoryEntry objects
        days: Number of days to show (default 90)

    Returns:
        Plotly Figure object with heatmap
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

    # Create date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Build data structure: date -> memory_id -> access_count
    access_data = defaultdict(lambda: defaultdict(int))

    # Track which memories were accessed on which days
    for mem in memories:
        # Count creation as an "access"
        if mem.created:
            created_date = mem.created.date()
            if start_date <= created_date <= end_date:
                access_data[created_date][mem.id] += 1

        # Count actual accesses
        if mem.access.last_accessed:
            access_date = mem.access.last_accessed.date()
            if start_date <= access_date <= end_date:
                access_data[access_date][mem.id] += mem.access.count

    # Create matrix: rows = memories, cols = dates
    dates = [start_date + timedelta(days=i) for i in range(days + 1)]
    memory_ids = [m.id for m in sorted(memories, key=lambda x: x.created, reverse=True)]

    # Build matrix
    matrix = []
    hover_text = []

    for mem in sorted(memories, key=lambda x: x.created, reverse=True):
        row = []
        hover_row = []
        for date in dates:
            count = access_data[date].get(mem.id, 0)
            row.append(count)
            hover_row.append(
                f"<b>{mem.title[:30]}</b><br>"
                f"Date: {date}<br>"
                f"Accesses: {count}"
            )
        matrix.append(row)
        hover_text.append(hover_row)

    # Create labels for y-axis (truncated memory titles)
    y_labels = [m.title[:30] + ('...' if len(m.title) > 30 else '')
                for m in sorted(memories, key=lambda x: x.created, reverse=True)]

    # Create x-axis labels (dates, show every 7th day)
    x_labels = []
    for i, date in enumerate(dates):
        if i % 7 == 0 or i == len(dates) - 1:
            x_labels.append(date.strftime('%m/%d'))
        else:
            x_labels.append('')

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[d.strftime('%Y-%m-%d') for d in dates],
        y=y_labels,
        colorscale='Blues',
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text,
        showscale=True,
        colorbar=dict(title="Accesses"),
    ))

    fig.update_layout(
        title=f'Memory Access Heatmap (Last {days} Days)',
        xaxis_title='Date',
        yaxis_title='Memory',
        height=max(400, len(memories) * 20),
        xaxis=dict(
            tickmode='array',
            tickvals=[dates[i].strftime('%Y-%m-%d') for i in range(0, len(dates), 7)],
            ticktext=[dates[i].strftime('%m/%d') for i in range(0, len(dates), 7)],
        ),
        yaxis=dict(
            tickmode='linear',
            autorange='reversed',
        ),
    )

    return fig


def create_activity_calendar(memories: list[MemoryEntry], days: int = 90) -> go.Figure:
    """Create calendar-style heatmap showing daily activity.

    Args:
        memories: List of MemoryEntry objects
        days: Number of days to show

    Returns:
        Plotly Figure object with calendar heatmap
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

    # Count activities per day
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    daily_counts = defaultdict(int)
    daily_accesses = defaultdict(int)

    for mem in memories:
        # Count memory creations
        if mem.created:
            created_date = mem.created.date()
            if start_date <= created_date <= end_date:
                daily_counts[created_date] += 1

        # Count accesses
        if mem.access.last_accessed:
            access_date = mem.access.last_accessed.date()
            if start_date <= access_date <= end_date:
                daily_accesses[access_date] += mem.access.count

    # Create data for calendar
    dates = []
    counts = []
    accesses = []
    hover_text = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        count = daily_counts[current_date]
        access_count = daily_accesses[current_date]
        counts.append(count)
        accesses.append(access_count)

        hover_text.append(
            f"<b>{current_date.strftime('%Y-%m-%d')}</b><br>"
            f"Memories Created: {count}<br>"
            f"Total Accesses: {access_count}"
        )
        current_date += timedelta(days=1)

    # Create scatter plot with markers sized by activity
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=[1] * len(dates),  # All on same line
        mode='markers',
        marker=dict(
            size=[5 + c * 5 for c in counts],  # Size by creation count
            color=accesses,  # Color by access count
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Accesses"),
            line=dict(width=1, color='white'),
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text,
        showlegend=False,
    ))

    fig.update_layout(
        title=f'Activity Calendar (Last {days} Days)',
        xaxis_title='Date',
        height=200,
        yaxis=dict(visible=False),
        hovermode='closest',
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig
