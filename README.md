# Claude Memory System

A two-tier memory system for Claude Code that provides:
- **Short-term memory**: Active session tracking with auto-updates
- **Long-term memory**: Persistent project history and decisions
- **Skills evolution**: Automatic pattern detection and skill candidate extraction
- **Concurrent sessions**: Safe multi-session memory access
- **Global + Project scope**: User-wide and project-specific memories

## Features

- 🧠 **Automatic session tracking** - Claude tracks work as you go
- 📚 **Long-term memory** - Save sessions, decisions, and implementations
- 🎯 **Lazy-loading pointers** - Only load detailed memory when contextually relevant
- 🔄 **Concurrent-safe** - Multiple Claude sessions can work simultaneously
- 🌍 **Global + Project** - Memories shared across projects or kept project-specific
- ⚡ **Skill extraction** - Patterns evolve into reusable skills
- 🔍 **Smart search** - Find memories by keywords, tags, and triggers

## Architecture

```
Global Memory (~/.claude/)
├── CLAUDE.md                 # Static memory pointers (read by all sessions)
├── config.json               # Configuration
├── memory/
│   ├── index.json            # Base memory index
│   ├── index-log/            # Append-only updates (concurrent-safe)
│   ├── sessions/
│   │   ├── active/           # Currently running sessions
│   │   └── archived/         # Completed sessions
│   ├── decisions/            # Decision records
│   └── implementations/      # Implementation details
└── skills/
    ├── index.json
    └── skill-candidates.md

Project Memory (/project/.claude/)
├── CLAUDE.md                 # Project-specific pointers
├── memory/                   # Same structure as global
└── skills/                   # Project-specific skills
```

## Installation

```bash
# Clone the repository
git clone https://github.com/carbonbasednerd/claude-memory-system.git
cd claude-memory-system

# Install with pip
pip install .

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

- **Append-log for concurrency**: Index updates use append-only logs, preventing write conflicts
- **Lazy loading**: Only load detailed memories when contextually triggered
- **Auto-tracking**: Sessions automatically track work, evaluated on completion
- **Hierarchical scope**: Global memories available everywhere, project memories isolated
- **Pattern detection**: Automatic flagging of skill candidates from repeated patterns

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
