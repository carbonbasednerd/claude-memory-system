# Helper Scripts Documentation

The `scripts/` directory contains bash helper scripts for common memory management tasks. These scripts provide convenient wrappers around CLI commands and maintenance operations.

## Overview

All scripts are located in the `scripts/` directory and should be run from your project root:

```bash
# Make scripts executable (one-time)
chmod +x scripts/*.sh

# Run a script
./scripts/script-name.sh [arguments]
```

## Scripts Reference

### 1. export-memory.sh

Export memory to a backup archive.

**Usage:**
```bash
./scripts/export-memory.sh [output-file]
```

**Arguments:**
- `output-file` (optional): Name of backup file. Default: `memory-backup-YYYYMMDD-HHMMSS.tar.gz`

**Behavior:**
- If run in a project directory (with `.claude/`): Backs up project memory
- If run outside a project: Backs up global memory from `~/.claude/`
- Creates a compressed tar.gz archive

**Examples:**
```bash
# Export with default filename
./scripts/export-memory.sh
# => memory-backup-20260119-143052.tar.gz

# Export with custom filename
./scripts/export-memory.sh my-backup.tar.gz

# Export before major changes
./scripts/export-memory.sh before-refactor-$(date +%Y%m%d).tar.gz
```

**Output:**
```
Exporting memory to my-backup.tar.gz...
✓ Exported project memory
Backup saved to: my-backup.tar.gz
```

**Use Cases:**
- Regular backups
- Before major refactoring
- Migrating between machines
- Archiving project memory

---

### 2. import-memory.sh

Import memory from a backup archive.

**Usage:**
```bash
./scripts/import-memory.sh <backup-file.tar.gz>
```

**Arguments:**
- `backup-file` (required): Path to backup archive

**Behavior:**
- If run in a project directory (with `.git/`): Imports to project `.claude/`
- If run outside a project: Imports to global `~/.claude/`
- Extracts and overwrites existing memory

**Examples:**
```bash
# Import backup
./scripts/import-memory.sh my-backup.tar.gz

# Import from another location
./scripts/import-memory.sh /path/to/backup-20260115.tar.gz

# Restore after failed experiment
./scripts/import-memory.sh before-refactor-20260119.tar.gz
```

**Output:**
```
Importing memory from my-backup.tar.gz...
✓ Imported to project directory
✓ Import complete
```

**Warning:**
This will overwrite existing `.claude/` directory. Export current memory first if needed.

---

### 3. rebuild-index.sh

Rebuild memory index from log entries.

**Usage:**
```bash
./scripts/rebuild-index.sh [scope]
```

**Arguments:**
- `scope` (optional): `project`, `global`, or `both`. Default: `project`

**Behavior:**
- Reads base index + all log entries
- Applies log operations sequentially
- Writes consolidated index
- Deletes log files

**Examples:**
```bash
# Rebuild project index
./scripts/rebuild-index.sh project

# Rebuild global index
./scripts/rebuild-index.sh global

# Rebuild both
./scripts/rebuild-index.sh both
```

**Output:**
```
Rebuilding project index...
✓ Index rebuild complete
```

**When to Use:**
- After concurrent sessions
- When log entries pile up (20+)
- Before searching large memory sets
- After importing memories
- When index appears out of sync

**Scheduled Rebuild:**
```bash
# Add to cron for daily rebuild
0 2 * * * cd /your/project && ./scripts/rebuild-index.sh both
```

---

### 4. cleanup-stale-sessions.sh

Clean up sessions with no activity for specified hours.

**Usage:**
```bash
./scripts/cleanup-stale-sessions.sh [hours]
```

**Arguments:**
- `hours` (optional): Inactivity threshold in hours. Default: `24`

**Behavior:**
- Finds sessions with no updates for N+ hours
- Auto-archives stale sessions
- Removes from active directory
- Saves to archived directory

**Examples:**
```bash
# Clean up sessions inactive for 24+ hours
./scripts/cleanup-stale-sessions.sh 24

# More aggressive - 12 hours
./scripts/cleanup-stale-sessions.sh 12

# Less aggressive - 48 hours
./scripts/cleanup-stale-sessions.sh 48

# Clean up old sessions (1 week)
./scripts/cleanup-stale-sessions.sh 168
```

**Output:**
```
Finding sessions with no activity for 24+ hours...
✓ Cleanup complete
```

**Scheduled Cleanup:**
```bash
# Add to cron for daily cleanup
0 0 * * * cd /your/project && ./scripts/cleanup-stale-sessions.sh 24
```

**Use Cases:**
- Regular maintenance
- Prevent session buildup
- Clean up forgotten sessions
- Automated housekeeping

---

### 5. validate-index.sh

Validate memory index integrity.

**Usage:**
```bash
./scripts/validate-index.sh [scope]
```

**Arguments:**
- `scope` (optional): `global`, `project`, or `both`. Default: `both`

**Behavior:**
- Validates JSON structure
- Counts memories in index
- Checks for pending log entries
- Reports warnings and errors

**Examples:**
```bash
# Validate both indices
./scripts/validate-index.sh both

# Validate only global
./scripts/validate-index.sh global

# Validate only project
./scripts/validate-index.sh project
```

**Output:**
```
Validating memory index...
Checking global index...
  ✓ Global index is valid JSON
  ✓ Global index contains 45 memories
  ⚠ 12 unmerged log entries (consider rebuilding index)
Checking project index...
  ✓ Project index is valid JSON
  ✓ Project index contains 23 memories
  ✓ No pending log entries
✓ Validation complete
```

**Exit Codes:**
- `0`: All validations passed
- `1`: Validation failed (invalid JSON, missing files, etc.)

**Use Cases:**
- Debugging search issues
- Verifying index after import
- Checking system health
- Pre-deployment validation

**CI Integration:**
```bash
# In CI pipeline
./scripts/validate-index.sh both || exit 1
```

---

### 6. analyze-patterns.sh

Analyze memory for skill candidates.

**Usage:**
```bash
./scripts/analyze-patterns.sh [scope] [min-occurrences] [days]
```

**Arguments:**
- `scope` (optional): `project`, `global`, or `both`. Default: `both`
- `min-occurrences` (optional): Minimum pattern occurrences. Default: `3`
- `days` (optional): Time window in days. Default: `90`

**Behavior:**
- Analyzes memories for repeated patterns
- Detects procedure, decision, and problem-solution patterns
- Generates skill candidates report
- Saves to `.claude/skills/skill-candidates.md`

**Examples:**
```bash
# Default analysis (3+ occurrences in 90 days)
./scripts/analyze-patterns.sh

# Analyze only project memory
./scripts/analyze-patterns.sh project

# More sensitive detection (2+ occurrences)
./scripts/analyze-patterns.sh both 2 90

# Longer time window (180 days)
./scripts/analyze-patterns.sh both 3 180

# Strict detection (5+ occurrences in 60 days)
./scripts/analyze-patterns.sh both 5 60
```

**Output:**
```
Analyzing memory for skill patterns...
  Scope: both
  Minimum occurrences: 3
  Time window: 90 days

Found 4 skill candidates:
  • API Endpoint Creation (procedure, 7 occurrences)
  • Database Migration Pattern (procedure, 5 occurrences)
  • Authentication Decision Framework (decision, 4 occurrences)
  • CORS Fix Pattern (problem-solution, 3 occurrences)

✓ Analysis complete
Report saved to: .claude/skills/skill-candidates.md
```

**Scheduled Analysis:**
```bash
# Weekly skill detection
0 0 * * 0 cd /your/project && ./scripts/analyze-patterns.sh both 3 90
```

**Use Cases:**
- Periodic pattern analysis
- Identifying automation opportunities
- Team knowledge extraction
- Building skill library

---

### 7. show-stats.sh

Display memory usage statistics and active sessions.

**Usage:**
```bash
./scripts/show-stats.sh
```

**Arguments:**
None.

**Behavior:**
- Shows memory statistics (counts, types, access patterns)
- Lists active sessions
- Displays both global and project stats

**Example:**
```bash
./scripts/show-stats.sh
```

**Output:**
```
Memory Statistics
=================

Global Memory:
  Total memories: 128
  By type:
    - Sessions: 89
    - Decisions: 24
    - Implementations: 15
  Most accessed: 5 memories
  Never accessed: 32 memories

Project Memory:
  Total memories: 45
  By type:
    - Sessions: 38
    - Decisions: 5
    - Implementations: 2
  Most accessed: 3 memories
  Never accessed: 12 memories

Active Sessions:
----------------
Project Sessions:
  - session-20260119-143052-abc123
    Task: Implement user authentication
    Started: 2026-01-19 14:30:52
    Last updated: 2026-01-19 15:45:23

  - session-20260119-160234-def456
    Task: Fix checkout bug
    Started: 2026-01-19 16:02:34
    Last updated: 2026-01-19 16:12:45

Global Sessions:
  (none)
```

**Use Cases:**
- Quick health check
- Monitor memory growth
- Check active work
- Identify unused memories

---

## Common Workflows

### Daily Maintenance Routine

```bash
#!/bin/bash
# daily-maintenance.sh

echo "=== Daily Memory Maintenance ==="

# 1. Cleanup stale sessions
echo "Cleaning up stale sessions..."
./scripts/cleanup-stale-sessions.sh 24

# 2. Show stats
echo "Current statistics:"
./scripts/show-stats.sh

# 3. Validate indices
echo "Validating indices..."
./scripts/validate-index.sh both

echo "✓ Maintenance complete"
```

### Weekly Maintenance Routine

```bash
#!/bin/bash
# weekly-maintenance.sh

echo "=== Weekly Memory Maintenance ==="

# 1. Daily tasks
./scripts/cleanup-stale-sessions.sh 48

# 2. Rebuild indices
echo "Rebuilding indices..."
./scripts/rebuild-index.sh both

# 3. Analyze patterns
echo "Analyzing for skill patterns..."
./scripts/analyze-patterns.sh both 3 90

# 4. Backup
echo "Creating backup..."
./scripts/export-memory.sh "backup-weekly-$(date +%Y%m%d).tar.gz"

# 5. Stats
./scripts/show-stats.sh

echo "✓ Weekly maintenance complete"
```

### Pre-Deployment Checklist

```bash
#!/bin/bash
# pre-deploy.sh

echo "=== Pre-Deployment Checks ==="

# 1. Validate indices
./scripts/validate-index.sh both || exit 1

# 2. Rebuild to consolidate
./scripts/rebuild-index.sh both

# 3. Backup current state
./scripts/export-memory.sh "pre-deploy-$(date +%Y%m%d-%H%M%S).tar.gz"

# 4. Verify backup
echo "✓ Pre-deployment checks complete"
echo "Backup created and validated"
```

---

## Automation

### Cron Jobs

Add to crontab (`crontab -e`):

```bash
# Daily cleanup at 2am
0 2 * * * cd /your/project && ./scripts/cleanup-stale-sessions.sh 24

# Weekly analysis on Sundays at 3am
0 3 * * 0 cd /your/project && ./scripts/analyze-patterns.sh both 3 90

# Weekly backup on Sundays at 4am
0 4 * * 0 cd /your/project && ./scripts/export-memory.sh "backup-$(date +\%Y\%m\%d).tar.gz"

# Monthly rebuild on 1st at 1am
0 1 1 * * cd /your/project && ./scripts/rebuild-index.sh both
```

### Git Hooks

#### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Rebuild index before committing .claude/
if git diff --cached --name-only | grep -q "^\.claude/"; then
    echo "Rebuilding memory index..."
    ./scripts/rebuild-index.sh project
    git add .claude/memory/index.json
fi
```

#### Post-merge Hook

```bash
#!/bin/bash
# .git/hooks/post-merge

# Rebuild index after pulling .claude/ changes
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q "^\.claude/"; then
    echo "Rebuilding memory index after merge..."
    ./scripts/rebuild-index.sh project
fi
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/memory-validation.yml
name: Validate Memory

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -e .

      - name: Validate indices
        run: ./scripts/validate-index.sh both

      - name: Check for stale sessions
        run: ./scripts/cleanup-stale-sessions.sh 24

      - name: Analyze patterns
        run: ./scripts/analyze-patterns.sh project 3 90
```

### Backup Workflow

```yaml
# .github/workflows/backup-memory.yml
name: Backup Memory

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Export memory
        run: ./scripts/export-memory.sh memory-backup.tar.gz

      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: memory-backup
          path: memory-backup.tar.gz
          retention-days: 90
```

---

## Troubleshooting

### Script Permission Denied

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Script Not Found

```bash
# Run from project root
cd /path/to/project
./scripts/script-name.sh

# Or use absolute path
/path/to/project/scripts/script-name.sh
```

### Python Command Not Found

Scripts assume `python3` is available. If using a virtual environment:

```bash
# Activate venv first
source venv/bin/activate
./scripts/script-name.sh
```

### Index Validation Fails

```bash
# Try rebuilding
./scripts/rebuild-index.sh both

# If still fails, check JSON syntax
python3 -m json.tool .claude/memory/index.json

# Backup and recreate
./scripts/export-memory.sh backup.tar.gz
rm .claude/memory/index.json
claude-memory rebuild-index
```

---

## Custom Scripts

### Creating Your Own Helper Scripts

Template for custom scripts:

```bash
#!/usr/bin/env bash
# Description of what this script does

set -e  # Exit on error

# Parse arguments
ARG1="${1:-default-value}"

echo "Doing something..."

# Call CLI commands
claude-memory your-command --option "$ARG1"

echo "✓ Complete"
```

**Best Practices:**
- Use `set -e` to exit on errors
- Provide default argument values
- Echo progress messages
- Use descriptive output (✓, ✗, ⚠)
- Document usage in header comments

### Example: Custom Backup Rotation

```bash
#!/usr/bin/env bash
# Backup with rotation (keep last 7 backups)

set -e

BACKUP_DIR="$HOME/memory-backups"
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S).tar.gz"

mkdir -p "$BACKUP_DIR"

# Create backup
./scripts/export-memory.sh "$BACKUP_DIR/$BACKUP_NAME"

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t backup-*.tar.gz | tail -n +8 | xargs -r rm

echo "✓ Backup created and old backups cleaned up"
ls -lh backup-*.tar.gz
```

---

## Best Practices

1. **Run from project root**: Scripts assume they're run from the project root directory
2. **Make executable**: Run `chmod +x scripts/*.sh` once after cloning
3. **Check return codes**: Scripts use exit code 0 for success, non-zero for failure
4. **Review output**: Scripts provide descriptive output to understand what happened
5. **Automate wisely**: Use cron for regular maintenance, but test manually first
6. **Backup before major operations**: Always export before importing or major changes
7. **Validate regularly**: Run `validate-index.sh` periodically to catch issues early
8. **Monitor stats**: Use `show-stats.sh` to understand memory growth and usage

---

## See Also

- `docs/USAGE.md` - CLI command reference
- `docs/API.md` - Python API reference
- `docs/EXAMPLES.md` - Usage examples
- `CONTRIBUTING.md` - Development guidelines
