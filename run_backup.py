"""
Study Assistant - Scheduled Backup Script
Run this script via Windows Task Scheduler for automatic daily backups.

Usage:
    python run_backup.py [--cloud] [--keep N]

Arguments:
    --cloud     Upload to Google Drive after backup
    --keep N    Keep only N most recent local backups (default: 5)
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
LOG_PATH = Path(__file__).parent / "backup_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_backup(upload_to_cloud: bool = False, keep_count: int = 5) -> bool:
    """
    Run backup and optionally upload to Google Drive.

    Args:
        upload_to_cloud: Whether to upload to Google Drive
        keep_count: Number of local backups to keep

    Returns:
        True if backup succeeded
    """
    import backup

    logger.info("=" * 50)
    logger.info("Starting scheduled backup")

    # Create local backup
    success, msg, backup_path = backup.create_backup(f"scheduled_{datetime.now().strftime('%A').lower()}")

    if not success:
        logger.error(f"Backup failed: {msg}")
        return False

    logger.info(f"Local backup created: {msg}")

    # Upload to Google Drive if specified
    if upload_to_cloud and backup_path:
        logger.info("Uploading to Google Drive...")

        try:
            from cloud.google_drive import get_client
            client = get_client()

            if client.is_authenticated():
                upload_success, upload_msg = client.upload_backup(backup_path)
                if upload_success:
                    logger.info(f"Cloud upload successful: {upload_msg}")
                else:
                    logger.error(f"Cloud upload failed: {upload_msg}")
            else:
                logger.warning("Google Drive not authenticated. Skipping upload.")
                logger.info("Connect to Google Drive via the app Settings > Backup & Sync tab first.")

        except ImportError as e:
            logger.error(f"Google Drive module import error: {e}")
        except Exception as e:
            logger.error(f"Cloud upload error: {e}")

    # Cleanup old backups
    if keep_count > 0:
        deleted, cleanup_msg = backup.cleanup_old_backups(keep_count)
        if deleted > 0:
            logger.info(f"Cleanup: {cleanup_msg}")

    logger.info("Backup completed successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Study Assistant Scheduled Backup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_backup.py                # Local backup only
    python run_backup.py --cloud        # Backup and upload to Google Drive
    python run_backup.py --keep 7       # Keep 7 most recent backups
        """
    )

    parser.add_argument(
        '--cloud',
        action='store_true',
        help='Upload backup to Google Drive'
    )

    parser.add_argument(
        '--keep',
        type=int,
        default=5,
        help='Number of local backups to keep (default: 5)'
    )

    args = parser.parse_args()

    try:
        success = run_backup(
            upload_to_cloud=args.cloud,
            keep_count=args.keep
        )
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
