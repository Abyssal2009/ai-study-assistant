"""
Study Assistant - Focus Timer Page
Pomodoro-style focus sessions with logging.
"""

import streamlit as st
from datetime import datetime, timedelta
import database as db


def render():
    """Render the Focus Timer page."""
    st.title("⏱️ Focus Timer")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Session state
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_start_time' not in st.session_state:
        st.session_state.timer_start_time = None
    if 'timer_duration' not in st.session_state:
        st.session_state.timer_duration = 25
    if 'timer_subject_id' not in st.session_state:
        st.session_state.timer_subject_id = None

    # Today's stats
    focus_today = db.get_total_focus_minutes_today()
    sessions_today = db.get_focus_sessions_today()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card-green">
            <h2 style="color: white; margin: 0;">{focus_today} min</h2>
            <p style="margin: 5px 0 0 0;">Focus Today</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="color: white; margin: 0;">{len(sessions_today)}</h2>
            <p style="margin: 5px 0 0 0;">Sessions Today</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        streak = db.get_focus_streak()
        st.markdown(f"""
        <div class="stat-card-orange">
            <h2 style="color: white; margin: 0;">{streak} days</h2>
            <p style="margin: 5px 0 0 0;">Focus Streak</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if not st.session_state.timer_running:
        # Timer setup
        st.markdown("### Start a Focus Session")

        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox(
                "What are you studying?",
                options=subjects,
                format_func=lambda x: x['name']
            )
        with col2:
            duration = st.selectbox(
                "Duration:",
                options=[15, 25, 30, 45, 60, 90],
                index=1,
                format_func=lambda x: f"{x} minutes"
            )

        st.markdown("#### Quick Start")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⚡ 15 min", use_container_width=True):
                _start_timer(subject['id'], 15)
        with col2:
            if st.button("🎯 25 min", use_container_width=True, type="primary"):
                _start_timer(subject['id'], 25)
        with col3:
            if st.button("💪 45 min", use_container_width=True):
                _start_timer(subject['id'], 45)

        if st.button(f"▶️ Start {duration} min Session", type="primary", use_container_width=True):
            _start_timer(subject['id'], duration)

    else:
        # Timer running
        start_time = st.session_state.timer_start_time
        duration = st.session_state.timer_duration
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        remaining = max(0, duration - elapsed)

        # Get subject name
        subject = db.get_subject_by_id(st.session_state.timer_subject_id)
        subject_name = subject['name'] if subject else "Unknown"

        st.markdown(f"### Studying: **{subject_name}**")

        # Timer display
        mins = int(remaining)
        secs = int((remaining - mins) * 60)

        st.markdown(f"""
        <div class="timer-display">
            {mins:02d}:{secs:02d}
        </div>
        """, unsafe_allow_html=True)

        progress = elapsed / duration if duration > 0 else 0
        st.progress(min(progress, 1.0))

        if remaining <= 0:
            st.success("🎉 Session Complete!")
            st.balloons()

            # Log the session
            db.add_focus_session(
                subject_id=st.session_state.timer_subject_id,
                duration_minutes=duration,
                completed=True
            )

            if st.button("Start Another Session", type="primary"):
                st.session_state.timer_running = False
                st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏸️ Pause & Save", use_container_width=True):
                    # Save partial session
                    db.add_focus_session(
                        subject_id=st.session_state.timer_subject_id,
                        duration_minutes=int(elapsed),
                        completed=False
                    )
                    st.session_state.timer_running = False
                    st.success(f"Saved {int(elapsed)} minutes!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.timer_running = False
                    st.rerun()

            # Auto-refresh
            st.markdown("*Timer updates every few seconds. Refresh page to update.*")

    # Recent sessions
    st.markdown("---")
    st.markdown("### Recent Sessions")

    recent = db.get_recent_focus_sessions(limit=10)
    if recent:
        for session in recent:
            status = "✅" if session.get('completed') else "⏸️"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px;">
                {status} <strong>{session['subject_name']}</strong> - {session['duration_minutes']} min
                <span style="color: #666; font-size: 12px; float: right;">{session['created_at'][:10]}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent sessions. Start your first focus session!")


def _start_timer(subject_id: int, duration: int):
    """Start a new timer session."""
    st.session_state.timer_running = True
    st.session_state.timer_start_time = datetime.now()
    st.session_state.timer_duration = duration
    st.session_state.timer_subject_id = subject_id
    st.rerun()
