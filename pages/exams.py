"""
Study Assistant - Exams Page
Exam calendar and countdown.
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

    tab1, tab2 = st.tabs(["📅 Upcoming Exams", "➕ Add Exam"])

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
                    <h3 style="margin: 10px 0; color: #333;">{exam['name']}</h3>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>{exam['subject_name']}</strong> • {exam['exam_date']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("🗑️ Delete", key=f"del_exam_{exam['id']}"):
                        db.delete_exam(exam['id'])
                        st.rerun()
        else:
            st.info("No exams scheduled. Add your exam dates to start the countdown!")

    # TAB 2: Add Exam
    with tab2:
        st.markdown("### Add New Exam")

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

            if st.form_submit_button("Add Exam", type="primary"):
                if name:
                    db.add_exam(
                        subject_id=subject['id'],
                        name=name,
                        exam_date=exam_date.isoformat(),
                        duration_minutes=duration,
                        location=location
                    )
                    st.success(f"Added: {name}")
                    st.rerun()
                else:
                    st.error("Please enter an exam name")
