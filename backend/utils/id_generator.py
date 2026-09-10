"""
ID Generator
=============
Thread-safe sequential ID generators for application and document IDs.
Format: APP-XXXX, DOC-XXXX (zero-padded 4-digit).
"""

import threading
import uuid


class SequentialIDGenerator:
    """Thread-safe sequential ID generator with a prefix."""

    def __init__(self, prefix: str, start: int = 1):
        self._prefix = prefix
        self._counter = start
        self._lock = threading.Lock()

    def next_id(self) -> str:
        """Generate the next sequential ID."""
        with self._lock:
            current = self._counter
            self._counter += 1
        return f"{self._prefix}-{current:04d}"


# Global generators
application_id_generator = SequentialIDGenerator("APP")
document_id_generator = SequentialIDGenerator("DOC")


def generate_application_id() -> str:
    """Generate a new application ID (APP-XXXX)."""
    return application_id_generator.next_id()


def generate_document_id() -> str:
    """Generate a new document ID (DOC-XXXX)."""
    return document_id_generator.next_id()


def generate_unique_id() -> str:
    """Generate a UUID for cases where sequential IDs aren't needed."""
    return str(uuid.uuid4())
