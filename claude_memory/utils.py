"""Utility functions for Claude Memory System."""

import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any


def get_global_claude_dir() -> Path:
    """Get the global .claude directory path."""
    return Path.home() / ".claude"


def find_project_root(start_path: Path | None = None) -> Path | None:
    """
    Find the project root directory by looking for project markers.

    Returns None if not in a project.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Don't consider home directory or root as projects
    home = Path.home()

    while current != current.parent:
        # Stop at home directory
        if current == home:
            return None

        # Check for project markers
        if any(
            (current / marker).exists()
            for marker in [
                ".git",
                ".claude",
                "package.json",
                "pyproject.toml",
                "Cargo.toml",
                "go.mod",
                "pom.xml",
            ]
        ):
            return current

        current = current.parent

    return None


def get_project_claude_dir(start_path: Path | None = None) -> Path | None:
    """Get the project .claude directory path, if in a project."""
    project_root = find_project_root(start_path)
    if project_root:
        return project_root / ".claude"
    return None


def is_project_directory(path: Path) -> bool:
    """Check if a directory appears to be a project."""
    return find_project_root(path) is not None


def generate_session_id() -> str:
    """Generate a unique session ID."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = secrets.token_hex(3)
    return f"session-{timestamp}-{random_suffix}"


def generate_memory_id(prefix: str = "memory") -> str:
    """Generate a unique memory ID."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = secrets.token_hex(2)
    return f"{prefix}-{timestamp}-{random_suffix}"


def calculate_checksum(data: dict[str, Any]) -> str:
    """Calculate a checksum for data."""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def read_json_file(path: Path) -> dict[str, Any]:
    """Read a JSON file."""
    if not path.exists():
        return {}

    with open(path) as f:
        return json.load(f)


def write_json_file(path: Path, data: dict[str, Any], pretty: bool = True) -> None:
    """Write a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        if pretty:
            json.dump(data, f, indent=2, default=str)
        else:
            json.dump(data, f, default=str)


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def get_relative_path(path: Path, base: Path) -> str:
    """Get relative path as string."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime(s: str) -> datetime:
    """Parse datetime string."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # Try common formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise
