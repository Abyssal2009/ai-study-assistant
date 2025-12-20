"""
Study Assistant - Subjects Page
Manage study subjects.
"""

import streamlit as st
import database as db
from utils import SUBJECT_COLOURS


def render():
    """Render the Subjects management page."""
    st.title("📚 Subjects")

    tab1, tab2 = st.tabs(["📋 My Subjects", "➕ Add Subject"])

    # TAB 1: My Subjects
    with tab1:
        subjects = db.get_all_subjects()

        if subjects:
            st.markdown(f"### Your Subjects ({len(subjects)})")

            for i, subject in enumerate(subjects):
                colour = subject.get('colour') or SUBJECT_COLOURS[i % len(SUBJECT_COLOURS)]

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: {colour}; width: 20px; height: 20px; border-radius: 50%; display: inline-block;"></span>
                        <strong>{subject['name']}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    if subject.get('exam_board'):
                        st.caption(f"Exam Board: {subject['exam_board']}")

                with col2:
                    # Stats
                    hw_count = db.get_homework_count_by_subject(subject['id'])
                    fc_count = db.get_flashcard_count_by_subject(subject['id'])
                    st.caption(f"📝 {hw_count} | 🃏 {fc_count}")

                with col3:
                    if st.button("🗑️", key=f"del_subj_{subject['id']}"):
                        db.delete_subject(subject['id'])
                        st.rerun()

                st.markdown("---")
        else:
            st.info("No subjects yet. Add your GCSE subjects to get started!")

            # Quick add for common subjects
            st.markdown("### Quick Add Common Subjects")
            common_subjects = [
                "English Language", "English Literature", "Mathematics",
                "Biology", "Chemistry", "Physics", "Combined Science",
                "History", "Geography", "French", "Spanish", "German",
                "Computer Science", "Business Studies", "Art", "Music",
                "PE", "Religious Studies", "Additional Maths"
            ]

            cols = st.columns(3)
            for i, subj in enumerate(common_subjects):
                with cols[i % 3]:
                    if st.button(subj, key=f"quick_{subj}"):
                        db.add_subject(
                            name=subj,
                            colour=SUBJECT_COLOURS[i % len(SUBJECT_COLOURS)]
                        )
                        st.rerun()

    # TAB 2: Add Subject
    with tab2:
        st.markdown("### Add New Subject")

        with st.form("add_subject"):
            name = st.text_input("Subject Name *", placeholder="e.g., Biology")
            exam_board = st.text_input("Exam Board (optional)", placeholder="e.g., AQA, Edexcel, OCR")

            st.markdown("**Choose a colour:**")
            colour_cols = st.columns(8)

            for i, colour in enumerate(SUBJECT_COLOURS[:8]):
                with colour_cols[i]:
                    st.markdown(f"""
                    <div style="background: {colour}; width: 30px; height: 30px; border-radius: 4px; margin: 5px auto;"></div>
                    """, unsafe_allow_html=True)

            colour_index = st.selectbox(
                "Colour",
                options=list(range(len(SUBJECT_COLOURS))),
                format_func=lambda x: f"Colour {x + 1}"
            )

            if st.form_submit_button("Add Subject", type="primary"):
                if name:
                    db.add_subject(
                        name=name,
                        exam_board=exam_board,
                        colour=SUBJECT_COLOURS[colour_index]
                    )
                    st.success(f"Added: {name}")
                    st.rerun()
                else:
                    st.error("Please enter a subject name")
