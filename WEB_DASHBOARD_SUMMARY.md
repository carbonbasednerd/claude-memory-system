# Claude Memory Web Dashboard - Feature Summary

**Version:** Phase 1 & 2 Complete
**Date:** 2026-01-29
**Status:** Production Ready ✅

---

## Overview

The Claude Memory Web Dashboard is an interactive, browser-based visualization tool for exploring and analyzing your Claude memory system. Built with Streamlit and Plotly, it provides rich, interactive charts and data export capabilities that complement the terminal-based `viz` commands.

## Quick Start

```bash
# Install dependencies (one-time)
pip install -e ".[web]"

# Launch dashboard
claude-memory web

# Custom port
claude-memory web --port 8080

# Don't auto-open browser
claude-memory web --no-open
```

Dashboard runs at `http://localhost:8501` by default.

---

## Features by Tab

### 📊 Tab 1: Overview

**Purpose:** High-level statistics and metrics about your memory system.

**Components:**

1. **Top Metrics Row:**
   - Total Memories
   - Total Accesses
   - Average Accesses per Memory
   - Unique Tags

2. **Second Metrics Row:**
   - Global Memories count
   - Project Memories count
   - Never Accessed count

3. **Memory Types Chart:**
   - Bar chart showing distribution (session, decision, implementation, pattern)
   - Color-coded visualization

4. **Access Distribution Histogram:**
   - Shows how many memories have X accesses
   - 20 bins for granular distribution
   - Helps identify most/least accessed memories

5. **Most Accessed Memories Table:**
   - Top 10 memories by access count
   - Shows: Title, Type, Scope, Accesses, Tags (top 3)
   - Sortable, filterable

6. **Mini Timeline:**
   - Compact line chart showing memory creation over time
   - Daily aggregation
   - Hover for details

---

### 📅 Tab 2: Timeline

**Purpose:** Chronological visualization of all memories.

**Components:**

1. **Interactive Scatter Plot:**
   - X-axis: Creation date
   - Y-axis: Memory type
   - Size: Access count (larger = more accessed)
   - Color: Access count (gradient scale)
   - **Interactions:**
     - Zoom: Click and drag to zoom into date range
     - Pan: Shift + drag to pan
     - Reset: Double-click to reset view
     - Hover: See memory details
   - Toolbar: Save, zoom, pan, reset controls

2. **Interaction Tips Panel:**
   - Built-in usage guide
   - Quick reference for chart interactions

3. **Memory List Table:**
   - All memories in table format
   - Columns: Title, Type, Scope, Created, Accesses, Tags, ID
   - Sorted by creation date (newest first)
   - Full-width, scrollable

4. **Memory Detail Viewer:**
   - Dropdown to select any memory by ID
   - Shows complete details:
     - Metadata: Type, Scope, Created
     - Access info: Count, Last Accessed
     - Tags
     - Full content (rendered Markdown or code)
     - File path

---

### 🏷️ Tab 3: Tags

**Purpose:** Analyze tag usage patterns and relationships.

**Components:**

1. **Tag Statistics Header:**
   - Total unique tags count

2. **Most Common Tags (Bar Chart):**
   - Top 20 tags by frequency
   - Horizontal bar chart
   - Height scales with tag count
   - Color: Uniform blue

3. **All Tags Table:**
   - Complete tag list with:
     - Tag name
     - Count (# of memories)
     - Percentage of total memories
   - Scrollable, searchable
   - 400px height for easy browsing

4. **Tag Co-occurrence Analysis:**
   - Shows which tags appear together
   - Top 15 tag pairs
   - Table format: Tag 1, Tag 2, Co-occurrence Count
   - Helps identify related concepts
   - Only shows pairs that appear in 2+ memories

---

### 🔍 Tab 4: Search

**Purpose:** Full-text search with live filtering.

**Components:**

1. **Search Interface:**
   - Text input field
   - Search in titles and tags (case-insensitive)
   - Search button trigger

2. **Results Display:**
   - Shows count: "X results"
   - Each result as expandable card:
     - Header: Title (Type)
     - Metadata row: Scope, Created, Accesses, Tags (top 2)
     - "View Details" button
   - Sorted by creation date (newest first)

3. **Detail View:**
   - Click "View Details" to expand
   - Shows full session detail inline
   - Same layout as Timeline detail viewer

---

### 📈 Tab 5: Analytics (Phase 2)

**Purpose:** Advanced analytics, trends, and data export.

**Components:**

#### 1. Tag Network Graph

- **Visualization:** Force-directed graph (NetworkX spring layout)
- **Nodes:** Individual tags
  - Size: Tag frequency (how many memories)
  - Color: Number of connections (gradient)
  - Label: Tag name (top-center)
- **Edges:** Tag co-occurrences
  - Width: Co-occurrence count (thicker = more common)
  - Color: Semi-transparent gray
- **Interactive Controls:**
  - Slider: Minimum co-occurrence threshold (1-10)
  - Adjusts which edges are shown
  - Default: 2 (pairs appearing 2+ times)
- **Hover:** Shows tag name, frequency, connection count
- **Use Case:** Discover tag relationships, identify tag clusters

**Example Output:**
- 54 tags → 169 network traces
- Clear visualization of tag ecosystems

#### 2. Activity Trends

- **Chart Type:** Line chart with dual y-axis
- **Time Period Selector:** 30/60/90/180/365 days
- **Data Series:**
  - Memories Created (daily, light blue)
  - Created 7-day avg (thick blue line)
  - Memory Accesses (daily, light red)
  - Accesses 7-day avg (thick red line)
- **Features:**
  - Unified hover (shows all values for date)
  - Moving averages smooth out noise
  - Separate axes prevent scale issues
- **Use Case:** Track creation vs usage patterns over time

#### 3. Cumulative Growth Chart

- **Chart Type:** Area chart with fill
- **Data:**
  - Total memories (green, filled)
  - Global memories (blue, dashed)
  - Project memories (red, dashed)
- **X-axis:** Time (all-time)
- **Y-axis:** Total count
- **Use Case:** See memory accumulation rate, compare global vs project growth

#### 4. Memory Type Trends

- **Chart Type:** Stacked area chart
- **Data:** Daily creation counts by type
- **Time Period:** Same as Activity Trends selector
- **Colors:**
  - Session: Blue
  - Decision: Red
  - Implementation: Green
  - Pattern: Purple
- **Features:**
  - Stacked layout shows total + breakdown
  - Unified hover
- **Use Case:** Understand how memory type usage evolves

#### 5. Activity Calendar

- **Chart Type:** Scatter plot with sized markers
- **Time Period:** Last 90 days
- **Data:**
  - Marker size: Memories created that day
  - Marker color: Total accesses that day
  - All on single horizontal line (calendar view)
- **Color Scale:** Viridis (dark to light)
- **Hover:** Date, memories created, total accesses
- **Use Case:** Quick visual scan of active days

#### 6. Export Data

**Three Export Formats:**

1. **JSON Export:**
   - Structured data format
   - Includes: id, title, type, scope, created, updated, tags, summary, keywords, triggers, file, access_count, last_accessed, files_modified, decisions
   - Metadata: export_date, total_memories
   - Example size: ~27KB for 20 memories
   - File format: `memories_export_YYYYMMDD_HHMMSS.json`
   - Use case: Programmatic access, backups, data processing

2. **Markdown Export:**
   - Human-readable report format
   - Header with export date and count
   - Each memory as numbered section:
     - Title as H2 heading
     - Metadata as bullet list
     - Summary, keywords, files (first 5), decisions
   - Separator lines between entries
   - File format: `memories_export_YYYYMMDD_HHMMSS.md`
   - Use case: Documentation, sharing, archival

3. **CSV Export:**
   - Spreadsheet-compatible format
   - Columns: ID, Title, Type, Scope, Created, Updated, Tags, Access Count, Last Accessed, Summary (truncated to 200 chars), Keywords, File
   - Header row included
   - Comma-separated values
   - Example: 21 rows for 20 memories + header
   - File format: `memories_export_YYYYMMDD_HHMMSS.csv`
   - Use case: Excel analysis, data science, reporting

**Export UI:**
- Three buttons in row
- Click to prepare export
- Download button appears below
- Timestamped filenames prevent overwrites

---

## Sidebar Filters

**Available on All Tabs** (except search results are pre-filtered)

### 1. Scope Filter
- Options: both, global, project
- Default: both
- Applied at data load level (cached)

### 2. Memory Types
- Multiselect dropdown
- Options: session, decision, implementation, pattern
- Default: All (empty selection)
- Applied client-side

### 3. Tags
- Multiselect dropdown
- Shows all available tags
- Default: All (empty selection)
- Applied client-side

### 4. Date Range
- **Presets:**
  - All Time (default)
  - Last 7 Days
  - Last 30 Days
  - Last 90 Days
  - Custom (date pickers)
- Filters by creation date

### 5. Access Count
- **Presets:**
  - All (default)
  - Never Accessed (0)
  - Accessed (1+)
  - Popular (5+)
  - Very Popular (10+)
  - Custom Range (min/max inputs)
- Filters by memory.access.count

### 6. Refresh Button
- Clears 5-minute cache
- Reloads all data from disk
- Force-refreshes after creating new memories

---

## Architecture

### Technology Stack

**Frontend:**
- Streamlit 1.53+ (web framework)
- Plotly 6.5+ (interactive charts)
- Pandas 2.3+ (data manipulation)

**Backend:**
- NetworkX 3.6+ (graph algorithms)
- Existing MemoryManager (data access)
- viz/ module functions (calculations)

**Export:**
- Kaleido 1.2+ (chart export, for Phase 3)
- Python csv, json modules

### Module Structure

```
claude_memory/web/
├── app.py                      # Main Streamlit app (204 lines)
├── data_loader.py              # Data loading + caching (80 lines)
├── README.md                   # Module documentation
├── components/
│   ├── filters.py              # Sidebar filters (154 lines)
│   ├── stats_overview.py       # Stats dashboard (103 lines)
│   ├── session_detail.py       # Detail viewer (87 lines)
│   └── tag_cloud.py            # Tag analysis (107 lines)
├── charts/
│   ├── plotly_timeline.py      # Timeline charts (159 lines)
│   ├── plotly_network.py       # Tag network (219 lines) ⭐
│   ├── plotly_heatmap.py       # Heatmaps (198 lines) ⭐
│   └── plotly_trends.py        # Trends (286 lines) ⭐
├── export/
│   └── exporters.py            # Export functions (148 lines) ⭐
└── utils/
    ├── formatters.py           # Display formatting (58 lines)
    └── transformers.py         # Data conversion (109 lines)
```

⭐ = Phase 2 additions

### Data Flow

1. **Load:** `load_memory_data()` → MemoryManager → @st.cache_data(ttl=300)
2. **Filter:** Sidebar controls → `apply_filters()` → filtered list
3. **Transform:** MemoryEntry list → `memories_to_dataframe()` → Pandas DF
4. **Visualize:** DataFrame → Plotly charts → Streamlit UI
5. **Export:** Filtered memories → `export_to_*()` → Download file

### Performance

**Caching Strategy:**
- Memory data: 5-minute TTL cache
- Stats calculation: No cache (fast enough, non-serializable)
- Tag stats: No cache (fast enough)
- Charts: Generated on-demand (interactive parameters)

**Tested Performance:**
- 20 memories: < 2 seconds load time
- Tag network (54 tags): 169 traces, renders instantly
- Activity trends: 4 traces, renders instantly
- Export JSON: ~27KB, instant download
- Export CSV: 21 rows, instant download

**Scalability:**
- Expected smooth performance up to 100 memories
- For 1000+ memories, consider:
  - Pagination in tables
  - Scattergl instead of scatter
  - Monthly aggregation for trends
  - Default to last 90 days with "Load All" option

---

## Key Design Decisions

### 1. Reuse Over Reinvent
- Reused calculation functions from `viz/` module
- `calculate_stats()`, `calculate_tag_stats()` work unchanged
- Only created new rendering layer (Rich → Streamlit/Plotly)

### 2. Progressive Enhancement
- Phase 1: MVP (core features, 1 day)
- Phase 2: Analytics (advanced viz, 0.5 day)
- Phase 3: Future (static export, deployment)
- Each phase fully functional on its own

### 3. Client-Side Filtering
- Load once, filter many times
- Filters applied to cached data in browser
- Fast, responsive UX
- No server round-trips for filter changes

### 4. Serialization Workaround
- Original `calculate_stats()` returns non-serializable objects
- Web version converts to plain dicts
- Removes caching from stats functions
- Memory data cache is sufficient for performance

### 5. No External Database
- Uses existing file-based memory system
- No new dependencies or setup required
- Dashboard reads from `.claude/memory/` directly
- Same data as CLI tools

---

## Usage Tips

### For Daily Use

1. **Quick Overview:**
   - Launch dashboard
   - Check Overview tab metrics
   - Scan mini timeline for activity

2. **Find Specific Memory:**
   - Search tab → enter keywords
   - Or Timeline tab → select from dropdown

3. **Analyze Patterns:**
   - Analytics tab → tag network
   - See which topics cluster together
   - Identify related work areas

4. **Track Activity:**
   - Analytics tab → activity trends
   - See creation vs access patterns
   - Spot inactive periods

5. **Export for Reporting:**
   - Apply filters to desired scope
   - Analytics tab → Export as Markdown
   - Clean report for documentation

### For Analysis

1. **Tag Cleanup:**
   - Tags tab → review co-occurrence
   - Identify redundant tags
   - Consolidate similar tags

2. **Memory Hygiene:**
   - Overview → never accessed count
   - Review old, unused memories
   - Consider archiving or adding context

3. **Work Patterns:**
   - Analytics → cumulative growth
   - See productivity trends
   - Compare global vs project focus

4. **Topic Evolution:**
   - Analytics → type trends
   - See how memory types change
   - Adjust workflow accordingly

---

## Troubleshooting

### Dashboard Won't Start

**Error:** `Streamlit not found`
```bash
pip install -e ".[web]"
```

**Error:** `Port already in use`
```bash
claude-memory web --port 8080  # Try different port
```

### Data Not Loading

**Issue:** Empty dashboard
- Check: `~/.claude/memory/` exists
- Check: `.claude/memory/` in project (if project scope)
- Run: `claude-memory viz stats` to verify memories exist

**Issue:** Old data showing
- Click "Refresh Data" button in sidebar
- Or restart dashboard (5-min cache)

### Charts Not Rendering

**Issue:** Blank chart areas
- Check browser console for errors
- Try different browser (Chrome recommended)
- Ensure JavaScript enabled

**Issue:** Network graph shows "No co-occurrences"
- Lower co-occurrence threshold slider
- Or add more tags to memories

### Export Not Working

**Issue:** Download button doesn't appear
- Click export button first
- Then download button appears below

**Issue:** File download fails
- Check browser download settings
- Allow downloads from localhost
- Check disk space

---

## Future Enhancements (Phase 3)

Documented in `FUTURE_WORK.md`:

1. **Static HTML Export**
   - Generate standalone HTML file
   - Embed charts as static PNGs (Kaleido)
   - Share without running server

2. **PDF Reports**
   - Professional report generation
   - Include charts and summaries
   - Customizable templates

3. **Deployment Options**
   - Docker containerization
   - Deploy to Railway/Render/Fly.io
   - Public sharing with authentication

4. **Advanced Features**
   - Real-time updates (file watching)
   - Comparison mode (before/after)
   - Custom dashboard layouts
   - More chart types

---

## Development

### Adding New Charts

1. Create chart function in `charts/` directory
2. Return Plotly Figure object
3. Import in `app.py`
4. Add to appropriate tab
5. Test with various data sizes

**Example:**
```python
# charts/my_chart.py
import plotly.graph_objects as go

def create_my_chart(memories: list) -> go.Figure:
    fig = go.Figure()
    # ... build chart
    return fig

# app.py
from claude_memory.web.charts.my_chart import create_my_chart

fig = create_my_chart(filtered_memories)
st.plotly_chart(fig, use_container_width=True)
```

### Adding New Components

1. Create component file in `components/`
2. Implement `render(memories)` function
3. Import in `components/__init__.py`
4. Use in `app.py` tabs

### Adding New Export Formats

1. Add function to `export/exporters.py`
2. Follow signature: `export_to_FORMAT(memories: list) -> str`
3. Add download button in Analytics tab
4. Use timestamped filename

---

## Statistics (As of 2026-01-29)

**Development:**
- Total files: 19
- Total lines: ~1,600+
- Development time: 1.5 days (Phase 1 + 2)
- Commits: 2

**Testing:**
- Test dataset: 20 memories, 54 tags
- Tag network: 169 traces generated
- JSON export: 26,769 characters
- CSV export: 21 rows

**Features:**
- Tabs: 5
- Chart types: 10+
- Export formats: 3
- Filter types: 5
- Interactive controls: 8

---

## Credits

**Technology:**
- Streamlit (Snowflake Inc.)
- Plotly (Plotly Technologies Inc.)
- NetworkX (NetworkX Developers)
- Pandas (pandas-dev)

**Development:**
- Phase 1: Claude Sonnet 4.5
- Phase 2: Claude Sonnet 4.5
- Planning: User requirements + implementation plan

---

## See Also

- `docs/USAGE.md` - Full usage guide including web dashboard
- `claude_memory/web/README.md` - Developer documentation
- `FUTURE_WORK.md` - Phase 3 roadmap
- Terminal commands: `claude-memory viz --help`

---

**Last Updated:** 2026-01-29
**Version:** Phase 2 Complete
**Repository:** https://github.com/carbonbasednerd/claude-memory-system
