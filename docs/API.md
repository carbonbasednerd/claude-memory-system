# API Reference

Complete API documentation for developers who want to programmatically integrate with or extend the Claude Memory System.

## Overview

The Claude Memory System provides a Python API for:
- Creating and managing memory sessions
- Saving and searching long-term memories
- Detecting skill patterns
- Managing concurrent sessions safely

## Installation

```python
# As a library
from claude_memory import MemoryManager, SessionTracker
```

```bash
# Development installation
cd ~/git/jay-i
pip install -e .
```

## Quick Start

```python
from claude_memory import MemoryManager
from claude_memory.models import MemoryScope

# Initialize memory manager
manager = MemoryManager()

# Create a session
session = manager.create_session()
session.update_task("Implement user authentication")

# Track work
session.add_file_modified("src/auth/login.py")
session.add_decision(
    decision="Use JWT tokens",
    rationale="Stateless, scalable, industry standard",
    alternatives=["Session cookies", "OAuth only"]
)

# Save to long-term memory
memory = manager.save_session_to_memory(
    session=session,
    scope=MemoryScope.PROJECT,
    tags=["authentication", "security"],
    summary="Implemented JWT-based authentication"
)

# Search memory
results = manager.search_memory(
    query="authentication",
    tags=["security"]
)
```

## Core Classes

### MemoryManager

Main interface for the memory system.

#### Constructor

```python
MemoryManager(working_dir: Path | None = None)
```

**Parameters:**
- `working_dir`: Current working directory (defaults to `Path.cwd()`)

**Attributes:**
- `global_dir`: Path to global `~/.claude/` directory
- `project_dir`: Path to project `.claude/` directory (if in a project)
- `global_index`: Global `IndexManager` instance
- `project_index`: Project `IndexManager` instance (if applicable)
- `config`: Loaded configuration

#### Methods

##### create_session()

```python
create_session(session_id: str | None = None) -> SessionTracker
```

Create a new session tracker.

**Parameters:**
- `session_id`: Optional session ID (auto-generated if not provided)

**Returns:**
- `SessionTracker` instance

**Example:**
```python
session = manager.create_session()
session.update_task("Fix bug in checkout flow")
```

##### save_session_to_memory()

```python
save_session_to_memory(
    session: SessionTracker,
    scope: MemoryScope,
    memory_type: MemoryType = MemoryType.SESSION,
    tags: list[str] | None = None,
    summary: str | None = None,
) -> MemoryEntry
```

Save a session to long-term memory.

**Parameters:**
- `session`: The session to save
- `scope`: `MemoryScope.GLOBAL` or `MemoryScope.PROJECT`
- `memory_type`: Type of memory entry (default: `MemoryType.SESSION`)
- `tags`: List of tags for searchability
- `summary`: Brief summary of the session

**Returns:**
- Created `MemoryEntry`

**Example:**
```python
memory = manager.save_session_to_memory(
    session=session,
    scope=MemoryScope.PROJECT,
    tags=["bug-fix", "checkout", "payments"],
    summary="Fixed race condition in checkout process"
)
print(f"Saved memory: {memory.id}")
```

##### search_memory()

```python
search_memory(
    query: str = "",
    tags: list[str] | None = None,
    memory_type: MemoryType | None = None,
    scope: MemoryScope | None = None,
) -> list[MemoryEntry]
```

Search memory across global and/or project.

**Parameters:**
- `query`: Search query (searches title, summary, keywords, triggers)
- `tags`: Filter by tags (OR matching)
- `memory_type`: Filter by type
- `scope`: Search only specific scope (`None` = both global and project)

**Returns:**
- List of matching `MemoryEntry` objects, sorted by relevance

**Example:**
```python
# Search all memories
results = manager.search_memory("database")

# Search with filters
results = manager.search_memory(
    query="performance",
    tags=["optimization"],
    scope=MemoryScope.PROJECT
)

for memory in results:
    print(f"{memory.title} - {memory.summary}")
```

##### get_memory()

```python
get_memory(memory_id: str) -> MemoryEntry | None
```

Get a specific memory entry by ID.

**Parameters:**
- `memory_id`: The memory ID to retrieve

**Returns:**
- `MemoryEntry` if found, `None` otherwise

**Example:**
```python
memory = manager.get_memory("memory-20260119-143052-a1b2c3")
if memory:
    print(f"Title: {memory.title}")
    print(f"Summary: {memory.summary}")
```

##### record_memory_access()

```python
record_memory_access(memory_id: str, query: str = "") -> None
```

Record that a memory was accessed (updates access tracking).

**Parameters:**
- `memory_id`: The memory ID that was accessed
- `query`: Optional search query that led to this access

**Example:**
```python
manager.record_memory_access(
    "memory-20260119-143052-a1b2c3",
    query="authentication"
)
```

---

### SessionTracker

Tracks an active Claude Code session.

#### Constructor

```python
SessionTracker(claude_dir: Path, session_id: str | None = None)
```

**Parameters:**
- `claude_dir`: Path to `.claude` directory
- `session_id`: Optional session ID (auto-generated if not provided)

**Attributes:**
- `session_id`: Unique session identifier
- `data`: `SessionData` object containing all session information

#### Methods

##### update_task()

```python
update_task(task: str) -> None
```

Update the current task description.

**Example:**
```python
session.update_task("Refactor authentication module")
```

##### add_file_modified()

```python
add_file_modified(file_path: str) -> None
```

Track a file that was modified.

**Example:**
```python
session.add_file_modified("src/auth/login.py")
session.add_file_modified("tests/test_auth.py")
```

##### add_decision()

```python
add_decision(
    decision: str,
    rationale: str,
    alternatives: list[str] | None = None
) -> None
```

Track a decision made during the session.

**Example:**
```python
session.add_decision(
    decision="Use PostgreSQL instead of MySQL",
    rationale="Better JSON support and PostGIS for geospatial",
    alternatives=["MySQL", "MongoDB", "SQLite"]
)
```

##### add_problem()

```python
add_problem(problem: str, solution: str | None = None) -> None
```

Track a problem encountered and its solution.

**Example:**
```python
session.add_problem(
    problem="CORS errors blocking API calls from frontend",
    solution="Added CORS middleware with credentials support"
)
```

##### add_note()

```python
add_note(note: str) -> None
```

Add a free-form note to the session.

**Example:**
```python
session.add_note("Need to update API documentation after this change")
```

##### add_todo() / remove_todo()

```python
add_todo(todo: str) -> None
remove_todo(todo: str) -> None
```

Manage TODO items.

**Example:**
```python
session.add_todo("Add integration tests")
session.add_todo("Update changelog")
# ... later ...
session.remove_todo("Add integration tests")
```

##### save()

```python
save() -> None
```

Manually save session data to file (called automatically by other methods).

##### archive()

```python
archive(archive_name: str | None = None) -> Path
```

Archive this session.

**Returns:**
- Path to archived file

**Example:**
```python
archive_path = session.archive()
print(f"Session archived to: {archive_path}")
```

##### discard()

```python
discard() -> None
```

Discard this session without archiving.

##### to_markdown()

```python
to_markdown() -> str
```

Convert session data to markdown format.

**Returns:**
- Markdown string representation

##### Class Methods

###### list_active_sessions()

```python
@classmethod
list_active_sessions(cls, claude_dir: Path) -> list[SessionData]
```

List all active sessions in a `.claude` directory.

**Example:**
```python
sessions = SessionTracker.list_active_sessions(Path.home() / ".claude")
for session in sessions:
    print(f"{session.session_id}: {session.task}")
```

###### cleanup_stale_sessions()

```python
@classmethod
cleanup_stale_sessions(
    cls,
    claude_dir: Path,
    hours_threshold: int = 24
) -> list[str]
```

Find stale sessions with no activity for specified hours.

**Returns:**
- List of stale session IDs

---

### IndexManager

Manages memory index with append-log for concurrent safety.

#### Constructor

```python
IndexManager(claude_dir: Path, scope: MemoryScope)
```

**Parameters:**
- `claude_dir`: Path to `.claude` directory
- `scope`: `MemoryScope.GLOBAL` or `MemoryScope.PROJECT`

#### Methods

##### read_index()

```python
read_index(include_logs: bool = True) -> MemoryIndex
```

Read the memory index, optionally including log entries.

**Parameters:**
- `include_logs`: If `True`, merge pending log entries

**Returns:**
- `MemoryIndex` object

##### add_memory()

```python
add_memory(memory: MemoryEntry, session_id: str) -> None
```

Add a new memory entry via append-log.

##### update_memory()

```python
update_memory(memory_id: str, memory: MemoryEntry, session_id: str) -> None
```

Update an existing memory entry via append-log.

##### delete_memory()

```python
delete_memory(memory_id: str, session_id: str) -> None
```

Delete a memory entry via append-log.

##### rebuild_index()

```python
rebuild_index() -> None
```

Rebuild the index by merging all log entries. Should be called periodically or when log entries exceed threshold.

##### should_rebuild()

```python
should_rebuild(threshold: int = 20) -> bool
```

Check if index should be rebuilt based on log entry count.

**Returns:**
- `True` if rebuild is needed

---

### SkillDetector

Detects patterns that could become skills.

#### Constructor

```python
SkillDetector(memories: list[MemoryEntry])
```

**Parameters:**
- `memories`: List of memory entries to analyze

#### Methods

##### detect_candidates()

```python
detect_candidates(
    min_occurrences: int = 3,
    within_days: int = 90,
) -> list[dict]
```

Detect skill candidates from memory patterns.

**Parameters:**
- `min_occurrences`: Minimum number of similar patterns required
- `within_days`: Look for patterns within this time window

**Returns:**
- List of skill candidate dictionaries

**Example:**
```python
from claude_memory.skills import SkillDetector

# Get all memories
index = manager.global_index.read_index(include_logs=True)
detector = SkillDetector(index.memories)

# Detect candidates
candidates = detector.detect_candidates(
    min_occurrences=3,
    within_days=90
)

for candidate in candidates:
    print(f"Type: {candidate['type']}")
    print(f"Name: {candidate['name']}")
    print(f"Occurrences: {candidate['occurrences']}")
    print(f"Confidence: {candidate['confidence']}")
```

##### generate_report()

```python
generate_report(candidates: list[dict], output_file: Path) -> None
```

Generate a skill candidates report in markdown.

**Parameters:**
- `candidates`: List of candidate dictionaries
- `output_file`: Path to write markdown report

---

## Data Models

All data models are Pydantic models supporting validation and serialization.

### MemoryEntry

Represents a single memory entry.

**Fields:**
```python
id: str                           # Unique identifier
type: MemoryType                  # SESSION, DECISION, IMPLEMENTATION, PATTERN
scope: MemoryScope                # GLOBAL or PROJECT
file: str                         # Relative path to markdown file
title: str                        # Display title
created: datetime                 # Creation timestamp
updated: datetime                 # Last update timestamp
tags: list[str]                   # Searchable tags
summary: str                      # Brief summary
keywords: list[str]               # Extracted keywords
triggers: list[str]               # Lazy-load triggers
related_files: list[str]          # Related memory IDs
files_modified: list[str]         # Code files touched
decisions: list[str]              # Decisions made
promoted: PromotionInfo           # Short-term promotion info
access: AccessInfo                # Usage tracking
scope_decision: ScopeDecision     # How scope was chosen
skill_candidate: SkillCandidate   # Skill extraction info
```

### MemoryIndex

Container for all memory entries.

**Fields:**
```python
version: str                      # Index version
scope: MemoryScope                # GLOBAL or PROJECT
last_updated: datetime            # Last update time
checksum: str                     # Data integrity checksum
memories: list[MemoryEntry]       # All memory entries
stats: dict[str, Any]             # Statistics
```

**Methods:**
```python
find_by_id(memory_id: str) -> MemoryEntry | None
search(
    query: str = "",
    tags: list[str] | None = None,
    memory_type: MemoryType | None = None
) -> list[MemoryEntry]
```

### SessionData

Tracks data during an active session.

**Fields:**
```python
session_id: str                   # Unique session ID
started: datetime                 # Session start time
last_updated: datetime            # Last activity
task: str                         # Current task description
status: SessionStatus             # ACTIVE, ARCHIVED, DISCARDED
files_modified: list[str]         # Files changed
decisions: list[dict]             # Decisions with rationale
problems: list[dict]              # Problems and solutions
notes: list[str]                  # Free-form notes
todos: list[str]                  # TODO items
```

### Enums

#### MemoryScope
```python
class MemoryScope(str, Enum):
    GLOBAL = "global"    # Shared across all projects
    PROJECT = "project"  # Project-specific
```

#### MemoryType
```python
class MemoryType(str, Enum):
    SESSION = "session"              # Session record
    DECISION = "decision"            # Decision record
    IMPLEMENTATION = "implementation" # Implementation details
    PATTERN = "pattern"              # Detected pattern
```

#### SessionStatus
```python
class SessionStatus(str, Enum):
    ACTIVE = "active"        # Currently running
    ARCHIVED = "archived"    # Saved to memory
    DISCARDED = "discarded"  # Discarded without saving
```

### Supporting Models

#### AccessInfo
```python
count: int                        # Number of accesses
last_accessed: datetime | None    # Last access time
first_accessed: datetime | None   # First access time
recent_searches: list[dict]       # Recent search queries (max 10)
```

#### PromotionInfo
```python
is_promoted: bool                 # Currently in short-term
promoted_at: datetime | None      # Promotion timestamp
short_description: str            # Brief description for CLAUDE.md
```

#### ScopeDecision
```python
automatic: bool                   # Auto-determined scope
user_specified: bool              # User manually set scope
reasoning: str                    # Why this scope
generalizability: float           # 0.0 to 1.0
blockers: list[str]               # What prevents global scope
```

#### SkillCandidate
```python
flagged: bool                     # Is a skill candidate
candidate_name: str               # Suggested skill name
confidence: str                   # "high", "medium", "low"
related_memories: list[str]       # Related memory IDs
```

---

## Utility Functions

### Path Utilities

```python
from claude_memory.utils import (
    get_global_claude_dir,
    get_project_claude_dir,
    find_project_root,
    is_project_directory
)

# Get global directory
global_dir = get_global_claude_dir()  # ~/.claude/

# Get project directory (if in a project)
project_dir = get_project_claude_dir()  # /path/to/project/.claude/ or None

# Find project root
root = find_project_root()  # Looks for .git, package.json, etc.

# Check if in project
if is_project_directory(Path.cwd()):
    print("In a project")
```

### ID Generation

```python
from claude_memory.utils import generate_session_id, generate_memory_id

session_id = generate_session_id()
# => "session-20260119-143052-a1b2c3"

memory_id = generate_memory_id("decision")
# => "decision-20260119-143052-a1b2"
```

### JSON Utilities

```python
from claude_memory.utils import read_json_file, write_json_file

# Read JSON
data = read_json_file(Path("config.json"))

# Write JSON (pretty-printed by default)
write_json_file(Path("output.json"), {"key": "value"})
```

### Other Utilities

```python
from claude_memory.utils import (
    calculate_checksum,
    format_datetime,
    parse_datetime
)

# Calculate checksum
checksum = calculate_checksum({"data": "value"})

# Format datetime
formatted = format_datetime(datetime.now())
# => "2026-01-19 14:30:52"

# Parse datetime
dt = parse_datetime("2026-01-19 14:30:52")
```

---

## Advanced Usage

### Custom Memory Types

```python
from claude_memory.models import MemoryEntry, MemoryType, MemoryScope
from datetime import datetime

# Create a custom decision record
decision_memory = MemoryEntry(
    id=generate_memory_id("decision"),
    type=MemoryType.DECISION,
    scope=MemoryScope.GLOBAL,
    file="decisions/api-versioning.md",
    title="API Versioning Strategy",
    created=datetime.now(),
    updated=datetime.now(),
    tags=["architecture", "API", "versioning"],
    summary="Use URL-based versioning for API",
    keywords=["api", "versioning", "rest"],
    triggers=["api", "/v1/", "versioning"]
)

# Add to index
manager.global_index.add_memory(decision_memory, "manual-entry")
```

### Concurrent Session Safety

The system uses append-only logs for concurrent safety:

```python
# Multiple processes can safely work simultaneously
# Process 1
manager1 = MemoryManager()
session1 = manager1.create_session()
session1.update_task("Feature A")

# Process 2 (different process/terminal)
manager2 = MemoryManager()
session2 = manager2.create_session()
session2.update_task("Feature B")

# Both can save without conflicts
manager1.save_session_to_memory(session1, MemoryScope.PROJECT)
manager2.save_session_to_memory(session2, MemoryScope.PROJECT)

# Index will eventually be rebuilt, merging both
manager1.global_index.rebuild_index()
```

### Custom Configuration

```python
from claude_memory.models import Config

# Load and modify config
config_path = get_global_claude_dir() / "config.json"
config_data = read_json_file(config_path)

# Update settings
config_data["memory"]["indexRebuild"]["thresholdEntries"] = 50
config_data["memory"]["refresh"]["intervalMinutes"] = 10

# Save back
write_json_file(config_path, config_data)

# Reload manager
manager = MemoryManager()
```

### Pattern Analysis

```python
from claude_memory.skills import flag_skill_candidates

# Get all memories
index = manager.project_index.read_index(include_logs=True)

# Flag skill candidates
updated_memories = flag_skill_candidates(
    memories=index.memories,
    min_occurrences=3,
    within_days=60
)

# Check which are flagged
for memory in updated_memories:
    if memory.skill_candidate.flagged:
        print(f"Skill candidate: {memory.title}")
        print(f"  Suggested name: {memory.skill_candidate.candidate_name}")
        print(f"  Confidence: {memory.skill_candidate.confidence}")
```

---

## Integration Examples

### Automatic Session Tracking

```python
class AutoTrackingSession:
    """Context manager for automatic session tracking."""

    def __init__(self, manager: MemoryManager, task: str):
        self.manager = manager
        self.task = task
        self.session = None

    def __enter__(self):
        self.session = self.manager.create_session()
        self.session.update_task(self.task)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - save to memory
            self.manager.save_session_to_memory(
                self.session,
                scope=MemoryScope.PROJECT,
                summary=f"Completed: {self.task}"
            )
        else:
            # Error - still save with problem recorded
            self.session.add_problem(
                f"Error: {exc_type.__name__}",
                f"{exc_val}"
            )
            self.manager.save_session_to_memory(
                self.session,
                scope=MemoryScope.PROJECT,
                summary=f"Failed: {self.task}"
            )

# Usage
manager = MemoryManager()
with AutoTrackingSession(manager, "Implement feature X") as session:
    session.add_file_modified("src/feature.py")
    session.add_decision("Use approach A", "Better performance")
    # ... do work ...
```

### Smart Memory Retrieval

```python
def get_relevant_memories(
    manager: MemoryManager,
    current_files: list[str],
    current_task: str
) -> list[MemoryEntry]:
    """Get memories relevant to current work."""

    # Extract keywords from current context
    keywords = current_task.lower().split()
    file_extensions = {f.split('.')[-1] for f in current_files if '.' in f}

    results = []

    # Search by keywords
    for keyword in keywords:
        results.extend(manager.search_memory(keyword))

    # Search by file types
    for ext in file_extensions:
        results.extend(manager.search_memory(f".{ext}"))

    # Deduplicate and sort by access count
    seen = set()
    unique = []
    for memory in results:
        if memory.id not in seen:
            seen.add(memory.id)
            unique.append(memory)

    return sorted(unique, key=lambda m: m.access.count, reverse=True)[:10]
```

### Memory Export/Import

```python
def export_memories(manager: MemoryManager, output_path: Path):
    """Export all memories to a single JSON file."""
    global_index = manager.global_index.read_index(include_logs=True)
    project_index = (
        manager.project_index.read_index(include_logs=True)
        if manager.project_index
        else None
    )

    export_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "global": global_index.model_dump(),
        "project": project_index.model_dump() if project_index else None
    }

    write_json_file(output_path, export_data)

def import_memories(manager: MemoryManager, input_path: Path):
    """Import memories from exported file."""
    data = read_json_file(input_path)

    # Import global memories
    if data.get("global"):
        for memory_data in data["global"]["memories"]:
            memory = MemoryEntry(**memory_data)
            manager.global_index.add_memory(memory, "import")

    # Import project memories
    if data.get("project") and manager.project_index:
        for memory_data in data["project"]["memories"]:
            memory = MemoryEntry(**memory_data)
            manager.project_index.add_memory(memory, "import")

    # Rebuild indices
    manager.global_index.rebuild_index()
    if manager.project_index:
        manager.project_index.rebuild_index()
```

---

## Best Practices

### 1. Always Use Context Managers

```python
# Good
with AutoTrackingSession(manager, "Task") as session:
    session.add_file_modified("file.py")

# Less good - manual save required
session = manager.create_session()
session.update_task("Task")
# ... easy to forget to save
```

### 2. Provide Rich Context

```python
# Good - rich context
session.add_decision(
    decision="Use Redis for caching",
    rationale="Need distributed cache, already have Redis, proven at scale",
    alternatives=["Memcached", "In-memory cache", "Database cache"]
)

# Less good - minimal context
session.add_decision("Use Redis", "It's fast")
```

### 3. Tag Consistently

```python
# Good - consistent, hierarchical tags
tags = ["backend", "api", "authentication", "security"]

# Less good - inconsistent
tags = ["backend stuff", "auth", "Security", "api-endpoint"]
```

### 4. Rebuild Index Periodically

```python
# Check and rebuild if needed
if manager.global_index.should_rebuild():
    manager.global_index.rebuild_index()

if manager.project_index and manager.project_index.should_rebuild():
    manager.project_index.rebuild_index()
```

### 5. Handle Scope Appropriately

```python
# Global scope for reusable patterns
if is_generally_applicable(session):
    scope = MemoryScope.GLOBAL
else:
    scope = MemoryScope.PROJECT
```

---

## Error Handling

```python
from pathlib import Path

try:
    manager = MemoryManager(working_dir=Path("/invalid/path"))
except Exception as e:
    print(f"Failed to initialize: {e}")

try:
    memory = manager.get_memory("invalid-id")
    if memory is None:
        print("Memory not found")
except Exception as e:
    print(f"Error retrieving memory: {e}")
```

---

## Thread Safety

The append-log architecture ensures safe concurrent writes from different **processes**, but individual `MemoryManager` instances are **not thread-safe**. For multi-threaded applications:

```python
# Create separate manager per thread
import threading

def worker():
    manager = MemoryManager()  # Thread-local instance
    session = manager.create_session()
    # ... do work
```

---

## Performance Considerations

- **Index reads** with logs are fast (<100ms for 1000+ memories)
- **Rebuild** happens automatically when log entries exceed threshold (default: 20)
- **Search** is in-memory linear scan (acceptable for thousands of memories)
- **File operations** are minimal (append-only logs, periodic consolidation)

For large-scale deployments (10,000+ memories), consider:
- Lowering rebuild threshold
- Implementing custom search indexing
- Using scheduled rebuilds during off-hours

---

## Version Compatibility

Current API version: **1.0**

All data models use Pydantic for validation and support forward/backward compatibility through optional fields.
