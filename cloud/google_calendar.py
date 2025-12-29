"""
Study Assistant - Google Calendar Integration
Two-way sync between app exams and Google Calendar.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# Import shared credentials from google_drive
from cloud.google_drive import TOKEN_PATH, CREDENTIALS_PATH, SCOPES

# Calendar name for exam events
CALENDAR_SUMMARY = "Study Assistant Exams"


class GoogleCalendarClient:
    """Google Calendar client for exam sync."""

    def __init__(self):
        self._service = None
        self._credentials = None
        self._calendar_id = None

    def _get_credentials(self):
        """Load or refresh credentials."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
        except ImportError:
            raise ImportError(
                "Google libraries not installed. Run: "
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )

        creds = None

        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save_credentials(creds)
            except Exception:
                creds = None

        return creds

    def _save_credentials(self, creds):
        """Save credentials to token file."""
        TOKEN_PATH.write_text(creds.to_json())

    def _build_service(self):
        """Build the Calendar API service."""
        from googleapiclient.discovery import build

        creds = self._get_credentials()
        if not creds or not creds.valid:
            raise Exception("Not authenticated")

        self._service = build('calendar', 'v3', credentials=creds)
        self._credentials = creds

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with Calendar scope."""
        try:
            creds = self._get_credentials()
            if not creds or not creds.valid:
                return False
            # Check if calendar scope is included
            return 'https://www.googleapis.com/auth/calendar' in (creds.scopes or [])
        except Exception:
            return False

    def _ensure_calendar(self) -> str:
        """Ensure our exam calendar exists, return calendar ID."""
        if self._calendar_id:
            return self._calendar_id

        if not self._service:
            self._build_service()

        # Look for existing calendar
        calendars = self._service.calendarList().list().execute()
        for cal in calendars.get('items', []):
            if cal.get('summary') == CALENDAR_SUMMARY:
                self._calendar_id = cal['id']
                return self._calendar_id

        # Create new calendar
        calendar = {
            'summary': CALENDAR_SUMMARY,
            'description': 'Exam dates synced from Study Assistant',
            'timeZone': 'Europe/London'
        }
        created = self._service.calendars().insert(body=calendar).execute()
        self._calendar_id = created['id']
        return self._calendar_id

    def sync_exam_to_calendar(self, exam: dict) -> Tuple[bool, str, Optional[str]]:
        """
        Sync an exam to Google Calendar.

        Args:
            exam: Exam dict with name, exam_date, subject_name, location, etc.

        Returns:
            Tuple of (success, message, calendar_event_id)
        """
        try:
            if not self._service:
                self._build_service()

            calendar_id = self._ensure_calendar()

            # Build event
            event = {
                'summary': f"📚 {exam['name']}",
                'description': f"Subject: {exam.get('subject_name', 'Unknown')}\n"
                              f"Duration: {exam.get('duration_minutes', 'N/A')} minutes\n"
                              f"Location: {exam.get('location', 'TBC')}",
                'start': {
                    'date': exam['exam_date'],
                },
                'end': {
                    'date': exam['exam_date'],
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 1440},  # 1 day before
                        {'method': 'popup', 'minutes': 10080},  # 1 week before
                    ]
                }
            }

            # Add location if provided
            if exam.get('location'):
                event['location'] = exam['location']

            # Check if we're updating or creating
            existing_id = exam.get('google_calendar_id')
            if existing_id:
                # Update existing event
                try:
                    updated = self._service.events().update(
                        calendarId=calendar_id,
                        eventId=existing_id,
                        body=event
                    ).execute()
                    return True, f"Updated: {exam['name']}", updated['id']
                except Exception:
                    # Event might have been deleted, create new one
                    pass

            # Create new event
            created = self._service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            return True, f"Added to calendar: {exam['name']}", created['id']

        except Exception as e:
            return False, f"Sync error: {str(e)}", None

    def delete_from_calendar(self, event_id: str) -> Tuple[bool, str]:
        """
        Delete an event from Google Calendar.

        Args:
            event_id: Google Calendar event ID

        Returns:
            Tuple of (success, message)
        """
        if not event_id:
            return True, "No calendar event to delete"

        try:
            if not self._service:
                self._build_service()

            calendar_id = self._ensure_calendar()

            self._service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return True, "Removed from calendar"

        except Exception as e:
            # Event might already be deleted
            if 'notFound' in str(e):
                return True, "Event already removed"
            return False, f"Delete error: {str(e)}"

    def get_calendar_events(self, days_ahead: int = 90) -> Tuple[bool, str, List[Dict]]:
        """
        Get upcoming events from the exam calendar.

        Args:
            days_ahead: How many days ahead to look

        Returns:
            Tuple of (success, message, list of events)
        """
        try:
            if not self._service:
                self._build_service()

            calendar_id = self._ensure_calendar()

            now = datetime.utcnow().isoformat() + 'Z'
            future = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

            events_result = self._service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=future,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = []
            for event in events_result.get('items', []):
                start = event['start'].get('date') or event['start'].get('dateTime', '')[:10]
                events.append({
                    'id': event['id'],
                    'name': event.get('summary', 'Untitled'),
                    'date': start,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })

            return True, f"Found {len(events)} events", events

        except Exception as e:
            return False, f"Error: {str(e)}", []

    def sync_all_exams(self, exams: list) -> Tuple[int, int, List[str]]:
        """
        Sync all exams to Google Calendar.

        Args:
            exams: List of exam dicts

        Returns:
            Tuple of (success_count, fail_count, list of messages)
        """
        success = 0
        failed = 0
        messages = []

        for exam in exams:
            ok, msg, event_id = self.sync_exam_to_calendar(exam)
            if ok:
                success += 1
                # Update database with calendar ID
                if event_id:
                    import database as db
                    db.update_exam_calendar_id(exam['id'], event_id)
            else:
                failed += 1
                messages.append(msg)

        return success, failed, messages


# Singleton instance
_client = None


def get_client() -> GoogleCalendarClient:
    """Get Google Calendar client instance."""
    global _client
    if _client is None:
        _client = GoogleCalendarClient()
    return _client
