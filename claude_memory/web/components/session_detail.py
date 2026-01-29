"""Session detail modal component."""

import streamlit as st
from pathlib import Path

from claude_memory.models import MemoryEntry, MemoryScope
from claude_memory.web.utils.formatters import format_datetime, format_tags
from claude_memory.utils import get_global_claude_dir, get_project_claude_dir


def render(memory: MemoryEntry):
    """Render detailed view of a memory/session.

    Args:
        memory: MemoryEntry object to display
    """
    st.header(memory.title)

    # Metadata
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Type**")
        st.write(memory.type)

    with col2:
        st.markdown("**Scope**")
        st.write(memory.scope)

    with col3:
        st.markdown("**Created**")
        st.write(format_datetime(memory.created, '%Y-%m-%d %H:%M'))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Access Count**")
        st.write(memory.access.count)

    with col2:
        st.markdown("**Last Accessed**")
        st.write(format_datetime(memory.access.last_accessed))

    with col3:
        st.markdown("**Tags**")
        st.write(format_tags(memory.tags))

    st.divider()

    # Content
    st.subheader("Content")

    # Construct full file path
    if memory.scope == MemoryScope.GLOBAL:
        base_dir = get_global_claude_dir() / "memory"
    else:
        project_dir = get_project_claude_dir(Path.cwd())
        base_dir = project_dir / "memory" if project_dir else None

    if base_dir:
        file_path = base_dir / memory.file

        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Display based on file type
                if str(memory.file).endswith('.md'):
                    st.markdown(content)
                else:
                    st.code(content, language='text')

            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.write(f"File path: {file_path}")
        else:
            st.warning("Content file not found")
            st.write(f"Expected path: {file_path}")
    else:
        st.warning("Could not determine memory base directory")

    # File path info
    st.divider()
    st.caption(f"File: `{memory.file}`")


def show_modal(memory: MemoryEntry):
    """Show memory detail in a modal dialog.

    Args:
        memory: MemoryEntry to display
    """
    with st.expander(f"📄 {memory.title}", expanded=True):
        render(memory)
