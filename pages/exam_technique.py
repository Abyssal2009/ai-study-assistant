"""
Study Assistant - Exam Technique Trainer Page
Practice exam techniques with timed questions and AI feedback.
"""

import streamlit as st
import database as db
from utils import call_claude
import json
import time
from datetime import datetime


def render():
    """Render the Exam Technique Trainer page."""
    st.title("🎯 Exam Technique Trainer")
    st.markdown("Master exam skills with strategies, timed practice, and technique feedback.")

    # Seed techniques on first load
    db.seed_exam_techniques()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Exam Strategies",
        "⏱️ Timed Practice",
        "📊 Post-Exam Review",
        "📈 Progress Tracker"
    ])

    with tab1:
        _render_strategies_tab()

    with tab2:
        _render_timed_practice_tab()

    with tab3:
        _render_post_exam_review_tab()

    with tab4:
        _render_progress_tracker_tab()


# =============================================================================
# TAB 1: EXAM STRATEGIES
# =============================================================================

def _render_strategies_tab():
    """Render exam strategies and tips."""
    st.markdown("### Exam Technique Library")
    st.markdown("Browse proven strategies to improve your exam performance.")

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox(
            "Category",
            ["All", "time_management", "question_approach", "answer_technique"],
            format_func=lambda x: {
                "All": "All Categories",
                "time_management": "⏰ Time Management",
                "question_approach": "📝 Question Approach",
                "answer_technique": "✍️ Answer Technique"
            }.get(x, x)
        )
    with col2:
        question_type = st.selectbox(
            "Question Type",
            ["All", "essay", "multiple_choice", "short_answer"],
            format_func=lambda x: {
                "All": "All Types",
                "essay": "📄 Essay",
                "multiple_choice": "☑️ Multiple Choice",
                "short_answer": "📋 Short Answer"
            }.get(x, x)
        )

    # Get techniques
    cat_filter = None if category == "All" else category
    type_filter = None if question_type == "All" else question_type
    techniques = db.get_all_exam_techniques(cat_filter, type_filter)

    if not techniques:
        st.info("No techniques found for the selected filters.")
        return

    # Display technique cards
    for tech in techniques:
        _render_technique_card(tech)


def _render_technique_card(technique: dict):
    """Render a single technique tip card."""
    category_icons = {
        "time_management": "⏰",
        "question_approach": "📝",
        "answer_technique": "✍️"
    }
    category_colors = {
        "time_management": "#3498db",
        "question_approach": "#27ae60",
        "answer_technique": "#9b59b6"
    }

    icon = category_icons.get(technique['category'], "📌")
    color = category_colors.get(technique['category'], "#666")

    with st.expander(f"{icon} {technique['title']}", expanded=False):
        st.markdown(f"**{technique['description']}**")

        if technique.get('question_type'):
            st.caption(f"Best for: {technique['question_type'].replace('_', ' ').title()} questions")

        # Parse and display tips
        try:
            tips = json.loads(technique['tips']) if isinstance(technique['tips'], str) else technique['tips']
            st.markdown("**Tips:**")
            for tip in tips:
                st.markdown(f"- {tip}")
        except (json.JSONDecodeError, TypeError):
            st.markdown(technique['tips'])


# =============================================================================
# TAB 2: TIMED PRACTICE
# =============================================================================

def _render_timed_practice_tab():
    """Render timed practice session."""
    api_key = st.session_state.get('bubble_ace_api_key', '')

    if st.session_state.get('technique_session'):
        _render_active_practice(api_key)
    else:
        _render_practice_setup(api_key)


def _render_practice_setup(api_key: str):
    """Setup form for new practice session."""
    st.markdown("### Start a Practice Session")
    st.markdown("Test your exam technique with timed questions.")

    if not api_key:
        st.warning("Add your Claude API key in Settings for AI-generated questions and feedback.")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Add subjects first to start practicing.")
        return

    col1, col2 = st.columns(2)
    with col1:
        subject_options = {s['id']: s['name'] for s in subjects}
        subject_id = st.selectbox(
            "Subject",
            options=list(subject_options.keys()),
            format_func=lambda x: subject_options[x]
        )

        num_questions = st.selectbox(
            "Number of Questions",
            [5, 10, 15],
            index=0
        )

    with col2:
        question_types = st.selectbox(
            "Question Types",
            ["mixed", "multiple_choice", "short_answer", "essay"],
            format_func=lambda x: {
                "mixed": "Mixed (Recommended)",
                "multiple_choice": "Multiple Choice Only",
                "short_answer": "Short Answer Only",
                "essay": "Essay Only"
            }.get(x, x)
        )

        timer_mode = st.selectbox(
            "Timer Mode",
            ["real_exam", "relaxed", "untimed"],
            format_func=lambda x: {
                "real_exam": "Real Exam Pace (1.5 min/mark)",
                "relaxed": "Relaxed (2x time)",
                "untimed": "Untimed (No timer)"
            }.get(x, x)
        )

    st.markdown("---")

    if st.button("🚀 Start Practice", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please add your Claude API key in Settings first.")
            return

        with st.spinner("Generating practice questions..."):
            questions = _generate_practice_questions(api_key, subject_id, num_questions, question_types)

        if questions:
            # Calculate time limit
            total_marks = sum(q.get('marks', 1) for q in questions)
            if timer_mode == "real_exam":
                time_limit = int(total_marks * 1.5 * 60)  # 1.5 min per mark in seconds
            elif timer_mode == "relaxed":
                time_limit = int(total_marks * 3 * 60)  # 3 min per mark
            else:
                time_limit = None

            # Create session
            session_id = db.create_technique_session(
                subject_id=subject_id,
                session_type=timer_mode,
                question_types=question_types,
                total_questions=len(questions),
                time_limit=time_limit
            )

            # Store in session state
            st.session_state.technique_session = session_id
            st.session_state.technique_questions = questions
            st.session_state.technique_question_index = 0
            st.session_state.technique_start_time = time.time()
            st.session_state.technique_question_start = time.time()

            st.rerun()
        else:
            st.error("Couldn't generate practice questions. Check your API key in **Settings** and try again with fewer questions.")


def _generate_practice_questions(api_key: str, subject_id: int, num_questions: int, question_types: str) -> list:
    """Generate practice questions using AI."""
    subject = db.get_subject_by_id(subject_id)
    if not subject:
        return []

    type_instruction = ""
    if question_types == "multiple_choice":
        type_instruction = "Generate only multiple choice questions with 4 options (A, B, C, D)."
    elif question_types == "short_answer":
        type_instruction = "Generate only short answer questions requiring 1-3 sentence answers."
    elif question_types == "essay":
        type_instruction = "Generate only essay questions requiring paragraph-length answers."
    else:
        type_instruction = "Generate a mix of multiple choice, short answer, and essay questions."

    prompt = f"""Generate {num_questions} GCSE-level exam questions for {subject['name']}.

{type_instruction}

For each question, provide:
- question_text: The question
- question_type: "multiple_choice", "short_answer", or "essay"
- options: For multiple choice, provide options A, B, C, D (null for other types)
- correct_answer: The correct answer (letter for MC, brief answer for others)
- marks: Marks available (1-2 for MC, 2-4 for short, 4-8 for essay)
- topic: The topic being tested

Respond in JSON format:
{{
    "questions": [
        {{
            "question_text": "...",
            "question_type": "multiple_choice",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
            "correct_answer": "B",
            "marks": 1,
            "topic": "..."
        }},
        ...
    ]
}}"""

    try:
        result = call_claude(api_key, prompt, model='sonnet')

        # Parse JSON
        json_str = result
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())
        return data.get('questions', [])
    except Exception as e:
        st.error(f"Couldn't generate questions: {e}. Try selecting fewer questions or a different question type.")
        return []


def _render_active_practice(api_key: str):
    """Active practice session with timer."""
    session_id = st.session_state.technique_session
    questions = st.session_state.technique_questions
    current_idx = st.session_state.technique_question_index

    if current_idx >= len(questions):
        _complete_practice_session(api_key)
        return

    session = db.get_technique_session(session_id)
    current_q = questions[current_idx]

    # Header with progress
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown(f"### Question {current_idx + 1} of {len(questions)}")
    with col2:
        st.progress((current_idx) / len(questions))
    with col3:
        if st.button("❌ End", help="End session early"):
            _abandon_session()
            st.rerun()

    # Timer display
    if session and session.get('time_limit_seconds'):
        _render_timer_display(
            st.session_state.technique_start_time,
            session['time_limit_seconds'],
            st.session_state.technique_question_start,
            int(current_q.get('marks', 1) * 90)  # 1.5 min per mark suggested
        )

    st.markdown("---")

    # Question card
    q_type = current_q.get('question_type', 'short_answer')
    marks = current_q.get('marks', 1)

    type_badges = {
        "multiple_choice": ("☑️ Multiple Choice", "good"),
        "short_answer": ("📋 Short Answer", "excellent"),
        "essay": ("📄 Essay", "average")
    }
    badge_text, badge_class = type_badges.get(q_type, ("❓ Question", "good"))

    st.markdown(f"""
    <div class="feedback-card feedback-card-info">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="grade-badge grade-badge-b">{badge_text}</span>
            <span class="score-badge score-badge-{badge_class}">{marks} mark{"s" if marks > 1 else ""}</span>
        </div>
        <p class="technique-description" style="margin-top: 10px;"><strong>{current_q['question_text']}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Technique hint (collapsible)
    with st.expander("💡 Technique Hint", expanded=False):
        _show_question_hint(q_type, marks)

    # Answer input
    st.markdown("**Your Answer:**")
    if q_type == "multiple_choice" and current_q.get('options'):
        options = current_q['options']
        answer = st.radio(
            "Select your answer:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}: {options[x]}",
            key=f"answer_{current_idx}",
            label_visibility="collapsed"
        )
    elif q_type == "essay":
        answer = st.text_area(
            "Write your answer:",
            height=200,
            key=f"answer_{current_idx}",
            label_visibility="collapsed"
        )
    else:
        answer = st.text_area(
            "Write your answer:",
            height=100,
            key=f"answer_{current_idx}",
            label_visibility="collapsed"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col2:
        if st.button("Submit & Next ➡️", type="primary", use_container_width=True):
            if not answer:
                st.warning("Please provide an answer before submitting.")
            else:
                _submit_answer(session_id, current_idx, current_q, answer, api_key)
                st.rerun()


def _render_timer_display(session_start: float, time_limit: int, question_start: float, suggested_time: int):
    """Render dual timer: session total and current question."""
    now = time.time()
    session_elapsed = int(now - session_start)
    question_elapsed = int(now - question_start)
    session_remaining = max(0, time_limit - session_elapsed)

    mins, secs = divmod(session_remaining, 60)

    # Determine timer class based on remaining time
    if session_remaining > time_limit * 0.2:
        timer_class = "primary"
    elif session_remaining > time_limit * 0.1:
        timer_class = "warning"
    else:
        timer_class = "danger"

    st.markdown(f"""
    <div class="timer-large timer-large-{timer_class}" style="margin: 10px 0;">
        <div class="timer-value timer-value-{timer_class}">{mins:02d}:{secs:02d}</div>
        <div class="score-label" style="margin-top: 8px;">
            This question: {question_elapsed}s | Suggested: {suggested_time}s
        </div>
    </div>
    """, unsafe_allow_html=True)


def _show_question_hint(question_type: str, marks: int):
    """Show technique hint for question type."""
    hints = {
        "multiple_choice": [
            "Read all options before choosing",
            "Eliminate obviously wrong answers",
            "Look for absolute words like 'always' or 'never'"
        ],
        "short_answer": [
            "Identify the command word (explain, describe, state)",
            "Be concise - aim for 1-3 sentences",
            f"For {marks} marks, make {marks} distinct points"
        ],
        "essay": [
            "Spend 2-3 minutes planning",
            "Use PEE/PEEL structure for paragraphs",
            "Link your conclusion back to the question"
        ]
    }
    tips = hints.get(question_type, ["Answer clearly and check your work"])
    for tip in tips:
        st.markdown(f"- {tip}")


def _submit_answer(session_id: int, question_idx: int, question: dict, answer: str, api_key: str):
    """Submit and evaluate an answer."""
    q_time = int(time.time() - st.session_state.technique_question_start)
    marks = question.get('marks', 1)
    suggested_time = int(marks * 90)  # 1.5 min per mark

    # Determine time status
    if q_time < suggested_time * 0.5:
        time_status = "rushed"
    elif q_time <= suggested_time * 1.5:
        time_status = "appropriate"
    else:
        time_status = "slow"

    # Evaluate answer
    correct_answer = question.get('correct_answer', '')
    q_type = question.get('question_type', 'short_answer')

    if q_type == "multiple_choice":
        is_correct = 1 if answer.upper() == correct_answer.upper() else 0
        marks_awarded = marks if is_correct else 0
    else:
        # For short answer and essay, use AI to evaluate
        is_correct, marks_awarded = _evaluate_answer(api_key, question, answer, marks)

    # Save response
    db.save_technique_response(
        session_id=session_id,
        question_number=question_idx + 1,
        question_type=q_type,
        question_text=question['question_text'],
        student_answer=answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        marks_awarded=marks_awarded,
        max_marks=marks,
        time_taken=q_time,
        time_status=time_status
    )

    # Move to next question
    st.session_state.technique_question_index += 1
    st.session_state.technique_question_start = time.time()


def _evaluate_answer(api_key: str, question: dict, answer: str, max_marks: int) -> tuple:
    """Use AI to evaluate short answer or essay."""
    if not api_key:
        return 0, 0

    prompt = f"""Evaluate this GCSE student's answer.

Question: {question['question_text']}
Correct Answer/Key Points: {question.get('correct_answer', 'N/A')}
Student Answer: {answer}
Maximum Marks: {max_marks}

Respond in JSON:
{{"marks_awarded": <0-{max_marks}>, "is_correct": <1 if marks > 50% else 0>}}"""

    try:
        result = call_claude(api_key, prompt, model='haiku')
        json_str = result
        if "```" in result:
            json_str = result.split("```")[1].split("```")[0]
            if json_str.startswith("json"):
                json_str = json_str[4:]
        data = json.loads(json_str.strip())
        return data.get('is_correct', 0), data.get('marks_awarded', 0)
    except Exception:
        # Default to partial credit
        return 0, max_marks // 2


def _complete_practice_session(api_key: str):
    """Complete session and generate AI review."""
    session_id = st.session_state.technique_session
    total_time = int(time.time() - st.session_state.technique_start_time)

    # Generate AI review
    ai_review = None
    if api_key:
        with st.spinner("Generating your technique analysis..."):
            ai_review = _generate_post_exam_review(api_key, session_id)

    # Complete session
    db.complete_technique_session(session_id, total_time, ai_review)

    # Store for review tab
    st.session_state.last_completed_session = session_id

    # Clear session state
    st.session_state.technique_session = None
    st.session_state.technique_questions = []
    st.session_state.technique_question_index = 0
    st.session_state.technique_start_time = None
    st.session_state.technique_question_start = None

    st.success("Practice session complete! Check the Post-Exam Review tab for your analysis.")
    st.rerun()


def _abandon_session():
    """Abandon current session."""
    if st.session_state.technique_session:
        db.update_technique_session(st.session_state.technique_session, status='abandoned')

    st.session_state.technique_session = None
    st.session_state.technique_questions = []
    st.session_state.technique_question_index = 0
    st.session_state.technique_start_time = None
    st.session_state.technique_question_start = None


def _generate_post_exam_review(api_key: str, session_id: int) -> str:
    """Generate AI post-exam technique analysis."""
    session = db.get_technique_session(session_id)
    responses = db.get_technique_responses(session_id)

    if not session or not responses:
        return None

    # Build question breakdown
    breakdown = []
    for r in responses:
        breakdown.append(
            f"Q{r['question_number']}: {r['question_type']} | "
            f"{r['marks_awarded']}/{r['max_marks']} marks | "
            f"{r['time_taken_seconds']}s ({r['time_status']})"
        )

    prompt = f"""Analyze this exam practice session and provide technique feedback.

Session: {session['subject_name']}
Score: {session['marks_achieved']}/{session['total_marks']} ({session['marks_achieved']*100//max(session['total_marks'],1)}%)
Time: {session['time_taken_seconds']}s / {session.get('time_limit_seconds', 'untimed')}s

Question Performance:
{chr(10).join(breakdown)}

Provide a technique-focused review. Respond in JSON:
{{
    "summary": "2-3 sentence overall assessment",
    "grade_equivalent": "A-G or 1-9",
    "technique_assessment": {{
        "time_management": {{
            "rating": "excellent|good|adequate|needs_work|poor",
            "observations": ["observation 1", "observation 2"],
            "improvement_tip": "specific tip"
        }},
        "answer_quality": {{
            "rating": "excellent|good|adequate|needs_work|poor",
            "observations": ["observation 1"],
            "improvement_tip": "specific tip"
        }},
        "question_interpretation": {{
            "rating": "excellent|good|adequate|needs_work|poor",
            "observations": ["observation 1"],
            "improvement_tip": "specific tip"
        }}
    }},
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["area 1", "area 2"],
    "next_session_focus": "recommendation for next practice"
}}"""

    try:
        result = call_claude(api_key, prompt, model='sonnet')
        return result
    except Exception:
        return None


# =============================================================================
# TAB 3: POST-EXAM REVIEW
# =============================================================================

def _render_post_exam_review_tab():
    """Render post-exam review interface."""
    st.markdown("### Post-Exam Review")
    st.markdown("Analyze your practice sessions to improve technique.")

    # Get recent sessions
    sessions = db.get_recent_technique_sessions(limit=10)

    if not sessions:
        st.info("Complete a practice session to see your review here.")
        return

    # Session selector
    session_options = {
        s['id']: f"{s['subject_name']} - {s['completed_at'][:10]} ({s['marks_achieved']}/{s['total_marks']})"
        for s in sessions
    }

    # Auto-select last completed if available
    default_session = st.session_state.get('last_completed_session', sessions[0]['id'])
    if default_session not in session_options:
        default_session = sessions[0]['id']

    selected_id = st.selectbox(
        "Select a session to review:",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x],
        index=list(session_options.keys()).index(default_id) if (default_id := default_session) in session_options else 0
    )

    _display_session_review(selected_id)


def _display_session_review(session_id: int):
    """Display detailed review of a completed session."""
    session = db.get_technique_session(session_id)
    responses = db.get_technique_responses(session_id)

    if not session:
        return

    # Score summary
    score_pct = session['marks_achieved'] * 100 // max(session['total_marks'], 1)

    # Get CSS class based on score
    if score_pct >= 80:
        score_class = "excellent"
    elif score_pct >= 65:
        score_class = "good"
    elif score_pct >= 50:
        score_class = "average"
    else:
        score_class = "poor"

    st.markdown(f"""
    <div class="score-card score-card-{score_class}">
        <h1 class="score-value score-value-{score_class}">{score_pct}%</h1>
        <p class="score-label">{session['marks_achieved']}/{session['total_marks']} marks</p>
        <p class="score-summary">{session['subject_name']} | {session['questions_answered']} questions</p>
    </div>
    """, unsafe_allow_html=True)

    # AI Review
    if session.get('ai_review'):
        st.markdown("### Technique Analysis")
        try:
            review_str = session['ai_review']
            if "```json" in review_str:
                review_str = review_str.split("```json")[1].split("```")[0]
            elif "```" in review_str:
                review_str = review_str.split("```")[1].split("```")[0]
            review = json.loads(review_str.strip())

            st.markdown(f"**{review.get('summary', '')}**")

            if review.get('grade_equivalent'):
                st.markdown(f"Estimated Grade: **{review['grade_equivalent']}**")

            # Technique breakdown
            if review.get('technique_assessment'):
                st.markdown("#### Technique Breakdown")
                _render_technique_breakdown(review['technique_assessment'])

            # Strengths and improvements
            col1, col2 = st.columns(2)
            with col1:
                if review.get('strengths'):
                    st.markdown("#### ✅ What Went Well")
                    for s in review['strengths']:
                        st.markdown(f"- {s}")
            with col2:
                if review.get('areas_to_improve'):
                    st.markdown("#### 🎯 Areas to Improve")
                    for a in review['areas_to_improve']:
                        st.markdown(f"- {a}")

            if review.get('next_session_focus'):
                st.info(f"**Next Session Focus:** {review['next_session_focus']}")

        except (json.JSONDecodeError, TypeError):
            st.markdown(session['ai_review'])

    # Question-by-question review
    if responses:
        st.markdown("### Question-by-Question Review")
        for r in responses:
            status_color = "#27ae60" if r['is_correct'] else "#e74c3c"
            time_color = {"rushed": "#e74c3c", "appropriate": "#27ae60", "slow": "#f39c12"}.get(r['time_status'], "#666")

            with st.expander(f"Q{r['question_number']}: {r['marks_awarded']}/{r['max_marks']} marks"):
                st.markdown(f"**Question:** {r['question_text']}")
                st.markdown(f"**Your Answer:** {r['student_answer']}")
                st.markdown(f"**Correct Answer:** {r['correct_answer']}")
                st.markdown(f"**Time:** {r['time_taken_seconds']}s "
                           f"<span style='color:{time_color}'>({r['time_status']})</span>",
                           unsafe_allow_html=True)


def _render_technique_breakdown(assessment: dict):
    """Render technique assessment breakdown."""
    # Map ratings to CSS classes
    rating_classes = {
        "excellent": ("a", "success"),
        "good": ("b", "success"),
        "adequate": ("c", "warning"),
        "needs_work": ("d", "warning"),
        "poor": ("f", "error")
    }

    for area, data in assessment.items():
        if not isinstance(data, dict):
            continue

        rating = data.get('rating', 'adequate')
        badge_class, card_class = rating_classes.get(rating, ("c", "info"))
        area_name = area.replace('_', ' ').title()

        st.markdown(f"""
        <div class="feedback-card feedback-card-{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong class="feedback-title">{area_name}</strong>
                <span class="grade-badge grade-badge-{badge_class}">{rating.replace('_', ' ')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if data.get('observations'):
            for obs in data['observations']:
                st.caption(f"• {obs}")
        if data.get('improvement_tip'):
            st.caption(f"💡 Tip: {data['improvement_tip']}")


# =============================================================================
# TAB 4: PROGRESS TRACKER
# =============================================================================

def _render_progress_tracker_tab():
    """Render progress tracking and analytics."""
    st.markdown("### Your Progress")
    st.markdown("Track your improvement over time.")

    # Subject filter
    subjects = db.get_all_subjects()
    subject_options = {"all": "All Subjects"} | {s['id']: s['name'] for s in subjects}
    selected = st.selectbox(
        "Filter by subject:",
        options=list(subject_options.keys()),
        format_func=lambda x: subject_options[x]
    )
    subject_filter = None if selected == "all" else selected

    # Get stats
    stats = db.get_technique_stats(subject_filter, days=30)
    progress = db.get_technique_progress_over_time(subject_filter, limit=20)
    type_stats = db.get_technique_by_question_type(subject_filter)

    # Overview metrics
    st.markdown("#### Last 30 Days")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sessions", stats['total_sessions'])
    with col2:
        st.metric("Avg Score", f"{stats['avg_score']:.0f}%")
    with col3:
        st.metric("Time Efficiency", f"{stats['time_efficiency']*100:.0f}%")
    with col4:
        accuracy = stats['total_correct'] * 100 // max(stats['total_questions'], 1)
        st.metric("Accuracy", f"{accuracy}%")

    st.markdown("---")

    # Score trend
    if progress:
        st.markdown("#### Score Trend")
        _render_score_trend(progress)

    st.markdown("---")

    # Performance by question type
    if type_stats:
        st.markdown("#### Performance by Question Type")
        _render_question_type_performance(type_stats)


def _render_score_trend(progress: list):
    """Render score progression."""
    if not progress:
        st.info("Complete more sessions to see your trend.")
        return

    # Simple text-based trend (reverse to show oldest first)
    progress = list(reversed(progress))
    scores = [p['score_pct'] for p in progress]

    # Calculate trend
    if len(scores) >= 3:
        first_half = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)
        second_half = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
        trend = "📈 Improving" if second_half > first_half + 5 else "📉 Declining" if second_half < first_half - 5 else "➡️ Stable"
        st.markdown(f"**Trend:** {trend}")

    # Display recent scores
    cols = st.columns(min(len(progress), 5))
    for i, (col, p) in enumerate(zip(cols, progress[-5:])):
        with col:
            score = p['score_pct']
            if score >= 80:
                score_class = "excellent"
            elif score >= 65:
                score_class = "good"
            elif score >= 50:
                score_class = "average"
            else:
                score_class = "poor"

            st.markdown(f"""
            <div class="score-card score-card-{score_class}" style="padding: 10px;">
                <div class="score-value score-value-{score_class}" style="font-size: 1.5rem;">{score:.0f}%</div>
                <div class="score-label">Session {i+1}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_question_type_performance(type_stats: list):
    """Render performance by question type."""
    if not type_stats:
        st.info("Answer more questions to see breakdown.")
        return

    for stat in type_stats:
        q_type = stat['question_type'] or 'unknown'
        total = stat['total'] or 0
        correct = stat['correct'] or 0

        pct = correct * 100 // max(total, 1)
        if pct >= 80:
            bar_class = "excellent"
        elif pct >= 65:
            bar_class = "good"
        elif pct >= 50:
            bar_class = "average"
        else:
            bar_class = "poor"

        st.markdown(f"""
        <div class="criteria-card">
            <div class="criteria-header">
                <span class="criteria-name">{q_type.replace('_', ' ').title()}</span>
                <span class="criteria-score score-value-{bar_class}">{correct}/{total} ({pct}%)</span>
            </div>
            <div class="criteria-bar">
                <div class="criteria-bar-fill criteria-bar-fill-{bar_class}" style="width: {pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
