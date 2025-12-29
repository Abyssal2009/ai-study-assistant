"""
Study Assistant - Utility Functions
Common helper functions used across the application.
"""

from datetime import date


def days_until(target_date) -> int:
    """Calculate days until a target date."""
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    return (target_date - date.today()).days


def format_due_date(due_date) -> str:
    """Format a due date with helpful text."""
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)

    days = days_until(due_date)

    if days < 0:
        return f"**OVERDUE** ({abs(days)} days ago)"
    elif days == 0:
        return "**Due TODAY**"
    elif days == 1:
        return "Due tomorrow"
    elif days <= 7:
        return f"Due in {days} days"
    else:
        return f"Due {due_date.strftime('%d %B %Y')}"


def get_priority_badge(priority: str) -> str:
    """Return HTML for a priority badge."""
    colours = {
        'high': '#e74c3c',
        'medium': '#f39c12',
        'low': '#27ae60'
    }
    colour = colours.get(priority, '#95a5a6')
    return (f'<span style="background-color: {colour}; color: white; '
            f'padding: 2px 8px; border-radius: 4px; font-size: 12px;">'
            f'{priority.upper()}</span>')


def get_urgency_colour(urgency: str) -> str:
    """Return colour for urgency level."""
    colours = {
        'critical': '#e74c3c',
        'high': '#e67e22',
        'medium': '#f39c12',
        'low': '#3498db'
    }
    return colours.get(urgency, '#3498db')


def get_urgency_icon(urgency: str) -> str:
    """Return icon for urgency level."""
    icons = {
        'critical': '🚨',
        'high': '⚠️',
        'medium': '📌',
        'low': '💡'
    }
    return icons.get(urgency, '📌')


def format_minutes(minutes: int) -> str:
    """Format minutes into hours and minutes."""
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def get_subject_colour(index: int) -> str:
    """Return a colour for a subject based on index."""
    colours = [
        '#667eea', '#e94560', '#11998e', '#f39c12', '#9b59b6',
        '#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#1abc9c',
        '#e67e22', '#8e44ad', '#16a085', '#d35400', '#2980b9'
    ]
    return colours[index % len(colours)]


# Available Claude models
CLAUDE_MODELS = {
    'haiku': {
        'id': 'claude-haiku-4-20250514',
        'name': 'Haiku (Fast)',
        'description': 'Faster responses, lower cost',
        'icon': '⚡'
    },
    'sonnet': {
        'id': 'claude-sonnet-4-20250514',
        'name': 'Sonnet (Balanced)',
        'description': 'Better quality, moderate speed',
        'icon': '✨'
    }
}

DEFAULT_MODEL = 'sonnet'


def call_claude(api_key: str, prompt: str, system: str = None, model: str = None) -> str:
    """Call the Claude API with a prompt.

    Args:
        api_key: Anthropic API key
        prompt: User message to send
        system: System prompt (optional)
        model: Model to use - 'haiku' or 'sonnet' (default: sonnet)
    """
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        # Get model ID
        model_key = model or DEFAULT_MODEL
        model_id = CLAUDE_MODELS.get(model_key, CLAUDE_MODELS[DEFAULT_MODEL])['id']

        messages = [{"role": "user", "content": prompt}]

        response = client.messages.create(
            model=model_id,
            max_tokens=2048,
            system=system or "You are a helpful study assistant for GCSE students. Use British English spellings.",
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def call_claude_with_rag(api_key: str, prompt: str, system: str = None,
                         model: str = None, subject_id: int = None,
                         use_rag: bool = True) -> tuple:
    """
    Call Claude API with RAG (Retrieval-Augmented Generation).

    This function searches your notes, flashcards, and past paper topics
    for relevant information and includes it in the prompt to give
    Claude better context for answering your questions.

    Args:
        api_key: Anthropic API key
        prompt: User message to send
        system: System prompt (optional)
        model: Model to use - 'haiku' or 'sonnet'
        subject_id: Optional subject filter for RAG search
        use_rag: Whether to use RAG (default True)

    Returns:
        Tuple of (response_text, sources_list)
        sources_list contains the documents used for context
    """
    sources = []

    # Get RAG context if enabled
    augmented_prompt = prompt
    if use_rag:
        try:
            import rag
            context, sources = rag.get_context_for_query(prompt, max_tokens=1500, subject_id=subject_id)

            if context:
                augmented_prompt = f"""I have a question: {prompt}

{context}"""
        except Exception as e:
            # RAG failed, continue without it
            pass

    # Build system prompt with RAG awareness
    base_system = system or "You are a helpful study assistant for GCSE students. Use British English spellings."

    if sources:
        base_system += """

IMPORTANT: I've provided relevant information from the student's own study materials above.
When answering:
1. Use this information when relevant to give personalised answers
2. Reference their notes/flashcards when applicable
3. If the information is helpful, mention you found it in their materials
4. If the question isn't covered by their materials, answer from your general knowledge"""

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        model_key = model or DEFAULT_MODEL
        model_id = CLAUDE_MODELS.get(model_key, CLAUDE_MODELS[DEFAULT_MODEL])['id']

        messages = [{"role": "user", "content": augmented_prompt}]

        response = client.messages.create(
            model=model_id,
            max_tokens=2048,
            system=base_system,
            messages=messages
        )

        return response.content[0].text, sources

    except Exception as e:
        return f"Error: {str(e)}", []


def call_claude_chat_with_rag(api_key: str, messages: list, system: str = None,
                               model: str = None, subject_id: int = None,
                               use_rag: bool = True) -> tuple:
    """
    Call Claude API with RAG for multi-turn chat conversations.

    Args:
        api_key: Anthropic API key
        messages: List of message dicts with 'role' and 'content'
        system: System prompt (optional)
        model: Model to use
        subject_id: Optional subject filter for RAG
        use_rag: Whether to use RAG

    Returns:
        Tuple of (response_text, sources_list)
    """
    sources = []

    # Get the last user message for RAG search
    last_user_msg = None
    for msg in reversed(messages):
        if msg['role'] == 'user':
            last_user_msg = msg['content']
            break

    # Augment last user message with RAG context
    augmented_messages = messages.copy()
    if use_rag and last_user_msg:
        try:
            import rag
            context, sources = rag.get_context_for_query(last_user_msg, max_tokens=1500, subject_id=subject_id)

            if context and sources:
                # Add context as a system-like injection in the last user message
                for i in range(len(augmented_messages) - 1, -1, -1):
                    if augmented_messages[i]['role'] == 'user':
                        augmented_messages[i] = {
                            'role': 'user',
                            'content': f"{augmented_messages[i]['content']}\n\n{context}"
                        }
                        break
        except Exception:
            pass

    # Build system prompt
    base_system = system or "You are a helpful study assistant for GCSE students. Use British English spellings."

    if sources:
        base_system += """

IMPORTANT: Relevant information from the student's study materials has been provided.
Use this information when answering, and mention when something comes from their notes."""

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        model_key = model or DEFAULT_MODEL
        model_id = CLAUDE_MODELS.get(model_key, CLAUDE_MODELS[DEFAULT_MODEL])['id']

        response = client.messages.create(
            model=model_id,
            max_tokens=2048,
            system=base_system,
            messages=augmented_messages
        )

        return response.content[0].text, sources

    except Exception as e:
        return f"Error: {str(e)}", []


# Urgency labels for recommendations
URGENCY_LABELS = {
    'critical': '🚨 CRITICAL',
    'high': '⚠️ HIGH',
    'medium': '📌 MEDIUM',
    'low': '💡 LOW'
}

# Subject colours for consistent display
SUBJECT_COLOURS = [
    '#667eea', '#e94560', '#11998e', '#f39c12', '#9b59b6',
    '#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#1abc9c',
    '#e67e22', '#8e44ad', '#16a085', '#d35400', '#2980b9'
]
