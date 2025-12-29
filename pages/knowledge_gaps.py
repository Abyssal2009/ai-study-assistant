"""
Study Assistant - Knowledge Gap Assessment Page
Identify knowledge gaps and track mastery over time.
"""

import streamlit as st
import database as db
import json
import time
from datetime import date


def render():
    """Render the Knowledge Gap Assessment page."""
    st.title("🎯 Knowledge Gap Assessment")
    st.markdown("Identify what you know, discover what you need to learn.")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Check for API key
    api_key = st.session_state.get('bubble_ace_api_key', '')

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 Assessment Quiz",
        "🔍 Gap Analysis",
        "📊 Progress Report"
    ])

    with tab1:
        _render_assessment_tab(subjects, api_key)

    with tab2:
        _render_gap_analysis_tab(subjects, api_key)

    with tab3:
        _render_progress_report_tab(subjects)


def _render_assessment_tab(subjects, api_key):
    """Render the assessment quiz tab."""

    # Check for in-progress assessment
    if st.session_state.get('current_assessment'):
        _render_active_assessment(api_key)
        return

    st.markdown("### Start New Assessment")

    if not api_key:
        st.warning("Set your Claude API key in Settings to enable AI-generated questions.")

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox(
            "Subject *",
            options=subjects,
            format_func=lambda x: x['name'],
            key="assessment_subject"
        )

        assessment_types = [
            ("quick", "Quick Check (5 questions)"),
            ("comprehensive", "Comprehensive (15 questions)"),
            ("topic_focused", "Topic Focused (10 questions)")
        ]
        assessment_type = st.selectbox(
            "Assessment Type",
            options=assessment_types,
            format_func=lambda x: x[1],
            key="assessment_type"
        )

    with col2:
        selected_topics = []
        if assessment_type[0] == "topic_focused":
            topics = db.get_available_topics_for_subject(subject['id'])
            if topics:
                selected_topics = st.multiselect(
                    "Select Topics",
                    options=topics,
                    key="selected_topics"
                )
            else:
                st.info("No topics available. Add past papers or flashcards first.")

        question_source = st.radio(
            "Question Source",
            ["AI Generated", "Mixed"],
            horizontal=True,
            key="question_source"
        )

    st.markdown("---")

    # Start button
    can_start = api_key and (assessment_type[0] != "topic_focused" or selected_topics)

    if st.button("🚀 Start Assessment", type="primary", disabled=not can_start):
        with st.spinner("Generating questions..."):
            assessment_id = _create_and_populate_assessment(
                subject['id'],
                assessment_type[0],
                question_source,
                selected_topics,
                api_key,
                subject['name']
            )
            if assessment_id:
                st.session_state.current_assessment = assessment_id
                st.session_state.assessment_index = 0
                st.session_state.assessment_start_time = time.time()
                st.rerun()
            else:
                st.error("Failed to create assessment. Please try again.")

    # Recent assessments
    st.markdown("---")
    st.markdown("### Recent Assessments")

    recent = db.get_assessments_by_subject(subject['id'], limit=5)
    if recent:
        for assessment in recent:
            status_icon = "✅" if assessment['status'] == 'completed' else "⏳"
            score_text = f"{assessment['score_percentage']:.0f}%" if assessment['score_percentage'] else "In progress"

            with st.expander(f"{status_icon} {assessment['assessment_type'].title()} - {score_text}"):
                st.caption(f"Started: {assessment['started_at']}")
                if assessment['status'] == 'completed':
                    st.caption(f"Score: {assessment['correct_answers']}/{assessment['total_questions']}")
                    if assessment['ai_feedback']:
                        st.markdown("**AI Feedback:**")
                        st.markdown(assessment['ai_feedback'])
    else:
        st.info("No assessments yet. Start one above!")


def _render_active_assessment(api_key):
    """Render an in-progress assessment."""

    assessment_id = st.session_state.current_assessment
    assessment = db.get_assessment_by_id(assessment_id)

    if not assessment:
        st.session_state.current_assessment = None
        st.rerun()
        return

    questions = db.get_assessment_questions(assessment_id)
    current_idx = st.session_state.get('assessment_index', 0)

    # Check if assessment is complete
    if current_idx >= len(questions):
        _complete_assessment(assessment_id, api_key)
        return

    question = questions[current_idx]

    # Progress bar
    progress = current_idx / len(questions)
    st.progress(progress, text=f"Question {current_idx + 1} of {len(questions)}")

    # Question card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea22, #764ba222);
                border-left: 4px solid #667eea;
                padding: 20px;
                border-radius: 0 12px 12px 0;
                margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span style="background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                {question['topic']}
            </span>
            <span style="color: #666; font-size: 12px;">
                {question['difficulty'].title()} | {question['marks']} mark(s)
            </span>
        </div>
        <h3 style="margin: 10px 0; color: #333;">{question['question_text']}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Answer input based on question type
    answer = None

    if question['question_type'] == 'multiple_choice':
        options = json.loads(question['options']) if question['options'] else []
        if options:
            answer = st.radio(
                "Select your answer:",
                options,
                key=f"answer_{question['id']}"
            )
    elif question['question_type'] == 'true_false':
        answer = st.radio(
            "True or False?",
            ["True", "False"],
            key=f"answer_{question['id']}"
        )
    else:  # short_answer
        answer = st.text_area(
            "Your answer:",
            key=f"answer_{question['id']}",
            height=100
        )

    # Confidence slider
    confidence = st.slider(
        "How confident are you?",
        min_value=1,
        max_value=5,
        value=3,
        key=f"confidence_{question['id']}",
        help="1 = Guessing, 5 = Very confident"
    )

    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("✓ Submit Answer", type="primary", disabled=not answer):
            _submit_answer(assessment_id, question, answer, confidence, api_key)
            st.session_state.assessment_index = current_idx + 1
            st.rerun()

    with col2:
        if st.button("⏭ Skip"):
            st.session_state.assessment_index = current_idx + 1
            st.rerun()

    with col3:
        if st.button("🚪 Exit"):
            if st.session_state.get('confirm_exit'):
                st.session_state.current_assessment = None
                st.session_state.assessment_index = 0
                st.session_state.confirm_exit = False
                st.rerun()
            else:
                st.session_state.confirm_exit = True
                st.warning("Click Exit again to confirm")


def _render_gap_analysis_tab(subjects, api_key):
    """Render the gap analysis tab."""

    st.markdown("### Knowledge Gap Analysis")
    st.markdown("Compare what you know against what the exam requires.")

    # Subject filter
    filter_subject = st.selectbox(
        "Filter by subject:",
        options=[None] + subjects,
        format_func=lambda x: "All Subjects" if x is None else x['name'],
        key="gap_subject_filter"
    )
    subject_id = filter_subject['id'] if filter_subject else None

    # Sync button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Sync from Past Papers"):
            db.sync_exam_requirements_from_papers(subject_id)
            st.success("Exam requirements synced!")
            st.rerun()

    # Coverage overview
    coverage = db.get_coverage_stats(subject_id)

    st.markdown("---")
    st.markdown("#### Coverage Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Exam Topics", coverage['total_exam_topics'])
    with col2:
        st.metric("Topics Assessed", coverage['topics_assessed'])
    with col3:
        st.metric("Topics Mastered", coverage['topics_mastered'])
    with col4:
        pct = coverage['coverage_percentage']
        color = "normal" if pct >= 50 else "off"
        st.metric("Coverage", f"{pct:.0f}%", delta_color=color)

    st.markdown("---")

    # Gap visualization
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Knowledge Gaps")
        gaps = db.get_knowledge_gaps(subject_id)
        if gaps:
            for gap in gaps[:10]:
                urgency_color = _get_gap_urgency_color(gap)
                st.markdown(f"""
                <div style="border-left: 4px solid {urgency_color}; padding: 10px; margin: 5px 0; background: #fafafa; border-radius: 0 8px 8px 0;">
                    <strong>{gap['topic']}</strong><br>
                    <small style="color: #666;">
                        Exam frequency: {gap['frequency']}x |
                        Current mastery: {gap['mastery_level']:.0f}% |
                        Importance: {gap['importance_level'].title()}
                    </small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No significant gaps identified!")

    with col2:
        st.markdown("#### 🟢 Strengths")
        strengths = db.get_strong_topics(subject_id)
        if strengths:
            for strength in strengths[:10]:
                st.markdown(f"""
                <div style="border-left: 4px solid #27ae60; padding: 10px; margin: 5px 0; background: #f0fff4; border-radius: 0 8px 8px 0;">
                    <strong>{strength['topic']}</strong><br>
                    <small style="color: #666;">
                        Mastery: {strength['mastery_level']:.0f}% |
                        Attempts: {strength['total_attempts']}
                    </small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Complete some assessments to identify strengths.")

    # AI Gap Analysis
    st.markdown("---")
    st.markdown("#### 🤖 AI Gap Analysis")

    if not api_key:
        st.warning("Set your Claude API key in Settings to enable AI analysis.")
    elif st.button("Generate AI Analysis", type="primary"):
        with st.spinner("Analyzing your knowledge gaps..."):
            analysis = _generate_ai_gap_analysis(subject_id, api_key)
            if analysis:
                st.markdown(analysis)
            else:
                st.error("Failed to generate analysis. Please try again.")


def _render_progress_report_tab(subjects):
    """Render the progress report tab."""

    st.markdown("### Progress Report")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        filter_subject = st.selectbox(
            "Filter by subject:",
            options=[None] + subjects,
            format_func=lambda x: "All Subjects" if x is None else x['name'],
            key="progress_subject_filter"
        )
        subject_id = filter_subject['id'] if filter_subject else None

    with col2:
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            key="time_period"
        )
        days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": 365}
        days = days_map[time_period]

    # Overview stats
    stats = db.get_assessment_stats(subject_id, days)

    st.markdown("---")
    st.markdown("#### Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Assessments", stats['total_assessments'])
    with col2:
        st.metric("Questions", stats['total_questions'])
    with col3:
        st.metric("Avg Score", f"{stats['avg_score']:.0f}%")
    with col4:
        st.metric("Accuracy", f"{stats['accuracy']:.0f}%")

    st.markdown("---")

    # Progress over time
    st.markdown("#### Score Progress")
    progress_data = db.get_assessment_progress_over_time(subject_id, limit=20)

    if progress_data:
        # Reverse for chronological order
        progress_data = list(reversed(progress_data))

        # Simple text-based chart
        for entry in progress_data[-10:]:
            score = entry['score_percentage'] or 0
            bar_length = int(score / 5)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            date_str = entry['started_at'][:10] if entry['started_at'] else "Unknown"
            st.text(f"{date_str} | {bar} {score:.0f}%")
    else:
        st.info("Complete some assessments to see progress.")

    st.markdown("---")

    # Topic mastery breakdown
    st.markdown("#### Topic Mastery Levels")
    mastery_data = db.get_topic_mastery(subject_id)

    if mastery_data:
        for topic_data in mastery_data[:15]:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{topic_data['topic']}**")
                mastery_pct = topic_data['mastery_level']
                st.progress(mastery_pct / 100)

            with col2:
                color = "#27ae60" if mastery_pct >= 70 else ("#f39c12" if mastery_pct >= 40 else "#e74c3c")
                st.markdown(f"<span style='color:{color}'>{mastery_pct:.0f}%</span>", unsafe_allow_html=True)

            with col3:
                trend_icons = {"improving": "📈", "declining": "📉", "stable": "➡️"}
                st.markdown(f"{trend_icons.get(topic_data['trend'], '➡️')} {topic_data['trend'].title()}")
    else:
        st.info("Complete some assessments to see mastery levels.")

    st.markdown("---")

    # Performance by question type
    st.markdown("#### Performance by Question Type")
    type_performance = db.get_performance_by_question_type(subject_id)

    if type_performance:
        for perf in type_performance:
            type_name = perf['question_type'].replace('_', ' ').title()
            pct = perf['percentage']
            color = "#27ae60" if pct >= 70 else ("#f39c12" if pct >= 40 else "#e74c3c")
            st.markdown(
                f"**{type_name}:** "
                f"<span style='color:{color}'>{perf['correct']}/{perf['total']} ({pct:.0f}%)</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No question type data yet.")

    # Export button
    st.markdown("---")
    if st.button("📄 Export Report"):
        report = _generate_report_markdown(subject_id, stats, mastery_data, type_performance)
        st.download_button(
            "Download Report",
            report,
            file_name=f"knowledge_report_{date.today().isoformat()}.md",
            mime="text/markdown"
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _create_and_populate_assessment(subject_id, assessment_type, question_source,
                                     selected_topics, api_key, subject_name):
    """Create assessment and populate with AI-generated questions."""

    # Determine question count
    question_counts = {"quick": 5, "comprehensive": 15, "topic_focused": 10}
    num_questions = question_counts.get(assessment_type, 10)

    # Create assessment record
    assessment_id = db.create_assessment(subject_id, assessment_type, num_questions)

    # Get topics to assess
    if selected_topics:
        topics = selected_topics
    else:
        # Use topics from past papers or generate from subject
        topics = db.get_available_topics_for_subject(subject_id)
        if not topics:
            topics = [subject_name]  # Use subject name as fallback topic

    # Generate questions using AI
    questions_generated = 0
    topics_cycle = topics * ((num_questions // len(topics)) + 1) if topics else [subject_name]

    for i in range(num_questions):
        topic = topics_cycle[i % len(topics_cycle)] if topics_cycle else subject_name

        question = _generate_question_for_topic(topic, subject_name, api_key)

        if question:
            db.add_assessment_question(
                assessment_id=assessment_id,
                question_text=question['question_text'],
                question_type=question['question_type'],
                correct_answer=question['correct_answer'],
                topic=topic,
                options=json.dumps(question.get('options')) if question.get('options') else None,
                difficulty=question.get('difficulty', 'medium'),
                source_type='ai_generated',
                marks=question.get('marks', 1)
            )
            questions_generated += 1

    if questions_generated == 0:
        return None

    return assessment_id


def _generate_question_for_topic(topic, subject_name, api_key):
    """Generate a single question for a topic using Claude AI."""
    try:
        from utils import call_claude

        prompt = f"""Generate a single GCSE-level question about "{topic}" for {subject_name}.

Respond ONLY with valid JSON in this exact format:
{{
    "question_text": "Your question here?",
    "question_type": "multiple_choice",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A) First option",
    "difficulty": "medium",
    "marks": 1
}}

For question_type, use one of: "multiple_choice", "short_answer", "true_false"
For true_false, options should be ["True", "False"]
For short_answer, options should be null

Make the question test understanding, not just memorization."""

        result = call_claude(
            api_key=api_key,
            prompt=prompt,
            system="You are an exam question generator for GCSE students. Generate clear, accurate questions. Respond ONLY with valid JSON, no other text."
        )

        if result and not result.startswith("Error:"):
            # Parse JSON from response
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])

    except Exception as e:
        pass

    return None


def _submit_answer(assessment_id, question, student_answer, confidence, api_key):
    """Submit and evaluate student's answer."""

    is_correct = False
    ai_evaluation = None

    if question['question_type'] in ['multiple_choice', 'true_false']:
        # Exact match for MC and T/F
        correct = question['correct_answer'].strip().lower()
        given = student_answer.strip().lower()
        is_correct = given == correct or given.startswith(correct[:1])
    else:
        # Use AI to evaluate short answer
        is_correct, ai_evaluation = _evaluate_short_answer(
            question['question_text'],
            question['correct_answer'],
            student_answer,
            api_key
        )

    # Record response
    db.record_response(
        assessment_id=assessment_id,
        question_id=question['id'],
        student_answer=student_answer,
        is_correct=is_correct,
        marks_awarded=question['marks'] if is_correct else 0,
        confidence=confidence,
        ai_evaluation=ai_evaluation
    )

    # Get subject_id for mastery update
    assessment = db.get_assessment_by_id(assessment_id)
    if assessment:
        db.update_topic_mastery(
            subject_id=assessment['subject_id'],
            topic=question['topic'],
            is_correct=is_correct
        )


def _evaluate_short_answer(question, correct_answer, student_answer, api_key):
    """Use AI to evaluate a short answer response."""
    try:
        from utils import call_claude

        prompt = f"""Evaluate this student's answer:

Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

Respond ONLY with valid JSON:
{{
    "is_correct": true or false,
    "explanation": "Brief explanation (1-2 sentences)"
}}

Be fair - award marks for substantially correct answers even if wording differs slightly."""

        result = call_claude(
            api_key=api_key,
            prompt=prompt,
            system="You are a fair exam marker. Respond ONLY with valid JSON."
        )

        if result and not result.startswith("Error:"):
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                parsed = json.loads(result[start:end])
                return parsed.get('is_correct', False), parsed.get('explanation', '')

    except:
        pass

    # Default to incorrect if AI fails
    return False, None


def _complete_assessment(assessment_id, api_key):
    """Complete the assessment and show results."""

    assessment = db.get_assessment_by_id(assessment_id)
    responses = db.get_assessment_responses(assessment_id)

    # Generate AI feedback
    ai_feedback = None
    if api_key:
        ai_feedback = _generate_assessment_feedback(assessment, responses, api_key)

    # Mark complete
    db.complete_assessment(assessment_id, ai_feedback)

    # Show results
    st.balloons()

    score_pct = (assessment['correct_answers'] / assessment['total_questions'] * 100
                 if assessment['total_questions'] > 0 else 0)

    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea22, #764ba222); border-radius: 16px; margin: 20px 0;">
        <h1 style="margin: 0; font-size: 3rem;">🎉 Assessment Complete!</h1>
        <h2 style="margin: 20px 0; color: #667eea;">{score_pct:.0f}%</h2>
        <p style="font-size: 1.2rem; color: #666;">
            You got {assessment['correct_answers']} out of {assessment['total_questions']} correct
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Show AI feedback
    if ai_feedback:
        st.markdown("### AI Feedback")
        st.markdown(ai_feedback)

    # Show detailed results
    with st.expander("View Detailed Results"):
        for resp in responses:
            icon = "✅" if resp['is_correct'] else "❌"
            st.markdown(f"""
            **{icon} {resp['question_text']}**
            - Your answer: {resp['student_answer']}
            - Correct answer: {resp['correct_answer']}
            """)
            if resp.get('ai_evaluation'):
                st.caption(f"Feedback: {resp['ai_evaluation']}")

    # Reset state
    if st.button("Start New Assessment", type="primary"):
        st.session_state.current_assessment = None
        st.session_state.assessment_index = 0
        st.rerun()


def _generate_assessment_feedback(assessment, responses, api_key):
    """Generate AI feedback for completed assessment."""
    try:
        from utils import call_claude

        # Summarize performance
        correct_topics = [r['topic'] for r in responses if r['is_correct']]
        incorrect_topics = [r['topic'] for r in responses if not r['is_correct']]

        prompt = f"""A student just completed a {assessment['assessment_type']} assessment in {assessment['subject_name']}.

Score: {assessment['correct_answers']}/{assessment['total_questions']}
Topics answered correctly: {', '.join(correct_topics) if correct_topics else 'None'}
Topics answered incorrectly: {', '.join(incorrect_topics) if incorrect_topics else 'None'}

Provide brief, encouraging feedback (3-4 sentences) that:
1. Acknowledges their effort
2. Highlights strengths
3. Suggests 1-2 specific areas to focus on
4. Ends with encouragement"""

        result = call_claude(
            api_key=api_key,
            prompt=prompt,
            system="You are an encouraging study coach for GCSE students. Be supportive but specific."
        )

        if result and not result.startswith("Error:"):
            return result

    except:
        pass

    return None


def _generate_ai_gap_analysis(subject_id, api_key):
    """Generate AI-powered gap analysis."""
    try:
        from utils import call_claude

        gaps = db.get_knowledge_gaps(subject_id)
        strengths = db.get_strong_topics(subject_id)
        exam_reqs = db.get_exam_requirements(subject_id)
        coverage = db.get_coverage_stats(subject_id)

        data_summary = f"""
Coverage: {coverage['coverage_percentage']:.0f}% ({coverage['topics_mastered']} of {coverage['total_exam_topics']} topics mastered)

Top Knowledge Gaps (need work):
{json.dumps([{'topic': g['topic'], 'mastery': g['mastery_level'], 'frequency': g['frequency']} for g in gaps[:8]], indent=2)}

Strengths (mastered):
{json.dumps([{'topic': s['topic'], 'mastery': s['mastery_level']} for s in strengths[:5]], indent=2)}

Key Exam Topics:
{json.dumps([{'topic': e['topic'], 'frequency': e['frequency'], 'importance': e['importance_level']} for e in exam_reqs[:10]], indent=2)}
"""

        prompt = f"""Based on this knowledge gap analysis:

{data_summary}

Provide a focused analysis with:
1. **Priority Focus Areas** - Top 3 gaps to address first (explain why)
2. **Study Recommendations** - Specific actions for each priority area
3. **Leverage Your Strengths** - How to use what you know well
4. **Exam Readiness** - Brief assessment of preparation level
5. **Quick Win** - One easy improvement to make today

Keep it practical and encouraging. Use bullet points."""

        result = call_claude(
            api_key=api_key,
            prompt=prompt,
            system="You are an expert study advisor helping a GCSE student prepare for exams. Be specific and actionable."
        )

        if result and not result.startswith("Error:"):
            return result

    except:
        pass

    return None


def _get_gap_urgency_color(gap):
    """Get color based on gap urgency."""
    importance = gap.get('importance_level', 'medium')
    mastery = gap.get('mastery_level', 0)

    if importance == 'critical' or (mastery < 30 and gap.get('frequency', 0) >= 3):
        return "#e74c3c"  # Red - urgent
    elif importance == 'high' or mastery < 50:
        return "#f39c12"  # Orange - important
    else:
        return "#3498db"  # Blue - normal


def _generate_report_markdown(subject_id, stats, mastery_data, type_performance):
    """Generate a markdown report."""

    report = f"""# Knowledge Gap Assessment Report
Generated: {date.today().isoformat()}

## Overview
- **Assessments Completed:** {stats['total_assessments']}
- **Total Questions:** {stats['total_questions']}
- **Average Score:** {stats['avg_score']:.0f}%
- **Overall Accuracy:** {stats['accuracy']:.0f}%

## Topic Mastery Levels
"""

    if mastery_data:
        for topic in mastery_data:
            status = "✅ Mastered" if topic['mastery_level'] >= 70 else ("⚠️ Needs Work" if topic['mastery_level'] >= 40 else "❌ Weak")
            report += f"- **{topic['topic']}:** {topic['mastery_level']:.0f}% ({status})\n"
    else:
        report += "No mastery data yet.\n"

    report += "\n## Performance by Question Type\n"

    if type_performance:
        for perf in type_performance:
            report += f"- **{perf['question_type'].replace('_', ' ').title()}:** {perf['correct']}/{perf['total']} ({perf['percentage']:.0f}%)\n"
    else:
        report += "No question type data yet.\n"

    report += "\n---\n*Generated by AI Study Assistant*\n"

    return report
