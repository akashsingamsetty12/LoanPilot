"""
File Helper Utilities
======================
File type validation, path generation, and size checks for document uploads.

"""

from pathlib import Path
from config import get_settings


def validate_file_type(content_type: str) -> bool:
    """Check if the uploaded file's MIME type is allowed."""
    settings = get_settings()
    return content_type in settings.ALLOWED_FILE_TYPES


def validate_file_size(size: int) -> bool:
    """Check if the file size is within the allowed limit."""
    settings = get_settings()
    return size <= settings.max_file_size_bytes


def get_upload_path(app_id: str, doc_id: str, filename: str) -> Path:
    """
    Generate the storage path for an uploaded document.

    Structure: uploads/{app_id}/{doc_id}/{filename}
    """
    settings = get_settings()
    path = Path(settings.UPLOAD_DIR) / app_id / doc_id
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


def get_report_path(app_id: str) -> Path:
    """
    Generate the storage path for generated reports.

    Structure: uploads/{app_id}/reports/
    """
    settings = get_settings()
    path = Path(settings.UPLOAD_DIR) / app_id / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path
