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

# Custom CSS for better styling with vibrant colours
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e94560 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Card-like containers */
    .stExpander {
        border-radius: 12px;
        border: 2px solid #e94560;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }

    /* Priority badges */
    .priority-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(231, 76, 60, 0.3);
    }
    .priority-medium {
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(243, 156, 18, 0.3);
    }
    .priority-low {
        background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(39, 174, 96, 0.3);
    }

    /* Overdue styling */
    .overdue {
        color: #e74c3c;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
    }

    /* Stats cards with colours */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }

    /* Timer display */
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        font-family: monospace;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Subject badge */
    .subject-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Homework item card */
    .homework-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Exam countdown card */
    .exam-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);
    }

    /* Flashcard styling */
    .flashcard {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        font-size: 1.2rem;
    }

    /* Success message */
    .success-msg {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    /* Warning message */
    .warning-msg {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    /* Page header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    /* Streak display */
    .streak-display {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
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
        ["Dashboard", "Bubble Ace", "AI Tools", "What Next?", "Homework", "Exams", "Flashcards", "Notes", "Past Papers", "Focus Timer", "Subjects", "Statistics", "Settings"],
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
        next_exam_days = days_until(exams[0]['exam_date']) if exams else 0
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
        st.markdown("### 🃏 Flashcards Due")
        if fc_due > 0:
            st.markdown(f"""
            <div class="warning-msg">
                <strong>{fc_due} cards</strong> need review!
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Review", key="dash_review"):
                st.info("Go to Flashcards page to review")
        else:
            st.markdown("""
            <div class="success-msg">All caught up!</div>
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


# =============================================================================
# AI TOOLS PAGE
# =============================================================================

elif page == "AI Tools":
    st.title("🤖 AI Tools")
    st.markdown("Powerful AI-powered study tools to supercharge your revision.")

    # Check for API key
    if 'bubble_ace_api_key' not in st.session_state:
        st.session_state.bubble_ace_api_key = ""

    # API Key check
    if not st.session_state.bubble_ace_api_key:
        st.warning("""
        **Claude API Key Required**

        To use AI Tools, you need to set up your Claude API key first.

        Go to **Bubble Ace** page and enter your API key there, or enter it below:
        """)

        api_key = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...")
        if api_key:
            st.session_state.bubble_ace_api_key = api_key
            st.success("API key set! Refresh to use AI Tools.")
            st.rerun()
        st.stop()

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Tabs for different AI tools
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🃏 Generate Flashcards",
        "❓ Create Quiz",
        "📝 Summarise Notes",
        "🎯 Study Coach",
        "✍️ Essay Helper"
    ])

    # Helper function to call Claude API
    def call_claude(prompt: str, system: str = None) -> str:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=st.session_state.bubble_ace_api_key)

            messages = [{"role": "user", "content": prompt}]

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=system or "You are a helpful study assistant for GCSE students. Use British English spellings.",
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    # ===================
    # TAB 1: GENERATE FLASHCARDS
    # ===================
    with tab1:
        st.markdown("### 🃏 Generate Flashcards from Notes")
        st.markdown("Let AI create flashcards from your notes or any topic.")

        fc_method = st.radio(
            "Choose source:",
            ["From my notes", "From a topic"],
            horizontal=True
        )

        if fc_method == "From my notes":
            notes = db.get_all_notes()
            if notes:
                selected_note = st.selectbox(
                    "Select a note:",
                    options=notes,
                    format_func=lambda x: f"{x['title']} ({x['subject_name']})"
                )

                num_cards = st.slider("Number of flashcards", 3, 15, 5)

                if st.button("🪄 Generate Flashcards", type="primary"):
                    with st.spinner("Generating flashcards..."):
                        prompt = f"""Based on these notes, create exactly {num_cards} flashcards for a GCSE student.

Notes Title: {selected_note['title']}
Subject: {selected_note['subject_name']}
Content:
{selected_note['content']}

Format each flashcard as:
Q: [question]
A: [answer]

Make the questions test understanding, not just memorisation. Include a mix of definition, explanation, and application questions."""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.success("Flashcards generated!")
                            st.markdown("### Generated Flashcards")
                            st.markdown(result)

                            # Option to save flashcards
                            st.markdown("---")
                            if st.button("💾 Save These Flashcards"):
                                # Parse and save flashcards
                                lines = result.split('\n')
                                current_q = None
                                saved_count = 0

                                for line in lines:
                                    line = line.strip()
                                    if line.startswith('Q:'):
                                        current_q = line[2:].strip()
                                    elif line.startswith('A:') and current_q:
                                        answer = line[2:].strip()
                                        db.add_flashcard(
                                            subject_id=selected_note['subject_id'],
                                            question=current_q,
                                            answer=answer,
                                            topic=selected_note['topic'] or selected_note['title']
                                        )
                                        saved_count += 1
                                        current_q = None

                                st.success(f"Saved {saved_count} flashcards!")
                        else:
                            st.error(result)
            else:
                st.info("No notes found. Create some notes first!")

        else:  # From a topic
            fc_subject = st.selectbox(
                "Subject:",
                options=subjects,
                format_func=lambda x: x['name'],
                key="fc_topic_subject"
            )

            fc_topic = st.text_input("Topic:", placeholder="e.g., Photosynthesis, The Cold War, Quadratic Equations")
            num_cards = st.slider("Number of flashcards", 3, 15, 5, key="fc_topic_num")

            if st.button("🪄 Generate Flashcards", type="primary", key="fc_topic_btn"):
                if fc_topic:
                    with st.spinner("Generating flashcards..."):
                        prompt = f"""Create exactly {num_cards} flashcards about "{fc_topic}" for GCSE {fc_subject['name']}.

Format each flashcard as:
Q: [question]
A: [answer]

Make the questions appropriate for GCSE level. Include a mix of:
- Key definitions
- Explanations of concepts
- Application questions
- Common exam-style questions"""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.success("Flashcards generated!")
                            st.markdown("### Generated Flashcards")
                            st.markdown(result)

                            st.markdown("---")
                            if st.button("💾 Save These Flashcards", key="save_topic_fc"):
                                lines = result.split('\n')
                                current_q = None
                                saved_count = 0

                                for line in lines:
                                    line = line.strip()
                                    if line.startswith('Q:'):
                                        current_q = line[2:].strip()
                                    elif line.startswith('A:') and current_q:
                                        answer = line[2:].strip()
                                        db.add_flashcard(
                                            subject_id=fc_subject['id'],
                                            question=current_q,
                                            answer=answer,
                                            topic=fc_topic
                                        )
                                        saved_count += 1
                                        current_q = None

                                st.success(f"Saved {saved_count} flashcards!")
                        else:
                            st.error(result)
                else:
                    st.warning("Please enter a topic.")

    # ===================
    # TAB 2: CREATE QUIZ
    # ===================
    with tab2:
        st.markdown("### ❓ Create a Practice Quiz")
        st.markdown("Generate quiz questions to test your knowledge.")

        quiz_subject = st.selectbox(
            "Subject:",
            options=subjects,
            format_func=lambda x: x['name'],
            key="quiz_subject"
        )

        quiz_topic = st.text_input("Topic:", placeholder="e.g., Cell Biology, World War 2", key="quiz_topic")

        col1, col2 = st.columns(2)
        with col1:
            quiz_num = st.slider("Number of questions", 3, 10, 5)
        with col2:
            quiz_type = st.selectbox(
                "Question type:",
                ["Mixed", "Multiple Choice", "Short Answer", "True/False"]
            )

        if st.button("📝 Generate Quiz", type="primary"):
            if quiz_topic:
                with st.spinner("Creating your quiz..."):
                    type_instruction = ""
                    if quiz_type == "Multiple Choice":
                        type_instruction = "Make all questions multiple choice with 4 options (A, B, C, D). Mark the correct answer."
                    elif quiz_type == "Short Answer":
                        type_instruction = "Make all questions short answer (1-2 sentence answers needed)."
                    elif quiz_type == "True/False":
                        type_instruction = "Make all questions True/False. State whether each is True or False."
                    else:
                        type_instruction = "Mix question types: some multiple choice, some short answer, some true/false."

                    prompt = f"""Create a {quiz_num} question quiz about "{quiz_topic}" for GCSE {quiz_subject['name']}.

{type_instruction}

Format:
**Question 1:** [question]
[options if multiple choice]

**Answer:** [correct answer]
**Explanation:** [brief explanation]

---

Continue for all {quiz_num} questions. Make questions progressively harder."""

                    result = call_claude(prompt)

                    if not result.startswith("Error:"):
                        st.success("Quiz generated!")

                        # Store in session state for interactive quiz
                        if 'current_quiz' not in st.session_state:
                            st.session_state.current_quiz = result

                        st.markdown("### Your Quiz")
                        st.markdown(result)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a topic.")

    # ===================
    # TAB 3: SUMMARISE NOTES
    # ===================
    with tab3:
        st.markdown("### 📝 Summarise & Simplify")
        st.markdown("Get AI summaries of your notes or complex topics.")

        sum_method = st.radio(
            "Choose source:",
            ["Summarise my notes", "Explain a topic"],
            horizontal=True,
            key="sum_method"
        )

        if sum_method == "Summarise my notes":
            notes = db.get_all_notes()
            if notes:
                selected_note = st.selectbox(
                    "Select a note to summarise:",
                    options=notes,
                    format_func=lambda x: f"{x['title']} ({x['subject_name']})",
                    key="sum_note"
                )

                sum_style = st.selectbox(
                    "Summary style:",
                    ["Bullet points", "Short paragraph", "Mind map structure", "Key facts only"]
                )

                if st.button("✨ Summarise", type="primary"):
                    with st.spinner("Summarising..."):
                        prompt = f"""Summarise these notes for a GCSE student.

Title: {selected_note['title']}
Subject: {selected_note['subject_name']}

Notes:
{selected_note['content']}

Create a {sum_style.lower()} summary. Focus on:
- Key concepts and definitions
- Important facts to remember
- Connections between ideas

Keep it concise but don't miss important points."""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.success("Summary generated!")
                            st.markdown("### Summary")
                            st.markdown(result)

                            if st.button("💾 Save as New Note"):
                                db.add_note(
                                    subject_id=selected_note['subject_id'],
                                    title=f"Summary: {selected_note['title']}",
                                    content=result,
                                    topic=selected_note['topic']
                                )
                                st.success("Summary saved as a new note!")
                        else:
                            st.error(result)
            else:
                st.info("No notes found. Create some notes first!")

        else:  # Explain a topic
            exp_subject = st.selectbox(
                "Subject:",
                options=subjects,
                format_func=lambda x: x['name'],
                key="exp_subject"
            )

            exp_topic = st.text_input("Topic to explain:", placeholder="e.g., Osmosis, Tectonic Plates")

            exp_level = st.selectbox(
                "Explanation level:",
                ["Simple (like I'm 10)", "Standard GCSE level", "Detailed with examples", "Exam-focused"]
            )

            if st.button("💡 Explain", type="primary", key="explain_btn"):
                if exp_topic:
                    with st.spinner("Creating explanation..."):
                        level_instruction = {
                            "Simple (like I'm 10)": "Explain like I'm 10 years old. Use simple words and fun analogies.",
                            "Standard GCSE level": "Explain at GCSE level with proper terminology.",
                            "Detailed with examples": "Give a detailed explanation with real-world examples.",
                            "Exam-focused": "Focus on what would be asked in exams and how to answer."
                        }

                        prompt = f"""Explain "{exp_topic}" for GCSE {exp_subject['name']}.

{level_instruction[exp_level]}

Structure your explanation with:
1. What it is (definition)
2. How it works
3. Why it matters
4. Key points to remember for exams"""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.success("Explanation generated!")
                            st.markdown("### Explanation")
                            st.markdown(result)

                            if st.button("💾 Save as Note", key="save_exp"):
                                db.add_note(
                                    subject_id=exp_subject['id'],
                                    title=f"Explanation: {exp_topic}",
                                    content=result,
                                    topic=exp_topic
                                )
                                st.success("Saved as a new note!")
                        else:
                            st.error(result)
                else:
                    st.warning("Please enter a topic.")

    # ===================
    # TAB 4: STUDY COACH
    # ===================
    with tab4:
        st.markdown("### 🎯 AI Study Coach")
        st.markdown("Get personalised study advice based on your data.")

        # Gather data for analysis
        homework_stats = db.get_homework_stats()
        flashcard_stats = db.get_flashcard_stats()
        weak_topics = db.get_weak_topics(5)
        paper_count = db.get_paper_count()

        st.markdown("#### Your Current Situation")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Pending Homework", homework_stats['pending'])
            st.metric("Overdue", homework_stats['overdue'])

        with col2:
            st.metric("Flashcards Due", flashcard_stats['due_today'])
            st.metric("7-Day Accuracy", f"{flashcard_stats['accuracy_7_days']}%")

        with col3:
            st.metric("Past Papers Done", paper_count)
            st.metric("Weak Topics", len(weak_topics))

        st.markdown("---")

        coach_question = st.selectbox(
            "What do you need help with?",
            [
                "How should I structure my revision?",
                "What should I focus on first?",
                "Help me create a study plan for this week",
                "How can I improve my weak areas?",
                "Tips for exam preparation",
                "Custom question..."
            ]
        )

        if coach_question == "Custom question...":
            coach_question = st.text_input("Your question:", placeholder="Ask anything about your studies...")

        if st.button("🎯 Get Advice", type="primary"):
            if coach_question:
                with st.spinner("Analyzing your study data..."):
                    # Build context from user data
                    context = f"""Student's current study situation:

Homework:
- Pending: {homework_stats['pending']}
- Overdue: {homework_stats['overdue']}
- Completed this week: {homework_stats['completed_this_week']}

Flashcards:
- Due today: {flashcard_stats['due_today']}
- Total cards: {flashcard_stats['total']}
- 7-day accuracy: {flashcard_stats['accuracy_7_days']}%
- Reviewed today: {flashcard_stats['reviewed_today']}

Past Papers:
- Completed: {paper_count}
- Weak topics: {', '.join([t['topic'] + ' (' + str(t['percentage']) + '%)' for t in weak_topics]) if weak_topics else 'None identified yet'}

Subjects: {', '.join([s['name'] for s in subjects])}"""

                    prompt = f"""{context}

Student's question: {coach_question}

Provide specific, actionable advice based on their actual data. Be encouraging but realistic.
Give concrete steps they can take today.
If they have overdue work or low accuracy areas, address those.
Use British English."""

                    result = call_claude(prompt, system="You are an experienced, friendly study coach helping a GCSE student. Be encouraging, specific, and practical.")

                    if not result.startswith("Error:"):
                        st.markdown("### 💡 Study Coach Advice")
                        st.markdown(result)
                    else:
                        st.error(result)

    # ===================
    # TAB 5: ESSAY HELPER
    # ===================
    with tab5:
        st.markdown("### ✍️ Essay & Extended Writing Helper")
        st.markdown("Get help planning and improving essays.")

        essay_mode = st.radio(
            "What do you need?",
            ["Plan an essay", "Get feedback on my essay", "Improve a paragraph"],
            horizontal=True
        )

        essay_subject = st.selectbox(
            "Subject:",
            options=subjects,
            format_func=lambda x: x['name'],
            key="essay_subject"
        )

        if essay_mode == "Plan an essay":
            essay_question = st.text_area(
                "Essay question:",
                placeholder="e.g., 'Explain how the structure of a leaf is adapted for photosynthesis' (6 marks)"
            )

            essay_marks = st.number_input("How many marks?", 2, 20, 6)

            if st.button("📋 Create Essay Plan", type="primary"):
                if essay_question:
                    with st.spinner("Creating essay plan..."):
                        prompt = f"""Create a detailed essay plan for this GCSE {essay_subject['name']} question:

Question: {essay_question}
Marks: {essay_marks}

Provide:
1. Key points to include (based on mark scheme expectations)
2. Suggested structure (intro, main points, conclusion if needed)
3. Important keywords/terminology to use
4. Common mistakes to avoid
5. How to get full marks

Be specific to the question and subject."""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.markdown("### Essay Plan")
                            st.markdown(result)

                            if st.button("💾 Save Plan as Note"):
                                db.add_note(
                                    subject_id=essay_subject['id'],
                                    title=f"Essay Plan: {essay_question[:50]}...",
                                    content=f"**Question:** {essay_question}\n\n**Plan:**\n{result}",
                                    topic="Essay Plans"
                                )
                                st.success("Plan saved!")
                        else:
                            st.error(result)
                else:
                    st.warning("Please enter an essay question.")

        elif essay_mode == "Get feedback on my essay":
            essay_question = st.text_input("What was the question?", key="fb_question")
            essay_text = st.text_area("Paste your essay:", height=300, key="fb_essay")
            essay_marks = st.number_input("Total marks available:", 2, 20, 6, key="fb_marks")

            if st.button("📊 Get Feedback", type="primary"):
                if essay_text and essay_question:
                    with st.spinner("Analysing your essay..."):
                        prompt = f"""Analyse this GCSE {essay_subject['name']} essay and provide constructive feedback.

Question: {essay_question}
Marks available: {essay_marks}

Student's essay:
{essay_text}

Provide:
1. Estimated mark out of {essay_marks} with justification
2. What was done well (be specific)
3. Areas for improvement (be constructive)
4. Missing points that should be included
5. Suggestions to improve the answer
6. Spelling/grammar notes if relevant

Be encouraging but honest. This is a GCSE student."""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.markdown("### Essay Feedback")
                            st.markdown(result)
                        else:
                            st.error(result)
                else:
                    st.warning("Please enter both the question and your essay.")

        else:  # Improve a paragraph
            para_text = st.text_area("Paste your paragraph:", height=150, key="para_text")
            para_goal = st.selectbox(
                "What do you want to improve?",
                ["Make it clearer", "Add more detail", "Use better vocabulary", "Make it more scientific", "Fix grammar"]
            )

            if st.button("✨ Improve Paragraph", type="primary"):
                if para_text:
                    with st.spinner("Improving..."):
                        prompt = f"""Improve this paragraph for a GCSE {essay_subject['name']} essay.

Original paragraph:
{para_text}

Goal: {para_goal}

Provide:
1. The improved paragraph
2. Brief explanation of what you changed and why

Keep the student's voice but enhance the quality. Use British English."""

                        result = call_claude(prompt)

                        if not result.startswith("Error:"):
                            st.markdown("### Improved Paragraph")
                            st.markdown(result)
                        else:
                            st.error(result)
                else:
                    st.warning("Please enter a paragraph.")


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
# NOTES PAGE
# =============================================================================

elif page == "Notes":
    st.title("📝 Notes")
    st.markdown("Store and search your revision notes in one place.")

    # Initialize the database (creates notes table if it doesn't exist)
    db.init_database()

    subjects = db.get_all_subjects()

    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Session state for editing
    if 'editing_note_id' not in st.session_state:
        st.session_state.editing_note_id = None
    if 'viewing_note_id' not in st.session_state:
        st.session_state.viewing_note_id = None
    if 'ocr_extracted_text' not in st.session_state:
        st.session_state.ocr_extracted_text = ""

    # OCR Import Section
    with st.expander("📷 Import from Image (OCR)", expanded=False):
        st.markdown("""
        Upload an image of handwritten or printed notes to extract the text.
        Works best with clear, well-lit photos of printed text.
        """)

        # Check if Tesseract is installed
        tesseract_available = False
        try:
            import pytesseract
            from PIL import Image
            # Try to find Tesseract
            try:
                pytesseract.get_tesseract_version()
                tesseract_available = True
            except:
                # Try common Windows paths
                common_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(
                        __import__('os').environ.get('USERNAME', '')
                    ),
                ]
                for path in common_paths:
                    if __import__('os').path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        tesseract_available = True
                        break
        except ImportError:
            pass

        if not tesseract_available:
            st.warning("""
            **Tesseract OCR not found!**

            To use OCR, you need to install Tesseract:

            1. Download from: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
            2. Run the installer (choose "Add to PATH" option)
            3. Restart this app

            *Tesseract is free and open-source.*
            """)
        else:
            st.success("✅ Tesseract OCR is ready!")

            col_upload, col_settings = st.columns([2, 1])

            with col_upload:
                uploaded_image = st.file_uploader(
                    "Upload an image",
                    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'],
                    help="Supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP"
                )

            with col_settings:
                ocr_language = st.selectbox(
                    "Language",
                    options=["eng", "eng+equ"],
                    format_func=lambda x: "English" if x == "eng" else "English + Equations",
                    help="Select the language of the text in your image"
                )

                preprocess = st.checkbox("Enhance image", value=True,
                    help="Apply preprocessing to improve OCR accuracy")

            if uploaded_image:
                # Display the uploaded image
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image", use_container_width=True)

                if st.button("🔍 Extract Text", type="primary", use_container_width=True):
                    with st.spinner("Extracting text... This may take a moment."):
                        try:
                            # Preprocessing for better OCR
                            if preprocess:
                                # Convert to RGB if necessary
                                if image.mode != 'RGB':
                                    image = image.convert('RGB')

                                # Convert to grayscale
                                import PIL.ImageOps
                                image = image.convert('L')

                                # Increase contrast
                                from PIL import ImageEnhance
                                enhancer = ImageEnhance.Contrast(image)
                                image = enhancer.enhance(2.0)

                                # Increase sharpness
                                enhancer = ImageEnhance.Sharpness(image)
                                image = enhancer.enhance(2.0)

                            # Perform OCR
                            extracted_text = pytesseract.image_to_string(
                                image,
                                lang=ocr_language,
                                config='--psm 6'  # Assume uniform block of text
                            )

                            if extracted_text.strip():
                                st.session_state.ocr_extracted_text = extracted_text.strip()
                                st.success(f"✅ Extracted {len(extracted_text.split())} words!")
                            else:
                                st.warning("No text could be extracted. Try a clearer image.")

                        except Exception as e:
                            st.error(f"OCR Error: {str(e)}")

            # Show extracted text and create note option
            if st.session_state.ocr_extracted_text:
                st.markdown("### Extracted Text")
                st.text_area(
                    "Extracted text (you can edit before saving)",
                    value=st.session_state.ocr_extracted_text,
                    height=200,
                    key="ocr_text_display",
                    disabled=True
                )

                st.markdown("### Save as Note")
                with st.form("ocr_save_form"):
                    ocr_title = st.text_input("Note Title", placeholder="e.g., Biology Class Notes 15/01")

                    ocr_col1, ocr_col2 = st.columns(2)
                    with ocr_col1:
                        ocr_subject = st.selectbox(
                            "Subject",
                            options=subjects,
                            format_func=lambda x: x['name'],
                            key="ocr_subject"
                        )
                    with ocr_col2:
                        ocr_topic = st.text_input("Topic (optional)", placeholder="e.g., Chapter 5")

                    # Editable content
                    ocr_content = st.text_area(
                        "Content (edit as needed)",
                        value=st.session_state.ocr_extracted_text,
                        height=300,
                        key="ocr_content_edit"
                    )

                    col_save, col_clear = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save as Note", type="primary", use_container_width=True):
                            if ocr_title and ocr_content:
                                db.add_note(
                                    subject_id=ocr_subject['id'],
                                    title=ocr_title,
                                    content=ocr_content,
                                    topic=ocr_topic if ocr_topic else None
                                )
                                st.success("Note saved from OCR!")
                                st.session_state.ocr_extracted_text = ""
                                st.rerun()
                            else:
                                st.error("Please fill in the title.")
                    with col_clear:
                        if st.form_submit_button("🗑️ Clear", use_container_width=True):
                            st.session_state.ocr_extracted_text = ""
                            st.rerun()

        # Tips for better OCR
        with st.expander("💡 Tips for better OCR results"):
            st.markdown("""
            **For best results:**
            - Use good lighting (natural light works best)
            - Keep the camera steady and parallel to the paper
            - Make sure text is in focus and not blurry
            - Avoid shadows across the text
            - Crop the image to just the text area
            - Printed text works much better than handwriting

            **For handwritten notes:**
            - Write clearly and avoid cursive
            - Use a thick pen with good contrast
            - Space out your letters
            - Handwriting recognition is less accurate - expect to edit the result

            **Troubleshooting:**
            - If no text is extracted, try disabling "Enhance image"
            - Very small text may not work well - try zooming in when taking the photo
            - Coloured paper may cause issues - white paper works best
            """)

    st.markdown("---")

    # Top section: Search and filters
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search notes",
            placeholder="Search by title, topic, or content...",
            label_visibility="collapsed"
        )

    with col2:
        filter_subject = st.selectbox(
            "Filter by subject",
            options=[{"id": None, "name": "All Subjects"}] + subjects,
            format_func=lambda x: x['name'],
            label_visibility="collapsed"
        )

    with col3:
        show_favourites = st.checkbox("⭐ Favourites", value=False)

    # Get notes based on filters
    if search_query:
        notes = db.search_notes(search_query, filter_subject['id'] if filter_subject['id'] else None)
    elif show_favourites:
        notes = db.get_favourite_notes()
    else:
        notes = db.get_all_notes(filter_subject['id'] if filter_subject['id'] else None)

    st.markdown("---")

    # Two-column layout: Note list and editor/viewer
    col_list, col_content = st.columns([1, 2])

    with col_list:
        st.markdown("### 📚 Your Notes")

        # Add new note button
        if st.button("➕ New Note", type="primary", use_container_width=True):
            st.session_state.editing_note_id = "new"
            st.session_state.viewing_note_id = None

        # Note count
        total_notes = db.get_notes_count()
        st.caption(f"{len(notes)} of {total_notes} notes shown")

        # Note list
        if notes:
            for note in notes:
                # Create a card for each note
                is_selected = (st.session_state.viewing_note_id == note['id'] or
                              st.session_state.editing_note_id == note['id'])

                card_style = "border-left: 4px solid " + note['subject_colour'] + ";"
                if is_selected:
                    card_style += " background: linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%);"

                st.markdown(f"""
                <div style="background: white; {card_style} padding: 10px 15px;
                            border-radius: 0 8px 8px 0; margin: 8px 0;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <strong>{note['title']}</strong>
                    {"⭐" if note['is_favourite'] else ""}<br>
                    <span class="subject-badge" style="background-color: {note['subject_colour']};">
                        {note['subject_name']}
                    </span>
                    {f"<span style='color: #888; font-size: 0.8rem;'> • {note['topic']}</span>" if note['topic'] else ""}
                    <br>
                    <span style="color: #aaa; font-size: 0.75rem;">
                        Updated: {note['updated_at'][:10] if note['updated_at'] else 'Unknown'}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons for this note
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("👁️", key=f"view_{note['id']}", help="View"):
                        st.session_state.viewing_note_id = note['id']
                        st.session_state.editing_note_id = None
                        st.rerun()
                with btn_col2:
                    if st.button("✏️", key=f"edit_{note['id']}", help="Edit"):
                        st.session_state.editing_note_id = note['id']
                        st.session_state.viewing_note_id = None
                        st.rerun()
                with btn_col3:
                    if st.button("⭐" if not note['is_favourite'] else "★", key=f"fav_{note['id']}", help="Favourite"):
                        db.toggle_note_favourite(note['id'])
                        st.rerun()
        else:
            st.info("No notes found. Create your first note!")

    with col_content:
        # New note form
        if st.session_state.editing_note_id == "new":
            st.markdown("### ✨ Create New Note")

            with st.form("new_note_form"):
                new_title = st.text_input("Title", placeholder="e.g., Photosynthesis Summary")

                col_subj, col_topic = st.columns(2)
                with col_subj:
                    new_subject = st.selectbox(
                        "Subject",
                        options=subjects,
                        format_func=lambda x: x['name']
                    )
                with col_topic:
                    new_topic = st.text_input("Topic (optional)", placeholder="e.g., Chapter 3")

                new_content = st.text_area(
                    "Content",
                    placeholder="Write your notes here...\n\nYou can use markdown formatting!",
                    height=400
                )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Note", type="primary", use_container_width=True):
                        if new_title and new_content:
                            db.add_note(
                                subject_id=new_subject['id'],
                                title=new_title,
                                content=new_content,
                                topic=new_topic if new_topic else None
                            )
                            st.success("Note saved!")
                            st.session_state.editing_note_id = None
                            st.rerun()
                        else:
                            st.error("Please fill in the title and content.")
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.editing_note_id = None
                        st.rerun()

        # Edit existing note
        elif st.session_state.editing_note_id and st.session_state.editing_note_id != "new":
            note = db.get_note_by_id(st.session_state.editing_note_id)
            if note:
                st.markdown(f"### ✏️ Edit: {note['title']}")

                with st.form("edit_note_form"):
                    edit_title = st.text_input("Title", value=note['title'])

                    col_subj, col_topic = st.columns(2)
                    with col_subj:
                        # Find current subject index
                        current_idx = 0
                        for i, s in enumerate(subjects):
                            if s['id'] == note['subject_id']:
                                current_idx = i
                                break
                        edit_subject = st.selectbox(
                            "Subject",
                            options=subjects,
                            format_func=lambda x: x['name'],
                            index=current_idx
                        )
                    with col_topic:
                        edit_topic = st.text_input("Topic", value=note['topic'] or "")

                    edit_content = st.text_area(
                        "Content",
                        value=note['content'],
                        height=400
                    )

                    col_save, col_del, col_cancel = st.columns(3)
                    with col_save:
                        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                            db.update_note(
                                note_id=note['id'],
                                title=edit_title,
                                content=edit_content,
                                topic=edit_topic if edit_topic else None,
                                subject_id=edit_subject['id']
                            )
                            st.success("Note updated!")
                            st.session_state.editing_note_id = None
                            st.session_state.viewing_note_id = note['id']
                            st.rerun()
                    with col_del:
                        if st.form_submit_button("🗑️ Delete", use_container_width=True):
                            db.delete_note(note['id'])
                            st.success("Note deleted!")
                            st.session_state.editing_note_id = None
                            st.session_state.viewing_note_id = None
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.editing_note_id = None
                            st.rerun()

        # View note
        elif st.session_state.viewing_note_id:
            note = db.get_note_by_id(st.session_state.viewing_note_id)
            if note:
                # Note header
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {note['subject_colour']}22, {note['subject_colour']}11);
                            border-left: 4px solid {note['subject_colour']};
                            padding: 15px 20px; border-radius: 8px; margin-bottom: 15px;">
                    <h2 style="margin: 0;">{note['title']} {"⭐" if note['is_favourite'] else ""}</h2>
                    <span class="subject-badge" style="background-color: {note['subject_colour']};">
                        {note['subject_name']}
                    </span>
                    {f"<span style='color: #666;'> • {note['topic']}</span>" if note['topic'] else ""}
                    <br>
                    <span style="color: #888; font-size: 0.8rem;">
                        Created: {note['created_at'][:10] if note['created_at'] else 'Unknown'} •
                        Updated: {note['updated_at'][:10] if note['updated_at'] else 'Unknown'}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
                with btn_col1:
                    if st.button("✏️ Edit", use_container_width=True):
                        st.session_state.editing_note_id = note['id']
                        st.session_state.viewing_note_id = None
                        st.rerun()
                with btn_col2:
                    fav_label = "★ Unfavourite" if note['is_favourite'] else "⭐ Favourite"
                    if st.button(fav_label, use_container_width=True):
                        db.toggle_note_favourite(note['id'])
                        st.rerun()

                st.markdown("---")

                # Note content with markdown rendering
                st.markdown(note['content'])

                # Quick actions
                st.markdown("---")
                st.markdown("**Quick Actions:**")
                qa_col1, qa_col2 = st.columns(2)
                with qa_col1:
                    if st.button("🃏 Create Flashcards from This", use_container_width=True):
                        st.info("Go to Flashcards page and use Bubble Ace to generate flashcards from these notes!")
                with qa_col2:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.code(note['content'], language=None)
                        st.caption("Select and copy the text above")

        # No note selected
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; color: #888;">
                <h1 style="font-size: 4rem; margin: 0;">📝</h1>
                <h3>Select a note to view</h3>
                <p>Or click "New Note" to create one</p>
            </div>
            """, unsafe_allow_html=True)

            # Show recent notes
            recent = db.get_recent_notes(3)
            if recent:
                st.markdown("### 🕐 Recently Updated")
                for note in recent:
                    st.markdown(f"""
                    <div class="homework-card" style="border-left-color: {note['subject_colour']};">
                        <strong>{note['title']}</strong><br>
                        <span class="subject-badge" style="background-color: {note['subject_colour']};">
                            {note['subject_name']}
                        </span>
                        <span style="color: #888; font-size: 0.8rem;"> • {note['updated_at'][:10] if note['updated_at'] else ''}</span>
                    </div>
                    """, unsafe_allow_html=True)


# =============================================================================
# PAST PAPERS PAGE
# =============================================================================

elif page == "Past Papers":
    st.title("📄 Past Paper Analysis")
    st.markdown("Track your practice papers and identify weak areas to focus on.")

    # Initialize database
    db.init_database()

    subjects = db.get_all_subjects()

    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Session state
    if 'viewing_paper_id' not in st.session_state:
        st.session_state.viewing_paper_id = None
    if 'adding_paper' not in st.session_state:
        st.session_state.adding_paper = False

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📝 Add Paper", "📋 All Papers"])

    # ===================
    # TAB 1: ANALYSIS
    # ===================
    with tab1:
        paper_count = db.get_paper_count()

        if paper_count == 0:
            st.info("No past papers recorded yet. Go to 'Add Paper' tab to log your first one!")
        else:
            # Overview stats
            st.markdown("### 📈 Overview")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="stat-card-blue">
                    <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{paper_count}</h1>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Papers Done</p>
                </div>
                """, unsafe_allow_html=True)

            # Calculate overall average
            all_papers = db.get_all_past_papers()
            total_achieved = sum(p['marks_achieved'] or 0 for p in all_papers)
            total_possible = sum(p['total_marks'] for p in all_papers)
            overall_avg = round((total_achieved / total_possible) * 100, 1) if total_possible > 0 else 0

            with col2:
                avg_color = "stat-card-green" if overall_avg >= 70 else ("stat-card-orange" if overall_avg >= 50 else "stat-card")
                st.markdown(f"""
                <div class="{avg_color}">
                    <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{overall_avg}%</h1>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Average Score</p>
                </div>
                """, unsafe_allow_html=True)

            # Subject count
            subject_stats = db.get_subject_paper_stats()
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{len(subject_stats)}</h1>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Subjects Covered</p>
                </div>
                """, unsafe_allow_html=True)

            # Weak topics count
            weak_topics = db.get_weak_topics(5)
            with col4:
                st.markdown(f"""
                <div class="stat-card-orange">
                    <h1 style="font-size: 2.5rem; margin: 0; color: white !important; -webkit-text-fill-color: white;">{len(weak_topics)}</h1>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Weak Areas</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Two column layout
            col_left, col_right = st.columns(2)

            with col_left:
                # Weak topics (areas to focus on)
                st.markdown("### 🎯 Areas to Focus On")
                if weak_topics:
                    for topic in weak_topics:
                        pct = topic['percentage'] or 0
                        color = "#e74c3c" if pct < 50 else ("#f39c12" if pct < 70 else "#27ae60")
                        st.markdown(f"""
                        <div class="homework-card" style="border-left-color: {topic['subject_colour']};">
                            <strong>{topic['topic']}</strong>
                            <span style="float: right; color: {color}; font-weight: bold;">{pct}%</span><br>
                            <span class="subject-badge" style="background-color: {topic['subject_colour']};">
                                {topic['subject_name']}
                            </span>
                            <span style="color: #888; font-size: 0.8rem;"> • {topic['question_count']} questions</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Add topics to your questions to see analysis here.")

            with col_right:
                # Subject performance
                st.markdown("### 📚 Subject Performance")
                if subject_stats:
                    for subj in subject_stats:
                        pct = subj['average_percentage'] or 0
                        color = "#e74c3c" if pct < 50 else ("#f39c12" if pct < 70 else "#27ae60")
                        st.markdown(f"""
                        <div class="homework-card" style="border-left-color: {subj['subject_colour']};">
                            <strong>{subj['subject_name']}</strong>
                            <span style="float: right; color: {color}; font-weight: bold;">{pct}%</span><br>
                            <span style="color: #888; font-size: 0.8rem;">{subj['paper_count']} paper(s) • {subj['total_achieved'] or 0}/{subj['total_possible'] or 0} marks</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No papers recorded yet.")

            # Progress over time
            st.markdown("---")
            st.markdown("### 📈 Progress Over Time")

            progress = db.get_progress_over_time(limit=15)
            if progress:
                # Simple bar chart using Streamlit
                chart_data = {
                    'Paper': [p['paper_name'][:20] + '...' if len(p['paper_name']) > 20 else p['paper_name'] for p in progress],
                    'Score (%)': [p['percentage'] or 0 for p in progress]
                }
                st.bar_chart(chart_data, x='Paper', y='Score (%)')
            else:
                st.info("Complete more papers to see your progress over time.")

    # ===================
    # TAB 2: ADD PAPER
    # ===================
    with tab2:
        st.markdown("### 📝 Log a Past Paper")

        with st.form("add_paper_form"):
            col1, col2 = st.columns(2)

            with col1:
                paper_subject = st.selectbox(
                    "Subject",
                    options=subjects,
                    format_func=lambda x: x['name']
                )
                paper_name = st.text_input(
                    "Paper Name",
                    placeholder="e.g., Biology Paper 1 - Cells and Organisation"
                )
                paper_total = st.number_input(
                    "Total Marks",
                    min_value=1,
                    max_value=500,
                    value=60
                )

            with col2:
                paper_board = st.selectbox(
                    "Exam Board",
                    options=["AQA", "Edexcel", "OCR", "WJEC", "Other"]
                )
                paper_year = st.text_input(
                    "Year (optional)",
                    placeholder="e.g., 2023"
                )
                paper_time = st.number_input(
                    "Time Taken (minutes, optional)",
                    min_value=0,
                    max_value=300,
                    value=0
                )

            paper_notes = st.text_area(
                "Notes (optional)",
                placeholder="Any observations about this paper..."
            )

            st.markdown("---")
            st.markdown("### 📊 Enter Your Scores")
            st.markdown("Add each question's score. Optionally add the topic for better analysis.")

            # Dynamic question entry
            num_questions = st.number_input(
                "Number of Questions",
                min_value=1,
                max_value=50,
                value=5
            )

            questions_data = []
            for i in range(int(num_questions)):
                st.markdown(f"**Question {i+1}**")
                q_col1, q_col2, q_col3 = st.columns([1, 1, 2])

                with q_col1:
                    max_marks = st.number_input(
                        "Max Marks",
                        min_value=1,
                        max_value=50,
                        value=6,
                        key=f"max_{i}"
                    )
                with q_col2:
                    achieved = st.number_input(
                        "Your Marks",
                        min_value=0,
                        max_value=50,
                        value=0,
                        key=f"achieved_{i}"
                    )
                with q_col3:
                    topic = st.text_input(
                        "Topic (optional)",
                        placeholder="e.g., Cell Division",
                        key=f"topic_{i}"
                    )

                questions_data.append({
                    'number': str(i + 1),
                    'max_marks': max_marks,
                    'achieved': min(achieved, max_marks),  # Can't exceed max
                    'topic': topic
                })

            if st.form_submit_button("💾 Save Paper", type="primary"):
                if paper_name and paper_total:
                    # Add the paper
                    paper_id = db.add_past_paper(
                        subject_id=paper_subject['id'],
                        paper_name=paper_name,
                        total_marks=paper_total,
                        exam_board=paper_board,
                        year=paper_year if paper_year else None,
                        time_taken_minutes=paper_time if paper_time > 0 else None,
                        notes=paper_notes if paper_notes else None
                    )

                    # Add questions
                    for q in questions_data:
                        db.add_paper_question(
                            paper_id=paper_id,
                            question_number=q['number'],
                            max_marks=q['max_marks'],
                            marks_achieved=q['achieved'],
                            topic=q['topic'] if q['topic'] else None
                        )

                    total_achieved = sum(q['achieved'] for q in questions_data)
                    percentage = round((total_achieved / paper_total) * 100, 1)

                    st.success(f"✅ Paper saved! You scored {total_achieved}/{paper_total} ({percentage}%)")
                    st.balloons()
                else:
                    st.error("Please fill in the paper name and total marks.")

    # ===================
    # TAB 3: ALL PAPERS
    # ===================
    with tab3:
        st.markdown("### 📋 All Past Papers")

        # Filter by subject
        filter_subject = st.selectbox(
            "Filter by Subject",
            options=[{"id": None, "name": "All Subjects"}] + subjects,
            format_func=lambda x: x['name'],
            key="paper_filter"
        )

        papers = db.get_all_past_papers(filter_subject['id'] if filter_subject['id'] else None)

        if papers:
            for paper in papers:
                achieved = paper['marks_achieved'] or 0
                percentage = round((achieved / paper['total_marks']) * 100, 1) if paper['total_marks'] > 0 else 0
                pct_color = "#27ae60" if percentage >= 70 else ("#f39c12" if percentage >= 50 else "#e74c3c")

                with st.expander(f"**{paper['paper_name']}** - {percentage}%"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"""
                        <span class="subject-badge" style="background-color: {paper['subject_colour']};">
                            {paper['subject_name']}
                        </span>
                        """, unsafe_allow_html=True)

                        if paper['exam_board']:
                            st.write(f"**Exam Board:** {paper['exam_board']}")
                        if paper['year']:
                            st.write(f"**Year:** {paper['year']}")
                        if paper['time_taken_minutes']:
                            st.write(f"**Time Taken:** {paper['time_taken_minutes']} minutes")
                        if paper['notes']:
                            st.write(f"**Notes:** {paper['notes']}")

                        st.write(f"**Completed:** {paper['completed_at'][:10] if paper['completed_at'] else 'Unknown'}")

                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 20px;
                                    background: linear-gradient(135deg, {pct_color}22, {pct_color}11);
                                    border-radius: 12px;">
                            <h1 style="margin: 0; color: {pct_color};">{percentage}%</h1>
                            <p style="margin: 5px 0 0 0;">{achieved}/{paper['total_marks']} marks</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # View details button
                    if st.button("View Question Breakdown", key=f"view_{paper['id']}"):
                        full_paper = db.get_past_paper_by_id(paper['id'])
                        if full_paper and full_paper.get('questions'):
                            st.markdown("**Question Breakdown:**")
                            for q in full_paper['questions']:
                                q_pct = round((q['marks_achieved'] / q['max_marks']) * 100) if q['max_marks'] > 0 else 0
                                q_color = "#27ae60" if q_pct >= 70 else ("#f39c12" if q_pct >= 50 else "#e74c3c")
                                topic_text = f" ({q['topic']})" if q['topic'] else ""
                                st.markdown(f"""
                                Q{q['question_number']}{topic_text}: **{q['marks_achieved']}/{q['max_marks']}**
                                <span style="color: {q_color};">({q_pct}%)</span>
                                """, unsafe_allow_html=True)

                    # Delete button
                    if st.button("🗑️ Delete Paper", key=f"del_{paper['id']}"):
                        db.delete_past_paper(paper['id'])
                        st.success("Paper deleted!")
                        st.rerun()
        else:
            st.info("No papers recorded yet. Go to 'Add Paper' tab to log your first one!")


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
# BUBBLE ACE - AI STUDY BUDDY
# =============================================================================

elif page == "Bubble Ace":
    st.title("🫧 Bubble Ace")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 20px; border-radius: 16px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #333;">Hey there! I'm Bubble Ace, your AI study buddy! 🎓</h3>
        <p style="margin: 10px 0 0 0; color: #555;">
            I'm here to help you understand tricky topics, quiz you on what you're learning,
            and make studying more fun! Just ask me anything about your subjects.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history in session state
    if 'bubble_ace_messages' not in st.session_state:
        st.session_state.bubble_ace_messages = []

    if 'bubble_ace_api_key' not in st.session_state:
        st.session_state.bubble_ace_api_key = ""

    # API Key input
    with st.expander("🔑 API Key Settings", expanded=not st.session_state.bubble_ace_api_key):
        st.markdown("""
        To chat with Bubble Ace, you need a Claude API key from Anthropic.

        **How to get one:**
        1. Go to [console.anthropic.com](https://console.anthropic.com)
        2. Sign up or log in
        3. Go to API Keys and create a new key
        4. Paste it below

        *Your key is stored only in this session and never saved.*
        """)

        api_key_input = st.text_input(
            "Claude API Key",
            type="password",
            value=st.session_state.bubble_ace_api_key,
            placeholder="sk-ant-..."
        )

        if api_key_input:
            st.session_state.bubble_ace_api_key = api_key_input
            st.success("API key set! You can now chat with Bubble Ace.")

    # Quick action buttons
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    quick_prompts = {
        "Explain a Topic": "Can you explain this topic to me in a simple way: ",
        "Quiz Me": "Give me 5 quiz questions about: ",
        "Summarise Notes": "Please summarise these notes for me: ",
        "Essay Help": "Help me structure an essay about: "
    }

    with col1:
        if st.button("📖 Explain Topic", use_container_width=True):
            st.session_state.bubble_ace_quick = "explain"
    with col2:
        if st.button("❓ Quiz Me", use_container_width=True):
            st.session_state.bubble_ace_quick = "quiz"
    with col3:
        if st.button("📝 Summarise", use_container_width=True):
            st.session_state.bubble_ace_quick = "summarise"
    with col4:
        if st.button("✍️ Essay Help", use_container_width=True):
            st.session_state.bubble_ace_quick = "essay"

    # Subject context
    subjects = db.get_all_subjects()
    if subjects:
        selected_subject = st.selectbox(
            "📚 What subject are you studying?",
            options=["General"] + [s['name'] for s in subjects],
            help="This helps Bubble Ace give you more relevant answers"
        )
    else:
        selected_subject = "General"

    st.markdown("---")

    # Chat container with custom styling
    st.markdown("""
    <style>
        .bubble-ace-msg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 20px 20px 5px 20px;
            margin: 10px 0;
            max-width: 80%;
        }
        .user-msg {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #333;
            padding: 15px 20px;
            border-radius: 20px 20px 20px 5px;
            margin: 10px 0;
            margin-left: auto;
            max-width: 80%;
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display chat history
    chat_container = st.container()

    with chat_container:
        if not st.session_state.bubble_ace_messages:
            st.markdown("""
            <div style="text-align: center; padding: 40px; color: #888;">
                <h2>🫧</h2>
                <p>Start a conversation! Ask me about any topic you're studying.</p>
                <p><em>Try: "Explain photosynthesis like I'm 10" or "Quiz me on the Cold War"</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.bubble_ace_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end;">
                        <div class="user-msg">
                            <strong>You:</strong><br>{msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-start;">
                        <div class="bubble-ace-msg">
                            <strong>🫧 Bubble Ace:</strong><br>{msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Chat input
    st.markdown("---")

    # Handle quick action prefixes
    quick_prefix = ""
    if 'bubble_ace_quick' in st.session_state:
        quick_actions = {
            "explain": "Explain this topic to me in a simple, easy-to-understand way: ",
            "quiz": "Give me 5 quiz questions (with answers) about: ",
            "summarise": "Summarise these notes in bullet points: ",
            "essay": "Help me structure an essay about: "
        }
        quick_prefix = quick_actions.get(st.session_state.bubble_ace_quick, "")
        del st.session_state.bubble_ace_quick

    user_input = st.text_area(
        "Message Bubble Ace",
        value=quick_prefix,
        placeholder="Ask me anything about your studies...",
        height=100,
        key="bubble_ace_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.bubble_ace_messages = []
            st.rerun()

    if send_button and user_input.strip():
        if not st.session_state.bubble_ace_api_key:
            st.error("Please enter your Claude API key first!")
        else:
            # Add user message to history
            st.session_state.bubble_ace_messages.append({
                "role": "user",
                "content": user_input
            })

            # Generate response
            with st.spinner("🫧 Bubble Ace is thinking..."):
                try:
                    from anthropic import Anthropic

                    client = Anthropic(api_key=st.session_state.bubble_ace_api_key)

                    # Build system prompt
                    system_prompt = f"""You are Bubble Ace, a friendly and encouraging AI study buddy for GCSE students.

Your personality:
- Friendly, supportive, and enthusiastic about learning
- Use simple language appropriate for 14-16 year olds
- Add occasional emojis to be friendly but not excessive
- Be encouraging when students struggle
- Celebrate when they understand something

The student is currently studying: {selected_subject}

Guidelines:
- Explain concepts clearly using analogies and examples
- For quizzes, provide the answer after each question
- Break down complex topics into manageable chunks
- If asked about topics outside of typical GCSE subjects, still help but keep it educational
- Encourage the student to keep studying and praise their effort
- Keep responses focused and not too long (students have short attention spans!)
- Use British English spellings (colour, favourite, organise, etc.)"""

                    # Build messages for API
                    api_messages = []
                    for msg in st.session_state.bubble_ace_messages:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        system=system_prompt,
                        messages=api_messages
                    )

                    assistant_message = response.content[0].text

                    # Add assistant response to history
                    st.session_state.bubble_ace_messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })

                    st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    if "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                        st.error("❌ Invalid API key. Please check your key and try again.")
                    elif "rate_limit" in error_msg.lower():
                        st.error("⏳ Rate limit reached. Please wait a moment and try again.")
                    else:
                        st.error(f"❌ Error: {error_msg}")

                    # Remove the failed user message
                    st.session_state.bubble_ace_messages.pop()

    # Tips section
    with st.expander("💡 Tips for chatting with Bubble Ace"):
        st.markdown("""
        **Great questions to ask:**
        - "Explain [topic] like I'm 10 years old"
        - "Give me 5 quiz questions about [topic]"
        - "What are the key points I need to remember about [topic]?"
        - "Help me understand why [concept] happens"
        - "What's the difference between [thing 1] and [thing 2]?"
        - "Can you give me an example of [concept]?"
        - "How do I answer a 6-mark question about [topic]?"
        - "Summarise [chapter/topic] in bullet points"

        **Study techniques I can help with:**
        - Creating mnemonics to remember things
        - Breaking down essay questions
        - Explaining mark schemes
        - Practising exam-style questions
        - Making connections between topics
        """)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Study Assistant v1.8 | AI Tools, Past Papers, OCR, Notes & Bubble Ace! 🤖📄📷📝🫧")
