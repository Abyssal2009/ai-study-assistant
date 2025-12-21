"""
Study Assistant - Modular CSS Styles
====================================

This package provides a modular CSS system for the Streamlit application.
Styles are organized into logical modules for maintainability.

Modules:
    _variables    - Design tokens (colors, fonts, spacing, etc.)
    _typography   - Headings, body text, links
    _layout       - Containers, spacing, alignment
    _navigation   - Sidebar and navigation
    _cards        - Stat cards, item cards
    _badges       - Tags, badges, status indicators
    _interactive  - Buttons, tabs, expanders
    _components   - Timer, flashcards, chat, etc.
    _forms        - Inputs, selects, textareas
    _interactions - Hover, focus, animations, states
    _utilities    - Helper classes, responsive

Usage:
    from styles import CUSTOM_CSS, apply_styles

    # In your Streamlit app:
    apply_styles(st)

    # Or manually:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
"""

from ._variables import VARIABLES_CSS
from ._typography import TYPOGRAPHY_CSS
from ._layout import LAYOUT_CSS
from ._navigation import NAVIGATION_CSS
from ._cards import CARDS_CSS
from ._badges import BADGES_CSS
from ._interactive import INTERACTIVE_CSS
from ._components import COMPONENTS_CSS
from ._forms import FORMS_CSS
from ._interactions import INTERACTIONS_CSS
from ._utilities import UTILITIES_CSS


# Combine all CSS modules in the correct order
CUSTOM_CSS = f"""
<style>
{VARIABLES_CSS}
{TYPOGRAPHY_CSS}
{LAYOUT_CSS}
{NAVIGATION_CSS}
{CARDS_CSS}
{BADGES_CSS}
{INTERACTIVE_CSS}
{COMPONENTS_CSS}
{FORMS_CSS}
{INTERACTIONS_CSS}
{UTILITIES_CSS}
</style>
"""


def apply_styles(st):
    """Apply all custom CSS styles to a Streamlit app.

    Args:
        st: The Streamlit module (import streamlit as st)

    Example:
        import streamlit as st
        from styles import apply_styles

        apply_styles(st)
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_module_css(module_name: str) -> str:
    """Get CSS for a specific module.

    Args:
        module_name: One of 'variables', 'typography', 'layout',
                    'navigation', 'cards', 'badges', 'interactive',
                    'components', 'forms', 'utilities'

    Returns:
        The CSS string for that module.

    Raises:
        ValueError: If module_name is not recognized.
    """
    modules = {
        'variables': VARIABLES_CSS,
        'typography': TYPOGRAPHY_CSS,
        'layout': LAYOUT_CSS,
        'navigation': NAVIGATION_CSS,
        'cards': CARDS_CSS,
        'badges': BADGES_CSS,
        'interactive': INTERACTIVE_CSS,
        'components': COMPONENTS_CSS,
        'forms': FORMS_CSS,
        'interactions': INTERACTIONS_CSS,
        'utilities': UTILITIES_CSS,
    }

    if module_name not in modules:
        valid = ', '.join(modules.keys())
        raise ValueError(f"Unknown module: {module_name}. Valid: {valid}")

    return modules[module_name]


def apply_module(st, module_name: str):
    """Apply CSS for a specific module only.

    Useful for debugging or partial styling.

    Args:
        st: The Streamlit module
        module_name: The module to apply
    """
    css = get_module_css(module_name)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Export commonly used items
__all__ = [
    'CUSTOM_CSS',
    'apply_styles',
    'get_module_css',
    'apply_module',
    # Individual modules for advanced usage
    'VARIABLES_CSS',
    'TYPOGRAPHY_CSS',
    'LAYOUT_CSS',
    'NAVIGATION_CSS',
    'CARDS_CSS',
    'BADGES_CSS',
    'INTERACTIVE_CSS',
    'COMPONENTS_CSS',
    'FORMS_CSS',
    'INTERACTIONS_CSS',
    'UTILITIES_CSS',
]
