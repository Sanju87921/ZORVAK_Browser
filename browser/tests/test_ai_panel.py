"""
Unit tests for GAVIX AI Side Panel.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.ai_panel import GavixAiPanel
from gavix_browser.app_shell import GavixMainWindow


def test_ai_panel_instantiation_and_defaults():
    app = QApplication.instance() or QApplication(sys.argv)
    panel = GavixAiPanel()
    assert panel is not None
    # Crucial MVP requirement: consent toggle must be OFF by default!
    assert panel.chk_use_content.isChecked() is False
    assert panel.prompt_input is not None
    assert "Standby" in panel.status_title.text()
    panel.close()


def test_ai_panel_action_click():
    app = QApplication.instance() or QApplication(sys.argv)
    panel = GavixAiPanel()

    # Trigger action without consent
    panel._on_action_clicked("Summarize page")
    assert "Action: Summarize page" in panel.status_title.text()
    assert "consent is OFF" in panel.status_text.text()

    # Turn consent ON and trigger action
    panel.chk_use_content.setChecked(True)
    panel._on_action_clicked("Summarize page")
    assert "consent enabled" in panel.status_text.text()
    panel.close()


def test_main_window_ai_panel_integration():
    app = QApplication.instance() or QApplication(sys.argv)
    window = GavixMainWindow()
    assert window.ai_panel is not None
    # Panel is hidden by default to keep the web viewport wide
    assert window.ai_panel.isHidden() is True

    # Toggle open (unhide)
    window._on_toggle_ai_panel()
    assert window.ai_panel.isHidden() is False

    # Toggle closed (hide)
    window._on_toggle_ai_panel()
    assert window.ai_panel.isHidden() is True

    window.close()
