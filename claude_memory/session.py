"""Session tracking for active work."""

from datetime import datetime
from pathlib import Path

from claude_memory.models import SessionData, SessionStatus
from claude_memory.utils import (
    generate_session_id,
    read_json_file,
    write_json_file,
)


class SessionTracker:
    """Tracks an active Claude Code session."""

    def __init__(self, claude_dir: Path, session_id: str | None = None):
        self.claude_dir = claude_dir
        self.session_id = session_id or generate_session_id()
        self.active_dir = claude_dir / "sessions" / "active"
        self.archived_dir = claude_dir / "sessions" / "archived"
        self.session_file = self.active_dir / f"{self.session_id}.json"

        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.archived_dir.mkdir(parents=True, exist_ok=True)

        # Load or create session data
        if self.session_file.exists():
            data = read_json_file(self.session_file)
            self.data = SessionData(**data)
        else:
            self.data = SessionData(
                session_id=self.session_id,
                started=datetime.now(),
                last_updated=datetime.now(),
            )
            self.save()

    def update_task(self, task: str) -> None:
        """Update the current task description."""
        self.data.task = task
        self._update_timestamp()
        self.save()

    def add_file_modified(self, file_path: str) -> None:
        """Track a file that was modified."""
        if file_path not in self.data.files_modified:
            self.data.files_modified.append(file_path)
            self._update_timestamp()
            self.save()

    def add_decision(self, decision: str, rationale: str, alternatives: list[str] | None = None) -> None:
        """Track a decision made during the session."""
        self.data.decisions.append(
            {
                "decision": decision,
                "rationale": rationale,
                "alternatives": alternatives or [],
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._update_timestamp()
        self.save()

    def add_problem(self, problem: str, solution: str | None = None) -> None:
        """Track a problem encountered and its solution."""
        self.data.problems.append(
            {
                "problem": problem,
                "solution": solution,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._update_timestamp()
        self.save()

    def add_note(self, note: str) -> None:
        """Add a note to the session."""
        self.data.notes.append(note)
        self._update_timestamp()
        self.save()

    def add_todo(self, todo: str) -> None:
        """Add a TODO item."""
        if todo not in self.data.todos:
            self.data.todos.append(todo)
            self._update_timestamp()
            self.save()

    def remove_todo(self, todo: str) -> None:
        """Remove a completed TODO item."""
        if todo in self.data.todos:
            self.data.todos.remove(todo)
            self._update_timestamp()
            self.save()

    def save(self) -> None:
        """Save session data to file."""
        write_json_file(self.session_file, self.data.model_dump())

    def archive(self, archive_name: str | None = None) -> Path:
        """
        Archive this session.

        Args:
            archive_name: Optional custom archive filename

        Returns:
            Path to archived file
        """
        self.data.status = SessionStatus.ARCHIVED
        self.save()

        # Generate archive filename
        if not archive_name:
            date_str = self.data.started.strftime("%Y-%m-%d")
            task_slug = (
                self.data.task[:50]
                .lower()
                .replace(" ", "-")
                .replace("/", "-")
                .replace("_", "-")
            )
            archive_name = f"{date_str}-{task_slug}.json"

        archive_path = self.archived_dir / archive_name

        # Move session file to archive
        self.session_file.rename(archive_path)

        return archive_path

    def discard(self) -> None:
        """Discard this session without archiving."""
        self.data.status = SessionStatus.DISCARDED
        if self.session_file.exists():
            self.session_file.unlink()

    def _update_timestamp(self) -> None:
        """Update the last_updated timestamp."""
        self.data.last_updated = datetime.now()

    @classmethod
    def list_active_sessions(cls, claude_dir: Path) -> list[SessionData]:
        """List all active sessions in a .claude directory."""
        active_dir = claude_dir / "sessions" / "active"
        if not active_dir.exists():
            return []

        sessions = []
        for session_file in active_dir.glob("*.json"):
            data = read_json_file(session_file)
            if data:
                try:
                    session = SessionData(**data)
                    sessions.append(session)
                except Exception:
                    pass

        return sessions

    @classmethod
    def cleanup_stale_sessions(
        cls, claude_dir: Path, hours_threshold: int = 24
    ) -> list[str]:
        """
        Find stale sessions (no activity for hours_threshold).

        Args:
            claude_dir: Path to .claude directory
            hours_threshold: Hours of inactivity to consider stale

        Returns:
            List of stale session IDs
        """
        sessions = cls.list_active_sessions(claude_dir)
        stale = []
        now = datetime.now()

        for session in sessions:
            hours_since_update = (now - session.last_updated).total_seconds() / 3600
            if hours_since_update >= hours_threshold:
                stale.append(session.session_id)

        return stale

    def to_markdown(self) -> str:
        """Convert session data to markdown format."""
        md = f"""# Session: {self.session_id}
**Started**: {self.data.started.strftime('%Y-%m-%d %H:%M:%S')}
**Last Updated**: {self.data.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
**Task**: {self.data.task or 'Not specified'}
**Status**: {self.data.status.value}

## Files Modified
"""
        if self.data.files_modified:
            for file in self.data.files_modified:
                md += f"- {file}\n"
        else:
            md += "- None\n"

        md += "\n## Decisions Made\n"
        if self.data.decisions:
            for dec in self.data.decisions:
                md += f"\n### {dec['decision']}\n"
                md += f"**Rationale**: {dec['rationale']}\n"
                if dec.get("alternatives"):
                    md += "**Alternatives considered**:\n"
                    for alt in dec["alternatives"]:
                        md += f"- {alt}\n"
        else:
            md += "- None\n"

        md += "\n## Problems Encountered\n"
        if self.data.problems:
            for prob in self.data.problems:
                md += f"\n### {prob['problem']}\n"
                if prob.get("solution"):
                    md += f"**Solution**: {prob['solution']}\n"
        else:
            md += "- None\n"

        md += "\n## Notes\n"
        if self.data.notes:
            for note in self.data.notes:
                md += f"- {note}\n"
        else:
            md += "- None\n"

        md += "\n## TODOs\n"
        if self.data.todos:
            for todo in self.data.todos:
                md += f"- [ ] {todo}\n"
        else:
            md += "- None\n"

        return md
