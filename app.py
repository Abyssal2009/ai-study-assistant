"""
Study Assistant - Main Application
A simple but powerful study tool for GCSE students.

Run with: streamlit run app.py
"""

import streamlit as st
import database as db
from styles import apply_styles
from pages import (
    dashboard, ai_tools, bubble_ace, study_schedule,
    homework, exams, flashcards, notes,
    past_papers, focus_timer, subjects, statistics, settings,
    knowledge_gaps, srs_analytics, essay_tutor, exam_technique, study_skills
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styles
apply_styles(st)

# Hide default Streamlit sidebar header elements
st.markdown("""
<style>
    [data-testid="stSidebarHeader"] {display: none;}
    section[data-testid="stSidebar"] > div:first-child {padding-top: 1rem;}
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
    st.session_state.timer_duration = 25
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

# Chat state
if 'bubble_ace_api_key' not in st.session_state:
    st.session_state.bubble_ace_api_key = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Knowledge Gap Assessment state
if 'current_assessment' not in st.session_state:
    st.session_state.current_assessment = None
if 'assessment_index' not in st.session_state:
    st.session_state.assessment_index = 0
if 'assessment_start_time' not in st.session_state:
    st.session_state.assessment_start_time = None

# Exam Technique Trainer state
if 'technique_session' not in st.session_state:
    st.session_state.technique_session = None
if 'technique_question_index' not in st.session_state:
    st.session_state.technique_question_index = 0
if 'technique_start_time' not in st.session_state:
    st.session_state.technique_start_time = None
if 'technique_question_start' not in st.session_state:
    st.session_state.technique_question_start = None
if 'technique_questions' not in st.session_state:
    st.session_state.technique_questions = []


# =============================================================================
# SIDEBAR - NAVIGATION (Grouped for easier navigation)
# =============================================================================

# Define navigation groups for better UX
NAV_GROUPS = {
    "Daily Tasks": ["Dashboard", "Homework", "Focus Timer"],
    "Study Tools": ["Flashcards", "Notes", "Past Papers", "Exams"],
    "AI Assistants": ["Bubble Ace", "AI Tools", "Essay Tutor", "Exam Technique", "Study Skills"],
    "Progress": ["Study Schedule", "Knowledge Gaps", "SRS Analytics", "Statistics"],
    "Settings": ["Subjects", "Settings"],
}

# Page display names with emojis
PAGE_LABELS = {
    "Dashboard": "📊 Dashboard",
    "Homework": "📝 Homework",
    "Focus Timer": "⏱️ Focus Timer",
    "Flashcards": "🃏 Flashcards",
    "Notes": "📓 Notes",
    "Past Papers": "📄 Past Papers",
    "Exams": "🎓 Exams",
    "Bubble Ace": "💬 Bubble Ace",
    "AI Tools": "🤖 AI Tools",
    "Essay Tutor": "✍️ Essay Tutor",
    "Exam Technique": "🎯 Exam Technique",
    "Study Skills": "📚 Study Skills",
    "Study Schedule": "📅 Study Schedule",
    "Knowledge Gaps": "🔍 Knowledge Gaps",
    "SRS Analytics": "📈 SRS Analytics",
    "Statistics": "📉 Statistics",
    "Subjects": "📖 Subjects",
    "Settings": "⚙️ Settings",
}

# Flatten for page lookup
ALL_PAGES = [page for pages in NAV_GROUPS.values() for page in pages]

with st.sidebar:
    # Logo at top
    st.title("📚 Study Assistant")
    st.markdown("---")

    # Initialize selected page in session state
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard"

    # Render grouped selectbox navigation
    for group_name, group_pages in NAV_GROUPS.items():
        # Build options with emoji labels
        options = [PAGE_LABELS[p] for p in group_pages]

        # Check if current selection is in this group
        current_in_group = st.session_state.selected_page in group_pages

        # Calculate default index (0 if not in this group)
        if current_in_group:
            default_index = group_pages.index(st.session_state.selected_page)
        else:
            default_index = 0

        # Selectbox for this group
        selected_label = st.selectbox(
            group_name,
            options=options,
            index=default_index,
            key=f"nav_select_{group_name}"
        )

        # Reverse lookup: find page name from label
        selected_page = next(p for p, lbl in PAGE_LABELS.items() if lbl == selected_label)

        # Only navigate if user selected from this group and it's different
        if selected_page in group_pages and selected_page != st.session_state.selected_page:
            st.session_state.selected_page = selected_page
            st.rerun()

    # Get current page from session state
    page = st.session_state.selected_page

    st.markdown("---")

    # Quick stats in sidebar
    stats = db.get_homework_stats()
    st.metric("Pending Homework", stats['pending'])
    if stats['overdue'] > 0:
        st.metric("Overdue", stats['overdue'], delta=f"-{stats['overdue']}", delta_color="inverse")

    flashcard_due = db.get_due_flashcards_count()
    st.metric("Flashcards Due", flashcard_due)

    focus_today = db.get_total_focus_minutes_today()
    st.metric("Focus Today", f"{focus_today} min")


# =============================================================================
# PAGE ROUTING
# =============================================================================

# Map page names to render functions
PAGE_MODULES = {
    "Dashboard": dashboard,
    "Bubble Ace": bubble_ace,
    "AI Tools": ai_tools,
    "Essay Tutor": essay_tutor,
    "Exam Technique": exam_technique,
    "Study Skills": study_skills,
    "Knowledge Gaps": knowledge_gaps,
    "Study Schedule": study_schedule,
    "Homework": homework,
    "Exams": exams,
    "Flashcards": flashcards,
    "SRS Analytics": srs_analytics,
    "Notes": notes,
    "Past Papers": past_papers,
    "Focus Timer": focus_timer,
    "Subjects": subjects,
    "Statistics": statistics,
    "Settings": settings,
}

# Render the selected page
if page in PAGE_MODULES:
    PAGE_MODULES[page].render()


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Study Assistant v2.5 | Study Skills, Exam Technique, Essay Tutor & More! 📚🎯📝🤖")
