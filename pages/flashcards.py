"""
Study Assistant - Flashcards Page
Spaced repetition flashcard system with SM-2 algorithm.
"""

import streamlit as st
import database as db


def render():
    """Render the Flashcards page."""
    st.title("🃏 Flashcards")
    st.markdown("Create and review flashcards using spaced repetition for better memory retention.")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Add your subjects first in **Subjects** (under Settings) to start creating flashcards.")
        st.stop()

    # Session state for review
    if 'review_mode' not in st.session_state:
        st.session_state.review_mode = False
    if 'review_cards' not in st.session_state:
        st.session_state.review_cards = []
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False

    tab1, tab2, tab3 = st.tabs(["📖 Review", "➕ Add Cards", "📚 All Cards"])

    # TAB 1: Review
    with tab1:
        if not st.session_state.review_mode:
            # Show review options
            due_count = db.get_due_flashcards_count()

            st.markdown(f"### Cards Due Today: **{due_count}**")

            col1, col2 = st.columns(2)
            with col1:
                review_subject = st.selectbox(
                    "Select subject:",
                    options=[None] + subjects,
                    format_func=lambda x: "All Subjects" if x is None else x['name'],
                    key="review_subject_select"
                )
            with col2:
                review_limit = st.number_input("Cards to review:", min_value=5, max_value=100, value=20)

            if st.button("🎯 Start Review", type="primary"):
                subject_id = review_subject['id'] if review_subject else None
                cards = db.get_due_flashcards(subject_id=subject_id, limit=review_limit)
                if cards:
                    st.session_state.review_mode = True
                    st.session_state.review_cards = cards
                    st.session_state.review_index = 0
                    st.session_state.show_answer = False
                    st.rerun()
                else:
                    st.success("No cards due for review! 🎉")

        else:
            # Review mode
            cards = st.session_state.review_cards
            index = st.session_state.review_index

            if index >= len(cards):
                st.success("🎉 Review Complete!")
                st.markdown(f"You reviewed **{len(cards)}** cards.")
                if st.button("Finish"):
                    st.session_state.review_mode = False
                    st.rerun()
            else:
                card = cards[index]
                progress = (index + 1) / len(cards)
                st.progress(progress, text=f"Card {index + 1} of {len(cards)}")

                st.markdown(f"**Subject:** {card['subject_name']}")
                if card.get('topic'):
                    st.caption(f"Topic: {card['topic']}")

                # Question card
                st.markdown(f"""
                <div class="flashcard">
                    <div style="font-size: 1.3rem;">{card['question']}</div>
                </div>
                """, unsafe_allow_html=True)

                if not st.session_state.show_answer:
                    if st.button("Show Answer", type="primary", use_container_width=True):
                        st.session_state.show_answer = True
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div style="background: #e8f5e9; padding: 20px; border-radius: 12px; margin: 10px 0;">
                        <strong>Answer:</strong><br>{card['answer']}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("**How well did you know this?**")
                    col1, col2, col3, col4, col5 = st.columns(5)

                    ratings = [
                        (col1, "😰 Again", 1),
                        (col2, "😕 Hard", 2),
                        (col3, "😐 Okay", 3),
                        (col4, "🙂 Good", 4),
                        (col5, "😄 Easy", 5)
                    ]

                    for col, label, quality in ratings:
                        with col:
                            if st.button(label, key=f"rate_{quality}"):
                                db.review_flashcard(card['id'], quality)
                                st.session_state.review_index += 1
                                st.session_state.show_answer = False
                                st.rerun()

                if st.button("Exit Review"):
                    st.session_state.review_mode = False
                    st.rerun()

    # TAB 2: Add Cards
    with tab2:
        st.markdown("### Add New Flashcard")

        with st.form("add_flashcard"):
            subject = st.selectbox(
                "Subject *",
                options=subjects,
                format_func=lambda x: x['name']
            )
            topic = st.text_input("Topic (optional)", placeholder="e.g., Cell Biology, Photosynthesis")
            question = st.text_area("Question *", placeholder="e.g., What is the function of mitochondria?")
            answer = st.text_area("Answer *", placeholder="e.g., Mitochondria are the powerhouse of the cell, producing ATP through cellular respiration.")

            if st.form_submit_button("Add Flashcard", type="primary"):
                if question and answer:
                    db.add_flashcard(
                        subject_id=subject['id'],
                        question=question,
                        answer=answer,
                        topic=topic
                    )
                    st.success("✓ Flashcard added! Add another or switch to the Review tab.")
                    st.rerun()
                else:
                    st.error("Please fill in both the question and answer fields.")

    # TAB 3: All Cards
    with tab3:
        all_cards = db.get_all_flashcards()
        if all_cards:
            # Group by subject
            filter_subject = st.selectbox(
                "Filter by subject:",
                options=[None] + subjects,
                format_func=lambda x: "All Subjects" if x is None else x['name'],
                key="filter_cards"
            )

            filtered = all_cards
            if filter_subject:
                filtered = [c for c in filtered if c['subject_id'] == filter_subject['id']]

            st.markdown(f"**{len(filtered)} cards**")

            for card in filtered[:50]:
                with st.expander(f"{card['question'][:50]}..."):
                    st.markdown(f"**Q:** {card['question']}")
                    st.markdown(f"**A:** {card['answer']}")
                    st.caption(f"Subject: {card['subject_name']} | Topic: {card.get('topic', 'N/A')}")

                    if st.button("🗑️ Delete", key=f"del_card_{card['id']}"):
                        db.delete_flashcard(card['id'])
                        st.rerun()
        else:
            st.info("No flashcards yet. Add some using the 'Add Cards' tab!")
