"""
Interactive Element Styles
Buttons, tabs, expanders, progress bars.
"""

INTERACTIVE_CSS = """
    /* =========================================
       BUTTONS
       ========================================= */

    .stButton > button {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-6);
        font-weight: var(--font-semibold);
        font-size: var(--text-base);
        letter-spacing: var(--tracking-wide);
        text-transform: none;
        transition: all var(--transition-normal);
        box-shadow: var(--shadow-primary);
        margin: var(--space-1) 0;
        text-align: center;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton {
        margin-bottom: var(--space-3);
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: var(--surface-secondary);
        color: var(--color-primary);
        border: var(--border-width-2) solid var(--color-primary);
        box-shadow: none;
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--color-primary);
        color: white;
    }

    /* Danger button style */
    .btn-danger {
        background: linear-gradient(135deg, var(--color-error) 0%, #c0392b 100%) !important;
        box-shadow: var(--shadow-error) !important;
    }

    /* Success button style */
    .btn-success {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%) !important;
        box-shadow: var(--shadow-success) !important;
    }

    /* =========================================
       TABS
       ========================================= */

    .stTabs {
        margin-top: var(--space-6);
        margin-bottom: var(--space-4);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-2);
        background: var(--surface-secondary);
        padding: var(--space-2);
        border-radius: var(--radius-lg);
        margin-bottom: var(--space-6);
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-semibold) !important;
        letter-spacing: var(--tracking-wide);
        background: transparent;
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-6);
        transition: all var(--transition-normal);
        text-align: center;
        color: var(--text-secondary);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: var(--color-primary);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: var(--space-4);
    }

    /* =========================================
       EXPANDERS
       ========================================= */

    .stExpander {
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        background: var(--surface-primary);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        margin: var(--space-4) 0;
        transition: all var(--transition-normal);
    }

    .stExpander:hover {
        border-color: var(--color-accent);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.1);
    }

    .stExpander > details > summary {
        font-family: var(--font-sans) !important;
        font-weight: var(--font-semibold);
        padding: var(--space-4) var(--space-5);
        cursor: pointer;
    }

    .stExpander > details > div {
        padding: var(--space-2) var(--space-5) var(--space-5);
    }

    /* =========================================
       PROGRESS BARS
       ========================================= */

    .stProgress {
        margin: var(--space-4) 0;
    }

    .stProgress > div > div {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        border-radius: var(--radius-md);
        transition: width var(--transition-slow);
    }

    /* Custom progress bar container */
    .progress-container {
        background: var(--surface-tertiary);
        border-radius: var(--radius-md);
        height: 8px;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: var(--radius-md);
        transition: width var(--transition-slow);
    }

    .progress-bar-primary {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    }

    .progress-bar-success {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
    }

    .progress-bar-warning {
        background: linear-gradient(135deg, var(--color-warning) 0%, #e67e22 100%);
    }

    /* =========================================
       TOOLTIPS
       ========================================= */

    [data-tooltip] {
        position: relative;
        cursor: help;
    }

    [data-tooltip]:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--color-gray-800);
        color: white;
        padding: var(--space-2) var(--space-3);
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
        white-space: nowrap;
        z-index: var(--z-tooltip);
    }

    /* =========================================
       CHECKBOX & TOGGLE
       ========================================= */

    .stCheckbox {
        margin-bottom: var(--space-4);
    }

    .stCheckbox label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        padding: var(--space-2) 0;
        line-height: var(--leading-normal);
    }

    /* =========================================
       RADIO BUTTONS (non-sidebar)
       ========================================= */

    .stRadio {
        margin-bottom: var(--space-4);
    }

    .stRadio label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        padding: var(--space-2) 0;
        line-height: var(--leading-normal);
    }

    .stRadio > div[role="radiogroup"] {
        gap: var(--space-2);
    }
"""
