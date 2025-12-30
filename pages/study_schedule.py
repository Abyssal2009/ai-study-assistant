"""
Study Assistant - Study Schedule Page
Adaptive study scheduling with smart recommendations.
"""

import streamlit as st
import database as db
from datetime import date, datetime, timedelta
from utils import call_claude
import json


def render():
    """Render the Study Schedule page."""
    st.title("📅 Study Schedule")
    st.markdown("**Personalised study plan that adapts to your progress.**")

    # Check for subjects
    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Get API key for AI features
    api_key = st.session_state.get('bubble_ace_api_key', '')

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 What Next?",
        "📅 My Schedule",
        "🔧 Generate New",
        "📊 Adjustments"
    ])

    # TAB 1: What Next? - Smart Recommendations
    with tab1:
        _render_what_next_tab(api_key)

    # TAB 2: My Schedule - View/Manage
    with tab2:
        _render_schedule_tab()

    # TAB 3: Generate New - Schedule Creation
    with tab3:
        _render_generate_tab(subjects, api_key)

    # TAB 4: Adjustments - Change Log
    with tab4:
        _render_adjustments_tab()


def _render_what_next_tab(api_key: str):
    """Render the What Next? smart recommendation tab."""
    st.markdown("### 🎯 What Should I Study Now?")

    # Time selector
    col1, col2 = st.columns([2, 3])
    with col1:
        available_time = st.select_slider(
            "Time available:",
            options=[15, 30, 45, 60, 90, 120],
            value=30,
            format_func=lambda x: f"{x} mins"
        )

    # Get smart recommendation
    result = db.get_smart_recommendation(available_time)

    if result['recommendation']:
        rec = result['recommendation']

        st.markdown("---")
        st.markdown("### 🏆 TOP RECOMMENDATION")

        # Main recommendation card
        _render_recommendation_card(rec, is_top=True)

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Focus Session", type="primary", key="start_focus"):
                st.session_state['focus_subject_id'] = rec['subject_id']
                st.session_state['focus_topic'] = rec['topic']
                st.info(f"Ready to start a {rec['estimated_minutes']}-minute session on {rec['topic']}")
        with col2:
            if rec['action_type'] == 'flashcard_review':
                if st.button("📚 Go to Flashcards", key="go_flashcards"):
                    st.info("Navigate to Flashcards page to review")
            else:
                if st.button("📝 View Notes", key="view_notes"):
                    st.info(f"Search notes for: {rec['topic']}")
        with col3:
            if api_key and st.button("🤖 Get AI Study Tips", key="ai_tips"):
                _get_ai_study_tips(api_key, rec)

        # Alternative options
        if result['alternatives']:
            st.markdown("---")
            st.markdown("### 📋 Other Options")

            cols = st.columns(min(len(result['alternatives']), 3))
            for i, alt in enumerate(result['alternatives'][:3]):
                with cols[i]:
                    _render_recommendation_card(alt, is_top=False)
    else:
        st.info("No specific recommendations at this time. You're all caught up!")
        st.markdown("""
        **To get recommendations, make sure you have:**
        - Added subjects and exams
        - Completed some past papers to identify knowledge gaps
        - Created flashcards for revision
        """)

    # Topics Due for Review (SRS)
    st.markdown("---")
    _render_topics_due_section()


def _render_recommendation_card(rec: dict, is_top: bool = False):
    """Render a recommendation card."""
    colour = rec.get('subject_colour', '#3498db')

    # Priority colour
    priority = rec['priority_score']
    if priority >= 70:
        priority_colour = "#e74c3c"
        priority_label = "HIGH"
    elif priority >= 50:
        priority_colour = "#f39c12"
        priority_label = "MEDIUM"
    else:
        priority_colour = "#3498db"
        priority_label = "LOW"

    # Card styling
    card_bg = f"linear-gradient(135deg, {colour}22, {colour}11)" if is_top else f"{colour}11"

    st.markdown(f"""
    <div style="background: {card_bg};
                border-left: 4px solid {colour};
                padding: 15px;
                border-radius: 0 12px 12px 0;
                margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: bold; color: {colour};">{rec['subject_name']}</span>
            <span style="background: {priority_colour}; color: white; padding: 2px 8px;
                        border-radius: 12px; font-size: 11px;">{priority_label} - {priority:.0f}</span>
        </div>
        <h4 style="margin: 5px 0; color: #333;">{rec['topic']}</h4>
        <p style="margin: 5px 0; color: #666; font-size: 14px;">
            ⏰ {rec['estimated_minutes']} mins
            {f" | 📅 Exam in {rec['exam_days']} days" if rec.get('exam_days') else ""}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Reasons (only for top recommendation)
    if is_top and rec.get('reasons'):
        with st.expander("💡 Why this recommendation?"):
            for reason in rec['reasons']:
                st.markdown(f"• {reason}")


def _get_ai_study_tips(api_key: str, rec: dict):
    """Get AI-generated study tips for a topic."""
    prompt = f"""You are a study coach. A GCSE student should study:
Subject: {rec['subject_name']}
Topic: {rec['topic']}
Available time: {rec['estimated_minutes']} minutes
Mastery level: {rec.get('mastery_level', 'Unknown')}%

Give 3-4 specific, actionable study tips for this session. Be concise and practical.
Focus on active learning techniques suitable for GCSE level."""

    with st.spinner("Getting personalised tips..."):
        result = call_claude(api_key, prompt, model='haiku')
        if not result.startswith("Error:"):
            st.markdown("#### 🤖 AI Study Tips")
            st.markdown(result)
        else:
            st.error("Could not generate tips. Check your API key.")


def _render_schedule_tab():
    """Render the My Schedule tab."""
    st.markdown("### 📅 My Study Schedule")

    schedule = db.get_active_schedule()

    if not schedule:
        st.info("No active schedule. Create one in the 'Generate New' tab!")
        return

    # Schedule info header
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Schedule", schedule['name'])
    with col2:
        st.metric("Period", f"{schedule['start_date']} to {schedule['end_date']}")
    with col3:
        st.metric("Total Hours", schedule.get('total_hours_planned', 0))

    # Get session stats
    stats = db.get_session_stats(schedule['id'])

    # Progress bar
    if stats['total'] > 0:
        progress = stats['completed'] / stats['total']
        st.progress(progress, text=f"Progress: {stats['completed']}/{stats['total']} sessions ({progress*100:.0f}%)")

    # View selector
    st.markdown("---")
    view_mode = st.radio("View:", ["Daily", "Weekly", "List"], horizontal=True)

    # Date navigation
    if 'schedule_view_date' not in st.session_state:
        st.session_state.schedule_view_date = date.today()

    view_date = st.session_state.schedule_view_date

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Previous"):
            if view_mode == "Weekly":
                st.session_state.schedule_view_date -= timedelta(days=7)
            else:
                st.session_state.schedule_view_date -= timedelta(days=1)
            st.rerun()
    with col2:
        if st.button("📍 Today", use_container_width=True):
            st.session_state.schedule_view_date = date.today()
            st.rerun()
    with col3:
        if st.button("Next ▶"):
            if view_mode == "Weekly":
                st.session_state.schedule_view_date += timedelta(days=7)
            else:
                st.session_state.schedule_view_date += timedelta(days=1)
            st.rerun()

    st.markdown("---")

    # Display sessions based on view mode
    if view_mode == "Daily":
        _render_daily_view(schedule['id'], view_date)
    elif view_mode == "Weekly":
        week_start = view_date - timedelta(days=view_date.weekday())
        _render_weekly_view(schedule['id'], week_start)
    else:
        _render_list_view(schedule['id'])

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export as CSV"):
            _export_schedule_csv(schedule['id'])
    with col2:
        if st.button("🗑️ Deactivate Schedule"):
            db.deactivate_schedule(schedule['id'])
            st.success("Schedule deactivated")
            st.rerun()


def _render_daily_view(schedule_id: int, view_date: date):
    """Render daily schedule view."""
    sessions = db.get_sessions_for_date(schedule_id, view_date)

    # Date header
    day_name = view_date.strftime("%A")
    date_str = view_date.strftime("%d %B %Y")
    is_today = view_date == date.today()

    st.markdown(f"### {day_name}, {date_str} {'(Today)' if is_today else ''}")

    if not sessions:
        st.info("No sessions scheduled for this day.")
        return

    # Display each session
    for session in sessions:
        _render_session_card(session)


def _render_weekly_view(schedule_id: int, week_start: date):
    """Render weekly schedule view."""
    sessions = db.get_sessions_for_week(schedule_id, week_start)

    # Group by date
    sessions_by_date = {}
    for session in sessions:
        d = session['scheduled_date']
        if d not in sessions_by_date:
            sessions_by_date[d] = []
        sessions_by_date[d].append(session)

    # Display each day
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.isoformat()
        day_name = day.strftime("%a %d")
        is_today = day == date.today()

        with st.expander(f"{'📍 ' if is_today else ''}{day_name}", expanded=is_today):
            day_sessions = sessions_by_date.get(day_str, [])
            if day_sessions:
                for session in day_sessions:
                    _render_session_card(session, compact=True)
            else:
                st.caption("No sessions")


def _render_list_view(schedule_id: int):
    """Render list view of all sessions."""
    sessions = db.get_all_schedule_sessions(schedule_id)

    if not sessions:
        st.info("No sessions in this schedule.")
        return

    # Filter options
    status_filter = st.selectbox(
        "Filter by status:",
        ["All", "Pending", "Completed", "Missed"],
        key="list_status_filter"
    )

    if status_filter != "All":
        sessions = [s for s in sessions if s['status'] == status_filter.lower()]

    # Display sessions
    for session in sessions[:50]:  # Limit to 50 for performance
        _render_session_card(session)


def _render_session_card(session: dict, compact: bool = False):
    """Render a single session card."""
    colour = session.get('subject_colour', '#3498db')

    # Status styling
    status = session['status']
    status_icons = {
        'pending': '⏳',
        'completed': '✅',
        'missed': '❌',
        'rescheduled': '🔄'
    }
    status_icon = status_icons.get(status, '⏳')

    if compact:
        # Compact view for weekly display
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <span style="color: {colour}; font-weight: bold;">{session['subject_name']}</span>
            <span style="color: #666;"> - {session.get('topic', 'General')}</span>
            <span style="color: #999; font-size: 12px;"> ({session['duration_minutes']}m)</span>
            """, unsafe_allow_html=True)
        with col2:
            st.caption(f"{status_icon} {status}")
        with col3:
            if status == 'pending':
                if st.button("✓", key=f"done_{session['id']}"):
                    db.mark_session_complete(session['id'], session['duration_minutes'])
                    st.rerun()
    else:
        # Full card view
        st.markdown(f"""
        <div style="background: {colour}11;
                    border-left: 4px solid {colour};
                    padding: 12px;
                    border-radius: 0 8px 8px 0;
                    margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; color: {colour};">{session['subject_name']}</span>
                <span>{status_icon} {status.title()}</span>
            </div>
            <p style="margin: 5px 0; font-size: 16px; color: #333;">
                {session.get('topic', 'General Study')}
            </p>
            <p style="margin: 2px 0; color: #666; font-size: 13px;">
                📅 {session['scheduled_date']} | ⏰ {session['duration_minutes']} mins
                {f" | {session['start_time']}" if session.get('start_time') else ""}
            </p>
            {f"<p style='margin: 2px 0; color: #888; font-size: 12px;'>💡 {session['reason']}</p>" if session.get('reason') else ""}
        </div>
        """, unsafe_allow_html=True)

        # Action buttons for pending sessions
        if status == 'pending':
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Done", key=f"complete_{session['id']}"):
                    db.mark_session_complete(session['id'], session['duration_minutes'])
                    st.success("Session completed!")
                    st.rerun()
            with col2:
                if st.button("⏭️ Skip", key=f"skip_{session['id']}"):
                    db.trigger_missed_session_adjustment(session['id'])
                    st.info("Session rescheduled")
                    st.rerun()
            with col3:
                if st.button("📝 Notes", key=f"notes_{session['id']}"):
                    st.session_state[f"show_notes_{session['id']}"] = True

            # Notes input
            if st.session_state.get(f"show_notes_{session['id']}"):
                notes = st.text_input("Add notes:", key=f"note_input_{session['id']}")
                if st.button("Save Notes", key=f"save_notes_{session['id']}"):
                    db.mark_session_complete(session['id'], session['duration_minutes'], notes)
                    del st.session_state[f"show_notes_{session['id']}"]
                    st.rerun()


def _export_schedule_csv(schedule_id: int):
    """Export schedule to CSV."""
    sessions = db.get_all_schedule_sessions(schedule_id)

    if not sessions:
        st.warning("No sessions to export")
        return

    # Build CSV
    import io
    output = io.StringIO()
    output.write("Date,Subject,Topic,Duration (mins),Status,Reason\n")

    for s in sessions:
        output.write(f"{s['scheduled_date']},{s['subject_name']},{s.get('topic', '')},")
        output.write(f"{s['duration_minutes']},{s['status']},{s.get('reason', '')}\n")

    st.download_button(
        label="📥 Download CSV",
        data=output.getvalue(),
        file_name="study_schedule.csv",
        mime="text/csv"
    )


def _render_generate_tab(subjects: list, api_key: str):
    """Render the Generate New schedule tab."""
    st.markdown("### 🔧 Generate New Schedule")

    # Check if there's an active schedule
    active = db.get_active_schedule()
    if active:
        st.warning(f"You have an active schedule: **{active['name']}**. Generating a new one will replace it.")

    # Schedule settings
    st.markdown("#### Schedule Settings")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today())
    with col2:
        end_date = st.date_input("End Date", value=date.today() + timedelta(days=14))

    if end_date <= start_date:
        st.error("End date must be after start date")
        return

    col1, col2 = st.columns(2)
    with col1:
        daily_minutes = st.number_input(
            "Daily Study Time (minutes)",
            min_value=30, max_value=480, value=120, step=15
        )
    with col2:
        session_length = st.select_slider(
            "Session Length",
            options=[15, 20, 25, 30, 45, 60],
            value=30,
            format_func=lambda x: f"{x} mins"
        )

    # Subject selection
    st.markdown("#### Include Subjects")
    all_subjects = st.checkbox("All subjects", value=True)

    selected_subject_ids = None
    if not all_subjects:
        selected_subjects = st.multiselect(
            "Select subjects:",
            options=subjects,
            format_func=lambda x: x['name'],
            default=subjects[:5] if len(subjects) > 5 else subjects
        )
        selected_subject_ids = [s['id'] for s in selected_subjects]

    # Preview info
    st.markdown("---")
    days = (end_date - start_date).days + 1
    sessions_per_day = daily_minutes // session_length
    total_sessions = days * sessions_per_day
    total_hours = (total_sessions * session_length) // 60

    st.markdown(f"""
    **Schedule Preview:**
    - **Duration:** {days} days
    - **Sessions per day:** {sessions_per_day}
    - **Total sessions:** ~{total_sessions}
    - **Total study time:** ~{total_hours} hours
    """)

    # Subject summary
    st.markdown("#### 📊 Subject Status")
    summary = db.get_subject_study_summary()

    if summary:
        for subj in summary:
            if selected_subject_ids and subj['subject_id'] not in selected_subject_ids:
                continue

            with st.expander(f"{subj['subject_name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if subj['exam_days'] is not None:
                        st.metric("Exam in", f"{subj['exam_days']} days")
                    else:
                        st.metric("Exam", "Not set")
                with col2:
                    st.metric("Avg Mastery", f"{subj['avg_mastery']:.0f}%")
                with col3:
                    st.metric("Gaps", subj['knowledge_gaps'])

    # Generate buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Generate Schedule", type="primary", use_container_width=True):
            with st.spinner("Generating schedule..."):
                # Create schedule name
                schedule_name = f"Study Plan {start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}"

                # Create schedule
                schedule_id = db.create_study_schedule(
                    name=schedule_name,
                    start_date=start_date,
                    end_date=end_date,
                    generation_params={
                        'daily_minutes': daily_minutes,
                        'session_length': session_length,
                        'subject_ids': selected_subject_ids
                    }
                )

                # Generate sessions
                sessions_created = db.generate_schedule_sessions(
                    schedule_id=schedule_id,
                    start_date=start_date,
                    end_date=end_date,
                    daily_minutes=daily_minutes,
                    session_length=session_length,
                    subject_ids=selected_subject_ids
                )

                st.success(f"Schedule created with {sessions_created} sessions!")
                st.balloons()
                st.rerun()

    with col2:
        if api_key:
            if st.button("🤖 Generate with AI", use_container_width=True):
                st.info("AI-enhanced generation coming soon!")
        else:
            st.caption("Add API key in Settings for AI features")


def _render_adjustments_tab():
    """Render the Adjustments change log tab."""
    st.markdown("### 📊 Schedule Adjustments")
    st.markdown("See what changed in your schedule and why.")

    schedule = db.get_active_schedule()

    if not schedule:
        st.info("No active schedule. Adjustments will appear here when you have an active schedule.")
        return

    adjustments = db.get_schedule_adjustments(schedule['id'], limit=30)

    if not adjustments:
        st.info("No adjustments yet. The schedule will adapt as you complete sessions and take quizzes.")
        st.markdown("""
        **Adjustments happen when:**
        - You miss a scheduled session (auto-reschedule)
        - Quiz scores are below 50% (extra sessions added)
        - New exams are added (priorities recalculated)
        """)
        return

    # Display adjustments
    for adj in adjustments:
        # Format timestamp
        created = adj['created_at']
        if isinstance(created, str):
            try:
                dt = datetime.fromisoformat(created)
                time_str = dt.strftime("%d %b %H:%M")
            except ValueError:
                time_str = created[:16]
        else:
            time_str = str(created)[:16]

        # Adjustment type icons
        type_icons = {
            'quiz_result': '📝',
            'missed_session': '⏰',
            'rescheduled': '🔄',
            'exam_added': '📅',
            'manual': '✏️'
        }
        icon = type_icons.get(adj['adjustment_type'], '🔧')

        # Card
        st.markdown(f"""
        <div style="background: #f8f9fa; border-left: 3px solid #3498db;
                    padding: 12px; margin-bottom: 10px; border-radius: 0 8px 8px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">{icon} {adj['adjustment_type'].replace('_', ' ').title()}</span>
                <span style="color: #666; font-size: 12px;">{time_str}</span>
            </div>
            <p style="margin: 0; color: #333;">{adj['reason']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Show details if available
        if adj.get('old_value') or adj.get('new_value'):
            with st.expander("View details"):
                if adj.get('old_value'):
                    try:
                        old = json.loads(adj['old_value'])
                        st.json({"Previous": old})
                    except json.JSONDecodeError:
                        st.text(f"Previous: {adj['old_value']}")
                if adj.get('new_value'):
                    try:
                        new = json.loads(adj['new_value'])
                        st.json({"New": new})
                    except json.JSONDecodeError:
                        st.text(f"New: {adj['new_value']}")


def _render_topics_due_section():
    """Render the Topics Due for Review section using SRS."""
    st.markdown("### 📚 Topics Due for Review")
    st.caption("Topics tracked with spaced repetition that need attention")

    # Get topic recommendations
    due_topics = db.get_topic_review_recommendations(limit=5)

    if due_topics:
        for topic in due_topics:
            colour = topic.get('subject_colour', '#3498db')
            days_overdue = int(topic.get('days_overdue', 0))
            avg_score = topic.get('avg_quiz_score', 0)
            importance = topic.get('importance_level', 'medium')

            # Urgency indicator
            if days_overdue > 7:
                urgency_color = "#e74c3c"
                urgency_label = "OVERDUE"
            elif days_overdue > 0:
                urgency_color = "#f39c12"
                urgency_label = f"{days_overdue}d overdue"
            else:
                urgency_color = "#3498db"
                urgency_label = "Due today"

            st.markdown(f"""
            <div style="background: {colour}11;
                        border-left: 4px solid {colour};
                        padding: 12px 15px;
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: {colour};">{topic['subject_name']}</span>
                    <span style="background: {urgency_color}; color: white; padding: 2px 8px;
                                border-radius: 12px; font-size: 11px;">{urgency_label}</span>
                </div>
                <h4 style="margin: 5px 0; color: #333;">{topic['topic']}</h4>
                <p style="margin: 5px 0; color: #666; font-size: 13px;">
                    {f"Avg score: {avg_score:.0f}% | " if avg_score else ""}
                    Importance: {importance.title()}
                    {f" | Exam in {int(topic['days_to_exam'])} days" if topic.get('days_to_exam') and topic['days_to_exam'] < 999 else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Sync button
        st.markdown("---")
        if st.button("🔄 Sync Topics from Flashcards", key="sync_topics_schedule"):
            count = db.sync_topics_from_flashcards()
            if count > 0:
                st.success(f"Synced {count} new topics!")
                st.rerun()
            else:
                st.info("All topics already synced.")
    else:
        st.success("No topics due for review right now!")
        st.markdown("""
        **Topics are added when you:**
        - Create flashcards with topics
        - Complete knowledge gap assessments
        - Add them manually in SRS Settings
        """)
