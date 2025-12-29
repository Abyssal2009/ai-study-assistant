"""
Study Assistant - Backup and Restore Module
Handles local backup creation, restoration, and integrity verification.
"""

import os
import json
import shutil
import zipfile
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Paths
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"
DB_PATH = BASE_PATH / "study.db"
IMAGES_PATH = DATA_PATH / "images" / "notes"
BACKUPS_PATH = DATA_PATH / "backups"

# Backup format version
BACKUP_VERSION = "1.0"


def ensure_backup_dir():
    """Ensure backup directory exists."""
    BACKUPS_PATH.mkdir(parents=True, exist_ok=True)


def get_backup_metadata() -> Dict:
    """Generate metadata for a backup."""
    import database as db

    metadata = {
        'version': BACKUP_VERSION,
        'created_at': datetime.now().isoformat(),
        'app_name': 'AI Study Assistant',
        'counts': {
            'subjects': len(db.get_all_subjects()),
            'notes': len(db.get_all_notes()),
            'flashcards': len(db.get_all_flashcards()),
            'past_papers': db.get_paper_count(),
            'note_images': db.get_note_images_count()
        }
    }
    return metadata


def create_backup(backup_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Create a backup ZIP file containing the database and images.

    Args:
        backup_name: Optional custom name for the backup. If None, uses timestamp.

    Returns:
        Tuple of (success, message, backup_path)
    """
    ensure_backup_dir()

    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if backup_name:
        safe_name = "".join(c for c in backup_name if c.isalnum() or c in "._- ")
        filename = f"backup_{safe_name}_{timestamp}.zip"
    else:
        filename = f"backup_{timestamp}.zip"

    backup_path = BACKUPS_PATH / filename

    try:
        # Check if database exists
        if not DB_PATH.exists():
            return False, "Database file not found", None

        # Create the ZIP file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add metadata
            metadata = get_backup_metadata()
            zf.writestr('metadata.json', json.dumps(metadata, indent=2))

            # Add database
            zf.write(DB_PATH, 'study.db')

            # Add images
            if IMAGES_PATH.exists():
                for img_file in IMAGES_PATH.glob('*'):
                    if img_file.is_file() and img_file.name != '.gitkeep':
                        arcname = f"images/notes/{img_file.name}"
                        zf.write(img_file, arcname)

        # Verify the backup
        is_valid, verify_msg = verify_backup_integrity(str(backup_path))
        if not is_valid:
            backup_path.unlink()  # Delete invalid backup
            return False, f"Backup verification failed: {verify_msg}", None

        size_mb = backup_path.stat().st_size / (1024 * 1024)
        return True, f"Backup created successfully ({size_mb:.2f} MB)", str(backup_path)

    except Exception as e:
        # Clean up failed backup
        if backup_path.exists():
            backup_path.unlink()
        return False, f"Backup failed: {str(e)}", None


def verify_backup_integrity(backup_path: str) -> Tuple[bool, str]:
    """
    Verify that a backup file is valid and complete.

    Args:
        backup_path: Path to the backup ZIP file

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        path = Path(backup_path)
        if not path.exists():
            return False, "Backup file not found"

        if not zipfile.is_zipfile(backup_path):
            return False, "Not a valid ZIP file"

        with zipfile.ZipFile(backup_path, 'r') as zf:
            # Check for required files
            file_list = zf.namelist()

            if 'metadata.json' not in file_list:
                return False, "Missing metadata.json"

            if 'study.db' not in file_list:
                return False, "Missing database file"

            # Verify metadata
            try:
                metadata = json.loads(zf.read('metadata.json'))
                if 'version' not in metadata:
                    return False, "Invalid metadata format"
            except json.JSONDecodeError:
                return False, "Corrupted metadata.json"

            # Test ZIP integrity
            bad_file = zf.testzip()
            if bad_file:
                return False, f"Corrupted file in backup: {bad_file}"

        return True, "Backup is valid"

    except Exception as e:
        return False, f"Verification error: {str(e)}"


def get_backup_info(backup_path: str) -> Optional[Dict]:
    """
    Get information about a backup file.

    Args:
        backup_path: Path to the backup ZIP file

    Returns:
        Dictionary with backup info or None if invalid
    """
    try:
        path = Path(backup_path)
        if not path.exists() or not zipfile.is_zipfile(backup_path):
            return None

        with zipfile.ZipFile(backup_path, 'r') as zf:
            metadata = json.loads(zf.read('metadata.json'))

            # Count images in backup
            image_files = [f for f in zf.namelist() if f.startswith('images/')]

            return {
                'filename': path.name,
                'path': str(path),
                'size_bytes': path.stat().st_size,
                'size_mb': path.stat().st_size / (1024 * 1024),
                'created_at': metadata.get('created_at'),
                'version': metadata.get('version'),
                'counts': metadata.get('counts', {}),
                'image_count': len(image_files),
                'modified_time': datetime.fromtimestamp(path.stat().st_mtime)
            }
    except Exception:
        return None


def list_local_backups() -> List[Dict]:
    """
    List all local backup files.

    Returns:
        List of backup info dictionaries, sorted by date (newest first)
    """
    ensure_backup_dir()
    backups = []

    for backup_file in BACKUPS_PATH.glob('*.zip'):
        info = get_backup_info(str(backup_file))
        if info:
            backups.append(info)

    # Sort by modified time, newest first
    backups.sort(key=lambda x: x['modified_time'], reverse=True)
    return backups


def restore_backup(backup_path: str, create_safety_backup: bool = True) -> Tuple[bool, str]:
    """
    Restore from a backup file.

    Args:
        backup_path: Path to the backup ZIP file
        create_safety_backup: If True, create a safety backup before restoring

    Returns:
        Tuple of (success, message)
    """
    # Verify the backup first
    is_valid, verify_msg = verify_backup_integrity(backup_path)
    if not is_valid:
        return False, f"Cannot restore: {verify_msg}"

    try:
        # Create safety backup of current data
        if create_safety_backup and DB_PATH.exists():
            safety_success, safety_msg, safety_path = create_backup("pre_restore_safety")
            if not safety_success:
                return False, f"Failed to create safety backup: {safety_msg}"

        # Extract to temporary directory first
        temp_dir = BACKUPS_PATH / f"restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(temp_dir)

            # Verify extracted database
            extracted_db = temp_dir / 'study.db'
            if not extracted_db.exists():
                raise Exception("Extracted database not found")

            # Test database integrity
            conn = sqlite3.connect(str(extracted_db))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            conn.close()

            if integrity_result != 'ok':
                raise Exception(f"Database integrity check failed: {integrity_result}")

            # Replace current database
            if DB_PATH.exists():
                DB_PATH.unlink()
            shutil.copy2(extracted_db, DB_PATH)

            # Replace images
            extracted_images = temp_dir / 'images' / 'notes'
            if extracted_images.exists():
                # Clear current images (except .gitkeep)
                if IMAGES_PATH.exists():
                    for img in IMAGES_PATH.glob('*'):
                        if img.name != '.gitkeep':
                            img.unlink()
                else:
                    IMAGES_PATH.mkdir(parents=True, exist_ok=True)

                # Copy restored images
                for img in extracted_images.glob('*'):
                    if img.is_file():
                        shutil.copy2(img, IMAGES_PATH / img.name)

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            return True, "Backup restored successfully"

        except Exception as e:
            # Clean up temp directory on failure
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise e

    except Exception as e:
        return False, f"Restore failed: {str(e)}"


def delete_backup(backup_path: str) -> Tuple[bool, str]:
    """
    Delete a local backup file.

    Args:
        backup_path: Path to the backup file

    Returns:
        Tuple of (success, message)
    """
    try:
        path = Path(backup_path)
        if not path.exists():
            return False, "Backup file not found"

        if not str(path.resolve()).startswith(str(BACKUPS_PATH.resolve())):
            return False, "Cannot delete files outside backup directory"

        path.unlink()
        return True, "Backup deleted"

    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def cleanup_old_backups(keep_count: int = 5) -> Tuple[int, str]:
    """
    Remove old backups, keeping only the most recent ones.

    Args:
        keep_count: Number of recent backups to keep

    Returns:
        Tuple of (deleted_count, message)
    """
    backups = list_local_backups()

    if len(backups) <= keep_count:
        return 0, f"No cleanup needed ({len(backups)} backups exist)"

    # Get backups to delete (oldest ones beyond keep_count)
    to_delete = backups[keep_count:]
    deleted = 0

    for backup in to_delete:
        success, _ = delete_backup(backup['path'])
        if success:
            deleted += 1

    return deleted, f"Deleted {deleted} old backup(s), kept {keep_count} most recent"


def export_backup_to_path(backup_path: str, export_path: str) -> Tuple[bool, str]:
    """
    Copy a backup file to an external location.

    Args:
        backup_path: Path to the backup file
        export_path: Destination path

    Returns:
        Tuple of (success, message)
    """
    try:
        src = Path(backup_path)
        dst = Path(export_path)

        if not src.exists():
            return False, "Backup file not found"

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        return True, f"Backup exported to {dst}"

    except Exception as e:
        return False, f"Export failed: {str(e)}"


def import_backup_from_path(source_path: str) -> Tuple[bool, str, Optional[str]]:
    """
    Import a backup file from an external location.

    Args:
        source_path: Path to the external backup file

    Returns:
        Tuple of (success, message, local_path)
    """
    try:
        src = Path(source_path)

        if not src.exists():
            return False, "Source file not found", None

        # Verify it's a valid backup
        is_valid, verify_msg = verify_backup_integrity(str(src))
        if not is_valid:
            return False, f"Invalid backup file: {verify_msg}", None

        # Copy to local backups directory
        ensure_backup_dir()
        dst = BACKUPS_PATH / src.name

        # Handle duplicate names
        if dst.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = BACKUPS_PATH / f"{src.stem}_{timestamp}{src.suffix}"

        shutil.copy2(src, dst)
        return True, f"Backup imported successfully", str(dst)

    except Exception as e:
        return False, f"Import failed: {str(e)}", None
