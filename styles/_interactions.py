"""
Interaction Styles
Hover effects, focus states, animations, and micro-interactions.
"""

INTERACTIONS_CSS = """
    /* =========================================
       ANIMATION KEYFRAMES
       ========================================= */

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
        50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.6); }
    }

    /* =========================================
       ANIMATION CLASSES
       ========================================= */

    .animate-fadeIn { animation: fadeIn var(--transition-normal) ease-out; }
    .animate-fadeInUp { animation: fadeInUp var(--transition-normal) ease-out; }
    .animate-fadeInDown { animation: fadeInDown var(--transition-normal) ease-out; }
    .animate-slideInLeft { animation: slideInLeft var(--transition-normal) ease-out; }
    .animate-slideInRight { animation: slideInRight var(--transition-normal) ease-out; }
    .animate-scaleIn { animation: scaleIn var(--transition-normal) ease-out; }

    .animate-pulse { animation: pulse 2s ease-in-out infinite; }
    .animate-bounce { animation: bounce 1s ease-in-out infinite; }
    .animate-shake { animation: shake 0.5s ease-in-out; }
    .animate-spin { animation: spin 1s linear infinite; }
    .animate-glow { animation: glow 2s ease-in-out infinite; }

    /* =========================================
       HOVER LIFT EFFECTS
       ========================================= */

    .hover-lift {
        transition: transform var(--transition-normal), box-shadow var(--transition-normal);
    }

    .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    .hover-lift-sm {
        transition: transform var(--transition-fast), box-shadow var(--transition-fast);
    }

    .hover-lift-sm:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    /* =========================================
       HOVER SCALE EFFECTS
       ========================================= */

    .hover-scale {
        transition: transform var(--transition-normal);
    }

    .hover-scale:hover {
        transform: scale(1.02);
    }

    .hover-scale-sm {
        transition: transform var(--transition-fast);
    }

    .hover-scale-sm:hover {
        transform: scale(1.01);
    }

    /* =========================================
       HOVER COLOR EFFECTS
       ========================================= */

    .hover-primary {
        transition: background-color var(--transition-normal), color var(--transition-normal);
    }

    .hover-primary:hover {
        background-color: var(--color-primary) !important;
        color: white !important;
    }

    .hover-accent {
        transition: background-color var(--transition-normal), color var(--transition-normal);
    }

    .hover-accent:hover {
        background-color: var(--color-accent) !important;
        color: white !important;
    }

    .hover-highlight {
        transition: background-color var(--transition-fast);
    }

    .hover-highlight:hover {
        background-color: rgba(102, 126, 234, 0.1);
    }

    /* =========================================
       FOCUS STATES (Accessibility)
       ========================================= */

    /* Focus ring for all interactive elements */
    :focus-visible {
        outline: 2px solid var(--color-primary);
        outline-offset: 2px;
    }

    /* Custom focus for buttons */
    .stButton > button:focus-visible {
        outline: 3px solid var(--color-primary-light);
        outline-offset: 2px;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }

    /* Focus for inputs */
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible {
        outline: none;
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }

    /* Skip to content focus */
    .skip-link:focus {
        position: fixed;
        top: var(--space-4);
        left: var(--space-4);
        z-index: 9999;
        padding: var(--space-3) var(--space-4);
        background: var(--color-primary);
        color: white;
        border-radius: var(--radius-md);
    }

    /* =========================================
       ACTIVE/PRESSED STATES
       ========================================= */

    .active-scale:active {
        transform: scale(0.98);
    }

    .active-darken:active {
        filter: brightness(0.9);
    }

    /* =========================================
       LOADING STATES
       ========================================= */

    .loading {
        position: relative;
        pointer-events: none;
    }

    .loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid var(--border-color);
        border-top-color: var(--color-primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    .loading-overlay {
        position: relative;
    }

    .loading-overlay::before {
        content: '';
        position: absolute;
        inset: 0;
        background: var(--surface-primary);
        opacity: 0.8;
        z-index: 10;
        border-radius: inherit;
    }

    .loading-overlay::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 30px;
        height: 30px;
        margin: -15px 0 0 -15px;
        border: 3px solid var(--border-color);
        border-top-color: var(--color-primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        z-index: 11;
    }

    /* Skeleton loading */
    .skeleton {
        background: linear-gradient(
            90deg,
            var(--surface-secondary) 25%,
            var(--surface-tertiary) 50%,
            var(--surface-secondary) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--radius-md);
    }

    .skeleton-text {
        height: 1em;
        margin-bottom: var(--space-2);
    }

    .skeleton-title {
        height: 1.5em;
        width: 60%;
        margin-bottom: var(--space-3);
    }

    .skeleton-card {
        height: 120px;
    }

    /* =========================================
       SUCCESS/ERROR/WARNING STATES
       ========================================= */

    .state-success {
        border-color: var(--color-success) !important;
        background-color: rgba(17, 153, 142, 0.05) !important;
    }

    .state-success::before {
        content: '✓';
        color: var(--color-success);
        margin-right: var(--space-2);
    }

    .state-error {
        border-color: var(--color-error) !important;
        background-color: rgba(231, 76, 60, 0.05) !important;
        animation: shake 0.5s ease-in-out;
    }

    .state-warning {
        border-color: var(--color-warning) !important;
        background-color: rgba(243, 156, 18, 0.05) !important;
    }

    /* Input validation states */
    input.valid,
    textarea.valid {
        border-color: var(--color-success) !important;
    }

    input.invalid,
    textarea.invalid {
        border-color: var(--color-error) !important;
    }

    /* =========================================
       CONTEXTUAL HIGHLIGHTING
       ========================================= */

    /* Highlight on scroll into view */
    .highlight-new {
        animation: highlightFade 2s ease-out;
    }

    @keyframes highlightFade {
        0% { background-color: rgba(102, 126, 234, 0.2); }
        100% { background-color: transparent; }
    }

    /* Urgent item highlight */
    .highlight-urgent {
        position: relative;
    }

    .highlight-urgent::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--color-error);
        border-radius: var(--radius-sm) 0 0 var(--radius-sm);
        animation: pulse 1.5s ease-in-out infinite;
    }

    /* Due soon highlight */
    .highlight-due-soon {
        border-left: 4px solid var(--color-warning) !important;
    }

    /* Overdue highlight */
    .highlight-overdue {
        border-left: 4px solid var(--color-error) !important;
        background: rgba(231, 76, 60, 0.03);
    }

    /* =========================================
       TOOLTIPS
       ========================================= */

    [data-tooltip] {
        position: relative;
        cursor: help;
    }

    [data-tooltip]::before,
    [data-tooltip]::after {
        position: absolute;
        visibility: hidden;
        opacity: 0;
        transition: all var(--transition-fast);
        z-index: var(--z-tooltip);
    }

    [data-tooltip]::before {
        content: attr(data-tooltip);
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        padding: var(--space-2) var(--space-3);
        background: var(--color-gray-800);
        color: white;
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        white-space: nowrap;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
    }

    [data-tooltip]::after {
        content: '';
        bottom: calc(100% + 2px);
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: var(--color-gray-800);
    }

    [data-tooltip]:hover::before,
    [data-tooltip]:hover::after {
        visibility: visible;
        opacity: 1;
    }

    /* Tooltip positions */
    [data-tooltip-pos="bottom"]::before {
        bottom: auto;
        top: calc(100% + 8px);
    }

    [data-tooltip-pos="bottom"]::after {
        bottom: auto;
        top: calc(100% + 2px);
        border-top-color: transparent;
        border-bottom-color: var(--color-gray-800);
    }

    /* =========================================
       RIPPLE EFFECT
       ========================================= */

    .ripple {
        position: relative;
        overflow: hidden;
    }

    .ripple::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10%);
        background-repeat: no-repeat;
        background-position: 50%;
        transform: scale(10, 10);
        opacity: 0;
        transition: transform 0.5s, opacity 0.5s;
    }

    .ripple:active::after {
        transform: scale(0, 0);
        opacity: 0.3;
        transition: 0s;
    }

    /* =========================================
       CONTEXT MENU STYLES
       ========================================= */

    .context-menu {
        position: fixed;
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        padding: var(--space-2);
        z-index: var(--z-popover);
        min-width: 180px;
        animation: scaleIn var(--transition-fast) ease-out;
    }

    .context-menu-item {
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: background-color var(--transition-fast);
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }

    .context-menu-item:hover {
        background: var(--surface-secondary);
    }

    .context-menu-item-danger {
        color: var(--color-error);
    }

    .context-menu-item-danger:hover {
        background: rgba(231, 76, 60, 0.1);
    }

    .context-menu-divider {
        height: 1px;
        background: var(--border-color);
        margin: var(--space-2) 0;
    }

    /* =========================================
       DRAG AND DROP
       ========================================= */

    .draggable {
        cursor: grab;
        transition: opacity var(--transition-fast);
    }

    .draggable:active {
        cursor: grabbing;
    }

    .dragging {
        opacity: 0.5;
        transform: scale(1.02);
    }

    .drop-zone {
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-8);
        text-align: center;
        transition: all var(--transition-normal);
        color: var(--text-secondary);
    }

    .drop-zone-active {
        border-color: var(--color-primary);
        background: rgba(102, 126, 234, 0.05);
    }

    .drop-zone-hover {
        border-color: var(--color-primary);
        background: rgba(102, 126, 234, 0.1);
        transform: scale(1.01);
    }

    /* =========================================
       SELECTION STATES
       ========================================= */

    .selectable {
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .selectable:hover {
        background: var(--surface-secondary);
    }

    .selected {
        background: rgba(102, 126, 234, 0.1) !important;
        border-color: var(--color-primary) !important;
    }

    .selected::before {
        content: '✓';
        position: absolute;
        top: var(--space-2);
        right: var(--space-2);
        width: 20px;
        height: 20px;
        background: var(--color-primary);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--text-xs);
    }

    /* Multi-select count badge */
    .selection-count {
        position: fixed;
        bottom: var(--space-6);
        right: var(--space-6);
        background: var(--color-primary);
        color: white;
        padding: var(--space-3) var(--space-5);
        border-radius: var(--radius-full);
        box-shadow: var(--shadow-lg);
        font-weight: var(--font-semibold);
        z-index: var(--z-fixed);
        animation: fadeInUp var(--transition-normal) ease-out;
    }
"""
