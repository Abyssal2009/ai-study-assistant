"""
Study Assistant - Essay Writing Tutor Page
AI-powered essay grading with structured feedback and improvement suggestions.
"""

import streamlit as st
import database as db
from utils import call_claude
from datetime import datetime
import json


def render():
    """Render the Essay Writing Tutor page."""
    st.title("📝 Essay Writing Tutor")
    st.markdown("**Get detailed feedback on your essays with AI-powered grading.**")

    # Check for API key
    api_key = st.session_state.get('bubble_ace_api_key', '')
    if not api_key:
        st.warning("Please add your Claude API key in Settings to use the Essay Tutor.")
        st.info("Go to **Settings** > **API Keys** to add your key.")
        st.stop()

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "📤 Submit & Grade",
        "📋 Detailed Feedback",
        "📚 History"
    ])

    with tab1:
        _render_submit_tab(api_key)

    with tab2:
        _render_feedback_tab()

    with tab3:
        _render_history_tab()


def _render_submit_tab(api_key: str):
    """Render the Submit & Grade tab."""
    st.markdown("### Submit Your Essay")

    # Subject selection
    subjects = db.get_all_subjects()
    subject_options = [{"id": None, "name": "No subject (general essay)"}] + subjects
    selected_subject = st.selectbox(
        "Subject (optional):",
        options=subject_options,
        format_func=lambda x: x['name'],
        key="essay_subject"
    )

    # Essay question/prompt
    essay_question = st.text_input(
        "Essay Question or Prompt:",
        placeholder="e.g., Discuss the causes of World War I...",
        key="essay_question"
    )

    # Essay title (optional)
    essay_title = st.text_input(
        "Essay Title (optional):",
        placeholder="e.g., The Causes and Consequences of WWI",
        key="essay_title"
    )

    # Essay text
    essay_text = st.text_area(
        "Your Essay:",
        height=400,
        placeholder="Paste or type your essay here...",
        key="essay_text"
    )

    # Word count
    word_count = len(essay_text.split()) if essay_text.strip() else 0
    col1, col2 = st.columns([1, 3])
    with col1:
        if word_count < 200 and word_count > 0:
            st.warning(f"**{word_count}** words (quite short)")
        elif word_count > 2000:
            st.warning(f"**{word_count}** words (quite long)")
        elif word_count > 0:
            st.info(f"**{word_count}** words")
        else:
            st.caption("0 words")

    # Grade button
    st.markdown("---")
    if st.button("🎯 Grade My Essay", type="primary", disabled=len(essay_text.strip()) < 50):
        if len(essay_text.strip()) < 50:
            st.error("Please enter at least 50 characters of essay text.")
        else:
            _grade_essay(
                api_key=api_key,
                subject=selected_subject,
                question=essay_question,
                title=essay_title or "Untitled Essay",
                text=essay_text,
                word_count=word_count
            )

    # Show current feedback if available
    if 'essay_feedback' in st.session_state and st.session_state.essay_feedback:
        st.markdown("---")
        _display_grade_summary(st.session_state.essay_feedback)


def _grade_essay(api_key: str, subject: dict, question: str, title: str,
                 text: str, word_count: int):
    """Grade the essay using AI."""
    subject_name = subject['name'] if subject['id'] else "General"

    # Build the grading prompt
    prompt = f"""You are an experienced GCSE examiner for {subject_name}.

Grade this essay and provide detailed, constructive feedback.

Essay Question: {question if question else "Not specified"}
Essay Text:
{text}

Word Count: {word_count}

Respond in JSON format with this exact structure:
{{
    "grade": "B",
    "overall_score": 72,
    "summary": "A brief 2-3 sentence overall assessment of the essay's strengths and main areas for improvement.",
    "criteria_scores": {{
        "content_knowledge": {{"score": 8, "max": 10, "comment": "Brief comment on content accuracy and depth"}},
        "analysis_evaluation": {{"score": 7, "max": 10, "comment": "Brief comment on analytical skills"}},
        "structure_organisation": {{"score": 7, "max": 10, "comment": "Brief comment on essay structure"}},
        "written_communication": {{"score": 8, "max": 10, "comment": "Brief comment on clarity and language"}}
    }},
    "sections": {{
        "introduction": {{
            "rating": "good",
            "strengths": ["Specific strength 1", "Specific strength 2"],
            "improvements": ["Specific improvement needed"]
        }},
        "body_paragraphs": {{
            "rating": "adequate",
            "strengths": ["Specific strength"],
            "improvements": ["Specific improvement 1", "Specific improvement 2"]
        }},
        "conclusion": {{
            "rating": "needs_work",
            "strengths": ["Specific strength"],
            "improvements": ["Specific improvement"]
        }}
    }},
    "issues": [
        {{"type": "structure", "severity": "medium", "description": "Specific issue with the essay structure"}},
        {{"type": "evidence", "severity": "high", "description": "Specific issue with evidence or examples"}}
    ],
    "actionable_suggestions": [
        "Specific, numbered suggestion 1",
        "Specific, numbered suggestion 2",
        "Specific, numbered suggestion 3",
        "Specific, numbered suggestion 4",
        "Specific, numbered suggestion 5"
    ]
}}

Ratings for sections should be one of: "excellent", "good", "adequate", "needs_work", "poor"
Issue severity should be one of: "high", "medium", "low"
Issue types should be one of: "structure", "clarity", "evidence", "analysis", "language", "relevance"

Be specific and constructive. Reference actual parts of the essay in your feedback."""

    system_prompt = f"You are a helpful and encouraging GCSE {subject_name} examiner. Give honest but constructive feedback that helps students improve."

    with st.spinner("Analysing your essay..."):
        result = call_claude(api_key, prompt, system=system_prompt, model='sonnet')

        if result.startswith("Error:"):
            st.error(f"Failed to grade essay: {result}")
            return

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = result
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0]

            feedback = json.loads(json_str.strip())

            # Store in session state
            st.session_state.essay_feedback = feedback
            st.session_state.essay_text = text
            st.session_state.essay_question = question

            # Save to database
            subject_id = subject['id'] if subject['id'] else None
            db.save_essay_submission(
                subject_id=subject_id,
                title=title,
                question=question,
                text=text,
                word_count=word_count,
                grade=feedback.get('grade', 'N/A'),
                overall_score=feedback.get('overall_score', 0),
                feedback_json=json.dumps(feedback)
            )

            st.success("Essay graded successfully!")
            st.rerun()

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response. Please try again.")
            with st.expander("Raw response"):
                st.code(result)


def _display_grade_summary(feedback: dict):
    """Display the grade summary card."""
    grade = feedback.get('grade', 'N/A')
    score = feedback.get('overall_score', 0)
    summary = feedback.get('summary', '')

    # Grade colour
    grade_colors = {
        'A*': '#27ae60', 'A': '#2ecc71', '9': '#27ae60', '8': '#2ecc71',
        'B': '#3498db', '7': '#3498db', '6': '#3498db',
        'C': '#f39c12', '5': '#f39c12', '4': '#f39c12',
        'D': '#e67e22', '3': '#e67e22',
        'E': '#e74c3c', 'F': '#e74c3c', '2': '#e74c3c', '1': '#e74c3c',
        'U': '#95a5a6', '0': '#95a5a6'
    }
    grade_color = grade_colors.get(grade, '#3498db')

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {grade_color}22, {grade_color}11);
                border: 2px solid {grade_color};
                padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 3.5rem; margin: 0; color: {grade_color};">{grade}</h1>
        <p style="font-size: 1.3rem; margin: 10px 0; color: #333;">{score}/100</p>
        <p style="color: #666; font-size: 0.95rem; margin-top: 15px;">{summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # Criteria scores
    st.markdown("#### Score Breakdown")
    criteria_scores = feedback.get('criteria_scores', {})

    for criteria, data in criteria_scores.items():
        score_val = data.get('score', 0)
        max_val = data.get('max', 10)
        comment = data.get('comment', '')
        pct = (score_val / max_val * 100) if max_val > 0 else 0

        # Colour based on percentage
        if pct >= 80:
            bar_color = "#2ecc71"
        elif pct >= 60:
            bar_color = "#3498db"
        elif pct >= 40:
            bar_color = "#f39c12"
        else:
            bar_color = "#e74c3c"

        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="font-weight: 500;">{criteria.replace('_', ' ').title()}</span>
                <span style="font-weight: bold; color: {bar_color};">{score_val}/{max_val}</span>
            </div>
            <div style="background: #eee; height: 10px; border-radius: 5px; overflow: hidden;">
                <div style="background: {bar_color}; width: {pct}%; height: 100%;"></div>
            </div>
            <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">{comment}</p>
        </div>
        """, unsafe_allow_html=True)


def _render_feedback_tab():
    """Render the Detailed Feedback tab."""
    st.markdown("### Detailed Feedback")

    if 'essay_feedback' not in st.session_state or not st.session_state.essay_feedback:
        st.info("Submit an essay in the 'Submit & Grade' tab to see detailed feedback here.")
        return

    feedback = st.session_state.essay_feedback

    # Section-by-section analysis
    sections = feedback.get('sections', {})

    for section_name, section_data in sections.items():
        rating = section_data.get('rating', 'unknown')
        strengths = section_data.get('strengths', [])
        improvements = section_data.get('improvements', [])

        # Rating colours
        rating_colors = {
            'excellent': '#27ae60',
            'good': '#2ecc71',
            'adequate': '#f39c12',
            'needs_work': '#e67e22',
            'poor': '#e74c3c'
        }
        rating_color = rating_colors.get(rating, '#3498db')

        st.markdown(f"""
        <div style="background: {rating_color}11; border-left: 4px solid {rating_color};
                    padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #333;">{section_name.replace('_', ' ').title()}</h4>
                <span style="background: {rating_color}; color: white; padding: 3px 10px;
                            border-radius: 12px; font-size: 12px; text-transform: uppercase;">
                    {rating.replace('_', ' ')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Strengths:**")
            for strength in strengths:
                st.markdown(f"- {strength}")
        with col2:
            st.markdown("**Areas to Improve:**")
            for improvement in improvements:
                st.markdown(f"- {improvement}")

        st.markdown("")

    # Issues
    st.markdown("---")
    st.markdown("### Issues Identified")

    issues = feedback.get('issues', [])
    if issues:
        severity_colors = {
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#3498db'
        }

        for issue in issues:
            issue_type = issue.get('type', 'general')
            severity = issue.get('severity', 'medium')
            description = issue.get('description', '')
            color = severity_colors.get(severity, '#3498db')

            st.markdown(f"""
            <div style="background: {color}11; border-left: 3px solid {color};
                        padding: 12px; margin-bottom: 10px; border-radius: 0 6px 6px 0;">
                <div style="margin-bottom: 5px;">
                    <span style="background: {color}; color: white; padding: 2px 8px;
                                border-radius: 4px; font-size: 11px; text-transform: uppercase;
                                margin-right: 8px;">{severity}</span>
                    <span style="background: #f0f0f0; color: #666; padding: 2px 8px;
                                border-radius: 4px; font-size: 11px; text-transform: uppercase;">
                        {issue_type}
                    </span>
                </div>
                <p style="margin: 5px 0 0 0; color: #333;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No major issues identified!")

    # Actionable suggestions
    st.markdown("---")
    st.markdown("### Actionable Suggestions")

    suggestions = feedback.get('actionable_suggestions', [])
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 12px 15px; margin-bottom: 8px;
                        border-radius: 8px; display: flex; align-items: flex-start;">
                <span style="background: #3498db; color: white; min-width: 24px; height: 24px;
                            border-radius: 50%; display: flex; align-items: center;
                            justify-content: center; font-size: 12px; margin-right: 12px;">
                    {i}
                </span>
                <span style="color: #333;">{suggestion}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific suggestions available.")


def _render_history_tab():
    """Render the History tab."""
    st.markdown("### Essay History")

    # Get submissions
    submissions = db.get_essay_submissions(limit=20)

    if not submissions:
        st.info("No essay submissions yet. Submit an essay to start building your history!")
        return

    # Stats summary
    stats = db.get_essay_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Essays", int(stats.get('total_essays', 0) or 0))
    with col2:
        avg_score = stats.get('avg_score', 0)
        st.metric("Avg Score", f"{avg_score:.0f}" if avg_score else "N/A")
    with col3:
        best = stats.get('best_score', 0)
        st.metric("Best Score", best if best else "N/A")
    with col4:
        avg_words = stats.get('avg_word_count', 0)
        st.metric("Avg Words", f"{avg_words:.0f}" if avg_words else "N/A")

    st.markdown("---")

    # List submissions
    for submission in submissions:
        grade = submission.get('grade', 'N/A')
        score = submission.get('overall_score', 0)
        title = submission.get('essay_title', 'Untitled')
        subject_name = submission.get('subject_name', 'General')
        subject_colour = submission.get('subject_colour', '#3498db')
        word_count = submission.get('word_count', 0)
        submitted = submission.get('submitted_at', '')

        # Format date
        if submitted:
            try:
                dt = datetime.fromisoformat(submitted)
                date_str = dt.strftime("%d %b %Y, %H:%M")
            except ValueError:
                date_str = submitted[:16]
        else:
            date_str = "Unknown"

        # Grade colour
        grade_colors = {
            'A*': '#27ae60', 'A': '#2ecc71', '9': '#27ae60', '8': '#2ecc71',
            'B': '#3498db', '7': '#3498db', '6': '#3498db',
            'C': '#f39c12', '5': '#f39c12', '4': '#f39c12',
            'D': '#e67e22', '3': '#e67e22',
            'E': '#e74c3c', 'F': '#e74c3c', '2': '#e74c3c', '1': '#e74c3c'
        }
        grade_color = grade_colors.get(grade, '#95a5a6')

        st.markdown(f"""
        <div style="background: #f8f9fa; border-left: 4px solid {subject_colour};
                    padding: 15px; margin-bottom: 10px; border-radius: 0 8px 8px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 1.1rem;">{title}</strong>
                    <span style="background: {subject_colour}; color: white; padding: 2px 8px;
                                border-radius: 12px; font-size: 11px; margin-left: 10px;">
                        {subject_name}
                    </span>
                </div>
                <div style="text-align: right;">
                    <span style="background: {grade_color}; color: white; padding: 5px 12px;
                                border-radius: 8px; font-weight: bold; font-size: 1.1rem;">
                        {grade}
                    </span>
                    <span style="color: #666; margin-left: 10px;">{score}/100</span>
                </div>
            </div>
            <p style="color: #666; font-size: 0.85rem; margin: 8px 0 0 0;">
                {word_count} words | {date_str}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # View/Delete buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("👁️ View", key=f"view_{submission['id']}"):
                _load_essay_feedback(submission)
        with col2:
            if st.button("🗑️", key=f"delete_{submission['id']}"):
                db.delete_essay_submission(submission['id'])
                st.success("Essay deleted")
                st.rerun()


def _load_essay_feedback(submission: dict):
    """Load essay feedback into session state for viewing."""
    try:
        feedback_json = submission.get('feedback_json', '{}')
        feedback = json.loads(feedback_json)
        st.session_state.essay_feedback = feedback
        st.session_state.essay_text = submission.get('essay_text', '')
        st.session_state.essay_question = submission.get('essay_question', '')
        st.success("Feedback loaded! Switch to 'Detailed Feedback' tab to view.")
    except json.JSONDecodeError:
        st.error("Could not load feedback for this essay.")
