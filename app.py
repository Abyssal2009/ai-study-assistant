"""
Study Assistant - Main Application
A simple but powerful study tool for GCSE students.

Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date, datetime, timedelta
import database as db

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }

    /* Card-like containers */
    .stExpander {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }

    /* Priority badges */
    .priority-high {
        background-color: #e74c3c;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    .priority-medium {
        background-color: #f39c12;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    .priority-low {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }

    /* Overdue styling */
    .overdue {
        color: #e74c3c;
        font-weight: bold;
    }

    /* Stats cards */
    .stat-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    /* Timer display */
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALISATION
# =============================================================================

# Timer state
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'timer_start_time' not in st.session_state:
    st.session_state.timer_start_time = None
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 25  # Default 25 minutes
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'timer_subject_id' not in st.session_state:
    st.session_state.timer_subject_id = None

# Flashcard review session state
if 'review_mode' not in st.session_state:
    st.session_state.review_mode = False
if 'review_cards' not in st.session_state:
    st.session_state.review_cards = []
if 'review_index' not in st.session_state:
    st.session_state.review_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'review_subject_id' not in st.session_state:
    st.session_state.review_subject_id = None
if 'cards_reviewed_session' not in st.session_state:
    st.session_state.cards_reviewed_session = 0
if 'cards_correct_session' not in st.session_state:
    st.session_state.cards_correct_session = 0


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def days_until(target_date) -> int:
    """Calculate days until a target date."""
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    return (target_date - date.today()).days


def format_due_date(due_date) -> str:
    """Format a due date with helpful text."""
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)

    days = days_until(due_date)

    if days < 0:
        return f"**OVERDUE** ({abs(days)} days ago)"
    elif days == 0:
        return "**Due TODAY**"
    elif days == 1:
        return "Due tomorrow"
    elif days <= 7:
        return f"Due in {days} days"
    else:
        return f"Due {due_date.strftime('%d %B %Y')}"


def get_priority_badge(priority: str) -> str:
    """Return HTML for a priority badge."""
    colours = {
        'high': '#e74c3c',
        'medium': '#f39c12',
        'low': '#27ae60'
    }
    colour = colours.get(priority, '#95a5a6')
    return f'<span style="background-color: {colour}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{priority.upper()}</span>'


# =============================================================================
# SIDEBAR - NAVIGATION
# =============================================================================

with st.sidebar:
    st.title("📚 Study Assistant")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["Dashboard", "What Next?", "Homework", "Exams", "Flashcards", "Focus Timer", "Subjects", "Statistics", "Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Quick stats in sidebar
    stats = db.get_homework_stats()
    st.metric("Pending Homework", stats['pending'])
    if stats['overdue'] > 0:
        st.metric("Overdue", stats['overdue'], delta=f"-{stats['overdue']}", delta_color="inverse")

    # Flashcard stats
    flashcard_due = db.get_due_flashcards_count()
    st.metric("Flashcards Due", flashcard_due)

    focus_today = db.get_total_focus_minutes_today()
    st.metric("Focus Today", f"{focus_today} min")


# =============================================================================
# DASHBOARD PAGE
# =============================================================================

if page == "Dashboard":
    st.title("📊 Dashboard")
    st.markdown(f"**Today is {date.today().strftime('%A, %d %B %Y')}**")

    # Check if subjects exist
    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("👋 **Welcome!** You haven't added any subjects yet. Go to the **Subjects** page to add your GCSE subjects first.")
        st.stop()

    # TOP RECOMMENDATION - What should I study next?
    top_rec = db.get_top_recommendation()
    if top_rec:
        urgency_colors = {
            'critical': '#e74c3c',
            'high': '#e67e22',
            'medium': '#f39c12',
            'low': '#3498db'
        }
        urgency_icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📌',
            'low': '💡'
        }
        color = urgency_colors.get(top_rec['urgency'], '#3498db')
        icon = urgency_icons.get(top_rec['urgency'], '📌')

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

    # Four columns for key info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("📋 Due Today")
        due_today = db.get_homework_due_today()
        if due_today:
            for hw in due_today:
                st.markdown(f"- **{hw['subject_name']}**: {hw['title']}")
        else:
            st.success("Nothing due today!")

    with col2:
        st.subheader("⚠️ Overdue")
        overdue = db.get_overdue_homework()
        if overdue:
            for hw in overdue:
                days_late = abs(days_until(hw['due_date']))
                st.markdown(f"- **{hw['subject_name']}**: {hw['title']} ({days_late} days late)")
        else:
            st.success("Nothing overdue!")

    with col3:
        st.subheader("🃏 Flashcards Due")
        fc_due = db.get_due_flashcards_count()
        if fc_due > 0:
            st.warning(f"**{fc_due} cards** need review!")
            if st.button("Start Review", key="dash_review"):
                st.switch_page = "Flashcards"  # Note: This won't work directly, user needs to navigate
                st.info("Go to Flashcards page to review")
        else:
            st.success("All caught up!")

    with col4:
        st.subheader("📅 Upcoming Exams")
        exams = db.get_exams_this_month()
        if exams:
            for exam in exams[:3]:  # Show top 3
                days = days_until(exam['exam_date'])
                st.markdown(f"- **{exam['subject_name']}**: {exam['name']} ({days} days)")
        else:
            st.info("No exams in the next 30 days")

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


# =============================================================================
# WHAT NEXT? PAGE - Study Recommendations
# =============================================================================

elif page == "What Next?":
    st.title("🎯 What Should I Study Next?")
    st.markdown("**Personalised recommendations based on your deadlines, exams, and flashcards.**")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Get all recommendations
    recommendations = db.get_study_recommendations(limit=10)

    if not recommendations:
        st.success("""
        🎉 **Amazing! You're all caught up!**

        No urgent tasks right now. Here are some suggestions:
        - Add flashcards for topics you're learning
        - Start a focus session to review a subject
        - Check if you have any upcoming exams to prepare for
        """)
    else:
        # Top recommendation (highlighted)
        top_rec = recommendations[0]

        urgency_colors = {
            'critical': '#e74c3c',
            'high': '#e67e22',
            'medium': '#f39c12',
            'low': '#3498db'
        }
        urgency_labels = {
            'critical': '🚨 CRITICAL',
            'high': '⚠️ HIGH PRIORITY',
            'medium': '📌 MEDIUM',
            'low': '💡 SUGGESTED'
        }
        type_icons = {
            'homework': '📝',
            'flashcards': '🃏',
            'exam_prep': '📚',
            'review': '🔄'
        }

        color = urgency_colors.get(top_rec['urgency'], '#3498db')

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}33, {color}11);
                    border: 2px solid {color};
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="background: {color}; color: white; padding: 4px 12px;
                            border-radius: 20px; font-size: 12px; font-weight: bold;">
                    {urgency_labels.get(top_rec['urgency'], 'SUGGESTED')}
                </span>
                <span style="color: #666;">Priority Score: {top_rec['priority_score']}</span>
            </div>
            <h2 style="margin: 15px 0 10px 0;">{type_icons.get(top_rec['type'], '📌')} {top_rec['title']}</h2>
            <p style="font-size: 1.1em; margin: 10px 0;">
                <strong style="color: {top_rec.get('subject_colour', '#333')};">{top_rec['subject_name']}</strong>
            </p>
            <p style="margin: 10px 0; color: #666; font-size: 1.1em;">{top_rec['reason']}</p>
            <p style="margin: 15px 0 0 0; padding: 10px;
                     background: rgba(255,255,255,0.5); border-radius: 6px;">
                <strong>Action:</strong> {top_rec['action']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick action buttons for top recommendation
        col1, col2, col3 = st.columns(3)
        with col1:
            if top_rec['type'] == 'homework' and st.button("✅ Mark as Done", type="primary", use_container_width=True):
                db.mark_homework_complete(top_rec['item_id'])
                st.success("Marked as complete!")
                st.rerun()
        with col2:
            if top_rec['type'] == 'flashcards' and st.button("🃏 Start Review", type="primary", use_container_width=True):
                st.info("Go to Flashcards page to start reviewing")
        with col3:
            if st.button("⏱️ Start Focus Timer", use_container_width=True):
                st.info("Go to Focus Timer page to start a session")

        # Other recommendations
        if len(recommendations) > 1:
            st.markdown("---")
            st.subheader("📋 Other Recommendations")

            for rec in recommendations[1:]:
                color = urgency_colors.get(rec['urgency'], '#3498db')
                icon = type_icons.get(rec['type'], '📌')

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"""
                    <div style="border-left: 3px solid {color}; padding-left: 15px; margin: 10px 0;">
                        <strong>{icon} {rec['title']}</strong><br>
                        <span style="color: {rec.get('subject_colour', '#666')};">{rec['subject_name']}</span> •
                        <span style="color: #888;">{rec['reason']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if rec['type'] == 'homework':
                        if st.button("✅ Done", key=f"done_rec_{rec['item_id']}"):
                            db.mark_homework_complete(rec['item_id'])
                            st.rerun()

    # Subject Priority Overview
    st.markdown("---")
    st.subheader("📊 Subject Priority Overview")
    st.caption("Which subjects need the most attention right now?")

    subject_priorities = db.get_subject_priority_scores()

    if subject_priorities:
        # Find max score for scaling
        max_score = max(s['priority_score'] for s in subject_priorities) if subject_priorities else 1
        if max_score == 0:
            max_score = 1

        for subj in subject_priorities:
            col1, col2, col3 = st.columns([2, 3, 2])

            with col1:
                st.markdown(f"**{subj['subject_name']}**")

            with col2:
                # Progress bar showing relative priority
                progress = subj['priority_score'] / max_score if max_score > 0 else 0
                st.progress(progress)

            with col3:
                if subj['reasons']:
                    st.caption(", ".join(subj['reasons']))
                else:
                    st.caption("No urgent tasks")

    # How the scoring works
    with st.expander("ℹ️ How does the recommendation system work?"):
        st.markdown("""
        The system calculates priority scores based on multiple factors:

        | Factor | Points |
        |--------|--------|
        | Overdue homework | 100+ (more days = higher) |
        | Homework due today | 80 |
        | Homework due tomorrow | 60 |
        | Exam within 7 days | 70-100 |
        | Exam within 14 days | 50 |
        | Flashcards due | 50-75 (based on count) |
        | Subject not studied in days | 5 per day (max 30) |

        Tasks are sorted by total score, so the most urgent always appears first.
        Complete tasks to see your next priority!
        """)


# =============================================================================
# HOMEWORK PAGE
# =============================================================================

elif page == "Homework":
    st.title("📝 Homework Tracker")

    # Add new homework
    with st.expander("➕ Add New Homework", expanded=False):
        subjects = db.get_all_subjects()

        if not subjects:
            st.warning("Please add subjects first in the Subjects page.")
        else:
            with st.form("add_homework_form"):
                col1, col2 = st.columns(2)

                with col1:
                    hw_subject = st.selectbox(
                        "Subject",
                        options=subjects,
                        format_func=lambda x: x['name']
                    )
                    hw_title = st.text_input("Title", placeholder="e.g., Chapter 5 questions")

                with col2:
                    hw_due = st.date_input("Due Date", value=date.today() + timedelta(days=1))
                    hw_priority = st.selectbox("Priority", ["medium", "high", "low"])

                hw_description = st.text_area("Description (optional)", placeholder="Any additional details...")

                if st.form_submit_button("Add Homework"):
                    if hw_title and hw_subject:
                        db.add_homework(
                            subject_id=hw_subject['id'],
                            title=hw_title,
                            due_date=hw_due,
                            description=hw_description,
                            priority=hw_priority
                        )
                        st.success(f"Added: {hw_title}")
                        st.rerun()
                    else:
                        st.error("Please fill in the title and select a subject.")

    # Filter options
    col1, col2 = st.columns([3, 1])
    with col2:
        show_completed = st.checkbox("Show completed", value=False)

    # Display homework
    homework_list = db.get_all_homework(include_completed=show_completed)

    if not homework_list:
        st.info("No homework to display. Add some above!")
    else:
        # Group by urgency
        overdue = []
        due_today = []
        due_soon = []
        later = []
        completed = []

        for hw in homework_list:
            if hw['completed']:
                completed.append(hw)
            else:
                days = days_until(hw['due_date'])
                if days < 0:
                    overdue.append(hw)
                elif days == 0:
                    due_today.append(hw)
                elif days <= 3:
                    due_soon.append(hw)
                else:
                    later.append(hw)

        # Display each group
        def display_homework_item(hw):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                if hw['completed']:
                    st.markdown(f"~~{hw['title']}~~")
                else:
                    st.markdown(f"**{hw['title']}**")
                st.caption(f"🏷️ {hw['subject_name']}")
                if hw['description']:
                    st.caption(hw['description'])

            with col2:
                st.markdown(format_due_date(hw['due_date']))
                st.caption(f"Priority: {hw['priority'].upper()}")

            with col3:
                if hw['completed']:
                    if st.button("↩️ Undo", key=f"undo_{hw['id']}"):
                        db.mark_homework_incomplete(hw['id'])
                        st.rerun()
                else:
                    if st.button("✓ Done", key=f"done_{hw['id']}"):
                        db.mark_homework_complete(hw['id'])
                        st.rerun()

            with col4:
                if st.button("🗑️", key=f"del_{hw['id']}"):
                    db.delete_homework(hw['id'])
                    st.rerun()

        if overdue:
            st.error(f"⚠️ OVERDUE ({len(overdue)} items)")
            for hw in overdue:
                display_homework_item(hw)
                st.markdown("---")

        if due_today:
            st.warning(f"📅 DUE TODAY ({len(due_today)} items)")
            for hw in due_today:
                display_homework_item(hw)
                st.markdown("---")

        if due_soon:
            st.info(f"⏰ DUE SOON - Next 3 days ({len(due_soon)} items)")
            for hw in due_soon:
                display_homework_item(hw)
                st.markdown("---")

        if later:
            st.subheader(f"📚 Coming Up ({len(later)} items)")
            for hw in later:
                display_homework_item(hw)
                st.markdown("---")

        if completed and show_completed:
            st.subheader(f"✅ Completed ({len(completed)} items)")
            for hw in completed:
                display_homework_item(hw)
                st.markdown("---")


# =============================================================================
# EXAMS PAGE
# =============================================================================

elif page == "Exams":
    st.title("📅 Exam Calendar")

    # Add new exam
    with st.expander("➕ Add New Exam", expanded=False):
        subjects = db.get_all_subjects()

        if not subjects:
            st.warning("Please add subjects first in the Subjects page.")
        else:
            with st.form("add_exam_form"):
                col1, col2 = st.columns(2)

                with col1:
                    exam_subject = st.selectbox(
                        "Subject",
                        options=subjects,
                        format_func=lambda x: x['name']
                    )
                    exam_name = st.text_input("Exam Name", placeholder="e.g., Paper 1 - Biology")

                with col2:
                    exam_date = st.date_input("Exam Date")
                    exam_duration = st.number_input("Duration (minutes)", min_value=0, value=60)

                col1, col2 = st.columns(2)
                with col1:
                    exam_location = st.text_input("Location (optional)", placeholder="e.g., Main Hall")
                with col2:
                    exam_notes = st.text_area("Notes (optional)", placeholder="Topics to revise...")

                if st.form_submit_button("Add Exam"):
                    if exam_name and exam_subject:
                        db.add_exam(
                            subject_id=exam_subject['id'],
                            name=exam_name,
                            exam_date=exam_date,
                            duration_minutes=exam_duration if exam_duration > 0 else None,
                            location=exam_location,
                            notes=exam_notes
                        )
                        st.success(f"Added exam: {exam_name}")
                        st.rerun()
                    else:
                        st.error("Please fill in the exam name and select a subject.")

    # Display exams
    exams = db.get_all_exams()

    if not exams:
        st.info("No upcoming exams. Add some above!")
    else:
        for exam in exams:
            days = days_until(exam['exam_date'])
            exam_date_obj = date.fromisoformat(exam['exam_date']) if isinstance(exam['exam_date'], str) else exam['exam_date']

            # Colour based on urgency
            if days <= 7:
                colour = "🔴"
            elif days <= 30:
                colour = "🟡"
            else:
                colour = "🟢"

            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"{colour} **{exam['name']}**")
                st.caption(f"📚 {exam['subject_name']}")
                if exam['location']:
                    st.caption(f"📍 {exam['location']}")
                if exam['notes']:
                    st.caption(f"📝 {exam['notes']}")

            with col2:
                st.markdown(f"**{exam_date_obj.strftime('%A, %d %B %Y')}**")
                if days == 0:
                    st.markdown("**TODAY!**")
                elif days == 1:
                    st.markdown("**Tomorrow!**")
                else:
                    st.markdown(f"In **{days} days**")
                if exam['duration_minutes']:
                    st.caption(f"⏱️ {exam['duration_minutes']} minutes")

            with col3:
                if st.button("🗑️", key=f"del_exam_{exam['id']}"):
                    db.delete_exam(exam['id'])
                    st.rerun()

            st.markdown("---")


# =============================================================================
# FLASHCARDS PAGE
# =============================================================================

elif page == "Flashcards":
    st.title("🃏 Flashcards")

    subjects = db.get_all_subjects()

    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Check if we're in review mode
    if st.session_state.review_mode:
        # =================================================================
        # REVIEW MODE - Active flashcard review session
        # =================================================================
        st.subheader("📖 Review Session")

        # Get current card
        if st.session_state.review_index < len(st.session_state.review_cards):
            current_card = st.session_state.review_cards[st.session_state.review_index]

            # Progress bar
            progress = st.session_state.review_index / len(st.session_state.review_cards)
            st.progress(progress)
            st.caption(f"Card {st.session_state.review_index + 1} of {len(st.session_state.review_cards)}")

            # Display card
            st.markdown(f"**Subject:** {current_card['subject_name']}")
            if current_card['topic']:
                st.caption(f"Topic: {current_card['topic']}")

            st.markdown("---")

            # Question
            st.markdown("### Question")
            st.markdown(f"**{current_card['question']}**")

            st.markdown("---")

            # Answer (show/hide)
            if not st.session_state.show_answer:
                if st.button("🔍 Show Answer", type="primary", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()
            else:
                st.markdown("### Answer")
                st.success(current_card['answer'])

                st.markdown("---")
                st.markdown("**How well did you remember?**")

                # Quality rating buttons with descriptions
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**😫 Forgot**")
                    if st.button("Again (0)", key="q0", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=0)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

                    if st.button("Hard (1)", key="q1", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=1)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col2:
                    st.markdown("**😐 Struggled**")
                    if st.button("Difficult (2)", key="q2", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=2)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

                    if st.button("Okay (3)", key="q3", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=3)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.cards_correct_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col3:
                    st.markdown("**😊 Remembered**")
                    if st.button("Good (4)", key="q4", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=4)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.cards_correct_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

                    if st.button("Perfect (5)", key="q5", use_container_width=True):
                        db.review_flashcard(current_card['id'], quality=5)
                        st.session_state.cards_reviewed_session += 1
                        st.session_state.cards_correct_session += 1
                        st.session_state.review_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

            st.markdown("---")
            if st.button("❌ End Review Session"):
                st.session_state.review_mode = False
                st.session_state.review_cards = []
                st.session_state.review_index = 0
                st.session_state.show_answer = False
                st.rerun()

        else:
            # Review session complete!
            st.balloons()
            st.success("🎉 Review session complete!")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cards Reviewed", st.session_state.cards_reviewed_session)
            with col2:
                if st.session_state.cards_reviewed_session > 0:
                    accuracy = round((st.session_state.cards_correct_session / st.session_state.cards_reviewed_session) * 100)
                    st.metric("Accuracy", f"{accuracy}%")

            if st.button("🏠 Back to Flashcards", type="primary"):
                st.session_state.review_mode = False
                st.session_state.review_cards = []
                st.session_state.review_index = 0
                st.session_state.show_answer = False
                st.session_state.cards_reviewed_session = 0
                st.session_state.cards_correct_session = 0
                st.rerun()

    else:
        # =================================================================
        # NORMAL MODE - Flashcard management
        # =================================================================

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📖 Review", "➕ Add Cards", "📋 All Cards"])

        # -----------------------------------------------------------------
        # TAB 1: Review due cards
        # -----------------------------------------------------------------
        with tab1:
            st.subheader("Cards Due for Review")

            # Get flashcard stats
            fc_stats = db.get_flashcard_stats()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Due Today", fc_stats['due_today'])
            with col2:
                st.metric("Total Cards", fc_stats['total'])
            with col3:
                st.metric("Reviewed Today", fc_stats['reviewed_today'])
            with col4:
                st.metric("7-Day Accuracy", f"{fc_stats['accuracy_7_days']}%")

            st.markdown("---")

            # Subject filter for review
            due_by_subject = db.get_due_flashcards_by_subject()

            if not due_by_subject and fc_stats['due_today'] == 0:
                st.success("🎉 No cards due for review! Come back later or add more cards.")
            else:
                st.markdown("**Start a review session:**")

                # Option to review all subjects
                all_due = db.get_due_flashcards()
                if all_due:
                    if st.button(f"📚 Review All Subjects ({len(all_due)} cards)", type="primary", use_container_width=True):
                        st.session_state.review_mode = True
                        st.session_state.review_cards = [dict(card) for card in all_due]
                        st.session_state.review_index = 0
                        st.session_state.show_answer = False
                        st.session_state.cards_reviewed_session = 0
                        st.session_state.cards_correct_session = 0
                        st.rerun()

                st.markdown("**Or review by subject:**")

                # Review by subject
                for subj in due_by_subject:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{subj['name']}** - {subj['due_count']} cards due")
                    with col2:
                        if st.button("Review", key=f"review_subj_{subj['id']}"):
                            cards = db.get_due_flashcards(subject_id=subj['id'])
                            st.session_state.review_mode = True
                            st.session_state.review_cards = [dict(card) for card in cards]
                            st.session_state.review_index = 0
                            st.session_state.show_answer = False
                            st.session_state.review_subject_id = subj['id']
                            st.session_state.cards_reviewed_session = 0
                            st.session_state.cards_correct_session = 0
                            st.rerun()

        # -----------------------------------------------------------------
        # TAB 2: Add new cards
        # -----------------------------------------------------------------
        with tab2:
            st.subheader("Add New Flashcard")

            with st.form("add_flashcard_form", clear_on_submit=True):
                fc_subject = st.selectbox(
                    "Subject",
                    options=subjects,
                    format_func=lambda x: x['name']
                )

                fc_topic = st.text_input("Topic (optional)", placeholder="e.g., Cell Biology, Algebra")

                fc_question = st.text_area(
                    "Question",
                    placeholder="What is the powerhouse of the cell?",
                    height=100
                )

                fc_answer = st.text_area(
                    "Answer",
                    placeholder="The mitochondria",
                    height=100
                )

                if st.form_submit_button("➕ Add Flashcard", type="primary"):
                    if fc_question and fc_answer and fc_subject:
                        db.add_flashcard(
                            subject_id=fc_subject['id'],
                            question=fc_question.strip(),
                            answer=fc_answer.strip(),
                            topic=fc_topic.strip()
                        )
                        st.success("Flashcard added! It's ready for review.")
                        st.rerun()
                    else:
                        st.error("Please fill in both question and answer.")

            # Quick add multiple cards
            st.markdown("---")
            st.subheader("Quick Add Multiple Cards")
            st.caption("Add multiple cards at once. Format: Question | Answer (one per line)")

            bulk_subject = st.selectbox(
                "Subject for bulk add",
                options=subjects,
                format_func=lambda x: x['name'],
                key="bulk_subject"
            )

            bulk_topic = st.text_input("Topic for all cards (optional)", key="bulk_topic")

            bulk_cards = st.text_area(
                "Cards (one per line)",
                placeholder="What is 2+2? | 4\nCapital of France? | Paris\nH2O is? | Water",
                height=150
            )

            if st.button("➕ Add All Cards"):
                if bulk_cards.strip():
                    lines = bulk_cards.strip().split('\n')
                    added = 0
                    for line in lines:
                        if '|' in line:
                            parts = line.split('|', 1)
                            if len(parts) == 2:
                                q = parts[0].strip()
                                a = parts[1].strip()
                                if q and a:
                                    db.add_flashcard(
                                        subject_id=bulk_subject['id'],
                                        question=q,
                                        answer=a,
                                        topic=bulk_topic.strip()
                                    )
                                    added += 1
                    if added > 0:
                        st.success(f"Added {added} flashcards!")
                        st.rerun()
                    else:
                        st.error("No valid cards found. Use format: Question | Answer")
                else:
                    st.error("Please enter at least one card.")

        # -----------------------------------------------------------------
        # TAB 3: View all cards
        # -----------------------------------------------------------------
        with tab3:
            st.subheader("All Flashcards")

            # Filter by subject
            view_subject = st.selectbox(
                "Filter by subject",
                options=[None] + list(subjects),
                format_func=lambda x: "All Subjects" if x is None else x['name'],
                key="view_subject"
            )

            subject_id = view_subject['id'] if view_subject else None
            all_cards = db.get_all_flashcards(subject_id=subject_id)

            if not all_cards:
                st.info("No flashcards found. Add some in the 'Add Cards' tab!")
            else:
                st.caption(f"Showing {len(all_cards)} cards")

                for card in all_cards:
                    with st.expander(f"**{card['question'][:50]}{'...' if len(card['question']) > 50 else ''}**"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**Subject:** {card['subject_name']}")
                            if card['topic']:
                                st.caption(f"Topic: {card['topic']}")

                            st.markdown("**Question:**")
                            st.markdown(card['question'])

                            st.markdown("**Answer:**")
                            st.success(card['answer'])

                            # Card stats
                            st.markdown("---")
                            st.caption(f"📊 Reviewed {card['times_reviewed']} times | "
                                      f"Accuracy: {round(card['times_correct']/card['times_reviewed']*100) if card['times_reviewed'] > 0 else 0}% | "
                                      f"Next review: {card['next_review']}")

                        with col2:
                            if st.button("🗑️ Delete", key=f"del_fc_{card['id']}"):
                                db.delete_flashcard(card['id'])
                                st.rerun()

                            if st.button("🔄 Reset", key=f"reset_fc_{card['id']}"):
                                db.reset_flashcard(card['id'])
                                st.success("Card reset!")
                                st.rerun()


# =============================================================================
# FOCUS TIMER PAGE
# =============================================================================

elif page == "Focus Timer":
    st.title("⏱️ Focus Timer")
    st.markdown("Use the Pomodoro technique: **25 minutes focus**, then **5 minutes break**.")

    subjects = db.get_all_subjects()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Start a Focus Session")

        # Timer settings
        timer_subject = st.selectbox(
            "What are you studying?",
            options=[None] + list(subjects),
            format_func=lambda x: "General / No subject" if x is None else x['name']
        )

        timer_duration = st.slider(
            "Session length (minutes)",
            min_value=5,
            max_value=60,
            value=25,
            step=5
        )

        # Timer controls
        if not st.session_state.timer_running:
            if st.button("▶️ Start Focus Session", type="primary", use_container_width=True):
                subject_id = timer_subject['id'] if timer_subject else None
                session_id = db.start_focus_session(subject_id, timer_duration)
                st.session_state.timer_running = True
                st.session_state.timer_start_time = datetime.now()
                st.session_state.timer_duration = timer_duration
                st.session_state.current_session_id = session_id
                st.session_state.timer_subject_id = subject_id
                st.rerun()
        else:
            # Timer is running
            elapsed = datetime.now() - st.session_state.timer_start_time
            elapsed_minutes = elapsed.total_seconds() / 60
            remaining = st.session_state.timer_duration - elapsed_minutes

            if remaining > 0:
                mins = int(remaining)
                secs = int((remaining - mins) * 60)
                st.markdown(f"<h1 style='text-align: center; font-family: monospace;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                st.progress(elapsed_minutes / st.session_state.timer_duration)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("⏹️ End Session", use_container_width=True):
                        db.end_focus_session(st.session_state.current_session_id, completed=True)
                        st.session_state.timer_running = False
                        st.success("Session completed! Well done! 🎉")
                        st.rerun()
                with col_b:
                    if st.button("❌ Cancel", use_container_width=True):
                        db.end_focus_session(st.session_state.current_session_id, completed=False)
                        st.session_state.timer_running = False
                        st.rerun()

                # Auto-refresh to update timer
                st.markdown("""
                <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                </script>
                """, unsafe_allow_html=True)
            else:
                # Timer finished
                st.balloons()
                st.success("🎉 Time's up! Great focus session!")
                db.end_focus_session(st.session_state.current_session_id, completed=True)
                st.session_state.timer_running = False

                if st.button("Start Another Session", type="primary"):
                    st.rerun()

    with col2:
        st.subheader("Today's Progress")

        focus_today = db.get_total_focus_minutes_today()
        focus_week = db.get_total_focus_minutes_this_week()

        st.metric("Focus Time Today", f"{focus_today} minutes")
        st.metric("Focus Time This Week", f"{focus_week} minutes")

        # Today's sessions
        st.markdown("---")
        st.markdown("**Today's Sessions:**")
        sessions_today = db.get_focus_sessions_today()

        if sessions_today:
            for session in sessions_today:
                subject_name = session['subject_name'] if session['subject_name'] else "General"
                status = "✅" if session['completed'] else "❌"
                minutes = session['actual_minutes'] if session['actual_minutes'] else "In progress"
                st.markdown(f"- {status} {subject_name}: {minutes} min")
        else:
            st.caption("No sessions yet today. Start one!")


# =============================================================================
# SUBJECTS PAGE
# =============================================================================

elif page == "Subjects":
    st.title("📚 Manage Subjects")

    # Predefined GCSE subjects with colours
    default_subjects = [
        ("Additional Maths", "#9b59b6"),
        ("Biology", "#27ae60"),
        ("Business Studies", "#e67e22"),
        ("Chemistry", "#3498db"),
        ("English Language", "#e74c3c"),
        ("English Literature", "#c0392b"),
        ("Food and Nutrition", "#f39c12"),
        ("Geography", "#1abc9c"),
        ("Mathematics", "#2980b9"),
        ("Physical Education", "#d35400"),
        ("Physics", "#8e44ad"),
    ]

    # Quick add all subjects
    subjects = db.get_all_subjects()
    if not subjects:
        st.info("You haven't added any subjects yet. Click below to add all your GCSE subjects at once!")
        if st.button("➕ Add All My GCSE Subjects", type="primary"):
            for name, colour in default_subjects:
                try:
                    db.add_subject(name, colour)
                except:
                    pass  # Subject might already exist
            st.success("Added all subjects!")
            st.rerun()

    # Add single subject
    with st.expander("➕ Add Individual Subject"):
        with st.form("add_subject_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                subject_name = st.text_input("Subject Name", placeholder="e.g., History")
            with col2:
                subject_colour = st.color_picker("Colour", value="#3498db")

            if st.form_submit_button("Add Subject"):
                if subject_name:
                    try:
                        db.add_subject(subject_name, subject_colour)
                        st.success(f"Added: {subject_name}")
                        st.rerun()
                    except:
                        st.error("Subject already exists.")
                else:
                    st.error("Please enter a subject name.")

    # Display subjects
    st.markdown("---")
    st.subheader("Your Subjects")

    subjects = db.get_all_subjects()

    if subjects:
        for subject in subjects:
            col1, col2, col3 = st.columns([1, 6, 1])

            with col1:
                st.markdown(f"<div style='width: 30px; height: 30px; background-color: {subject['colour']}; border-radius: 5px;'></div>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"**{subject['name']}**")

            with col3:
                if st.button("🗑️", key=f"del_sub_{subject['id']}"):
                    db.delete_subject(subject['id'])
                    st.rerun()
    else:
        st.info("No subjects added yet.")


# =============================================================================
# STATISTICS PAGE
# =============================================================================

elif page == "Statistics":
    st.title("📊 Statistics")

    # Homework stats
    st.subheader("📝 Homework")
    stats = db.get_homework_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pending Homework", stats['pending'])

    with col2:
        st.metric("Completed This Week", stats['completed_this_week'])

    with col3:
        st.metric("Overdue Items", stats['overdue'])

    with col4:
        focus_week = db.get_total_focus_minutes_this_week()
        hours = focus_week // 60
        mins = focus_week % 60
        st.metric("Study Time This Week", f"{hours}h {mins}m")

    st.markdown("---")

    # Flashcard stats
    st.subheader("🃏 Flashcards")
    fc_stats = db.get_flashcard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Cards", fc_stats['total'])

    with col2:
        st.metric("Due Today", fc_stats['due_today'])

    with col3:
        st.metric("Reviewed Today", fc_stats['reviewed_today'])

    with col4:
        st.metric("7-Day Accuracy", f"{fc_stats['accuracy_7_days']}%")

    # Card status breakdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("New Cards", fc_stats['new'], help="Cards never reviewed")
    with col2:
        st.metric("Learning", fc_stats['learning'], help="Cards with interval < 21 days")
    with col3:
        st.metric("Mature", fc_stats['mature'], help="Cards with interval >= 21 days")

    # Review history
    st.markdown("---")
    st.subheader("📈 Review History (Last 7 Days)")
    review_history = db.get_review_history(days=7)

    if review_history:
        for day in review_history:
            accuracy = round((day['correct'] / day['total_reviews']) * 100) if day['total_reviews'] > 0 else 0
            st.markdown(f"**{day['review_date']}**: {day['total_reviews']} reviews, {accuracy}% correct")
    else:
        st.info("No review history yet. Start reviewing flashcards!")

    st.markdown("---")

    # Focus time by day (simple version)
    st.subheader("⏱️ Recent Focus Sessions")
    sessions = db.get_focus_sessions_today()

    if sessions:
        for session in sessions:
            subject = session['subject_name'] if session['subject_name'] else "General"
            status = "Completed" if session['completed'] else "Cancelled"
            minutes = session['actual_minutes'] if session['actual_minutes'] else 0
            st.markdown(f"- **{subject}**: {minutes} minutes ({status})")
    else:
        st.info("No focus sessions today. Start one on the Focus Timer page!")


# =============================================================================
# SETTINGS PAGE
# =============================================================================

elif page == "Settings":
    st.title("⚙️ Settings")

    # Email Settings
    st.subheader("📧 Email Reminders")

    st.markdown("""
    Set up daily email reminders to receive a summary of your homework, exams, and flashcards each morning.

    **How it works:**
    1. Configure your email settings below
    2. Test the email to make sure it works
    3. Set up the daily scheduler to run automatically
    """)

    # Try to load current config
    try:
        import config
        current_sender = config.EMAIL_SENDER
        current_recipient = config.EMAIL_RECIPIENT
        has_password = config.EMAIL_PASSWORD != "your-app-password-here"
    except:
        current_sender = ""
        current_recipient = ""
        has_password = False

    with st.expander("📝 Email Configuration", expanded=True):
        st.warning("""
        **For Gmail users:** You must use an App Password, not your regular password.

        To get an App Password:
        1. Go to [Google Account Security](https://myaccount.google.com/security)
        2. Enable 2-Step Verification if not already enabled
        3. Search for "App passwords" and create one for "Mail"
        4. Use that 16-character password below
        """)

        with st.form("email_config_form"):
            email_sender = st.text_input(
                "Your Email Address",
                value=current_sender if current_sender != "your.email@gmail.com" else "",
                placeholder="yourname@gmail.com"
            )

            email_password = st.text_input(
                "App Password",
                type="password",
                placeholder="Your 16-character app password",
                help="For Gmail, use an App Password, not your regular password"
            )

            email_recipient = st.text_input(
                "Send Reminders To (can be same as above)",
                value=current_recipient if current_recipient != "your.email@gmail.com" else "",
                placeholder="yourname@gmail.com"
            )

            if st.form_submit_button("💾 Save Email Settings"):
                if email_sender and email_password:
                    # Save to config file
                    config_content = f'''"""
Configuration file for the Study Assistant.
Edit these settings to configure email reminders.
"""

# Email Settings
EMAIL_SENDER = "{email_sender}"
EMAIL_PASSWORD = "{email_password}"
EMAIL_RECIPIENT = "{email_recipient if email_recipient else email_sender}"

# SMTP server settings (Gmail defaults)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Reminder settings
REMINDER_TIME = "07:00"
INCLUDE_HOMEWORK_DUE_TODAY = True
INCLUDE_HOMEWORK_DUE_TOMORROW = True
INCLUDE_HOMEWORK_DUE_THIS_WEEK = True
INCLUDE_OVERDUE_HOMEWORK = True
INCLUDE_UPCOMING_EXAMS = True
INCLUDE_FLASHCARDS_DUE = True
INCLUDE_STUDY_STATS = True
'''
                    try:
                        from pathlib import Path
                        config_path = Path(__file__).parent / "config.py"
                        with open(config_path, 'w') as f:
                            f.write(config_content)
                        st.success("✅ Email settings saved!")
                        st.info("Now click 'Test Email' below to verify it works.")
                    except Exception as e:
                        st.error(f"Error saving config: {e}")
                else:
                    st.error("Please fill in your email address and app password.")

    # Test email
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧪 Test Email")
        if st.button("📤 Send Test Email", type="primary"):
            try:
                # Reload config
                import importlib
                import config
                importlib.reload(config)

                from email_reminder import send_email
                if send_email():
                    st.success("✅ Test email sent! Check your inbox.")
                else:
                    st.error("❌ Failed to send email. Check your settings.")
            except Exception as e:
                st.error(f"Error: {e}")

        if st.button("👁️ Preview Email"):
            try:
                from email_reminder import generate_plain_text
                preview = generate_plain_text()
                st.text_area("Email Preview", preview, height=400)
            except Exception as e:
                st.error(f"Error generating preview: {e}")

    with col2:
        st.subheader("⏰ Schedule Daily Reminder")
        st.markdown("""
        To receive automatic daily emails:

        1. Open the folder: `C:\\Code\\ai-study-assistant`
        2. Right-click `setup_daily_reminder.bat`
        3. Select **"Run as administrator"**
        4. The reminder will run daily at 7:00 AM

        **To change the time:**
        - Open Windows Task Scheduler
        - Find "StudyAssistantReminder"
        - Edit the trigger time
        """)

        if st.button("📂 Open Project Folder"):
            import subprocess
            subprocess.Popen(['explorer', 'C:\\Code\\ai-study-assistant'])

    # Other settings
    st.markdown("---")
    st.subheader("🗄️ Data Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export Data**")
        if st.button("📥 Export All Data to CSV"):
            try:
                import csv
                from pathlib import Path
                export_dir = Path("C:/Code/ai-study-assistant/exports")
                export_dir.mkdir(exist_ok=True)

                # Export homework
                homework = db.get_all_homework(include_completed=True)
                with open(export_dir / "homework.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Subject', 'Title', 'Description', 'Due Date', 'Priority', 'Completed'])
                    for hw in homework:
                        writer.writerow([hw['subject_name'], hw['title'], hw['description'],
                                        hw['due_date'], hw['priority'], 'Yes' if hw['completed'] else 'No'])

                # Export flashcards
                flashcards = db.get_all_flashcards()
                with open(export_dir / "flashcards.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Subject', 'Topic', 'Question', 'Answer', 'Times Reviewed', 'Accuracy'])
                    for card in flashcards:
                        accuracy = round(card['times_correct']/card['times_reviewed']*100) if card['times_reviewed'] > 0 else 0
                        writer.writerow([card['subject_name'], card['topic'], card['question'],
                                        card['answer'], card['times_reviewed'], f"{accuracy}%"])

                st.success(f"✅ Data exported to C:\\Code\\ai-study-assistant\\exports\\")
            except Exception as e:
                st.error(f"Export error: {e}")

    with col2:
        st.markdown("**Database Location**")
        st.code("C:\\Code\\ai-study-assistant\\study.db")
        st.caption("Back up this file to save all your data.")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Study Assistant v1.3 | Now with Smart Study Recommendations! 📚")
