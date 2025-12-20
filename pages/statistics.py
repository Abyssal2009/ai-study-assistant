"""
Study Assistant - Statistics Page
Study analytics and progress tracking.
"""

import streamlit as st
from datetime import date, timedelta
import database as db


def render():
    """Render the Statistics page."""
    st.title("📈 Statistics")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first to see statistics.")
        st.stop()

    # Overview metrics
    st.markdown("### Overview")

    col1, col2, col3, col4 = st.columns(4)

    hw_stats = db.get_homework_stats()
    fc_stats = db.get_flashcard_stats()
    focus_today = db.get_total_focus_minutes_today()
    paper_count = db.get_paper_count()

    with col1:
        st.metric("Homework Completed", hw_stats['completed_this_week'], delta="This week")

    with col2:
        st.metric("Flashcards Reviewed", fc_stats['reviewed_today'], delta="Today")

    with col3:
        st.metric("Focus Time", f"{focus_today} min", delta="Today")

    with col4:
        st.metric("Past Papers", paper_count)

    st.markdown("---")

    # Tabs for different stats
    tab1, tab2, tab3 = st.tabs(["📝 Homework", "🃏 Flashcards", "⏱️ Focus Time"])

    # TAB 1: Homework Stats
    with tab1:
        st.markdown("### Homework Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Status")
            st.metric("Pending", hw_stats['pending'])
            st.metric("Overdue", hw_stats['overdue'])
            st.metric("Completed This Week", hw_stats['completed_this_week'])
            st.metric("Completed Total", hw_stats['completed_total'])

        with col2:
            st.markdown("#### By Subject")
            for subject in subjects:
                count = db.get_homework_count_by_subject(subject['id'])
                if count > 0:
                    st.markdown(f"**{subject['name']}:** {count} items")

    # TAB 2: Flashcard Stats
    with tab2:
        st.markdown("### Flashcard Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Overview")
            st.metric("Total Cards", fc_stats['total'])
            st.metric("Due Today", fc_stats['due_today'])
            st.metric("Reviewed Today", fc_stats['reviewed_today'])
            st.metric("7-Day Accuracy", f"{fc_stats['accuracy_7_days']}%")

        with col2:
            st.markdown("#### By Subject")
            for subject in subjects:
                count = db.get_flashcard_count_by_subject(subject['id'])
                if count > 0:
                    st.markdown(f"**{subject['name']}:** {count} cards")

        # Accuracy trend
        st.markdown("---")
        st.markdown("#### Review Performance")

        if fc_stats['reviewed_today'] > 0:
            st.progress(fc_stats['accuracy_7_days'] / 100)
            if fc_stats['accuracy_7_days'] >= 80:
                st.success("Excellent! Your retention is strong.")
            elif fc_stats['accuracy_7_days'] >= 60:
                st.info("Good progress! Keep reviewing regularly.")
            else:
                st.warning("Consider reviewing cards more frequently.")

    # TAB 3: Focus Time Stats
    with tab3:
        st.markdown("### Focus Time Statistics")

        # This week's focus
        week_focus = db.get_focus_minutes_this_week()
        streak = db.get_focus_streak()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Today", f"{focus_today} min")

        with col2:
            st.metric("This Week", f"{week_focus} min")

        with col3:
            st.metric("Streak", f"{streak} days")

        st.markdown("---")
        st.markdown("#### Focus by Subject")

        for subject in subjects:
            mins = db.get_focus_minutes_by_subject(subject['id'])
            if mins > 0:
                hours = mins // 60
                remaining_mins = mins % 60
                time_str = f"{hours}h {remaining_mins}m" if hours > 0 else f"{mins}m"
                st.markdown(f"**{subject['name']}:** {time_str}")

        # Recent sessions
        st.markdown("---")
        st.markdown("#### Recent Sessions")

        recent = db.get_recent_focus_sessions(limit=5)
        if recent:
            for session in recent:
                status = "✅" if session.get('completed') else "⏸️"
                st.markdown(f"- {status} {session['subject_name']} - {session['duration_minutes']} min ({session['created_at'][:10]})")
        else:
            st.info("No focus sessions yet.")
