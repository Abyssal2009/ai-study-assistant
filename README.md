# AI Study Assistant

A personal study assistant built for GCSE students to help with revision, homework tracking, and staying focused.

## Features

- **Homework Tracker** - Track assignments with due dates, priorities, and completion status
- **Exam Calendar** - Keep track of upcoming exams with countdowns
- **Flashcards with Spaced Repetition** - SM-2 algorithm for optimal memory retention
- **Focus Timer** - Pomodoro-style timer to help you stay focused
- **Daily Email Reminders** - Receive morning summaries of what's due
- **"What Should I Study Next?"** - Smart recommendations based on deadlines and priorities
- **Statistics** - Track your study progress over time

## Installation

1. Make sure you have Python 3.11+ installed
2. Clone this repository
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```
5. Open http://localhost:8501 in your browser

## Setting Up Email Reminders

1. Copy `config.example.py` to `config.py`
2. Edit `config.py` with your email settings
3. For Gmail, you need an App Password (not your regular password):
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Search for "App passwords" and create one
4. Test the email: `python email_reminder.py --send`
5. Set up daily reminders by running `setup_daily_reminder.bat` as administrator

## Project Structure

```
ai-study-assistant/
├── app.py                 # Main Streamlit application
├── database.py            # Database functions and SM-2 algorithm
├── email_reminder.py      # Daily email reminder script
├── config.example.py      # Example configuration (copy to config.py)
├── requirements.txt       # Python dependencies
├── run_email_reminder.bat # Runner for Task Scheduler
└── setup_daily_reminder.bat # Sets up Windows Task Scheduler
```

## How the Spaced Repetition Works

The flashcard system uses the SuperMemo 2 (SM-2) algorithm:
- Cards you remember well are shown less frequently
- Cards you forget are shown again soon
- The system adapts to your learning pace

Rating scale when reviewing:
- 0-2: Forgot (card resets, shown tomorrow)
- 3: Remembered with effort
- 4: Remembered well
- 5: Perfect instant recall

## Tech Stack

- Python 3.11+
- Streamlit (web interface)
- SQLite (database)
- No external services required (runs locally)

## Privacy

All your data is stored locally in `study.db`. Nothing is sent to external servers unless you configure email reminders.

---

Built for GCSE success!
