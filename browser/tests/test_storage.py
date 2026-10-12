"""
Unit tests for GAVIX SQLite storage: Bookmarks, History, and Settings.
"""

import sys
import os
import gc
import tempfile
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.storage import GavixStorage


def _safe_remove(path: str):
    gc.collect()
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def test_bookmarks_crud():
    temp_fd, temp_db = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    try:
        storage = GavixStorage(db_path=temp_db)
        assert len(storage.get_bookmarks()) == 0

        # Add bookmark
        res = storage.add_bookmark("https://gavix.org", "GAVIX Platform")
        assert res is True
        assert storage.is_bookmarked("https://gavix.org") is True

        # Duplicates update title instead of erroring
        storage.add_bookmark("https://gavix.org", "GAVIX Updated Title")
        bookmarks = storage.get_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0]["title"] == "GAVIX Updated Title"

        # Delete bookmark
        deleted = storage.remove_bookmark("https://gavix.org")
        assert deleted is True
        assert storage.is_bookmarked("https://gavix.org") is False
        assert len(storage.get_bookmarks()) == 0
    finally:
        _safe_remove(temp_db)


def test_history_crud_and_clearing():
    temp_fd, temp_db = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    try:
        storage = GavixStorage(db_path=temp_db)
        assert len(storage.get_history()) == 0

        # Add visits
        storage.add_history_entry("https://example.com", "Example Domain", "success")
        storage.add_history_entry("https://wikipedia.org", "Wikipedia", "success")

        history = storage.get_history()
        assert len(history) == 2
        # Most recent first
        assert history[0]["url"] == "https://wikipedia.org"

        # Filter out internal/empty pages
        assert storage.add_history_entry("about:blank", "") is False
        assert storage.add_history_entry("file:///assets/home.html", "") is False

        # Clear history
        cleared_count = storage.clear_history()
        assert cleared_count == 2
        assert len(storage.get_history()) == 0
    finally:
        _safe_remove(temp_db)


def test_settings_persistence():
    temp_fd, temp_db = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    try:
        storage = GavixStorage(db_path=temp_db)
        assert storage.get_setting("search_engine", "default") == "default"

        storage.set_setting("search_engine", "gavix_v1")
        assert storage.get_setting("search_engine") == "gavix_v1"
    finally:
        _safe_remove(temp_db)
