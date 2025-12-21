"""
Study Assistant - CSS Styles
All custom styling for the Streamlit application.
"""

CUSTOM_CSS = """
<style>
    /* =========================================
       BASE TYPOGRAPHY & FONT SYSTEM
       ========================================= */

    /* System font stack for optimal rendering */
    :root {
        --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                     'Helvetica Neue', Arial, sans-serif, 'Apple Color Emoji',
                     'Segoe UI Emoji';
        --font-mono: 'SF Mono', 'Cascadia Code', 'Consolas', 'Monaco',
                     'Liberation Mono', 'Courier New', monospace;
        --font-display: 'Segoe UI', -apple-system, BlinkMacSystemFont,
                        Roboto, 'Helvetica Neue', Arial, sans-serif;

        /* Type scale (1.25 ratio) */
        --text-xs: 0.75rem;      /* 12px */
        --text-sm: 0.875rem;     /* 14px */
        --text-base: 1rem;       /* 16px */
        --text-lg: 1.125rem;     /* 18px */
        --text-xl: 1.25rem;      /* 20px */
        --text-2xl: 1.5rem;      /* 24px */
        --text-3xl: 1.875rem;    /* 30px */
        --text-4xl: 2.5rem;      /* 40px */

        /* Line heights */
        --leading-tight: 1.25;
        --leading-snug: 1.375;
        --leading-normal: 1.5;
        --leading-relaxed: 1.625;
        --leading-loose: 1.75;

        /* Letter spacing */
        --tracking-tighter: -0.05em;
        --tracking-tight: -0.025em;
        --tracking-normal: 0;
        --tracking-wide: 0.025em;
        --tracking-wider: 0.05em;
        --tracking-widest: 0.1em;
    }

    /* Base text rendering */
    html, body, [class*="st-"] {
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }

    /* =========================================
       TYPOGRAPHY HIERARCHY
       ========================================= */

    /* Page titles - Large gradient text */
    h1 {
        font-family: var(--font-display) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: var(--text-4xl) !important;
        margin-top: 1rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-tight) !important;
    }

    /* Section headers */
    h2 {
        font-family: var(--font-display) !important;
        color: #1a1a2e !important;
        font-weight: 700 !important;
        font-size: var(--text-2xl) !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e94560;
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-snug) !important;
    }

    /* Subsection headers */
    h3 {
        font-family: var(--font-display) !important;
        color: #16213e !important;
        font-weight: 600 !important;
        font-size: var(--text-xl) !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        letter-spacing: var(--tracking-normal);
        line-height: var(--leading-snug) !important;
    }

    /* Small headers */
    h4 {
        font-family: var(--font-display) !important;
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: var(--text-lg) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: var(--tracking-normal);
        line-height: var(--leading-snug) !important;
    }

    /* Body text improvements */
    p {
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
        color: #374151;
        margin-bottom: 1rem;
        max-width: 70ch; /* Optimal reading width */
    }

    /* List items */
    li {
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
        color: #374151;
        margin-bottom: 0.5rem;
        padding-left: 0.25rem;
    }

    /* List containers */
    ul, ol {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        padding-left: 1.75rem;
    }

    /* Strong/bold text */
    strong, b {
        font-weight: 600;
        color: #1a1a2e;
    }

    /* Emphasis/italic */
    em, i {
        font-style: italic;
        color: #4a5568;
    }

    /* Small text */
    small, .small {
        font-size: var(--text-sm);
        line-height: var(--leading-normal);
        color: #6b7280;
    }

    /* Captions and helper text */
    .caption, figcaption {
        font-size: var(--text-sm);
        line-height: var(--leading-normal);
        color: #6b7280;
        margin-top: 0.5rem;
    }

    /* Code and monospace */
    code, pre, .mono {
        font-family: var(--font-mono) !important;
        font-size: 0.9em;
        background: #f3f4f6;
        border-radius: 4px;
        padding: 0.125rem 0.375rem;
    }

    pre {
        padding: 1rem;
        overflow-x: auto;
        line-height: var(--leading-relaxed);
    }

    /* Links */
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }

    a:hover {
        color: #764ba2;
        text-decoration: underline;
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
       ALIGNMENT & TEXT UTILITIES
       ========================================= */

    /* Text alignment classes */
    .text-left { text-align: left !important; }
    .text-center { text-align: center !important; }
    .text-right { text-align: right !important; }

    /* Vertical alignment for inline elements */
    .align-top { vertical-align: top; }
    .align-middle { vertical-align: middle; }
    .align-bottom { vertical-align: bottom; }

    /* Flex alignment helpers */
    .flex-center {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .flex-between {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .flex-start {
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }

    /* Column content alignment */
    [data-testid="column"] > div {
        display: flex;
        flex-direction: column;
    }

    /* Center content in columns */
    [data-testid="column"].centered > div {
        align-items: center;
    }

    /* Metric label and value alignment */
    [data-testid="stMetric"] {
        text-align: center;
    }

    [data-testid="stMetricLabel"] {
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        margin-bottom: 0.25rem;
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: var(--text-3xl) !important;
        font-weight: 700 !important;
        letter-spacing: var(--tracking-tight);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    [data-testid="stMetricDelta"] {
        font-size: var(--text-sm) !important;
        font-weight: 600;
    }

    /* Text truncation */
    .truncate {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .line-clamp-3 {
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Number/data formatting */
    .number, .data-value {
        font-family: var(--font-mono) !important;
        font-variant-numeric: tabular-nums;
        letter-spacing: var(--tracking-tight);
    }

    /* Large numbers (for stats) */
    .stat-number {
        font-family: var(--font-display) !important;
        font-size: var(--text-4xl);
        font-weight: 800;
        line-height: 1;
        letter-spacing: var(--tracking-tighter);
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
        font-family: var(--font-display) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        font-size: var(--text-4xl) !important;
        font-weight: 800 !important;
        margin: 0 0 0.25rem 0 !important;
        letter-spacing: var(--tracking-tighter);
        line-height: 1 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Stat card label */
    .stat-card p, .stat-card-green p, .stat-card-orange p, .stat-card-blue p {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        margin: 0 !important;
        opacity: 0.9;
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
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: var(--text-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
        display: inline-flex;
        align-items: center;
        line-height: 1;
    }

    .priority-medium {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: var(--text-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        box-shadow: 0 2px 6px rgba(243, 156, 18, 0.3);
        display: inline-flex;
        align-items: center;
        line-height: 1;
    }

    .priority-low {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: var(--text-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        box-shadow: 0 2px 6px rgba(39, 174, 96, 0.3);
        display: inline-flex;
        align-items: center;
        line-height: 1;
    }

    .subject-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: var(--text-xs);
        font-weight: 700;
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        line-height: 1;
    }

    /* Due date badges */
    .due-badge {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }

    .overdue {
        color: #e74c3c;
        font-weight: 700;
    }

    .due-soon {
        color: #f39c12;
        font-weight: 600;
    }

    .due-later {
        color: #6b7280;
        font-weight: 500;
    }

    .streak-display {
        font-family: var(--font-display) !important;
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: var(--text-base);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 12px rgba(245, 175, 25, 0.3);
        letter-spacing: var(--tracking-tight);
    }

    /* Count badges */
    .count-badge {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs);
        font-weight: 700;
        background: #e9ecef;
        color: #374151;
        padding: 2px 8px;
        border-radius: 10px;
        font-variant-numeric: tabular-nums;
    }

    /* =========================================
       INTERACTIVE ELEMENTS
       ========================================= */

    /* Buttons */
    .stButton > button {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: var(--text-base);
        letter-spacing: var(--tracking-wide);
        text-transform: none;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
        margin: 0.25rem 0;
        text-align: center;
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

    /* Small buttons */
    .stButton > button[data-size="small"] {
        font-size: var(--text-sm);
        padding: 0.5rem 1rem;
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
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 600 !important;
        letter-spacing: var(--tracking-wide);
        background: transparent;
        border-radius: 10px;
        padding: 12px 24px;
        transition: all 0.2s;
        text-align: center;
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
        font-family: var(--font-mono) !important;
        font-size: 5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.05em;
        font-variant-numeric: tabular-nums;
        line-height: 1;
    }

    /* Timer label */
    .timer-label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        color: #6b7280;
        text-align: center;
        margin-top: 0.5rem;
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
        font-family: var(--font-sans) !important;
        font-size: var(--text-xl);
        line-height: var(--leading-relaxed);
        color: #1a1a2e;
        transition: transform 0.3s;
    }

    .flashcard:hover {
        transform: scale(1.02);
    }

    /* Flashcard question styling */
    .flashcard-question {
        font-weight: 600;
        font-size: var(--text-xl);
    }

    /* Flashcard answer styling */
    .flashcard-answer {
        font-weight: 400;
        font-size: var(--text-lg);
        color: #374151;
    }

    /* Chat bubbles */
    .user-message {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.75rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
    }

    .assistant-message {
        font-family: var(--font-sans) !important;
        background: #f8f9fa;
        color: #1a1a2e;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.75rem 0;
        max-width: 80%;
        border-left: 3px solid #e94560;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
    }

    /* Chat message code blocks */
    .user-message code, .assistant-message code {
        font-family: var(--font-mono) !important;
        font-size: 0.875em;
        background: rgba(0,0,0,0.1);
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
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

    /* Form labels - improved typography */
    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stNumberInput label, .stDateInput label, .stSlider label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 600 !important;
        color: #374151 !important;
        letter-spacing: var(--tracking-wide);
        margin-bottom: 0.5rem;
        display: block;
    }

    /* Required field indicator */
    .stTextInput label span[style*="color: red"],
    .stSelectbox label span[style*="color: red"] {
        color: #e94560 !important;
        font-weight: 700;
    }

    /* Text inputs */
    .stTextInput > div > div > input {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.85rem 1.25rem;
        transition: border-color 0.2s, box-shadow 0.2s;
        color: #1a1a2e;
    }

    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
        font-style: italic;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* Select boxes */
    .stSelectbox > div > div {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: 10px;
        padding: 0.25rem 0;
    }

    .stSelectbox [data-baseweb="select"] > div {
        font-size: var(--text-base) !important;
    }

    /* Text areas */
    .stTextArea > div > div > textarea {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 1rem 1.25rem;
        line-height: var(--leading-relaxed);
        color: #1a1a2e;
    }

    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af;
        font-style: italic;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    /* Number inputs */
    .stNumberInput > div > div > input {
        font-family: var(--font-mono) !important;
        font-size: var(--text-base) !important;
        font-variant-numeric: tabular-nums;
    }

    /* Sliders */
    .stSlider {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        padding: 0 0.5rem;
    }

    .stSlider [data-baseweb="slider"] div {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
    }

    /* Checkboxes and radio buttons */
    .stCheckbox, .stRadio {
        margin-bottom: 1rem;
    }

    .stCheckbox label, .stRadio label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        padding: 0.5rem 0;
        line-height: var(--leading-normal);
    }

    /* Help text under inputs */
    .stTextInput small, .stSelectbox small, .stTextArea small {
        font-size: var(--text-xs) !important;
        color: #6b7280;
        margin-top: 0.25rem;
        display: block;
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
