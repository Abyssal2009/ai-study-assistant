"""
Study Assistant - AI Tools Page
AI-powered study tools including flashcard generation, quiz creation, and more.
"""

import streamlit as st
import database as db
from utils import call_claude


def render():
    """Render the AI Tools page."""
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

    # Local helper for Claude API
    def _call_claude(prompt: str, system: str = None) -> str:
        return call_claude(st.session_state.bubble_ace_api_key, prompt, system)

    # TAB 1: GENERATE FLASHCARDS
    with tab1:
        _render_flashcard_tab(subjects, _call_claude)

    # TAB 2: CREATE QUIZ
    with tab2:
        _render_quiz_tab(subjects, _call_claude)

    # TAB 3: SUMMARISE NOTES
    with tab3:
        _render_summary_tab(subjects, _call_claude)

    # TAB 4: STUDY COACH
    with tab4:
        _render_coach_tab(subjects, _call_claude)

    # TAB 5: ESSAY HELPER
    with tab5:
        _render_essay_tab(subjects, _call_claude)


def _render_flashcard_tab(subjects, call_claude):
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

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.success("Flashcards generated!")
                        st.markdown("### Generated Flashcards")
                        st.markdown(result)
                        st.session_state['generated_flashcards'] = result
                        st.session_state['fc_subject_id'] = selected_note['subject_id']
                        st.session_state['fc_topic'] = selected_note['topic'] or selected_note['title']
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

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.success("Flashcards generated!")
                        st.markdown("### Generated Flashcards")
                        st.markdown(result)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a topic.")


def _render_quiz_tab(subjects, call_claude):
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
                    "Multiple Choice": "Make all questions multiple choice with 4 options (A, B, C, D). Mark the correct answer.",
                    "Short Answer": "Make all questions short answer (1-2 sentence answers needed).",
                    "True/False": "Make all questions True/False. State whether each is True or False.",
                    "Mixed": "Mix question types: some multiple choice, some short answer, some true/false."
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

                result = call_claude(prompt)
                if not result.startswith("Error:"):
                    st.success("Quiz generated!")
                    st.markdown("### Your Quiz")
                    st.markdown(result)
                else:
                    st.error(result)
        else:
            st.warning("Please enter a topic.")


def _render_summary_tab(subjects, call_claude):
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

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.success("Summary generated!")
                        st.markdown("### Summary")
                        st.markdown(result)
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

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.success("Explanation generated!")
                        st.markdown("### Explanation")
                        st.markdown(result)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a topic.")


def _render_coach_tab(subjects, call_claude):
    """Render the study coach tab."""
    st.markdown("### 🎯 AI Study Coach")
    st.markdown("Get personalised study advice based on your data.")

    # Gather data
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
                context = f"""Student's current study situation:
Homework: Pending={homework_stats['pending']}, Overdue={homework_stats['overdue']}
Flashcards: Due today={flashcard_stats['due_today']}, Accuracy={flashcard_stats['accuracy_7_days']}%
Past Papers: {paper_count} completed
Weak topics: {', '.join([t['topic'] for t in weak_topics]) if weak_topics else 'None'}
Subjects: {', '.join([s['name'] for s in subjects])}"""

                prompt = f"""{context}

Student's question: {coach_question}

Provide specific, actionable advice based on their actual data. Be encouraging but realistic."""

                result = call_claude(prompt, system="You are an experienced study coach helping a GCSE student.")
                if not result.startswith("Error:"):
                    st.markdown("### 💡 Study Coach Advice")
                    st.markdown(result)
                else:
                    st.error(result)


def _render_essay_tab(subjects, call_claude):
    """Render the essay helper tab."""
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

Provide: 1. Key points 2. Structure 3. Keywords 4. Common mistakes 5. How to get full marks"""

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.markdown("### Essay Plan")
                        st.markdown(result)
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
                    prompt = f"""Analyse this GCSE {essay_subject['name']} essay:

Question: {essay_question}
Marks available: {essay_marks}

Student's essay:
{essay_text}

Provide: 1. Estimated mark 2. What was done well 3. Areas to improve 4. Missing points 5. Suggestions"""

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

Original: {para_text}
Goal: {para_goal}

Provide: 1. The improved paragraph 2. What you changed and why"""

                    result = call_claude(prompt)
                    if not result.startswith("Error:"):
                        st.markdown("### Improved Paragraph")
                        st.markdown(result)
                    else:
                        st.error(result)
            else:
                st.warning("Please enter a paragraph.")
