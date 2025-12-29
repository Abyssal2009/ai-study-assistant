"""
CSS Custom Properties - Design Tokens
Colors, fonts, spacing, and other reusable values.
"""

VARIABLES_CSS = """
    /* =========================================
       DESIGN TOKENS (CSS Custom Properties)
       ========================================= */

    :root {
        /* ===================
           COLOR PALETTE
           =================== */

        /* Primary colors */
        --color-primary: #667eea;
        --color-primary-dark: #764ba2;
        --color-primary-light: #818cf8;

        /* Accent colors */
        --color-accent: #e94560;
        --color-accent-dark: #c0392b;

        /* Success/Error/Warning */
        --color-success: #11998e;
        --color-success-light: #38ef7d;
        --color-error: #e74c3c;
        --color-warning: #f39c12;

        /* Neutrals */
        --color-gray-50: #f9fafb;
        --color-gray-100: #f3f4f6;
        --color-gray-200: #e5e7eb;
        --color-gray-300: #d1d5db;
        --color-gray-400: #9ca3af;
        --color-gray-500: #6b7280;
        --color-gray-600: #4b5563;
        --color-gray-700: #374151;
        --color-gray-800: #1f2937;
        --color-gray-900: #111827;

        /* Dark theme colors */
        --color-dark-bg: #1a1a2e;
        --color-dark-surface: #16213e;
        --color-dark-accent: #0f3460;

        /* ===================
           SEMANTIC TEXT COLORS
           =================== */

        /* These change based on light/dark mode */
        --text-primary: #111827;          /* Main text - near black */
        --text-secondary: #374151;        /* Secondary text - dark gray */
        --text-tertiary: #6b7280;         /* Muted text - medium gray */
        --text-inverse: #ffffff;          /* Text on dark backgrounds */

        /* Surface colors */
        --surface-primary: #ffffff;
        --surface-secondary: #f9fafb;
        --surface-tertiary: #f3f4f6;
        --border-color: #e5e7eb;

        /* ===================
           TYPOGRAPHY
           =================== */

        /* Font families */
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
        --text-5xl: 3rem;        /* 48px */

        /* Line heights */
        --leading-none: 1;
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

        /* Font weights */
        --font-normal: 400;
        --font-medium: 500;
        --font-semibold: 600;
        --font-bold: 700;
        --font-extrabold: 800;

        /* ===================
           SPACING
           =================== */

        --space-0: 0;
        --space-1: 0.25rem;     /* 4px */
        --space-2: 0.5rem;      /* 8px */
        --space-3: 0.75rem;     /* 12px */
        --space-4: 1rem;        /* 16px */
        --space-5: 1.25rem;     /* 20px */
        --space-6: 1.5rem;      /* 24px */
        --space-8: 2rem;        /* 32px */
        --space-10: 2.5rem;     /* 40px */
        --space-12: 3rem;       /* 48px */
        --space-16: 4rem;       /* 64px */

        /* ===================
           BORDERS & RADIUS
           =================== */

        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 20px;
        --radius-full: 9999px;

        --border-width: 1px;
        --border-width-2: 2px;

        /* ===================
           SHADOWS
           =================== */

        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 8px 24px rgba(0, 0, 0, 0.12);

        /* Colored shadows */
        --shadow-primary: 0 4px 20px rgba(102, 126, 234, 0.25);
        --shadow-success: 0 4px 20px rgba(17, 153, 142, 0.25);
        --shadow-error: 0 4px 20px rgba(231, 76, 60, 0.25);
        --shadow-accent: 0 4px 20px rgba(233, 69, 96, 0.25);

        /* ===================
           TRANSITIONS
           =================== */

        --transition-fast: 0.15s ease;
        --transition-normal: 0.2s ease;
        --transition-slow: 0.3s ease;

        /* ===================
           Z-INDEX
           =================== */

        --z-dropdown: 1000;
        --z-sticky: 1020;
        --z-fixed: 1030;
        --z-modal: 1040;
        --z-popover: 1050;
        --z-tooltip: 1060;
    }

    /* ===================
       GRADIENTS
       =================== */

    .gradient-primary {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    }

    .gradient-success {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
    }

    .gradient-accent {
        background: linear-gradient(135deg, var(--color-accent) 0%, #f5576c 100%);
    }

    .gradient-warm {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }

    .gradient-cool {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }

    .gradient-ocean {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    /* =========================================
       DARK MODE OVERRIDES
       ========================================= */

    /* Streamlit dark theme detection */
    [data-theme="dark"],
    .stApp[data-theme="dark"],
    [data-testid="stAppViewContainer"][data-theme="dark"] {
        --text-primary: #f9fafb;          /* Main text - near white */
        --text-secondary: #e5e7eb;        /* Secondary text - light gray */
        --text-tertiary: #9ca3af;         /* Muted text - medium gray */
        --text-inverse: #111827;          /* Text on light backgrounds */

        --surface-primary: #1a1a2e;
        --surface-secondary: #16213e;
        --surface-tertiary: #0f3460;
        --border-color: #374151;

        /* Adjusted grays for dark mode readability */
        --color-gray-50: #1f2937;
        --color-gray-100: #374151;
        --color-gray-200: #4b5563;
        --color-gray-300: #6b7280;
        --color-gray-400: #9ca3af;
        --color-gray-500: #d1d5db;
        --color-gray-600: #e5e7eb;
        --color-gray-700: #f3f4f6;
        --color-gray-800: #f9fafb;
        --color-gray-900: #ffffff;

        --color-dark-bg: #f9fafb;
        --color-dark-surface: #f3f4f6;
    }

    /* System preference dark mode */
    @media (prefers-color-scheme: dark) {
        :root:not([data-theme="light"]) {
            --text-primary: #f9fafb;
            --text-secondary: #e5e7eb;
            --text-tertiary: #9ca3af;
            --text-inverse: #111827;

            --surface-primary: #1a1a2e;
            --surface-secondary: #16213e;
            --surface-tertiary: #0f3460;
            --border-color: #374151;
        }
    }
"""
