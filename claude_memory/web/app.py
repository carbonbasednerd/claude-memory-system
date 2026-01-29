"""Main Streamlit web dashboard for Claude Memory System."""

import streamlit as st
from pathlib import Path

from claude_memory.web.data_loader import load_memory_data
from claude_memory.web.components import filters, stats_overview, session_detail, tag_cloud
from claude_memory.web.charts.plotly_timeline import create_timeline_chart, create_mini_timeline


# Page configuration
st.set_page_config(
    page_title="Claude Memory Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point."""

    # Header
    st.title("🧠 Claude Memory Dashboard")
    st.markdown("Interactive visualization and exploration of your Claude memory system")

    # Initialize session state
    if 'selected_memory_id' not in st.session_state:
        st.session_state.selected_memory_id = None

    # Load all memories first (for filter options)
    try:
        all_memories = load_memory_data(scope="both")
    except Exception as e:
        st.error(f"Error loading memories: {e}")
        st.info("Make sure you're in a directory with Claude memory data or have global memories saved.")
        return

    # Render filters in sidebar
    filter_config = filters.render_filter_sidebar(all_memories)

    # Apply scope filter via data loader (for caching efficiency)
    scope_memories = load_memory_data(scope=filter_config['scope'])

    # Apply remaining filters
    filtered_memories = filters.apply_filters(scope_memories, filter_config)

    # Display filter summary
    if filtered_memories != all_memories:
        st.info(f"Showing {len(filtered_memories)} of {len(all_memories)} total memories")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📅 Timeline", "🏷️ Tags", "🔍 Search"])

    # Tab 1: Overview
    with tab1:
        st.header("Overview")

        if filtered_memories:
            # Stats overview
            stats_overview.render(filtered_memories)

            # Mini timeline
            st.divider()
            st.subheader("Memory Creation Timeline")
            mini_timeline = create_mini_timeline(filtered_memories)
            st.plotly_chart(mini_timeline, use_container_width=True)
        else:
            st.info("No memories match the current filters")

    # Tab 2: Timeline
    with tab2:
        st.header("Timeline Visualization")

        if filtered_memories:
            timeline_fig = create_timeline_chart(filtered_memories)
            st.plotly_chart(timeline_fig, use_container_width=True)

            st.markdown("""
            **Interaction tips:**
            - Hover over points to see details
            - Click and drag to zoom into a time range
            - Double-click to reset zoom
            - Use the toolbar to pan, zoom, or save the chart
            """)

            # Show memories in a table below
            st.divider()
            st.subheader("Memory List")

            # Create table data
            table_data = []
            for mem in sorted(filtered_memories, key=lambda m: m.created, reverse=True):
                table_data.append({
                    'Title': mem.title,
                    'Type': mem.type,
                    'Scope': mem.scope,
                    'Created': mem.created.strftime('%Y-%m-%d %H:%M'),
                    'Accesses': mem.access.count,
                    'Tags': ', '.join(mem.tags[:3]) if mem.tags else 'None',
                    'ID': mem.id,
                })

            # Display table with selection
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'ID': st.column_config.TextColumn('ID', width='small'),
                }
            )

            # Memory selection for detail view
            selected_id = st.selectbox(
                "Select memory to view details:",
                options=[''] + [m.id for m in filtered_memories],
                format_func=lambda x: 'Choose a memory...' if x == '' else x,
            )

            if selected_id:
                selected_memory = next((m for m in filtered_memories if m.id == selected_id), None)
                if selected_memory:
                    st.divider()
                    session_detail.render(selected_memory)

        else:
            st.info("No memories match the current filters")

    # Tab 3: Tags
    with tab3:
        st.header("Tag Analysis")

        if filtered_memories:
            tag_cloud.render(filtered_memories)
        else:
            st.info("No memories match the current filters")

    # Tab 4: Search
    with tab4:
        st.header("Search Memories")

        # Search interface
        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "Search in titles and tags",
                placeholder="Enter search terms...",
                help="Search is case-insensitive"
            )

        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            search_button = st.button("🔍 Search", use_container_width=True)

        # Perform search
        if search_query or filtered_memories:
            # Filter by search query if provided
            if search_query:
                search_lower = search_query.lower()
                search_results = [
                    m for m in filtered_memories
                    if search_lower in m.title.lower() or
                       any(search_lower in tag.lower() for tag in m.tags)
                ]
            else:
                search_results = filtered_memories

            st.write(f"**{len(search_results)} results**")

            if search_results:
                # Display results
                for mem in sorted(search_results, key=lambda m: m.created, reverse=True):
                    with st.expander(f"{mem.title} ({mem.type})"):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.write(f"**Scope:** {mem.scope}")
                        with col2:
                            st.write(f"**Created:** {mem.created.strftime('%Y-%m-%d')}")
                        with col3:
                            st.write(f"**Accesses:** {mem.access.count}")
                        with col4:
                            st.write(f"**Tags:** {', '.join(mem.tags[:2]) if mem.tags else 'None'}")

                        if st.button(f"View Details", key=f"detail_{mem.id}"):
                            st.session_state.selected_memory_id = mem.id

                        # Show details if selected
                        if st.session_state.selected_memory_id == mem.id:
                            st.divider()
                            session_detail.render(mem)
            else:
                st.info("No memories match your search query")

    # Footer
    st.divider()
    st.caption("Claude Memory System Web Dashboard | Use filters in the sidebar to refine results")


if __name__ == "__main__":
    main()
