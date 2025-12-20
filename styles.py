"""
Study Assistant - CSS Styles
All custom styling for the Streamlit application.
"""

CUSTOM_CSS = """
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e94560 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Flush sidebar navigation buttons */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(233, 69, 96, 0.2) !important;
        padding-left: 1.2rem !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg, #e94560 0%, #0f3460 100%) !important;
        font-weight: bold !important;
        border-left: 3px solid #e94560 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] {
        padding: 0 !important;
    }

    /* Card-like containers */
    .stExpander {
        border-radius: 12px;
        border: 2px solid #e94560;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }

    /* Priority badges */
    .priority-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(231, 76, 60, 0.3);
    }
    .priority-medium {
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(243, 156, 18, 0.3);
    }
    .priority-low {
        background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(39, 174, 96, 0.3);
    }

    /* Overdue styling */
    .overdue {
        color: #e74c3c;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
    }

    /* Stats cards with colours */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }

    /* Timer display */
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        font-family: monospace;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Subject badge */
    .subject-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Homework item card */
    .homework-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Exam countdown card */
    .exam-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);
    }

    /* Flashcard styling */
    .flashcard {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        font-size: 1.2rem;
    }

    /* Success message */
    .success-msg {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    /* Warning message */
    .warning-msg {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    /* Page header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    /* Streak display */
    .streak-display {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }

    /* Chat message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #1a1a2e;
        padding: 1rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
        border: 1px solid #e94560;
    }
</style>
"""


def apply_styles(st):
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
