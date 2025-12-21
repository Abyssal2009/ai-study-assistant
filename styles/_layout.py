"""
Layout & Spacing Styles
Containers, grids, spacing utilities, and alignment.
"""

LAYOUT_CSS = """
    /* =========================================
       MAIN CONTAINER
       ========================================= */

    .main {
        padding: var(--space-8) var(--space-12);
        max-width: 1400px;
    }

    .main .block-container {
        padding-top: var(--space-8);
        padding-bottom: var(--space-12);
    }

    /* =========================================
       ELEMENT SPACING
       ========================================= */

    .element-container {
        margin-bottom: var(--space-5);
    }

    /* Column gaps */
    [data-testid="column"] {
        padding: 0 var(--space-4);
    }

    [data-testid="column"] > div {
        display: flex;
        flex-direction: column;
    }

    /* Row spacing */
    .row-widget {
        margin-bottom: var(--space-6);
    }

    /* Markdown block spacing */
    .stMarkdown {
        margin-bottom: var(--space-4);
    }

    /* Metric spacing */
    [data-testid="stMetric"] {
        padding: var(--space-2);
        text-align: center;
    }

    /* =========================================
       SECTION CONTAINERS
       ========================================= */

    .section-container {
        background: white;
        border-radius: var(--radius-xl);
        padding: var(--space-8) var(--space-10);
        margin: var(--space-6) 0;
        box-shadow: var(--shadow-md);
    }

    /* =========================================
       DIVIDERS
       ========================================= */

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
        margin: var(--space-10) 0;
    }

    /* =========================================
       ALIGNMENT UTILITIES
       ========================================= */

    /* Text alignment */
    .text-left { text-align: left !important; }
    .text-center { text-align: center !important; }
    .text-right { text-align: right !important; }

    /* Vertical alignment */
    .align-top { vertical-align: top; }
    .align-middle { vertical-align: middle; }
    .align-bottom { vertical-align: bottom; }

    /* Flexbox utilities */
    .flex { display: flex !important; }
    .flex-col { flex-direction: column !important; }
    .flex-row { flex-direction: row !important; }
    .flex-wrap { flex-wrap: wrap !important; }

    .items-start { align-items: flex-start !important; }
    .items-center { align-items: center !important; }
    .items-end { align-items: flex-end !important; }

    .justify-start { justify-content: flex-start !important; }
    .justify-center { justify-content: center !important; }
    .justify-end { justify-content: flex-end !important; }
    .justify-between { justify-content: space-between !important; }

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

    /* Gap utilities */
    .gap-1 { gap: var(--space-1) !important; }
    .gap-2 { gap: var(--space-2) !important; }
    .gap-3 { gap: var(--space-3) !important; }
    .gap-4 { gap: var(--space-4) !important; }
    .gap-6 { gap: var(--space-6) !important; }
    .gap-8 { gap: var(--space-8) !important; }

    /* =========================================
       SPACING UTILITIES
       ========================================= */

    /* Margin */
    .m-0 { margin: 0 !important; }
    .m-1 { margin: var(--space-1) !important; }
    .m-2 { margin: var(--space-2) !important; }
    .m-4 { margin: var(--space-4) !important; }
    .m-6 { margin: var(--space-6) !important; }
    .m-8 { margin: var(--space-8) !important; }

    .mt-0 { margin-top: 0 !important; }
    .mt-2 { margin-top: var(--space-2) !important; }
    .mt-4 { margin-top: var(--space-4) !important; }
    .mt-6 { margin-top: var(--space-6) !important; }
    .mt-8 { margin-top: var(--space-8) !important; }

    .mb-0 { margin-bottom: 0 !important; }
    .mb-2 { margin-bottom: var(--space-2) !important; }
    .mb-4 { margin-bottom: var(--space-4) !important; }
    .mb-6 { margin-bottom: var(--space-6) !important; }
    .mb-8 { margin-bottom: var(--space-8) !important; }

    .mx-auto { margin-left: auto !important; margin-right: auto !important; }

    /* Padding */
    .p-0 { padding: 0 !important; }
    .p-2 { padding: var(--space-2) !important; }
    .p-4 { padding: var(--space-4) !important; }
    .p-6 { padding: var(--space-6) !important; }
    .p-8 { padding: var(--space-8) !important; }

    .py-2 { padding-top: var(--space-2) !important; padding-bottom: var(--space-2) !important; }
    .py-4 { padding-top: var(--space-4) !important; padding-bottom: var(--space-4) !important; }
    .px-4 { padding-left: var(--space-4) !important; padding-right: var(--space-4) !important; }
    .px-6 { padding-left: var(--space-6) !important; padding-right: var(--space-6) !important; }

    /* Spacer elements */
    .spacer-sm { height: var(--space-4); }
    .spacer-md { height: var(--space-8); }
    .spacer-lg { height: var(--space-12); }

    /* =========================================
       WIDTH & HEIGHT
       ========================================= */

    .w-full { width: 100% !important; }
    .w-auto { width: auto !important; }
    .h-full { height: 100% !important; }
    .h-auto { height: auto !important; }

    .max-w-sm { max-width: 24rem !important; }
    .max-w-md { max-width: 28rem !important; }
    .max-w-lg { max-width: 32rem !important; }
    .max-w-xl { max-width: 36rem !important; }
    .max-w-2xl { max-width: 42rem !important; }
    .max-w-prose { max-width: 70ch !important; }
"""
