## Usage Guide

## Quick Start

### 1. Installation

```bash
cd ~/git/jay-i
pip install -e .
```

### 2. Initialize Memory System

```bash
# Initialize global and project memory
claude-memory init

# Initialize only global
claude-memory init --scope global

# Initialize only project (must be in a project directory)
claude-memory init --scope project
```

### 3. Start Working

The memory system tracks your work automatically when you make changes. To explicitly start a session:

```bash
# Start a new session
claude-memory start-session "Implementing user authentication"
```

### 4. Working with Sessions

During your work, Claude Code will automatically track:
- Files you modify
- Decisions you make
- Problems you encounter
- Notes and TODOs

### 5. Save Session to Long-Term Memory

When you're done with a task:

```bash
# Save the current session
claude-memory save-session

# Save with specific scope
claude-memory save-session --scope global

# Save with tags and summary
claude-memory save-session \
  --scope project \
  --tags "authentication,security,OAuth" \
  --summary "Implemented OAuth2 authentication with JWT tokens"
```

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
