"""
Study Assistant - Cloud Integration Module
Provides Google Drive backup support.
"""

from enum import Enum


class CloudService(Enum):
    """Supported cloud services."""
    NONE = "none"
    GOOGLE_DRIVE = "google_drive"


def get_available_services():
    """Get list of available cloud services."""
    return [
        {"id": CloudService.NONE.value, "name": "None (Local only)"},
        {"id": CloudService.GOOGLE_DRIVE.value, "name": "Google Drive"},
    ]
