"""
Study Assistant - Exams Page
Exam calendar and countdown with Google Calendar sync.
"""

import streamlit as st
import database as db
from utils import days_until


def render():
    """Render the Exams calendar page."""
    st.title("📅 Exam Calendar")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Google Calendar sync status
    _render_calendar_sync_status()

    tab1, tab2, tab3 = st.tabs(["📅 Upcoming Exams", "➕ Add Exam", "🔄 Import from Calendar"])

    # TAB 1: Upcoming Exams
    with tab1:
        exams = db.get_all_exams()
        if exams:
            for exam in exams:
                days = days_until(exam['exam_date'])
                if days < 0:
                    continue  # Skip past exams

                # Urgency styling
                if days <= 7:
                    urgency_color = "#e74c3c"
                    urgency_text = "🚨 VERY SOON"
                elif days <= 14:
                    urgency_color = "#e67e22"
                    urgency_text = "⚠️ SOON"
                elif days <= 30:
                    urgency_color = "#f39c12"
                    urgency_text = "📌 UPCOMING"
                else:
                    urgency_color = "#3498db"
                    urgency_text = "📅 SCHEDULED"

                # Sync indicator
                sync_icon = "☁️" if exam.get('google_calendar_id') else ""

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {urgency_color}22, {urgency_color}11);
                            border-left: 4px solid {urgency_color};
                            padding: 15px;
                            margin: 10px 0;
                            border-radius: 0 12px 12px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: {urgency_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">{urgency_text}</span>
                        <span style="font-size: 2rem; font-weight: bold; color: {urgency_color};">{days} days</span>
                    </div>
                    <h3 style="margin: 10px 0; color: #333;">{sync_icon} {exam['name']}</h3>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>{exam['subject_name']}</strong> • {exam['exam_date']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([3, 1, 1])
                with col2:
                    if not exam.get('google_calendar_id'):
                        if st.button("☁️ Sync", key=f"sync_exam_{exam['id']}"):
                            _sync_single_exam(exam)
                with col3:
                    if st.button("🗑️ Delete", key=f"del_exam_{exam['id']}"):
                        _delete_exam_with_calendar(exam['id'])
                        st.rerun()
        else:
            st.info("No exams scheduled. Add your exam dates to start the countdown!")

    # TAB 2: Add Exam
    with tab2:
        st.markdown("### Add New Exam")

        # Check calendar connection for auto-sync option
        try:
            from cloud.google_calendar import get_client
            calendar_client = get_client()
            calendar_connected = calendar_client.is_authenticated()
        except (ImportError, Exception):
            calendar_connected = False

        with st.form("add_exam"):
            name = st.text_input("Exam Name *", placeholder="e.g., Biology Paper 1")
            subject = st.selectbox(
                "Subject *",
                options=subjects,
                format_func=lambda x: x['name']
            )
            exam_date = st.date_input("Exam Date *")
            st.time_input("Exam Time (optional)")  # Displayed but not stored
            duration = st.number_input("Duration (minutes)", min_value=30, max_value=300, value=90)
            location = st.text_input("Location (optional)", placeholder="e.g., Main Hall")

            if calendar_connected:
                auto_sync = st.checkbox("Add to Google Calendar", value=True)
            else:
                auto_sync = False

            if st.form_submit_button("Add Exam", type="primary"):
                if name:
                    exam_id = db.add_exam(
                        subject_id=subject['id'],
                        name=name,
                        exam_date=exam_date.isoformat(),
                        duration_minutes=duration,
                        location=location
                    )
                    st.success(f"Added: {name}")

                    # Auto-sync to calendar if enabled
                    if auto_sync and calendar_connected:
                        exam = db.get_exam_by_id(exam_id)
                        if exam:
                            success, msg, event_id = calendar_client.sync_exam_to_calendar(exam)
                            if success and event_id:
                                db.update_exam_calendar_id(exam_id, event_id)
                                st.success("☁️ Added to Google Calendar")
                            else:
                                st.warning(f"Calendar sync failed: {msg}")

                    st.rerun()
                else:
                    st.error("Please enter an exam name")

    # TAB 3: Import from Calendar
    with tab3:
        st.markdown("### 🔄 Import from Google Calendar")
        _render_calendar_import(subjects)


def _render_calendar_sync_status():
    """Show Google Calendar connection status and sync button."""
    try:
        from cloud.google_calendar import get_client
        client = get_client()

        if client.is_authenticated():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success("☁️ Connected to Google Calendar")
            with col2:
                unsynced = db.get_exams_without_calendar_id()
                if unsynced:
                    if st.button(f"Sync All ({len(unsynced)})"):
                        with st.spinner("Syncing exams to Google Calendar..."):
                            success, failed, messages = client.sync_all_exams(unsynced)
                            if success > 0:
                                st.success(f"Synced {success} exam(s) to calendar")
                            if failed > 0:
                                for msg in messages:
                                    st.warning(msg)
                            st.rerun()
        else:
            st.info("☁️ Connect to Google Calendar in Settings > Backup & Sync to enable sync")

    except ImportError:
        st.caption("Google Calendar integration not available")
    except Exception as e:
        st.caption(f"Calendar status: {e}")


def _sync_single_exam(exam: dict):
    """Sync a single exam to Google Calendar."""
    try:
        from cloud.google_calendar import get_client
        client = get_client()

        if client.is_authenticated():
            with st.spinner("Syncing..."):
                success, msg, event_id = client.sync_exam_to_calendar(exam)
                if success and event_id:
                    db.update_exam_calendar_id(exam['id'], event_id)
                    st.success(f"☁️ {msg}")
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.warning("Connect to Google Calendar first in Settings")
    except Exception as e:
        st.error(f"Sync error: {e}")


def _delete_exam_with_calendar(exam_id: int):
    """Delete exam and remove from Google Calendar if synced."""
    calendar_id = db.delete_exam(exam_id)

    if calendar_id:
        try:
            from cloud.google_calendar import get_client
            client = get_client()
            if client.is_authenticated():
                client.delete_from_calendar(calendar_id)
        except (ImportError, Exception):
            pass  # Calendar deletion is best-effort


def _render_calendar_import(subjects):
    """Render the calendar import UI."""
    try:
        from cloud.google_calendar import get_client
        client = get_client()

        if not client.is_authenticated():
            st.warning("Connect to Google Calendar first in Settings > Backup & Sync")
            return

        st.markdown("""
        Import events from your Google Calendar as exams.
        Events will be fetched from the "Study Assistant Exams" calendar.
        """)

        if st.button("🔍 Fetch Calendar Events", type="primary"):
            with st.spinner("Fetching events..."):
                success, msg, events = client.get_calendar_events(days_ahead=90)

                if success:
                    if events:
                        st.session_state.calendar_events = events
                        st.success(f"Found {len(events)} upcoming events")
                    else:
                        st.info("No upcoming events found in the calendar")
                else:
                    st.error(msg)

        # Show fetched events for import
        if 'calendar_events' in st.session_state and st.session_state.calendar_events:
            st.markdown("---")
            st.markdown("#### Events to Import")

            for event in st.session_state.calendar_events:
                with st.expander(f"📅 {event['name']} - {event['date']}"):
                    st.caption(f"Date: {event['date']}")
                    if event.get('description'):
                        st.caption(f"Description: {event['description'][:100]}")

                    # Import form
                    import_subject = st.selectbox(
                        "Assign to subject:",
                        options=subjects,
                        format_func=lambda x: x['name'],
                        key=f"import_subject_{event['id']}"
                    )

                    if st.button("Import as Exam", key=f"import_{event['id']}"):
                        # Clean name (remove emoji if present)
                        name = event['name'].replace("📚 ", "")

                        exam_id = db.add_exam(
                            subject_id=import_subject['id'],
                            name=name,
                            exam_date=event['date']
                        )
                        # Store the calendar event ID
                        db.update_exam_calendar_id(exam_id, event['id'])
                        st.success(f"Imported: {name}")
                        # Remove from list
                        st.session_state.calendar_events = [
                            e for e in st.session_state.calendar_events
                            if e['id'] != event['id']
                        ]
                        st.rerun()

    except ImportError:
        st.error("Google Calendar module not available")
    except Exception as e:
        st.error(f"Error: {e}")
