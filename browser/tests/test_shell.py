"""
Basic integration test for GAVIX App Shell.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.app_shell import GavixMainWindow


def test_main_window_instantiation():
    app = QApplication.instance() or QApplication(sys.argv)
    window = GavixMainWindow()
    assert window is not None
    assert "GAVIX" in window.windowTitle()
    assert window.address_bar is not None
    assert window.web_view is not None
    assert window.btn_back is not None
    assert window.btn_forward is not None
    assert window.btn_reload is not None
    window.close()
