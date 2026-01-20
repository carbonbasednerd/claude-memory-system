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
cd ~/git/jay-i
pip install -e .
```

## Usage

### Initialize Memory System
```bash
# Creates ~/.claude/ on first use (automatic)
# Creates project .claude/ when prompted
claude-memory init
```

### Session Workflow
```bash
# Start working (automatic tracking)
# ... make changes, decisions, etc ...

# When done
claude-memory save-session
# - Evaluates session for long-term storage
# - Suggests scope (global vs project)
# - Detects skill candidates
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
