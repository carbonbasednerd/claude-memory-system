"""Core memory management for Claude Memory System."""

from datetime import datetime
from pathlib import Path

from claude_memory.index import IndexManager
from claude_memory.models import (
    AccessInfo,
    Config,
    MemoryEntry,
    MemoryScope,
    MemoryType,
    PromotionInfo,
    ScopeDecision,
)
from claude_memory.session import SessionTracker
from claude_memory.utils import (
    ensure_directory,
    generate_memory_id,
    get_global_claude_dir,
    get_project_claude_dir,
    read_json_file,
    write_json_file,
)


class MemoryManager:
    """Main interface for Claude Memory System."""

    def __init__(self, working_dir: Path | None = None):
        """
        Initialize memory manager.

        Args:
            working_dir: Current working directory (defaults to cwd)
        """
        self.working_dir = working_dir or Path.cwd()

        # Get global and project directories
        self.global_dir = get_global_claude_dir()
        self.project_dir = get_project_claude_dir(self.working_dir)

        # Initialize if needed
        self._ensure_initialized()

        # Create index managers
        self.global_index = IndexManager(self.global_dir, MemoryScope.GLOBAL)
        self.project_index = (
            IndexManager(self.project_dir, MemoryScope.PROJECT)
            if self.project_dir
            else None
        )

        # Load configuration
        self.config = self._load_config()

    def _ensure_initialized(self) -> None:
        """Ensure memory system is initialized."""
        # Always initialize global
        if not self.global_dir.exists():
            self._initialize_claude_dir(self.global_dir, MemoryScope.GLOBAL)

        # Ask about project initialization if needed
        if self.project_dir and not self.project_dir.exists():
            # For now, auto-initialize project (CLI can handle prompting)
            self._initialize_claude_dir(self.project_dir, MemoryScope.PROJECT)

    def _initialize_claude_dir(self, claude_dir: Path, scope: MemoryScope) -> None:
        """Initialize a .claude directory structure."""
        # Create directory structure
        (claude_dir / "memory" / "index-log").mkdir(parents=True, exist_ok=True)
        (claude_dir / "memory" / "sessions" / "active").mkdir(parents=True, exist_ok=True)
        (claude_dir / "memory" / "sessions" / "archived").mkdir(parents=True, exist_ok=True)
        (claude_dir / "memory" / "decisions").mkdir(parents=True, exist_ok=True)
        (claude_dir / "memory" / "implementations").mkdir(parents=True, exist_ok=True)
        (claude_dir / "sessions" / "active").mkdir(parents=True, exist_ok=True)
        (claude_dir / "sessions" / "archived").mkdir(parents=True, exist_ok=True)
        (claude_dir / "skills").mkdir(parents=True, exist_ok=True)

        # Create CLAUDE.md
        claude_md = claude_dir / "CLAUDE.md"
        if not claude_md.exists():
            template = self._get_claude_md_template(scope)
            claude_md.write_text(template)

        # Create config.json
        config_file = claude_dir / "config.json"
        if not config_file.exists():
            config = Config()
            write_json_file(config_file, config.model_dump())

        # Initialize index
        index_manager = IndexManager(claude_dir, scope)
        index_manager.initialize()

        # Create skills index
        skills_index = claude_dir / "skills" / "index.json"
        if not skills_index.exists():
            write_json_file(
                skills_index,
                {
                    "version": "1.0",
                    "skills": [],
                    "last_updated": datetime.now().isoformat(),
                },
            )

    def _get_claude_md_template(self, scope: MemoryScope) -> str:
        """Get template for CLAUDE.md."""
        if scope == MemoryScope.GLOBAL:
            return """# Global User Preferences

## Coding Style
(Add your global coding preferences here)

## Memory Pointers
(Memory pointers will be added here as you work)
"""
        else:
            return """# Project Memory

## Project Context
(Project-specific context will be added here)

## Memory Pointers
(Project memory pointers will be added here)
"""

    def _load_config(self) -> Config:
        """Load configuration (project takes precedence over global)."""
        # Load global config
        global_config_path = self.global_dir / "config.json"
        config_data = read_json_file(global_config_path)

        # Override with project config if exists
        if self.project_dir:
            project_config_path = self.project_dir / "config.json"
            if project_config_path.exists():
                project_config_data = read_json_file(project_config_path)
                # Merge configs (project overrides global)
                config_data.update(project_config_data)

        return Config(**config_data) if config_data else Config()

    def create_session(self, session_id: str | None = None) -> SessionTracker:
        """
        Create a new session tracker.

        Args:
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            SessionTracker instance
        """
        # Use project directory if available, otherwise global
        claude_dir = self.project_dir if self.project_dir else self.global_dir
        return SessionTracker(claude_dir, session_id)

    def save_session_to_memory(
        self,
        session: SessionTracker,
        scope: MemoryScope,
        memory_type: MemoryType = MemoryType.SESSION,
        tags: list[str] | None = None,
        summary: str | None = None,
    ) -> MemoryEntry:
        """
        Save a session to long-term memory.

        Args:
            session: The session to save
            scope: Global or project scope
            memory_type: Type of memory entry
            tags: Tags for the memory
            summary: Summary of the session

        Returns:
            Created memory entry
        """
        # Generate memory ID
        memory_id = generate_memory_id("session")

        # Create memory file
        date_str = session.data.started.strftime("%Y-%m-%d")
        task_slug = (
            session.data.task[:50]
            .lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace("_", "-")
        )
        filename = f"{date_str}-{task_slug}.md"

        # Choose target directory
        target_dir = (
            self.global_dir if scope == MemoryScope.GLOBAL else self.project_dir
        )
        if not target_dir:
            raise ValueError("No project directory available for project scope")

        memory_file = target_dir / "memory" / "sessions" / filename
        memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Write markdown file
        markdown_content = session.to_markdown()
        if summary:
            markdown_content = f"## Summary\n{summary}\n\n{markdown_content}"

        memory_file.write_text(markdown_content)

        # Create memory entry
        memory_entry = MemoryEntry(
            id=memory_id,
            type=memory_type,
            scope=scope,
            file=f"sessions/{filename}",
            title=session.data.task or "Untitled Session",
            created=session.data.started,
            updated=datetime.now(),
            tags=tags or [],
            summary=summary or "",
            keywords=self._extract_keywords(session),
            triggers=self._extract_triggers(session, tags or []),
            files_modified=session.data.files_modified,
            decisions=[d["decision"] for d in session.data.decisions],
            access=AccessInfo(),
        )

        # Add to index
        index_manager = (
            self.global_index if scope == MemoryScope.GLOBAL else self.project_index
        )
        if index_manager:
            index_manager.add_memory(memory_entry, session.session_id)

            # Check if rebuild needed
            if index_manager.should_rebuild(
                self.config.memory["indexRebuild"]["thresholdEntries"]
            ):
                index_manager.rebuild_index()

        return memory_entry

    def search_memory(
        self,
        query: str = "",
        tags: list[str] | None = None,
        memory_type: MemoryType | None = None,
        scope: MemoryScope | None = None,
    ) -> list[MemoryEntry]:
        """
        Search memory across global and/or project.

        Args:
            query: Search query
            tags: Filter by tags
            memory_type: Filter by type
            scope: Search only specific scope (None = both)

        Returns:
            List of matching memory entries
        """
        results = []

        # Search global
        if scope is None or scope == MemoryScope.GLOBAL:
            global_index = self.global_index.read_index(include_logs=True)
            results.extend(global_index.search(query, tags, memory_type))

        # Search project
        if (scope is None or scope == MemoryScope.PROJECT) and self.project_index:
            project_index = self.project_index.read_index(include_logs=True)
            results.extend(project_index.search(query, tags, memory_type))

        # Remove duplicates and sort
        seen = set()
        unique_results = []
        for entry in results:
            if entry.id not in seen:
                seen.add(entry.id)
                unique_results.append(entry)

        return unique_results

    def get_memory(self, memory_id: str) -> MemoryEntry | None:
        """Get a specific memory entry by ID."""
        # Try global first
        global_index = self.global_index.read_index(include_logs=True)
        memory = global_index.find_by_id(memory_id)
        if memory:
            return memory

        # Try project
        if self.project_index:
            project_index = self.project_index.read_index(include_logs=True)
            memory = project_index.find_by_id(memory_id)
            if memory:
                return memory

        return None

    def record_memory_access(
        self, memory_id: str, query: str = ""
    ) -> None:
        """Record that a memory was accessed."""
        memory = self.get_memory(memory_id)
        if not memory:
            return

        # Update access info
        now = datetime.now()
        if not memory.access.first_accessed:
            memory.access.first_accessed = now
        memory.access.last_accessed = now
        memory.access.count += 1

        if query:
            memory.access.recent_searches.append(
                {"query": query, "timestamp": now.isoformat()}
            )
            # Keep only last 10
            memory.access.recent_searches = memory.access.recent_searches[-10:]

        # Update in index
        index_manager = (
            self.global_index if memory.scope == MemoryScope.GLOBAL else self.project_index
        )
        if index_manager:
            index_manager.update_memory(memory_id, memory, "access-tracker")

    def _extract_keywords(self, session: SessionTracker) -> list[str]:
        """Extract keywords from session data."""
        keywords = []

        # Extract from task
        if session.data.task:
            keywords.extend(session.data.task.lower().split())

        # Extract from decisions
        for decision in session.data.decisions:
            keywords.extend(decision["decision"].lower().split())

        # Extract from file paths (languages, frameworks)
        for file_path in session.data.files_modified:
            # Get file extension
            if "." in file_path:
                ext = file_path.rsplit(".", 1)[-1]
                keywords.append(ext)

            # Get directory names (might indicate modules)
            parts = file_path.split("/")
            keywords.extend(parts[:-1])

        # Deduplicate and filter
        keywords = list(set(k for k in keywords if len(k) > 2))

        return keywords[:20]  # Limit to 20 keywords

    def _extract_triggers(self, session: SessionTracker, tags: list[str]) -> list[str]:
        """Extract triggers for lazy loading."""
        triggers = list(tags)  # Start with tags

        # Add file extensions
        for file_path in session.data.files_modified:
            if "." in file_path:
                ext = file_path.rsplit(".", 1)[-1]
                triggers.append(f".{ext}")

        # Add common framework/language keywords from task
        task_lower = session.data.task.lower() if session.data.task else ""
        for keyword in [
            "python",
            "javascript",
            "typescript",
            "react",
            "vue",
            "django",
            "flask",
            "fastapi",
            "auth",
            "database",
            "api",
        ]:
            if keyword in task_lower:
                triggers.append(keyword)

        return list(set(triggers))

    def update_current_work(self) -> None:
        """
        Update CLAUDE.md with current work section.

        Shows active sessions from project (if available), else global.
        """
        # Determine which sessions to show and which CLAUDE.md to update
        if self.project_dir and self.project_dir.exists():
            # Check project sessions first
            sessions = SessionTracker.list_active_sessions(self.project_dir)
            claude_md_path = self.project_dir / "CLAUDE.md"
            scope_label = "Project"
        else:
            sessions = []
            claude_md_path = None
            scope_label = "Global"

        # Fall back to global if no project sessions
        if not sessions:
            sessions = SessionTracker.list_active_sessions(self.global_dir)
            claude_md_path = self.global_dir / "CLAUDE.md"
            scope_label = "Global"

        if not claude_md_path or not claude_md_path.exists():
            return

        # Read current CLAUDE.md
        content = claude_md_path.read_text()

        # Generate current work section
        current_work = self._generate_current_work_section(sessions, scope_label)

        # Replace or insert current work section
        if "## Current Work" in content:
            # Replace existing section
            import re
            # Match from ## Current Work (with optional scope label) to the next ## heading or end
            pattern = r"## Current Work.*?\n.*?(?=\n## |\Z)"
            content = re.sub(pattern, current_work.rstrip(), content, flags=re.DOTALL)
        else:
            # Insert after # Project Memory or # Global User Preferences
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    insert_pos = i + 1
                    break

            lines.insert(insert_pos, "")
            lines.insert(insert_pos + 1, current_work)
            content = "\n".join(lines)

        # Write back
        claude_md_path.write_text(content)

    def _generate_current_work_section(
        self, sessions: list, scope_label: str
    ) -> str:
        """Generate the Current Work markdown section."""
        if not sessions:
            return """## Current Work

(No active sessions)
"""

        md = f"## Current Work ({scope_label})\n\n"

        for session in sessions:
            md += f"### {session.task or 'Untitled Session'}\n"
            md += f"**Session ID**: {session.session_id}\n"
            md += f"**Started**: {session.started.strftime('%Y-%m-%d %H:%M')}\n"
            md += f"**Last Updated**: {session.last_updated.strftime('%Y-%m-%d %H:%M')}\n"

            if session.files_modified:
                md += "\n**Files Modified**:\n"
                for file in session.files_modified[:10]:  # Limit to 10
                    md += f"  - {file}\n"
                if len(session.files_modified) > 10:
                    md += f"  - ... and {len(session.files_modified) - 10} more\n"

            if session.todos:
                md += "\n**TODOs**:\n"
                for todo in session.todos[:10]:  # Limit to 10
                    md += f"  - [ ] {todo}\n"
                if len(session.todos) > 10:
                    md += f"  - ... and {len(session.todos) - 10} more\n"

            md += "\n---\n\n"

        return md
