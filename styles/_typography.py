"""
Typography Styles
Headings, body text, links, and text utilities.
"""

TYPOGRAPHY_CSS = """
    /* =========================================
       BASE TEXT RENDERING
       ========================================= */

    html, body, [class*="st-"] {
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }

    /* =========================================
       HEADING HIERARCHY
       ========================================= */

    /* Page titles - Large gradient text */
    h1 {
        font-family: var(--font-display) !important;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: var(--font-extrabold) !important;
        font-size: var(--text-4xl) !important;
        margin-top: var(--space-4) !important;
        margin-bottom: var(--space-6) !important;
        padding-bottom: var(--space-2) !important;
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-tight) !important;
    }

    /* Section headers */
    h2 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
        font-weight: var(--font-bold) !important;
        font-size: var(--text-2xl) !important;
        margin-top: var(--space-10) !important;
        margin-bottom: var(--space-6) !important;
        padding-bottom: var(--space-3);
        border-bottom: var(--border-width-2) solid var(--color-accent);
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-snug) !important;
    }

    /* Subsection headers */
    h3 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
        font-weight: var(--font-semibold) !important;
        font-size: var(--text-xl) !important;
        margin-top: var(--space-8) !important;
        margin-bottom: var(--space-4) !important;
        letter-spacing: var(--tracking-normal);
        line-height: var(--leading-snug) !important;
    }

    /* Small headers */
    h4 {
        font-family: var(--font-display) !important;
        color: var(--text-secondary) !important;
        font-weight: var(--font-semibold) !important;
        font-size: var(--text-lg) !important;
        margin-top: var(--space-6) !important;
        margin-bottom: var(--space-3) !important;
        letter-spacing: var(--tracking-normal);
        line-height: var(--leading-snug) !important;
    }

    /* =========================================
       BODY TEXT
       ========================================= */

    p {
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
        color: var(--text-secondary);
        margin-bottom: var(--space-4);
        max-width: 70ch; /* Optimal reading width */
    }

    /* List items */
    li {
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
        color: var(--text-secondary);
        margin-bottom: var(--space-2);
        padding-left: var(--space-1);
    }

    /* List containers */
    ul, ol {
        margin-top: var(--space-4);
        margin-bottom: var(--space-6);
        padding-left: var(--space-6);
    }

    /* =========================================
       TEXT VARIATIONS
       ========================================= */

    /* Strong/bold text */
    strong, b {
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    /* Emphasis/italic */
    em, i {
        font-style: italic;
        color: var(--text-secondary);
    }

    /* Small text */
    small, .small {
        font-size: var(--text-sm);
        line-height: var(--leading-normal);
        color: var(--text-tertiary);
    }

    /* Captions and helper text */
    .caption, figcaption {
        font-size: var(--text-sm);
        line-height: var(--leading-normal);
        color: var(--text-tertiary);
        margin-top: var(--space-2);
    }

    /* =========================================
       CODE & MONOSPACE
       ========================================= */

    code, pre, .mono {
        font-family: var(--font-mono) !important;
        font-size: 0.9em;
        background: var(--color-gray-100);
        border-radius: var(--radius-sm);
        padding: 0.125rem 0.375rem;
    }

    pre {
        padding: var(--space-4);
        overflow-x: auto;
        line-height: var(--leading-relaxed);
    }

    /* =========================================
       LINKS
       ========================================= */

    a {
        color: var(--color-primary);
        text-decoration: none;
        font-weight: var(--font-medium);
        transition: color var(--transition-normal);
    }

    a:hover {
        color: var(--color-primary-dark);
        text-decoration: underline;
    }

    /* =========================================
       TEXT UTILITY CLASSES
       ========================================= */

    /* Sizes */
    .text-xs { font-size: var(--text-xs) !important; }
    .text-sm { font-size: var(--text-sm) !important; }
    .text-base { font-size: var(--text-base) !important; }
    .text-lg { font-size: var(--text-lg) !important; }
    .text-xl { font-size: var(--text-xl) !important; }
    .text-2xl { font-size: var(--text-2xl) !important; }
    .text-3xl { font-size: var(--text-3xl) !important; }
    .text-4xl { font-size: var(--text-4xl) !important; }

    /* Weights */
    .font-normal { font-weight: var(--font-normal) !important; }
    .font-medium { font-weight: var(--font-medium) !important; }
    .font-semibold { font-weight: var(--font-semibold) !important; }
    .font-bold { font-weight: var(--font-bold) !important; }

    /* Colors */
    .text-primary { color: var(--color-primary) !important; }
    .text-accent { color: var(--color-accent) !important; }
    .text-success { color: var(--color-success) !important; }
    .text-error { color: var(--color-error) !important; }
    .text-warning { color: var(--color-warning) !important; }
    .text-muted { color: var(--text-tertiary) !important; }
    .text-body { color: var(--text-secondary) !important; }
    .text-heading { color: var(--text-primary) !important; }

    /* Transforms */
    .uppercase { text-transform: uppercase !important; }
    .lowercase { text-transform: lowercase !important; }
    .capitalize { text-transform: capitalize !important; }

    /* Line heights */
    .leading-tight { line-height: var(--leading-tight) !important; }
    .leading-normal { line-height: var(--leading-normal) !important; }
    .leading-relaxed { line-height: var(--leading-relaxed) !important; }
"""
