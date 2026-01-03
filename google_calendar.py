"""
Google Calendar Integration for Exam Sync.
Handles OAuth 2.0 authentication and syncing exams to Google Calendar.
"""

import streamlit as st
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import database as db

# OAuth 2.0 configuration
# OAuth scopes for Google APIs:
# calendar - Full calendar access (read/write)
# calendar.events - Create/modify calendar events
# drive.file - Access to Drive files created by this app
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.file'
]
REDIRECT_URI = 'http://localhost:8501'  # Streamlit default port


def get_oauth_config():
    """Get OAuth configuration from Streamlit secrets."""
    try:
        return {
            'client_id': st.secrets['google_calendar']['client_id'],
            'client_secret': st.secrets['google_calendar']['client_secret']
        }
    except (KeyError, FileNotFoundError):
        return None


def get_calendar_auth_url() -> str:
    """Generate OAuth authorization URL."""
    config = get_oauth_config()
    if not config:
        return None

    flow = Flow.from_client_config(
        {
            'web': {
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    return auth_url


def handle_calendar_callback(code: str) -> bool:
    """Exchange authorization code for tokens and store them."""
    config = get_oauth_config()
    if not config:
        return False

    try:
        flow = Flow.from_client_config(
            {
                'web': {
                    'client_id': config['client_id'],
                    'client_secret': config['client_secret'],
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Store tokens in database
        db.save_calendar_tokens(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expiry=credentials.expiry
        )

        return True
    except Exception as e:
        st.error(f"Failed to authenticate: {e}")
        return False


def get_calendar_service():
    """Get authenticated Google Calendar service with auto token refresh."""
    tokens = db.get_calendar_tokens()
    if not tokens or not tokens.get('access_token'):
        return None

    config = get_oauth_config()
    if not config:
        return None

    try:
        # Parse token expiry
        expiry = None
        if tokens.get('token_expiry'):
            if isinstance(tokens['token_expiry'], str):
                expiry = datetime.fromisoformat(tokens['token_expiry'].replace('Z', '+00:00'))
            else:
                expiry = tokens['token_expiry']

        credentials = Credentials(
            token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            expiry=expiry
        )

        # Check if token needs refresh
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())

            # Update stored tokens
            db.save_calendar_tokens(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expiry=credentials.expiry
            )

        service = build('calendar', 'v3', credentials=credentials)
        return service

    except Exception as e:
        st.error(f"Failed to get calendar service: {e}")
        return None


def sync_exam_to_calendar(exam_id: int) -> bool:
    """Create or update a calendar event for an exam."""
    service = get_calendar_service()
    if not service:
        return False

    exam = db.get_exam_with_calendar_id(exam_id)
    if not exam:
        return False

    try:
        # Format event
        event = {
            'summary': f"[{exam['subject_name']}] {exam['name']}",
            'start': {
                'date': str(exam['exam_date']),
            },
            'end': {
                'date': str(exam['exam_date']),
            },
            'description': _build_exam_description(exam),
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 1440},  # 1 day before
                    {'method': 'popup', 'minutes': 10080},  # 1 week before
                ],
            },
        }

        if exam.get('google_calendar_id'):
            # Update existing event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=exam['google_calendar_id'],
                body=event
            ).execute()
            return True
        else:
            # Create new event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            # Store the calendar event ID
            db.update_exam_calendar_id(exam_id, created_event['id'])
            return True

    except HttpError as e:
        if e.resp.status == 404:
            # Event was deleted from calendar, create new one
            try:
                created_event = service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()
                db.update_exam_calendar_id(exam_id, created_event['id'])
                return True
            except Exception:
                return False
        st.error(f"Calendar API error: {e}")
        return False
    except Exception as e:
        st.error(f"Failed to sync exam: {e}")
        return False


def _build_exam_description(exam: dict) -> str:
    """Build event description from exam details."""
    parts = []

    if exam.get('duration_minutes'):
        parts.append(f"Duration: {exam['duration_minutes']} minutes")

    if exam.get('location'):
        parts.append(f"Location: {exam['location']}")

    if exam.get('notes'):
        parts.append(f"\nNotes:\n{exam['notes']}")

    parts.append("\n---\nSynced from Study Assistant")

    return '\n'.join(parts)


def delete_exam_from_calendar(exam_id: int) -> bool:
    """Delete an exam event from Google Calendar."""
    service = get_calendar_service()
    if not service:
        return False

    exam = db.get_exam_with_calendar_id(exam_id)
    if not exam or not exam.get('google_calendar_id'):
        return True  # Nothing to delete

    try:
        service.events().delete(
            calendarId='primary',
            eventId=exam['google_calendar_id']
        ).execute()

        db.clear_exam_calendar_id(exam_id)
        return True

    except HttpError as e:
        if e.resp.status == 404:
            # Already deleted from calendar
            db.clear_exam_calendar_id(exam_id)
            return True
        st.error(f"Failed to delete calendar event: {e}")
        return False
    except Exception as e:
        st.error(f"Failed to delete from calendar: {e}")
        return False


def sync_all_exams() -> tuple:
    """Sync all exams to Google Calendar. Returns (success_count, fail_count)."""
    if not db.is_calendar_connected():
        return (0, 0)

    exams = db.get_exams_without_calendar_id()
    success_count = 0
    fail_count = 0

    for exam in exams:
        if sync_exam_to_calendar(exam['id']):
            success_count += 1
        else:
            fail_count += 1

    if success_count > 0:
        db.update_calendar_last_sync()

    return (success_count, fail_count)


def disconnect_calendar():
    """Disconnect from Google Calendar."""
    db.clear_calendar_tokens()


def is_configured() -> bool:
    """Check if Google Calendar credentials are configured."""
    return get_oauth_config() is not None
