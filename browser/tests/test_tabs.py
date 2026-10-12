"""
Unit and integration tests for GAVIX Tabs and Home Page.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.tabs import GavixTabWidget, GavixTab
from gavix_browser.home_page import get_home_page_html
from gavix_browser.app_shell import GavixMainWindow


def test_home_page_html_generation():
    html = get_home_page_html()
    assert "<!DOCTYPE html>" in html
    assert "GAVIX" in html
    assert "Gateway for Advanced Virtual Internet Experience" in html
    assert "status-card" in html
    assert "shortcuts-grid" in html


def test_tab_widget_lifecycle():
    app = QApplication.instance() or QApplication(sys.argv)
    tab_widget = GavixTabWidget()
    assert tab_widget.count() == 0

    # 1. Add first tab
    tab1 = tab_widget.new_tab()
    assert tab_widget.count() == 1
    assert tab1.is_home is True

    # 2. Add second tab
    tab2 = tab_widget.new_tab("https://example.com")
    assert tab_widget.count() == 2
    assert tab_widget.currentIndex() == 1

    # 3. Close tab
    tab_widget.close_tab(1)
    assert tab_widget.count() == 1

    # 4. Closing the last tab automatically creates a fresh new tab fallback
    tab_widget.close_tab(0)
    assert tab_widget.count() == 1  # Should not be 0; auto-respawns new tab

    tab_widget.close()


def test_main_window_with_tabs():
    app = QApplication.instance() or QApplication(sys.argv)
    window = GavixMainWindow()
    assert window.tab_widget.count() >= 1
    assert window.current_tab is not None
    window.close()
