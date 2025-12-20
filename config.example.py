"""
Configuration file for the Study Assistant.
Copy this file to config.py and edit with your settings.

IMPORTANT: Keep your email password/app password secret!
Never share config.py or commit it to version control.
"""

# =============================================================================
# EMAIL SETTINGS
# =============================================================================

# Your email address (the one that will SEND the reminder)
EMAIL_SENDER = "your.email@gmail.com"

# Your email password or App Password
# For Gmail: You MUST use an App Password, not your regular password
# How to get an App Password:
#   1. Go to https://myaccount.google.com/security
#   2. Enable 2-Step Verification if not already enabled
#   3. Go to "App passwords" (search for it)
#   4. Generate a new app password for "Mail"
#   5. Copy the 16-character password here (no spaces)
EMAIL_PASSWORD = "your-app-password-here"

# Email address to RECEIVE the reminder (can be the same as sender)
EMAIL_RECIPIENT = "your.email@gmail.com"

# SMTP server settings (Gmail defaults - change if using different provider)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# =============================================================================
# REMINDER SETTINGS
# =============================================================================

# What time to send the daily reminder (used by Task Scheduler)
# Format: HH:MM (24-hour)
REMINDER_TIME = "07:00"

# Include these sections in the email
INCLUDE_HOMEWORK_DUE_TODAY = True
INCLUDE_HOMEWORK_DUE_TOMORROW = True
INCLUDE_HOMEWORK_DUE_THIS_WEEK = True
INCLUDE_OVERDUE_HOMEWORK = True
INCLUDE_UPCOMING_EXAMS = True
INCLUDE_FLASHCARDS_DUE = True
INCLUDE_STUDY_STATS = True
