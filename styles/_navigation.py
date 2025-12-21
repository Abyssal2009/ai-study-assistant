"""
Navigation Styles
Sidebar, navigation buttons, and menu styling.
"""

NAVIGATION_CSS = """
    /* =========================================
       SIDEBAR CONTAINER
       ========================================= */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            var(--color-dark-bg) 0%,
            var(--color-dark-surface) 50%,
            var(--color-dark-accent) 100%
        );
    }

    /* =========================================
       SIDEBAR TYPOGRAPHY
       ========================================= */

    [data-testid="stSidebar"] h1 {
        color: var(--color-accent) !important;
        -webkit-text-fill-color: var(--color-accent) !important;
        font-size: var(--text-2xl) !important;
        text-align: center;
        padding: var(--space-4) 0;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--color-accent) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: white !important;
    }

    /* =========================================
       NAVIGATION RADIO BUTTONS
       ========================================= */

    /* Remove default gaps */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] {
        padding: 0 !important;
    }

    /* Navigation item base styles */
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        padding: var(--space-3) var(--space-4) !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all var(--transition-normal) !important;
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-medium) !important;
    }

    /* Hover state */
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(233, 69, 96, 0.15) !important;
        padding-left: var(--space-6) !important;
        border-left: 3px solid rgba(233, 69, 96, 0.5) !important;
    }

    /* Active/selected state */
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(
            90deg,
            var(--color-accent) 0%,
            var(--color-dark-accent) 100%
        ) !important;
        font-weight: var(--font-semibold) !important;
        border-left: 4px solid var(--color-accent) !important;
        padding-left: var(--space-5) !important;
    }

    /* =========================================
       SIDEBAR METRICS
       ========================================= */

    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--color-success-light) !important;
        -webkit-text-fill-color: var(--color-success-light) !important;
        font-size: var(--text-2xl) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }

    /* =========================================
       SIDEBAR BUTTONS
       ========================================= */

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }

    /* =========================================
       SIDEBAR DIVIDERS
       ========================================= */

    [data-testid="stSidebar"] hr {
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        margin: var(--space-4) 0;
    }

    /* =========================================
       SIDEBAR EXPANDERS
       ========================================= */

    [data-testid="stSidebar"] .stExpander {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-testid="stSidebar"] .stExpander summary {
        color: white !important;
    }
"""
