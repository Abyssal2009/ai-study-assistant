"""
Study Assistant - Bubble Ace Page
AI chatbot study buddy with RAG (Retrieval-Augmented Generation).
"""

import streamlit as st
import database as db
from utils import call_claude_chat_with_rag, CLAUDE_MODELS, DEFAULT_MODEL
import uuid
import json


def render():
    """Render the Bubble Ace chatbot page."""
    st.title("🫧 Bubble Ace")
    st.markdown("Your AI study buddy! Ask questions, get explanations, or request quizzes on any topic.")

    # Session state setup
    if 'bubble_ace_api_key' not in st.session_state:
        st.session_state.bubble_ace_api_key = ""
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = DEFAULT_MODEL
    if 'use_rag' not in st.session_state:
        st.session_state.use_rag = True
    if 'last_sources' not in st.session_state:
        st.session_state.last_sources = []

    # Chat session ID for persistence
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = str(uuid.uuid4())

    # Load chat history from database on first load
    if 'chat_history' not in st.session_state:
        saved_messages = db.get_chat_messages(st.session_state.chat_session_id)
        st.session_state.chat_history = [
            {"role": msg['role'], "content": msg['content']}
            for msg in saved_messages
        ]

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

        # RAG toggle
        st.markdown("---")
        st.markdown("**Knowledge Base (RAG):**")
        use_rag = st.checkbox(
            "Search my notes & flashcards for context",
            value=st.session_state.use_rag,
            help="When enabled, Bubble Ace will search your notes, flashcards, and past paper topics to give more personalised answers."
        )
        if use_rag != st.session_state.use_rag:
            st.session_state.use_rag = use_rag

        if st.session_state.use_rag:
            st.caption("RAG enabled - answers will reference your study materials when relevant.")

    if not st.session_state.bubble_ace_api_key:
        st.warning("Please enter your Claude API key above to start chatting!")
        st.stop()

    # Subject context
    subjects = db.get_all_subjects()
    if subjects:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            selected_subject = st.selectbox(
                "Subject context (optional):",
                options=[None] + subjects,
                format_func=lambda x: "General" if x is None else x['name']
            )
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                db.clear_chat_session(st.session_state.chat_session_id)
                st.rerun()
        with col3:
            if st.button("🆕 New Chat"):
                st.session_state.chat_history = []
                st.session_state.chat_session_id = str(uuid.uuid4())
                st.rerun()

    # Quick actions - prominent section
    st.markdown("### ⚡ Quick Actions")
    st.caption("Click a button to start, then complete your question below.")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Explain", use_container_width=True, help="Get a clear explanation of any topic"):
            st.session_state.quick_prompt = "Can you explain "
    with col2:
        if st.button("❓ Quiz me", use_container_width=True, help="Test your knowledge with questions"):
            st.session_state.quick_prompt = "Quiz me on "
    with col3:
        if st.button("📚 Study tips", use_container_width=True, help="Get study advice for a topic"):
            st.session_state.quick_prompt = "Give me study tips for "
    with col4:
        if st.button("✍️ Essay help", use_container_width=True, help="Plan and structure an essay"):
            st.session_state.quick_prompt = "Help me plan an essay about "

    # Chat display
    st.markdown("---")
    for i, msg in enumerate(st.session_state.chat_history):
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">{msg['content']}</div>
            """, unsafe_allow_html=True)

            # Action buttons after AI responses (only for the last message)
            if i == len(st.session_state.chat_history) - 1:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("🃏 Make Flashcards", key=f"fc_{i}", help="Create flashcards from this topic"):
                        st.session_state.selected_page = "AI Tools"
                        st.session_state.ai_tools_tab = "flashcards"
                        st.rerun()
                with col2:
                    if st.button("📝 Take Quiz", key=f"quiz_{i}", help="Test your knowledge"):
                        st.session_state.selected_page = "Knowledge Gaps"
                        st.rerun()
                with col3:
                    if st.button("📅 Add to Schedule", key=f"sched_{i}", help="Schedule study time"):
                        st.session_state.selected_page = "Study Schedule"
                        st.rerun()
                with col4:
                    if st.button("📖 View Notes", key=f"notes_{i}", help="Go to Notes"):
                        st.session_state.selected_page = "Notes"
                        st.rerun()

    # Show sources from last response if RAG found any
    if st.session_state.last_sources:
        with st.expander(f"📚 Sources used ({len(st.session_state.last_sources)} items)", expanded=False):
            for source in st.session_state.last_sources:
                source_type = source.get('source_type', 'unknown')
                if source_type == 'note':
                    st.markdown(f"📝 **Note:** {source.get('title', 'Untitled')}")
                elif source_type == 'flashcard':
                    st.markdown(f"🎴 **Flashcard:** {source.get('preview', '')[:100]}...")
                elif source_type == 'past_paper':
                    st.markdown(f"📄 **Past Paper:** {source.get('title', 'Untitled')}")
                else:
                    st.markdown(f"📎 {source.get('preview', '')[:100]}...")

    # Chat input
    default_text = st.session_state.pop('quick_prompt', '')
    user_input = st.text_input("Ask Bubble Ace:", value=default_text, key="chat_input")

    if st.button("Send", type="primary") and user_input:
        # Add user message and save to database
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        db.save_chat_message(
            session_id=st.session_state.chat_session_id,
            role="user",
            content=user_input
        )

        with st.spinner("Bubble Ace is thinking..."):
            subject_context = ""
            subject_id = None
            if subjects and selected_subject:
                subject_context = f"The student is currently studying {selected_subject['name']}. "
                subject_id = selected_subject['id']

            system = f"""You are Bubble Ace, a friendly and encouraging AI study buddy for GCSE students.
{subject_context}
Use British English. Be helpful, clear, and supportive.
Keep responses concise but informative. Use examples when helpful."""

            # Use RAG-enhanced chat
            response, sources = call_claude_chat_with_rag(
                api_key=st.session_state.bubble_ace_api_key,
                messages=st.session_state.chat_history,
                system=system,
                model=st.session_state.ai_model,
                subject_id=subject_id,
                use_rag=st.session_state.use_rag
            )
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.last_sources = sources

            # Save assistant response to database
            db.save_chat_message(
                session_id=st.session_state.chat_session_id,
                role="assistant",
                content=response,
                sources_json=json.dumps(sources) if sources else None
            )

        st.rerun()
