"""
Special Component Styles
Timer, flashcards, chat bubbles, and other custom components.
"""

COMPONENTS_CSS = """
    /* =========================================
       TIMER DISPLAY
       ========================================= */

    .timer-display {
        font-family: var(--font-mono) !important;
        font-size: var(--text-5xl);
        font-weight: var(--font-extrabold);
        text-align: center;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: var(--tracking-wider);
        font-variant-numeric: tabular-nums;
        line-height: var(--leading-none);
    }

    .timer-label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        color: var(--text-tertiary);
        text-align: center;
        margin-top: var(--space-2);
    }

    .timer-container {
        text-align: center;
        padding: var(--space-8);
        position: relative;
    }

    /* Timer states */
    .timer-running .timer-display {
        animation: timerPulse 2s ease-in-out infinite;
    }

    .timer-paused .timer-display {
        opacity: 0.6;
    }

    .timer-finished .timer-display {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
        -webkit-background-clip: text;
        animation: celebrate 0.5s ease-out;
    }

    .timer-break .timer-display {
        background: linear-gradient(135deg, var(--color-warning) 0%, #e67e22 100%);
        -webkit-background-clip: text;
    }

    @keyframes timerPulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.01); }
    }

    @keyframes celebrate {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    /* Timer progress ring */
    .timer-progress {
        position: relative;
        width: 200px;
        height: 200px;
        margin: 0 auto;
    }

    .timer-progress-ring {
        transform: rotate(-90deg);
    }

    .timer-progress-ring circle {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dashoffset var(--transition-slow);
    }

    .timer-progress-ring .bg {
        stroke: var(--color-gray-200);
    }

    .timer-progress-ring .progress {
        stroke: var(--color-primary);
    }

    /* Timer warning state (last 5 minutes) */
    .timer-warning .timer-progress-ring .progress {
        stroke: var(--color-warning);
    }

    .timer-warning .timer-display {
        background: linear-gradient(135deg, var(--color-warning) 0%, #e67e22 100%);
        -webkit-background-clip: text;
    }

    /* Timer critical state (last 1 minute) */
    .timer-critical .timer-progress-ring .progress {
        stroke: var(--color-error);
        animation: criticalPulse 0.5s ease-in-out infinite;
    }

    .timer-critical .timer-display {
        background: linear-gradient(135deg, var(--color-error) 0%, #c0392b 100%);
        -webkit-background-clip: text;
        animation: criticalPulse 0.5s ease-in-out infinite;
    }

    @keyframes criticalPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* =========================================
       FLASHCARDS
       ========================================= */

    .flashcard {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: var(--space-10);
        border-radius: var(--radius-2xl);
        text-align: center;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: var(--shadow-xl);
        font-family: var(--font-sans) !important;
        font-size: var(--text-xl);
        line-height: var(--leading-relaxed);
        color: var(--color-dark-bg);
        transition: transform var(--transition-slow);
    }

    .flashcard:hover {
        transform: scale(1.02);
    }

    .flashcard-question {
        font-weight: var(--font-semibold);
        font-size: var(--text-xl);
    }

    .flashcard-answer {
        font-weight: var(--font-normal);
        font-size: var(--text-lg);
        color: var(--text-secondary);
    }

    .flashcard-hint {
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        font-style: italic;
        margin-top: var(--space-4);
    }

    /* Flashcard flip animation */
    .flashcard-container {
        perspective: 1000px;
        cursor: pointer;
    }

    .flashcard-inner {
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }

    .flashcard-container.flipped .flashcard-inner {
        transform: rotateY(180deg);
    }

    /* Flashcard difficulty states */
    .flashcard.difficulty-easy {
        border: 3px solid var(--color-success);
    }

    .flashcard.difficulty-medium {
        border: 3px solid var(--color-warning);
    }

    .flashcard.difficulty-hard {
        border: 3px solid var(--color-error);
    }

    /* Flashcard review states */
    .flashcard.correct {
        animation: correctPulse 0.5s ease-out;
        border: 3px solid var(--color-success);
    }

    .flashcard.incorrect {
        animation: shake 0.5s ease-out;
        border: 3px solid var(--color-error);
    }

    @keyframes correctPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); box-shadow: 0 0 30px rgba(17, 153, 142, 0.5); }
        100% { transform: scale(1); }
    }

    /* Flashcard hint reveal */
    .flashcard-hint {
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        font-style: italic;
        margin-top: var(--space-4);
        opacity: 0;
        transition: opacity var(--transition-normal);
    }

    .flashcard:hover .flashcard-hint {
        opacity: 1;
    }

    /* =========================================
       CHAT BUBBLES
       ========================================= */

    .user-message {
        font-family: var(--font-sans) !important;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        color: white;
        padding: var(--space-4) var(--space-5);
        border-radius: 18px 18px 4px 18px;
        margin: var(--space-3) 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
    }

    .assistant-message {
        font-family: var(--font-sans) !important;
        background: var(--surface-secondary);
        color: var(--text-primary);
        padding: var(--space-4) var(--space-5);
        border-radius: 18px 18px 18px 4px;
        margin: var(--space-3) 0;
        max-width: 80%;
        border-left: 3px solid var(--color-accent);
        box-shadow: var(--shadow-sm);
        font-size: var(--text-base);
        line-height: var(--leading-relaxed);
    }

    .user-message code,
    .assistant-message code {
        font-family: var(--font-mono) !important;
        font-size: 0.875em;
        background: rgba(0, 0, 0, 0.1);
        padding: 0.125rem 0.375rem;
        border-radius: var(--radius-sm);
    }

    .chat-timestamp {
        font-size: var(--text-xs);
        color: var(--text-tertiary);
        margin-top: var(--space-1);
    }

    /* =========================================
       MESSAGES & ALERTS
       ========================================= */

    .success-msg {
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
        color: white;
        padding: var(--space-4) var(--space-6);
        border-radius: var(--radius-lg);
        text-align: center;
        font-weight: var(--font-medium);
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.2);
    }

    .warning-msg {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: var(--space-4) var(--space-6);
        border-radius: var(--radius-lg);
        text-align: center;
        font-weight: var(--font-medium);
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.2);
    }

    .info-box {
        background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
        padding: var(--space-4) var(--space-6);
        border-radius: var(--radius-lg);
        margin: var(--space-4) 0;
        color: var(--color-dark-bg);
        font-weight: var(--font-medium);
    }

    /* Streamlit alerts */
    .stAlert {
        margin: var(--space-5) 0;
        padding: var(--space-4) var(--space-5);
        border-radius: var(--radius-lg);
    }

    /* =========================================
       QUIZ COMPONENTS
       ========================================= */

    .quiz-question {
        background: white;
        padding: var(--space-6);
        border-radius: var(--radius-lg);
        margin: var(--space-4) 0;
        border-left: 4px solid var(--color-primary);
        box-shadow: var(--shadow-sm);
    }

    .quiz-option {
        padding: var(--space-3) var(--space-4);
        margin: var(--space-2) 0;
        border: 2px solid var(--color-gray-200);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .quiz-option:hover {
        border-color: var(--color-primary);
        background: rgba(102, 126, 234, 0.05);
    }

    .quiz-option-selected {
        border-color: var(--color-primary);
        background: rgba(102, 126, 234, 0.1);
    }

    .quiz-option-correct {
        border-color: var(--color-success) !important;
        background: rgba(17, 153, 142, 0.1) !important;
    }

    .quiz-option-incorrect {
        border-color: var(--color-error) !important;
        background: rgba(231, 76, 60, 0.1) !important;
    }

    /* =========================================
       SCORE DISPLAY
       ========================================= */

    .score-display {
        text-align: center;
        padding: var(--space-8);
    }

    .score-number {
        font-family: var(--font-display) !important;
        font-size: var(--text-5xl);
        font-weight: var(--font-extrabold);
        background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .score-label {
        font-size: var(--text-lg);
        color: var(--text-tertiary);
        margin-top: var(--space-2);
    }
"""
