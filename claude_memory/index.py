"""Index management with append-log for concurrent writes."""

from datetime import datetime
from pathlib import Path

from claude_memory.models import (
    IndexLogEntry,
    MemoryEntry,
    MemoryIndex,
    MemoryScope,
)
from claude_memory.utils import (
    calculate_checksum,
    generate_memory_id,
    read_json_file,
    write_json_file,
)


class IndexManager:
    """Manages memory index with append-log for concurrent safety."""

    def __init__(self, claude_dir: Path, scope: MemoryScope):
        self.claude_dir = claude_dir
        self.scope = scope
        self.index_path = claude_dir / "memory" / "index.json"
        self.log_dir = claude_dir / "memory" / "index-log"

    def initialize(self) -> None:
        """Initialize index structure."""
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            # Create empty index
            index = MemoryIndex(
                scope=self.scope,
                last_updated=datetime.now(),
                memories=[],
            )
            self._write_index(index)

    def read_index(self, include_logs: bool = True) -> MemoryIndex:
        """
        Read the memory index, optionally including log entries.

        Args:
            include_logs: If True, merge log entries into the index
        """
        # Read base index
        data = read_json_file(self.index_path)
        if not data:
            # Return empty index
            return MemoryIndex(
                scope=self.scope,
                last_updated=datetime.now(),
                memories=[],
            )

        index = MemoryIndex(**data)

        # Merge log entries if requested
        if include_logs:
            log_entries = self._read_log_entries()
            index = self._merge_log_entries(index, log_entries)

        return index

    def add_memory(self, memory: MemoryEntry, session_id: str) -> None:
        """
        Add a new memory entry via append-log.

        Args:
            memory: The memory entry to add
            session_id: ID of the session adding this memory
        """
        log_entry = IndexLogEntry(
            operation="add",
            timestamp=datetime.now(),
            session_id=session_id,
            memory=memory,
        )
        self._append_log_entry(log_entry)

    def update_memory(self, memory_id: str, memory: MemoryEntry, session_id: str) -> None:
        """
        Update an existing memory entry via append-log.

        Args:
            memory_id: ID of the memory to update
            memory: Updated memory data
            session_id: ID of the session updating this memory
        """
        log_entry = IndexLogEntry(
            operation="update",
            timestamp=datetime.now(),
            session_id=session_id,
            memory=memory,
            memory_id=memory_id,
        )
        self._append_log_entry(log_entry)

    def delete_memory(self, memory_id: str, session_id: str) -> None:
        """
        Delete a memory entry via append-log.

        Args:
            memory_id: ID of the memory to delete
            session_id: ID of the session deleting this memory
        """
        log_entry = IndexLogEntry(
            operation="delete",
            timestamp=datetime.now(),
            session_id=session_id,
            memory_id=memory_id,
        )
        self._append_log_entry(log_entry)

    def rebuild_index(self) -> None:
        """
        Rebuild the index by merging all log entries.

        This should be called periodically or when log entries exceed threshold.
        """
        # Read current index and all logs
        index = self.read_index(include_logs=True)

        # Update metadata
        index.last_updated = datetime.now()
        index.checksum = calculate_checksum(index.model_dump())

        # Calculate stats
        index.stats = self._calculate_stats(index)

        # Write merged index
        self._write_index(index)

        # Clear log entries
        self._clear_log_entries()

    def should_rebuild(self, threshold: int = 20) -> bool:
        """
        Check if index should be rebuilt based on log entry count.

        Args:
            threshold: Number of log entries that triggers rebuild

        Returns:
            True if rebuild is needed
        """
        log_files = list(self.log_dir.glob("*.json"))
        return len(log_files) >= threshold

    def _read_log_entries(self) -> list[IndexLogEntry]:
        """Read all log entries."""
        entries = []
        log_files = sorted(self.log_dir.glob("*.json"))

        for log_file in log_files:
            data = read_json_file(log_file)
            if data:
                try:
                    entry = IndexLogEntry(**data)
                    entries.append(entry)
                except Exception:
                    # Skip invalid log entries
                    pass

        return entries

    def _append_log_entry(self, entry: IndexLogEntry) -> None:
        """Append a log entry to a new file."""
        # Generate unique log file name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        log_file = self.log_dir / f"{timestamp}-{entry.session_id}.json"

        # Write log entry
        write_json_file(log_file, entry.model_dump())

    def _merge_log_entries(
        self, index: MemoryIndex, log_entries: list[IndexLogEntry]
    ) -> MemoryIndex:
        """
        Merge log entries into the index.

        Args:
            index: Base index
            log_entries: List of log entries to merge

        Returns:
            Updated index
        """
        # Create a dict for fast lookup
        memories_dict = {m.id: m for m in index.memories}

        # Apply log entries in order
        for entry in log_entries:
            if entry.operation == "add" and entry.memory:
                memories_dict[entry.memory.id] = entry.memory

            elif entry.operation == "update" and entry.memory:
                if entry.memory.id in memories_dict:
                    memories_dict[entry.memory.id] = entry.memory

            elif entry.operation == "delete" and entry.memory_id:
                memories_dict.pop(entry.memory_id, None)

        # Update index
        index.memories = list(memories_dict.values())
        index.last_updated = datetime.now()

        return index

    def _write_index(self, index: MemoryIndex) -> None:
        """Write index to file."""
        write_json_file(self.index_path, index.model_dump())

    def _clear_log_entries(self) -> None:
        """Clear all log entry files."""
        for log_file in self.log_dir.glob("*.json"):
            log_file.unlink()

    def _calculate_stats(self, index: MemoryIndex) -> dict:
        """Calculate statistics for the index."""
        stats = {
            "total_memories": len(index.memories),
            "total_accesses": sum(m.access.count for m in index.memories),
            "by_type": {},
            "most_accessed": [],
            "never_accessed": [],
            "oldest_unaccessed": None,
        }

        # Count by type
        for memory in index.memories:
            type_name = memory.type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

        # Sort by access count
        sorted_by_access = sorted(
            index.memories, key=lambda m: m.access.count, reverse=True
        )

        # Most accessed (top 5)
        stats["most_accessed"] = [m.id for m in sorted_by_access[:5] if m.access.count > 0]

        # Never accessed
        stats["never_accessed"] = [m.id for m in index.memories if m.access.count == 0]

        # Oldest unaccessed
        unaccessed = [m for m in index.memories if m.access.count == 0]
        if unaccessed:
            oldest = min(unaccessed, key=lambda m: m.created)
            stats["oldest_unaccessed"] = oldest.id

        return stats
