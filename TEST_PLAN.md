# Claude Memory System - Test Plan

**Version:** 1.0
**Date:** 2026-02-02
**Purpose:** Comprehensive testing of all Claude Memory System features

---

## Test Environment Setup

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Git repository initialized
- [ ] `claude-memory` installed (`pip install -e .`)
- [ ] Web dependencies installed (`pip install -e ".[web]"`)
- [ ] Clean test environment (backup existing `~/.claude/` if needed)

### Setup Steps
```bash
# 1. Navigate to test directory
cd /tmp/test-claude-memory

# 2. Initialize git repo
git init

# 3. Verify installation
claude-memory --version
```

---

## Test Suite 1: Core Memory System

### Test 1.1: Initialization
**Objective:** Verify memory system initialization

**Steps:**
```bash
# Test global initialization
claude-memory init --scope global

# Test project initialization (in git repo)
claude-memory init --scope project

# Test both scopes
claude-memory init
```

**Expected Results:**
- [ ] `~/.claude/CLAUDE.md` created with instructions
- [ ] `.claude/CLAUDE.md` created in project
- [ ] Directory structure created (memory/, skills/)
- [ ] config.json created
- [ ] No errors displayed

**Verification:**
```bash
ls -la ~/.claude/
ls -la .claude/
cat ~/.claude/CLAUDE.md
```

---

### Test 1.2: Session Management
**Objective:** Test session creation and tracking

**Steps:**
```bash
# Start a session
claude-memory start-session "Test authentication feature"

# List active sessions
claude-memory list-sessions

# Update current work
claude-memory update-current-work
```

**Expected Results:**
- [ ] Session file created in `~/.claude/memory/sessions/active/`
- [ ] Session appears in list-sessions output
- [ ] CLAUDE.md updated with current work section
- [ ] Session ID generated correctly

**Verification:**
```bash
ls ~/.claude/memory/sessions/active/
cat ~/.claude/CLAUDE.md | grep "Current Work"
```

---

### Test 1.3: Session Saving
**Objective:** Test saving sessions to long-term memory

**Steps:**
```bash
# Save session with tags and summary
claude-memory save-session \
  --tags "authentication,security,testing" \
  --summary "Implemented OAuth 2.0 authentication with JWT tokens"
```

**Expected Results:**
- [ ] Session archived to `sessions/archived/`
- [ ] Active session removed
- [ ] Markdown file created with metadata
- [ ] Index updated
- [ ] Manifest updated (if it exists)

**Verification:**
```bash
ls ~/.claude/memory/sessions/archived/
cat ~/.claude/memory/sessions/archived/*.md | head -30
cat ~/.claude/memory/index.json
```

---

### Test 1.4: Memory Search
**Objective:** Test basic memory search functionality

**Steps:**
```bash
# Create multiple sessions for testing
claude-memory start-session "Database optimization"
claude-memory save-session --tags "database,performance" --summary "Optimized queries"

claude-memory start-session "Frontend UI updates"
claude-memory save-session --tags "frontend,ui,react" --summary "Updated dashboard"

# Search by keyword
claude-memory search "authentication"
claude-memory search "database" --scope global
claude-memory search "frontend" --scope project
```

**Expected Results:**
- [ ] Search returns relevant sessions
- [ ] Results include title, tags, and summary
- [ ] Scope filtering works correctly
- [ ] No results for non-matching queries

---

## Test Suite 2: Manifest System

### Test 2.1: Manifest Creation
**Objective:** Test manifest generation and structure

**Steps:**
```bash
# Rebuild manifest
claude-memory rebuild-manifest

# Check both scopes
claude-memory rebuild-manifest --scope global
claude-memory rebuild-manifest --scope project
```

**Expected Results:**
- [ ] `manifest.json` created in `.claude/memory/`
- [ ] Manifest contains metadata for all memories
- [ ] Token size estimates included
- [ ] Tags and summaries included
- [ ] No full content in manifest (lightweight)

**Verification:**
```bash
cat ~/.claude/memory/manifest.json | jq '.'
cat ~/.claude/memory/manifest.json | jq '.memories | length'
cat ~/.claude/memory/manifest.json | jq '.total_tokens'
```

---

### Test 2.2: Context Reduction
**Objective:** Verify 30% context reduction claim

**Steps:**
```bash
# Count tokens in CLAUDE.md
wc -w ~/.claude/CLAUDE.md

# Compare with/without manifest
# (Manual inspection of what gets loaded)
```

**Expected Results:**
- [ ] Manifest is loaded on-demand only
- [ ] CLAUDE.md is lightweight (no full memory content)
- [ ] Context usage reduced compared to previous approach

---

## Test Suite 3: Debug Mode

### Test 3.1: Debug Mode Toggle
**Objective:** Test debug mode CLI commands

**Steps:**
```bash
# Enable debug mode
claude-memory debug on

# Check status
claude-memory debug status

# Disable debug mode
claude-memory debug off

# Check status again
claude-memory debug status
```

**Expected Results:**
- [ ] `debug on` creates `~/.claude/debug.flag`
- [ ] `debug status` shows current state
- [ ] `debug off` removes flag file
- [ ] Status changes reflect actual state

**Verification:**
```bash
ls ~/.claude/debug.flag
```

---

### Test 3.2: Debug Mode in Conversation
**Objective:** Test debug mode context tracking (manual test with Claude)

**Steps:**
1. Enable debug mode: `claude-memory debug on`
2. Start Claude Code session
3. Ask Claude: "turn on debug mode" or "show context usage"
4. Observe context usage report

**Expected Results:**
- [ ] Claude recognizes debug mode is enabled
- [ ] Context usage report displays
- [ ] Report shows breakdown by component
- [ ] Token counts are reasonable

---

## Test Suite 4: Visualization (Terminal UI)

### Test 4.1: Timeline View
**Objective:** Test timeline visualization

**Steps:**
```bash
# Basic timeline
claude-memory viz timeline

# With filters
claude-memory viz timeline --days 30
claude-memory viz timeline --scope project
claude-memory viz timeline --type session
claude-memory viz timeline --min-accesses 5
claude-memory viz timeline --never-accessed
```

**Expected Results:**
- [ ] Memories displayed chronologically
- [ ] Grouped by month
- [ ] Visual progress bars shown
- [ ] Access counts displayed
- [ ] Tags visible
- [ ] Filters work correctly
- [ ] Rich formatting (colors, tables)

---

### Test 4.2: Session Detail View
**Objective:** Test session detail display and access tracking

**Steps:**
```bash
# Get a session ID from timeline
SESSION_ID=$(claude-memory viz timeline | grep -o 'session-[0-9-a-z]*' | head -1)

# View session details
claude-memory viz session $SESSION_ID

# View again to test access increment
claude-memory viz session $SESSION_ID
```

**Expected Results:**
- [ ] Full session details displayed
- [ ] Access count shown prominently
- [ ] First and last accessed timestamps
- [ ] Tags with color coding
- [ ] Summary and decisions visible
- [ ] Files modified listed
- [ ] Related sessions shown
- [ ] Access count increments on each view

**Verification:**
```bash
# Check access tracking in index
cat ~/.claude/memory/index.json | jq '.memories[] | select(.id=="'$SESSION_ID'") | .access_tracking'
```

---

### Test 4.3: Search Interface
**Objective:** Test advanced search with filters and export

**Steps:**
```bash
# Basic search
claude-memory viz search "authentication"

# With filters
claude-memory viz search "security" --scope project --tags "vlan,firewall" --days 30

# Access-based filters
claude-memory viz search "documentation" --min-accesses 5
claude-memory viz search "old-project" --never-accessed
claude-memory viz search "recent" --accessed-after 2026-01-01
claude-memory viz search "stale" --accessed-before 2025-12-31

# Export formats
claude-memory viz search "api" --export json > results.json
claude-memory viz search "security" --export markdown > report.md
```

**Expected Results:**
- [ ] Search results sorted by relevance
- [ ] Filters work correctly
- [ ] Visual indicators for frequently accessed memories (⭐)
- [ ] JSON export is valid JSON
- [ ] Markdown export is formatted correctly
- [ ] Export files created successfully

**Verification:**
```bash
cat results.json | jq '.'
head -20 report.md
```

---

### Test 4.4: Statistics Dashboard
**Objective:** Test stats dashboard and export

**Steps:**
```bash
# Full dashboard
claude-memory viz stats

# Scoped stats
claude-memory viz stats --scope global
claude-memory viz stats --scope project

# Export
claude-memory viz stats --export json > stats.json
```

**Expected Results:**
- [ ] Overview section (total memories, accesses, average)
- [ ] Breakdown by type
- [ ] Most accessed (top 10) shown
- [ ] Never accessed memories listed
- [ ] Activity timeline displayed
- [ ] Top tags with frequency bars
- [ ] Export contains all stats data

**Verification:**
```bash
cat stats.json | jq '.overview'
```

---

### Test 4.5: Tag Analysis
**Objective:** Test tag visualization

**Steps:**
```bash
# All tags
claude-memory viz tags

# With filters
claude-memory viz tags --min-count 3
claude-memory viz tags --scope project
```

**Expected Results:**
- [ ] Tag cloud displayed
- [ ] Frequency counts shown
- [ ] Access statistics per tag
- [ ] Co-occurrence network shown
- [ ] Orphaned tags identified
- [ ] Visual bars for frequency

---

### Test 4.6: Project Map
**Objective:** Test project discovery and mapping

**Steps:**
```bash
# Scan all projects
claude-memory viz projects
```

**Expected Results:**
- [ ] All `.claude` directories found
- [ ] Session/decision counts per project
- [ ] Most recent memory per project
- [ ] Most accessed memory per project
- [ ] Top tags per project
- [ ] Tree visualization
- [ ] Color-coded output

---

### Test 4.7: Health Check
**Objective:** Test memory system health checks

**Steps:**
```bash
# Full health check
claude-memory viz health

# Scoped check
claude-memory viz health --scope project
```

**Expected Results:**
- [ ] System integrity checks pass
- [ ] Quality warnings displayed:
  - Untagged sessions
  - Never-accessed memories
  - Potential duplicates
  - Stale sessions (>6 months, unused)
- [ ] Actionable recommendations provided
- [ ] Color-coded status (green/yellow/red)

---

## Test Suite 5: Web Dashboard

### Test 5.1: Web Dashboard Launch
**Objective:** Test web server startup

**Steps:**
```bash
# Launch with default settings
claude-memory web &
WEB_PID=$!

# Wait for startup
sleep 5

# Test custom port
kill $WEB_PID
claude-memory web --port 8080 --no-open &
WEB_PID=$!
```

**Expected Results:**
- [ ] Streamlit server starts successfully
- [ ] Browser opens automatically (default)
- [ ] No errors in console
- [ ] Custom port works
- [ ] `--no-open` prevents browser launch

**Verification:**
```bash
curl -s http://localhost:8501/ | grep -q "Streamlit"
kill $WEB_PID
```

---

### Test 5.2: Web Dashboard Tabs
**Objective:** Test all dashboard tabs (manual browser test)

**Steps:**
1. Launch: `claude-memory web`
2. Navigate to each tab:
   - Overview
   - Timeline
   - Analytics
   - Tags
   - Search

**Expected Results:**

**Overview Tab:**
- [ ] Statistics cards displayed
- [ ] Total memories, accesses, average
- [ ] Breakdown by type
- [ ] Recent activity

**Timeline Tab:**
- [ ] Interactive Plotly timeline
- [ ] Zoom and pan work
- [ ] Hover shows details
- [ ] Click opens session modal

**Analytics Tab:**
- [ ] Tag network graph (force-directed)
- [ ] Activity trends chart
- [ ] Cumulative growth chart
- [ ] Type trends stacked area
- [ ] Activity calendar heatmap
- [ ] Co-occurrence threshold slider works

**Tags Tab:**
- [ ] Tag frequency chart
- [ ] Co-occurrence table
- [ ] Access statistics

**Search Tab:**
- [ ] Search input works
- [ ] Multiple result views
- [ ] Filters apply correctly
- [ ] Results update in real-time

---

### Test 5.3: Web Dashboard Filters
**Objective:** Test sidebar filtering (manual browser test)

**Steps:**
1. Open web dashboard
2. Use sidebar filters:
   - Scope (Global/Project)
   - Type (Session/Decision/Implementation)
   - Tags (multi-select)
   - Date range slider
   - Access count slider
3. Use preset filters:
   - Last 7/30/90 days
   - Never Accessed
   - Popular (5+ accesses)

**Expected Results:**
- [ ] Filters update all visualizations
- [ ] Result counts shown
- [ ] Preset filters work
- [ ] Multiple filters combine correctly
- [ ] Refresh button reloads data

---

### Test 5.4: Web Dashboard Export
**Objective:** Test export functionality (manual browser test)

**Steps:**
1. Navigate to Analytics tab
2. Click export buttons:
   - JSON export
   - Markdown export
   - CSV export

**Expected Results:**
- [ ] JSON file downloads with valid JSON
- [ ] Markdown file downloads with formatted content
- [ ] CSV file downloads with proper columns
- [ ] Files contain current filtered data
- [ ] File names include timestamp

**Verification:**
```bash
cat ~/Downloads/memories-export-*.json | jq '.'
head ~/Downloads/memories-export-*.csv
```

---

## Test Suite 6: Skill Management

### Test 6.1: Skill Analysis
**Objective:** Test skill candidate detection

**Steps:**
```bash
# Create sessions with patterns
claude-memory start-session "Fix authentication bug"
claude-memory save-session --tags "bugfix,auth" --summary "Fixed login issue"

claude-memory start-session "Fix authorization bug"
claude-memory save-session --tags "bugfix,auth" --summary "Fixed permission issue"

# Analyze for skills
claude-memory analyze-skills
```

**Expected Results:**
- [ ] Skill candidates identified
- [ ] Patterns detected (repeated tags, similar summaries)
- [ ] Candidate saved to `skill-candidates.md`
- [ ] Recommendations provided

**Verification:**
```bash
cat ~/.claude/skills/skill-candidates.md
```

---

### Test 6.2: Skill Extraction
**Objective:** Test skill extraction from session

**Steps:**
```bash
# Extract skill from session
SESSION_ID=$(claude-memory viz timeline | grep -o 'session-[0-9-a-z]*' | head -1)
claude-memory extract-skill $SESSION_ID
```

**Expected Results:**
- [ ] Skill definition created
- [ ] Skill index updated
- [ ] Session marked as skill source
- [ ] Skill contains relevant context

---

## Test Suite 7: Maintenance & Operations

### Test 7.1: Index Rebuild
**Objective:** Test index reconstruction

**Steps:**
```bash
# Backup current index
cp ~/.claude/memory/index.json ~/.claude/memory/index.json.backup

# Rebuild index
claude-memory rebuild-index

# Compare
diff ~/.claude/memory/index.json.backup ~/.claude/memory/index.json
```

**Expected Results:**
- [ ] Index rebuilt successfully
- [ ] All memories present
- [ ] Logs consolidated
- [ ] No data loss

---

### Test 7.2: Session Cleanup
**Objective:** Test stale session cleanup

**Steps:**
```bash
# Create old session manually (modify timestamp)
# Then cleanup
claude-memory cleanup-sessions
```

**Expected Results:**
- [ ] Sessions >24 hours old are removed
- [ ] Active sessions with recent activity preserved
- [ ] Cleanup summary shown

---

### Test 7.3: Export/Backup
**Objective:** Test memory export

**Steps:**
```bash
# Export all memory
claude-memory export --output backup.tar.gz

# Extract and verify
mkdir test-extract
tar -xzf backup.tar.gz -C test-extract
ls -la test-extract/
```

**Expected Results:**
- [ ] Archive created successfully
- [ ] Contains all memory files
- [ ] CLAUDE.md included
- [ ] Index files included
- [ ] Sessions included
- [ ] Archive is valid tar.gz

---

## Test Suite 8: Integration Tests

### Test 8.1: Concurrent Sessions
**Objective:** Test multiple sessions working simultaneously

**Steps:**
```bash
# Terminal 1
claude-memory start-session "Task A"

# Terminal 2
claude-memory start-session "Task B"

# List from both
claude-memory list-sessions
```

**Expected Results:**
- [ ] Both sessions created
- [ ] No conflicts
- [ ] Append-log handles concurrency
- [ ] Both sessions visible in list

---

### Test 8.2: Global vs Project Scope
**Objective:** Test scope isolation

**Steps:**
```bash
# Create global memory
claude-memory start-session "Global task" --scope global
claude-memory save-session --tags "global" --summary "Global work"

# Create project memory
cd /tmp/test-project
git init
claude-memory init --scope project
claude-memory start-session "Project task"
claude-memory save-session --tags "project" --summary "Project work"

# Search each scope
claude-memory search "task" --scope global
claude-memory search "task" --scope project
```

**Expected Results:**
- [ ] Global memory accessible from anywhere
- [ ] Project memory isolated to project
- [ ] Scope filtering works correctly
- [ ] No cross-contamination

---

### Test 8.3: End-to-End Workflow
**Objective:** Complete workflow from init to visualization

**Steps:**
```bash
# 1. Initialize
claude-memory init

# 2. Create and save sessions
claude-memory start-session "Feature A"
claude-memory save-session --tags "feature,ui" --summary "Added dashboard"

claude-memory start-session "Bug fix B"
claude-memory save-session --tags "bugfix,backend" --summary "Fixed API"

# 3. Rebuild manifest
claude-memory rebuild-manifest

# 4. Search
claude-memory search "dashboard"

# 5. Visualize
claude-memory viz timeline
claude-memory viz stats
claude-memory viz tags

# 6. Web dashboard
claude-memory web --no-open &
WEB_PID=$!
sleep 5

# 7. Export
claude-memory viz search "all" --export json > all-memories.json

# 8. Cleanup
kill $WEB_PID
```

**Expected Results:**
- [ ] Complete workflow executes without errors
- [ ] All commands work together
- [ ] Data consistent across all views
- [ ] Export contains all data

---

## Test Suite 9: Error Handling

### Test 9.1: Invalid Commands
**Objective:** Test error handling for invalid inputs

**Steps:**
```bash
# Invalid scope
claude-memory init --scope invalid

# Invalid session ID
claude-memory viz session invalid-id

# Missing required args
claude-memory save-session

# Invalid export format
claude-memory viz search "test" --export invalid
```

**Expected Results:**
- [ ] Clear error messages
- [ ] No crashes
- [ ] Helpful suggestions provided
- [ ] Exit codes set correctly

---

### Test 9.2: Missing Dependencies
**Objective:** Test graceful degradation

**Steps:**
```bash
# Try web without dependencies (in clean venv)
python -m venv test-env
source test-env/bin/activate
pip install -e .  # Without [web]
claude-memory web
```

**Expected Results:**
- [ ] Clear error message about missing dependencies
- [ ] Suggestion to install with `pip install -e ".[web]"`
- [ ] Core features still work

---

### Test 9.3: Corrupted Data
**Objective:** Test recovery from corrupted files

**Steps:**
```bash
# Corrupt index
echo "invalid json" > ~/.claude/memory/index.json

# Try to use system
claude-memory list-sessions

# Rebuild
claude-memory rebuild-index
```

**Expected Results:**
- [ ] Error detected
- [ ] Rebuild command fixes issue
- [ ] Data recovered from logs
- [ ] No data loss

---

## Test Suite 10: Performance Tests

### Test 10.1: Large Memory Set
**Objective:** Test with many memories

**Steps:**
```bash
# Create 100+ sessions (script)
for i in {1..100}; do
  claude-memory start-session "Test session $i"
  claude-memory save-session --tags "test,perf" --summary "Session $i"
done

# Test operations
time claude-memory search "test"
time claude-memory viz timeline
time claude-memory viz stats
time claude-memory rebuild-manifest
```

**Expected Results:**
- [ ] Search completes in <2 seconds
- [ ] Visualization loads in <3 seconds
- [ ] Manifest rebuild in <5 seconds
- [ ] No memory issues
- [ ] Web dashboard responsive

---

### Test 10.2: Context Budget
**Objective:** Verify context stays within budget

**Steps:**
```bash
# Enable debug mode
claude-memory debug on

# Create many memories
# Check context usage in Claude session
```

**Expected Results:**
- [ ] Always-loaded context ≤ 968 tokens
- [ ] Manifest loaded on-demand
- [ ] Total context < 5000 token budget
- [ ] No performance degradation

---

## Test Results Summary

### Pass/Fail Criteria
- **Critical:** All Core Memory System tests must pass
- **High Priority:** Visualization, Debug Mode, Manifest tests
- **Medium Priority:** Web Dashboard, Skill Management
- **Low Priority:** Performance optimizations

### Test Execution Log

| Test Suite | Total Tests | Passed | Failed | Skipped | Notes |
|------------|-------------|--------|--------|---------|-------|
| 1. Core Memory | | | | | |
| 2. Manifest | | | | | |
| 3. Debug Mode | | | | | |
| 4. Visualization | | | | | |
| 5. Web Dashboard | | | | | |
| 6. Skill Management | | | | | |
| 7. Maintenance | | | | | |
| 8. Integration | | | | | |
| 9. Error Handling | | | | | |
| 10. Performance | | | | | |

### Issues Found
| ID | Severity | Test | Description | Status |
|----|----------|------|-------------|--------|
| | | | | |

---

## Regression Testing

When making changes, re-run relevant test suites:
- **Code changes in `viz/`**: Run Test Suite 4
- **Code changes in `web/`**: Run Test Suite 5
- **Code changes in `manifest.py`**: Run Test Suite 2
- **Code changes in `context_tracker.py`**: Run Test Suite 3
- **Any core changes**: Run Test Suites 1, 8, 9

---

## Automated Testing Script

**Status:** ✅ Implemented in `scripts/run-tests.sh`

### Quick Start

```bash
# Run all automated tests
./scripts/run-tests.sh

# Run with verbose output
./scripts/run-tests.sh --verbose

# Run specific test suite
./scripts/run-tests.sh --suite 4  # Visualization tests only

# Keep test artifacts for inspection
./scripts/run-tests.sh --no-cleanup
```

### What Gets Tested

The automated script runs **27 test cases** (84% of total):
- ✅ Suite 1: Core Memory System (4 tests)
- ✅ Suite 2: Manifest System (2 tests)
- ✅ Suite 3: Debug Mode (1 test + 1 manual)
- ✅ Suite 4: Visualization (7 tests)
- ✅ Suite 6: Skill Management (2 tests)
- ✅ Suite 7: Maintenance (3 tests)
- ✅ Suite 8: Integration (3 tests)
- ✅ Suite 9: Error Handling (2 tests + 1 skip)
- ✅ Suite 10: Performance (1 test + 1 manual)

### Manual Tests (Not Automated)

These 5 tests require manual execution:
- 3.2: Debug Mode In-Conversation (requires Claude session)
- 5.1-5.4: Web Dashboard UI (requires browser interaction)
- 10.2: Context Budget (requires Claude session)

### Features

- **Automatic environment setup** - Creates isolated test environment
- **Backup protection** - Backs up existing `~/.claude/` before testing
- **Colored output** - Green (pass), red (fail), yellow (skip/warn)
- **Detailed reporting** - Shows which tests failed
- **Cleanup** - Restores original environment after tests
- **Selective execution** - Run individual test suites
- **Performance testing** - Creates 50 sessions for load testing

### Options

```
Usage: ./scripts/run-tests.sh [OPTIONS]

Options:
  -v, --verbose       Show detailed command output
  --no-cleanup        Don't cleanup test environment after run
  --suite SUITE       Run specific test suite (1-10, or 'all')
  -h, --help          Show this help message
```

---

## Notes
- Manual tests (browser-based) marked with "(manual browser test)"
- Some tests require multiple terminals or time delays
- Performance benchmarks are approximate
- Test with both empty and populated memory systems
- Test on different platforms (Linux, macOS, Windows)

---

**Test Plan Version History:**
- v1.0 (2026-02-02): Initial comprehensive test plan
