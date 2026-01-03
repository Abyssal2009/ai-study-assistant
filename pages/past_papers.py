"""
Study Assistant - Past Papers Page
Upload, analyze, and track past paper performance with AI-powered insights.
"""

import streamlit as st
import database as db
import json
from io import BytesIO

# Question types for categorization
QUESTION_TYPES = [
    "multiple_choice",
    "short_answer",
    "essay",
    "calculation",
    "diagram",
    "data_analysis",
    "practical",
    "other"
]

QUESTION_TYPE_LABELS = {
    "multiple_choice": "Multiple Choice",
    "short_answer": "Short Answer",
    "essay": "Essay/Extended Writing",
    "calculation": "Calculation",
    "diagram": "Diagram/Drawing",
    "data_analysis": "Data Analysis",
    "practical": "Practical/Experiment",
    "other": "Other"
}


def render():
    """Render the Past Papers page."""
    st.title("📄 Past Papers")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload Paper",
        "📊 Analysis",
        "📝 Log Score",
        "🔍 Question Bank",
        "📚 All Papers"
    ])

    # TAB 1: Upload Paper
    with tab1:
        _render_upload_tab(subjects)

    # TAB 2: Analysis
    with tab2:
        _render_analysis_tab(subjects)

    # TAB 3: Log Score (simple manual entry)
    with tab3:
        _render_log_score_tab(subjects)

    # TAB 4: Question Bank
    with tab4:
        _render_question_bank_tab(subjects)

    # TAB 5: All Papers
    with tab5:
        _render_all_papers_tab(subjects)


def _render_upload_tab(subjects):
    """Render the upload and analysis tab."""
    st.markdown("### 📤 Upload & Analyze Past Paper")
    st.markdown("Upload a PDF or paste text from a past paper for AI analysis.")

    subject = st.selectbox(
        "Subject *",
        options=subjects,
        format_func=lambda x: x['name'],
        key="upload_subject"
    )

    col1, col2 = st.columns(2)
    with col1:
        paper_name = st.text_input("Paper Name *", placeholder="e.g., June 2023 Paper 1")
        exam_board = st.text_input("Exam Board", placeholder="e.g., AQA, Edexcel")
    with col2:
        year = st.text_input("Year", placeholder="e.g., 2023")
        total_marks = st.number_input("Total Marks *", min_value=1, max_value=200, value=100)

    input_method = st.radio(
        "Input Method:",
        ["Upload PDF", "Paste Text", "Upload Image"],
        horizontal=True
    )

    paper_content = None

    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload a past paper PDF for analysis"
        )
        if uploaded_file:
            paper_content = _extract_pdf_text(uploaded_file)
            if paper_content:
                with st.expander("Preview extracted text"):
                    st.text(paper_content[:2000] + "..." if len(paper_content) > 2000 else paper_content)

    elif input_method == "Paste Text":
        paper_content = st.text_area(
            "Paste paper content:",
            height=300,
            placeholder="Paste the questions from the past paper here..."
        )

    elif input_method == "Upload Image":
        uploaded_image = st.file_uploader(
            "Upload Image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a photo of the past paper"
        )
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
            paper_content = _extract_image_text(uploaded_image)
            if paper_content:
                with st.expander("Preview extracted text"):
                    st.text(paper_content[:2000] + "..." if len(paper_content) > 2000 else paper_content)

    if paper_content and paper_name:
        if st.button("🔍 Analyze Paper", type="primary"):
            with st.spinner("Analyzing paper with AI..."):
                # Save paper first
                paper_id = db.add_past_paper(
                    subject_id=subject['id'],
                    paper_name=paper_name,
                    total_marks=total_marks,
                    exam_board=exam_board,
                    year=year,
                    raw_content=paper_content
                )

                # Analyze with AI
                analysis = _analyze_paper_with_ai(paper_content, subject['name'])

                if analysis:
                    # Save questions
                    for q in analysis.get('questions', []):
                        db.add_paper_question(
                            paper_id=paper_id,
                            question_number=q.get('number', '?'),
                            question_text=q.get('text', ''),
                            max_marks=q.get('marks', 1),
                            topic=q.get('topic', ''),
                            question_type=q.get('type', 'other'),
                            difficulty=q.get('difficulty', 'medium')
                        )

                    # Save summary
                    db.update_paper_summary(paper_id, json.dumps(analysis.get('summary', {})))

                    st.success(f"Paper analyzed! Found {len(analysis.get('questions', []))} questions.")

                    # Display analysis
                    _display_analysis_results(analysis)
                else:
                    st.warning("Could not analyze paper. It has been saved for manual review.")

                st.rerun()


def _render_analysis_tab(subjects):
    """Render the analysis and patterns tab."""
    st.markdown("### 📊 Paper Analysis & Patterns")

    paper_count = db.get_paper_count()
    if paper_count == 0:
        st.info("No papers analyzed yet. Upload some papers to see analysis!")
        return

    # Filter by subject
    filter_subject = st.selectbox(
        "Filter by subject:",
        options=[None] + subjects,
        format_func=lambda x: "All Subjects" if x is None else x['name'],
        key="analysis_filter"
    )
    subject_id = filter_subject['id'] if filter_subject else None

    # Overview metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Papers Analyzed", paper_count)
    with col2:
        common_topics = db.get_common_topics(subject_id, limit=5)
        st.metric("Topics Identified", len(common_topics))
    with col3:
        type_stats = db.get_question_type_stats(subject_id)
        st.metric("Question Types", len(type_stats))

    st.markdown("---")

    # Question Type Breakdown
    st.markdown("#### Question Type Distribution")
    type_stats = db.get_question_type_stats(subject_id)
    if type_stats:
        for stat in type_stats:
            type_label = QUESTION_TYPE_LABELS.get(stat['question_type'], stat['question_type'])
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{type_label}**")
            with col2:
                st.caption(f"{stat['count']} questions")
            with col3:
                if stat['avg_percentage']:
                    st.caption(f"Avg: {stat['avg_percentage']:.0f}%")
    else:
        st.info("No question type data yet.")

    st.markdown("---")

    # Common Topics
    st.markdown("#### Most Common Topics")
    common_topics = db.get_common_topics(subject_id, limit=10)
    if common_topics:
        for topic in common_topics:
            freq_bar = "█" * min(topic['frequency'], 10)
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{topic['topic']}**")
            with col2:
                st.caption(f"{freq_bar} {topic['frequency']} times in {topic['paper_count']} papers")
            with col3:
                if topic['avg_percentage']:
                    color = "#27ae60" if topic['avg_percentage'] >= 70 else "#e74c3c"
                    st.markdown(f"<span style='color:{color}'>{topic['avg_percentage']:.0f}%</span>",
                               unsafe_allow_html=True)
    else:
        st.info("No topic data yet.")

    st.markdown("---")

    # Generate Pattern Report
    st.markdown("#### Generate AI Pattern Report")
    if st.button("🔍 Generate Pattern Report", type="primary"):
        with st.spinner("Analyzing patterns across papers..."):
            report = _generate_pattern_report(subject_id)
            if report:
                st.markdown("### Pattern Analysis Report")
                st.markdown(report)
                # Save report
                db.save_analysis_report(subject_id, "pattern_report", report)
            else:
                st.warning("Could not generate report. Try adding more papers.")


def _render_log_score_tab(subjects):
    """Render the simple score logging tab."""
    st.markdown("### 📝 Log Paper Score")
    st.markdown("Quickly log your score on a past paper without uploading.")

    with st.form("add_paper"):
        subject = st.selectbox(
            "Subject *",
            options=subjects,
            format_func=lambda x: x['name']
        )
        paper_name = st.text_input("Paper Name *", placeholder="e.g., June 2023 Paper 1")

        col1, col2 = st.columns(2)
        with col1:
            exam_board = st.text_input("Exam Board", placeholder="e.g., AQA, Edexcel")
            year = st.text_input("Year", placeholder="e.g., 2023")
        with col2:
            total_marks = st.number_input("Total Marks *", min_value=1, max_value=200, value=100)
            marks_achieved = st.number_input("Marks Achieved *", min_value=0, max_value=200, value=0)

        time_taken = st.number_input("Time Taken (minutes)", min_value=0, max_value=300, value=60)
        notes = st.text_area("Notes (optional)", placeholder="Any observations or areas to improve...")

        if st.form_submit_button("Save Paper", type="primary"):
            if paper_name and total_marks > 0:
                paper_id = db.add_past_paper(
                    subject_id=subject['id'],
                    paper_name=paper_name,
                    exam_board=exam_board,
                    year=year,
                    total_marks=total_marks,
                    time_taken_minutes=time_taken,
                    notes=notes
                )
                # Add a single question entry for the total score
                db.add_paper_question(
                    paper_id=paper_id,
                    question_number="Total",
                    max_marks=total_marks,
                    marks_achieved=marks_achieved
                )
                percentage = (marks_achieved / total_marks) * 100
                st.success(f"Paper saved! Score: {marks_achieved}/{total_marks} ({percentage:.0f}%)")
                st.rerun()
            else:
                st.error("Please fill in required fields")


def _render_question_bank_tab(subjects):
    """Render the searchable question bank."""
    st.markdown("### 🔍 Question Bank")
    st.markdown("Search and filter all questions from analyzed papers.")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_subject = st.selectbox(
            "Subject:",
            options=[None] + subjects,
            format_func=lambda x: "All" if x is None else x['name'],
            key="qbank_subject"
        )
    with col2:
        filter_type = st.selectbox(
            "Question Type:",
            options=[None] + QUESTION_TYPES,
            format_func=lambda x: "All Types" if x is None else QUESTION_TYPE_LABELS.get(x, x),
            key="qbank_type"
        )
    with col3:
        filter_topic = st.text_input("Topic:", placeholder="Search topic...", key="qbank_topic")

    subject_id = filter_subject['id'] if filter_subject else None
    questions = db.get_all_questions(
        subject_id=subject_id,
        topic=filter_topic if filter_topic else None,
        question_type=filter_type
    )

    if questions:
        st.caption(f"Found {len(questions)} questions")

        for q in questions[:50]:  # Limit display
            type_label = QUESTION_TYPE_LABELS.get(q.get('question_type', ''), 'Unknown')
            with st.expander(f"Q{q['question_number']} - {q.get('topic', 'No topic')} ({type_label})"):
                st.markdown(f"**Paper:** {q['paper_name']} ({q.get('year', 'N/A')})")
                st.markdown(f"**Subject:** {q['subject_name']}")
                st.markdown(f"**Marks:** {q['max_marks']}")
                if q.get('question_text'):
                    st.markdown(f"**Question:** {q['question_text'][:500]}...")
                if q.get('difficulty'):
                    st.markdown(f"**Difficulty:** {q['difficulty'].title()}")
    else:
        st.info("No questions found. Upload and analyze some papers first!")


def _render_all_papers_tab(subjects):
    """Render the all papers list."""
    st.markdown("### 📚 All Papers")

    papers = db.get_all_past_papers()

    if papers:
        filter_subject = st.selectbox(
            "Filter by subject:",
            options=[None] + subjects,
            format_func=lambda x: "All Subjects" if x is None else x['name'],
            key="filter_papers"
        )

        filtered = papers
        if filter_subject:
            filtered = [p for p in filtered if p['subject_id'] == filter_subject['id']]

        for paper in filtered:
            marks_achieved = paper.get('marks_achieved') or 0
            total_marks = paper.get('total_marks') or 1
            percentage = (marks_achieved / total_marks) * 100 if total_marks > 0 else 0

            # Color based on score
            if percentage >= 80:
                color = "#27ae60"
            elif percentage >= 60:
                color = "#f39c12"
            else:
                color = "#e74c3c"

            with st.expander(f"{paper['paper_name']} - {percentage:.0f}%"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Subject:** {paper['subject_name']}")
                    st.markdown(f"**Board:** {paper.get('exam_board', 'N/A')}")
                with col2:
                    st.markdown(f"**Score:** {marks_achieved}/{total_marks}")
                    st.markdown(f"**Year:** {paper.get('year', 'N/A')}")
                with col3:
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                        <h2 style="margin: 0; color: white;">{percentage:.0f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)

                # Show AI summary if available
                if paper.get('ai_summary'):
                    try:
                        summary = json.loads(paper['ai_summary'])
                        if summary.get('key_topics'):
                            st.markdown(f"**Key Topics:** {', '.join(summary['key_topics'][:5])}")
                    except json.JSONDecodeError:
                        pass  # Invalid JSON in stored summary

                if paper.get('notes'):
                    st.markdown(f"**Notes:** {paper['notes']}")

                if st.button("🗑️ Delete", key=f"del_paper_{paper['id']}"):
                    db.delete_past_paper(paper['id'])
                    st.rerun()
    else:
        st.info("No past papers logged yet. Add some using the 'Upload Paper' or 'Log Score' tabs!")


def _extract_pdf_text(uploaded_file) -> str:
    """Extract text from a PDF file."""
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return "\n\n".join(text_parts)
    except ImportError:
        st.error("PDF library not installed. Run: pip install pdfplumber")
        return None
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return None


def _extract_image_text(uploaded_file) -> str:
    """Extract text from an image using Vision API."""
    try:
        import vision_ocr

        if not vision_ocr.is_vision_available():
            st.error("Google Vision API not configured")
            return None

        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        text = vision_ocr.extract_text_from_bytes(image_bytes)
        return text
    except Exception as e:
        st.error(f"OCR error: {e}")
        return None


def _analyze_paper_with_ai(content: str, subject_name: str) -> dict:
    """Use Claude to analyze paper content and extract questions."""
    try:
        from utils import call_claude_with_rag

        prompt = f"""Analyze this {subject_name} past exam paper and extract all questions.

For each question, identify:
1. Question number
2. The question text (brief summary)
3. Marks available
4. Topic/theme it covers
5. Question type (one of: multiple_choice, short_answer, essay, calculation, diagram, data_analysis, practical, other)
6. Difficulty (easy, medium, hard)

Also provide a summary with:
- Key topics covered
- Question type distribution
- Any patterns noticed

Paper content:
{content[:8000]}

Respond in JSON format:
{{
    "questions": [
        {{"number": "1a", "text": "...", "marks": 3, "topic": "...", "type": "...", "difficulty": "..."}}
    ],
    "summary": {{
        "key_topics": ["topic1", "topic2"],
        "total_questions": 10,
        "patterns": "..."
    }}
}}"""

        result, _ = call_claude_with_rag(prompt, system="You are an exam paper analyst. Extract question information accurately. Always respond with valid JSON.")

        # Parse JSON from response
        try:
            # Find JSON in response
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except json.JSONDecodeError:
            pass  # Invalid JSON from AI response

        return None
    except Exception as e:
        st.error(f"AI analysis error: {e}")
        return None


def _generate_pattern_report(subject_id: int = None) -> str:
    """Generate a pattern analysis report using AI."""
    try:
        from utils import call_claude_with_rag

        # Gather data
        common_topics = db.get_common_topics(subject_id, limit=15)
        type_stats = db.get_question_type_stats(subject_id)
        weak_topics = db.get_weak_topics(limit=10)

        data_summary = f"""
Topics frequency: {json.dumps([{'topic': t['topic'], 'freq': t['frequency'], 'papers': t['paper_count']} for t in common_topics])}

Question types: {json.dumps([{'type': t['question_type'], 'count': t['count']} for t in type_stats])}

Weak areas: {json.dumps([{'topic': t['topic'], 'score': t['percentage']} for t in weak_topics])}
"""

        prompt = f"""Based on this past paper analysis data, write a helpful study report for a GCSE student.

{data_summary}

Include:
1. Most frequently examined topics (what to prioritize)
2. Common question types and how to prepare for each
3. Identified weak areas and improvement suggestions
4. Predictions for likely exam topics based on patterns
5. Specific revision recommendations

Make it actionable and encouraging. Use bullet points for clarity."""

        result, _ = call_claude_with_rag(prompt, system="You are a helpful study advisor analyzing exam patterns.")
        return result if not result.startswith("Error:") else None

    except Exception as e:
        return None


def _display_analysis_results(analysis: dict):
    """Display the AI analysis results."""
    st.markdown("---")
    st.markdown("### Analysis Results")

    questions = analysis.get('questions', [])
    summary = analysis.get('summary', {})

    if summary:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key Topics:**")
            for topic in summary.get('key_topics', [])[:5]:
                st.markdown(f"- {topic}")
        with col2:
            if summary.get('patterns'):
                st.markdown("**Patterns Noticed:**")
                st.markdown(summary['patterns'])

    if questions:
        st.markdown(f"**Questions Found:** {len(questions)}")

        # Type distribution
        type_counts = {}
        for q in questions:
            qtype = q.get('type', 'other')
            type_counts[qtype] = type_counts.get(qtype, 0) + 1

        st.markdown("**Question Types:**")
        for qtype, count in type_counts.items():
            label = QUESTION_TYPE_LABELS.get(qtype, qtype)
            st.caption(f"- {label}: {count}")
