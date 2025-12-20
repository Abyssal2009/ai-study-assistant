"""
Study Assistant - Homework Page
Homework tracking and management.
"""

import streamlit as st
from datetime import date
import database as db
from utils import format_due_date, days_until


def render():
    """Render the Homework tracking page."""
    st.title("📝 Homework Tracker")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["📋 All Homework", "➕ Add New", "✅ Completed"])

    # TAB 1: All Homework
    with tab1:
        homework = db.get_all_homework()
        if homework:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_subject = st.selectbox(
                    "Filter by subject:",
                    options=[None] + subjects,
                    format_func=lambda x: "All Subjects" if x is None else x['name']
                )
            with col2:
                filter_priority = st.selectbox(
                    "Filter by priority:",
                    options=[None, "high", "medium", "low"],
                    format_func=lambda x: "All Priorities" if x is None else x.title()
                )

            # Apply filters
            filtered = homework
            if filter_subject:
                filtered = [h for h in filtered if h['subject_id'] == filter_subject['id']]
            if filter_priority:
                filtered = [h for h in filtered if h['priority'] == filter_priority]

            st.markdown("---")

            for hw in filtered:
                days = days_until(hw['due_date'])
                is_overdue = days < 0

                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    if is_overdue:
                        st.markdown(f"**⚠️ {hw['title']}**")
                    else:
                        st.markdown(f"**{hw['title']}**")
                    st.caption(f"{hw['subject_name']}")
                with col2:
                    st.markdown(format_due_date(hw['due_date']))
                with col3:
                    priority_colors = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                    st.markdown(priority_colors.get(hw['priority'], '⚪'))
                with col4:
                    if st.button("✓", key=f"complete_{hw['id']}"):
                        db.mark_homework_complete(hw['id'])
                        st.rerun()

                if hw['description']:
                    st.caption(hw['description'])
                st.markdown("---")
        else:
            st.info("No homework to show! Add some using the 'Add New' tab.")

    # TAB 2: Add New
    with tab2:
        st.markdown("### Add New Homework")

        with st.form("add_homework"):
            title = st.text_input("Title *", placeholder="e.g., Biology worksheet page 45")
            subject = st.selectbox(
                "Subject *",
                options=subjects,
                format_func=lambda x: x['name']
            )
            due_date = st.date_input("Due Date *", value=date.today())
            priority = st.selectbox("Priority", options=["medium", "high", "low"])
            description = st.text_area("Description (optional)", placeholder="Additional details...")

            if st.form_submit_button("Add Homework", type="primary"):
                if title:
                    db.add_homework(
                        subject_id=subject['id'],
                        title=title,
                        description=description,
                        due_date=due_date.isoformat(),
                        priority=priority
                    )
                    st.success(f"Added: {title}")
                    st.rerun()
                else:
                    st.error("Please enter a title")

    # TAB 3: Completed
    with tab3:
        completed = db.get_completed_homework()
        if completed:
            st.markdown(f"### Completed ({len(completed)} items)")
            for hw in completed[:20]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"~~{hw['title']}~~")
                    st.caption(f"{hw['subject_name']}")
                with col2:
                    if st.button("🗑️", key=f"delete_{hw['id']}"):
                        db.delete_homework(hw['id'])
                        st.rerun()
        else:
            st.info("No completed homework yet. Keep working!")
