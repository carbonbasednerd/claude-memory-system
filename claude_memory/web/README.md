# Claude Memory Web Dashboard

Interactive web-based visualization dashboard for the Claude Memory System.

## Features

### Phase 1 (Implemented)

- **Multi-tab Interface**: Overview, Timeline, Tags, and Search tabs
- **Interactive Timeline**: Plotly scatter chart with zoom, pan, hover details
- **Statistics Dashboard**: Metrics, charts, and top memories
- **Tag Analysis**: Frequency bars and co-occurrence tables
- **Advanced Search**: Full-text search with sidebar filters
- **Session Details**: Click any memory to view full content
- **Sidebar Filters**:
  - Scope (global/project/both)
  - Memory types (multiselect)
  - Tags (multiselect)
  - Date range (presets + custom)
  - Access count (presets + custom range)

### Phase 2 (Future)

- Tag network force-directed graph
- Access heatmap visualization
- Activity trends with moving averages
- Enhanced export (JSON, Markdown, CSV)

### Phase 3 (Future)

- Static HTML export
- PDF report generation
- Docker deployment

## Installation

```bash
pip install -e ".[web]"
```

This installs:
- Streamlit 1.53+ (web framework)
- Plotly 6.5+ (interactive charts)
- Pandas 2.3+ (data manipulation)
- NetworkX 3.6+ (tag networks)
- Kaleido 1.2+ (chart export)

## Usage

```bash
# Launch dashboard (opens browser)
claude-memory web

# Custom port
claude-memory web --port 8080

# Don't open browser
claude-memory web --no-open
```

Dashboard runs at `http://localhost:8501` (or your custom port).

## Architecture

```
claude_memory/web/
├── app.py                      # Main Streamlit app
├── data_loader.py              # Cached data loading
├── components/
│   ├── filters.py              # Sidebar filters
│   ├── stats_overview.py       # Statistics dashboard
│   ├── session_detail.py       # Session detail view
│   └── tag_cloud.py            # Tag analysis
├── charts/
│   └── plotly_timeline.py      # Timeline visualization
└── utils/
    ├── transformers.py         # Data transformations
    └── formatters.py           # Formatting utilities
```

## Design Principles

1. **Reuse Calculations**: Uses existing `calculate_stats()` and `calculate_tag_stats()` from viz module
2. **New Rendering**: Purpose-built Streamlit/Plotly UI (different paradigm from Rich terminal UI)
3. **Caching**: 5-minute TTL on data loading for performance
4. **Client-Side Filtering**: All filtering happens in-browser on loaded data
5. **Progressive Enhancement**: MVP first, advanced features in later phases

## Development

### Adding New Charts

1. Create chart function in `charts/` (returns Plotly Figure)
2. Call from appropriate tab in `app.py`
3. Add filters if needed in `components/filters.py`

### Adding New Components

1. Create component file in `components/`
2. Implement `render(memories)` function
3. Import in `components/__init__.py`
4. Use in `app.py` tabs

### Testing

```bash
# Run Streamlit in development mode
streamlit run claude_memory/web/app.py --server.runOnSave true
```

## Performance

- Handles 100+ memories smoothly
- 5-minute cache reduces reload time
- For 1000+ memories, consider:
  - Pagination
  - Scattergl for large charts
  - Monthly aggregation
  - Default to last 90 days with "Load All" option

## Known Limitations

- Requires browser (not terminal-only)
- Port conflicts if multiple instances
- No static export yet (Phase 3)
- Large datasets may need optimization
