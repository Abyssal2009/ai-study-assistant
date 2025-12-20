"""
Study Assistant - Settings Page
Application settings and configuration.
"""

import streamlit as st
import database as db


def render():
    """Render the Settings page."""
    st.title("⚙️ Settings")

    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "📧 Email Reminders", "🗄️ Data"])

    # TAB 1: API Keys
    with tab1:
        st.markdown("### Claude API Key")
        st.markdown("""
        The AI features (Bubble Ace, AI Tools) require a Claude API key from Anthropic.

        **How to get a key:**
        1. Go to [console.anthropic.com](https://console.anthropic.com)
        2. Create an account or sign in
        3. Generate an API key
        4. Paste it below
        """)

        if 'bubble_ace_api_key' not in st.session_state:
            st.session_state.bubble_ace_api_key = ""

        api_key = st.text_input(
            "API Key",
            value=st.session_state.bubble_ace_api_key,
            type="password",
            placeholder="sk-ant-..."
        )

        if api_key != st.session_state.bubble_ace_api_key:
            st.session_state.bubble_ace_api_key = api_key
            st.success("API key saved for this session!")

        st.info("Note: API keys are only stored for the current session and are not saved to disk.")

    # TAB 2: Email Reminders
    with tab2:
        st.markdown("### Email Reminder Settings")
        st.markdown("""
        Get daily email reminders about your homework, exams, and flashcards.

        **Setup requires:**
        1. A Gmail account (or other email provider)
        2. An app password (not your regular password)

        See the `email_reminder.py` file for configuration.
        """)

        st.warning("Email reminders require manual setup. Check the documentation for details.")

        # Show current config status
        try:
            import config
            if hasattr(config, 'EMAIL_ADDRESS') and config.EMAIL_ADDRESS:
                st.success(f"Email configured: {config.EMAIL_ADDRESS}")
            else:
                st.info("Email not configured yet.")
        except ImportError:
            st.info("Config file not found. Copy config.example.py to config.py")

    # TAB 3: Data Management
    with tab3:
        st.markdown("### Data Management")

        # Database stats
        st.markdown("#### Database Statistics")

        col1, col2 = st.columns(2)

        with col1:
            subjects = db.get_all_subjects()
            st.metric("Subjects", len(subjects))

            hw_stats = db.get_homework_stats()
            st.metric("Homework Items", hw_stats['pending'] + hw_stats['completed_total'])

            notes_count = db.get_notes_count()
            st.metric("Notes", notes_count)

        with col2:
            fc_stats = db.get_flashcard_stats()
            st.metric("Flashcards", fc_stats['total'])

            paper_count = db.get_paper_count()
            st.metric("Past Papers", paper_count)

            exams = db.get_all_exams()
            st.metric("Exams", len(exams) if exams else 0)

        st.markdown("---")
        st.markdown("#### Danger Zone")

        st.warning("These actions cannot be undone!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear Completed Homework"):
                if st.session_state.get('confirm_clear_hw'):
                    db.clear_completed_homework()
                    st.session_state.confirm_clear_hw = False
                    st.success("Cleared completed homework!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_hw = True
                    st.warning("Click again to confirm")

        with col2:
            if st.button("🗑️ Clear All Flashcard Reviews"):
                if st.session_state.get('confirm_clear_reviews'):
                    db.reset_flashcard_reviews()
                    st.session_state.confirm_clear_reviews = False
                    st.success("Reset all flashcard reviews!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_reviews = True
                    st.warning("Click again to confirm")

        st.markdown("---")
        st.markdown("#### About")
        st.markdown("""
        **Study Assistant v1.8**

        A personal study tool built for GCSE students.

        Features:
        - Homework tracking
        - Exam calendar
        - Flashcards with spaced repetition (SM-2)
        - Focus timer
        - Notes with OCR import
        - Past paper analysis
        - AI study tools powered by Claude

        Built with Streamlit + Python + SQLite
        """)
