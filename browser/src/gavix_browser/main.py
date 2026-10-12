"""
GAVIX Browser - Main Entrypoint.
Initializes the Qt runtime, configures high DPI scaling, and launches the App Shell.
"""

import sys
import os
from pathlib import Path

# Add src directory to sys.path to allow execution directly from terminal
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from gavix_browser.app_shell import GavixMainWindow


def main():
    """Main application routine."""
    # Ensure High-DPI support on Windows
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("GAVIX")
    app.setOrganizationName("GavixNetwork")
    app_font = app.font()
    app_font.setPointSize(10)
    app.setFont(app_font)

    window = GavixMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
