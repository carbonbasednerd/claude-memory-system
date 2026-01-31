"""Memory manifest system for lightweight context usage.

The manifest provides a lightweight index of all memories without loading
their full content. This keeps context usage minimal while maintaining
awareness of what memories exist.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from claude_memory.models import MemoryIndex, MemoryEntry, MemoryScope


class MemoryManifest:
    """Lightweight index of memory entries."""

    def __init__(self, claude_dir: Path, scope: MemoryScope):
        """Initialize manifest for a given scope.

        Args:
            claude_dir: Path to .claude directory
            scope: Memory scope (global or project)
        """
        self.claude_dir = claude_dir
        self.scope = scope
        self.manifest_file = claude_dir / "memory" / "manifest.json"

    def generate_from_index(self, index: MemoryIndex) -> dict:
        """Generate manifest from memory index.

        Args:
            index: MemoryIndex to convert

        Returns:
            Manifest dictionary
        """
        entries = []

        for memory in index.memories:
            # Estimate token count (rough approximation: 1 token ≈ 4 chars)
            file_path = self.claude_dir / "memory" / memory.file
            size_tokens = 0
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    size_tokens = len(content) // 4
                except Exception:
                    size_tokens = 0

            entries.append({
                "id": memory.id,
                "title": memory.title,
                "type": memory.type.value,
                "scope": memory.scope.value,
                "created": memory.created.isoformat() if memory.created else None,
                "tags": memory.tags,
                "file": memory.file,
                "size_tokens": size_tokens,
                "access_count": memory.access.count,
                "last_accessed": memory.access.last_accessed.isoformat() if memory.access.last_accessed else None,
                "summary": memory.summary[:200] if memory.summary else "",  # Truncate
            })

        manifest = {
            "version": "1.0",
            "scope": self.scope.value,
            "last_updated": datetime.now().isoformat(),
            "index": entries,
            "stats": {
                "total_memories": len(entries),
                "total_tokens": sum(e["size_tokens"] for e in entries),
                "by_type": index.stats.get("by_type", {}),
            }
        }

        return manifest

    def save(self, manifest: dict):
        """Save manifest to file.

        Args:
            manifest: Manifest dictionary to save
        """
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

    def load(self) -> Optional[dict]:
        """Load manifest from file.

        Returns:
            Manifest dictionary or None if not found
        """
        if not self.manifest_file.exists():
            return None

        try:
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def rebuild(self, index: MemoryIndex):
        """Rebuild manifest from index.

        Args:
            index: MemoryIndex to rebuild from
        """
        manifest = self.generate_from_index(index)
        self.save(manifest)

    def get_memory_info(self, memory_id: str) -> Optional[dict]:
        """Get memory info from manifest without loading full content.

        Args:
            memory_id: Memory ID to look up

        Returns:
            Memory info dict or None if not found
        """
        manifest = self.load()
        if not manifest:
            return None

        for entry in manifest["index"]:
            if entry["id"] == memory_id:
                return entry

        return None

    def search(self, query: str = "", tags: list[str] = None) -> list[dict]:
        """Search manifest for memories.

        Args:
            query: Search query (matches title, summary)
            tags: List of tags to filter by

        Returns:
            List of matching memory info dicts
        """
        manifest = self.load()
        if not manifest:
            return []

        results = []
        query_lower = query.lower()
        tags = tags or []

        for entry in manifest["index"]:
            # Match query
            if query:
                if query_lower not in entry["title"].lower() and \
                   query_lower not in entry.get("summary", "").lower():
                    continue

            # Match tags
            if tags:
                if not any(tag in entry["tags"] for tag in tags):
                    continue

            results.append(entry)

        return results

    def estimate_tokens(self) -> int:
        """Estimate token count of manifest file itself.

        Returns:
            Estimated tokens (rough approximation)
        """
        if not self.manifest_file.exists():
            return 0

        try:
            content = self.manifest_file.read_text()
            return len(content) // 4  # Rough: 1 token ≈ 4 chars
        except Exception:
            return 0
