"""
Study Assistant - Study Skills Coach Page
Learn effective note-taking methods, get AI feedback on notes, and master active learning techniques.
"""

import streamlit as st
import database as db
from utils import call_claude
import json


def render():
    """Render the Study Skills Coach page."""
    st.title("📚 Study Skills Coach")
    st.markdown("Master effective learning techniques for GCSE success.")

    # Seed methods on first load
    db.seed_study_methods()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Learn Methods",
        "🔍 Evaluate My Notes",
        "🧠 Active Learning",
        "📈 My Progress"
    ])

    with tab1:
        _render_methods_tab()

    with tab2:
        _render_evaluation_tab()

    with tab3:
        _render_active_learning_tab()

    with tab4:
        _render_progress_tab()


# =============================================================================
# TAB 1: LEARN METHODS
# =============================================================================

def _render_methods_tab():
    """Display note-taking methods with examples."""
    st.markdown("### Note-Taking Methods")
    st.markdown("Learn proven techniques to take better notes and retain more information.")

    # Get note-taking methods
    methods = db.get_study_methods(category="note_taking")

    if not methods:
        st.info("No methods available. Please check the database.")
        return

    # Method type filter
    method_types = list(set(m['method_type'] for m in methods))
    type_labels = {
        "cornell": "📋 Cornell Method",
        "outline": "📝 Outline Method",
        "mind_map": "🧠 Mind Mapping",
        "charting": "📊 Charting Method"
    }

    selected_type = st.selectbox(
        "Select a method to learn:",
        options=["all"] + method_types,
        format_func=lambda x: "All Methods" if x == "all" else type_labels.get(x, x.replace('_', ' ').title())
    )

    # Filter methods
    if selected_type != "all":
        methods = [m for m in methods if m['method_type'] == selected_type]

    # Display method cards
    for method in methods:
        _render_method_card(method)


def _render_method_card(method: dict):
    """Render a single method card."""
    method_icons = {
        "cornell": "📋",
        "outline": "📝",
        "mind_map": "🧠",
        "charting": "📊",
        "summarising": "✂️",
        "self_testing": "❓",
        "spaced_repetition": "🔄",
        "elaboration": "🔗"
    }

    icon = method_icons.get(method['method_type'], "📌")

    with st.expander(f"{icon} {method['title']}", expanded=False):
        st.markdown(f"**{method['description']}**")

        if method.get('when_to_use'):
            st.caption(f"Best for: {method['when_to_use']}")

        st.markdown("---")

        # Steps
        if method.get('steps'):
            st.markdown("**How to do it:**")
            try:
                steps = json.loads(method['steps']) if isinstance(method['steps'], str) else method['steps']
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. {step}")
            except (json.JSONDecodeError, TypeError):
                st.markdown(method['steps'])

        st.markdown("")

        # Tips
        if method.get('tips'):
            st.markdown("**Tips:**")
            try:
                tips = json.loads(method['tips']) if isinstance(method['tips'], str) else method['tips']
                for tip in tips:
                    st.markdown(f"- {tip}")
            except (json.JSONDecodeError, TypeError):
                st.markdown(method['tips'])

        # Example template
        if method.get('example_template'):
            st.markdown("---")
            st.markdown("**Example Template:**")
            st.code(method['example_template'], language='markdown')


# =============================================================================
# TAB 2: EVALUATE MY NOTES
# =============================================================================

def _render_evaluation_tab():
    """AI-powered note evaluation."""
    st.markdown("### Evaluate Your Notes")
    st.markdown("Paste your notes below and get AI feedback on how to improve them.")

    api_key = st.session_state.get('bubble_ace_api_key', '')

    if not api_key:
        st.warning("Add your Claude API key in Settings to use the note evaluation feature.")

    # Input form
    col1, col2 = st.columns(2)
    with col1:
        subjects = db.get_all_subjects()
        subject_options = {"none": "No subject"} | {s['id']: s['name'] for s in subjects}
        selected_subject = st.selectbox(
            "Subject (optional):",
            options=list(subject_options.keys()),
            format_func=lambda x: subject_options[x]
        )
        subject_id = None if selected_subject == "none" else selected_subject

    with col2:
        method_options = {
            "none": "Not sure / Mixed",
            "cornell": "Cornell Method",
            "outline": "Outline Method",
            "mind_map": "Mind Mapping",
            "charting": "Charting Method",
            "other": "Other method"
        }
        method_used = st.selectbox(
            "Method used (optional):",
            options=list(method_options.keys()),
            format_func=lambda x: method_options[x]
        )
        if method_used == "none":
            method_used = None

    # Notes input
    notes = st.text_area(
        "Paste your notes here:",
        height=250,
        placeholder="Enter or paste your study notes here...\n\nTip: The more notes you provide, the better feedback you'll receive!"
    )

    # Word count
    word_count = len(notes.split()) if notes else 0
    st.caption(f"Word count: {word_count}")

    if word_count < 20:
        st.info("Enter at least 20 words for meaningful feedback.")

    st.markdown("---")

    if st.button("🔍 Evaluate My Notes", type="primary", use_container_width=True, disabled=not api_key or word_count < 20):
        with st.spinner("Analysing your notes..."):
            feedback = _evaluate_notes(api_key, subject_id, method_used, notes, word_count)

        if feedback:
            # Save evaluation
            db.save_note_evaluation(
                subject_id=subject_id,
                method_used=method_used,
                note_content=notes[:1000],  # Store first 1000 chars
                word_count=word_count,
                overall_score=feedback.get('overall_score', 0),
                feedback_json=json.dumps(feedback)
            )

            # Store in session for display
            st.session_state.note_feedback = feedback
            st.rerun()

    # Display results if available
    if st.session_state.get('note_feedback'):
        _display_evaluation_results(st.session_state.note_feedback)


def _evaluate_notes(api_key: str, subject_id: int, method_used: str, notes: str, word_count: int) -> dict:
    """Evaluate notes using AI."""
    subject_name = "General"
    if subject_id:
        subject = db.get_subject_by_id(subject_id)
        if subject:
            subject_name = subject['name']

    method_context = f"The student used the {method_used.replace('_', ' ')} method." if method_used else "The student did not specify a note-taking method."

    prompt = f"""You are an expert study skills coach for GCSE students.

Evaluate these study notes and provide detailed, encouraging feedback to help the student improve.

Subject: {subject_name}
{method_context}
Word Count: {word_count}

Notes:
{notes}

Evaluate the notes on these criteria (score each 1-10):
1. Organisation - Clear structure, logical flow, easy to navigate
2. Completeness - Key concepts covered, sufficient detail
3. Clarity - Easy to understand, good explanations
4. Conciseness - Not too wordy, well-summarised
5. Usefulness - Good for revision, includes examples where helpful

Respond in JSON format:
{{
    "overall_score": 72,
    "summary": "2-3 sentence encouraging assessment of the notes quality",
    "criteria_scores": {{
        "organisation": {{"score": 8, "max": 10, "comment": "Specific feedback"}},
        "completeness": {{"score": 7, "max": 10, "comment": "Specific feedback"}},
        "clarity": {{"score": 7, "max": 10, "comment": "Specific feedback"}},
        "conciseness": {{"score": 6, "max": 10, "comment": "Specific feedback"}},
        "usefulness": {{"score": 8, "max": 10, "comment": "Specific feedback"}}
    }},
    "strengths": [
        "Specific strength 1",
        "Specific strength 2"
    ],
    "improvements": [
        {{
            "area": "organisation",
            "issue": "What could be better",
            "suggestion": "How to improve it",
            "example": "Brief example of the improvement"
        }}
    ],
    "recommended_method": "cornell",
    "method_tip": "Why this method would work well for this type of content",
    "next_steps": [
        "Actionable suggestion 1",
        "Actionable suggestion 2",
        "Actionable suggestion 3"
    ]
}}

Be encouraging but honest. Focus on specific, actionable feedback."""

    system_prompt = """You are an encouraging study skills coach for GCSE students.
Give constructive feedback that helps students improve their note-taking.
Use British English. Be specific about what works and what needs improvement.
Always be encouraging - students should feel motivated to improve, not discouraged."""

    try:
        result = call_claude(api_key, prompt, system=system_prompt, model='sonnet')

        # Parse JSON
        json_str = result
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0]

        return json.loads(json_str.strip())
    except Exception as e:
        st.error(f"Couldn't evaluate notes: {e}. Check your API key in **Settings** and try again.")
        return None


def _get_score_class(score: int) -> str:
    """Get CSS class based on score."""
    if score >= 80:
        return "excellent"
    elif score >= 65:
        return "good"
    elif score >= 50:
        return "average"
    elif score >= 35:
        return "below"
    else:
        return "poor"


def _display_evaluation_results(feedback: dict):
    """Display note evaluation feedback."""
    st.markdown("### Your Results")

    # Score card
    score = feedback.get('overall_score', 0)
    score_class = _get_score_class(score)

    st.markdown(f"""
    <div class="score-card score-card-{score_class}">
        <h1 class="score-value score-value-{score_class}">{score}%</h1>
        <p class="score-summary">{feedback.get('summary', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Criteria breakdown
    if feedback.get('criteria_scores'):
        st.markdown("#### Criteria Breakdown")
        for criteria, data in feedback['criteria_scores'].items():
            if not isinstance(data, dict):
                continue
            score_val = data.get('score', 0)
            max_val = data.get('max', 10)
            pct = (score_val / max_val) * 100
            bar_class = _get_score_class(int(pct))

            st.markdown(f"""
            <div class="criteria-card">
                <div class="criteria-header">
                    <span class="criteria-name">{criteria.replace('_', ' ').title()}</span>
                    <span class="criteria-score score-value-{bar_class}">{score_val}/{max_val}</span>
                </div>
                <div class="criteria-bar">
                    <div class="criteria-bar-fill criteria-bar-fill-{bar_class}" style="width: {pct}%;"></div>
                </div>
                <p class="criteria-comment">{data.get('comment', '')}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Strengths and improvements
    col1, col2 = st.columns(2)

    with col1:
        if feedback.get('strengths'):
            st.markdown("#### ✅ What's Working Well")
            for strength in feedback['strengths']:
                st.markdown(f"- {strength}")

    with col2:
        if feedback.get('improvements'):
            st.markdown("#### 🎯 Areas to Improve")
            for imp in feedback['improvements']:
                if isinstance(imp, dict):
                    st.markdown(f"**{imp.get('area', '').replace('_', ' ').title()}**")
                    st.markdown(f"- Issue: {imp.get('issue', '')}")
                    st.markdown(f"- Try: {imp.get('suggestion', '')}")
                    if imp.get('example'):
                        st.caption(f"Example: {imp['example']}")
                else:
                    st.markdown(f"- {imp}")

    # Recommended method
    if feedback.get('recommended_method'):
        method_labels = {
            "cornell": "Cornell Method",
            "outline": "Outline Method",
            "mind_map": "Mind Mapping",
            "charting": "Charting Method"
        }
        method_name = method_labels.get(feedback['recommended_method'], feedback['recommended_method'])
        st.info(f"**Recommended Method:** {method_name}\n\n{feedback.get('method_tip', '')}")

    # Next steps
    if feedback.get('next_steps'):
        st.markdown("#### 📋 Next Steps")
        for i, step in enumerate(feedback['next_steps'], 1):
            st.markdown(f"{i}. {step}")

    # Clear button
    if st.button("Clear Results", key="clear_note_feedback"):
        st.session_state.note_feedback = None
        st.rerun()


# =============================================================================
# TAB 3: ACTIVE LEARNING
# =============================================================================

def _render_active_learning_tab():
    """Active learning techniques."""
    st.markdown("### Active Learning Techniques")
    st.markdown("Go beyond passive reading - use these proven techniques to learn more effectively.")

    # Get active learning methods
    methods = db.get_study_methods(category="active_learning")

    if not methods:
        st.info("No techniques available.")
        return

    # Display technique cards
    for method in methods:
        _render_method_card(method)

    st.markdown("---")

    # Integration suggestions
    st.markdown("### 🔗 Use These With Other Features")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Self-Testing + Flashcards**

        Use the Flashcards feature for quick retrieval practice.
        The spaced repetition system automatically schedules reviews at optimal intervals!
        """)

    with col2:
        st.markdown("""
        **Spaced Repetition + Focus Timer**

        Use the Focus Timer for dedicated revision sessions.
        The Pomodoro technique pairs perfectly with spaced review!
        """)


# =============================================================================
# TAB 4: MY PROGRESS
# =============================================================================

def _render_progress_tab():
    """Track study skills improvement."""
    st.markdown("### Your Progress")
    st.markdown("Track your note-taking improvement over time.")

    # Get stats
    stats = db.get_note_evaluation_stats()
    evaluations = db.get_note_evaluations(limit=10)

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Evaluations", stats['total_evaluations'])
    with col2:
        st.metric("Average Score", f"{stats['avg_score']:.0f}%")
    with col3:
        st.metric("Best Score", f"{stats['best_score']}%")
    with col4:
        st.metric("Recent Score", f"{evaluations[0]['overall_score']}%" if evaluations else "N/A")

    st.markdown("---")

    # Recent evaluations
    if evaluations:
        st.markdown("#### Recent Evaluations")

        for eval_item in evaluations:
            score = eval_item['overall_score']
            color = "#27ae60" if score >= 70 else "#f39c12" if score >= 50 else "#e74c3c"
            subject = eval_item.get('subject_name', 'General')
            method = eval_item.get('method_used', 'Not specified')
            date_str = eval_item['created_at'][:10] if eval_item.get('created_at') else 'Unknown'

            with st.expander(f"{date_str} - {subject} ({score}%)"):
                st.markdown(f"**Method:** {method.replace('_', ' ').title() if method else 'Not specified'}")
                st.markdown(f"**Word Count:** {eval_item.get('word_count', 'N/A')}")

                # Show feedback summary if available
                if eval_item.get('feedback_json'):
                    try:
                        feedback = json.loads(eval_item['feedback_json'])
                        if feedback.get('summary'):
                            st.markdown(f"**Summary:** {feedback['summary']}")
                    except (json.JSONDecodeError, TypeError):
                        pass

                # Delete button
                if st.button("🗑️ Delete", key=f"del_eval_{eval_item['id']}"):
                    db.delete_note_evaluation(eval_item['id'])
                    st.rerun()

        # Score trend (simple text display)
        if len(evaluations) >= 3:
            scores = [e['overall_score'] for e in evaluations]
            first_half = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
            second_half = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)

            if second_half > first_half + 5:
                st.success("📈 Your note quality is improving! Keep up the great work.")
            elif second_half < first_half - 5:
                st.warning("📉 Your recent scores are lower. Check out the Learn Methods tab for tips!")
            else:
                st.info("➡️ Your scores are stable. Try a new note-taking method to boost your skills!")
    else:
        st.info("No evaluations yet. Use the 'Evaluate My Notes' tab to get your first feedback!")
