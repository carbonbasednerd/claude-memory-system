# Architecture

## System Overview

The Claude Memory System implements a two-tier memory architecture for Claude Code with support for concurrent sessions and skill evolution.

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐                  ┌──────────────────┐   │
│  │  Short-Term    │                  │  Session         │   │
│  │  Memory        │◄─────────────────┤  Tracker         │   │
│  │  (CLAUDE.md)   │  Auto-updates    │  (Active)        │   │
│  └────────────────┘                  └──────────────────┘   │
│         │                                      │             │
│         │ Lazy Load                            │ Save        │
│         ▼                                      ▼             │
│  ┌────────────────────────────────────────────────────┐     │
│  │            Long-Term Memory Index                  │     │
│  │            (Append-Log + Base Index)               │     │
│  └────────────────────────────────────────────────────┘     │
│         │                                      │             │
│         │                                      │             │
│         ▼                                      ▼             │
│  ┌──────────────┐                    ┌─────────────────┐    │
│  │  Memory      │                    │  Skill          │    │
│  │  Files       │                    │  Candidates     │    │
│  │  (Markdown)  │                    │  (Patterns)     │    │
│  └──────────────┘                    └─────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Memory Manager (`memory.py`)

Central coordinator for all memory operations:
- Initializes global and project memory structures
- Coordinates between session tracking and long-term storage
- Handles scope resolution (global vs project)
- Provides search and retrieval interfaces

**Key Methods:**
- `create_session()` - Create new session tracker
- `save_session_to_memory()` - Archive session to long-term
- `search_memory()` - Search across global and project
- `record_memory_access()` - Track memory usage

### 2. Session Tracker (`session.py`)

Manages active session state:
- Tracks files modified
- Records decisions made
- Captures problems encountered
- Maintains notes and TODOs
- Auto-updates timestamp on changes

**Key Methods:**
- `update_task()` - Set current task
- `add_file_modified()` - Track file changes
- `add_decision()` - Record decision with rationale
- `add_problem()` - Log problem and solution
- `archive()` - Move to archived sessions
- `to_markdown()` - Export to markdown format

### 3. Index Manager (`index.py`)

Handles concurrent-safe index operations:
- Maintains base index + append-log
- Provides atomic write operations
- Merges log entries on read
- Rebuilds consolidated index periodically

**Key Methods:**
- `read_index()` - Read with optional log merging
- `add_memory()` - Append new memory via log
- `update_memory()` - Update via log
- `rebuild_index()` - Consolidate logs into base

### 4. Skill Detector (`skills.py`)

Analyzes patterns for skill extraction:
- Detects repeated procedures
- Identifies decision frameworks
- Finds problem-solution pairs
- Generates skill candidate reports

**Key Methods:**
- `detect_candidates()` - Find skill patterns
- `generate_report()` - Create markdown report
- `flag_skill_candidates()` - Update memory entries

### 5. CLI (`cli.py`)

Command-line interface:
- `init` - Initialize memory system
- `start-session` - Begin tracking
- `save-session` - Archive to long-term
- `search` - Find memories
- `show` - Display memory details
- `analyze-skills` - Detect patterns
- `rebuild-index` - Consolidate logs
- `cleanup-sessions` - Remove stale sessions
- `list-sessions` - Show active sessions
- `stats` - Display statistics

## Data Models

### MemoryEntry

Core data structure for long-term memory:

```python
class MemoryEntry(BaseModel):
    id: str                           # Unique identifier
    type: MemoryType                  # session, decision, implementation
    scope: MemoryScope                # global or project
    file: str                         # Relative path to markdown file
    title: str                        # Display title
    created: datetime                 # When created
    updated: datetime                 # Last updated
    tags: list[str]                   # Searchable tags
    summary: str                      # Brief summary
    keywords: list[str]               # Extracted keywords
    triggers: list[str]               # Lazy-load triggers
    related_files: list[str]          # Related memories
    files_modified: list[str]         # Code files touched
    decisions: list[str]              # Decisions made
    promoted: PromotionInfo           # Short-term promotion
    access: AccessInfo                # Usage tracking
    scope_decision: ScopeDecision     # How scope was chosen
    skill_candidate: SkillCandidate   # Skill extraction info
```

### SessionData

Tracks active work:

```python
class SessionData(BaseModel):
    session_id: str                   # Unique session ID
    started: datetime                 # Session start time
    last_updated: datetime            # Last activity
    task: str                         # Current task description
    status: SessionStatus             # active, archived, discarded
    files_modified: list[str]         # Files changed
    decisions: list[dict]             # Decisions with rationale
    problems: list[dict]              # Problems and solutions
    notes: list[str]                  # Free-form notes
    todos: list[str]                  # TODO items
```

## Concurrency Model

### Append-Only Log Strategy

To support multiple concurrent sessions:

1. **Reads are always safe**: Base index + log entries merged in memory
2. **Writes are isolated**: Each write creates a new log file
3. **No write conflicts**: Append-only, no file locking needed
4. **Eventual consistency**: Logs merged during periodic rebuild

### Log Entry Structure

```
.claude/memory/index-log/
├── 20260119143052123456-session-abc123.json
├── 20260119150234567890-session-def456.json
└── 20260119161145098765-session-ghi789.json
```

Each log entry contains:
- Operation type (add, update, delete)
- Timestamp
- Session ID
- Memory data

### Rebuild Process

```python
def rebuild_index():
    1. Read base index
    2. Read all log entries (sorted by timestamp)
    3. Apply each operation sequentially
    4. Calculate new stats
    5. Write consolidated index
    6. Delete log files
```

Triggered when:
- Log entries exceed threshold (default: 20)
- Manual rebuild command
- Scheduled periodic rebuild

## Memory Visibility

### Scope Hierarchy

```
Session in /home/user/project-a/
    │
    ├─► ~/.claude/ (Global)
    │   └─► Visible to ALL sessions
    │
    └─► /home/user/project-a/.claude/ (Project)
        └─► Visible ONLY to sessions in project-a
```

### Loading Order

1. Load global CLAUDE.md (memory pointers)
2. Load global index (include logs)
3. Load project CLAUDE.md (if exists)
4. Load project index (if exists)
5. Merge in memory for session

### Refresh Strategy

- **Periodic**: Check timestamps every 5 minutes
- **On-search**: Always refresh before searching
- **On-demand**: Force refresh via API call

## Lazy Loading

### Trigger Mechanism

CLAUDE.md contains lightweight pointers:

```markdown
## Python Coding Practices
**Brief**: Use type hints, dataclasses
**When**: python, .py, type hints
**Details**: memory/implementations/python-practices.md
**Tags**: python, coding
```

When Claude sees triggers in context:
1. Match conversation/file against triggers
2. Load full memory file if matched
3. Use detailed content for response
4. Don't load if irrelevant

### Benefits

- Minimal token usage in short-term
- Full context when needed
- Automatic relevance detection
- Scales to large memory collections

## Skill Evolution Pipeline

```
Work → Session → Pattern Detection → Skill Candidate → Manual Review → Skill Creation
  │                     ▲                    │
  │                     │                    │
  └─────────┬──────────┘                    │
            │                                 │
     Repeated Pattern                         │
     (3+ occurrences)                        │
            │                                 │
            └─────────────────────────────────┘
                  Feedback Loop
```

### Detection Criteria

**Procedure Pattern**:
- Similar task titles (60%+ word overlap)
- Minimum 3 occurrences
- Within 90-day window

**Decision Pattern**:
- Similar decision keywords
- Repeated rationale structure
- Common alternatives considered

**Problem-Solution Pattern**:
- Matching tags
- Similar problem descriptions
- Reusable solutions

## File Organization

### Global Structure

```
~/.claude/
├── CLAUDE.md                 # Static pointers (read-only during sessions)
├── config.json               # Configuration
├── memory/
│   ├── index.json            # Base index
│   ├── index-log/            # Append-only logs
│   │   └── *.json
│   ├── sessions/
│   │   ├── active/           # Session tracking files
│   │   │   └── session-*.json
│   │   └── archived/         # Completed sessions
│   │       └── YYYY-MM-DD-*.md
│   ├── decisions/
│   │   └── *.md
│   └── implementations/
│       └── *.md
├── sessions/
│   ├── active/               # Active session tracking (legacy location)
│   └── archived/             # Archived sessions (legacy location)
└── skills/
    ├── index.json
    └── skill-candidates.md
```

### Project Structure

Same as global, scoped to project directory.

## Design Decisions

### Why Append-Log vs Locking?

**Append-Log Chosen**:
- ✅ No blocking between sessions
- ✅ Simple implementation
- ✅ Resilient to crashes
- ✅ Human-readable log files
- ✅ Easy debugging

**vs File Locking**:
- ❌ Can cause session blocking
- ❌ Stale lock cleanup needed
- ❌ Single point of contention

### Why JSON vs SQLite?

**JSON Chosen**:
- ✅ Human-readable
- ✅ Easy to inspect and debug
- ✅ Git-friendly (project memory)
- ✅ No database setup
- ✅ Simple backup/restore

**vs SQLite**:
- ❌ Binary format
- ❌ Harder to inspect
- ❌ Not git-friendly
- ✅ Better querying (but we don't need it)

### Why Markdown for Memory Files?

**Markdown Chosen**:
- ✅ Human-readable
- ✅ Claude can read natively
- ✅ Git-friendly with diffs
- ✅ Easy to edit manually
- ✅ Portable across systems

## Performance Considerations

### Memory Usage

- **Short-term**: ~2-5KB loaded per session
- **Index**: ~100-500KB for 1000 memories
- **Log entries**: ~1-5KB each

### Search Performance

- **Small index** (<1000 entries): <10ms
- **Large index** (>1000 entries): <100ms
- **With logs** (+20 entries): +5-10ms

### Rebuild Performance

- **100 memories + 20 logs**: ~100ms
- **1000 memories + 20 logs**: ~500ms
- **Blocking**: No (done in background or on-demand)

## Extension Points

### Custom Memory Types

Add new `MemoryType` enum values:
- `PATTERN`
- `SNIPPET`
- `REFERENCE`

### Custom Analyzers

Extend `SkillDetector` with new pattern detectors:
- Security vulnerability patterns
- Performance optimization patterns
- Code smell patterns

### Custom Triggers

Add domain-specific triggers:
- Framework-specific (Django, React, etc.)
- Domain-specific (finance, healthcare)
- Company-specific (internal tools)

## Future Enhancements

1. **Auto-pruning**: Implement configurable retention policies
2. **Encryption**: Support for sensitive memory encryption
3. **Sync**: Cloud sync for multi-machine setups
4. **UI**: Web interface for browsing memory
5. **AI summaries**: Auto-generate better summaries
6. **Similarity search**: Vector embeddings for semantic search
7. **Automatic tagging**: ML-based tag suggestions
8. **Memory merging**: Detect and merge duplicate memories
