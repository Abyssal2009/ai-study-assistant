"""
Study Assistant - Past Papers Page
Track and analyze past paper performance.
"""

import streamlit as st
import database as db


def render():
    """Render the Past Papers page."""
    st.title("📄 Past Papers")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "➕ Add Paper", "📚 All Papers"])

    # TAB 1: Analysis
    with tab1:
        st.markdown("### Performance Analysis")

        # Overall stats
        paper_count = db.get_paper_count()
        weak_topics = db.get_weak_topics(limit=5)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Papers Completed", paper_count)

        with col2:
            if weak_topics:
                st.markdown("**Weak Topics (< 70%):**")
                for topic in weak_topics:
                    color = "#e74c3c" if topic['percentage'] < 50 else "#f39c12"
                    st.markdown(f"""
                    <div style="background: {color}22; padding: 8px; margin: 4px 0; border-radius: 4px; border-left: 3px solid {color};">
                        {topic['topic']} - <strong>{topic['percentage']}%</strong>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Complete some papers to see weak topics")

        # Subject breakdown
        if paper_count > 0:
            st.markdown("---")
            st.markdown("### Subject Performance")

            for subject in subjects:
                stats = db.get_subject_paper_stats(subject['id'])
                if stats and stats['paper_count'] > 0:
                    st.markdown(f"**{subject['name']}**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Papers", stats['paper_count'])
                    with col2:
                        st.metric("Avg Score", f"{stats['average_percentage']:.0f}%")
                    with col3:
                        st.metric("Total Marks", f"{stats['total_marks_achieved']}/{stats['total_marks_possible']}")
                    st.progress(stats['average_percentage'] / 100)
                    st.markdown("---")

    # TAB 2: Add Paper
    with tab2:
        st.markdown("### Log a Past Paper")

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
                    db.add_past_paper(
                        subject_id=subject['id'],
                        paper_name=paper_name,
                        exam_board=exam_board,
                        year=year,
                        total_marks=total_marks,
                        marks_achieved=marks_achieved,
                        time_taken_minutes=time_taken,
                        notes=notes
                    )
                    percentage = (marks_achieved / total_marks) * 100
                    st.success(f"Paper saved! Score: {marks_achieved}/{total_marks} ({percentage:.0f}%)")
                    st.rerun()
                else:
                    st.error("Please fill in required fields")

    # TAB 3: All Papers
    with tab3:
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
                percentage = (paper['marks_achieved'] / paper['total_marks']) * 100 if paper['total_marks'] > 0 else 0

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
                        st.markdown(f"**Score:** {paper['marks_achieved']}/{paper['total_marks']}")
                        st.markdown(f"**Year:** {paper.get('year', 'N/A')}")
                    with col3:
                        st.markdown(f"""
                        <div style="background: {color}; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                            <h2 style="margin: 0; color: white;">{percentage:.0f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    if paper.get('notes'):
                        st.markdown(f"**Notes:** {paper['notes']}")

                    if st.button("🗑️ Delete", key=f"del_paper_{paper['id']}"):
                        db.delete_past_paper(paper['id'])
                        st.rerun()
        else:
            st.info("No past papers logged yet. Add some using the 'Add Paper' tab!")
