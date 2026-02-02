# Claude Memory System

A comprehensive two-tier memory system for Claude Code that provides intelligent context management, visualization, and analytics:
- **Short-term memory**: Active session tracking with auto-updates
- **Long-term memory**: Persistent project history and decisions
- **Memory visualization**: Rich terminal UI and interactive web dashboard
- **Context optimization**: Lightweight manifest system with 30% token reduction
- **Skills evolution**: Automatic pattern detection and skill candidate extraction
- **Concurrent sessions**: Safe multi-session memory access
- **Global + Project scope**: User-wide and project-specific memories

## Features

### Core Memory System
- 🧠 **Automatic session tracking** - Claude tracks work as you go
- 📚 **Long-term memory** - Save sessions, decisions, and implementations
- 🎯 **Lightweight manifest** - 30% context reduction with lazy-loading metadata
- 🔄 **Concurrent-safe** - Multiple Claude sessions can work simultaneously
- 🌍 **Global + Project** - Memories shared across projects or kept project-specific
- ⚡ **Skill extraction** - Patterns evolve into reusable skills
- 🔍 **Smart search** - Find memories by keywords, tags, and triggers

### Visualization & Analytics
- 📊 **Web Dashboard** - Interactive Streamlit app with charts and graphs
- 🎨 **Rich Terminal UI** - Beautiful CLI visualization powered by Rich library
- 📈 **Timeline views** - Chronological memory exploration with access tracking
- 🏷️ **Tag analysis** - Tag clouds, co-occurrence networks, and frequency stats
- 🔎 **Advanced search** - Full-text search with filters and export (JSON/Markdown/CSV)
- 📉 **Statistics dashboard** - Usage patterns, activity trends, and health checks
- 🗺️ **Project mapping** - Scan and visualize all projects with memory

### Optimization & Debugging
- 🐛 **Debug mode** - Track context usage and optimize token consumption
- 🔧 **Health checks** - Identify untagged, unused, or duplicate memories
- 📦 **Export capabilities** - JSON, Markdown, CSV exports for reporting
- ⚡ **Access tracking** - Monitor which memories are used most frequently

## Architecture

```
Global Memory (~/.claude/)
├── CLAUDE.md                 # Instructions for Claude (auto-generated)
├── config.json               # Configuration
├── memory/
│   ├── manifest.json         # Lightweight metadata index (30% token savings)
│   ├── index.json            # Full memory index
│   ├── index-log/            # Append-only updates (concurrent-safe)
│   ├── sessions/
│   │   ├── active/           # Currently running sessions
│   │   └── archived/         # Completed sessions (markdown files)
│   ├── decisions/            # Decision records
│   └── implementations/      # Implementation details
├── skills/
│   ├── index.json
│   └── skill-candidates.md
└── debug.flag                # Debug mode persistence flag

Project Memory (/project/.claude/)
├── CLAUDE.md                 # Project-specific instructions
├── memory/                   # Same structure as global (manifest, index, sessions)
└── skills/                   # Project-specific skills
```

## Installation

```bash
# Clone the repository
git clone https://github.com/carbonbasednerd/claude-memory-system.git
cd claude-memory-system

# Install core system
pip install .

# Or install with web dashboard support (includes Streamlit, Plotly, etc.)
pip install -e ".[web]"

# Or install in editable mode for development
pip install -e .
```

## Usage

### Initialize Memory System
```bash
# Initialize both global (~/.claude/) and project (.claude/) memory
claude-memory init

# Or initialize only global
claude-memory init --scope global

# Or initialize only project (must be in a git repository)
claude-memory init --scope project
```

This creates CLAUDE.md files with instructions that tell Claude to automatically manage your memory system.

### Automatic Workflow

**Claude manages the memory system for you!** When you start a new Claude Code session:

1. **Claude greets you** and summarizes any ongoing work
2. **Claude automatically tracks** your work (files, decisions, problems)
3. **When you're done**, Claude saves the session to long-term memory

You just work normally with Claude - the memory system runs automatically in the background.

### Manual Commands (Optional)

You can also use these commands directly if needed:

```bash
# Refresh the "Current Work" section in CLAUDE.md
claude-memory update-current-work

# Start a new session manually
claude-memory start-session "Task description"

# List active sessions
claude-memory list-sessions

# Save session with tags and summary
claude-memory save-session --tags "feature,auth" --summary "Added OAuth support"
```

### Memory Visualization (Terminal UI)
```bash
# Timeline view (chronological with access tracking)
claude-memory viz timeline
claude-memory viz timeline --days 30 --min-accesses 5

# Session details
claude-memory viz session <session-id>

# Advanced search with filters
claude-memory viz search "authentication" --scope project --tags "security"
claude-memory viz search "docs" --never-accessed --export markdown

# Statistics dashboard
claude-memory viz stats
claude-memory viz stats --export json

# Tag analysis (cloud, co-occurrence, frequency)
claude-memory viz tags --min-count 3

# Project map (scan all .claude directories)
claude-memory viz projects

# Health check (integrity, warnings, recommendations)
claude-memory viz health
```

### Web Dashboard (Interactive UI)
```bash
# Launch web dashboard (Streamlit + Plotly)
claude-memory web

# Custom port
claude-memory web --port 8080

# Installation (requires extra dependencies)
pip install -e ".[web]"
```

**Features:** Interactive timeline, tag network graphs, activity heatmaps, advanced search, export to JSON/Markdown/CSV.

### Debug Mode & Context Tracking
```bash
# Enable debug mode (track context usage)
claude-memory debug on

# Check status
claude-memory debug status

# Disable
claude-memory debug off
```

When enabled, Claude provides detailed context usage reports showing token consumption by component.

### Search Memory
```bash
claude-memory search "authentication"
claude-memory search "database" --scope project
claude-memory search "python practices" --scope global
```

### Skill Management
```bash
# Analyze for skill candidates
claude-memory analyze-skills

# Extract skill
claude-memory extract-skill <session-id>
```

### Maintenance
```bash
# Rebuild manifest (lightweight metadata index)
claude-memory rebuild-manifest
claude-memory rebuild-manifest --scope global

# Rebuild index from logs
claude-memory rebuild-index

# Cleanup stale sessions
claude-memory cleanup-sessions

# Export/backup
claude-memory export --output backup.tar.gz
```

## Documentation

- **[Usage Guide](docs/USAGE.md)** - Complete user guide for all CLI commands
- **[API Reference](docs/API.md)** - Python API documentation for developers
- **[Architecture](docs/ARCHITECTURE.md)** - System design and implementation details
- **[Examples](docs/EXAMPLES.md)** - Real-world usage examples and workflows
- **[Scripts](docs/SCRIPTS.md)** - Helper scripts documentation
- **[FAQ](docs/FAQ.md)** - Frequently asked questions and troubleshooting
- **[Contributing](CONTRIBUTING.md)** - Guidelines for contributors

## Design Decisions

- **Manifest-based optimization**: Lightweight metadata index reduces context usage by 30% (1,390 → 968 tokens always-loaded)
- **Append-log for concurrency**: Index updates use append-only logs, preventing write conflicts
- **Lazy loading**: Only load detailed memories when contextually triggered
- **Auto-tracking**: Sessions automatically track work, evaluated on completion
- **Hierarchical scope**: Global memories available everywhere, project memories isolated
- **Pattern detection**: Automatic flagging of skill candidates from repeated patterns
- **Access tracking**: Monitor which memories are used to optimize relevance
- **Multi-modal visualization**: Both terminal UI (Rich) and web UI (Streamlit) for different workflows
- **Debug mode**: Optional context tracking for optimization and transparency

## Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```

## License

MIT
