"""Data models for Claude Memory System."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class MemoryScope(str, Enum):
    """Scope of memory: global or project."""

    GLOBAL = "global"
    PROJECT = "project"


class MemoryType(str, Enum):
    """Type of memory entry."""

    SESSION = "session"
    DECISION = "decision"
    IMPLEMENTATION = "implementation"
    PATTERN = "pattern"


class SessionStatus(str, Enum):
    """Status of a session."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DISCARDED = "discarded"


class AccessInfo(BaseModel):
    """Tracking information for memory access."""

    count: int = 0
    last_accessed: datetime | None = None
    first_accessed: datetime | None = None
    recent_searches: list[dict[str, Any]] = Field(default_factory=list, max_length=10)


class PromotionInfo(BaseModel):
    """Information about memory promotion to short-term."""

    is_promoted: bool = False
    promoted_at: datetime | None = None
    short_description: str = ""


class ScopeDecision(BaseModel):
    """Information about how scope was decided."""

    automatic: bool = True
    user_specified: bool = False
    reasoning: str = ""
    generalizability: float = 0.0  # 0.0 to 1.0
    blockers: list[str] = Field(default_factory=list)


class SkillCandidate(BaseModel):
    """Information about skill extraction candidacy."""

    flagged: bool = False
    candidate_name: str = ""
    confidence: str = ""  # "high", "medium", "low"
    related_memories: list[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    """A single memory entry in the index."""

    id: str
    type: MemoryType
    scope: MemoryScope
    file: str  # Relative path from .claude/memory/
    title: str
    created: datetime
    updated: datetime
    tags: list[str] = Field(default_factory=list)
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    related_files: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    promoted: PromotionInfo = Field(default_factory=PromotionInfo)
    access: AccessInfo = Field(default_factory=AccessInfo)
    scope_decision: ScopeDecision = Field(default_factory=ScopeDecision)
    skill_candidate: SkillCandidate = Field(default_factory=SkillCandidate)


class MemoryIndex(BaseModel):
    """The memory index containing all memory entries."""

    version: str = "1.0"
    scope: MemoryScope
    last_updated: datetime
    checksum: str = ""
    memories: list[MemoryEntry] = Field(default_factory=list)
    stats: dict[str, Any] = Field(default_factory=dict)

    def find_by_id(self, memory_id: str) -> MemoryEntry | None:
        """Find a memory entry by ID."""
        for entry in self.memories:
            if entry.id == memory_id:
                return entry
        return None

    def search(
        self,
        query: str = "",
        tags: list[str] | None = None,
        memory_type: MemoryType | None = None,
    ) -> list[MemoryEntry]:
        """Search for memory entries."""
        results = []
        query_lower = query.lower()
        tags = tags or []

        for entry in self.memories:
            # Match query in title, summary, keywords, triggers
            if query:
                if (
                    query_lower in entry.title.lower()
                    or query_lower in entry.summary.lower()
                    or any(query_lower in kw.lower() for kw in entry.keywords)
                    or any(query_lower in t.lower() for t in entry.triggers)
                ):
                    pass
                else:
                    continue

            # Match tags
            if tags and not any(tag in entry.tags for tag in tags):
                continue

            # Match type
            if memory_type and entry.type != memory_type:
                continue

            results.append(entry)

        # Sort by last accessed (most recent first), then by created
        results.sort(
            key=lambda e: (
                e.access.last_accessed or datetime.min,
                e.created,
            ),
            reverse=True,
        )

        return results


class IndexLogEntry(BaseModel):
    """A single entry in the append-only index log."""

    operation: str  # "add", "update", "delete"
    timestamp: datetime
    session_id: str
    memory: MemoryEntry | None = None
    memory_id: str | None = None  # For updates/deletes


class SessionData(BaseModel):
    """Data tracked during an active session."""

    session_id: str
    started: datetime
    last_updated: datetime
    task: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    files_modified: list[str] = Field(default_factory=list)
    decisions: list[dict[str, Any]] = Field(default_factory=list)
    problems: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    todos: list[str] = Field(default_factory=list)


class Config(BaseModel):
    """Configuration for memory system."""

    memory: dict[str, Any] = Field(
        default_factory=lambda: {
            "refresh": {
                "strategy": "periodic",
                "intervalMinutes": 5,
                "onSearch": True,
                "watchFiles": False,
            },
            "visibility": {"showGlobalSessions": False, "showProjectSessions": True},
            "scopeDecisions": {
                "autoSuggest": True,
                "requireConfirmation": True,
                "analysisFrequency": "weekly",
                "promotionThreshold": {
                    "minProjectUses": 3,
                    "minCrossProjectUses": 2,
                    "generalizabilityScore": 0.7,
                },
            },
            "indexRebuild": {
                "strategy": "threshold",
                "thresholdEntries": 20,
                "periodicSchedule": "daily",
            },
        }
    )
