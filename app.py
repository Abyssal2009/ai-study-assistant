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
    knowledge_gaps, srs_analytics
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


# =============================================================================
# SIDEBAR - NAVIGATION
# =============================================================================

with st.sidebar:
    st.title("📚 Study Assistant")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Bubble Ace",
            "AI Tools",
            "Knowledge Gaps",
            "Study Schedule",
            "Homework",
            "Exams",
            "Flashcards",
            "SRS Analytics",
            "Notes",
            "Past Papers",
            "Focus Timer",
            "Subjects",
            "Statistics",
            "Settings"
        ],
        label_visibility="collapsed"
    )

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
st.caption("Study Assistant v2.1 | Adaptive Study Schedule, Knowledge Gaps, AI Tools & More! 📅🎯🤖📝")
