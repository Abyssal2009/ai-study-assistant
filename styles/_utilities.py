"""
Utility Styles
Helper classes, responsive adjustments, and misc utilities.
"""

UTILITIES_CSS = """
    /* =========================================
       TEXT TRUNCATION
       ========================================= */

    .truncate {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .line-clamp-1 {
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
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

    /* =========================================
       NUMBER FORMATTING
       ========================================= */

    .number,
    .data-value {
        font-family: var(--font-mono) !important;
        font-variant-numeric: tabular-nums;
        letter-spacing: var(--tracking-tight);
    }

    .stat-number {
        font-family: var(--font-display) !important;
        font-size: var(--text-4xl);
        font-weight: var(--font-extrabold);
        line-height: var(--leading-none);
        letter-spacing: var(--tracking-tighter);
    }

    /* =========================================
       VISIBILITY
       ========================================= */

    .hidden { display: none !important; }
    .invisible { visibility: hidden !important; }
    .visible { visibility: visible !important; }

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    /* =========================================
       OVERFLOW
       ========================================= */

    .overflow-auto { overflow: auto !important; }
    .overflow-hidden { overflow: hidden !important; }
    .overflow-scroll { overflow: scroll !important; }
    .overflow-x-auto { overflow-x: auto !important; }
    .overflow-y-auto { overflow-y: auto !important; }

    /* =========================================
       BORDERS
       ========================================= */

    .border { border: 1px solid var(--border-color) !important; }
    .border-2 { border: 2px solid var(--border-color) !important; }
    .border-none { border: none !important; }

    .border-t { border-top: 1px solid var(--border-color) !important; }
    .border-b { border-bottom: 1px solid var(--border-color) !important; }
    .border-l { border-left: 1px solid var(--border-color) !important; }
    .border-r { border-right: 1px solid var(--border-color) !important; }

    .border-primary { border-color: var(--color-primary) !important; }
    .border-accent { border-color: var(--color-accent) !important; }

    .rounded { border-radius: var(--radius-md) !important; }
    .rounded-lg { border-radius: var(--radius-lg) !important; }
    .rounded-xl { border-radius: var(--radius-xl) !important; }
    .rounded-full { border-radius: var(--radius-full) !important; }

    /* =========================================
       SHADOWS
       ========================================= */

    .shadow-none { box-shadow: none !important; }
    .shadow-sm { box-shadow: var(--shadow-sm) !important; }
    .shadow { box-shadow: var(--shadow-md) !important; }
    .shadow-lg { box-shadow: var(--shadow-lg) !important; }
    .shadow-xl { box-shadow: var(--shadow-xl) !important; }

    /* =========================================
       BACKGROUNDS
       ========================================= */

    .bg-white { background: var(--surface-primary) !important; }
    .bg-surface { background: var(--surface-primary) !important; }
    .bg-surface-secondary { background: var(--surface-secondary) !important; }
    .bg-surface-tertiary { background: var(--surface-tertiary) !important; }
    .bg-primary { background: var(--color-primary) !important; }
    .bg-accent { background: var(--color-accent) !important; }
    .bg-transparent { background: transparent !important; }

    /* =========================================
       CURSOR
       ========================================= */

    .cursor-pointer { cursor: pointer !important; }
    .cursor-default { cursor: default !important; }
    .cursor-not-allowed { cursor: not-allowed !important; }

    /* =========================================
       USER SELECT
       ========================================= */

    .select-none { user-select: none !important; }
    .select-text { user-select: text !important; }
    .select-all { user-select: all !important; }

    /* =========================================
       TRANSITIONS
       ========================================= */

    .transition { transition: all var(--transition-normal) !important; }
    .transition-fast { transition: all var(--transition-fast) !important; }
    .transition-slow { transition: all var(--transition-slow) !important; }
    .transition-none { transition: none !important; }

    /* =========================================
       TABLE STYLING
       ========================================= */

    .stDataFrame,
    .stTable {
        margin: var(--space-6) 0;
    }

    .stDataFrame table,
    .stTable table {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
    }

    .stDataFrame th,
    .stTable th {
        font-weight: var(--font-semibold) !important;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wide);
        font-size: var(--text-xs) !important;
    }

    /* =========================================
       CHART SPACING
       ========================================= */

    .stPlotlyChart,
    .stAltairChart,
    .stVegaLiteChart {
        margin: var(--space-6) 0;
        padding: var(--space-2);
    }

    /* =========================================
       CAPTION STYLING
       ========================================= */

    .stCaption {
        margin-top: var(--space-2);
        margin-bottom: var(--space-4);
    }

    /* =========================================
       RESPONSIVE ADJUSTMENTS
       ========================================= */

    @media (max-width: 768px) {
        /* Typography */
        h1 {
            font-size: var(--text-3xl) !important;
        }

        h2 {
            margin-top: var(--space-8) !important;
            font-size: var(--text-xl) !important;
        }

        /* Layout */
        .main {
            padding: var(--space-4) var(--space-6);
        }

        /* Timer */
        .timer-display {
            font-size: var(--text-4xl);
        }

        /* Cards */
        .stat-card,
        .stat-card-green,
        .stat-card-orange,
        .stat-card-blue {
            padding: var(--space-5) var(--space-4);
            margin: var(--space-3) 0;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            padding: var(--space-3) var(--space-4);
            font-size: var(--text-xs) !important;
        }

        /* Chat bubbles */
        .user-message,
        .assistant-message {
            max-width: 90%;
        }

        /* Flashcard */
        .flashcard {
            padding: var(--space-6);
            min-height: 180px;
            font-size: var(--text-lg);
        }
    }

    @media (max-width: 480px) {
        h1 {
            font-size: var(--text-2xl) !important;
        }

        .stat-card h1,
        .stat-card-green h1,
        .stat-card-orange h1,
        .stat-card-blue h1 {
            font-size: var(--text-3xl) !important;
        }

        .timer-display {
            font-size: var(--text-3xl);
        }
    }

    /* =========================================
       PRINT STYLES
       ========================================= */

    @media print {
        .no-print { display: none !important; }

        body {
            font-size: 12pt;
            line-height: 1.5;
        }

        h1, h2, h3 {
            page-break-after: avoid;
        }

        .stat-card,
        .homework-card,
        .exam-card {
            box-shadow: none;
            border: 1px solid #ccc;
        }
    }
"""
