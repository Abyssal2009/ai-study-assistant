"""
Study Assistant - Bubble Ace Page
AI chatbot study buddy.
"""

import streamlit as st
import database as db
from utils import call_claude, CLAUDE_MODELS, DEFAULT_MODEL


def render():
    """Render the Bubble Ace chatbot page."""
    st.title("🫧 Bubble Ace")
    st.markdown("Your AI study buddy! Ask me anything about your studies.")

    # Session state setup
    if 'bubble_ace_api_key' not in st.session_state:
        st.session_state.bubble_ace_api_key = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = DEFAULT_MODEL

    # Settings expander
    with st.expander("⚙️ Settings", expanded=not st.session_state.bubble_ace_api_key):
        # API Key input
        api_key = st.text_input(
            "Claude API Key",
            value=st.session_state.bubble_ace_api_key,
            type="password",
            placeholder="sk-ant-..."
        )
        if api_key != st.session_state.bubble_ace_api_key:
            st.session_state.bubble_ace_api_key = api_key
            st.success("API key saved!")

        # Model selector
        st.markdown("**AI Model:**")
        col1, col2 = st.columns(2)

        with col1:
            haiku = CLAUDE_MODELS['haiku']
            is_haiku = st.session_state.ai_model == 'haiku'
            if st.button(
                f"{haiku['icon']} {haiku['name']}",
                type="primary" if is_haiku else "secondary",
                use_container_width=True,
                key="btn_haiku"
            ):
                st.session_state.ai_model = 'haiku'
                st.rerun()
            st.caption(haiku['description'])

        with col2:
            sonnet = CLAUDE_MODELS['sonnet']
            is_sonnet = st.session_state.ai_model == 'sonnet'
            if st.button(
                f"{sonnet['icon']} {sonnet['name']}",
                type="primary" if is_sonnet else "secondary",
                use_container_width=True,
                key="btn_sonnet"
            ):
                st.session_state.ai_model = 'sonnet'
                st.rerun()
            st.caption(sonnet['description'])

        current_model = CLAUDE_MODELS[st.session_state.ai_model]
        st.info(f"Using: {current_model['icon']} **{current_model['name']}**")

    if not st.session_state.bubble_ace_api_key:
        st.warning("Please enter your Claude API key above to start chatting!")
        st.stop()

    # Subject context
    subjects = db.get_all_subjects()
    if subjects:
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_subject = st.selectbox(
                "Subject context (optional):",
                options=[None] + subjects,
                format_func=lambda x: "General" if x is None else x['name']
            )
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

    # Quick actions
    st.markdown("**Quick actions:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Explain a topic"):
            st.session_state.quick_prompt = "Can you explain "
    with col2:
        if st.button("❓ Quiz me"):
            st.session_state.quick_prompt = "Quiz me on "
    with col3:
        if st.button("📚 Study tips"):
            st.session_state.quick_prompt = "Give me study tips for "
    with col4:
        if st.button("✍️ Essay help"):
            st.session_state.quick_prompt = "Help me plan an essay about "

    # Chat display
    st.markdown("---")
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">{msg['content']}</div>
            """, unsafe_allow_html=True)

    # Chat input
    default_text = st.session_state.pop('quick_prompt', '')
    user_input = st.text_input("Ask Bubble Ace:", value=default_text, key="chat_input")

    if st.button("Send", type="primary") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Bubble Ace is thinking..."):
            subject_context = ""
            if subjects and selected_subject:
                subject_context = f"The student is currently studying {selected_subject['name']}. "

            system = f"""You are Bubble Ace, a friendly and encouraging AI study buddy for GCSE students.
{subject_context}
Use British English. Be helpful, clear, and supportive.
Keep responses concise but informative. Use examples when helpful."""

            response = call_claude(
                st.session_state.bubble_ace_api_key,
                user_input,
                system,
                model=st.session_state.ai_model
            )
            st.session_state.chat_history.append({"role": "assistant", "content": response})

        st.rerun()
