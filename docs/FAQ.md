# Frequently Asked Questions (FAQ)

## General Questions

### What is the Claude Memory System?

A two-tier memory system for Claude Code that provides:
- **Short-term memory**: Active session tracking updated automatically as you work
- **Long-term memory**: Persistent storage of sessions, decisions, and implementations
- **Skill evolution**: Automatic detection of reusable patterns
- **Concurrent safety**: Multiple Claude sessions can work simultaneously

### Why do I need this?

Claude Code sessions are stateless - each new session starts fresh. The Memory System allows Claude to:
- Remember past decisions and their rationale
- Recall solutions to previously solved problems
- Build on patterns from earlier work
- Share knowledge across projects (global scope)
- Learn from repeated procedures (skill detection)

### Is this official from Anthropic?

This is a community project designed to work with Claude Code. Check the repository for licensing and attribution.

---

## How It Works

### How does short-term memory work?

Short-term memory is stored in `CLAUDE.md` files:
- Located in `~/.claude/CLAUDE.md` (global) and `.claude/CLAUDE.md` (project)
- Contains lightweight memory pointers with triggers
- Claude reads this automatically at session start
- Only loads detailed memories when triggers match your current work

### How does long-term memory work?

Long-term memory uses a structured index:
- Memories stored as markdown files in `.claude/memory/`
- Indexed for fast search by title, tags, keywords, triggers
- Supports global (cross-project) and project-specific scopes
- Tracks access patterns to surface relevant memories

### What triggers loading a memory?

Memories have triggers like:
- File extensions (`.py`, `.js`)
- Keywords (`authentication`, `database`)
- Tags (`security`, `performance`)
- Framework names (`React`, `Django`)

When Claude sees these in your conversation or files being edited, relevant memories are loaded.

### How are skills detected?

The skill detector analyzes patterns:
- **Procedure patterns**: Similar tasks repeated 3+ times
- **Decision patterns**: Recurring decision frameworks
- **Problem-solution patterns**: Common issues and fixes

When detected, these are flagged as skill candidates for manual extraction.

---

## Scope Questions

### When should I use global vs project scope?

**Use Global scope for:**
- General coding practices (e.g., Python style preferences)
- Cross-project patterns (e.g., API design principles)
- Reusable solutions (e.g., CORS configuration)
- Team-wide standards (e.g., testing approaches)
- Tool configurations (e.g., Docker setup)

**Use Project scope for:**
- Project-specific decisions (e.g., database schema)
- Implementation details (e.g., authentication flow)
- Project architecture (e.g., module structure)
- Local workarounds (e.g., legacy code handling)
- Business logic (e.g., payment processing)

### Can I change the scope later?

Not directly through the API, but you can:
1. Export the memory file
2. Copy it to the other scope's directory
3. Add an entry to the target index manually
4. Rebuild the index

### Do global memories work in all projects?

Yes! Global memories are stored in `~/.claude/` and are available to Claude in any project on your machine.

### Can I have both global and project memories with the same tags?

Yes. When searching, results from both scopes are returned together. You can filter by scope if needed:
```bash
claude-memory search "auth" --scope project
claude-memory search "auth" --scope global
```

---

## Concurrent Sessions

### Can I run multiple Claude sessions at once?

Yes! The system is designed for concurrent sessions:
- Each session gets a unique ID
- Writes use append-only logs (no conflicts)
- Sessions can read the same memory safely
- Indices rebuild automatically to merge changes

### What happens if two sessions modify memory simultaneously?

Both writes succeed via append-only logs:
1. Session A writes to log file `timestamp-A.json`
2. Session B writes to log file `timestamp-B.json`
3. Both log files coexist peacefully
4. Next index rebuild merges both changes

### How often is the index rebuilt?

Automatically when log entries exceed threshold (default: 20), or manually via:
```bash
claude-memory rebuild-index
```

### Will concurrent sessions see each other's changes immediately?

No - changes are eventually consistent:
- New memories appear after index rebuild
- Active sessions show in `claude-memory list-sessions`
- Use `rebuild-index` to force synchronization

---

## Troubleshooting

### My memories aren't showing up in searches

**Possible causes:**

1. **Index not rebuilt**: Run `claude-memory rebuild-index`
2. **Wrong scope**: Try `--scope both` when searching
3. **Typo in query**: Check spelling, try broader terms
4. **No matching triggers**: Memory might not match your search terms

**Debug steps:**
```bash
# List all memories
claude-memory search "" --limit 100

# Check specific memory
claude-memory show <memory-id>

# Rebuild index
claude-memory rebuild-index

# Validate index
./scripts/validate-index.sh both
```

### Sessions aren't being tracked

**Check:**
1. Is `.claude/` directory initialized? Run `claude-memory init`
2. Are you in the right directory?
3. Is the session file created? Check `.claude/sessions/active/`

**Verify:**
```bash
# List active sessions
claude-memory list-sessions

# Check directory structure
ls -la .claude/sessions/active/
```

### "Index out of sync" errors

**Solution:**
```bash
# Rebuild both indices
claude-memory rebuild-index --scope global
claude-memory rebuild-index --scope project

# Validate
./scripts/validate-index.sh both
```

### Too many log entries piling up

**Normal operation** - logs accumulate until rebuild threshold.

**Force rebuild:**
```bash
# Check log count
ls .claude/memory/index-log/ | wc -l

# Rebuild to consolidate
claude-memory rebuild-index
```

### Stale sessions not cleaning up

**Manual cleanup:**
```bash
# Clean sessions inactive for 24+ hours
claude-memory cleanup-sessions --hours 24 --auto-archive

# Or use the script
./scripts/cleanup-stale-sessions.sh 24
```

### Memory files are missing

**Check locations:**
```bash
# Global memories
ls ~/.claude/memory/sessions/
ls ~/.claude/memory/decisions/
ls ~/.claude/memory/implementations/

# Project memories
ls .claude/memory/sessions/
```

**Possible causes:**
- Memory was deleted manually
- File was moved
- Index references wrong path

**Fix:**
Rebuild index to sync with actual files:
```bash
claude-memory rebuild-index
```

### Can't find old memories

**Strategies:**

1. **Broaden search:**
```bash
# Search everything
claude-memory search "" --limit 100
```

2. **Check archived sessions:**
```bash
ls .claude/sessions/archived/
ls .claude/memory/sessions/
```

3. **Search by date in filenames:**
```bash
find .claude/memory -name "2026-01-*"
```

---

## Performance

### How fast is memory search?

- **Small index** (<100 entries): <10ms
- **Medium index** (100-1000 entries): 10-50ms
- **Large index** (1000+ entries): 50-100ms
- **With logs** (+20 entries): +5-10ms

Search is in-memory linear scan, acceptable for thousands of memories.

### How much disk space does it use?

Minimal:
- **Index JSON**: ~500KB for 1000 memories
- **Each memory file**: 1-10KB
- **Session files**: 1-5KB each
- **Total for active project**: Usually <10MB

### Does it slow down Claude Code?

No:
- CLAUDE.md is loaded once at session start (~2-5KB)
- Detailed memories loaded only when triggered
- Index operations are fast (<100ms)
- No network calls, all local filesystem

### How do I optimize for large memory collections?

**If you have 5000+ memories:**

1. **Lower rebuild threshold:**
```json
// config.json
{
  "memory": {
    "indexRebuild": {
      "thresholdEntries": 10  // Rebuild more frequently
    }
  }
}
```

2. **Use specific tags:**
Tag memories consistently for targeted searches

3. **Archive old memories:**
Move ancient memories to a backup directory

4. **Split by scope:**
Use project scope for project-specific memories

---

## Integration

### How do I use this with existing Claude Code sessions?

The memory system integrates transparently:
1. Initialize: `claude-memory init`
2. Work normally in Claude Code
3. Manually save important sessions: `claude-memory save-session`
4. Claude auto-loads relevant memories from CLAUDE.md

### Can I import memories from other sources?

Yes, create markdown files manually:

```bash
# Create memory file
cat > .claude/memory/decisions/my-decision.md << 'EOF'
# API Design Decision

**Date**: 2026-01-19
**Decision**: Use REST over GraphQL

## Rationale
- Team familiarity
- Simpler tooling
- Established patterns

EOF

# Add to index
claude-memory rebuild-index
```

### Can I export memories for backup?

Yes:
```bash
# Export to tarball
./scripts/export-memory.sh backup-2026-01-19.tar.gz

# Import later
./scripts/import-memory.sh backup-2026-01-19.tar.gz
```

### Can I share project memories with my team?

Yes! Project memory (`.claude/`) can be committed to git:

```bash
# Add to git
git add .claude/
git commit -m "Add project memory"
git push

# Team members pull
git pull
claude-memory search "team knowledge"
```

**Note:** Be careful not to commit sensitive information.

### Does this work with the Claude API?

The memory system is file-based and can be used alongside any Claude integration. You can:
- Read CLAUDE.md and inject into prompts
- Query the index programmatically (see `docs/API.md`)
- Build custom integrations using the Python API

---

## Privacy & Security

### Where is my data stored?

- **Global memory**: `~/.claude/` on your machine
- **Project memory**: `.claude/` in project directory
- **No cloud storage**: Everything is local files

### Is my data sent to Anthropic?

No. The memory system is entirely local:
- Files stored on your filesystem
- No network requests
- No telemetry
- No external services

CLAUDE.md content may be included in your prompts to Claude Code, following Claude Code's normal privacy model.

### Can I encrypt my memories?

Not built-in currently, but you can:
- Encrypt the entire `.claude/` directory with filesystem encryption
- Store `.claude/` on an encrypted volume
- Use git-crypt for version-controlled project memories

### Should I commit sensitive information?

**No!** Never commit:
- API keys
- Passwords
- Credentials
- Personal information
- Proprietary code

Use `.gitignore` for sensitive project memories:
```gitignore
.claude/memory/secrets/
```

### Can I delete all my memories?

Yes:
```bash
# Delete global memories
rm -rf ~/.claude/

# Delete project memories
rm -rf .claude/

# Re-initialize if needed
claude-memory init
```

---

## Skills

### How do I extract a skill from a candidate?

Currently manual:
1. Run `claude-memory analyze-skills`
2. Review `skill-candidates.md`
3. Manually create skill based on pattern
4. (Automatic skill creation is a future enhancement)

### What's the difference between a memory and a skill?

- **Memory**: Record of past work (session, decision, implementation)
- **Skill**: Reusable procedure extracted from repeated patterns

Skills are like "recipes" distilled from memories.

### Can I create skills manually?

Yes, skills are stored in `.claude/skills/`. Create a markdown file with the procedure:

```markdown
# Skill: Create REST API Endpoint

## Trigger
Creating API endpoints, REST, Flask

## Procedure
1. Define route in `app/routes/`
2. Create Pydantic model for request/response
3. Implement handler function
4. Add validation
5. Write tests in `tests/api/`
6. Update API documentation

## Example
See: memory-20260119-143052-abc123
```

### How often should I analyze for skills?

Recommended: Weekly or monthly
```bash
# Add to cron
0 0 * * 0 cd /project && claude-memory analyze-skills
```

---

## Advanced

### Can I customize memory triggers?

Yes, edit CLAUDE.md manually:

```markdown
## My Custom Pattern
**Brief**: Description
**When**: custom-trigger, .ext, keyword
**Details**: memory/implementations/file.md
**Tags**: tag1, tag2
```

### Can I write custom memory analyzers?

Yes! Use the Python API:

```python
from claude_memory import MemoryManager

manager = MemoryManager()
index = manager.global_index.read_index(include_logs=True)

# Your custom analysis
for memory in index.memories:
    if your_condition(memory):
        # Do something
        pass
```

See `docs/API.md` for full API reference.

### Can I use a database instead of JSON?

The system is designed for filesystem storage, but you could:
1. Implement custom `IndexManager` with database backend
2. Keep interface compatible
3. Replace in `MemoryManager.__init__`

File-based storage is intentional for:
- Human readability
- Git-friendliness
- No dependencies
- Simple backup/restore

### How do I migrate from old version?

Version migration guide will be added as versions evolve. Generally:
1. Backup current memories: `./scripts/export-memory.sh`
2. Update package: `pip install --upgrade`
3. Rebuild indices: `claude-memory rebuild-index`
4. Validate: `./scripts/validate-index.sh`

---

## Contributing

### I found a bug. What should I do?

1. Check if it's already reported in GitHub Issues
2. Create a new issue with:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)

### I have a feature idea. Where do I suggest it?

Open a GitHub Issue with:
- Use case description
- Proposed solution
- Why it's valuable
- Alternatives considered

### How do I contribute code?

See `CONTRIBUTING.md` for detailed guidelines:
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

---

## Getting Help

**Can't find your question here?**

- Check the documentation in `docs/`
- Search GitHub Issues
- Open a new issue
- Start a GitHub Discussion

**Documentation:**
- `README.md` - Overview and quick start
- `docs/USAGE.md` - User guide
- `docs/API.md` - API reference
- `docs/ARCHITECTURE.md` - System design
- `docs/EXAMPLES.md` - Usage examples
- `CONTRIBUTING.md` - Development guide
