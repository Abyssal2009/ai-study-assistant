"""
Study Assistant - Dashboard Page
Main overview of study status and recommendations.
"""

import streamlit as st
from datetime import date
import database as db
from utils import days_until, format_due_date, get_urgency_colour, get_urgency_icon


def render():
    """Render the Dashboard page."""
    st.title("📊 Dashboard")
    st.markdown(f"**Today is {date.today().strftime('%A, %d %B %Y')}**")

    # Check if subjects exist - friendly onboarding
    subjects = db.get_all_subjects()
    if not subjects:
        st.markdown("""
        ### 👋 Welcome to Study Assistant!

        Get started in 3 easy steps:
        1. **Add your subjects** - Go to **Subjects** (under Settings) to add your GCSE subjects
        2. **Add homework & exams** - Track deadlines and exam dates
        3. **Create flashcards** - Build your revision materials

        Your personalised dashboard will appear here once you add your first subject.
        """)
        st.stop()

    # TOP RECOMMENDATION - What should I study next?
    top_rec = db.get_top_recommendation()
    if top_rec:
        color = get_urgency_colour(top_rec['urgency'])
        icon = get_urgency_icon(top_rec['urgency'])

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}22, {color}11);
                    border-left: 4px solid {color};
                    padding: 15px 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;">
            <h3 style="margin: 0 0 5px 0; color: {color};">{icon} What Should I Study Next?</h3>
            <p style="font-size: 1.2em; margin: 5px 0; font-weight: bold;">{top_rec['title']}</p>
            <p style="margin: 5px 0; color: #666;">
                <strong>{top_rec['subject_name']}</strong> • {top_rec['reason']}
            </p>
            <p style="margin: 5px 0; font-style: italic; color: #888;">{top_rec['action']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Four columns for key stats with coloured cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        due_today = db.get_homework_due_today()
        due_count = len(due_today)
        st.markdown(f"""
        <div class="stat-card-blue">
            <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{due_count}</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Due Today</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        overdue = db.get_overdue_homework()
        overdue_count = len(overdue)
        card_class = "stat-card-orange" if overdue_count > 0 else "stat-card-green"
        st.markdown(f"""
        <div class="{card_class}">
            <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{overdue_count}</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Overdue</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        fc_due = db.get_due_flashcards_count()
        st.markdown(f"""
        <div class="stat-card">
            <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{fc_due}</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Cards to Review</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        exams = db.get_exams_this_month()
        exam_count = len(exams)
        st.markdown(f"""
        <div class="stat-card-green">
            <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{exam_count}</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Exams This Month</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detail sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Due Today")
        if due_today:
            for hw in due_today:
                st.markdown(f"""
                <div class="homework-card" style="border-left-color: {hw['subject_colour']};">
                    <strong>{hw['title']}</strong><br>
                    <span class="subject-badge" style="background-color: {hw['subject_colour']};">{hw['subject_name']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-msg">Nothing due today!</div>
            """, unsafe_allow_html=True)

        st.markdown("### ⚠️ Overdue")
        if overdue:
            for hw in overdue:
                days_late = abs(days_until(hw['due_date']))
                st.markdown(f"""
                <div class="homework-card" style="border-left-color: #e74c3c;">
                    <strong class="overdue">{hw['title']}</strong><br>
                    <span class="subject-badge" style="background-color: {hw['subject_colour']};">{hw['subject_name']}</span>
                    <span class="priority-high">{days_late} days late</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-msg">Nothing overdue!</div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🃏 Flashcards & SRS")

        # Get SRS data
        srs_data = db.get_srs_notification_data()
        fc_overdue = srs_data['cards_overdue']
        streak = srs_data['streak']

        if fc_due > 0 or fc_overdue > 0:
            # Main alert
            alert_color = "#e74c3c" if fc_overdue > 0 else "#f39c12"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {alert_color}22, {alert_color}11);
                        border-left: 4px solid {alert_color};
                        padding: 12px 15px;
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 10px;">
                <strong style="color: {alert_color};">{fc_due} cards due</strong>
                {f"<span style='color: #e74c3c; margin-left: 10px;'>({fc_overdue} overdue!)</span>" if fc_overdue > 0 else ""}
            </div>
            """, unsafe_allow_html=True)

            # Streak display
            if streak > 0:
                st.markdown(f"""
                <div style="background: #e67e2211; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    🔥 <strong>{streak}-day streak</strong> - Don't break it!
                </div>
                """, unsafe_allow_html=True)

            if st.button("🎯 Start Review", key="dash_review", type="primary"):
                st.session_state.selected_page = "Flashcards"
                st.session_state.review_mode = True
                st.rerun()
        else:
            st.markdown("""
            <div class="success-msg">All caught up!</div>
            """, unsafe_allow_html=True)
            if streak > 0:
                st.markdown(f"""
                <div style="background: #2ecc7122; padding: 8px 12px; border-radius: 6px;">
                    🔥 <strong>{streak}-day streak</strong> - Great job!
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 📅 Upcoming Exams")
        if exams:
            for exam in exams[:3]:
                days = days_until(exam['exam_date'])
                urgency_class = "priority-high" if days <= 7 else ("priority-medium" if days <= 14 else "priority-low")
                st.markdown(f"""
                <div class="homework-card" style="border-left-color: {exam['subject_colour']};">
                    <strong>{exam['name']}</strong><br>
                    <span class="subject-badge" style="background-color: {exam['subject_colour']};">{exam['subject_name']}</span>
                    <span class="{urgency_class}">{days} days</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">No exams in the next 30 days</div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # This week's homework
    st.subheader("📅 This Week's Homework")
    week_homework = db.get_homework_due_this_week()

    if week_homework:
        for hw in week_homework:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{hw['title']}**")
                st.caption(f"{hw['subject_name']}")
            with col2:
                st.markdown(format_due_date(hw['due_date']))
            with col3:
                if st.button("✓ Done", key=f"dash_done_{hw['id']}"):
                    db.mark_homework_complete(hw['id'])
                    st.rerun()
            st.markdown("---")
    else:
        st.success("No homework due this week! 🎉")
