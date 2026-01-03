"""
Study Assistant - AI Tools Page
AI-powered study tools including flashcard generation, quiz creation, and more.
Uses RAG to provide context from your notes and flashcards.
"""

import streamlit as st
import database as db
from utils import call_claude_with_rag, CLAUDE_MODELS, DEFAULT_MODEL, days_until
import re


def render():
    """Render the AI Tools page."""
    st.title("🤖 AI Tools")
    st.markdown("Powerful AI-powered study tools to supercharge your revision.")

    # Session state setup
    if 'bubble_ace_api_key' not in st.session_state:
        st.session_state.bubble_ace_api_key = ""
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = DEFAULT_MODEL
    if 'ai_tools_use_rag' not in st.session_state:
        st.session_state.ai_tools_use_rag = True

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

    # Model and RAG selector
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    with col1:
        current_model = CLAUDE_MODELS[st.session_state.ai_model]
        st.markdown(f"**Model:** {current_model['icon']} {current_model['name']}")
    with col2:
        if st.button("⚡ Haiku", type="primary" if st.session_state.ai_model == 'haiku' else "secondary"):
            st.session_state.ai_model = 'haiku'
            st.rerun()
    with col3:
        if st.button("✨ Sonnet", type="primary" if st.session_state.ai_model == 'sonnet' else "secondary"):
            st.session_state.ai_model = 'sonnet'
            st.rerun()
    with col4:
        use_rag = st.checkbox(
            "📚 Use my notes",
            value=st.session_state.ai_tools_use_rag,
            help="Search your notes and flashcards for relevant context"
        )
        if use_rag != st.session_state.ai_tools_use_rag:
            st.session_state.ai_tools_use_rag = use_rag

    st.markdown("---")

    # Tabs for different AI tools
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🃏 Generate Flashcards",
        "❓ Create Quiz",
        "📝 Summarise Notes",
        "🎯 Study Coach",
        "✍️ Essay Helper"
    ])

    # Local helper for Claude API with RAG support
    def _call_claude(prompt: str, system: str = None, subject_id: int = None) -> tuple:
        """Call Claude with optional RAG. Returns (response, sources)."""
        response, sources = call_claude_with_rag(
            api_key=st.session_state.bubble_ace_api_key,
            prompt=prompt,
            system=system,
            model=st.session_state.ai_model,
            subject_id=subject_id,
            use_rag=st.session_state.ai_tools_use_rag
        )
        return response, sources

    # Helper to display RAG sources
    def _show_sources(sources):
        """Display sources used by RAG if any."""
        if sources:
            with st.expander(f"📚 Sources from your materials ({len(sources)} items)"):
                for source in sources:
                    source_type = source.get('source_type', 'unknown')
                    if source_type == 'note':
                        st.markdown(f"📝 **Note:** {source.get('title', 'Untitled')}")
                    elif source_type == 'flashcard':
                        st.markdown(f"🎴 **Flashcard:** {source.get('preview', '')[:80]}...")
                    elif source_type == 'past_paper':
                        st.markdown(f"📄 **Past Paper:** {source.get('title', 'Untitled')}")

    # TAB 1: GENERATE FLASHCARDS
    with tab1:
        _render_flashcard_tab(subjects, _call_claude, _show_sources)

    # TAB 2: CREATE QUIZ
    with tab2:
        _render_quiz_tab(subjects, _call_claude, _show_sources)

    # TAB 3: SUMMARISE NOTES
    with tab3:
        _render_summary_tab(subjects, _call_claude, _show_sources)

    # TAB 4: STUDY COACH
    with tab4:
        _render_coach_tab(subjects, _call_claude, _show_sources)

    # TAB 5: ESSAY HELPER
    with tab5:
        _render_essay_tab(subjects, _call_claude, _show_sources)


def _parse_generated_flashcards(text: str) -> list:
    """Parse Q/A formatted flashcards into a list of dicts."""
    flashcards = []
    # Match Q: ... A: ... patterns (handles multiline)
    pattern = r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    for q, a in matches:
        question = q.strip()
        answer = a.strip()
        if question and answer:
            flashcards.append({'question': question, 'answer': answer})

    return flashcards


def _render_flashcard_tab(subjects, call_claude, show_sources):
    """Render the flashcard generation tab."""
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

Make the questions test understanding, not just memorisation."""

                    result, sources = call_claude(prompt, subject_id=selected_note['subject_id'])
                    if not result.startswith("Error:"):
                        st.success("Flashcards generated!")
                        st.markdown("### Generated Flashcards")
                        st.markdown(result)
                        st.session_state['generated_flashcards'] = result
                        st.session_state['fc_subject_id'] = selected_note['subject_id']
                        st.session_state['fc_topic'] = selected_note['topic'] or selected_note['title']
                        show_sources(sources)
                    else:
                        st.error(result)

            # Show save button if flashcards were generated
            if st.session_state.get('generated_flashcards') and st.session_state.get('fc_subject_id'):
                st.markdown("---")
                parsed = _parse_generated_flashcards(st.session_state['generated_flashcards'])
                if parsed:
                    st.info(f"Found {len(parsed)} flashcards ready to save.")
                    if st.button("💾 Save All to Flashcards", type="primary", key="save_fc_notes"):
                        saved = 0
                        for card in parsed:
                            db.add_flashcard(
                                subject_id=st.session_state['fc_subject_id'],
                                question=card['question'],
                                answer=card['answer'],
                                topic=st.session_state.get('fc_topic', '')
                            )
                            saved += 1
                        st.success(f"✓ Saved {saved} flashcards! Go to **Flashcards** to review them.")
                        # Clear session state
                        del st.session_state['generated_flashcards']
                        del st.session_state['fc_subject_id']
                        if 'fc_topic' in st.session_state:
                            del st.session_state['fc_topic']
                        st.rerun()
        else:
            st.info("No notes found. Create some notes first!")

    else:  # From a topic
        fc_subject = st.selectbox(
            "Subject:",
            options=subjects,
            format_func=lambda x: x['name'],
            key="fc_topic_subject"
        )

        fc_topic = st.text_input("Topic:", placeholder="e.g., Photosynthesis, The Cold War")
        num_cards = st.slider("Number of flashcards", 3, 15, 5, key="fc_topic_num")

        if st.button("🪄 Generate Flashcards", type="primary", key="fc_topic_btn"):
            if fc_topic:
                with st.spinner("Generating flashcards..."):
                    prompt = f"""Create exactly {num_cards} flashcards about "{fc_topic}" for GCSE {fc_subject['name']}.

Format each flashcard as:
Q: [question]
A: [answer]

Make the questions appropriate for GCSE level."""

                    result, sources = call_claude(prompt, subject_id=fc_subject['id'])
                    if not result.startswith("Error:"):
                        st.success("Flashcards generated!")
                        st.markdown("### Generated Flashcards")
                        st.markdown(result)
                        # Store for saving
                        st.session_state['generated_flashcards_topic'] = result
                        st.session_state['fc_topic_subject_id'] = fc_subject['id']
                        st.session_state['fc_topic_name'] = fc_topic
                        show_sources(sources)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a topic.")

        # Show save button if flashcards were generated from topic
        if st.session_state.get('generated_flashcards_topic') and st.session_state.get('fc_topic_subject_id'):
            st.markdown("---")
            parsed = _parse_generated_flashcards(st.session_state['generated_flashcards_topic'])
            if parsed:
                st.info(f"Found {len(parsed)} flashcards ready to save.")
                if st.button("💾 Save All to Flashcards", type="primary", key="save_fc_topic"):
                    saved = 0
                    for card in parsed:
                        db.add_flashcard(
                            subject_id=st.session_state['fc_topic_subject_id'],
                            question=card['question'],
                            answer=card['answer'],
                            topic=st.session_state.get('fc_topic_name', '')
                        )
                        saved += 1
                    st.success(f"✓ Saved {saved} flashcards! Go to **Flashcards** to review them.")
                    # Clear session state
                    del st.session_state['generated_flashcards_topic']
                    del st.session_state['fc_topic_subject_id']
                    if 'fc_topic_name' in st.session_state:
                        del st.session_state['fc_topic_name']
                    st.rerun()


def _render_quiz_tab(subjects, call_claude, show_sources):
    """Render the quiz creation tab."""
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
                type_instructions = {
                    "Multiple Choice": "Make all questions multiple choice with 4 options "
                                       "(A, B, C, D). Mark the correct answer.",
                    "Short Answer": "Make all questions short answer (1-2 sentence answers).",
                    "True/False": "Make all questions True/False. State if each is True/False.",
                    "Mixed": "Mix question types: multiple choice, short answer, true/false."
                }

                prompt = f"""Create a {quiz_num} question quiz about "{quiz_topic}" for GCSE {quiz_subject['name']}.

{type_instructions[quiz_type]}

Format:
**Question 1:** [question]
[options if multiple choice]

**Answer:** [correct answer]
**Explanation:** [brief explanation]

---

Continue for all {quiz_num} questions."""

                result, sources = call_claude(prompt, subject_id=quiz_subject['id'])
                if not result.startswith("Error:"):
                    st.success("Quiz generated!")
                    st.markdown("### Your Quiz")
                    st.markdown(result)
                    show_sources(sources)
                else:
                    st.error(result)
        else:
            st.warning("Please enter a topic.")


def _render_summary_tab(subjects, call_claude, show_sources):
    """Render the notes summary tab."""
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

Create a {sum_style.lower()} summary. Focus on key concepts and important facts."""

                    result, sources = call_claude(prompt, subject_id=selected_note['subject_id'])
                    if not result.startswith("Error:"):
                        st.success("Summary generated!")
                        st.markdown("### Summary")
                        st.markdown(result)
                        show_sources(sources)
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
                    level_instructions = {
                        "Simple (like I'm 10)": "Explain like I'm 10 years old. Use simple words and fun analogies.",
                        "Standard GCSE level": "Explain at GCSE level with proper terminology.",
                        "Detailed with examples": "Give a detailed explanation with real-world examples.",
                        "Exam-focused": "Focus on what would be asked in exams and how to answer."
                    }

                    prompt = f"""Explain "{exp_topic}" for GCSE {exp_subject['name']}.

{level_instructions[exp_level]}

Structure: 1. Definition 2. How it works 3. Why it matters 4. Key exam points"""

                    result, sources = call_claude(prompt, subject_id=exp_subject['id'])
                    if not result.startswith("Error:"):
                        st.success("Explanation generated!")
                        st.markdown("### Explanation")
                        st.markdown(result)
                        show_sources(sources)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a topic.")


def _render_coach_tab(subjects, call_claude, show_sources):
    """Render the study coach tab."""
    st.markdown("### 🎯 AI Study Coach")
    st.markdown("Get personalised study advice based on your data.")

    # Gather data
    homework_stats = db.get_homework_stats()
    flashcard_stats = db.get_flashcard_stats()
    weak_topics = db.get_weak_topics(5)
    paper_count = db.get_paper_count()
    exams = db.get_all_exams()

    st.markdown("#### Your Current Situation")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pending Homework", homework_stats['pending'])
        st.metric("Overdue", homework_stats['overdue'])

    with col2:
        st.metric("Flashcards Due", flashcard_stats['due_today'])
        st.metric("7-Day Accuracy", f"{flashcard_stats['accuracy_7_days']}%")

    with col3:
        st.metric("Past Papers Done", paper_count)
        st.metric("Weak Topics", len(weak_topics))

    with col4:
        st.metric("Upcoming Exams", len(exams))
        if exams:
            next_exam = exams[0]
            days_to_exam = days_until(next_exam['exam_date'])
            st.metric("Next Exam In", f"{days_to_exam} days")

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
                # Build exam info string
                if exams:
                    exam_info = ', '.join([
                        f"{e['name']} ({days_until(e['exam_date'])} days)"
                        for e in exams[:5]  # Show up to 5 upcoming exams
                    ])
                else:
                    exam_info = 'None scheduled'

                context = f"""Student's current study situation:
Homework: Pending={homework_stats['pending']}, Overdue={homework_stats['overdue']}
Flashcards: Due today={flashcard_stats['due_today']}, Accuracy={flashcard_stats['accuracy_7_days']}%
Past Papers: {paper_count} completed
Upcoming exams: {exam_info}
Weak topics: {', '.join([t['topic'] for t in weak_topics]) if weak_topics else 'None'}
Subjects: {', '.join([s['name'] for s in subjects])}"""

                prompt = f"""{context}

Student's question: {coach_question}

Provide specific, actionable advice based on their actual data. Be encouraging but realistic."""

                result, sources = call_claude(prompt, system="You are an experienced study coach helping a GCSE student.")
                if not result.startswith("Error:"):
                    st.markdown("### 💡 Study Coach Advice")
                    st.markdown(result)
                    show_sources(sources)
                else:
                    st.error(result)


def _render_essay_tab(subjects, call_claude, show_sources):
    """Render the essay helper tab - redirects to Essay Tutor for full features."""
    st.markdown("### ✍️ Essay & Extended Writing Helper")

    # Promote Essay Tutor page
    st.info("""
    **For full essay grading and detailed feedback**, use the dedicated **Essay Tutor** page.
    It provides structured grading, section-by-section feedback, and tracks your essay history.
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Go to Essay Tutor", type="primary", use_container_width=True):
            st.session_state.selected_page = "Essay Tutor"
            st.rerun()
    with col2:
        if st.button("📊 View Essay History", use_container_width=True):
            st.session_state.selected_page = "Essay Tutor"
            st.session_state.essay_tab = "history"
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Quick Paragraph Improver")
    st.caption("For quick improvements to a single paragraph, use the tool below.")

    essay_subject = st.selectbox(
        "Subject:",
        options=subjects,
        format_func=lambda x: x['name'],
        key="essay_subject"
    )

    para_text = st.text_area("Paste your paragraph:", height=150, key="para_text")
    para_goal = st.selectbox(
        "What do you want to improve?",
        ["Make it clearer", "Add more detail", "Use better vocabulary", "Make it more scientific", "Fix grammar"]
    )

    if st.button("✨ Improve Paragraph", type="primary"):
        if para_text:
            with st.spinner("Improving..."):
                prompt = f"""Improve this paragraph for a GCSE {essay_subject['name']} essay.

Original: {para_text}
Goal: {para_goal}

Provide: 1. The improved paragraph 2. What you changed and why"""

                result, _ = call_claude(prompt)
                if not result.startswith("Error:"):
                    st.markdown("### Improved Paragraph")
                    st.markdown(result)
                else:
                    st.error(result)
        else:
            st.warning("Please enter a paragraph.")
