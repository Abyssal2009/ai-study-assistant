"""
Form Element Styles
Inputs, selects, textareas, and form layouts.
"""

FORMS_CSS = """
    /* =========================================
       FORM LAYOUT
       ========================================= */

    .stForm {
        margin-bottom: var(--space-8);
        padding: var(--space-6);
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
    }

    /* Form group spacing */
    .stTextInput,
    .stSelectbox,
    .stTextArea,
    .stNumberInput,
    .stDateInput {
        margin-bottom: var(--space-5);
    }

    /* =========================================
       FORM LABELS
       ========================================= */

    .stTextInput label,
    .stSelectbox label,
    .stTextArea label,
    .stNumberInput label,
    .stDateInput label,
    .stSlider label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-semibold) !important;
        color: var(--text-secondary) !important;
        letter-spacing: var(--tracking-wide);
        margin-bottom: var(--space-2);
        display: block;
    }

    /* Required field indicator */
    .stTextInput label span[style*="color: red"],
    .stSelectbox label span[style*="color: red"] {
        color: var(--color-accent) !important;
        font-weight: var(--font-bold);
    }

    /* =========================================
       TEXT INPUTS
       ========================================= */

    .stTextInput > div > div > input {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: var(--radius-md);
        border: var(--border-width-2) solid var(--border-color);
        padding: var(--space-3) var(--space-5);
        transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
        color: var(--text-primary);
        background: var(--surface-primary);
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-tertiary);
        font-style: italic;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        outline: none;
    }

    /* =========================================
       SELECT BOXES
       ========================================= */

    .stSelectbox > div > div {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: var(--radius-md);
        padding: var(--space-1) 0;
    }

    .stSelectbox [data-baseweb="select"] > div {
        font-size: var(--text-base) !important;
        border-radius: var(--radius-md);
    }

    .stSelectbox [data-baseweb="select"] > div:focus-within {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* Dropdown menu */
    [data-baseweb="popover"] {
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
    }

    [data-baseweb="menu"] {
        border-radius: var(--radius-md);
    }

    [data-baseweb="menu"] li {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        padding: var(--space-3) var(--space-4);
    }

    /* =========================================
       TEXT AREAS
       ========================================= */

    .stTextArea > div > div > textarea {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: var(--radius-md);
        border: var(--border-width-2) solid var(--border-color);
        padding: var(--space-4) var(--space-5);
        line-height: var(--leading-relaxed);
        color: var(--text-primary);
        background: var(--surface-primary);
        resize: vertical;
    }

    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-tertiary);
        font-style: italic;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        outline: none;
    }

    /* =========================================
       NUMBER INPUTS
       ========================================= */

    .stNumberInput > div > div > input {
        font-family: var(--font-mono) !important;
        font-size: var(--text-base) !important;
        font-variant-numeric: tabular-nums;
        border-radius: var(--radius-md);
        border: var(--border-width-2) solid var(--border-color);
        padding: var(--space-3) var(--space-4);
        color: var(--text-primary);
        background: var(--surface-primary);
    }

    .stNumberInput > div > div > input:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* =========================================
       DATE INPUTS
       ========================================= */

    .stDateInput > div > div > input {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: var(--radius-md);
        border: var(--border-width-2) solid var(--border-color);
        padding: var(--space-3) var(--space-4);
        color: var(--text-primary);
        background: var(--surface-primary);
    }

    .stDateInput > div > div > input:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* =========================================
       SLIDERS
       ========================================= */

    .stSlider {
        margin-top: var(--space-4);
        margin-bottom: var(--space-6);
        padding: 0 var(--space-2);
    }

    .stSlider [data-baseweb="slider"] {
        margin-top: var(--space-2);
    }

    .stSlider [data-baseweb="slider"] div {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
    }

    /* Slider track */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--color-primary);
    }

    /* =========================================
       HELP TEXT
       ========================================= */

    .stTextInput small,
    .stSelectbox small,
    .stTextArea small,
    .stNumberInput small {
        font-size: var(--text-xs) !important;
        color: var(--text-tertiary);
        margin-top: var(--space-1);
        display: block;
    }

    /* =========================================
       FILE UPLOADER
       ========================================= */

    .stFileUploader {
        margin-bottom: var(--space-5);
    }

    .stFileUploader > div {
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-8);
        text-align: center;
        transition: all var(--transition-normal);
        color: var(--text-secondary);
    }

    .stFileUploader > div:hover {
        border-color: var(--color-primary);
        background: rgba(102, 126, 234, 0.05);
    }

    /* =========================================
       DOWNLOAD BUTTON
       ========================================= */

    .stDownloadButton {
        margin: var(--space-4) 0;
    }

    .stDownloadButton > button {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        font-weight: var(--font-semibold);
    }
"""
