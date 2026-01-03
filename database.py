"""
Database module for the Study Assistant.
Handles all SQLite operations for subjects, homework, exams, focus sessions, and flashcards.
Includes the SM-2 spaced repetition algorithm for optimal flashcard scheduling.
"""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

# Database file location (same folder as this script)
DATABASE_PATH = Path(__file__).parent / "study.db"


def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def row_to_dict(row):
    """Convert a sqlite3.Row to a dictionary (needed for Streamlit compatibility)."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows):
    """Convert a list of sqlite3.Row objects to dictionaries."""
    return [dict(row) for row in rows]


def init_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Subjects table - your 11 GCSE subjects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            colour TEXT DEFAULT '#3498db',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Homework table - tracks assignments and deadlines
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE NOT NULL,
            priority TEXT DEFAULT 'medium',
            topic TEXT,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Migration: Add topic column to homework if it doesn't exist
    try:
        cursor.execute("ALTER TABLE homework ADD COLUMN topic TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Exams table - tracks exam dates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            exam_date DATE NOT NULL,
            duration_minutes INTEGER,
            location TEXT,
            notes TEXT,
            google_calendar_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Migration: Add google_calendar_id column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE exams ADD COLUMN google_calendar_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Focus sessions table - tracks study time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            started_at TIMESTAMP NOT NULL,
            ended_at TIMESTAMP,
            planned_minutes INTEGER DEFAULT 25,
            actual_minutes INTEGER,
            completed INTEGER DEFAULT 0,
            notes TEXT,
            topic TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Migration: Add topic column to focus_sessions if it doesn't exist
    try:
        cursor.execute("ALTER TABLE focus_sessions ADD COLUMN topic TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Flashcards table - stores questions and answers with SM-2 scheduling data
    # SM-2 Algorithm fields:
    #   - ease_factor: How easy the card is (starts at 2.5, min 1.3)
    #   - interval: Days until next review
    #   - repetitions: Number of times reviewed correctly in a row
    #   - next_review: Date when card should be reviewed next
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            topic TEXT,
            ease_factor REAL DEFAULT 2.5,
            interval INTEGER DEFAULT 0,
            repetitions INTEGER DEFAULT 0,
            next_review DATE NOT NULL,
            times_reviewed INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_reviewed_at TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Card reviews table - history of each review for statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flashcard_id INTEGER NOT NULL,
            quality INTEGER NOT NULL,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_taken_seconds INTEGER,
            ease_factor_before REAL,
            ease_factor_after REAL,
            interval_before INTEGER,
            interval_after INTEGER,
            FOREIGN KEY (flashcard_id) REFERENCES flashcards(id)
        )
    """)

    # Notes table - for storing revision notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favourite INTEGER DEFAULT 0,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Note images table - stores images from OCR alongside extracted text
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            width INTEGER,
            height INTEGER,
            extracted_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
    """)

    # Index for searching images by extracted text
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_images_text
        ON note_images(extracted_text)
    """)

    # Past papers table - for tracking practice papers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS past_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            paper_name TEXT NOT NULL,
            exam_board TEXT,
            year TEXT,
            paper_number TEXT,
            total_marks INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_taken_minutes INTEGER,
            notes TEXT,
            raw_content TEXT,
            ai_summary TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Migration: Add new columns to past_papers if they don't exist
    try:
        cursor.execute("ALTER TABLE past_papers ADD COLUMN raw_content TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE past_papers ADD COLUMN ai_summary TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Past paper questions - individual question scores with analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            question_number TEXT NOT NULL,
            question_text TEXT,
            topic TEXT,
            question_type TEXT,
            difficulty TEXT,
            max_marks INTEGER NOT NULL,
            marks_achieved INTEGER DEFAULT 0,
            notes TEXT,
            ai_analysis TEXT,
            FOREIGN KEY (paper_id) REFERENCES past_papers(id)
        )
    """)

    # Migration: Add new columns to paper_questions if they don't exist
    try:
        cursor.execute("ALTER TABLE paper_questions ADD COLUMN question_text TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE paper_questions ADD COLUMN question_type TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE paper_questions ADD COLUMN difficulty TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE paper_questions ADD COLUMN ai_analysis TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Paper analysis reports - cross-paper pattern analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_analysis_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            report_type TEXT NOT NULL,
            report_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Knowledge assessments - assessment sessions for gap analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            assessment_type TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            questions_answered INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            score_percentage REAL,
            time_taken_seconds INTEGER,
            status TEXT DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            ai_feedback TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Assessment questions - individual questions within an assessment
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            source_type TEXT,
            source_id INTEGER,
            marks INTEGER DEFAULT 1,
            FOREIGN KEY (assessment_id) REFERENCES knowledge_assessments(id)
        )
    """)

    # Assessment responses - student answers with evaluation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            student_answer TEXT,
            is_correct INTEGER,
            marks_awarded INTEGER DEFAULT 0,
            time_taken_seconds INTEGER,
            confidence_level INTEGER,
            ai_evaluation TEXT,
            responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES knowledge_assessments(id),
            FOREIGN KEY (question_id) REFERENCES assessment_questions(id)
        )
    """)

    # Topic mastery - tracks mastery levels per topic over time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_mastery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            mastery_level REAL DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            last_assessed_at TIMESTAMP,
            trend TEXT DEFAULT 'stable',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(subject_id, topic)
        )
    """)

    # Exam requirements - topics required by exams (from past papers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            frequency INTEGER DEFAULT 1,
            typical_marks INTEGER,
            importance_level TEXT DEFAULT 'medium',
            last_appeared_year TEXT,
            notes TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(subject_id, topic)
        )
    """)

    # Study schedules - main schedule storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            total_hours_planned INTEGER,
            generation_params TEXT
        )
    """)

    # Schedule sessions - individual study sessions within a schedule
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            topic TEXT,
            scheduled_date DATE NOT NULL,
            start_time TEXT,
            duration_minutes INTEGER NOT NULL DEFAULT 30,
            priority_score REAL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            completed_at TIMESTAMP,
            actual_duration_minutes INTEGER,
            notes TEXT,
            FOREIGN KEY (schedule_id) REFERENCES study_schedules(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Schedule adjustments - track automatic changes for transparency
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            session_id INTEGER,
            adjustment_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (schedule_id) REFERENCES study_schedules(id) ON DELETE CASCADE
        )
    """)

    # Study preferences - user preferences for scheduling
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_key TEXT NOT NULL UNIQUE,
            preference_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================================================
    # SRS ANALYTICS TABLES
    # ==========================================================================

    # Review activity - daily aggregated stats for analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date DATE NOT NULL UNIQUE,
            cards_reviewed INTEGER DEFAULT 0,
            cards_correct INTEGER DEFAULT 0,
            total_time_seconds INTEGER DEFAULT 0,
            streak_day INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Topic reviews - topic-level spaced repetition tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            ease_factor REAL DEFAULT 2.5,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review DATE NOT NULL,
            last_reviewed_at TIMESTAMP,
            times_reviewed INTEGER DEFAULT 0,
            avg_quiz_score REAL DEFAULT 0,
            importance_level TEXT DEFAULT 'medium',
            source TEXT DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(subject_id, topic)
        )
    """)

    # Index for efficient topic lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_reviews_next
        ON topic_reviews(next_review)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_reviews_subject
        ON topic_reviews(subject_id)
    """)

    # Notification settings - configurable notification preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT NOT NULL UNIQUE,
            setting_value TEXT,
            enabled INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Essay submissions - for Essay Writing Tutor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS essay_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            essay_title TEXT,
            essay_question TEXT,
            essay_text TEXT NOT NULL,
            word_count INTEGER,
            grade TEXT,
            overall_score INTEGER,
            feedback_json TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # ==========================================================================
    # EXAM TECHNIQUE TRAINER TABLES
    # ==========================================================================

    # Technique practice sessions - timed exam practice
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technique_practice_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            session_type TEXT NOT NULL,
            question_types TEXT,
            total_questions INTEGER NOT NULL,
            questions_answered INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_marks INTEGER DEFAULT 0,
            marks_achieved INTEGER DEFAULT 0,
            time_limit_seconds INTEGER,
            time_taken_seconds INTEGER,
            status TEXT DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            ai_review TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Technique practice responses - per-question responses with timing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technique_practice_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_type TEXT,
            question_text TEXT,
            student_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER,
            marks_awarded INTEGER DEFAULT 0,
            max_marks INTEGER DEFAULT 1,
            time_taken_seconds INTEGER,
            time_status TEXT,
            FOREIGN KEY (session_id) REFERENCES technique_practice_sessions(id)
        )
    """)

    # Exam techniques - static reference data for tips
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_techniques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question_type TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            tips TEXT NOT NULL
        )
    """)

    # ==========================================================================
    # STUDY SKILLS COACH TABLES
    # ==========================================================================

    # Study methods - note-taking and active learning methods
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            method_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            when_to_use TEXT,
            steps TEXT NOT NULL,
            tips TEXT,
            example_template TEXT,
            display_order INTEGER DEFAULT 0
        )
    """)

    # Note evaluations - history of AI note evaluations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            method_used TEXT,
            note_content TEXT NOT NULL,
            word_count INTEGER,
            overall_score INTEGER,
            feedback_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Index for efficient card_reviews date lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_card_reviews_date
        ON card_reviews(date(reviewed_at))
    """)

    # Chat messages - for Bubble Ace chat persistence
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Index for efficient chat message lookups by session
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session
        ON chat_messages(session_id, created_at DESC)
    """)

    # ==========================================================================
    # GOOGLE CALENDAR SYNC TABLE
    # ==========================================================================

    # Calendar sync - stores OAuth tokens and sync state
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_sync (
            id INTEGER PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            last_sync TIMESTAMP,
            is_connected INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# =============================================================================
# SUBJECT FUNCTIONS
# =============================================================================

def add_subject(name: str, colour: str = "#3498db") -> int:
    """Add a new subject. Returns the new subject's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (name, colour) VALUES (?, ?)",
        (name, colour)
    )
    conn.commit()
    subject_id = cursor.lastrowid
    conn.close()
    return subject_id


def get_all_subjects() -> list:
    """Get all subjects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY name")
    subjects = cursor.fetchall()
    conn.close()
    return rows_to_dicts(subjects)


def get_subject_by_id(subject_id: int):
    """Get a single subject by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    subject = cursor.fetchone()
    conn.close()
    return row_to_dict(subject)


def delete_subject(subject_id: int):
    """Delete a subject (also deletes related homework, exams, and flashcards)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete flashcard reviews first (foreign key constraint)
    cursor.execute("""
        DELETE FROM card_reviews WHERE flashcard_id IN
        (SELECT id FROM flashcards WHERE subject_id = ?)
    """, (subject_id,))
    cursor.execute("DELETE FROM flashcards WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM homework WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM exams WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM focus_sessions WHERE subject_id = ?", (subject_id,))
    cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()


# =============================================================================
# HOMEWORK FUNCTIONS
# =============================================================================

def add_homework(subject_id: int, title: str, due_date: date,
                 description: str = "", priority: str = "medium",
                 topic: str = None) -> int:
    """Add a new homework item. Returns the new homework's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO homework (subject_id, title, description, due_date, priority, topic)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (subject_id, title, description, due_date, priority, topic)
    )
    conn.commit()
    homework_id = cursor.lastrowid
    conn.close()
    return homework_id


def get_all_homework(include_completed: bool = False) -> list:
    """Get all homework, optionally including completed items."""
    conn = get_connection()
    cursor = conn.cursor()

    if include_completed:
        cursor.execute("""
            SELECT h.*, s.name as subject_name, s.colour as subject_colour
            FROM homework h
            JOIN subjects s ON h.subject_id = s.id
            ORDER BY h.due_date ASC, h.priority DESC
        """)
    else:
        cursor.execute("""
            SELECT h.*, s.name as subject_name, s.colour as subject_colour
            FROM homework h
            JOIN subjects s ON h.subject_id = s.id
            WHERE h.completed = 0
            ORDER BY h.due_date ASC, h.priority DESC
        """)

    homework = cursor.fetchall()
    conn.close()
    return rows_to_dicts(homework)


def get_homework_due_today() -> list:
    """Get homework due today."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.due_date = ? AND h.completed = 0
        ORDER BY h.priority DESC
    """, (today,))
    homework = cursor.fetchall()
    conn.close()
    return rows_to_dicts(homework)


def get_homework_due_this_week() -> list:
    """Get homework due within the next 7 days."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.due_date >= ?
          AND h.due_date <= date(?, '+7 days')
          AND h.completed = 0
        ORDER BY h.due_date ASC, h.priority DESC
    """, (today, today))
    homework = cursor.fetchall()
    conn.close()
    return rows_to_dicts(homework)


def get_overdue_homework() -> list:
    """Get homework that's past its due date and not completed."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.due_date < ? AND h.completed = 0
        ORDER BY h.due_date ASC
    """, (today,))
    homework = cursor.fetchall()
    conn.close()
    return rows_to_dicts(homework)


def mark_homework_complete(homework_id: int):
    """Mark a homework item as completed and update topic mastery if applicable."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get homework details to check for topic
    cursor.execute(
        "SELECT subject_id, topic FROM homework WHERE id = ?",
        (homework_id,)
    )
    homework = cursor.fetchone()

    # Mark as complete
    cursor.execute(
        "UPDATE homework SET completed = 1, completed_at = ? WHERE id = ?",
        (datetime.now(), homework_id)
    )
    conn.commit()
    conn.close()

    # Update topic mastery if homework has a topic
    if homework and homework['topic']:
        update_topic_mastery(
            subject_id=homework['subject_id'],
            topic=homework['topic'],
            is_correct=True  # Completing homework counts as successful practice
        )


def mark_homework_incomplete(homework_id: int):
    """Mark a homework item as not completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE homework SET completed = 0, completed_at = NULL WHERE id = ?",
        (homework_id,)
    )
    conn.commit()
    conn.close()


def delete_homework(homework_id: int):
    """Delete a homework item."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM homework WHERE id = ?", (homework_id,))
    conn.commit()
    conn.close()


# =============================================================================
# EXAM FUNCTIONS
# =============================================================================

def add_exam(subject_id: int, name: str, exam_date: date,
             duration_minutes: int = None, location: str = "", notes: str = "") -> int:
    """Add a new exam. Returns the new exam's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO exams (subject_id, name, exam_date, duration_minutes, location, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (subject_id, name, exam_date, duration_minutes, location, notes)
    )
    conn.commit()
    exam_id = cursor.lastrowid
    conn.close()
    return exam_id


def get_all_exams() -> list:
    """Get all upcoming exams."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.exam_date >= ?
        ORDER BY e.exam_date ASC
    """, (today,))
    exams = cursor.fetchall()
    conn.close()
    return rows_to_dicts(exams)


def get_exams_this_month() -> list:
    """Get exams within the next 30 days."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.exam_date >= ? AND e.exam_date <= date(?, '+30 days')
        ORDER BY e.exam_date ASC
    """, (today, today))
    exams = cursor.fetchall()
    conn.close()
    return rows_to_dicts(exams)


def delete_exam(exam_id: int) -> str:
    """Delete an exam. Returns the google_calendar_id if it existed."""
    conn = get_connection()
    cursor = conn.cursor()
    # Get calendar ID before deleting
    cursor.execute("SELECT google_calendar_id FROM exams WHERE id = ?", (exam_id,))
    row = cursor.fetchone()
    calendar_id = row['google_calendar_id'] if row else None
    cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()
    return calendar_id


def get_exam_by_id(exam_id: int) -> dict:
    """Get a single exam by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.id = ?
    """, (exam_id,))
    exam = cursor.fetchone()
    conn.close()
    return dict(exam) if exam else None


def update_exam_calendar_id(exam_id: int, calendar_id: str):
    """Update the Google Calendar ID for an exam."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE exams SET google_calendar_id = ? WHERE id = ?",
        (calendar_id, exam_id)
    )
    conn.commit()
    conn.close()


def get_exams_without_calendar_id() -> list:
    """Get exams that haven't been synced to Google Calendar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.google_calendar_id IS NULL
        ORDER BY e.exam_date ASC
    """)
    exams = cursor.fetchall()
    conn.close()
    return rows_to_dicts(exams)


# =============================================================================
# GOOGLE CALENDAR SYNC FUNCTIONS
# =============================================================================

def get_calendar_tokens() -> dict:
    """Get stored Google Calendar OAuth tokens."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar_sync WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row)


def save_calendar_tokens(access_token: str, refresh_token: str, expiry: datetime):
    """Save or update Google Calendar OAuth tokens."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO calendar_sync (id, access_token, refresh_token, token_expiry, is_connected)
        VALUES (1, ?, ?, ?, 1)
    """, (access_token, refresh_token, expiry))
    conn.commit()
    conn.close()


def update_calendar_last_sync():
    """Update the last sync timestamp."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE calendar_sync SET last_sync = ? WHERE id = 1
    """, (datetime.now(),))
    conn.commit()
    conn.close()


def clear_calendar_tokens():
    """Clear calendar tokens (disconnect)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE calendar_sync SET access_token = NULL, refresh_token = NULL,
        token_expiry = NULL, is_connected = 0 WHERE id = 1
    """)
    conn.commit()
    conn.close()


def is_calendar_connected() -> bool:
    """Check if Google Calendar is connected."""
    tokens = get_calendar_tokens()
    return tokens is not None and tokens.get('is_connected') == 1


def clear_exam_calendar_id(exam_id: int):
    """Clear the calendar ID for an exam (after deletion from calendar)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE exams SET google_calendar_id = NULL WHERE id = ?",
        (exam_id,)
    )
    conn.commit()
    conn.close()


def get_exam_with_calendar_id(exam_id: int) -> dict:
    """Get exam details including calendar ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.id = ?
    """, (exam_id,))
    exam = cursor.fetchone()
    conn.close()
    return row_to_dict(exam)


# =============================================================================
# FOCUS SESSION FUNCTIONS
# =============================================================================

def start_focus_session(subject_id: int = None, planned_minutes: int = 25) -> int:
    """Start a new focus session. Returns the session ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO focus_sessions (subject_id, started_at, planned_minutes)
           VALUES (?, ?, ?)""",
        (subject_id, datetime.now(), planned_minutes)
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def end_focus_session(session_id: int, completed: bool = True, notes: str = ""):
    """End a focus session."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get the start time to calculate actual minutes
    cursor.execute("SELECT started_at FROM focus_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    if row:
        started_at = datetime.fromisoformat(row['started_at'])
        ended_at = datetime.now()
        actual_minutes = int((ended_at - started_at).total_seconds() / 60)

        cursor.execute(
            """UPDATE focus_sessions
               SET ended_at = ?, actual_minutes = ?, completed = ?, notes = ?
               WHERE id = ?""",
            (ended_at, actual_minutes, 1 if completed else 0, notes, session_id)
        )
        conn.commit()
    conn.close()


def get_focus_sessions_today() -> list:
    """Get all focus sessions from today."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT fs.*, s.name as subject_name, s.colour as subject_colour
        FROM focus_sessions fs
        LEFT JOIN subjects s ON fs.subject_id = s.id
        WHERE date(fs.started_at) = ?
        ORDER BY fs.started_at DESC
    """, (today,))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def get_total_focus_minutes_today() -> int:
    """Get total focus minutes for today."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT COALESCE(SUM(actual_minutes), 0) as total
        FROM focus_sessions
        WHERE date(started_at) = ? AND completed = 1
    """, (today,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result else 0


def get_total_focus_minutes_this_week() -> int:
    """Get total focus minutes for the past 7 days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(actual_minutes), 0) as total
        FROM focus_sessions
        WHERE started_at >= date('now', '-7 days') AND completed = 1
    """)
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result else 0


def get_study_streak() -> int:
    """Calculate the current study streak (consecutive days with completed sessions)."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get distinct dates with completed sessions, ordered by date descending
    cursor.execute("""
        SELECT DISTINCT date(started_at) as study_date
        FROM focus_sessions
        WHERE completed = 1
        ORDER BY study_date DESC
    """)

    dates = [row['study_date'] for row in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    streak = 0
    current_date = date.today()

    for study_date in dates:
        if study_date == current_date.isoformat():
            streak += 1
            current_date = date.fromisoformat(study_date)
            # Move to previous day (simplified logic)
        elif streak == 0:
            # If first date isn't today, check if it's yesterday
            break
        else:
            break

    return streak


# =============================================================================
# STATISTICS FUNCTIONS
# =============================================================================

def get_homework_stats() -> dict:
    """Get homework statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total pending
    cursor.execute("SELECT COUNT(*) as count FROM homework WHERE completed = 0")
    pending = cursor.fetchone()['count']

    # Completed this week
    cursor.execute("""
        SELECT COUNT(*) as count FROM homework
        WHERE completed = 1 AND completed_at >= date('now', '-7 days')
    """)
    completed_week = cursor.fetchone()['count']

    # Overdue
    today = date.today().isoformat()
    cursor.execute("""
        SELECT COUNT(*) as count FROM homework
        WHERE completed = 0 AND due_date < ?
    """, (today,))
    overdue = cursor.fetchone()['count']

    # Total completed
    cursor.execute("SELECT COUNT(*) as count FROM homework WHERE completed = 1")
    completed_total = cursor.fetchone()['count']

    conn.close()

    return {
        'pending': pending,
        'completed_this_week': completed_week,
        'completed_total': completed_total,
        'overdue': overdue
    }


# =============================================================================
# FLASHCARD FUNCTIONS (with SM-2 Spaced Repetition Algorithm)
# =============================================================================

def sm2_algorithm(quality: int, repetitions: int, ease_factor: float, interval: int) -> tuple:
    """
    Implementation of the SuperMemo 2 (SM-2) algorithm.

    The SM-2 algorithm calculates when you should next review a flashcard based on
    how well you remembered it.

    Parameters:
        quality: How well you remembered (0-5 scale)
            0 - Complete blackout, no memory at all
            1 - Incorrect, but remembered upon seeing answer
            2 - Incorrect, but answer seemed easy to recall
            3 - Correct, but required significant effort
            4 - Correct, with some hesitation
            5 - Perfect response, instant recall
        repetitions: Number of times reviewed correctly in a row
        ease_factor: How easy this card is (starts at 2.5, minimum 1.3)
        interval: Current interval in days

    Returns:
        tuple: (new_repetitions, new_ease_factor, new_interval)
    """
    # If quality < 3, the response was incorrect - reset the card
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        # Correct response - increase interval
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetitions += 1

    # Update ease factor based on quality
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Ease factor must not go below 1.3
    if ease_factor < 1.3:
        ease_factor = 1.3

    return (repetitions, ease_factor, interval)


def add_flashcard(subject_id: int, question: str, answer: str, topic: str = "") -> int:
    """
    Add a new flashcard. Returns the new flashcard's ID.
    New cards are scheduled for immediate review (today).
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute(
        """INSERT INTO flashcards
           (subject_id, question, answer, topic, next_review)
           VALUES (?, ?, ?, ?, ?)""",
        (subject_id, question, answer, topic, today)
    )
    conn.commit()
    flashcard_id = cursor.lastrowid
    conn.close()
    return flashcard_id


def get_flashcard_by_id(flashcard_id: int):
    """Get a single flashcard by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, s.name as subject_name, s.colour as subject_colour
        FROM flashcards f
        JOIN subjects s ON f.subject_id = s.id
        WHERE f.id = ?
    """, (flashcard_id,))
    card = cursor.fetchone()
    conn.close()
    return row_to_dict(card)


def get_all_flashcards(subject_id: int = None) -> list:
    """Get all flashcards, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT f.*, s.name as subject_name, s.colour as subject_colour
            FROM flashcards f
            JOIN subjects s ON f.subject_id = s.id
            WHERE f.subject_id = ?
            ORDER BY f.next_review ASC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT f.*, s.name as subject_name, s.colour as subject_colour
            FROM flashcards f
            JOIN subjects s ON f.subject_id = s.id
            ORDER BY f.next_review ASC
        """)

    cards = cursor.fetchall()
    conn.close()
    return rows_to_dicts(cards)


def get_due_flashcards(subject_id: int = None) -> list:
    """Get all flashcards that are due for review today or earlier."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    if subject_id:
        cursor.execute("""
            SELECT f.*, s.name as subject_name, s.colour as subject_colour
            FROM flashcards f
            JOIN subjects s ON f.subject_id = s.id
            WHERE f.next_review <= ? AND f.subject_id = ?
            ORDER BY f.next_review ASC, f.ease_factor ASC
        """, (today, subject_id))
    else:
        cursor.execute("""
            SELECT f.*, s.name as subject_name, s.colour as subject_colour
            FROM flashcards f
            JOIN subjects s ON f.subject_id = s.id
            WHERE f.next_review <= ?
            ORDER BY f.next_review ASC, f.ease_factor ASC
        """, (today,))

    cards = cursor.fetchall()
    conn.close()
    return rows_to_dicts(cards)


def get_due_flashcards_count(subject_id: int = None) -> int:
    """Get count of flashcards due for review."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    if subject_id:
        cursor.execute(
            "SELECT COUNT(*) as count FROM flashcards WHERE next_review <= ? AND subject_id = ?",
            (today, subject_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) as count FROM flashcards WHERE next_review <= ?",
            (today,)
        )

    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_due_flashcards_by_subject() -> list:
    """Get count of due flashcards grouped by subject."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("""
        SELECT s.id, s.name, s.colour, COUNT(f.id) as due_count
        FROM subjects s
        LEFT JOIN flashcards f ON s.id = f.subject_id AND f.next_review <= ?
        GROUP BY s.id
        HAVING due_count > 0
        ORDER BY due_count DESC
    """, (today,))

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def review_flashcard(flashcard_id: int, quality: int, time_taken_seconds: int = None):
    """
    Review a flashcard and update its schedule using SM-2 algorithm.

    Parameters:
        flashcard_id: ID of the flashcard being reviewed
        quality: How well you remembered (0-5)
            0 - Complete blackout
            1 - Incorrect, remembered after seeing answer
            2 - Incorrect, answer seemed familiar
            3 - Correct with significant effort
            4 - Correct with some hesitation
            5 - Perfect, instant recall
        time_taken_seconds: Optional, how long it took to answer
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get current card data
    cursor.execute(
        "SELECT ease_factor, interval, repetitions FROM flashcards WHERE id = ?",
        (flashcard_id,)
    )
    card = cursor.fetchone()

    if not card:
        conn.close()
        return

    old_ease = card['ease_factor']
    old_interval = card['interval']

    # Apply SM-2 algorithm
    new_reps, new_ease, new_interval = sm2_algorithm(
        quality=quality,
        repetitions=card['repetitions'],
        ease_factor=card['ease_factor'],
        interval=card['interval']
    )

    # Calculate next review date
    next_review = (date.today() + timedelta(days=new_interval)).isoformat()

    # Update flashcard
    cursor.execute("""
        UPDATE flashcards
        SET ease_factor = ?,
            interval = ?,
            repetitions = ?,
            next_review = ?,
            times_reviewed = times_reviewed + 1,
            times_correct = times_correct + ?,
            last_reviewed_at = ?
        WHERE id = ?
    """, (
        new_ease,
        new_interval,
        new_reps,
        next_review,
        1 if quality >= 3 else 0,
        datetime.now(),
        flashcard_id
    ))

    # Log the review
    cursor.execute("""
        INSERT INTO card_reviews
        (flashcard_id, quality, time_taken_seconds, ease_factor_before,
         ease_factor_after, interval_before, interval_after)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        flashcard_id,
        quality,
        time_taken_seconds,
        old_ease,
        new_ease,
        old_interval,
        new_interval
    ))

    conn.commit()
    conn.close()


def delete_flashcard(flashcard_id: int):
    """Delete a flashcard and its review history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM card_reviews WHERE flashcard_id = ?", (flashcard_id,))
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
    conn.commit()
    conn.close()


def update_flashcard(flashcard_id: int, question: str, answer: str, topic: str = ""):
    """Update a flashcard's question and answer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE flashcards SET question = ?, answer = ?, topic = ? WHERE id = ?",
        (question, answer, topic, flashcard_id)
    )
    conn.commit()
    conn.close()


def reset_flashcard(flashcard_id: int):
    """Reset a flashcard's learning progress (start from scratch)."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        UPDATE flashcards
        SET ease_factor = 2.5,
            interval = 0,
            repetitions = 0,
            next_review = ?
        WHERE id = ?
    """, (today, flashcard_id))
    conn.commit()
    conn.close()


def get_flashcard_stats() -> dict:
    """Get overall flashcard statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    # Total cards
    cursor.execute("SELECT COUNT(*) as count FROM flashcards")
    total = cursor.fetchone()['count']

    # Due today
    cursor.execute("SELECT COUNT(*) as count FROM flashcards WHERE next_review <= ?", (today,))
    due_today = cursor.fetchone()['count']

    # Cards by learning stage
    # New (never reviewed)
    cursor.execute("SELECT COUNT(*) as count FROM flashcards WHERE times_reviewed = 0")
    new_cards = cursor.fetchone()['count']

    # Learning (reviewed but interval < 21 days)
    cursor.execute("SELECT COUNT(*) as count FROM flashcards WHERE times_reviewed > 0 AND interval < 21")
    learning = cursor.fetchone()['count']

    # Mature (interval >= 21 days)
    cursor.execute("SELECT COUNT(*) as count FROM flashcards WHERE interval >= 21")
    mature = cursor.fetchone()['count']

    # Reviews today
    cursor.execute("""
        SELECT COUNT(*) as count FROM card_reviews
        WHERE date(reviewed_at) = ?
    """, (today,))
    reviewed_today = cursor.fetchone()['count']

    # Average accuracy (last 7 days)
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct
        FROM card_reviews
        WHERE reviewed_at >= date('now', '-7 days')
    """)
    accuracy_row = cursor.fetchone()
    if accuracy_row and accuracy_row['total'] > 0:
        accuracy = round((accuracy_row['correct'] / accuracy_row['total']) * 100)
    else:
        accuracy = 0

    conn.close()

    return {
        'total': total,
        'due_today': due_today,
        'new': new_cards,
        'learning': learning,
        'mature': mature,
        'reviewed_today': reviewed_today,
        'accuracy_7_days': accuracy
    }


def get_flashcard_stats_by_subject(subject_id: int) -> dict:
    """Get flashcard statistics for a specific subject."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute(
        "SELECT COUNT(*) as count FROM flashcards WHERE subject_id = ?",
        (subject_id,)
    )
    total = cursor.fetchone()['count']

    cursor.execute(
        "SELECT COUNT(*) as count FROM flashcards WHERE subject_id = ? AND next_review <= ?",
        (subject_id, today)
    )
    due = cursor.fetchone()['count']

    cursor.execute("""
        SELECT AVG(
            CASE WHEN times_reviewed > 0
            THEN (times_correct * 100.0 / times_reviewed)
            ELSE 0 END
        ) as avg_accuracy
        FROM flashcards WHERE subject_id = ?
    """, (subject_id,))
    accuracy_row = cursor.fetchone()
    accuracy = round(accuracy_row['avg_accuracy']) if accuracy_row['avg_accuracy'] else 0

    conn.close()

    return {
        'total': total,
        'due': due,
        'accuracy': accuracy
    }


def get_review_history(days: int = 7) -> list:
    """Get review history for the past N days."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            date(reviewed_at) as review_date,
            COUNT(*) as total_reviews,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct,
            AVG(quality) as avg_quality
        FROM card_reviews
        WHERE reviewed_at >= date('now', ? || ' days')
        GROUP BY date(reviewed_at)
        ORDER BY review_date DESC
    """, (f'-{days}',))

    history = cursor.fetchall()
    conn.close()
    return rows_to_dicts(history)


# =============================================================================
# SRS ANALYTICS FUNCTIONS
# =============================================================================

def get_retention_rate_over_time(days: int = 30) -> list:
    """Calculate retention rate (% correct) for each day over the past N days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            date(reviewed_at) as review_date,
            COUNT(*) as total_reviews,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct_reviews,
            ROUND(100.0 * SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as retention_rate
        FROM card_reviews
        WHERE reviewed_at >= date('now', ? || ' days')
        GROUP BY date(reviewed_at)
        ORDER BY review_date ASC
    """, (f'-{days}',))
    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_forgetting_curve_data() -> list:
    """Get success rate by interval bucket for forgetting curve visualization."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            CASE
                WHEN interval_before <= 1 THEN '1 day'
                WHEN interval_before <= 3 THEN '2-3 days'
                WHEN interval_before <= 7 THEN '4-7 days'
                WHEN interval_before <= 14 THEN '8-14 days'
                WHEN interval_before <= 30 THEN '15-30 days'
                ELSE '30+ days'
            END as interval_bucket,
            CASE
                WHEN interval_before <= 1 THEN 1
                WHEN interval_before <= 3 THEN 2
                WHEN interval_before <= 7 THEN 3
                WHEN interval_before <= 14 THEN 4
                WHEN interval_before <= 30 THEN 5
                ELSE 6
            END as bucket_order,
            COUNT(*) as total,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct,
            ROUND(100.0 * SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
        FROM card_reviews
        WHERE interval_before IS NOT NULL
        GROUP BY interval_bucket
        ORDER BY bucket_order
    """)
    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_review_forecast(days: int = 30) -> list:
    """Predict how many cards will be due each day for the next N days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            next_review as due_date,
            COUNT(*) as cards_due
        FROM flashcards
        WHERE next_review BETWEEN date('now') AND date('now', ? || ' days')
        GROUP BY next_review
        ORDER BY next_review ASC
    """, (f'+{days}',))
    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_review_streak() -> dict:
    """Get current and longest review streak information."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get all distinct review dates in descending order
    cursor.execute("""
        SELECT DISTINCT date(reviewed_at) as review_date
        FROM card_reviews
        ORDER BY review_date DESC
    """)
    review_dates = [row['review_date'] for row in cursor.fetchall()]

    if not review_dates:
        conn.close()
        return {'current_streak': 0, 'longest_streak': 0, 'last_review_date': None}

    # Calculate current streak
    current_streak = 0
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    # Check if reviewed today or yesterday to continue streak
    if review_dates and (review_dates[0] == today or review_dates[0] == yesterday):
        check_date = date.fromisoformat(review_dates[0])
        for review_date in review_dates:
            if date.fromisoformat(review_date) == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

    # Calculate longest streak
    longest_streak = 0
    if review_dates:
        streak = 1
        for i in range(1, len(review_dates)):
            prev_date = date.fromisoformat(review_dates[i-1])
            curr_date = date.fromisoformat(review_dates[i])
            if prev_date - curr_date == timedelta(days=1):
                streak += 1
            else:
                longest_streak = max(longest_streak, streak)
                streak = 1
        longest_streak = max(longest_streak, streak)

    conn.close()
    return {
        'current_streak': current_streak,
        'longest_streak': max(longest_streak, current_streak),
        'last_review_date': review_dates[0] if review_dates else None
    }


def get_srs_performance_by_subject() -> list:
    """Get flashcard performance metrics grouped by subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.id as subject_id,
            s.name as subject_name,
            s.colour as subject_colour,
            COUNT(DISTINCT f.id) as total_cards,
            COUNT(DISTINCT CASE WHEN f.next_review <= date('now') THEN f.id END) as due_cards,
            COALESCE(AVG(f.ease_factor), 2.5) as avg_ease,
            COALESCE(
                100.0 * SUM(CASE WHEN cr.quality >= 3 THEN 1 ELSE 0 END) / NULLIF(COUNT(cr.id), 0),
                0
            ) as accuracy,
            COUNT(cr.id) as total_reviews
        FROM subjects s
        LEFT JOIN flashcards f ON f.subject_id = s.id
        LEFT JOIN card_reviews cr ON cr.flashcard_id = f.id
        GROUP BY s.id
        HAVING total_cards > 0
        ORDER BY total_cards DESC
    """)
    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_card_maturity_distribution() -> dict:
    """Get count of cards by maturity stage."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(CASE WHEN times_reviewed = 0 THEN 1 END) as new_cards,
            COUNT(CASE WHEN times_reviewed > 0 AND interval < 7 THEN 1 END) as learning,
            COUNT(CASE WHEN interval >= 7 AND interval < 21 THEN 1 END) as young,
            COUNT(CASE WHEN interval >= 21 THEN 1 END) as mature,
            COUNT(*) as total
        FROM flashcards
    """)
    result = row_to_dict(cursor.fetchone())
    conn.close()
    return result or {'new_cards': 0, 'learning': 0, 'young': 0, 'mature': 0, 'total': 0}


def get_average_review_time_trend(days: int = 14) -> list:
    """Get average time per card over the past N days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            date(reviewed_at) as review_date,
            ROUND(AVG(time_taken_seconds), 1) as avg_time_seconds,
            COUNT(*) as cards_reviewed
        FROM card_reviews
        WHERE reviewed_at >= date('now', ? || ' days')
          AND time_taken_seconds IS NOT NULL
          AND time_taken_seconds > 0
        GROUP BY date(reviewed_at)
        ORDER BY review_date ASC
    """, (f'-{days}',))
    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_review_heatmap_data(weeks: int = 12) -> list:
    """Get review activity data for calendar heatmap (GitHub-style)."""
    conn = get_connection()
    cursor = conn.cursor()
    days = weeks * 7
    cursor.execute("""
        SELECT
            date(reviewed_at) as review_date,
            COUNT(*) as review_count
        FROM card_reviews
        WHERE reviewed_at >= date('now', ? || ' days')
        GROUP BY date(reviewed_at)
        ORDER BY review_date ASC
    """, (f'-{days}',))

    reviews = {row['review_date']: row['review_count'] for row in cursor.fetchall()}

    # Find max for intensity calculation
    max_count = max(reviews.values()) if reviews else 1

    # Build heatmap data for all days
    result = []
    start_date = date.today() - timedelta(days=days)
    for i in range(days + 1):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()
        count = reviews.get(d_str, 0)
        # Calculate intensity level 0-4
        if count == 0:
            level = 0
        elif count <= max_count * 0.25:
            level = 1
        elif count <= max_count * 0.5:
            level = 2
        elif count <= max_count * 0.75:
            level = 3
        else:
            level = 4
        result.append({
            'date': d_str,
            'count': count,
            'level': level,
            'weekday': d.weekday()
        })

    conn.close()
    return result


def record_daily_activity():
    """Update review_activity table with today's stats (called after reviews)."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    # Get today's stats from card_reviews
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct,
            COALESCE(SUM(time_taken_seconds), 0) as time_total
        FROM card_reviews
        WHERE date(reviewed_at) = date('now')
    """)
    stats = cursor.fetchone()

    # Calculate streak
    streak_info = get_review_streak()

    # Upsert into review_activity
    cursor.execute("""
        INSERT INTO review_activity (activity_date, cards_reviewed, cards_correct, total_time_seconds, streak_day)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(activity_date) DO UPDATE SET
            cards_reviewed = excluded.cards_reviewed,
            cards_correct = excluded.cards_correct,
            total_time_seconds = excluded.total_time_seconds,
            streak_day = excluded.streak_day
    """, (today, stats['total'], stats['correct'], stats['time_total'], streak_info['current_streak']))

    conn.commit()
    conn.close()


def get_overdue_flashcards_count() -> int:
    """Get count of cards that are overdue (past their next_review date)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM flashcards
        WHERE next_review < date('now')
    """)
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_weekly_srs_summary() -> dict:
    """Get SRS performance summary for the past week."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as cards_reviewed,
            SUM(CASE WHEN quality >= 3 THEN 1 ELSE 0 END) as correct,
            COALESCE(SUM(time_taken_seconds), 0) as total_time_seconds
        FROM card_reviews
        WHERE reviewed_at >= date('now', '-7 days')
    """)
    result = cursor.fetchone()
    conn.close()

    cards = result['cards_reviewed'] if result else 0
    correct = result['correct'] if result else 0
    time_secs = result['total_time_seconds'] if result else 0

    return {
        'cards_reviewed': cards,
        'correct': correct,
        'accuracy': round(100.0 * correct / cards, 1) if cards > 0 else 0,
        'time_spent_mins': round(time_secs / 60, 1) if time_secs else 0
    }


def get_srs_notification_data() -> dict:
    """Get all data needed for SRS notifications."""
    due_count = get_due_flashcards_count()
    overdue_count = get_overdue_flashcards_count()
    streak = get_review_streak()
    weekly = get_weekly_srs_summary()

    return {
        'cards_due': due_count,
        'cards_overdue': overdue_count,
        'streak': streak['current_streak'],
        'longest_streak': streak['longest_streak'],
        'weekly_stats': weekly
    }


# =============================================================================
# TOPIC SRS FUNCTIONS
# =============================================================================

def add_topic_for_review(subject_id: int, topic: str, importance: str = 'medium',
                         source: str = 'manual') -> int:
    """Add or update a topic for spaced repetition tracking."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO topic_reviews (subject_id, topic, importance_level, source, next_review)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(subject_id, topic) DO UPDATE SET
            importance_level = COALESCE(excluded.importance_level, importance_level),
            source = COALESCE(excluded.source, source),
            updated_at = CURRENT_TIMESTAMP
    """, (subject_id, topic, importance, source, today))

    conn.commit()
    topic_id = cursor.lastrowid
    conn.close()
    return topic_id


def get_due_topics(subject_id: int = None, limit: int = 10) -> list:
    """Get topics that are due for review today or earlier."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT tr.*, s.name as subject_name, s.colour as subject_colour
            FROM topic_reviews tr
            JOIN subjects s ON tr.subject_id = s.id
            WHERE tr.next_review <= date('now')
              AND tr.subject_id = ?
            ORDER BY tr.next_review ASC, tr.ease_factor ASC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT tr.*, s.name as subject_name, s.colour as subject_colour
            FROM topic_reviews tr
            JOIN subjects s ON tr.subject_id = s.id
            WHERE tr.next_review <= date('now')
            ORDER BY tr.next_review ASC, tr.ease_factor ASC
            LIMIT ?
        """, (limit,))

    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def review_topic(topic_id: int, quiz_score: float, time_spent_minutes: int = None):
    """Update topic after a review/quiz session using SM-2 algorithm.
    quiz_score should be 0-100, will be mapped to 0-5 quality."""
    conn = get_connection()
    cursor = conn.cursor()

    # Map quiz score (0-100) to quality (0-5)
    if quiz_score >= 90:
        quality = 5
    elif quiz_score >= 80:
        quality = 4
    elif quiz_score >= 60:
        quality = 3
    elif quiz_score >= 40:
        quality = 2
    elif quiz_score >= 20:
        quality = 1
    else:
        quality = 0

    # Get current topic data
    cursor.execute("SELECT * FROM topic_reviews WHERE id = ?", (topic_id,))
    topic = cursor.fetchone()

    if not topic:
        conn.close()
        return

    # Apply SM-2 algorithm
    ease_factor = topic['ease_factor']
    interval = topic['interval']
    repetitions = topic['repetitions']

    if quality < 3:
        # Failed - reset
        repetitions = 0
        interval = 1
    else:
        # Passed
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)
        repetitions += 1

    # Update ease factor
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease_factor = max(1.3, ease_factor)

    # Calculate next review date
    next_review = (date.today() + timedelta(days=interval)).isoformat()

    # Calculate running average of quiz scores
    times_reviewed = topic['times_reviewed'] + 1
    prev_avg = topic['avg_quiz_score'] or 0
    new_avg = ((prev_avg * (times_reviewed - 1)) + quiz_score) / times_reviewed

    # Update topic
    cursor.execute("""
        UPDATE topic_reviews SET
            ease_factor = ?,
            interval = ?,
            repetitions = ?,
            next_review = ?,
            last_reviewed_at = CURRENT_TIMESTAMP,
            times_reviewed = ?,
            avg_quiz_score = ?
        WHERE id = ?
    """, (ease_factor, interval, repetitions, next_review, times_reviewed, new_avg, topic_id))

    conn.commit()
    conn.close()


def sync_topics_from_flashcards():
    """Auto-populate topic_reviews from flashcard topics."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get distinct topics from flashcards that aren't already in topic_reviews
    cursor.execute("""
        SELECT DISTINCT f.subject_id, f.topic
        FROM flashcards f
        WHERE f.topic IS NOT NULL
          AND f.topic != ''
          AND NOT EXISTS (
              SELECT 1 FROM topic_reviews tr
              WHERE tr.subject_id = f.subject_id AND tr.topic = f.topic
          )
    """)

    topics = cursor.fetchall()
    today = date.today().isoformat()

    for topic in topics:
        cursor.execute("""
            INSERT INTO topic_reviews (subject_id, topic, source, next_review)
            VALUES (?, ?, 'flashcard', ?)
        """, (topic['subject_id'], topic['topic'], today))

    conn.commit()
    conn.close()
    return len(topics)


def get_topic_review_recommendations(limit: int = 5) -> list:
    """Get prioritized list of topics to review based on multiple factors."""
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate priority score based on:
    # - Days overdue (higher = more urgent)
    # - Lower ease factor (harder topics)
    # - Lower avg_quiz_score
    # - Higher importance level
    cursor.execute("""
        SELECT
            tr.*,
            s.name as subject_name,
            s.colour as subject_colour,
            julianday('now') - julianday(tr.next_review) as days_overdue,
            e.exam_date,
            CASE WHEN e.exam_date IS NOT NULL
                 THEN julianday(e.exam_date) - julianday('now')
                 ELSE 999 END as days_to_exam,
            CASE
                WHEN tr.importance_level = 'critical' THEN 4
                WHEN tr.importance_level = 'high' THEN 3
                WHEN tr.importance_level = 'medium' THEN 2
                ELSE 1
            END as importance_score
        FROM topic_reviews tr
        JOIN subjects s ON tr.subject_id = s.id
        LEFT JOIN exams e ON e.subject_id = s.id AND e.exam_date >= date('now')
        WHERE tr.next_review <= date('now')
        ORDER BY
            days_overdue DESC,
            importance_score DESC,
            tr.ease_factor ASC,
            days_to_exam ASC
        LIMIT ?
    """, (limit,))

    result = rows_to_dicts(cursor.fetchall())
    conn.close()
    return result


def get_topics_due_count() -> int:
    """Get count of topics due for review."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM topic_reviews
        WHERE next_review <= date('now')
    """)
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


# =============================================================================
# NOTIFICATION SETTINGS FUNCTIONS
# =============================================================================

def get_notification_setting(key: str, default: str = None) -> tuple:
    """Get a notification setting value and enabled status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT setting_value, enabled FROM notification_settings WHERE setting_key = ?",
        (key,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return (result['setting_value'], bool(result['enabled']))
    return (default, True)


def set_notification_setting(key: str, value: str, enabled: bool = True):
    """Set a notification setting."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notification_settings (setting_key, setting_value, enabled, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(setting_key) DO UPDATE SET
            setting_value = excluded.setting_value,
            enabled = excluded.enabled,
            updated_at = CURRENT_TIMESTAMP
    """, (key, value, 1 if enabled else 0))
    conn.commit()
    conn.close()


def get_all_notification_settings() -> dict:
    """Get all notification settings as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT setting_key, setting_value, enabled FROM notification_settings")
    results = cursor.fetchall()
    conn.close()

    return {row['setting_key']: {'value': row['setting_value'], 'enabled': bool(row['enabled'])}
            for row in results}


# =============================================================================
# ESSAY TUTOR FUNCTIONS
# =============================================================================

def save_essay_submission(subject_id: int, title: str, question: str, text: str,
                          word_count: int, grade: str, overall_score: int,
                          feedback_json: str) -> int:
    """Save an essay submission with feedback. Returns the submission ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO essay_submissions
        (subject_id, essay_title, essay_question, essay_text, word_count,
         grade, overall_score, feedback_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (subject_id, title, question, text, word_count, grade, overall_score, feedback_json))
    conn.commit()
    submission_id = cursor.lastrowid
    conn.close()
    return submission_id


def get_essay_submissions(subject_id: int = None, limit: int = 20) -> list:
    """Get essay submissions, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT e.*, s.name as subject_name, s.colour as subject_colour
            FROM essay_submissions e
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.subject_id = ?
            ORDER BY e.submitted_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT e.*, s.name as subject_name, s.colour as subject_colour
            FROM essay_submissions e
            LEFT JOIN subjects s ON e.subject_id = s.id
            ORDER BY e.submitted_at DESC
            LIMIT ?
        """, (limit,))

    results = rows_to_dicts(cursor.fetchall())
    conn.close()
    return results


def get_essay_by_id(essay_id: int) -> dict:
    """Get a single essay submission by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM essay_submissions e
        LEFT JOIN subjects s ON e.subject_id = s.id
        WHERE e.id = ?
    """, (essay_id,))
    result = cursor.fetchone()
    conn.close()
    return row_to_dict(result)


def delete_essay_submission(essay_id: int):
    """Delete an essay submission."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM essay_submissions WHERE id = ?", (essay_id,))
    conn.commit()
    conn.close()


def get_essay_stats() -> dict:
    """Get essay submission statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_essays,
            AVG(overall_score) as avg_score,
            MAX(overall_score) as best_score,
            AVG(word_count) as avg_word_count
        FROM essay_submissions
    """)
    result = cursor.fetchone()
    conn.close()
    return row_to_dict(result) if result else {
        'total_essays': 0, 'avg_score': 0, 'best_score': 0, 'avg_word_count': 0
    }


# =============================================================================
# NOTE FUNCTIONS
# =============================================================================

def add_note(subject_id: int, title: str, content: str, topic: str = None) -> int:
    """Add a new note. Returns the new note's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO notes (subject_id, title, topic, content)
           VALUES (?, ?, ?, ?)""",
        (subject_id, title, topic, content)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id


def get_all_notes(subject_id: int = None) -> list:
    """Get all notes, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT n.*, s.name as subject_name, s.colour as subject_colour
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            WHERE n.subject_id = ?
            ORDER BY n.updated_at DESC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT n.*, s.name as subject_name, s.colour as subject_colour
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            ORDER BY n.updated_at DESC
        """)

    notes = cursor.fetchall()
    conn.close()
    return rows_to_dicts(notes)


def get_note_by_id(note_id: int):
    """Get a single note by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, s.name as subject_name, s.colour as subject_colour
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        WHERE n.id = ?
    """, (note_id,))
    note = cursor.fetchone()
    conn.close()
    return row_to_dict(note)


def update_note(note_id: int, title: str = None, content: str = None,
                topic: str = None, subject_id: int = None):
    """Update an existing note."""
    conn = get_connection()
    cursor = conn.cursor()

    # Build dynamic update query
    updates = []
    values = []

    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if content is not None:
        updates.append("content = ?")
        values.append(content)
    if topic is not None:
        updates.append("topic = ?")
        values.append(topic)
    if subject_id is not None:
        updates.append("subject_id = ?")
        values.append(subject_id)

    # Always update the updated_at timestamp
    updates.append("updated_at = CURRENT_TIMESTAMP")

    if updates:
        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        values.append(note_id)
        cursor.execute(query, values)
        conn.commit()

    conn.close()


def delete_note(note_id: int):
    """Delete a note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


def toggle_note_favourite(note_id: int):
    """Toggle the favourite status of a note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notes SET is_favourite = NOT is_favourite WHERE id = ?",
        (note_id,)
    )
    conn.commit()
    conn.close()


def get_favourite_notes() -> list:
    """Get all favourite notes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, s.name as subject_name, s.colour as subject_colour
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        WHERE n.is_favourite = 1
        ORDER BY n.updated_at DESC
    """)
    notes = cursor.fetchall()
    conn.close()
    return rows_to_dicts(notes)


def search_notes(query: str, subject_id: int = None) -> list:
    """Search notes by keyword in title, topic, or content."""
    conn = get_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"

    if subject_id:
        cursor.execute("""
            SELECT n.*, s.name as subject_name, s.colour as subject_colour
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            WHERE n.subject_id = ?
              AND (n.title LIKE ? OR n.topic LIKE ? OR n.content LIKE ?)
            ORDER BY n.updated_at DESC
        """, (subject_id, search_term, search_term, search_term))
    else:
        cursor.execute("""
            SELECT n.*, s.name as subject_name, s.colour as subject_colour
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            WHERE n.title LIKE ? OR n.topic LIKE ? OR n.content LIKE ?
            ORDER BY n.updated_at DESC
        """, (search_term, search_term, search_term))

    notes = cursor.fetchall()
    conn.close()
    return rows_to_dicts(notes)


def get_notes_count(subject_id: int = None) -> int:
    """Get count of notes, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute(
            "SELECT COUNT(*) as count FROM notes WHERE subject_id = ?",
            (subject_id,)
        )
    else:
        cursor.execute("SELECT COUNT(*) as count FROM notes")

    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_recent_notes(limit: int = 5) -> list:
    """Get most recently updated notes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, s.name as subject_name, s.colour as subject_colour
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        ORDER BY n.updated_at DESC
        LIMIT ?
    """, (limit,))
    notes = cursor.fetchall()
    conn.close()
    return rows_to_dicts(notes)


# =============================================================================
# NOTE IMAGES FUNCTIONS
# =============================================================================

def add_note_image(note_id: int, filename: str, original_filename: str,
                   file_path: str, file_size: int = None, width: int = None,
                   height: int = None, extracted_text: str = None) -> int:
    """Add an image associated with a note (from OCR)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO note_images
        (note_id, filename, original_filename, file_path, file_size, width, height, extracted_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (note_id, filename, original_filename, file_path, file_size, width, height, extracted_text))
    image_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return image_id


def get_note_images(note_id: int) -> list:
    """Get all images associated with a note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM note_images
        WHERE note_id = ?
        ORDER BY created_at ASC
    """, (note_id,))
    images = cursor.fetchall()
    conn.close()
    return rows_to_dicts(images)


def get_note_image_by_id(image_id: int):
    """Get a single note image by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM note_images WHERE id = ?", (image_id,))
    image = cursor.fetchone()
    conn.close()
    return row_to_dict(image)


def delete_note_image(image_id: int):
    """Delete a note image by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM note_images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()


def delete_note_images(note_id: int):
    """Delete all images associated with a note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM note_images WHERE note_id = ?", (note_id,))
    conn.commit()
    conn.close()


def get_all_note_images() -> list:
    """Get all note images (for backup purposes)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ni.*, n.title as note_title, s.name as subject_name
        FROM note_images ni
        JOIN notes n ON ni.note_id = n.id
        JOIN subjects s ON n.subject_id = s.id
        ORDER BY ni.created_at DESC
    """)
    images = cursor.fetchall()
    conn.close()
    return rows_to_dicts(images)


def get_note_images_count() -> int:
    """Get count of all note images."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM note_images")
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


# =============================================================================
# PAST PAPER FUNCTIONS
# =============================================================================

def add_past_paper(subject_id: int, paper_name: str, total_marks: int,
                   exam_board: str = None, year: str = None, paper_number: str = None,
                   time_taken_minutes: int = None, notes: str = None,
                   raw_content: str = None, ai_summary: str = None,
                   marks_achieved: int = None) -> int:
    """Add a new past paper record. Returns the paper ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO past_papers
           (subject_id, paper_name, total_marks, exam_board, year, paper_number,
            time_taken_minutes, notes, raw_content, ai_summary)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (subject_id, paper_name, total_marks, exam_board, year, paper_number,
         time_taken_minutes, notes, raw_content, ai_summary)
    )
    conn.commit()
    paper_id = cursor.lastrowid
    conn.close()
    return paper_id


def update_paper_summary(paper_id: int, ai_summary: str):
    """Update the AI summary for a paper."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE past_papers SET ai_summary = ? WHERE id = ?",
        (ai_summary, paper_id)
    )
    conn.commit()
    conn.close()


def add_paper_question(paper_id: int, question_number: str, max_marks: int,
                       marks_achieved: int = 0, topic: str = None, notes: str = None,
                       question_text: str = None, question_type: str = None,
                       difficulty: str = None, ai_analysis: str = None) -> int:
    """Add a question result to a past paper. Returns the question ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO paper_questions
           (paper_id, question_number, max_marks, marks_achieved, topic, notes,
            question_text, question_type, difficulty, ai_analysis)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (paper_id, question_number, max_marks, marks_achieved, topic, notes,
         question_text, question_type, difficulty, ai_analysis)
    )
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id


def get_question_type_stats(subject_id: int = None) -> list:
    """Get statistics by question type."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT
                pq.question_type,
                COUNT(*) as count,
                SUM(pq.max_marks) as total_marks,
                AVG(CAST(pq.marks_achieved AS FLOAT) / pq.max_marks * 100) as avg_percentage
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            WHERE pq.question_type IS NOT NULL AND pp.subject_id = ?
            GROUP BY pq.question_type
            ORDER BY count DESC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT
                pq.question_type,
                COUNT(*) as count,
                SUM(pq.max_marks) as total_marks,
                AVG(CAST(pq.marks_achieved AS FLOAT) / pq.max_marks * 100) as avg_percentage
            FROM paper_questions pq
            WHERE pq.question_type IS NOT NULL
            GROUP BY pq.question_type
            ORDER BY count DESC
        """)

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def get_common_topics(subject_id: int = None, limit: int = 10) -> list:
    """Get most common topics across papers."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT
                pq.topic,
                COUNT(*) as frequency,
                COUNT(DISTINCT pp.id) as paper_count,
                AVG(CAST(pq.marks_achieved AS FLOAT) / pq.max_marks * 100) as avg_percentage
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            WHERE pq.topic IS NOT NULL AND pq.topic != '' AND pp.subject_id = ?
            GROUP BY pq.topic
            ORDER BY frequency DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT
                pq.topic,
                COUNT(*) as frequency,
                COUNT(DISTINCT pp.id) as paper_count,
                AVG(CAST(pq.marks_achieved AS FLOAT) / pq.max_marks * 100) as avg_percentage
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            WHERE pq.topic IS NOT NULL AND pq.topic != ''
            GROUP BY pq.topic
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def save_analysis_report(subject_id: int, report_type: str, report_content: str) -> int:
    """Save an analysis report."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO paper_analysis_reports (subject_id, report_type, report_content)
           VALUES (?, ?, ?)""",
        (subject_id, report_type, report_content)
    )
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id


def get_latest_analysis_report(subject_id: int = None, report_type: str = None) -> dict:
    """Get the latest analysis report."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id and report_type:
        cursor.execute("""
            SELECT * FROM paper_analysis_reports
            WHERE subject_id = ? AND report_type = ?
            ORDER BY created_at DESC LIMIT 1
        """, (subject_id, report_type))
    elif subject_id:
        cursor.execute("""
            SELECT * FROM paper_analysis_reports
            WHERE subject_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (subject_id,))
    elif report_type:
        cursor.execute("""
            SELECT * FROM paper_analysis_reports
            WHERE report_type = ?
            ORDER BY created_at DESC LIMIT 1
        """, (report_type,))
    else:
        cursor.execute("""
            SELECT * FROM paper_analysis_reports
            ORDER BY created_at DESC LIMIT 1
        """)

    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def get_all_questions(subject_id: int = None, topic: str = None,
                      question_type: str = None) -> list:
    """Get all questions with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT pq.*, pp.paper_name, pp.exam_board, pp.year, s.name as subject_name
        FROM paper_questions pq
        JOIN past_papers pp ON pq.paper_id = pp.id
        JOIN subjects s ON pp.subject_id = s.id
        WHERE 1=1
    """
    params = []

    if subject_id:
        query += " AND pp.subject_id = ?"
        params.append(subject_id)
    if topic:
        query += " AND pq.topic LIKE ?"
        params.append(f"%{topic}%")
    if question_type:
        query += " AND pq.question_type = ?"
        params.append(question_type)

    query += " ORDER BY pp.year DESC, pp.paper_name, pq.question_number"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def get_all_past_papers(subject_id: int = None) -> list:
    """Get all past papers, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT pp.*, s.name as subject_name, s.colour as subject_colour,
                   (SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) as marks_achieved
            FROM past_papers pp
            JOIN subjects s ON pp.subject_id = s.id
            WHERE pp.subject_id = ?
            ORDER BY pp.completed_at DESC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT pp.*, s.name as subject_name, s.colour as subject_colour,
                   (SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) as marks_achieved
            FROM past_papers pp
            JOIN subjects s ON pp.subject_id = s.id
            ORDER BY pp.completed_at DESC
        """)

    papers = cursor.fetchall()
    conn.close()
    return rows_to_dicts(papers)


def get_past_paper_by_id(paper_id: int):
    """Get a single past paper by ID with its questions."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get paper details
    cursor.execute("""
        SELECT pp.*, s.name as subject_name, s.colour as subject_colour
        FROM past_papers pp
        JOIN subjects s ON pp.subject_id = s.id
        WHERE pp.id = ?
    """, (paper_id,))
    paper = cursor.fetchone()

    if paper:
        paper = row_to_dict(paper)

        # Get questions for this paper
        cursor.execute("""
            SELECT * FROM paper_questions
            WHERE paper_id = ?
            ORDER BY question_number
        """, (paper_id,))
        paper['questions'] = rows_to_dicts(cursor.fetchall())

        # Calculate total marks achieved
        paper['marks_achieved'] = sum(q['marks_achieved'] for q in paper['questions'])
        paper['percentage'] = round((paper['marks_achieved'] / paper['total_marks']) * 100, 1) if paper['total_marks'] > 0 else 0

    conn.close()
    return paper


def delete_past_paper(paper_id: int):
    """Delete a past paper and its questions."""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete questions first
    cursor.execute("DELETE FROM paper_questions WHERE paper_id = ?", (paper_id,))
    # Delete paper
    cursor.execute("DELETE FROM past_papers WHERE id = ?", (paper_id,))
    conn.commit()
    conn.close()


def get_topic_performance(subject_id: int = None) -> list:
    """Get performance breakdown by topic across all past papers."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT
                pq.topic,
                s.name as subject_name,
                s.colour as subject_colour,
                COUNT(*) as question_count,
                SUM(pq.max_marks) as total_possible,
                SUM(pq.marks_achieved) as total_achieved,
                ROUND(CAST(SUM(pq.marks_achieved) AS FLOAT) / SUM(pq.max_marks) * 100, 1) as percentage
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            JOIN subjects s ON pp.subject_id = s.id
            WHERE pq.topic IS NOT NULL AND pq.topic != '' AND pp.subject_id = ?
            GROUP BY pq.topic, s.id
            ORDER BY percentage ASC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT
                pq.topic,
                s.name as subject_name,
                s.colour as subject_colour,
                COUNT(*) as question_count,
                SUM(pq.max_marks) as total_possible,
                SUM(pq.marks_achieved) as total_achieved,
                ROUND(CAST(SUM(pq.marks_achieved) AS FLOAT) / SUM(pq.max_marks) * 100, 1) as percentage
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            JOIN subjects s ON pp.subject_id = s.id
            WHERE pq.topic IS NOT NULL AND pq.topic != ''
            GROUP BY pq.topic, s.id
            ORDER BY percentage ASC
        """)

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def get_subject_paper_stats(subject_id: int = None) -> list:
    """Get overall stats for each subject from past papers."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT
                s.id as subject_id,
                s.name as subject_name,
                s.colour as subject_colour,
                COUNT(DISTINCT pp.id) as paper_count,
                SUM(pp.total_marks) as total_possible,
                SUM(pq.marks_achieved) as total_achieved,
                ROUND(CAST(SUM(pq.marks_achieved) AS FLOAT) / SUM(pp.total_marks) * 100, 1) as average_percentage
            FROM subjects s
            LEFT JOIN past_papers pp ON s.id = pp.subject_id
            LEFT JOIN paper_questions pq ON pp.id = pq.paper_id
            WHERE s.id = ?
            GROUP BY s.id
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT
                s.id as subject_id,
                s.name as subject_name,
                s.colour as subject_colour,
                COUNT(DISTINCT pp.id) as paper_count,
                SUM(pp.total_marks) as total_possible,
                SUM(pq.marks_achieved) as total_achieved,
                ROUND(CAST(SUM(pq.marks_achieved) AS FLOAT) / NULLIF(SUM(pp.total_marks), 0) * 100, 1) as average_percentage
            FROM subjects s
            LEFT JOIN past_papers pp ON s.id = pp.subject_id
            LEFT JOIN paper_questions pq ON pp.id = pq.paper_id
            GROUP BY s.id
            HAVING paper_count > 0
            ORDER BY average_percentage ASC
        """)

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def get_weak_topics(limit: int = 10) -> list:
    """Get topics with lowest performance (weak areas to focus on)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pq.topic,
            s.name as subject_name,
            s.colour as subject_colour,
            COUNT(*) as question_count,
            SUM(pq.max_marks) as total_possible,
            SUM(pq.marks_achieved) as total_achieved,
            ROUND(CAST(SUM(pq.marks_achieved) AS FLOAT) / SUM(pq.max_marks) * 100, 1) as percentage
        FROM paper_questions pq
        JOIN past_papers pp ON pq.paper_id = pp.id
        JOIN subjects s ON pp.subject_id = s.id
        WHERE pq.topic IS NOT NULL AND pq.topic != ''
        GROUP BY pq.topic, s.id
        HAVING question_count >= 1
        ORDER BY percentage ASC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


def get_recent_papers(limit: int = 5) -> list:
    """Get most recent past papers."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pp.*, s.name as subject_name, s.colour as subject_colour,
               (SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) as marks_achieved
        FROM past_papers pp
        JOIN subjects s ON pp.subject_id = s.id
        ORDER BY pp.completed_at DESC
        LIMIT ?
    """, (limit,))

    papers = cursor.fetchall()
    conn.close()
    return rows_to_dicts(papers)


def get_paper_count() -> int:
    """Get total number of past papers."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM past_papers")
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_progress_over_time(subject_id: int = None, limit: int = 10) -> list:
    """Get paper scores over time to track progress."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT
                pp.id,
                pp.paper_name,
                pp.completed_at,
                pp.total_marks,
                s.name as subject_name,
                (SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) as marks_achieved,
                ROUND(CAST((SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) AS FLOAT)
                      / pp.total_marks * 100, 1) as percentage
            FROM past_papers pp
            JOIN subjects s ON pp.subject_id = s.id
            WHERE pp.subject_id = ?
            ORDER BY pp.completed_at ASC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT
                pp.id,
                pp.paper_name,
                pp.completed_at,
                pp.total_marks,
                s.name as subject_name,
                (SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) as marks_achieved,
                ROUND(CAST((SELECT SUM(marks_achieved) FROM paper_questions WHERE paper_id = pp.id) AS FLOAT)
                      / pp.total_marks * 100, 1) as percentage
            FROM past_papers pp
            JOIN subjects s ON pp.subject_id = s.id
            ORDER BY pp.completed_at ASC
            LIMIT ?
        """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return rows_to_dicts(results)


# =============================================================================
# STUDY RECOMMENDATION SYSTEM
# =============================================================================

def get_study_recommendations(limit: int = 5) -> list:
    """
    Generate prioritised study recommendations based on multiple factors.

    Scoring factors:
    - Overdue homework: +100 points (urgent!)
    - Homework due today: +80 points
    - Homework due tomorrow: +60 points
    - Homework due this week: +40 points
    - Flashcards overdue: +50 points (scaled by count)
    - Exam within 7 days: +70 points
    - Exam within 14 days: +50 points
    - Exam within 30 days: +30 points
    - Days since last study: +5 points per day (max 30)

    Returns a list of recommendation dictionaries with:
    - type: 'homework', 'flashcards', 'exam_prep', 'review'
    - subject_name: The subject
    - title: What to do
    - reason: Why this is recommended
    - priority_score: Numerical score (higher = more urgent)
    - action: Specific action to take
    """
    recommendations = []
    today = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------------------
    # 1. OVERDUE HOMEWORK (Highest priority)
    # -----------------------------------------------------------------
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.completed = 0 AND h.due_date < ?
        ORDER BY h.due_date ASC
    """, (today.isoformat(),))

    for hw in cursor.fetchall():
        days_overdue = (today - date.fromisoformat(hw['due_date'])).days
        score = 100 + (days_overdue * 10)  # More overdue = higher priority
        recommendations.append({
            'type': 'homework',
            'subject_id': hw['subject_id'],
            'subject_name': hw['subject_name'],
            'subject_colour': hw['subject_colour'],
            'title': hw['title'],
            'reason': f"OVERDUE by {days_overdue} day{'s' if days_overdue != 1 else ''}!",
            'priority_score': score,
            'action': 'Complete this homework immediately',
            'item_id': hw['id'],
            'urgency': 'critical'
        })

    # -----------------------------------------------------------------
    # 2. HOMEWORK DUE TODAY
    # -----------------------------------------------------------------
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.completed = 0 AND h.due_date = ?
        ORDER BY h.priority DESC
    """, (today.isoformat(),))

    for hw in cursor.fetchall():
        score = 80
        if hw['priority'] == 'high':
            score += 15
        recommendations.append({
            'type': 'homework',
            'subject_id': hw['subject_id'],
            'subject_name': hw['subject_name'],
            'subject_colour': hw['subject_colour'],
            'title': hw['title'],
            'reason': "Due TODAY",
            'priority_score': score,
            'action': 'Complete before end of day',
            'item_id': hw['id'],
            'urgency': 'high'
        })

    # -----------------------------------------------------------------
    # 3. HOMEWORK DUE TOMORROW
    # -----------------------------------------------------------------
    tomorrow = (today + timedelta(days=1)).isoformat()
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.completed = 0 AND h.due_date = ?
        ORDER BY h.priority DESC
    """, (tomorrow,))

    for hw in cursor.fetchall():
        score = 60
        if hw['priority'] == 'high':
            score += 10
        recommendations.append({
            'type': 'homework',
            'subject_id': hw['subject_id'],
            'subject_name': hw['subject_name'],
            'subject_colour': hw['subject_colour'],
            'title': hw['title'],
            'reason': "Due TOMORROW",
            'priority_score': score,
            'action': 'Start today to avoid rushing',
            'item_id': hw['id'],
            'urgency': 'medium'
        })

    # -----------------------------------------------------------------
    # 4. FLASHCARDS DUE (grouped by subject)
    # -----------------------------------------------------------------
    cursor.execute("""
        SELECT s.id as subject_id, s.name as subject_name, s.colour as subject_colour,
               COUNT(f.id) as due_count
        FROM subjects s
        JOIN flashcards f ON s.id = f.subject_id
        WHERE f.next_review <= ?
        GROUP BY s.id
        ORDER BY due_count DESC
    """, (today.isoformat(),))

    for row in cursor.fetchall():
        if row['due_count'] > 0:
            # Score based on number of cards due
            score = min(50 + row['due_count'], 75)  # Cap at 75
            recommendations.append({
                'type': 'flashcards',
                'subject_id': row['subject_id'],
                'subject_name': row['subject_name'],
                'subject_colour': row['subject_colour'],
                'title': f"Review {row['due_count']} flashcards",
                'reason': f"{row['due_count']} cards due for review",
                'priority_score': score,
                'action': 'Review flashcards to reinforce memory',
                'item_id': None,
                'urgency': 'medium' if row['due_count'] > 10 else 'low'
            })

    # -----------------------------------------------------------------
    # 5. UPCOMING EXAMS (Revision needed)
    # -----------------------------------------------------------------
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.exam_date >= ?
        ORDER BY e.exam_date ASC
    """, (today.isoformat(),))

    for exam in cursor.fetchall():
        days_until = (date.fromisoformat(exam['exam_date']) - today).days

        if days_until <= 7:
            score = 70 + (7 - days_until) * 5  # Higher as exam approaches
            urgency = 'high'
            reason = f"Exam in {days_until} day{'s' if days_until != 1 else ''}!"
        elif days_until <= 14:
            score = 50
            urgency = 'medium'
            reason = f"Exam in {days_until} days - start revising"
        elif days_until <= 30:
            score = 30
            urgency = 'low'
            reason = f"Exam in {days_until} days"
        else:
            continue  # Skip exams more than 30 days away

        recommendations.append({
            'type': 'exam_prep',
            'subject_id': exam['subject_id'],
            'subject_name': exam['subject_name'],
            'subject_colour': exam['subject_colour'],
            'title': f"Revise for: {exam['name']}",
            'reason': reason,
            'priority_score': score,
            'action': 'Create flashcards or review notes',
            'item_id': exam['id'],
            'urgency': urgency
        })

    # -----------------------------------------------------------------
    # 6. SUBJECTS NOT STUDIED RECENTLY
    # -----------------------------------------------------------------
    cursor.execute("""
        SELECT s.id, s.name, s.colour,
               MAX(fs.started_at) as last_studied
        FROM subjects s
        LEFT JOIN focus_sessions fs ON s.id = fs.subject_id AND fs.completed = 1
        GROUP BY s.id
    """)

    for row in cursor.fetchall():
        if row['last_studied']:
            last_date = datetime.fromisoformat(row['last_studied']).date()
            days_since = (today - last_date).days
        else:
            days_since = 30  # Never studied

        if days_since >= 3:  # Only recommend if not studied in 3+ days
            score = min(5 * days_since, 30)  # Cap at 30
            recommendations.append({
                'type': 'review',
                'subject_id': row['id'],
                'subject_name': row['name'],
                'subject_colour': row['colour'],
                'title': f"Review {row['name']}",
                'reason': f"Not studied in {days_since} days" if days_since < 30 else "Not studied yet",
                'priority_score': score,
                'action': 'Start a focus session to maintain knowledge',
                'item_id': None,
                'urgency': 'low'
            })

    conn.close()

    # Sort by priority score (highest first) and return top N
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
    return recommendations[:limit]


def get_top_recommendation():
    """Get the single most important thing to study right now."""
    recommendations = get_study_recommendations(limit=1)
    return recommendations[0] if recommendations else None


def get_subject_priority_scores() -> list:
    """
    Calculate priority scores for each subject based on all factors.
    Useful for showing which subjects need the most attention.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    # Get all subjects
    cursor.execute("SELECT * FROM subjects ORDER BY name")
    subjects = cursor.fetchall()

    results = []

    for subject in subjects:
        score = 0
        reasons = []

        # Overdue homework
        cursor.execute("""
            SELECT COUNT(*) as count FROM homework
            WHERE subject_id = ? AND completed = 0 AND due_date < ?
        """, (subject['id'], today.isoformat()))
        overdue = cursor.fetchone()['count']
        if overdue > 0:
            score += overdue * 20
            reasons.append(f"{overdue} overdue homework")

        # Due this week
        cursor.execute("""
            SELECT COUNT(*) as count FROM homework
            WHERE subject_id = ? AND completed = 0
            AND due_date >= ? AND due_date <= date(?, '+7 days')
        """, (subject['id'], today.isoformat(), today.isoformat()))
        due_week = cursor.fetchone()['count']
        if due_week > 0:
            score += due_week * 10
            reasons.append(f"{due_week} due this week")

        # Flashcards due
        cursor.execute("""
            SELECT COUNT(*) as count FROM flashcards
            WHERE subject_id = ? AND next_review <= ?
        """, (subject['id'], today.isoformat()))
        cards_due = cursor.fetchone()['count']
        if cards_due > 0:
            score += min(cards_due, 20)
            reasons.append(f"{cards_due} flashcards due")

        # Upcoming exams
        cursor.execute("""
            SELECT exam_date FROM exams
            WHERE subject_id = ? AND exam_date >= ?
            ORDER BY exam_date ASC LIMIT 1
        """, (subject['id'], today.isoformat()))
        exam = cursor.fetchone()
        if exam:
            days_until = (date.fromisoformat(exam['exam_date']) - today).days
            if days_until <= 14:
                score += max(30 - days_until, 0)
                reasons.append(f"Exam in {days_until} days")

        results.append({
            'subject_id': subject['id'],
            'subject_name': subject['name'],
            'subject_colour': subject['colour'],
            'priority_score': score,
            'reasons': reasons
        })

    conn.close()

    # Sort by score
    results.sort(key=lambda x: x['priority_score'], reverse=True)
    return results


# =============================================================================
# ADDITIONAL HELPER FUNCTIONS
# =============================================================================

def get_completed_homework():
    """Get all completed homework."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.*, s.name as subject_name, s.colour as subject_colour
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.completed = 1
        ORDER BY h.due_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_focus_streak():
    """Get the current focus streak (consecutive days with focus sessions)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT date(started_at) as focus_date
        FROM focus_sessions
        ORDER BY focus_date DESC
    """)
    dates = [row['focus_date'] for row in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    streak = 0
    today = date.today()

    for i, d in enumerate(dates):
        expected_date = (today - timedelta(days=i)).isoformat()
        if d == expected_date:
            streak += 1
        else:
            break

    return streak


def add_focus_session(subject_id: int, duration_minutes: int, completed: bool = True,
                      topic: str = None):
    """Add a focus session and update topic mastery if topic is provided."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO focus_sessions (subject_id, started_at, actual_minutes, completed, topic)
        VALUES (?, datetime('now'), ?, ?, ?)
    """, (subject_id, duration_minutes, 1 if completed else 0, topic))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()

    # Update topic mastery if session was completed with a topic
    if completed and topic and subject_id:
        update_topic_mastery(
            subject_id=subject_id,
            topic=topic,
            is_correct=True  # Completing a focus session counts as successful practice
        )

    return session_id


def get_recent_focus_sessions(limit: int = 10):
    """Get recent focus sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, s.name as subject_name
        FROM focus_sessions f
        JOIN subjects s ON f.subject_id = s.id
        ORDER BY f.started_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_homework_count_by_subject(subject_id: int) -> int:
    """Get homework count for a subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count FROM homework
        WHERE subject_id = ? AND completed = 0
    """, (subject_id,))
    count = cursor.fetchone()['count']
    conn.close()
    return count


def get_flashcard_count_by_subject(subject_id: int) -> int:
    """Get flashcard count for a subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count FROM flashcards
        WHERE subject_id = ?
    """, (subject_id,))
    count = cursor.fetchone()['count']
    conn.close()
    return count


def get_focus_minutes_this_week() -> int:
    """Get total focus minutes for the current week."""
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    cursor.execute("""
        SELECT COALESCE(SUM(actual_minutes), 0) as total
        FROM focus_sessions
        WHERE date(started_at) >= ?
    """, (week_start.isoformat(),))

    total = cursor.fetchone()['total']
    conn.close()
    return total


def get_focus_minutes_by_subject(subject_id: int) -> int:
    """Get total focus minutes for a subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(actual_minutes), 0) as total
        FROM focus_sessions
        WHERE subject_id = ?
    """, (subject_id,))
    total = cursor.fetchone()['total']
    conn.close()
    return total


def clear_completed_homework():
    """Delete all completed homework."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM homework WHERE completed = 1")
    conn.commit()
    conn.close()


def reset_flashcard_reviews():
    """Reset all flashcard review data to initial state."""
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today().isoformat()
    cursor.execute("""
        UPDATE flashcards
        SET next_review = ?,
            interval_days = 1,
            ease_factor = 2.5,
            repetitions = 0
    """, (today,))

    # Also clear review history
    cursor.execute("DELETE FROM flashcard_reviews")

    conn.commit()
    conn.close()


# =============================================================================
# KNOWLEDGE GAP ASSESSMENT FUNCTIONS
# =============================================================================

def create_assessment(subject_id: int, assessment_type: str, total_questions: int) -> int:
    """Create a new knowledge assessment session. Returns assessment ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO knowledge_assessments (subject_id, assessment_type, total_questions)
        VALUES (?, ?, ?)
    """, (subject_id, assessment_type, total_questions))
    conn.commit()
    assessment_id = cursor.lastrowid
    conn.close()
    return assessment_id


def add_assessment_question(assessment_id: int, question_text: str, question_type: str,
                            correct_answer: str, topic: str, options: str = None,
                            difficulty: str = 'medium', source_type: str = None,
                            source_id: int = None, marks: int = 1) -> int:
    """Add a question to an assessment. Returns question ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_questions
        (assessment_id, question_text, question_type, correct_answer, topic,
         options, difficulty, source_type, source_id, marks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (assessment_id, question_text, question_type, correct_answer, topic,
          options, difficulty, source_type, source_id, marks))
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id


def record_response(assessment_id: int, question_id: int, student_answer: str,
                    is_correct: bool, marks_awarded: int = 0, time_taken: int = None,
                    confidence: int = None, ai_evaluation: str = None) -> int:
    """Record a student's response to an assessment question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_responses
        (assessment_id, question_id, student_answer, is_correct, marks_awarded,
         time_taken_seconds, confidence_level, ai_evaluation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (assessment_id, question_id, student_answer, 1 if is_correct else 0,
          marks_awarded, time_taken, confidence, ai_evaluation))
    conn.commit()
    response_id = cursor.lastrowid

    # Update assessment progress
    cursor.execute("""
        UPDATE knowledge_assessments
        SET questions_answered = questions_answered + 1,
            correct_answers = correct_answers + ?
        WHERE id = ?
    """, (1 if is_correct else 0, assessment_id))
    conn.commit()
    conn.close()
    return response_id


def complete_assessment(assessment_id: int, ai_feedback: str = None):
    """Mark an assessment as completed and calculate final score."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get assessment data
    cursor.execute("""
        SELECT total_questions, correct_answers, started_at
        FROM knowledge_assessments WHERE id = ?
    """, (assessment_id,))
    assessment = cursor.fetchone()

    if assessment:
        score_pct = (assessment['correct_answers'] / assessment['total_questions'] * 100
                     if assessment['total_questions'] > 0 else 0)

        # Calculate time taken
        started = datetime.fromisoformat(assessment['started_at'])
        time_taken = int((datetime.now() - started).total_seconds())

        cursor.execute("""
            UPDATE knowledge_assessments
            SET status = 'completed',
                score_percentage = ?,
                time_taken_seconds = ?,
                completed_at = CURRENT_TIMESTAMP,
                ai_feedback = ?
            WHERE id = ?
        """, (score_pct, time_taken, ai_feedback, assessment_id))
        conn.commit()

    conn.close()


def get_assessment_by_id(assessment_id: int) -> dict:
    """Get full assessment details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ka.*, s.name as subject_name
        FROM knowledge_assessments ka
        JOIN subjects s ON ka.subject_id = s.id
        WHERE ka.id = ?
    """, (assessment_id,))
    assessment = cursor.fetchone()
    conn.close()
    return row_to_dict(assessment)


def get_assessments_by_subject(subject_id: int = None, limit: int = 20) -> list:
    """Get recent assessments, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT ka.*, s.name as subject_name
            FROM knowledge_assessments ka
            JOIN subjects s ON ka.subject_id = s.id
            WHERE ka.subject_id = ?
            ORDER BY ka.started_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT ka.*, s.name as subject_name
            FROM knowledge_assessments ka
            JOIN subjects s ON ka.subject_id = s.id
            ORDER BY ka.started_at DESC
            LIMIT ?
        """, (limit,))
    assessments = cursor.fetchall()
    conn.close()
    return rows_to_dicts(assessments)


def get_assessment_questions(assessment_id: int) -> list:
    """Get all questions for an assessment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assessment_questions
        WHERE assessment_id = ?
        ORDER BY id
    """, (assessment_id,))
    questions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(questions)


def get_unanswered_questions(assessment_id: int) -> list:
    """Get questions not yet answered in an assessment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT aq.* FROM assessment_questions aq
        LEFT JOIN assessment_responses ar ON aq.id = ar.question_id
        WHERE aq.assessment_id = ? AND ar.id IS NULL
        ORDER BY aq.id
    """, (assessment_id,))
    questions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(questions)


def get_assessment_responses(assessment_id: int) -> list:
    """Get all responses for an assessment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ar.*, aq.question_text, aq.correct_answer, aq.topic
        FROM assessment_responses ar
        JOIN assessment_questions aq ON ar.question_id = aq.id
        WHERE ar.assessment_id = ?
        ORDER BY ar.responded_at
    """, (assessment_id,))
    responses = cursor.fetchall()
    conn.close()
    return rows_to_dicts(responses)


# =============================================================================
# TOPIC MASTERY FUNCTIONS
# =============================================================================

def update_topic_mastery(subject_id: int, topic: str, is_correct: bool):
    """Update mastery level for a topic after an assessment question."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if topic exists
    cursor.execute("""
        SELECT * FROM topic_mastery
        WHERE subject_id = ? AND topic = ?
    """, (subject_id, topic))
    existing = cursor.fetchone()

    if existing:
        # Update existing
        new_total = existing['total_attempts'] + 1
        new_correct = existing['correct_attempts'] + (1 if is_correct else 0)
        new_mastery = (new_correct / new_total) * 100

        # Calculate trend (compare with previous)
        old_mastery = existing['mastery_level']
        if new_mastery > old_mastery + 5:
            trend = 'improving'
        elif new_mastery < old_mastery - 5:
            trend = 'declining'
        else:
            trend = 'stable'

        cursor.execute("""
            UPDATE topic_mastery
            SET total_attempts = ?,
                correct_attempts = ?,
                mastery_level = ?,
                trend = ?,
                last_assessed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE subject_id = ? AND topic = ?
        """, (new_total, new_correct, new_mastery, trend, subject_id, topic))
    else:
        # Insert new
        mastery = 100 if is_correct else 0
        cursor.execute("""
            INSERT INTO topic_mastery
            (subject_id, topic, mastery_level, total_attempts, correct_attempts, last_assessed_at)
            VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP)
        """, (subject_id, topic, mastery, 1 if is_correct else 0))

    conn.commit()
    conn.close()


def get_topic_mastery(subject_id: int = None) -> list:
    """Get mastery levels for all topics, optionally filtered by subject."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            WHERE tm.subject_id = ?
            ORDER BY tm.mastery_level ASC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            ORDER BY tm.mastery_level ASC
        """)
    mastery = cursor.fetchall()
    conn.close()
    return rows_to_dicts(mastery)


def get_weak_topics_from_mastery(subject_id: int = None, threshold: float = 60.0, limit: int = 10) -> list:
    """Get topics below mastery threshold (weak areas)."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            WHERE tm.subject_id = ? AND tm.mastery_level < ?
            ORDER BY tm.mastery_level ASC
            LIMIT ?
        """, (subject_id, threshold, limit))
    else:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            WHERE tm.mastery_level < ?
            ORDER BY tm.mastery_level ASC
            LIMIT ?
        """, (threshold, limit))
    topics = cursor.fetchall()
    conn.close()
    return rows_to_dicts(topics)


def get_strong_topics(subject_id: int = None, threshold: float = 80.0, limit: int = 10) -> list:
    """Get topics above mastery threshold (strengths)."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            WHERE tm.subject_id = ? AND tm.mastery_level >= ?
            ORDER BY tm.mastery_level DESC
            LIMIT ?
        """, (subject_id, threshold, limit))
    else:
        cursor.execute("""
            SELECT tm.*, s.name as subject_name
            FROM topic_mastery tm
            JOIN subjects s ON tm.subject_id = s.id
            WHERE tm.mastery_level >= ?
            ORDER BY tm.mastery_level DESC
            LIMIT ?
        """, (threshold, limit))
    topics = cursor.fetchall()
    conn.close()
    return rows_to_dicts(topics)


# =============================================================================
# GAP ANALYSIS FUNCTIONS
# =============================================================================

def sync_exam_requirements_from_papers(subject_id: int = None):
    """Sync exam requirements table from paper_questions data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get topic frequencies from past papers
    if subject_id:
        cursor.execute("""
            SELECT pp.subject_id, pq.topic, COUNT(*) as frequency,
                   AVG(pq.max_marks) as avg_marks, MAX(pp.year) as last_year
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            WHERE pp.subject_id = ? AND pq.topic IS NOT NULL AND pq.topic != ''
            GROUP BY pp.subject_id, pq.topic
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT pp.subject_id, pq.topic, COUNT(*) as frequency,
                   AVG(pq.max_marks) as avg_marks, MAX(pp.year) as last_year
            FROM paper_questions pq
            JOIN past_papers pp ON pq.paper_id = pp.id
            WHERE pq.topic IS NOT NULL AND pq.topic != ''
            GROUP BY pp.subject_id, pq.topic
        """)

    topics = cursor.fetchall()

    for topic_data in topics:
        # Determine importance based on frequency
        freq = topic_data['frequency']
        if freq >= 5:
            importance = 'critical'
        elif freq >= 3:
            importance = 'high'
        elif freq >= 2:
            importance = 'medium'
        else:
            importance = 'low'

        # Upsert into exam_requirements
        cursor.execute("""
            INSERT INTO exam_requirements (subject_id, topic, frequency, typical_marks, importance_level, last_appeared_year)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(subject_id, topic) DO UPDATE SET
                frequency = excluded.frequency,
                typical_marks = excluded.typical_marks,
                importance_level = excluded.importance_level,
                last_appeared_year = excluded.last_appeared_year
        """, (topic_data['subject_id'], topic_data['topic'], freq,
              int(topic_data['avg_marks']) if topic_data['avg_marks'] else None,
              importance, topic_data['last_year']))

    conn.commit()
    conn.close()


def get_exam_requirements(subject_id: int = None) -> list:
    """Get exam topic requirements."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT er.*, s.name as subject_name
            FROM exam_requirements er
            JOIN subjects s ON er.subject_id = s.id
            WHERE er.subject_id = ?
            ORDER BY er.frequency DESC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT er.*, s.name as subject_name
            FROM exam_requirements er
            JOIN subjects s ON er.subject_id = s.id
            ORDER BY er.frequency DESC
        """)
    requirements = cursor.fetchall()
    conn.close()
    return rows_to_dicts(requirements)


def get_knowledge_gaps(subject_id: int = None) -> list:
    """
    Compare topic_mastery against exam_requirements to identify gaps.
    Returns topics required by exam but not mastered by student.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT er.topic, er.frequency, er.importance_level, er.subject_id,
                   COALESCE(tm.mastery_level, 0) as mastery_level,
                   COALESCE(tm.total_attempts, 0) as attempts,
                   s.name as subject_name
            FROM exam_requirements er
            JOIN subjects s ON er.subject_id = s.id
            LEFT JOIN topic_mastery tm ON er.subject_id = tm.subject_id AND er.topic = tm.topic
            WHERE er.subject_id = ?
              AND (tm.mastery_level IS NULL OR tm.mastery_level < 70)
            ORDER BY er.frequency DESC, COALESCE(tm.mastery_level, 0) ASC
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT er.topic, er.frequency, er.importance_level, er.subject_id,
                   COALESCE(tm.mastery_level, 0) as mastery_level,
                   COALESCE(tm.total_attempts, 0) as attempts,
                   s.name as subject_name
            FROM exam_requirements er
            JOIN subjects s ON er.subject_id = s.id
            LEFT JOIN topic_mastery tm ON er.subject_id = tm.subject_id AND er.topic = tm.topic
            WHERE tm.mastery_level IS NULL OR tm.mastery_level < 70
            ORDER BY er.frequency DESC, COALESCE(tm.mastery_level, 0) ASC
        """)

    gaps = cursor.fetchall()
    conn.close()
    return rows_to_dicts(gaps)


def get_coverage_stats(subject_id: int = None) -> dict:
    """Calculate coverage statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total exam topics
    if subject_id:
        cursor.execute("SELECT COUNT(*) as count FROM exam_requirements WHERE subject_id = ?", (subject_id,))
    else:
        cursor.execute("SELECT COUNT(*) as count FROM exam_requirements")
    total_exam_topics = cursor.fetchone()['count']

    # Topics assessed (have mastery record)
    if subject_id:
        cursor.execute("""
            SELECT COUNT(DISTINCT tm.topic) as count
            FROM topic_mastery tm
            JOIN exam_requirements er ON tm.subject_id = er.subject_id AND tm.topic = er.topic
            WHERE tm.subject_id = ?
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT COUNT(DISTINCT tm.topic) as count
            FROM topic_mastery tm
            JOIN exam_requirements er ON tm.subject_id = er.subject_id AND tm.topic = er.topic
        """)
    topics_assessed = cursor.fetchone()['count']

    # Topics mastered (>= 70%)
    if subject_id:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM topic_mastery tm
            JOIN exam_requirements er ON tm.subject_id = er.subject_id AND tm.topic = er.topic
            WHERE tm.subject_id = ? AND tm.mastery_level >= 70
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM topic_mastery tm
            JOIN exam_requirements er ON tm.subject_id = er.subject_id AND tm.topic = er.topic
            WHERE tm.mastery_level >= 70
        """)
    topics_mastered = cursor.fetchone()['count']

    conn.close()

    coverage_pct = (topics_mastered / total_exam_topics * 100) if total_exam_topics > 0 else 0

    return {
        'total_exam_topics': total_exam_topics,
        'topics_assessed': topics_assessed,
        'topics_mastered': topics_mastered,
        'coverage_percentage': coverage_pct
    }


# =============================================================================
# ASSESSMENT ANALYTICS FUNCTIONS
# =============================================================================

def get_assessment_stats(subject_id: int = None, days: int = 30) -> dict:
    """Get aggregate assessment statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    if subject_id:
        cursor.execute("""
            SELECT COUNT(*) as total_assessments,
                   SUM(questions_answered) as total_questions,
                   AVG(score_percentage) as avg_score,
                   SUM(correct_answers) as total_correct,
                   SUM(questions_answered) as total_answered
            FROM knowledge_assessments
            WHERE subject_id = ? AND status = 'completed' AND started_at >= ?
        """, (subject_id, cutoff))
    else:
        cursor.execute("""
            SELECT COUNT(*) as total_assessments,
                   SUM(questions_answered) as total_questions,
                   AVG(score_percentage) as avg_score,
                   SUM(correct_answers) as total_correct,
                   SUM(questions_answered) as total_answered
            FROM knowledge_assessments
            WHERE status = 'completed' AND started_at >= ?
        """, (cutoff,))

    stats = cursor.fetchone()
    conn.close()

    total_answered = stats['total_answered'] or 0
    total_correct = stats['total_correct'] or 0
    accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0

    return {
        'total_assessments': stats['total_assessments'] or 0,
        'total_questions': stats['total_questions'] or 0,
        'avg_score': stats['avg_score'] or 0,
        'accuracy': accuracy
    }


def get_assessment_progress_over_time(subject_id: int = None, limit: int = 20) -> list:
    """Get assessment scores over time to show progress."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT id, score_percentage, started_at, assessment_type, subject_id
            FROM knowledge_assessments
            WHERE subject_id = ? AND status = 'completed'
            ORDER BY started_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT id, score_percentage, started_at, assessment_type, subject_id
            FROM knowledge_assessments
            WHERE status = 'completed'
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))

    progress = cursor.fetchall()
    conn.close()
    return rows_to_dicts(progress)


def get_performance_by_question_type(subject_id: int = None) -> list:
    """Get performance by question type."""
    conn = get_connection()
    cursor = conn.cursor()

    if subject_id:
        cursor.execute("""
            SELECT aq.question_type,
                   COUNT(*) as total,
                   SUM(ar.is_correct) as correct
            FROM assessment_responses ar
            JOIN assessment_questions aq ON ar.question_id = aq.id
            JOIN knowledge_assessments ka ON ar.assessment_id = ka.id
            WHERE ka.subject_id = ?
            GROUP BY aq.question_type
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT aq.question_type,
                   COUNT(*) as total,
                   SUM(ar.is_correct) as correct
            FROM assessment_responses ar
            JOIN assessment_questions aq ON ar.question_id = aq.id
            GROUP BY aq.question_type
        """)

    results = cursor.fetchall()
    conn.close()

    performance = []
    for r in results:
        pct = (r['correct'] / r['total'] * 100) if r['total'] > 0 else 0
        performance.append({
            'question_type': r['question_type'],
            'total': r['total'],
            'correct': r['correct'],
            'percentage': pct
        })

    return performance


def get_available_topics_for_subject(subject_id: int) -> list:
    """Get available topics for assessment from past papers and flashcards."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get topics from past papers
    cursor.execute("""
        SELECT DISTINCT pq.topic
        FROM paper_questions pq
        JOIN past_papers pp ON pq.paper_id = pp.id
        WHERE pp.subject_id = ? AND pq.topic IS NOT NULL AND pq.topic != ''
    """, (subject_id,))
    paper_topics = [r['topic'] for r in cursor.fetchall()]

    # Get topics from flashcards
    cursor.execute("""
        SELECT DISTINCT topic
        FROM flashcards
        WHERE subject_id = ? AND topic IS NOT NULL AND topic != ''
    """, (subject_id,))
    flashcard_topics = [r['topic'] for r in cursor.fetchall()]

    conn.close()

    # Combine and deduplicate
    all_topics = list(set(paper_topics + flashcard_topics))
    return sorted(all_topics)


# =============================================================================
# STUDY SCHEDULE FUNCTIONS
# =============================================================================

def create_study_schedule(name: str, start_date: date, end_date: date,
                          generation_params: dict = None) -> int:
    """Create a new study schedule. Returns the schedule ID."""
    import json
    conn = get_connection()
    cursor = conn.cursor()

    # Deactivate any existing active schedules
    cursor.execute("UPDATE study_schedules SET is_active = 0 WHERE is_active = 1")

    params_json = json.dumps(generation_params) if generation_params else None
    cursor.execute("""
        INSERT INTO study_schedules (name, start_date, end_date, generation_params)
        VALUES (?, ?, ?, ?)
    """, (name, start_date.isoformat(), end_date.isoformat(), params_json))
    conn.commit()
    schedule_id = cursor.lastrowid
    conn.close()
    return schedule_id


def get_active_schedule() -> dict:
    """Get the currently active study schedule with sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM study_schedules WHERE is_active = 1
    """)
    schedule = cursor.fetchone()
    conn.close()
    if schedule:
        return row_to_dict(schedule)
    return None


def get_schedule_by_id(schedule_id: int) -> dict:
    """Get a specific schedule with all its sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_schedules WHERE id = ?", (schedule_id,))
    schedule = cursor.fetchone()
    conn.close()
    return row_to_dict(schedule)


def get_all_schedules(include_inactive: bool = False) -> list:
    """Get all schedules, optionally including inactive ones."""
    conn = get_connection()
    cursor = conn.cursor()
    if include_inactive:
        cursor.execute("SELECT * FROM study_schedules ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM study_schedules WHERE is_active = 1 ORDER BY created_at DESC")
    schedules = cursor.fetchall()
    conn.close()
    return rows_to_dicts(schedules)


def deactivate_schedule(schedule_id: int):
    """Mark a schedule as inactive."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE study_schedules SET is_active = 0 WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()


def update_schedule_hours(schedule_id: int, total_hours: int):
    """Update the total planned hours for a schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE study_schedules
        SET total_hours_planned = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (total_hours, schedule_id))
    conn.commit()
    conn.close()


def add_schedule_session(schedule_id: int, subject_id: int, scheduled_date: date,
                         duration_minutes: int, topic: str = None,
                         priority_score: float = None, reason: str = None,
                         start_time: str = None) -> int:
    """Add a study session to a schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO schedule_sessions
        (schedule_id, subject_id, scheduled_date, duration_minutes, topic,
         priority_score, reason, start_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (schedule_id, subject_id, scheduled_date.isoformat(), duration_minutes,
          topic, priority_score, reason, start_time))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def get_sessions_for_date(schedule_id: int, target_date: date) -> list:
    """Get all sessions scheduled for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.*, s.name as subject_name, s.colour as subject_colour
        FROM schedule_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.schedule_id = ? AND ss.scheduled_date = ?
        ORDER BY ss.start_time, ss.priority_score DESC
    """, (schedule_id, target_date.isoformat()))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def get_sessions_for_week(schedule_id: int, week_start: date) -> list:
    """Get all sessions for a week starting from week_start."""
    week_end = week_start + timedelta(days=6)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.*, s.name as subject_name, s.colour as subject_colour
        FROM schedule_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.schedule_id = ? AND ss.scheduled_date BETWEEN ? AND ?
        ORDER BY ss.scheduled_date, ss.start_time, ss.priority_score DESC
    """, (schedule_id, week_start.isoformat(), week_end.isoformat()))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def get_all_schedule_sessions(schedule_id: int) -> list:
    """Get all sessions for a schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.*, s.name as subject_name, s.colour as subject_colour
        FROM schedule_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.schedule_id = ?
        ORDER BY ss.scheduled_date, ss.start_time
    """, (schedule_id,))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def mark_session_complete(session_id: int, actual_duration: int = None, notes: str = None):
    """Mark a session as completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedule_sessions
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
            actual_duration_minutes = ?, notes = ?
        WHERE id = ?
    """, (actual_duration, notes, session_id))
    conn.commit()
    conn.close()


def mark_session_missed(session_id: int):
    """Mark a session as missed (triggers rescheduling)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedule_sessions
        SET status = 'missed'
        WHERE id = ?
    """, (session_id,))
    conn.commit()
    conn.close()


def reschedule_session(session_id: int, new_date: date, new_time: str = None,
                       reason: str = None):
    """Reschedule a session to a new date/time."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get current session data for logging
    cursor.execute("SELECT * FROM schedule_sessions WHERE id = ?", (session_id,))
    old_session = row_to_dict(cursor.fetchone())

    # Update session
    cursor.execute("""
        UPDATE schedule_sessions
        SET scheduled_date = ?, start_time = ?, status = 'rescheduled'
        WHERE id = ?
    """, (new_date.isoformat(), new_time, session_id))

    # Log the adjustment
    if old_session:
        import json
        cursor.execute("""
            INSERT INTO schedule_adjustments
            (schedule_id, session_id, adjustment_type, old_value, new_value, reason)
            VALUES (?, ?, 'rescheduled', ?, ?, ?)
        """, (old_session['schedule_id'], session_id,
              json.dumps({'date': old_session['scheduled_date'], 'time': old_session['start_time']}),
              json.dumps({'date': new_date.isoformat(), 'time': new_time}),
              reason or 'Session rescheduled'))

    conn.commit()
    conn.close()


def log_schedule_adjustment(schedule_id: int, adjustment_type: str,
                            reason: str, session_id: int = None,
                            old_value: dict = None, new_value: dict = None):
    """Log an adjustment for transparency."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO schedule_adjustments
        (schedule_id, session_id, adjustment_type, old_value, new_value, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (schedule_id, session_id, adjustment_type,
          json.dumps(old_value) if old_value else None,
          json.dumps(new_value) if new_value else None,
          reason))
    conn.commit()
    conn.close()


def get_schedule_adjustments(schedule_id: int, limit: int = 20) -> list:
    """Get recent adjustments to a schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM schedule_adjustments
        WHERE schedule_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (schedule_id, limit))
    adjustments = cursor.fetchall()
    conn.close()
    return rows_to_dicts(adjustments)


def delete_schedule(schedule_id: int):
    """Delete a schedule and all its sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule_adjustments WHERE schedule_id = ?", (schedule_id,))
    cursor.execute("DELETE FROM schedule_sessions WHERE schedule_id = ?", (schedule_id,))
    cursor.execute("DELETE FROM study_schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()


def get_session_stats(schedule_id: int) -> dict:
    """Get statistics for a schedule's sessions."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total sessions
    cursor.execute("""
        SELECT COUNT(*) as total FROM schedule_sessions WHERE schedule_id = ?
    """, (schedule_id,))
    total = cursor.fetchone()['total']

    # Completed
    cursor.execute("""
        SELECT COUNT(*) as completed FROM schedule_sessions
        WHERE schedule_id = ? AND status = 'completed'
    """, (schedule_id,))
    completed = cursor.fetchone()['completed']

    # Missed
    cursor.execute("""
        SELECT COUNT(*) as missed FROM schedule_sessions
        WHERE schedule_id = ? AND status = 'missed'
    """, (schedule_id,))
    missed = cursor.fetchone()['missed']

    # Pending
    cursor.execute("""
        SELECT COUNT(*) as pending FROM schedule_sessions
        WHERE schedule_id = ? AND status = 'pending'
    """, (schedule_id,))
    pending = cursor.fetchone()['pending']

    # Total planned minutes
    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0) as planned_minutes
        FROM schedule_sessions WHERE schedule_id = ?
    """, (schedule_id,))
    planned_minutes = cursor.fetchone()['planned_minutes']

    # Actual completed minutes
    cursor.execute("""
        SELECT COALESCE(SUM(COALESCE(actual_duration_minutes, duration_minutes)), 0) as completed_minutes
        FROM schedule_sessions
        WHERE schedule_id = ? AND status = 'completed'
    """, (schedule_id,))
    completed_minutes = cursor.fetchone()['completed_minutes']

    conn.close()

    return {
        'total': total,
        'completed': completed,
        'missed': missed,
        'pending': pending,
        'planned_minutes': planned_minutes,
        'completed_minutes': completed_minutes,
        'completion_rate': (completed / total * 100) if total > 0 else 0
    }


# =============================================================================
# STUDY PREFERENCES FUNCTIONS
# =============================================================================

def get_study_preference(key: str, default: str = None) -> str:
    """Get a study preference value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT preference_value FROM study_preferences WHERE preference_key = ?
    """, (key,))
    row = cursor.fetchone()
    conn.close()
    return row['preference_value'] if row else default


def set_study_preference(key: str, value: str):
    """Set a study preference value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO study_preferences (preference_key, preference_value)
        VALUES (?, ?)
        ON CONFLICT(preference_key) DO UPDATE SET
        preference_value = excluded.preference_value,
        updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    conn.commit()
    conn.close()


def get_all_study_preferences() -> dict:
    """Get all study preferences as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preference_key, preference_value FROM study_preferences")
    rows = cursor.fetchall()
    conn.close()
    return {r['preference_key']: r['preference_value'] for r in rows}


# =============================================================================
# SMART RECOMMENDATION FUNCTIONS
# =============================================================================

def calculate_topic_priority(subject_id: int, topic: str, exam_days: int = None,
                             mastery_level: float = None, trend: str = None,
                             importance: str = None, days_since_review: int = None) -> float:
    """
    Calculate priority score for a topic (0-100 scale).

    Factors:
    - Exam urgency (35%): closer exams = higher priority
    - Knowledge gap (30%): lower mastery = higher priority
    - Topic importance (20%): from exam requirements
    - Review recency (15%): longer since review = higher priority
    """
    score = 0.0

    # 1. Exam Urgency (35%)
    if exam_days is not None:
        if exam_days <= 7:
            urgency_score = 100
        elif exam_days <= 14:
            urgency_score = 80
        elif exam_days <= 30:
            urgency_score = 60
        elif exam_days <= 60:
            urgency_score = 40
        else:
            urgency_score = 20
        score += urgency_score * 0.35

    # 2. Knowledge Gap (30%)
    if mastery_level is not None:
        if mastery_level < 30:
            gap_score = 100
        elif mastery_level < 50:
            gap_score = 80
        elif mastery_level < 70:
            gap_score = 60
        elif mastery_level < 85:
            gap_score = 30
        else:
            gap_score = 10
        # Bonus for declining trend
        if trend == 'declining':
            gap_score = min(100, gap_score + 20)
        score += gap_score * 0.30

    # 3. Topic Importance (20%)
    importance_scores = {'critical': 100, 'high': 75, 'medium': 50, 'low': 25}
    importance_score = importance_scores.get(importance, 50)
    score += importance_score * 0.20

    # 4. Review Recency (15%)
    if days_since_review is not None:
        if days_since_review is None or days_since_review > 30:
            recency_score = 100
        elif days_since_review > 14:
            recency_score = 80
        elif days_since_review > 7:
            recency_score = 50
        elif days_since_review > 3:
            recency_score = 30
        else:
            recency_score = 10
        score += recency_score * 0.15

    return round(score, 1)


def get_schedule_generation_data() -> dict:
    """
    Gather all data needed for schedule generation.
    Returns comprehensive data about exams, topics, mastery, and gaps.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    # Get all subjects
    subjects = get_all_subjects()

    # Get all upcoming exams with days until
    cursor.execute("""
        SELECT e.*, s.name as subject_name, s.colour as subject_colour
        FROM exams e
        JOIN subjects s ON e.subject_id = s.id
        WHERE e.exam_date >= ?
        ORDER BY e.exam_date
    """, (today.isoformat(),))
    exams = rows_to_dicts(cursor.fetchall())
    for exam in exams:
        exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d').date()
        exam['days_until'] = (exam_date - today).days

    # Get all topic mastery data
    cursor.execute("""
        SELECT tm.*, s.name as subject_name
        FROM topic_mastery tm
        JOIN subjects s ON tm.subject_id = s.id
        ORDER BY tm.mastery_level ASC
    """)
    mastery_data = rows_to_dicts(cursor.fetchall())

    # Get exam requirements (important topics)
    cursor.execute("""
        SELECT er.*, s.name as subject_name
        FROM exam_requirements er
        JOIN subjects s ON er.subject_id = s.id
        ORDER BY er.frequency DESC
    """)
    requirements = rows_to_dicts(cursor.fetchall())

    # Get flashcard due counts by subject
    flashcard_counts = {}
    for subject in subjects:
        cursor.execute("""
            SELECT COUNT(*) as due_count FROM flashcards
            WHERE subject_id = ? AND next_review <= ?
        """, (subject['id'], today.isoformat()))
        flashcard_counts[subject['id']] = cursor.fetchone()['due_count']

    # Get knowledge gaps (topics required but not mastered)
    gaps = get_knowledge_gaps_all()

    conn.close()

    return {
        'subjects': subjects,
        'exams': exams,
        'mastery_data': mastery_data,
        'requirements': requirements,
        'flashcard_counts': flashcard_counts,
        'knowledge_gaps': gaps,
        'today': today.isoformat()
    }


def get_knowledge_gaps_all() -> list:
    """Get knowledge gaps across all subjects."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            er.subject_id,
            er.topic,
            er.frequency,
            er.importance_level,
            COALESCE(tm.mastery_level, 0) as mastery_level,
            COALESCE(tm.total_attempts, 0) as attempts,
            tm.trend,
            tm.last_assessed_at,
            s.name as subject_name
        FROM exam_requirements er
        JOIN subjects s ON er.subject_id = s.id
        LEFT JOIN topic_mastery tm ON er.subject_id = tm.subject_id AND er.topic = tm.topic
        WHERE COALESCE(tm.mastery_level, 0) < 70
        ORDER BY er.frequency DESC, COALESCE(tm.mastery_level, 0) ASC
    """)
    gaps = rows_to_dicts(cursor.fetchall())
    conn.close()
    return gaps


def get_smart_recommendation(available_minutes: int = 30) -> dict:
    """
    Get intelligent study recommendation considering all factors.

    Returns the single best topic to study with reasoning.
    """
    today = date.today()
    conn = get_connection()
    cursor = conn.cursor()

    # Gather all relevant data
    data = get_schedule_generation_data()

    recommendations = []

    # Process each subject
    for subject in data['subjects']:
        subject_id = subject['id']

        # Find the nearest exam for this subject
        subject_exams = [e for e in data['exams'] if e['subject_id'] == subject_id]
        exam_days = subject_exams[0]['days_until'] if subject_exams else None

        # Get knowledge gaps for this subject
        subject_gaps = [g for g in data['knowledge_gaps'] if g['subject_id'] == subject_id]

        # Get flashcard count
        flashcard_due = data['flashcard_counts'].get(subject_id, 0)

        # If there are knowledge gaps, recommend the highest priority gap
        for gap in subject_gaps[:3]:  # Consider top 3 gaps per subject
            # Calculate days since last review
            days_since = None
            if gap.get('last_assessed_at'):
                try:
                    last_date = datetime.strptime(gap['last_assessed_at'][:10], '%Y-%m-%d').date()
                    days_since = (today - last_date).days
                except ValueError:
                    days_since = 30

            priority = calculate_topic_priority(
                subject_id=subject_id,
                topic=gap['topic'],
                exam_days=exam_days,
                mastery_level=gap['mastery_level'],
                trend=gap.get('trend'),
                importance=gap['importance_level'],
                days_since_review=days_since
            )

            # Build reasoning
            reasons = []
            if exam_days is not None and exam_days <= 30:
                reasons.append(f"Exam in {exam_days} days")
            if gap['mastery_level'] < 50:
                reasons.append(f"Mastery at {gap['mastery_level']:.0f}% (needs work)")
            elif gap['mastery_level'] < 70:
                reasons.append(f"Mastery at {gap['mastery_level']:.0f}% (below target)")
            if gap.get('trend') == 'declining':
                reasons.append("Performance declining")
            if gap['importance_level'] in ['critical', 'high']:
                reasons.append(f"{gap['importance_level'].title()} exam topic")
            if days_since and days_since > 7:
                reasons.append(f"Last reviewed {days_since} days ago")

            recommendations.append({
                'subject_id': subject_id,
                'subject_name': gap['subject_name'],
                'subject_colour': subject.get('colour', '#3498db'),
                'topic': gap['topic'],
                'priority_score': priority,
                'mastery_level': gap['mastery_level'],
                'reasons': reasons,
                'estimated_minutes': min(available_minutes, 45),
                'action_type': 'study_gap',
                'exam_days': exam_days
            })

        # Also consider flashcard review if many due
        if flashcard_due >= 10:
            fc_priority = 50 + min(25, flashcard_due)
            if exam_days and exam_days <= 14:
                fc_priority += 20
            recommendations.append({
                'subject_id': subject_id,
                'subject_name': subject['name'],
                'subject_colour': subject.get('colour', '#3498db'),
                'topic': 'Flashcard Review',
                'priority_score': fc_priority,
                'mastery_level': None,
                'reasons': [f"{flashcard_due} flashcards due for review"],
                'estimated_minutes': min(available_minutes, 20),
                'action_type': 'flashcard_review',
                'flashcard_count': flashcard_due,
                'exam_days': exam_days
            })

    conn.close()

    # Sort by priority and return top recommendation
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)

    if recommendations:
        top = recommendations[0]
        return {
            'recommendation': top,
            'alternatives': recommendations[1:4]  # Next 3 alternatives
        }

    return {
        'recommendation': None,
        'alternatives': []
    }


def get_unified_recommendations(available_time: int = 30, limit: int = 5) -> dict:
    """
    Unified recommendation engine used by Dashboard, Study Schedule, and AI Tools.

    Combines all factors: exam dates, knowledge gaps, flashcard due counts,
    homework, mastery levels, and review schedules.

    Returns:
        {
            'top': The single best recommendation (dict or None),
            'alternatives': List of up to (limit-1) additional recommendations,
            'summary': Brief text summary of what to do next
        }
    """
    # Use the smart recommendation engine as the base
    result = get_smart_recommendation(available_time)

    if result['recommendation']:
        top = result['recommendation']

        # Generate summary text
        summary = f"Study {top['topic']}"
        if top.get('exam_days') and top['exam_days'] <= 30:
            summary += f" (exam in {top['exam_days']} days)"
        elif top.get('mastery_level') and top['mastery_level'] < 50:
            summary += f" (mastery: {top['mastery_level']:.0f}%)"

        return {
            'top': top,
            'alternatives': result['alternatives'][:limit-1],
            'summary': summary
        }

    # If no smart recommendations, fall back to study_recommendations for urgent items
    fallback = get_study_recommendations(limit=limit)
    if fallback:
        top_fb = fallback[0]
        # Convert to unified format
        top = {
            'subject_id': top_fb.get('subject_id'),
            'subject_name': top_fb['subject_name'],
            'subject_colour': top_fb.get('subject_colour', '#3498db'),
            'topic': top_fb['title'],
            'priority_score': top_fb['priority_score'],
            'mastery_level': None,
            'reasons': [top_fb['reason']],
            'estimated_minutes': available_time,
            'action_type': top_fb['type'],
            'exam_days': None
        }
        alternatives = []
        for alt in fallback[1:limit]:
            alternatives.append({
                'subject_id': alt.get('subject_id'),
                'subject_name': alt['subject_name'],
                'subject_colour': alt.get('subject_colour', '#3498db'),
                'topic': alt['title'],
                'priority_score': alt['priority_score'],
                'mastery_level': None,
                'reasons': [alt['reason']],
                'estimated_minutes': available_time,
                'action_type': alt['type'],
                'exam_days': None
            })
        return {
            'top': top,
            'alternatives': alternatives,
            'summary': f"{top_fb['title']} - {top_fb['reason']}"
        }

    return {
        'top': None,
        'alternatives': [],
        'summary': "You're all caught up!"
    }


def get_subject_study_summary() -> list:
    """Get summary of study status per subject for schedule overview."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    subjects = get_all_subjects()
    summary = []

    for subject in subjects:
        # Get nearest exam
        cursor.execute("""
            SELECT exam_date, name FROM exams
            WHERE subject_id = ? AND exam_date >= ?
            ORDER BY exam_date LIMIT 1
        """, (subject['id'], today.isoformat()))
        exam = cursor.fetchone()
        exam_days = None
        exam_name = None
        if exam:
            exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d').date()
            exam_days = (exam_date - today).days
            exam_name = exam['name']

        # Get average mastery
        cursor.execute("""
            SELECT AVG(mastery_level) as avg_mastery
            FROM topic_mastery WHERE subject_id = ?
        """, (subject['id'],))
        mastery = cursor.fetchone()
        avg_mastery = mastery['avg_mastery'] if mastery['avg_mastery'] else 0

        # Get knowledge gap count
        cursor.execute("""
            SELECT COUNT(*) as gap_count
            FROM exam_requirements er
            LEFT JOIN topic_mastery tm ON er.subject_id = tm.subject_id AND er.topic = tm.topic
            WHERE er.subject_id = ? AND COALESCE(tm.mastery_level, 0) < 70
        """, (subject['id'],))
        gaps = cursor.fetchone()['gap_count']

        # Get flashcards due
        cursor.execute("""
            SELECT COUNT(*) as due FROM flashcards
            WHERE subject_id = ? AND next_review <= ?
        """, (subject['id'], today.isoformat()))
        flashcards_due = cursor.fetchone()['due']

        summary.append({
            'subject_id': subject['id'],
            'subject_name': subject['name'],
            'subject_colour': subject.get('colour', '#3498db'),
            'exam_days': exam_days,
            'exam_name': exam_name,
            'avg_mastery': round(avg_mastery, 1),
            'knowledge_gaps': gaps,
            'flashcards_due': flashcards_due
        })

    conn.close()
    return summary


def generate_schedule_sessions(schedule_id: int, start_date: date, end_date: date,
                               daily_minutes: int = 120, session_length: int = 30,
                               subject_ids: list = None) -> int:
    """
    Generate study sessions for a schedule based on priorities.

    Returns the number of sessions created.
    """
    data = get_schedule_generation_data()
    subjects = data['subjects']

    if subject_ids:
        subjects = [s for s in subjects if s['id'] in subject_ids]

    # Build priority queue of topics to schedule
    topic_queue = []

    for subject in subjects:
        subject_id = subject['id']

        # Find exam days
        subject_exams = [e for e in data['exams'] if e['subject_id'] == subject_id]
        exam_days = subject_exams[0]['days_until'] if subject_exams else 90

        # Get gaps for this subject
        subject_gaps = [g for g in data['knowledge_gaps'] if g['subject_id'] == subject_id]

        for gap in subject_gaps:
            days_since = None
            if gap.get('last_assessed_at'):
                try:
                    last_date = datetime.strptime(gap['last_assessed_at'][:10], '%Y-%m-%d').date()
                    days_since = (start_date - last_date).days
                except ValueError:
                    days_since = 30

            priority = calculate_topic_priority(
                subject_id=subject_id,
                topic=gap['topic'],
                exam_days=exam_days,
                mastery_level=gap['mastery_level'],
                trend=gap.get('trend'),
                importance=gap['importance_level'],
                days_since_review=days_since
            )

            # Determine reason
            reasons = []
            if exam_days <= 14:
                reasons.append(f"Exam in {exam_days} days")
            if gap['mastery_level'] < 50:
                reasons.append(f"Low mastery ({gap['mastery_level']:.0f}%)")
            if gap['importance_level'] == 'critical':
                reasons.append("Critical topic")

            topic_queue.append({
                'subject_id': subject_id,
                'subject_name': subject['name'],
                'topic': gap['topic'],
                'priority': priority,
                'reason': ', '.join(reasons) if reasons else 'Knowledge gap'
            })

        # Add flashcard review if many due
        flashcard_due = data['flashcard_counts'].get(subject_id, 0)
        if flashcard_due >= 5:
            topic_queue.append({
                'subject_id': subject_id,
                'subject_name': subject['name'],
                'topic': 'Flashcard Review',
                'priority': 40 + min(30, flashcard_due),
                'reason': f'{flashcard_due} cards due'
            })

    # Sort by priority
    topic_queue.sort(key=lambda x: x['priority'], reverse=True)

    # Generate sessions for each day
    sessions_created = 0
    current_date = start_date
    sessions_per_day = daily_minutes // session_length
    topic_index = 0

    while current_date <= end_date:
        daily_subject_count = {}  # Track sessions per subject per day

        for _ in range(sessions_per_day):
            if topic_index >= len(topic_queue):
                topic_index = 0  # Cycle through topics

            # Find next topic that doesn't exceed 2 per subject per day
            attempts = 0
            while attempts < len(topic_queue):
                topic = topic_queue[topic_index % len(topic_queue)]
                subject_id = topic['subject_id']

                if daily_subject_count.get(subject_id, 0) < 2:
                    # Add session
                    add_schedule_session(
                        schedule_id=schedule_id,
                        subject_id=subject_id,
                        scheduled_date=current_date,
                        duration_minutes=session_length,
                        topic=topic['topic'],
                        priority_score=topic['priority'],
                        reason=topic['reason']
                    )
                    daily_subject_count[subject_id] = daily_subject_count.get(subject_id, 0) + 1
                    sessions_created += 1
                    topic_index += 1
                    break

                topic_index += 1
                attempts += 1

        current_date += timedelta(days=1)

    # Update schedule with total hours
    total_hours = (sessions_created * session_length) // 60
    update_schedule_hours(schedule_id, total_hours)

    return sessions_created


# =============================================================================
# ADAPTIVE ADJUSTMENT FUNCTIONS
# =============================================================================

def trigger_quiz_adjustment(schedule_id: int, subject_id: int, topic: str,
                            score_percentage: float):
    """
    Adjust schedule based on quiz/assessment results.

    - Score < 50%: Increase session time by 50%
    - Score < 30%: Add extra session within 2 days
    """
    if score_percentage >= 50:
        return  # No adjustment needed

    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    # Find upcoming sessions for this subject/topic
    cursor.execute("""
        SELECT * FROM schedule_sessions
        WHERE schedule_id = ? AND subject_id = ? AND topic = ?
        AND scheduled_date >= ? AND status = 'pending'
        ORDER BY scheduled_date LIMIT 3
    """, (schedule_id, subject_id, topic, today.isoformat()))
    sessions = rows_to_dicts(cursor.fetchall())

    adjustment_made = False

    if score_percentage < 30:
        # Add extra session
        next_date = today + timedelta(days=1)
        add_schedule_session(
            schedule_id=schedule_id,
            subject_id=subject_id,
            scheduled_date=next_date,
            duration_minutes=45,
            topic=topic,
            priority_score=90,
            reason=f'Extra session: quiz score {score_percentage:.0f}%'
        )
        log_schedule_adjustment(
            schedule_id=schedule_id,
            adjustment_type='quiz_result',
            reason=f'Quiz score {score_percentage:.0f}% on {topic} - added extra session',
            new_value={'topic': topic, 'action': 'added_session', 'date': next_date.isoformat()}
        )
        adjustment_made = True

    elif score_percentage < 50 and sessions:
        # Increase first session duration by 50%
        session = sessions[0]
        old_duration = session['duration_minutes']
        new_duration = int(old_duration * 1.5)
        cursor.execute("""
            UPDATE schedule_sessions SET duration_minutes = ?
            WHERE id = ?
        """, (new_duration, session['id']))
        conn.commit()
        log_schedule_adjustment(
            schedule_id=schedule_id,
            session_id=session['id'],
            adjustment_type='quiz_result',
            reason=f'Quiz score {score_percentage:.0f}% on {topic} - increased session time',
            old_value={'duration': old_duration},
            new_value={'duration': new_duration}
        )
        adjustment_made = True

    conn.close()
    return adjustment_made


def trigger_missed_session_adjustment(session_id: int):
    """
    Handle missed session by rescheduling to next available slot.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get session details
    cursor.execute("SELECT * FROM schedule_sessions WHERE id = ?", (session_id,))
    session = row_to_dict(cursor.fetchone())

    if not session:
        conn.close()
        return False

    # Mark as missed
    mark_session_missed(session_id)

    # Find next available date (within 3 days)
    today = date.today()
    for days_ahead in range(1, 4):
        new_date = today + timedelta(days=days_ahead)

        # Check how many sessions on that day
        cursor.execute("""
            SELECT COUNT(*) as count FROM schedule_sessions
            WHERE schedule_id = ? AND scheduled_date = ? AND status = 'pending'
        """, (session['schedule_id'], new_date.isoformat()))

        if cursor.fetchone()['count'] < 4:  # Max 4 sessions per day
            # Create rescheduled session
            new_session_id = add_schedule_session(
                schedule_id=session['schedule_id'],
                subject_id=session['subject_id'],
                scheduled_date=new_date,
                duration_minutes=session['duration_minutes'],
                topic=session['topic'],
                priority_score=session['priority_score'],
                reason=f"Rescheduled from {session['scheduled_date']}"
            )

            log_schedule_adjustment(
                schedule_id=session['schedule_id'],
                session_id=new_session_id,
                adjustment_type='missed_session',
                reason=f"Session missed - rescheduled to {new_date.isoformat()}",
                old_value={'date': session['scheduled_date'], 'session_id': session_id},
                new_value={'date': new_date.isoformat(), 'session_id': new_session_id}
            )

            conn.close()
            return True

    conn.close()
    return False


# =============================================================================
# EXAM TECHNIQUE TRAINER FUNCTIONS
# =============================================================================

def create_technique_session(subject_id: int, session_type: str, question_types: str,
                             total_questions: int, time_limit: int = None) -> int:
    """Create a new technique practice session. Returns session ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO technique_practice_sessions
        (subject_id, session_type, question_types, total_questions, time_limit_seconds)
        VALUES (?, ?, ?, ?, ?)
    """, (subject_id, session_type, question_types, total_questions, time_limit))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def update_technique_session(session_id: int, **kwargs):
    """Update technique session fields."""
    if not kwargs:
        return
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [session_id]
    cursor.execute(f"UPDATE technique_practice_sessions SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def complete_technique_session(session_id: int, time_taken: int, ai_review: str = None):
    """Mark a technique session as completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE technique_practice_sessions
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
            time_taken_seconds = ?, ai_review = ?
        WHERE id = ?
    """, (time_taken, ai_review, session_id))
    conn.commit()
    conn.close()


def get_technique_session(session_id: int) -> dict:
    """Get a technique practice session by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tps.*, s.name as subject_name, s.colour as subject_colour
        FROM technique_practice_sessions tps
        JOIN subjects s ON tps.subject_id = s.id
        WHERE tps.id = ?
    """, (session_id,))
    session = cursor.fetchone()
    conn.close()
    return row_to_dict(session)


def get_recent_technique_sessions(subject_id: int = None, limit: int = 20) -> list:
    """Get recent completed technique practice sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT tps.*, s.name as subject_name, s.colour as subject_colour
            FROM technique_practice_sessions tps
            JOIN subjects s ON tps.subject_id = s.id
            WHERE tps.subject_id = ? AND tps.status = 'completed'
            ORDER BY tps.completed_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT tps.*, s.name as subject_name, s.colour as subject_colour
            FROM technique_practice_sessions tps
            JOIN subjects s ON tps.subject_id = s.id
            WHERE tps.status = 'completed'
            ORDER BY tps.completed_at DESC
            LIMIT ?
        """, (limit,))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def save_technique_response(session_id: int, question_number: int, question_type: str,
                            question_text: str, student_answer: str, correct_answer: str,
                            is_correct: int, marks_awarded: int, max_marks: int,
                            time_taken: int, time_status: str) -> int:
    """Save a response to a technique practice question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO technique_practice_responses
        (session_id, question_number, question_type, question_text, student_answer,
         correct_answer, is_correct, marks_awarded, max_marks, time_taken_seconds, time_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, question_number, question_type, question_text, student_answer,
          correct_answer, is_correct, marks_awarded, max_marks, time_taken, time_status))
    conn.commit()
    response_id = cursor.lastrowid

    # Update session stats
    cursor.execute("""
        UPDATE technique_practice_sessions
        SET questions_answered = questions_answered + 1,
            correct_answers = correct_answers + ?,
            marks_achieved = marks_achieved + ?,
            total_marks = total_marks + ?
        WHERE id = ?
    """, (is_correct, marks_awarded, max_marks, session_id))
    conn.commit()
    conn.close()
    return response_id


def get_technique_responses(session_id: int) -> list:
    """Get all responses for a technique practice session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM technique_practice_responses
        WHERE session_id = ?
        ORDER BY question_number
    """, (session_id,))
    responses = cursor.fetchall()
    conn.close()
    return rows_to_dicts(responses)


def get_technique_stats(subject_id: int = None, days: int = 30) -> dict:
    """Get aggregate statistics for technique practice sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cutoff = (date.today() - timedelta(days=days)).isoformat()

    if subject_id:
        cursor.execute("""
            SELECT
                COUNT(*) as total_sessions,
                COALESCE(AVG(CASE WHEN total_marks > 0 THEN marks_achieved * 100.0 / total_marks END), 0) as avg_score,
                COALESCE(AVG(CASE WHEN time_limit_seconds > 0 AND time_taken_seconds <= time_limit_seconds THEN 1.0 ELSE 0.0 END), 0) as time_efficiency,
                COALESCE(SUM(questions_answered), 0) as total_questions,
                COALESCE(SUM(correct_answers), 0) as total_correct
            FROM technique_practice_sessions
            WHERE subject_id = ? AND status = 'completed' AND started_at >= ?
        """, (subject_id, cutoff))
    else:
        cursor.execute("""
            SELECT
                COUNT(*) as total_sessions,
                COALESCE(AVG(CASE WHEN total_marks > 0 THEN marks_achieved * 100.0 / total_marks END), 0) as avg_score,
                COALESCE(AVG(CASE WHEN time_limit_seconds > 0 AND time_taken_seconds <= time_limit_seconds THEN 1.0 ELSE 0.0 END), 0) as time_efficiency,
                COALESCE(SUM(questions_answered), 0) as total_questions,
                COALESCE(SUM(correct_answers), 0) as total_correct
            FROM technique_practice_sessions
            WHERE status = 'completed' AND started_at >= ?
        """, (cutoff,))

    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row) if row else {
        'total_sessions': 0, 'avg_score': 0, 'time_efficiency': 0,
        'total_questions': 0, 'total_correct': 0
    }


def get_technique_progress_over_time(subject_id: int = None, limit: int = 20) -> list:
    """Get session-by-session progress for charting."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT
                id, started_at, completed_at,
                CASE WHEN total_marks > 0 THEN marks_achieved * 100.0 / total_marks ELSE 0 END as score_pct,
                time_taken_seconds, time_limit_seconds,
                questions_answered, correct_answers
            FROM technique_practice_sessions
            WHERE subject_id = ? AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT
                id, started_at, completed_at,
                CASE WHEN total_marks > 0 THEN marks_achieved * 100.0 / total_marks ELSE 0 END as score_pct,
                time_taken_seconds, time_limit_seconds,
                questions_answered, correct_answers
            FROM technique_practice_sessions
            WHERE status = 'completed'
            ORDER BY completed_at DESC
            LIMIT ?
        """, (limit,))
    sessions = cursor.fetchall()
    conn.close()
    return rows_to_dicts(sessions)


def get_technique_by_question_type(subject_id: int = None) -> list:
    """Get performance breakdown by question type."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT
                question_type,
                COUNT(*) as total,
                SUM(is_correct) as correct,
                AVG(time_taken_seconds) as avg_time,
                AVG(CASE WHEN max_marks > 0 THEN marks_awarded * 100.0 / max_marks ELSE 0 END) as avg_score
            FROM technique_practice_responses tpr
            JOIN technique_practice_sessions tps ON tpr.session_id = tps.id
            WHERE tps.subject_id = ? AND tps.status = 'completed'
            GROUP BY question_type
        """, (subject_id,))
    else:
        cursor.execute("""
            SELECT
                question_type,
                COUNT(*) as total,
                SUM(is_correct) as correct,
                AVG(time_taken_seconds) as avg_time,
                AVG(CASE WHEN max_marks > 0 THEN marks_awarded * 100.0 / max_marks ELSE 0 END) as avg_score
            FROM technique_practice_responses tpr
            JOIN technique_practice_sessions tps ON tpr.session_id = tps.id
            WHERE tps.status = 'completed'
            GROUP BY question_type
        """)
    types = cursor.fetchall()
    conn.close()
    return rows_to_dicts(types)


def get_all_exam_techniques(category: str = None, question_type: str = None) -> list:
    """Get exam techniques, optionally filtered by category or question type."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM exam_techniques WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if question_type:
        query += " AND (question_type = ? OR question_type IS NULL)"
        params.append(question_type)

    query += " ORDER BY category, title"
    cursor.execute(query, params)
    techniques = cursor.fetchall()
    conn.close()
    return rows_to_dicts(techniques)


def seed_exam_techniques():
    """Seed initial exam technique tips if table is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM exam_techniques")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return 0

    import json
    techniques = [
        # Time Management
        {
            "category": "time_management",
            "question_type": None,
            "title": "Marks-to-Minutes Rule",
            "description": "Allocate roughly 1-1.5 minutes per mark available. Check total marks and exam time to calculate your pace.",
            "tips": json.dumps(["Check total marks and time at start", "Calculate time per mark", "Set mini-deadlines for each section"])
        },
        {
            "category": "time_management",
            "question_type": None,
            "title": "Leave Time for Review",
            "description": "Save 5-10 minutes at the end to check your work and catch silly mistakes.",
            "tips": json.dumps(["Plan to finish 10 mins early", "Check calculations and spelling", "Ensure you answered the question asked"])
        },
        {
            "category": "time_management",
            "question_type": None,
            "title": "Don't Get Stuck",
            "description": "If a question is taking too long, move on and return to it later. Don't let one question cost you marks on others.",
            "tips": json.dumps(["Set a time limit per question", "Mark difficult questions to revisit", "Secure easy marks first"])
        },
        # Question Approach - Essay
        {
            "category": "question_approach",
            "question_type": "essay",
            "title": "PEE/PEEL Structure",
            "description": "Use Point-Evidence-Explanation-Link for each paragraph. This ensures structured, analytical writing.",
            "tips": json.dumps(["State your point clearly first", "Support with specific evidence or quotes", "Explain why this supports your argument", "Link back to the question"])
        },
        {
            "category": "question_approach",
            "question_type": "essay",
            "title": "Plan Before Writing",
            "description": "Spend 3-5 minutes planning your essay structure. A quick plan leads to better organised answers.",
            "tips": json.dumps(["Jot down 3-4 main points", "Order them logically", "Note key evidence for each", "Write a thesis statement"])
        },
        # Question Approach - Multiple Choice
        {
            "category": "question_approach",
            "question_type": "multiple_choice",
            "title": "Process of Elimination",
            "description": "Rule out obviously wrong answers first, then choose from remaining options.",
            "tips": json.dumps(["Cross out answers you know are wrong", "Compare remaining options", "Look for absolute words like 'always' or 'never'"])
        },
        {
            "category": "question_approach",
            "question_type": "multiple_choice",
            "title": "Read All Options First",
            "description": "Don't jump at the first plausible answer. Read all options before deciding.",
            "tips": json.dumps(["Read the question twice", "Consider all options", "Look for the 'best' answer, not just a correct one"])
        },
        # Question Approach - Short Answer
        {
            "category": "question_approach",
            "question_type": "short_answer",
            "title": "Key Term Focus",
            "description": "Identify command words (explain, describe, compare) and key terms. Answer exactly what's asked.",
            "tips": json.dumps(["Underline command words", "Address every part of the question", "Be concise - no waffle"])
        },
        # Answer Technique
        {
            "category": "answer_technique",
            "question_type": None,
            "title": "Show Your Working",
            "description": "In maths and science, show all steps. You can get marks for method even if the final answer is wrong.",
            "tips": json.dumps(["Write each step clearly", "Include units", "Box or underline final answers"])
        },
        {
            "category": "answer_technique",
            "question_type": None,
            "title": "Answer the Actual Question",
            "description": "Re-read the question after writing your answer. Make sure you answered what was asked.",
            "tips": json.dumps(["Check command words", "Ensure you addressed all parts", "Link conclusion to the question"])
        },
        {
            "category": "answer_technique",
            "question_type": None,
            "title": "Use Subject Terminology",
            "description": "Use correct technical terms from your subject. Examiners look for proper vocabulary.",
            "tips": json.dumps(["Learn key terms for each topic", "Define terms when first used", "Avoid vague language"])
        }
    ]

    for tech in techniques:
        cursor.execute("""
            INSERT INTO exam_techniques (category, question_type, title, description, tips)
            VALUES (?, ?, ?, ?, ?)
        """, (tech['category'], tech['question_type'], tech['title'], tech['description'], tech['tips']))

    conn.commit()
    count = len(techniques)
    conn.close()
    return count


def delete_technique_session(session_id: int):
    """Delete a technique practice session and its responses."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM technique_practice_responses WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM technique_practice_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


# =============================================================================
# STUDY SKILLS COACH FUNCTIONS
# =============================================================================

def seed_study_methods():
    """Seed initial study methods content if table is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM study_methods")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return 0

    import json
    methods = [
        # NOTE-TAKING METHODS
        {
            "category": "note_taking",
            "method_type": "cornell",
            "title": "Cornell Note-Taking Method",
            "description": "Divide your page into three sections: notes, cues, and summary. Perfect for lectures and textbook reading.",
            "when_to_use": "Lectures, textbook reading, revision sessions",
            "steps": json.dumps([
                "Draw a vertical line about 6cm from the left edge of your page",
                "Draw a horizontal line about 5cm from the bottom",
                "Take notes in the large right section during class",
                "After class, write questions and cues in the left column",
                "Write a 2-3 sentence summary in the bottom section"
            ]),
            "tips": json.dumps([
                "Leave space between ideas for later additions",
                "Use abbreviations consistently",
                "Review within 24 hours to fill in the cue column",
                "Use the summary to test yourself later"
            ]),
            "example_template": """## Cornell Notes: [Topic]

| Cue Column | Notes |
|------------|-------|
| What causes...? | - Main point 1 |
| Define... | - Supporting detail |
| Why is...? | - Example or evidence |

---
**Summary:** Write 2-3 sentences summarising the key takeaways from this section.""",
            "display_order": 1
        },
        {
            "category": "note_taking",
            "method_type": "outline",
            "title": "Outline Method",
            "description": "Hierarchical structure with main topics, subtopics, and supporting details. Great for well-organised subjects.",
            "when_to_use": "Well-structured content, science topics, history timelines, any logical sequence",
            "steps": json.dumps([
                "Write main topics as Roman numerals (I, II, III)",
                "Indent subtopics with capital letters (A, B, C)",
                "Further indent supporting details with numbers (1, 2, 3)",
                "Use consistent indentation throughout your notes"
            ]),
            "tips": json.dumps([
                "Listen for signal words like 'firstly', 'importantly', 'in contrast'",
                "Leave space to add details later",
                "Use bullet points for quick facts",
                "Number your pages for easy reference"
            ]),
            "example_template": """## I. Main Topic
   A. Subtopic 1
      1. Supporting detail
      2. Example or evidence
   B. Subtopic 2
      1. Key point
      2. Related fact

## II. Second Main Topic
   A. First subtopic
      1. Detail
   B. Second subtopic""",
            "display_order": 2
        },
        {
            "category": "note_taking",
            "method_type": "mind_map",
            "title": "Mind Mapping",
            "description": "Visual diagram with a central idea branching into related concepts. Excellent for brainstorming and seeing connections.",
            "when_to_use": "Brainstorming, revision, essay planning, seeing relationships between ideas",
            "steps": json.dumps([
                "Write the main topic in the centre of your page",
                "Draw branches outward for main subtopics",
                "Add smaller branches for details and examples",
                "Use colours and small images to aid memory",
                "Connect related ideas with lines across branches"
            ]),
            "tips": json.dumps([
                "Use single words or short phrases, not full sentences",
                "Make branches curved rather than straight - it's more memorable",
                "Use different colours for different branches",
                "Add small drawings or symbols to help you remember"
            ]),
            "example_template": """```
                    [Subtopic A]
                   /
    [Detail] --- [Branch 1] --- [Detail]
                /
    [CENTRAL TOPIC]
                \\
    [Detail] --- [Branch 2] --- [Detail]
                   \\
                    [Subtopic B]
```

Start with your main topic in the centre, then branch out!""",
            "display_order": 3
        },
        {
            "category": "note_taking",
            "method_type": "charting",
            "title": "Charting Method",
            "description": "Organise information in columns and rows. Perfect for comparing and contrasting multiple topics.",
            "when_to_use": "Comparing topics, vocabulary lists, historical events, scientific concepts with multiple properties",
            "steps": json.dumps([
                "Identify the categories or features you want to compare",
                "Create columns with clear headings",
                "Fill in information row by row as you learn",
                "Keep entries brief and consistent across columns"
            ]),
            "tips": json.dumps([
                "Pre-draw your chart before class if you know the topic",
                "Leave extra rows blank to fill in later",
                "Use this method for revision comparison tables",
                "Colour-code similar information across columns"
            ]),
            "example_template": """| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Definition | ... | ... | ... |
| Advantages | ... | ... | ... |
| Disadvantages | ... | ... | ... |
| Example | ... | ... | ... |
| When to use | ... | ... | ... |""",
            "display_order": 4
        },
        # ACTIVE LEARNING TECHNIQUES
        {
            "category": "active_learning",
            "method_type": "summarising",
            "title": "Active Summarisation",
            "description": "Condense information into your own words. Forces deep understanding rather than passive copying.",
            "when_to_use": "After reading a chapter, reviewing notes, preparing for exams",
            "steps": json.dumps([
                "Read the entire section or chapter first",
                "Close the book and write down what you remember",
                "Check for gaps and fill them in",
                "Reduce your notes to only the key points"
            ]),
            "tips": json.dumps([
                "Aim for 20-30% of the original length",
                "Use your own words, not copied phrases",
                "Include examples only if they help understanding",
                "Test yourself by explaining the summary to someone else"
            ]),
            "example_template": None,
            "display_order": 10
        },
        {
            "category": "active_learning",
            "method_type": "self_testing",
            "title": "Self-Testing (Retrieval Practice)",
            "description": "Test yourself without looking at notes. The effort of retrieval strengthens memory far more than re-reading.",
            "when_to_use": "Daily revision, before exams, reinforcing new material",
            "steps": json.dumps([
                "Close your notes completely",
                "Write down everything you can remember about the topic",
                "Check against your notes for accuracy",
                "Focus your next revision on what you forgot"
            ]),
            "tips": json.dumps([
                "Testing is MORE effective than re-reading - research proves it!",
                "Use flashcards for quick self-tests",
                "Space your tests over days, not just hours",
                "Getting answers wrong actually helps learning!"
            ]),
            "example_template": None,
            "display_order": 11
        },
        {
            "category": "active_learning",
            "method_type": "spaced_repetition",
            "title": "Spaced Repetition",
            "description": "Review material at increasing intervals. Much more effective than cramming everything at once.",
            "when_to_use": "Long-term learning, memorising facts, vocabulary, formulas",
            "steps": json.dumps([
                "Learn new material thoroughly on day 1",
                "Review after 1 day",
                "Review again after 3 days",
                "Then after 1 week, 2 weeks, 1 month, etc.",
                "Increase intervals as you get better at recalling"
            ]),
            "tips": json.dumps([
                "Use the Flashcards feature - it has spaced repetition built in!",
                "Start revision early to give yourself time for spacing",
                "Review before you forget completely",
                "This is how memory champions learn hundreds of facts"
            ]),
            "example_template": None,
            "display_order": 12
        },
        {
            "category": "active_learning",
            "method_type": "elaboration",
            "title": "Elaboration",
            "description": "Connect new information to what you already know. Ask 'why' and 'how' questions to deepen understanding.",
            "when_to_use": "Understanding complex concepts, making information meaningful, preparing for essay questions",
            "steps": json.dumps([
                "Ask yourself 'Why does this work?' or 'How does this connect?'",
                "Explain the concept in your own words",
                "Think of examples from your own experience",
                "Connect to other topics you've studied"
            ]),
            "tips": json.dumps([
                "The more connections you make, the easier it is to remember",
                "Teach the concept to someone else - it forces elaboration",
                "Create analogies: 'This is like...'",
                "Write about how new information changes your understanding"
            ]),
            "example_template": None,
            "display_order": 13
        }
    ]

    for method in methods:
        cursor.execute("""
            INSERT INTO study_methods (category, method_type, title, description,
                                       when_to_use, steps, tips, example_template, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (method['category'], method['method_type'], method['title'], method['description'],
              method['when_to_use'], method['steps'], method['tips'],
              method['example_template'], method['display_order']))

    conn.commit()
    count = len(methods)
    conn.close()
    return count


def get_study_methods(category: str = None, method_type: str = None) -> list:
    """Get study methods with optional filtering."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM study_methods WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if method_type:
        query += " AND method_type = ?"
        params.append(method_type)

    query += " ORDER BY display_order, title"
    cursor.execute(query, params)
    methods = cursor.fetchall()
    conn.close()
    return rows_to_dicts(methods)


def save_note_evaluation(subject_id: int, method_used: str, note_content: str,
                         word_count: int, overall_score: int, feedback_json: str) -> int:
    """Save a note evaluation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO note_evaluations (subject_id, method_used, note_content,
                                      word_count, overall_score, feedback_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (subject_id, method_used, note_content, word_count, overall_score, feedback_json))
    conn.commit()
    evaluation_id = cursor.lastrowid
    conn.close()
    return evaluation_id


def get_note_evaluations(subject_id: int = None, limit: int = 20) -> list:
    """Get recent note evaluations."""
    conn = get_connection()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
            SELECT ne.*, s.name as subject_name, s.colour as subject_colour
            FROM note_evaluations ne
            LEFT JOIN subjects s ON ne.subject_id = s.id
            WHERE ne.subject_id = ?
            ORDER BY ne.created_at DESC
            LIMIT ?
        """, (subject_id, limit))
    else:
        cursor.execute("""
            SELECT ne.*, s.name as subject_name, s.colour as subject_colour
            FROM note_evaluations ne
            LEFT JOIN subjects s ON ne.subject_id = s.id
            ORDER BY ne.created_at DESC
            LIMIT ?
        """, (limit,))
    evaluations = cursor.fetchall()
    conn.close()
    return rows_to_dicts(evaluations)


def get_note_evaluation_stats() -> dict:
    """Get aggregate stats for note evaluations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_evaluations,
            COALESCE(AVG(overall_score), 0) as avg_score,
            COALESCE(MAX(overall_score), 0) as best_score,
            COALESCE(MIN(overall_score), 0) as lowest_score
        FROM note_evaluations
    """)
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row) if row else {
        'total_evaluations': 0, 'avg_score': 0, 'best_score': 0, 'lowest_score': 0
    }


def delete_note_evaluation(evaluation_id: int):
    """Delete a note evaluation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM note_evaluations WHERE id = ?", (evaluation_id,))
    conn.commit()
    conn.close()


# =============================================================================
# CHAT PERSISTENCE FUNCTIONS (for Bubble Ace)
# =============================================================================

def save_chat_message(session_id: str, role: str, content: str,
                      sources_json: str = None) -> int:
    """Save a chat message to the database. Returns the message ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_messages (session_id, role, content, sources_json)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, sources_json))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id


def get_chat_messages(session_id: str, limit: int = 50) -> list:
    """Get chat messages for a session, ordered by creation time."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, role, content, sources_json, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_recent_chat_sessions(limit: int = 10) -> list:
    """Get list of recent chat sessions with their last message."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id,
               MAX(created_at) as last_activity,
               COUNT(*) as message_count
        FROM chat_messages
        GROUP BY session_id
        ORDER BY last_activity DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def clear_chat_session(session_id: str):
    """Clear all messages in a chat session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def delete_old_chat_messages(days_old: int = 30):
    """Delete chat messages older than specified days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM chat_messages
        WHERE created_at < datetime('now', ?)
    """, (f'-{days_old} days',))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


# Initialise database when module is imported
init_database()
