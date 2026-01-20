# Contributing to Claude Memory System

Thank you for your interest in contributing to the Claude Memory System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

Be respectful, constructive, and collaborative. We're building tools to help developers, so let's help each other.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of the memory system architecture (see `docs/ARCHITECTURE.md`)

### Ways to Contribute

1. **Bug Reports** - Found a bug? Open an issue with reproduction steps
2. **Feature Requests** - Have an idea? Open an issue to discuss it
3. **Code Contributions** - Fix bugs, implement features, improve performance
4. **Documentation** - Improve docs, add examples, fix typos
5. **Testing** - Add tests, improve test coverage
6. **Scripts** - Enhance helper scripts in `scripts/`

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/jay-i.git
cd jay-i
```

### 2. Create Virtual Environment

```bash
# Create virtualenv
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Development Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or if pyproject.toml doesn't have [dev] yet:
pip install -e .
pip install pytest ruff black mypy
```

### 4. Verify Installation

```bash
# Run tests
pytest

# Check code style
ruff check .

# Verify CLI works
claude-memory --help
```

## Project Structure

```
jay-i/
├── claude_memory/          # Main package
│   ├── __init__.py         # Package exports
│   ├── cli.py              # Command-line interface
│   ├── memory.py           # MemoryManager class
│   ├── session.py          # SessionTracker class
│   ├── index.py            # IndexManager class
│   ├── skills.py           # SkillDetector class
│   ├── models.py           # Pydantic data models
│   └── utils.py            # Utility functions
├── scripts/                # Helper bash scripts
├── docs/                   # Documentation
│   ├── API.md              # API reference
│   ├── ARCHITECTURE.md     # System architecture
│   ├── USAGE.md            # User guide
│   └── EXAMPLES.md         # Usage examples
├── tests/                  # Test suite (create this)
├── pyproject.toml          # Project metadata and dependencies
└── README.md               # Project overview
```

### Key Modules

- **memory.py**: Core memory management, orchestrates sessions and storage
- **session.py**: Active session tracking with real-time updates
- **index.py**: Concurrent-safe index using append-only logs
- **skills.py**: Pattern detection for skill extraction
- **models.py**: All Pydantic data models
- **cli.py**: Click-based command-line interface
- **utils.py**: Shared utility functions

## Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/bug-description
```

### 2. Make Changes

- Follow coding standards (see below)
- Write tests for new functionality
- Update documentation as needed
- Run tests frequently

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_memory

# Run specific test file
pytest tests/test_memory.py

# Run specific test
pytest tests/test_memory.py::test_create_session
```

### 4. Lint and Format

```bash
# Check style issues
ruff check .

# Auto-fix style issues
ruff check --fix .

# Format code
black .

# Type checking
mypy claude_memory
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: brief description

Longer explanation of what changed and why.
Fixes #123"
```

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Open a Pull Request on GitHub
```

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Maximum line length: **88 characters** (Black default)
- Use **docstrings** for all public functions/classes

### Type Hints Example

```python
from pathlib import Path
from claude_memory.models import MemoryEntry, MemoryScope

def save_memory(
    memory: MemoryEntry,
    scope: MemoryScope,
    output_dir: Path
) -> Path:
    """
    Save a memory entry to a file.

    Args:
        memory: The memory entry to save
        scope: Global or project scope
        output_dir: Directory to save to

    Returns:
        Path to the saved file
    """
    # Implementation
    pass
```

### Code Organization

- **One class per file** (except small helper classes)
- **Group related functions** together
- **Import order**: standard library, third-party, local
- **Avoid circular imports**

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `MemoryManager`)
- **Functions/methods**: `snake_case` (e.g., `create_session`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_THRESHOLD`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Error Handling

```python
# Good - specific exceptions
try:
    memory = index.find_by_id(memory_id)
    if memory is None:
        raise ValueError(f"Memory not found: {memory_id}")
except ValueError as e:
    logger.error(f"Invalid memory ID: {e}")
    raise

# Avoid bare except
try:
    something()
except:  # Don't do this
    pass
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from datetime import datetime

class MyModel(BaseModel):
    """Model description."""

    id: str
    created: datetime
    tags: list[str] = Field(default_factory=list)
    optional_field: str | None = None
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_memory.py           # MemoryManager tests
├── test_session.py          # SessionTracker tests
├── test_index.py            # IndexManager tests
├── test_skills.py           # SkillDetector tests
└── test_cli.py              # CLI tests
```

### Writing Tests

```python
import pytest
from pathlib import Path
from claude_memory import MemoryManager
from claude_memory.models import MemoryScope

def test_create_session(tmp_path):
    """Test session creation."""
    # Setup
    manager = MemoryManager(working_dir=tmp_path)

    # Execute
    session = manager.create_session()

    # Assert
    assert session.session_id is not None
    assert session.data.task == ""
    assert session.data.status == SessionStatus.ACTIVE

def test_save_session_to_memory(tmp_path):
    """Test saving session to long-term memory."""
    manager = MemoryManager(working_dir=tmp_path)
    session = manager.create_session()
    session.update_task("Test task")

    # Save
    memory = manager.save_session_to_memory(
        session=session,
        scope=MemoryScope.GLOBAL,
        tags=["test"],
        summary="Test summary"
    )

    # Verify
    assert memory.id is not None
    assert memory.title == "Test task"
    assert "test" in memory.tags
```

### Test Fixtures

```python
# conftest.py
import pytest
from pathlib import Path
from claude_memory import MemoryManager

@pytest.fixture
def temp_manager(tmp_path):
    """Create a temporary MemoryManager for testing."""
    return MemoryManager(working_dir=tmp_path)

@pytest.fixture
def sample_session(temp_manager):
    """Create a sample session."""
    session = temp_manager.create_session()
    session.update_task("Sample task")
    session.add_file_modified("test.py")
    return session
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=claude_memory --cov-report=html

# Specific test
pytest tests/test_memory.py::test_create_session

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Documentation

### Docstring Style

Use **Google style** docstrings:

```python
def search_memory(
    query: str = "",
    tags: list[str] | None = None,
    scope: MemoryScope | None = None
) -> list[MemoryEntry]:
    """
    Search memory across global and/or project.

    Args:
        query: Search query string
        tags: Optional list of tags to filter by
        scope: Scope to search (None = both)

    Returns:
        List of matching memory entries

    Raises:
        ValueError: If query is invalid

    Example:
        >>> results = manager.search_memory("auth", tags=["security"])
        >>> print(len(results))
        5
    """
    pass
```

### Documentation Files

When updating functionality, update relevant docs:

- `README.md` - Overview and quick start
- `docs/USAGE.md` - User-facing features
- `docs/API.md` - API changes
- `docs/ARCHITECTURE.md` - Design decisions
- `docs/EXAMPLES.md` - Usage examples

### Code Comments

```python
# Good - explain WHY, not WHAT
# Use append-log to avoid write conflicts in concurrent sessions
self._append_log_entry(entry)

# Less good - obvious from code
# Append the entry to the log
self._append_log_entry(entry)
```

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines (ruff, black)
- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No breaking changes (or clearly documented)
- [ ] Type hints are added
- [ ] Docstrings are complete

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] No breaking changes

## Related Issues
Fixes #123
```

### Review Process

1. Submit PR with clear description
2. Automated tests run (CI)
3. Code review by maintainers
4. Address feedback
5. Approval and merge

## Release Process

(For maintainers)

### Version Numbering

Follow **Semantic Versioning** (semver):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes

### Release Steps

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. Create GitHub release
6. Build and publish to PyPI (if applicable)

## Common Tasks

### Adding a New CLI Command

1. Add command in `cli.py`:
```python
@cli.command()
@click.argument("arg")
@click.option("--flag", is_flag=True)
def new_command(arg: str, flag: bool):
    """Command description."""
    # Implementation
    pass
```

2. Add tests in `tests/test_cli.py`
3. Update `docs/USAGE.md`

### Adding a New Data Model

1. Add model in `models.py`:
```python
class NewModel(BaseModel):
    """Model description."""
    field: str
    optional: int | None = None
```

2. Add tests in `tests/test_models.py`
3. Update `docs/API.md` if public

### Adding a New Utility Function

1. Add function in `utils.py`:
```python
def new_utility(param: str) -> str:
    """Utility description."""
    return param.upper()
```

2. Add tests in `tests/test_utils.py`
3. Export in `__init__.py` if public

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email maintainers privately
- **Ideas**: Open an issue for discussion first

## Development Tips

### Use Virtual Environment

Always activate your virtual environment before working:
```bash
source venv/bin/activate
```

### Run Tests Frequently

```bash
# Quick test during development
pytest tests/test_memory.py

# Full test before committing
pytest
```

### Use Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Debug with pdb

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Check Type Hints

```bash
mypy claude_memory --strict
```

## Architecture Guidelines

### Concurrency Model

- Use **append-only logs** for concurrent writes
- Never use file locking
- Rebuild index periodically to consolidate logs

### Data Storage

- **JSON** for indices (human-readable, git-friendly)
- **Markdown** for memory content (readable, diffable)
- **Filesystem** for structure (no databases)

### Error Handling

- Fail fast on invalid input
- Graceful degradation for missing files
- Clear error messages for users

### Performance

- Keep index reads fast (<100ms)
- Lazy-load detailed memories
- Rebuild indices when log threshold reached

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Claude Memory System!
