"""
Unit tests for GAVIX Download Manager and Sanitization.
"""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.downloads import sanitize_filename, GavixDownloadManager


def test_sanitize_filename_prevents_path_traversal():
    # Attack vectors
    assert sanitize_filename("../../../malicious.exe") == "malicious.exe"
    assert sanitize_filename("..\\..\\malicious.bat") == "malicious.bat"
    assert sanitize_filename("/etc/passwd") == "passwd"
    assert sanitize_filename("C:\\Windows\\System32\\calc.exe") == "calc.exe"


def test_sanitize_filename_strips_illegal_characters():
    assert sanitize_filename('test:file*name?.txt') == "test_file_name_.txt"
    assert sanitize_filename('<bad>|name".pdf') == "_bad__name_.pdf"


def test_download_manager_default_directory():
    manager = GavixDownloadManager()
    downloads_dir = manager.get_default_download_directory()
    assert "Downloads" in downloads_dir
    assert manager.get_downloads() == []
