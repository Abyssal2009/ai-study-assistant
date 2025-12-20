"""
Daily Email Reminder Script for Study Assistant.

This script sends a daily email summary of:
- Homework due today, tomorrow, and this week
- Overdue homework
- Upcoming exams
- Flashcards due for review
- Study statistics

Run manually: python email_reminder.py
Or schedule with Windows Task Scheduler (see setup_scheduler.bat)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta
import sys
from pathlib import Path

# Add the project directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

import database as db
import config


def get_homework_due_tomorrow():
    """Get homework due tomorrow."""
    conn = db.get_connection()
    cursor = conn.cursor()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    cursor.execute("""
        SELECT h.*, s.name as subject_name
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        WHERE h.due_date = ? AND h.completed = 0
        ORDER BY h.priority DESC
    """, (tomorrow,))
    homework = cursor.fetchall()
    conn.close()
    return homework


def generate_email_content():
    """Generate the HTML email content with today's summary."""

    today = date.today()
    today_str = today.strftime("%A, %d %B %Y")

    # Gather all data
    homework_today = db.get_homework_due_today()
    homework_tomorrow = get_homework_due_tomorrow()
    homework_week = db.get_homework_due_this_week()
    overdue = db.get_overdue_homework()
    exams = db.get_exams_this_month()
    flashcard_stats = db.get_flashcard_stats()
    focus_week = db.get_total_focus_minutes_this_week()

    # Build HTML email
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 25px;
            }}
            .urgent {{
                background-color: #fee;
                border-left: 4px solid #e74c3c;
                padding: 10px;
                margin: 10px 0;
            }}
            .warning {{
                background-color: #fff8e6;
                border-left: 4px solid #f39c12;
                padding: 10px;
                margin: 10px 0;
            }}
            .info {{
                background-color: #e8f4f8;
                border-left: 4px solid #3498db;
                padding: 10px;
                margin: 10px 0;
            }}
            .success {{
                background-color: #e8f8e8;
                border-left: 4px solid #27ae60;
                padding: 10px;
                margin: 10px 0;
            }}
            .stat-box {{
                display: inline-block;
                background-color: #f8f9fa;
                padding: 15px;
                margin: 5px;
                border-radius: 8px;
                text-align: center;
                min-width: 100px;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .stat-label {{
                font-size: 12px;
                color: #7f8c8d;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .subject {{
                font-weight: bold;
                color: #2980b9;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <h1>📚 Good Morning! Here's Your Study Plan</h1>
        <p><strong>{today_str}</strong></p>
    """

    # Overdue section (if any)
    if config.INCLUDE_OVERDUE_HOMEWORK and overdue:
        html += """
        <h2>🚨 OVERDUE - Needs Immediate Attention!</h2>
        <div class="urgent">
        <ul>
        """
        for hw in overdue:
            days_late = (today - date.fromisoformat(hw['due_date'])).days
            html += f"<li><span class='subject'>{hw['subject_name']}</span>: {hw['title']} ({days_late} days late)</li>"
        html += "</ul></div>"

    # Due today
    if config.INCLUDE_HOMEWORK_DUE_TODAY:
        html += "<h2>📋 Due Today</h2>"
        if homework_today:
            html += "<div class='warning'><ul>"
            for hw in homework_today:
                html += f"<li><span class='subject'>{hw['subject_name']}</span>: {hw['title']}</li>"
            html += "</ul></div>"
        else:
            html += "<div class='success'><p>Nothing due today! ✓</p></div>"

    # Due tomorrow
    if config.INCLUDE_HOMEWORK_DUE_TOMORROW:
        html += "<h2>📅 Due Tomorrow</h2>"
        if homework_tomorrow:
            html += "<div class='info'><ul>"
            for hw in homework_tomorrow:
                html += f"<li><span class='subject'>{hw['subject_name']}</span>: {hw['title']}</li>"
            html += "</ul></div>"
        else:
            html += "<div class='success'><p>Nothing due tomorrow! ✓</p></div>"

    # This week
    if config.INCLUDE_HOMEWORK_DUE_THIS_WEEK:
        # Filter out today and tomorrow from weekly list
        week_only = [hw for hw in homework_week
                     if hw['due_date'] != today.isoformat()
                     and hw['due_date'] != (today + timedelta(days=1)).isoformat()]
        if week_only:
            html += "<h2>📆 Later This Week</h2><div class='info'><ul>"
            for hw in week_only[:5]:  # Show max 5
                due = date.fromisoformat(hw['due_date'])
                days = (due - today).days
                html += f"<li><span class='subject'>{hw['subject_name']}</span>: {hw['title']} (in {days} days)</li>"
            if len(week_only) > 5:
                html += f"<li>...and {len(week_only) - 5} more</li>"
            html += "</ul></div>"

    # Upcoming exams
    if config.INCLUDE_UPCOMING_EXAMS and exams:
        html += "<h2>📝 Upcoming Exams</h2><div class='warning'><ul>"
        for exam in exams[:3]:
            days = (date.fromisoformat(exam['exam_date']) - today).days
            if days == 0:
                html += f"<li><strong>TODAY!</strong> <span class='subject'>{exam['subject_name']}</span>: {exam['name']}</li>"
            elif days == 1:
                html += f"<li><strong>TOMORROW!</strong> <span class='subject'>{exam['subject_name']}</span>: {exam['name']}</li>"
            else:
                html += f"<li><span class='subject'>{exam['subject_name']}</span>: {exam['name']} (in {days} days)</li>"
        html += "</ul></div>"

    # Flashcards
    if config.INCLUDE_FLASHCARDS_DUE:
        html += "<h2>🃏 Flashcards</h2>"
        if flashcard_stats['due_today'] > 0:
            html += f"""
            <div class='info'>
                <p><strong>{flashcard_stats['due_today']} cards</strong> are due for review today.</p>
                <p>You have {flashcard_stats['total']} total cards.
                   Your 7-day accuracy is {flashcard_stats['accuracy_7_days']}%.</p>
            </div>
            """
        else:
            html += "<div class='success'><p>No flashcards due! You're all caught up. ✓</p></div>"

    # Stats
    if config.INCLUDE_STUDY_STATS:
        hours = focus_week // 60
        mins = focus_week % 60
        hw_stats = db.get_homework_stats()
        html += f"""
        <h2>📊 Your Week So Far</h2>
        <div style="text-align: center;">
            <div class="stat-box">
                <div class="stat-number">{hours}h {mins}m</div>
                <div class="stat-label">Study Time</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{hw_stats['completed_this_week']}</div>
                <div class="stat-label">Tasks Completed</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{flashcard_stats['reviewed_today']}</div>
                <div class="stat-label">Cards Reviewed Today</div>
            </div>
        </div>
        """

    # Motivational closing
    html += """
        <div class="footer">
            <p>💪 <em>Small consistent effort beats big irregular effort. You've got this!</em></p>
            <p>This email was sent by your Study Assistant.<br>
            Open the app to manage your tasks: <code>streamlit run app.py</code></p>
        </div>
    </body>
    </html>
    """

    return html


def generate_plain_text():
    """Generate plain text version of the email."""
    today = date.today()
    today_str = today.strftime("%A, %d %B %Y")

    homework_today = db.get_homework_due_today()
    homework_tomorrow = get_homework_due_tomorrow()
    overdue = db.get_overdue_homework()
    exams = db.get_exams_this_month()
    flashcard_stats = db.get_flashcard_stats()

    text = f"""
STUDY ASSISTANT - Daily Summary
{today_str}
{'=' * 40}

"""

    if overdue:
        text += "🚨 OVERDUE:\n"
        for hw in overdue:
            days_late = (today - date.fromisoformat(hw['due_date'])).days
            text += f"  - {hw['subject_name']}: {hw['title']} ({days_late} days late)\n"
        text += "\n"

    text += "📋 DUE TODAY:\n"
    if homework_today:
        for hw in homework_today:
            text += f"  - {hw['subject_name']}: {hw['title']}\n"
    else:
        text += "  Nothing due today!\n"
    text += "\n"

    text += "📅 DUE TOMORROW:\n"
    if homework_tomorrow:
        for hw in homework_tomorrow:
            text += f"  - {hw['subject_name']}: {hw['title']}\n"
    else:
        text += "  Nothing due tomorrow!\n"
    text += "\n"

    if exams:
        text += "📝 UPCOMING EXAMS:\n"
        for exam in exams[:3]:
            days = (date.fromisoformat(exam['exam_date']) - today).days
            text += f"  - {exam['subject_name']}: {exam['name']} (in {days} days)\n"
        text += "\n"

    text += f"🃏 FLASHCARDS: {flashcard_stats['due_today']} cards due for review\n\n"

    text += "---\nGood luck with your studies today!\n"

    return text


def send_email():
    """Send the daily reminder email."""

    # Check if email is configured
    if config.EMAIL_SENDER == "your.email@gmail.com":
        print("❌ Email not configured!")
        print("Please edit config.py with your email settings.")
        print("See the comments in config.py for instructions on getting a Gmail App Password.")
        return False

    # Generate content
    html_content = generate_email_content()
    plain_content = generate_plain_text()

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Study Plan for {date.today().strftime('%A, %d %B')}"
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = config.EMAIL_RECIPIENT

    # Attach both plain text and HTML versions
    part1 = MIMEText(plain_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        # Connect to SMTP server
        print(f"Connecting to {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()  # Enable security

        # Login
        print("Logging in...")
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)

        # Send email
        print(f"Sending email to {config.EMAIL_RECIPIENT}...")
        server.sendmail(config.EMAIL_SENDER, config.EMAIL_RECIPIENT, msg.as_string())

        # Disconnect
        server.quit()

        print("✅ Email sent successfully!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("Check your email address and App Password in config.py")
        print("For Gmail, you MUST use an App Password, not your regular password.")
        print("See: https://support.google.com/accounts/answer/185833")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def preview_email():
    """Preview the email content without sending."""
    print("\n" + "=" * 60)
    print("EMAIL PREVIEW (Plain Text Version)")
    print("=" * 60)
    print(generate_plain_text())
    print("=" * 60)
    print("\nTo send this email, run: python email_reminder.py --send")
    print("To configure email settings, edit: config.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Study Assistant Daily Email Reminder")
    parser.add_argument('--send', action='store_true', help='Send the email')
    parser.add_argument('--preview', action='store_true', help='Preview email without sending')

    args = parser.parse_args()

    if args.send:
        send_email()
    elif args.preview:
        preview_email()
    else:
        # Default: preview
        preview_email()
