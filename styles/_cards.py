"""
Card Styles
Stat cards, item cards, and card-based layouts.
"""

CARDS_CSS = """
    /* =========================================
       STAT CARDS - BASE
       ========================================= */

    .stat-card,
    .stat-card-green,
    .stat-card-orange,
    .stat-card-blue {
        padding: var(--space-6) var(--space-6);
        border-radius: var(--radius-xl);
        text-align: center;
        color: white;
        transition: transform var(--transition-normal), box-shadow var(--transition-normal);
        margin: var(--space-2) 0;
    }

    .stat-card:hover,
    .stat-card-green:hover,
    .stat-card-orange:hover,
    .stat-card-blue:hover {
        transform: translateY(-3px);
    }

    /* Stat card variants */
    .stat-card {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        box-shadow: var(--shadow-primary);
    }

    .stat-card:hover {
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
    }

    .stat-card-green {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
        box-shadow: var(--shadow-success);
    }

    .stat-card-green:hover {
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.35);
    }

    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 20px rgba(245, 87, 108, 0.25);
    }

    .stat-card-orange:hover {
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.35);
    }

    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.25);
    }

    .stat-card-blue:hover {
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.35);
    }

    /* =========================================
       STAT CARD TYPOGRAPHY
       ========================================= */

    .stat-card h1,
    .stat-card-green h1,
    .stat-card-orange h1,
    .stat-card-blue h1 {
        font-family: var(--font-display) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        font-size: var(--text-4xl) !important;
        font-weight: var(--font-extrabold) !important;
        margin: 0 0 var(--space-1) 0 !important;
        letter-spacing: var(--tracking-tighter);
        line-height: var(--leading-none) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stat-card p,
    .stat-card-green p,
    .stat-card-orange p,
    .stat-card-blue p {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-medium);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        margin: 0 !important;
        opacity: 0.9;
    }

    /* =========================================
       ITEM CARDS
       ========================================= */

    /* Homework card */
    .homework-card {
        background: white;
        border-left: 4px solid var(--color-primary);
        padding: var(--space-5) var(--space-6);
        margin: var(--space-4) 0;
        border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-normal);
        position: relative;
    }

    .homework-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateX(4px);
    }

    /* Homework card contextual states */
    .homework-card.overdue {
        border-left-color: var(--color-error);
        background: linear-gradient(90deg, rgba(231, 76, 60, 0.05) 0%, white 20%);
    }

    .homework-card.due-today {
        border-left-color: var(--color-accent);
        background: linear-gradient(90deg, rgba(233, 69, 96, 0.05) 0%, white 20%);
    }

    .homework-card.due-soon {
        border-left-color: var(--color-warning);
        background: linear-gradient(90deg, rgba(243, 156, 18, 0.05) 0%, white 20%);
    }

    .homework-card.completed {
        opacity: 0.7;
        border-left-color: var(--color-success);
    }

    .homework-card.completed::after {
        content: '✓';
        position: absolute;
        top: var(--space-2);
        right: var(--space-3);
        color: var(--color-success);
        font-size: var(--text-lg);
    }

    /* Homework card title */
    .homework-card h4,
    .homework-card strong {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base) !important;
        font-weight: var(--font-semibold) !important;
        color: var(--text-primary) !important;
        margin-bottom: var(--space-2) !important;
    }

    /* Exam card */
    .exam-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: var(--space-6) var(--space-6);
        border-radius: var(--radius-xl);
        color: white;
        margin: var(--space-4) 0;
        box-shadow: 0 4px 20px rgba(250, 112, 154, 0.25);
        transition: transform var(--transition-normal);
        position: relative;
        overflow: hidden;
    }

    .exam-card:hover {
        transform: scale(1.02);
    }

    .exam-card h3,
    .exam-card strong {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Exam card contextual states */
    .exam-card.exam-soon {
        animation: pulse 2s ease-in-out infinite;
    }

    .exam-card.exam-imminent::before {
        content: '⚠️ SOON';
        position: absolute;
        top: var(--space-2);
        right: var(--space-3);
        background: rgba(255, 255, 255, 0.9);
        color: var(--color-error);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
    }

    .exam-card.exam-completed {
        opacity: 0.7;
        filter: grayscale(0.3);
    }

    /* Note card */
    .note-card {
        background: var(--surface-primary);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-normal);
        color: var(--text-secondary);
    }

    .note-card:hover {
        box-shadow: var(--shadow-md);
    }

    /* =========================================
       METRIC CARDS (Streamlit native)
       ========================================= */

    [data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-medium) !important;
        color: var(--text-tertiary) !important;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        margin-bottom: var(--space-1);
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: var(--text-3xl) !important;
        font-weight: var(--font-bold) !important;
        letter-spacing: var(--tracking-tight);
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    [data-testid="stMetricDelta"] {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: var(--font-semibold);
    }

    /* =========================================
       CARD GRID LAYOUTS
       ========================================= */

    .card-grid {
        display: grid;
        gap: var(--space-4);
    }

    .card-grid-2 {
        grid-template-columns: repeat(2, 1fr);
    }

    .card-grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }

    .card-grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }

    @media (max-width: 768px) {
        .card-grid-2,
        .card-grid-3,
        .card-grid-4 {
            grid-template-columns: 1fr;
        }
    }

    /* =========================================
       SCORE CARDS
       For displaying grades, scores, and evaluations
       ========================================= */

    .score-card {
        background: linear-gradient(135deg, var(--surface-secondary), var(--surface-tertiary));
        border: 2px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        text-align: center;
        transition: all var(--transition-normal);
        margin: var(--space-4) 0;
    }

    .score-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    /* Score card color variants */
    .score-card-excellent {
        border-color: var(--color-grade-a);
        background: linear-gradient(135deg, var(--color-grade-a-bg), rgba(17, 153, 142, 0.05));
    }

    .score-card-good {
        border-color: var(--color-grade-b);
        background: linear-gradient(135deg, var(--color-grade-b-bg), rgba(102, 126, 234, 0.05));
    }

    .score-card-average {
        border-color: var(--color-grade-c);
        background: linear-gradient(135deg, var(--color-grade-c-bg), rgba(243, 156, 18, 0.05));
    }

    .score-card-below {
        border-color: var(--color-grade-d);
        background: linear-gradient(135deg, var(--color-grade-d-bg), rgba(230, 126, 34, 0.05));
    }

    .score-card-poor {
        border-color: var(--color-grade-f);
        background: linear-gradient(135deg, var(--color-grade-f-bg), rgba(231, 76, 60, 0.05));
    }

    /* Score value inside cards */
    .score-value {
        font-family: var(--font-display) !important;
        font-size: var(--text-5xl) !important;
        font-weight: var(--font-extrabold) !important;
        line-height: var(--leading-none) !important;
        margin: 0 0 var(--space-2) 0 !important;
    }

    .score-value-excellent { color: var(--color-grade-a) !important; }
    .score-value-good { color: var(--color-grade-b) !important; }
    .score-value-average { color: var(--color-grade-c) !important; }
    .score-value-below { color: var(--color-grade-d) !important; }
    .score-value-poor { color: var(--color-grade-f) !important; }

    .score-label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
    }

    .score-summary {
        font-family: var(--font-sans) !important;
        font-size: var(--text-base);
        color: var(--text-secondary);
        margin-top: var(--space-3);
        line-height: var(--leading-relaxed);
    }

    /* =========================================
       CRITERIA CARDS
       For displaying evaluation criteria scores
       ========================================= */

    .criteria-card {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-2) 0;
    }

    .criteria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-2);
    }

    .criteria-name {
        font-family: var(--font-sans) !important;
        font-weight: var(--font-semibold);
        color: var(--text-primary);
        text-transform: capitalize;
    }

    .criteria-score {
        font-family: var(--font-mono) !important;
        font-weight: var(--font-bold);
        font-size: var(--text-sm);
    }

    .criteria-bar {
        height: 8px;
        background: var(--surface-tertiary);
        border-radius: var(--radius-full);
        overflow: hidden;
        margin: var(--space-2) 0;
    }

    .criteria-bar-fill {
        height: 100%;
        border-radius: var(--radius-full);
        transition: width var(--transition-slow);
    }

    .criteria-bar-fill-excellent { background: linear-gradient(90deg, var(--color-grade-a), #38ef7d); }
    .criteria-bar-fill-good { background: linear-gradient(90deg, var(--color-grade-b), #818cf8); }
    .criteria-bar-fill-average { background: linear-gradient(90deg, var(--color-grade-c), #f5c542); }
    .criteria-bar-fill-below { background: linear-gradient(90deg, var(--color-grade-d), #f39c12); }
    .criteria-bar-fill-poor { background: linear-gradient(90deg, var(--color-grade-f), #c0392b); }

    .criteria-comment {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        font-style: italic;
    }

    /* =========================================
       FEEDBACK CARDS
       For displaying strengths, improvements, etc.
       ========================================= */

    .feedback-card {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin: var(--space-3) 0;
    }

    .feedback-card-success {
        border-left: 4px solid var(--color-success);
        background: linear-gradient(90deg, var(--color-grade-a-bg) 0%, var(--surface-primary) 20%);
    }

    .feedback-card-warning {
        border-left: 4px solid var(--color-warning);
        background: linear-gradient(90deg, var(--color-grade-c-bg) 0%, var(--surface-primary) 20%);
    }

    .feedback-card-error {
        border-left: 4px solid var(--color-error);
        background: linear-gradient(90deg, var(--color-grade-f-bg) 0%, var(--surface-primary) 20%);
    }

    .feedback-card-info {
        border-left: 4px solid var(--color-primary);
        background: linear-gradient(90deg, var(--color-grade-b-bg) 0%, var(--surface-primary) 20%);
    }

    .feedback-title {
        font-family: var(--font-sans) !important;
        font-weight: var(--font-semibold);
        font-size: var(--text-base);
        color: var(--text-primary);
        margin-bottom: var(--space-2);
    }

    .feedback-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .feedback-list li {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        padding: var(--space-1) 0;
        padding-left: var(--space-4);
        position: relative;
    }

    .feedback-list li::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--color-primary);
        font-weight: bold;
    }

    /* =========================================
       SESSION CARDS
       For study sessions, practice sessions, etc.
       ========================================= */

    .session-card {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin: var(--space-3) 0;
        transition: all var(--transition-normal);
    }

    .session-card:hover {
        box-shadow: var(--shadow-md);
    }

    .session-card-active {
        border-color: var(--color-primary);
        background: linear-gradient(135deg, var(--color-grade-b-bg), var(--surface-primary));
    }

    .session-card-completed {
        border-color: var(--color-success);
        background: linear-gradient(135deg, var(--color-grade-a-bg), var(--surface-primary));
    }

    .session-card-missed {
        border-color: var(--color-error);
        background: linear-gradient(135deg, var(--color-grade-f-bg), var(--surface-primary));
        opacity: 0.8;
    }

    /* =========================================
       TECHNIQUE CARDS
       For exam techniques, study methods, etc.
       ========================================= */

    .technique-card {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin: var(--space-3) 0;
        transition: all var(--transition-normal);
    }

    .technique-card:hover {
        border-color: var(--color-primary);
        box-shadow: var(--shadow-md);
    }

    .technique-title {
        font-family: var(--font-sans) !important;
        font-weight: var(--font-semibold);
        font-size: var(--text-lg);
        color: var(--text-primary);
        margin-bottom: var(--space-2);
    }

    .technique-description {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        line-height: var(--leading-relaxed);
    }

    .technique-steps {
        margin-top: var(--space-4);
        padding-left: var(--space-4);
    }

    .technique-steps li {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        padding: var(--space-1) 0;
    }

    .technique-tips {
        margin-top: var(--space-3);
        padding: var(--space-3);
        background: var(--surface-secondary);
        border-radius: var(--radius-md);
    }

    .technique-tips li {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        padding: var(--space-1) 0;
        list-style: none;
        padding-left: var(--space-4);
        position: relative;
    }

    .technique-tips li::before {
        content: '💡';
        position: absolute;
        left: 0;
    }
"""
