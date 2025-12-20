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
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

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
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

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
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Past paper questions - individual question scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            question_number TEXT NOT NULL,
            topic TEXT,
            max_marks INTEGER NOT NULL,
            marks_achieved INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (paper_id) REFERENCES past_papers(id)
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
                 description: str = "", priority: str = "medium") -> int:
    """Add a new homework item. Returns the new homework's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO homework (subject_id, title, description, due_date, priority)
           VALUES (?, ?, ?, ?, ?)""",
        (subject_id, title, description, due_date, priority)
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
    """Mark a homework item as completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE homework SET completed = 1, completed_at = ? WHERE id = ?",
        (datetime.now(), homework_id)
    )
    conn.commit()
    conn.close()


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


def delete_exam(exam_id: int):
    """Delete an exam."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()


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

    # Check if today or yesterday is in the list (streak must be current)
    today = date.today().isoformat()
    yesterday = date.today().isoformat()  # Simplified - would need proper date calc

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

    conn.close()

    return {
        'pending': pending,
        'completed_this_week': completed_week,
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
# PAST PAPER FUNCTIONS
# =============================================================================

def add_past_paper(subject_id: int, paper_name: str, total_marks: int,
                   exam_board: str = None, year: str = None, paper_number: str = None,
                   time_taken_minutes: int = None, notes: str = None) -> int:
    """Add a new past paper record. Returns the paper ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO past_papers
           (subject_id, paper_name, total_marks, exam_board, year, paper_number, time_taken_minutes, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (subject_id, paper_name, total_marks, exam_board, year, paper_number, time_taken_minutes, notes)
    )
    conn.commit()
    paper_id = cursor.lastrowid
    conn.close()
    return paper_id


def add_paper_question(paper_id: int, question_number: str, max_marks: int,
                       marks_achieved: int, topic: str = None, notes: str = None) -> int:
    """Add a question result to a past paper. Returns the question ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO paper_questions
           (paper_id, question_number, max_marks, marks_achieved, topic, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (paper_id, question_number, max_marks, marks_achieved, topic, notes)
    )
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id


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
                'action': f'Review flashcards to reinforce memory',
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


# Initialise database when module is imported
init_database()
