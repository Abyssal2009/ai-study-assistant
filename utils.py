"""
Study Assistant - Utility Functions
Common helper functions used across the application.
"""

from datetime import date, datetime, timedelta


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
    return f'<span style="background-color: {colour}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{priority.upper()}</span>'


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


def call_claude(api_key: str, prompt: str, system: str = None) -> str:
    """Call the Claude API with a prompt."""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        messages = [{"role": "user", "content": prompt}]

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system or "You are a helpful study assistant for GCSE students. Use British English spellings.",
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


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
