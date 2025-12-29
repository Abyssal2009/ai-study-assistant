"""
Study Assistant - Google Drive Integration
Uses Google Drive API with OAuth 2.0 authentication.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Token storage path
TOKEN_PATH = Path(__file__).parent.parent / "google_token.json"
CREDENTIALS_PATH = Path(__file__).parent.parent / "google_credentials.json"
BACKUP_FOLDER = "StudyAssistantBackups"

# OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveClient:
    """Google Drive client using Google Drive API."""

    def __init__(self):
        self._service = None
        self._credentials = None
        self._folder_id = None

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

        # Load existing token
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        # Refresh if expired
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
        """Build the Drive API service."""
        from googleapiclient.discovery import build

        creds = self._get_credentials()
        if not creds or not creds.valid:
            raise Exception("Not authenticated")

        self._service = build('drive', 'v3', credentials=creds)
        self._credentials = creds

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        try:
            creds = self._get_credentials()
            return creds is not None and creds.valid
        except Exception:
            return False

    def has_credentials_file(self) -> bool:
        """Check if OAuth credentials file exists."""
        return CREDENTIALS_PATH.exists()

    def start_auth_flow(self) -> Tuple[bool, str, Optional[Dict]]:
        """
        Start OAuth authentication flow.

        Returns:
            Tuple of (success, message, flow_data)
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            return False, "Google libraries not installed", None

        if not CREDENTIALS_PATH.exists():
            return False, (
                "Google credentials file not found. Please:\n"
                "1. Go to Google Cloud Console\n"
                "2. Create a project and enable Drive API\n"
                "3. Create OAuth 2.0 credentials (Desktop app)\n"
                "4. Download credentials.json\n"
                f"5. Save as: {CREDENTIALS_PATH}"
            ), None

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )

            # Use local server for OAuth callback
            creds = flow.run_local_server(port=0)
            self._save_credentials(creds)
            self._credentials = creds

            return True, "Authentication successful", None

        except Exception as e:
            return False, f"Auth error: {str(e)}", None

    def disconnect(self) -> Tuple[bool, str]:
        """Remove stored credentials."""
        try:
            if TOKEN_PATH.exists():
                TOKEN_PATH.unlink()
            self._service = None
            self._credentials = None
            self._folder_id = None
            return True, "Disconnected from Google Drive"
        except Exception as e:
            return False, f"Disconnect error: {str(e)}"

    def _ensure_backup_folder(self) -> str:
        """Ensure backup folder exists in Google Drive, return folder ID."""
        if self._folder_id:
            return self._folder_id

        if not self._service:
            self._build_service()

        # Search for existing folder
        query = f"name='{BACKUP_FOLDER}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self._service.files().list(
            q=query, spaces='drive', fields='files(id, name)'
        ).execute()

        files = results.get('files', [])
        if files:
            self._folder_id = files[0]['id']
            return self._folder_id

        # Create folder
        folder_metadata = {
            'name': BACKUP_FOLDER,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self._service.files().create(
            body=folder_metadata, fields='id'
        ).execute()

        self._folder_id = folder['id']
        return self._folder_id

    def upload_backup(self, local_path: str, remote_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Upload a backup file to Google Drive.

        Args:
            local_path: Path to the local backup file
            remote_name: Optional name for the file in Drive

        Returns:
            Tuple of (success, message)
        """
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError:
            return False, "Google libraries not installed"

        try:
            local_file = Path(local_path)
            if not local_file.exists():
                return False, "Local file not found"

            if not self._service:
                self._build_service()

            folder_id = self._ensure_backup_folder()
            filename = remote_name or local_file.name

            # Check if file already exists
            query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
            results = self._service.files().list(q=query, fields='files(id)').execute()
            existing = results.get('files', [])

            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            media = MediaFileUpload(
                str(local_file),
                mimetype='application/zip',
                resumable=True
            )

            if existing:
                # Update existing file
                file = self._service.files().update(
                    fileId=existing[0]['id'],
                    media_body=media
                ).execute()
            else:
                # Create new file
                file = self._service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return True, f"Uploaded {filename} to Google Drive"

        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def list_backups(self) -> Tuple[bool, str, List[Dict]]:
        """
        List backup files in Google Drive.

        Returns:
            Tuple of (success, message, list of backup info dicts)
        """
        try:
            if not self._service:
                self._build_service()

            folder_id = self._ensure_backup_folder()

            query = f"'{folder_id}' in parents and trashed=false and mimeType='application/zip'"
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size, createdTime, modifiedTime)',
                orderBy='modifiedTime desc'
            ).execute()

            files = results.get('files', [])
            backups = []

            for f in files:
                if f['name'].endswith('.zip'):
                    size = int(f.get('size', 0))
                    backups.append({
                        'id': f['id'],
                        'name': f['name'],
                        'size_bytes': size,
                        'size_mb': size / (1024 * 1024),
                        'created_at': f.get('createdTime'),
                        'modified_at': f.get('modifiedTime')
                    })

            return True, f"Found {len(backups)} backup(s)", backups

        except Exception as e:
            return False, f"List error: {str(e)}", []

    def download_backup(self, remote_name: str, local_path: str) -> Tuple[bool, str]:
        """
        Download a backup file from Google Drive.

        Args:
            remote_name: Name of the file in Drive
            local_path: Where to save the file locally

        Returns:
            Tuple of (success, message)
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io
        except ImportError:
            return False, "Google libraries not installed"

        try:
            if not self._service:
                self._build_service()

            folder_id = self._ensure_backup_folder()

            # Find file
            query = f"name='{remote_name}' and '{folder_id}' in parents and trashed=false"
            results = self._service.files().list(q=query, fields='files(id)').execute()
            files = results.get('files', [])

            if not files:
                return False, f"File not found: {remote_name}"

            file_id = files[0]['id']

            # Download
            request = self._service.files().get_media(fileId=file_id)
            local_file = Path(local_path)
            local_file.parent.mkdir(parents=True, exist_ok=True)

            with open(local_file, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return True, f"Downloaded to {local_path}"

        except Exception as e:
            return False, f"Download error: {str(e)}"

    def delete_backup(self, remote_name: str) -> Tuple[bool, str]:
        """
        Delete a backup file from Google Drive.

        Args:
            remote_name: Name of the file to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self._service:
                self._build_service()

            folder_id = self._ensure_backup_folder()

            # Find file
            query = f"name='{remote_name}' and '{folder_id}' in parents and trashed=false"
            results = self._service.files().list(q=query, fields='files(id)').execute()
            files = results.get('files', [])

            if not files:
                return False, "File not found"

            # Delete (move to trash)
            self._service.files().delete(fileId=files[0]['id']).execute()
            return True, f"Deleted {remote_name}"

        except Exception as e:
            return False, f"Delete error: {str(e)}"

    def get_user_info(self) -> Tuple[bool, str, Optional[Dict]]:
        """Get connected user information."""
        try:
            if not self._service:
                self._build_service()

            about = self._service.about().get(fields='user').execute()
            user = about.get('user', {})

            return True, "Success", {
                'name': user.get('displayName'),
                'email': user.get('emailAddress')
            }

        except Exception as e:
            return False, f"Error: {str(e)}", None


# Singleton instance
_client = None


def get_client() -> GoogleDriveClient:
    """Get Google Drive client instance."""
    global _client
    if _client is None:
        _client = GoogleDriveClient()
    return _client
