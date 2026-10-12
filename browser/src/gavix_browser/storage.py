"""
GAVIX Browser - Local SQLite Storage Engine.
Manages persistent local metadata: Bookmarks, History, and Application Settings.
Strictly local to %LOCALAPPDATA%/GavixBrowser/gavix_data.db.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def get_db_path() -> str:
    """Returns the persistent SQLite database path for GAVIX."""
    app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / ".gavix"))
    base_dir = os.path.join(app_data, "GavixBrowser")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "gavix_data.db")


class GavixStorage:
    """Thread-safe SQLite manager for bookmarks, history, and settings."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def close(self):
        """No-op or cleanup if holding persistent connections."""
        pass

    def _init_db(self):
        """Initializes tables for bookmarks, history, and settings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Bookmarks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    folder TEXT DEFAULT 'Default'
                )
            """)

            # 2. History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    visited_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

            # 3. Settings Key-Value Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Bookmarks CRUD ---

    def add_bookmark(self, url: str, title: str, folder: str = "Default") -> bool:
        """Adds or updates a bookmark."""
        clean_url = url.strip()
        if not clean_url or clean_url.startswith("about:") or clean_url.endswith("home.html"):
            return False

        clean_title = title.strip() or clean_url
        now_str = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookmarks (url, title, created_at, folder)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    folder=excluded.folder
            """, (clean_url, clean_title, now_str, folder))
            conn.commit()
            return True

    def remove_bookmark(self, url: str) -> bool:
        """Removes a bookmark by URL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE url = ?", (url.strip(),))
            conn.commit()
            return cursor.rowcount > 0

    def is_bookmarked(self, url: str) -> bool:
        """Checks if a URL is currently bookmarked."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bookmarks WHERE url = ?", (url.strip(),))
            return cursor.fetchone() is not None

    def get_bookmarks(self) -> List[Dict]:
        """Returns all bookmarks ordered by creation time descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, title, created_at, folder FROM bookmarks ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    # --- History CRUD ---

    def add_history_entry(self, url: str, title: str, status: str = "success") -> bool:
        """Records a completed navigation visit."""
        clean_url = url.strip()
        if not clean_url or clean_url.startswith("about:") or clean_url.endswith("home.html") or "assets/home.html" in clean_url:
            return False

        clean_title = title.strip() or clean_url
        now_str = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (url, title, visited_at, status)
                VALUES (?, ?, ?, ?)
            """, (clean_url, clean_title, now_str, status))
            conn.commit()
            return True

    def get_history(self, limit: int = 100) -> List[Dict]:
        """Returns recent browsing history ordered by visit time descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, title, visited_at, status FROM history ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def clear_history(self) -> int:
        """Deletes all local browsing history records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
            return cursor.rowcount

    # --- Settings Key-Value ---

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
