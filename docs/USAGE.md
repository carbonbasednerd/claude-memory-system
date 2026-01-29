## Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/carbonbasednerd/claude-memory-system.git
cd claude-memory-system

# Install with pip
pip install .

# Or install in editable mode for development
pip install -e .
```

### 2. Initialize Memory System

```bash
# Initialize global and project memory
claude-memory init

# Initialize only global
claude-memory init --scope global

# Initialize only project (must be in a git repository)
claude-memory init --scope project
```

This creates:
- `~/.claude/CLAUDE.md` - Global memory with instructions for Claude
- `.claude/CLAUDE.md` - Project-specific memory (if in a project)

The CLAUDE.md files contain instructions that tell Claude to automatically manage the memory system.

### 3. Working with Claude Code (Automatic Mode)

**This is the recommended workflow** - Claude manages everything for you!

**When you start a new Claude Code session:**
1. Claude runs `claude-memory update-current-work` automatically
2. Claude greets you and summarizes any active sessions
3. Claude asks if you want to continue existing work or start something new

**While working:**
- Claude creates session trackers for new tasks
- Claude tracks files modified, decisions made, and problems encountered
- All tracking happens automatically in the background

**When you're done:**
- Tell Claude you're finished or ask to save work
- Claude runs `claude-memory save-session` automatically
- Claude confirms what was saved to long-term memory

**You just work with Claude normally** - the memory system is hands-off!

### 4. Manual Commands (For Advanced Users)

You can also use these commands directly if you prefer manual control:

```bash
# Start a new session manually
claude-memory start-session "Implementing user authentication"

# List active sessions
claude-memory list-sessions

# Update the "Current Work" section in CLAUDE.md
claude-memory update-current-work

# Save the current session
claude-memory save-session

# Save with specific scope, tags, and summary
claude-memory save-session \
  --scope project \
  --tags "authentication,security,OAuth" \
  --summary "Implemented OAuth2 authentication with JWT tokens"
```

## Memory Visualization (`viz` commands)

The `claude-memory viz` command group provides rich, interactive visualization of your memory system with beautiful terminal output powered by the Rich library.

### Timeline View

View memories chronologically with visual progress bars and access tracking:

```bash
# View all memories in timeline
claude-memory viz timeline

# Last 30 days only
claude-memory viz timeline --days 30

# Filter by scope
claude-memory viz timeline --scope project

# Filter by type
claude-memory viz timeline --type session

# Show only frequently accessed memories
claude-memory viz timeline --min-accesses 5

# Show only never-accessed memories
claude-memory viz timeline --never-accessed
```

**Output**: Memories grouped by month with visual bars, showing access counts, tags, file counts, and decisions.

### Session Detail View

View comprehensive information about a specific session:

```bash
# View session details (automatically records access)
claude-memory viz session session-20260119-213545-e98c
```

**Features**:
- Prominent access tracking section (count, first/last accessed, recent queries)
- Complete metadata (scope, type, created/updated dates)
- Tags with color coding
- Summary and decisions
- Files modified (up to 15 shown)
- Related sessions based on tag overlap

**Note**: Viewing a session automatically records the access, incrementing the access count and updating timestamps.

### Search Interface

Full-text search with advanced filtering and export capabilities:

```bash
# Basic search
claude-memory viz search "authentication"

# Search with filters
claude-memory viz search "security" \
  --scope project \
  --tags "vlan,firewall" \
  --days 30

# Advanced access-based filters
claude-memory viz search "documentation" --min-accesses 5
claude-memory viz search "old-project" --never-accessed
claude-memory viz search "recent" --accessed-after 2026-01-01
claude-memory viz search "stale" --accessed-before 2025-12-31
claude-memory viz search "rarely-used" --max-accesses 2

# Export results
claude-memory viz search "api" --export json > results.json
claude-memory viz search "security" --export markdown > report.md
```

**Features**:
- Results sorted by relevance (access count + recency)
- Visual indicators for highly accessed memories (⭐)
- Rich panel-based display
- JSON/Markdown export for reporting

### Statistics Dashboard

View comprehensive statistics about your memory system:

```bash
# Full dashboard
claude-memory viz stats

# Project stats only
claude-memory viz stats --scope project

# Export as JSON
claude-memory viz stats --export json > stats.json
```

**Displays**:
- Overview (total memories, accesses, average)
- Breakdown by type with access counts
- **Most Accessed (Top 10)** - frequently referenced memories
- **Never Accessed** - unused memories
- Activity timeline (last 90 days by week)
- Top tags with frequency bars

### Tag Analysis

Visualize tag relationships and frequency:

```bash
# View all tags
claude-memory viz tags

# Filter by minimum occurrence
claude-memory viz tags --min-count 3

# Project tags only
claude-memory viz tags --scope project
```

**Features**:
- Tag cloud with frequency visualization
- Access statistics per tag (avg accesses per memory)
- Co-occurrence network showing tag relationships
- Orphaned tags identification (never paired with other tags)

### Project Map

Scan and visualize all projects with memory:

```bash
# View all projects
claude-memory viz projects
```

**Displays**:
- All discovered `.claude` directories
- Session/decision/access counts per project
- Most recent and most accessed memories
- Top tags per project
- Beautiful tree visualization

### Health Check

Check memory system integrity and identify issues:

```bash
# Full health check
claude-memory viz health

# Project only
claude-memory viz health --scope project
```

**Checks**:
- **System Integrity**: Index files, session files, markdown archives
- **Quality Warnings**:
  - Untagged sessions (add tags for searchability)
  - Never-accessed memories (may be outdated)
  - Potential duplicates (similarity detection)
  - Stale sessions (>6 months old, unused)
- **Actionable Recommendations**: Specific steps to improve memory health

### Export Capabilities

Most viz commands support exporting data:

```bash
# Export formats
--export json       # JSON format for programmatic access
--export markdown   # Markdown format for documentation
```

**Available on**:
- `viz search` - Export search results
- `viz stats` - Export statistics data

## Searching Memory

### Basic Search

```bash
# Search across all memory
claude-memory search "authentication"

# Search only project memory
claude-memory search "database" --scope project

# Search only global memory
claude-memory search "python practices" --scope global
```

### Filtered Search

```bash
# Search by tags
claude-memory search "auth" --tags "security,OAuth"

# Search by type
claude-memory search "API" --type implementation

# Limit results
claude-memory search "refactor" --limit 5
```

### View Memory Details

```bash
# Show full details of a memory entry
claude-memory show memory-20260119-143052-a1b2c3
```

## Skill Detection

### Analyze for Patterns

```bash
# Analyze all memory for skill candidates
claude-memory analyze-skills

# Analyze only project memory
claude-memory analyze-skills --scope project

# Customize detection thresholds
claude-memory analyze-skills \
  --min-occurrences 5 \
  --days 60
```

This will generate a `skill-candidates.md` report in your `.claude/` directory.

## Maintenance

### Rebuild Index

The index automatically rebuilds when log entries reach the threshold (default: 20). To manually rebuild:

```bash
# Rebuild project index
claude-memory rebuild-index

# Rebuild global index
claude-memory rebuild-index --scope global

# Or use the helper script
./scripts/rebuild-index.sh project
```

### Cleanup Stale Sessions

Remove sessions with no activity for 24+ hours:

```bash
# Find and auto-archive stale sessions
claude-memory cleanup-sessions --auto-archive

# Customize inactivity threshold
claude-memory cleanup-sessions --hours 48 --auto-archive

# Or use the helper script
./scripts/cleanup-stale-sessions.sh 24
```

### View Statistics

```bash
# Show memory stats
claude-memory stats

# List active sessions
claude-memory list-sessions

# Or use the helper script
./scripts/show-stats.sh
```

### Backup and Restore

```bash
# Export memory
./scripts/export-memory.sh my-backup.tar.gz

# Import memory
./scripts/import-memory.sh my-backup.tar.gz

# Validate index integrity
./scripts/validate-index.sh both
```

## Working with Multiple Sessions

The system supports concurrent Claude Code sessions:

### Session Isolation

- Each session gets a unique ID
- Sessions track their work independently
- All sessions can read the same memory
- Writes use append-log for safety

### Viewing Other Sessions

```bash
# List all active sessions
claude-memory list-sessions
```

### Best Practices

1. **Save sessions when done** - Don't leave sessions active indefinitely
2. **Use descriptive tasks** - Makes it easier to find memories later
3. **Tag appropriately** - Tags enable better search and pattern detection
4. **Clean up periodically** - Archive stale sessions to keep things tidy

## Configuration

Configuration is stored in `.claude/config.json`:

```json
{
  "memory": {
    "refresh": {
      "strategy": "periodic",
      "intervalMinutes": 5,
      "onSearch": true
    },
    "indexRebuild": {
      "strategy": "threshold",
      "thresholdEntries": 20
    },
    "scopeDecisions": {
      "autoSuggest": true,
      "requireConfirmation": true
    }
  }
}
```

You can customize:
- Refresh frequency
- Index rebuild threshold
- Scope decision behavior
- Session visibility

## File Structure

### Global Memory (`~/.claude/`)

```
~/.claude/
├── CLAUDE.md              # Static memory pointers
├── config.json            # Configuration
├── memory/
│   ├── index.json         # Memory index
│   ├── index-log/         # Pending updates
│   ├── sessions/
│   │   ├── active/        # Active sessions
│   │   └── archived/      # Completed sessions
│   ├── decisions/
│   └── implementations/
├── sessions/
│   ├── active/            # Session tracking files
│   └── archived/
└── skills/
    └── skill-candidates.md
```

### Project Memory (`/project/.claude/`)

Same structure as global, but project-specific.

## Integration with Claude Code

The memory system is designed to integrate with Claude Code:

1. **Auto-tracking**: Claude tracks work automatically
2. **Contextual loading**: Memory is loaded based on triggers
3. **Search on demand**: Search memory when needed
4. **Pattern detection**: Automatic skill candidate flagging

## Examples

### Example 1: Track a Feature Implementation

```bash
# Start session
claude-memory start-session "Add user profile page"

# ... work on feature, Claude tracks automatically ...

# Save when done
claude-memory save-session \
  --scope project \
  --tags "frontend,React,user-profile" \
  --summary "Created user profile page with edit functionality"
```

### Example 2: Find Similar Past Work

```bash
# Search for similar implementations
claude-memory search "user profile" --type implementation

# View details
claude-memory show memory-20260115-094523-xyz
```

### Example 3: Detect Reusable Patterns

```bash
# Analyze memory
claude-memory analyze-skills --scope project

# Review skill-candidates.md
# Extract useful patterns into skills
```

### Example 4: Backup Before Major Changes

```bash
# Backup current memory
./scripts/export-memory.sh before-refactor.tar.gz

# ... make changes ...

# If needed, restore
./scripts/import-memory.sh before-refactor.tar.gz
```
