# Examples

## Complete Workflow Examples

### Example 1: Automatic Workflow with Claude Code (Recommended)

**Scenario**: You're working with Claude Code and the memory system manages everything automatically.

**Starting a new session:**
```
You: Hi Claude!

Claude: Welcome back! I see you have one active session:
- "Implement OAuth2 authentication" - Working on src/auth/oauth.py

Would you like to continue with that, or start something new?

You: Let's continue the OAuth work.

Claude: Great! I'll help you continue the OAuth2 authentication work...
```

**Claude automatically:**
- Ran `claude-memory update-current-work` at session start
- Greeted you and summarized active work
- Created session tracker (if starting new work)
- Tracks all files, decisions, and problems as you work

**When you're done:**
```
You: I think we're done with the OAuth implementation. Let's save this.

Claude: I'll save this session to long-term memory.

[Claude runs: claude-memory save-session --scope project --tags "authentication,OAuth2,security" --summary "Implemented OAuth2 flow with JWT tokens"]

✓ Saved session to project memory
  Memory ID: session-20260120-oauth-impl
  Title: Implement OAuth2 authentication

Your work has been saved! You can find it later by searching for "OAuth" or "authentication".
```

**No manual commands needed** - just work naturally with Claude!

---

### Example 2: Feature Development with Manual Commands

**Scenario**: You're building an authentication system and want to track the work.

```bash
# 1. Start session
claude-memory start-session "Implement OAuth2 authentication"

# 2. Work on the feature
# Claude automatically tracks:
# - Files you create/modify (src/auth/oauth.py, src/middleware/auth.py)
# - Decisions (chose JWT over sessions, httpOnly cookies vs localStorage)
# - Problems (CORS issues, token refresh race condition)

# 3. Save session when done
claude-memory save-session \
  --scope project \
  --tags "authentication,OAuth2,security,JWT" \
  --summary "Implemented OAuth2 flow with JWT refresh tokens. Chose httpOnly cookies for XSS protection. Fixed CORS and refresh race conditions."

# 4. Memory is now saved and searchable
claude-memory search "authentication" --scope project
```

### Example 3: Finding Past Solutions

**Scenario**: You encounter a CORS issue and remember solving it before.

```bash
# Search for past CORS solutions
claude-memory search "CORS" --tags "security"

# View the specific memory
claude-memory show memory-20260119-oauth-impl

# The memory shows:
# - Problem: CORS blocking credentials
# - Solution: Added credentials: 'include' and proper headers
# - Code location: src/middleware/cors.py:45
```

### Example 4: Building a Skill from Patterns

**Scenario**: You've implemented 5 similar API endpoints and want to create a reusable skill.

```bash
# 1. Analyze patterns
claude-memory analyze-skills --scope project --min-occurrences 3

# Output:
# Found 1 skill candidate:
# • API Endpoint Creation Pattern
#   Type: procedure
#   Confidence: high
#   Occurrences: 5
#   Suggested name: create-api-endpoint

# 2. Review the pattern
# Open .claude/skill-candidates.md to see:
# - Common steps across all 5 implementations
# - Files typically modified
# - Standard testing approach

# 3. Extract to skill (manual process for now)
# Create a skill based on the pattern
```

### Example 5: Cross-Project Learning

**Scenario**: You solved a complex problem in Project A and want to use it in Project B.

**In Project A:**
```bash
cd ~/projects/project-a

# Save the solution to global memory (not project)
claude-memory save-session \
  --scope global \
  --tags "database,performance,indexing" \
  --summary "Optimized database queries with compound indexes. 10x speedup on user search."
```

**In Project B:**
```bash
cd ~/projects/project-b

# Search global memory
claude-memory search "database performance" --scope global

# Find the solution from Project A
claude-memory show memory-20260119-db-optimization

# Apply the same pattern to Project B
```

### Example 6: Concurrent Sessions

**Scenario**: You're working on two features simultaneously in different terminals.

**Terminal 1:**
```bash
# Session 1: Working on frontend
claude-memory start-session "Redesign user dashboard"
# ... make changes to React components ...
```

**Terminal 2:**
```bash
# Session 2: Working on backend
claude-memory start-session "Add analytics API"
# ... make changes to API endpoints ...

# View what other sessions are doing
claude-memory list-sessions

# Output:
# Project Sessions:
#   - session-20260119-143052-abc123
#     Task: Redesign user dashboard
#     Started: 2026-01-19 14:30:52
#
#   - session-20260119-150234-def456
#     Task: Add analytics API
#     Started: 2026-01-19 15:02:34
```

**Both sessions save independently without conflicts:**
```bash
# Terminal 1
claude-memory save-session --tags "frontend,React,dashboard"

# Terminal 2
claude-memory save-session --tags "backend,API,analytics"
```

## Memory Organization Strategies

### Strategy 1: Feature-Based Organization

Tag memories by feature:
- `--tags "auth,feature-user-login"`
- `--tags "payments,feature-checkout"`
- `--tags "admin,feature-user-management"`

### Strategy 2: Technology-Based Organization

Tag by tech stack:
- `--tags "React,frontend,hooks"`
- `--tags "PostgreSQL,backend,database"`
- `--tags "AWS,deployment,infrastructure"`

### Strategy 3: Problem-Domain Organization

Tag by problem type:
- `--tags "performance,optimization"`
- `--tags "security,vulnerability-fix"`
- `--tags "bug-fix,edge-case"`

### Strategy 4: Mixed Approach (Recommended)

Combine multiple dimensions:
```bash
claude-memory save-session \
  --tags "authentication,security,backend,bug-fix,CORS" \
  --summary "Fixed CORS issue in OAuth flow"
```

## Advanced Usage

### Custom Memory Files

You can manually create memory files in `.claude/memory/`:

```bash
# Create a decision record
cat > .claude/memory/decisions/api-versioning.md << 'EOF'
# API Versioning Strategy

**Date**: 2026-01-19
**Decision**: Use URL-based versioning (/v1/, /v2/)

## Rationale
- Simple and explicit
- Easy to route and cache
- Industry standard

## Alternatives Considered
- Header-based versioning: Rejected (not cache-friendly)
- Query param versioning: Rejected (not RESTful)

## Impact
- All API routes must include version prefix
- Version must be in URL routing
EOF

# Add to index manually or rebuild
claude-memory rebuild-index
```

### CLAUDE.md Memory Pointers

Add pointers to frequently accessed memories:

```markdown
# Memory Pointers

## Authentication System
**Brief**: OAuth2 with JWT, httpOnly cookies
**When**: auth, login, tokens, security
**Details**: memory/implementations/auth-system.md
**Tags**: authentication, OAuth2, JWT

## Database Schema
**Brief**: PostgreSQL normalized schema with Prisma
**When**: database, schema, migrations
**Details**: memory/decisions/database-architecture.md
**Tags**: database, PostgreSQL, Prisma
```

Claude will automatically load these when working on related topics.

### Maintenance Routine

Weekly maintenance script:

```bash
#!/bin/bash
# weekly-maintenance.sh

echo "=== Weekly Memory Maintenance ==="

# 1. Cleanup stale sessions
echo "Cleaning up stale sessions..."
claude-memory cleanup-sessions --hours 48 --auto-archive

# 2. Rebuild indices
echo "Rebuilding indices..."
claude-memory rebuild-index --scope global
claude-memory rebuild-index --scope project

# 3. Analyze for new skills
echo "Analyzing for skill patterns..."
claude-memory analyze-skills --scope both

# 4. Show stats
echo "Current stats:"
claude-memory stats

# 5. Backup
echo "Creating backup..."
./scripts/export-memory.sh "backup-$(date +%Y%m%d).tar.gz"

echo "✓ Maintenance complete"
```

## Integration Patterns

### Pattern 1: Pre-commit Hook

Save session before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash

if [ -f ".claude/sessions/active/"*.json ]; then
    echo "Active session detected. Save it?"
    read -p "Save session to memory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        claude-memory save-session
    fi
fi
```

### Pattern 2: CI/CD Integration

Export memory as build artifact:

```yaml
# .github/workflows/backup-memory.yml
name: Backup Memory
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Export memory
        run: ./scripts/export-memory.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: memory-backup
          path: '*.tar.gz'
```

### Pattern 3: Team Sharing

Share project memory via git:

```bash
# Include project .claude/ in git
echo "# Project Memory" > .claude/README.md
git add .claude/
git commit -m "Add project memory"

# Team members get shared memory
git pull
claude-memory search "team" --scope project
```

## Troubleshooting

### Problem: Index out of sync

```bash
# Solution: Rebuild index
claude-memory rebuild-index --scope both
./scripts/validate-index.sh
```

### Problem: Too many log entries

```bash
# Check log count
ls -l .claude/memory/index-log/ | wc -l

# Rebuild to merge
claude-memory rebuild-index
```

### Problem: Can't find old memory

```bash
# Search with broader query
claude-memory search "" --scope both --limit 100

# Check if it's in archived sessions
ls -l .claude/sessions/archived/
```

### Problem: Stale sessions piling up

```bash
# Regular cleanup
claude-memory cleanup-sessions --hours 24 --auto-archive

# Or add to cron
crontab -e
# Add: 0 0 * * * cd ~/project && claude-memory cleanup-sessions --auto-archive
```
