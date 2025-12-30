"""
Badge & Tag Styles
Priority badges, subject tags, status indicators.
"""

BADGES_CSS = """
    /* =========================================
       PRIORITY BADGES
       ========================================= */

    .priority-high,
    .priority-medium,
    .priority-low {
        font-family: var(--font-sans) !important;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        display: inline-flex;
        align-items: center;
        line-height: var(--leading-none);
        color: white;
    }

    .priority-high {
        background: linear-gradient(135deg, var(--color-error) 0%, #c0392b 100%);
        box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
    }

    .priority-medium {
        background: linear-gradient(135deg, var(--color-warning) 0%, #d68910 100%);
        box-shadow: 0 2px 6px rgba(243, 156, 18, 0.3);
    }

    .priority-low {
        background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
        box-shadow: 0 2px 6px rgba(39, 174, 96, 0.3);
    }

    /* =========================================
       SUBJECT BADGES
       ========================================= */

    .subject-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        line-height: var(--leading-none);
    }

    /* =========================================
       DUE DATE BADGES
       ========================================= */

    .due-badge {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
    }

    .overdue {
        color: var(--color-error) !important;
        font-weight: var(--font-bold) !important;
    }

    .due-soon {
        color: var(--color-warning) !important;
        font-weight: var(--font-semibold) !important;
    }

    .due-later {
        color: var(--text-tertiary) !important;
        font-weight: var(--font-medium) !important;
    }

    .due-today {
        color: var(--color-accent) !important;
        font-weight: var(--font-bold) !important;
    }

    /* =========================================
       STATUS BADGES
       ========================================= */

    .status-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
    }

    .status-active {
        background: rgba(17, 153, 142, 0.15);
        color: var(--color-success);
    }

    .status-pending {
        background: rgba(243, 156, 18, 0.15);
        color: var(--color-warning);
    }

    .status-completed {
        background: rgba(102, 126, 234, 0.15);
        color: var(--color-primary);
    }

    /* =========================================
       STREAK DISPLAY
       ========================================= */

    .streak-display {
        font-family: var(--font-display) !important;
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: var(--space-2) var(--space-5);
        border-radius: var(--radius-full);
        font-weight: var(--font-bold);
        font-size: var(--text-base);
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        box-shadow: 0 4px 12px rgba(245, 175, 25, 0.3);
        letter-spacing: var(--tracking-tight);
    }

    /* =========================================
       COUNT BADGES
       ========================================= */

    .count-badge {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        background: var(--surface-tertiary);
        color: var(--text-secondary);
        padding: 2px var(--space-2);
        border-radius: var(--radius-md);
        font-variant-numeric: tabular-nums;
        min-width: 1.5rem;
        text-align: center;
    }

    .count-badge-primary {
        background: var(--color-primary);
        color: white;
    }

    .count-badge-accent {
        background: var(--color-accent);
        color: white;
    }

    /* =========================================
       NOTIFICATION DOT
       ========================================= */

    .notification-dot {
        width: 8px;
        height: 8px;
        border-radius: var(--radius-full);
        background: var(--color-accent);
        display: inline-block;
    }

    .notification-dot-success {
        background: var(--color-success);
    }

    /* =========================================
       TAG GROUPS
       ========================================= */

    .tag-group {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        margin: var(--space-2) 0;
    }

    .tag {
        font-family: var(--font-sans) !important;
        font-size: var(--text-xs);
        font-weight: var(--font-medium);
        background: var(--surface-tertiary);
        color: var(--text-secondary);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
    }

    .tag:hover {
        background: var(--surface-secondary);
    }

    .tag-clickable {
        cursor: pointer;
    }

    .tag-clickable:hover {
        background: var(--color-primary);
        color: white;
    }

    /* =========================================
       GRADE BADGES
       For displaying A-F grades consistently
       ========================================= */

    .grade-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-sm);
        font-weight: var(--font-bold);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        min-width: 2.5rem;
    }

    .grade-badge-a {
        background: var(--color-grade-a-bg);
        color: var(--color-grade-a);
        border: 1px solid var(--color-grade-a-border);
    }

    .grade-badge-b {
        background: var(--color-grade-b-bg);
        color: var(--color-grade-b);
        border: 1px solid var(--color-grade-b-border);
    }

    .grade-badge-c {
        background: var(--color-grade-c-bg);
        color: var(--color-grade-c);
        border: 1px solid var(--color-grade-c-border);
    }

    .grade-badge-d {
        background: var(--color-grade-d-bg);
        color: var(--color-grade-d);
        border: 1px solid var(--color-grade-d-border);
    }

    .grade-badge-f {
        background: var(--color-grade-f-bg);
        color: var(--color-grade-f);
        border: 1px solid var(--color-grade-f-border);
    }

    /* Large grade display */
    .grade-large {
        font-family: var(--font-display) !important;
        font-size: var(--text-4xl);
        font-weight: var(--font-extrabold);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
    }

    .grade-large-a {
        background: linear-gradient(135deg, var(--color-grade-a), #38ef7d);
        color: white;
    }

    .grade-large-b {
        background: linear-gradient(135deg, var(--color-grade-b), #818cf8);
        color: white;
    }

    .grade-large-c {
        background: linear-gradient(135deg, var(--color-grade-c), #f5c542);
        color: white;
    }

    .grade-large-d {
        background: linear-gradient(135deg, var(--color-grade-d), #f39c12);
        color: white;
    }

    .grade-large-f {
        background: linear-gradient(135deg, var(--color-grade-f), #c0392b);
        color: white;
    }

    /* =========================================
       SCORE BADGES
       For displaying numeric scores (e.g. 85%)
       ========================================= */

    .score-badge {
        font-family: var(--font-mono) !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
        font-weight: var(--font-bold);
    }

    .score-badge-excellent {
        background: var(--color-grade-a-bg);
        color: var(--color-grade-a);
    }

    .score-badge-good {
        background: var(--color-grade-b-bg);
        color: var(--color-grade-b);
    }

    .score-badge-average {
        background: var(--color-grade-c-bg);
        color: var(--color-grade-c);
    }

    .score-badge-below {
        background: var(--color-grade-d-bg);
        color: var(--color-grade-d);
    }

    .score-badge-poor {
        background: var(--color-grade-f-bg);
        color: var(--color-grade-f);
    }

    /* =========================================
       SESSION STATUS BADGES
       For practice sessions, study sessions, etc.
       ========================================= */

    .session-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
    }

    .session-badge-active {
        background: rgba(102, 126, 234, 0.15);
        color: var(--color-primary);
    }

    .session-badge-active::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--color-primary);
        border-radius: var(--radius-full);
        animation: pulse 2s ease-in-out infinite;
    }

    .session-badge-completed {
        background: rgba(17, 153, 142, 0.15);
        color: var(--color-success);
    }

    .session-badge-scheduled {
        background: rgba(243, 156, 18, 0.15);
        color: var(--color-warning);
    }

    .session-badge-missed {
        background: rgba(231, 76, 60, 0.15);
        color: var(--color-error);
    }

    /* =========================================
       DIFFICULTY BADGES
       ========================================= */

    .difficulty-badge {
        font-family: var(--font-sans) !important;
        display: inline-flex;
        align-items: center;
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
    }

    .difficulty-easy {
        background: var(--color-grade-a-bg);
        color: var(--color-grade-a);
    }

    .difficulty-medium {
        background: var(--color-grade-c-bg);
        color: var(--color-grade-c);
    }

    .difficulty-hard {
        background: var(--color-grade-f-bg);
        color: var(--color-grade-f);
    }
"""
