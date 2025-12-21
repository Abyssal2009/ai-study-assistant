"""
Study Assistant - CSS Styles
All custom styling for the Streamlit application.
"""

CUSTOM_CSS = """
<style>
    /* =========================================
       TYPOGRAPHY HIERARCHY
       ========================================= */

    /* Page titles - Large gradient text */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        margin-top: 1rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
    }

    /* Section headers */
    h2 {
        color: #1a1a2e !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e94560;
    }

    /* Subsection headers */
    h3 {
        color: #16213e !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    /* Body text improvements */
    p, li {
        line-height: 1.7;
        color: #333;
        margin-bottom: 0.75rem;
    }

    /* List spacing */
    ul, ol {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        padding-left: 1.5rem;
    }

    li {
        margin-bottom: 0.5rem;
        padding-left: 0.25rem;
    }

    /* =========================================
       LAYOUT & SPACING
       ========================================= */

    /* Main container */
    .main {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    /* Block container spacing */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Element vertical spacing */
    .element-container {
        margin-bottom: 1.25rem;
    }

    /* Column gaps */
    [data-testid="column"] {
        padding: 0 1rem;
    }

    /* Row spacing */
    .row-widget {
        margin-bottom: 1.5rem;
    }

    /* Section containers */
    .section-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }

    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e94560, transparent);
        margin: 2.5rem 0;
    }

    /* Markdown block spacing */
    .stMarkdown {
        margin-bottom: 1rem;
    }

    /* Spacing after metrics row */
    [data-testid="stMetric"] {
        padding: 0.5rem;
    }

    /* =========================================
       SIDEBAR NAVIGATION
       ========================================= */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    [data-testid="stSidebar"] h1 {
        color: #e94560 !important;
        -webkit-text-fill-color: #e94560 !important;
        font-size: 1.5rem !important;
        text-align: center;
        padding: 1rem 0;
    }

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e94560 !important;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Flush navigation buttons */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        padding: 0.75rem 1rem !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.2s ease !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(233, 69, 96, 0.15) !important;
        padding-left: 1.5rem !important;
        border-left: 3px solid rgba(233, 69, 96, 0.5) !important;
    }

    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg, #e94560 0%, #0f3460 100%) !important;
        font-weight: 600 !important;
        border-left: 4px solid #e94560 !important;
        padding-left: 1.25rem !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] {
        padding: 0 !important;
    }

    /* Sidebar metrics */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #38ef7d !important;
        -webkit-text-fill-color: #38ef7d !important;
        font-size: 1.5rem !important;
    }

    /* =========================================
       STAT CARDS
       ========================================= */

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.75rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 0.5rem 0;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
    }

    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.75rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(17, 153, 142, 0.25);
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 0.5rem 0;
    }

    .stat-card-green:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.35);
    }

    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.75rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(245, 87, 108, 0.25);
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 0.5rem 0;
    }

    .stat-card-orange:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.35);
    }

    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.75rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.25);
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 0.5rem 0;
    }

    .stat-card-blue:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.35);
    }

    /* Stat card number */
    .stat-card h1, .stat-card-green h1, .stat-card-orange h1, .stat-card-blue h1 {
        color: white !important;
        -webkit-text-fill-color: white !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* =========================================
       ITEM CARDS
       ========================================= */

    .homework-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }

    .homework-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }

    .exam-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem 1.75rem;
        border-radius: 16px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(250, 112, 154, 0.25);
        transition: transform 0.2s;
    }

    .exam-card:hover {
        transform: scale(1.02);
    }

    /* Note cards */
    .note-card {
        background: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* =========================================
       BADGES & TAGS
       ========================================= */

    .priority-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
    }

    .priority-medium {
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(243, 156, 18, 0.3);
    }

    .priority-low {
        background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(39, 174, 96, 0.3);
    }

    .subject-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .overdue {
        color: #e74c3c;
        font-weight: 700;
        text-shadow: 0 0 8px rgba(231, 76, 60, 0.2);
    }

    .streak-display {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(245, 175, 25, 0.3);
    }

    /* =========================================
       INTERACTIVE ELEMENTS
       ========================================= */

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
        margin: 0.25rem 0;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Button container spacing */
    .stButton {
        margin-bottom: 0.75rem;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: #f8f9fa;
        color: #667eea;
        border: 2px solid #667eea;
    }

    /* Tabs */
    .stTabs {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 8px;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    /* Tab panel content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }

    /* Expanders */
    .stExpander {
        border-radius: 12px;
        border: 1px solid #e9ecef;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        overflow: hidden;
        margin: 1rem 0;
    }

    .stExpander:hover {
        border-color: #e94560;
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.1);
    }

    .stExpander > details > summary {
        padding: 1rem 1.25rem;
    }

    .stExpander > details > div {
        padding: 0.5rem 1.25rem 1.25rem;
    }

    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }

    /* =========================================
       SPECIAL COMPONENTS
       ========================================= */

    /* Timer display */
    .timer-display {
        font-size: 5rem;
        font-weight: 800;
        text-align: center;
        font-family: 'SF Mono', 'Consolas', monospace;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
        text-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }

    /* Flashcard */
    .flashcard {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        font-size: 1.25rem;
        line-height: 1.6;
        transition: transform 0.3s;
    }

    .flashcard:hover {
        transform: scale(1.02);
    }

    /* Chat bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.75rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
        line-height: 1.5;
    }

    .assistant-message {
        background: #f8f9fa;
        color: #1a1a2e;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.75rem 0;
        max-width: 80%;
        border-left: 3px solid #e94560;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        line-height: 1.5;
    }

    /* =========================================
       MESSAGES & ALERTS
       ========================================= */

    .success-msg {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.2);
    }

    .warning-msg {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.2);
    }

    .info-box {
        background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #1a1a2e;
        font-weight: 500;
    }

    /* =========================================
       FORM ELEMENTS
       ========================================= */

    /* Form group spacing */
    .stTextInput, .stSelectbox, .stTextArea, .stNumberInput, .stDateInput {
        margin-bottom: 1.25rem;
    }

    /* Form labels */
    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stNumberInput label, .stDateInput label {
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.85rem 1.25rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 10px;
        padding: 0.25rem 0;
    }

    /* Text areas */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 1rem 1.25rem;
        line-height: 1.6;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* Sliders */
    .stSlider {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        padding: 0 0.5rem;
    }

    /* Checkboxes and radio buttons */
    .stCheckbox, .stRadio {
        margin-bottom: 1rem;
    }

    .stCheckbox label, .stRadio label {
        padding: 0.5rem 0;
    }

    /* =========================================
       RESPONSIVE ADJUSTMENTS
       ========================================= */

    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }

        h2 {
            margin-top: 2rem !important;
        }

        .main {
            padding: 1rem 1.5rem;
        }

        .timer-display {
            font-size: 3.5rem;
        }

        .stat-card, .stat-card-green, .stat-card-orange, .stat-card-blue {
            padding: 1.25rem 1rem;
            margin: 0.75rem 0;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
        }
    }

    /* =========================================
       WHITESPACE UTILITIES
       ========================================= */

    /* Extra spacing helpers */
    .spacer-sm { height: 1rem; }
    .spacer-md { height: 2rem; }
    .spacer-lg { height: 3rem; }

    /* Content sections */
    .content-section {
        margin-bottom: 2.5rem;
    }

    /* Breathing room between major elements */
    .stDataFrame, .stTable {
        margin: 1.5rem 0;
    }

    /* Chart spacing */
    .stPlotlyChart, .stAltairChart, .stVegaLiteChart {
        margin: 1.5rem 0;
        padding: 0.5rem;
    }

    /* Alert/info box spacing */
    .stAlert {
        margin: 1.25rem 0;
        padding: 1rem 1.25rem;
    }

    /* Spacing after forms */
    .stForm {
        margin-bottom: 2rem;
        padding: 1.5rem;
    }

    /* Download button spacing */
    .stDownloadButton {
        margin: 1rem 0;
    }

    /* Caption/small text spacing */
    .stCaption {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
"""


def apply_styles(st):
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
