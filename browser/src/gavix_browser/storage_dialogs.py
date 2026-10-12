"""
GAVIX Browser - Data Management and History/Bookmarks Dialogs.
Provides clean dark-themed modal interfaces for inspecting and managing
Bookmarks, History, and Clear Browsing Data with honest scope descriptions.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QCheckBox,
    QFrame
)
from gavix_browser.storage import GavixStorage
from gavix_browser.theme import GavixColors


class GavixBookmarksDialog(QDialog):
    """Modal dialog displaying local saved bookmarks."""

    open_url_requested = Signal(str)

    def __init__(self, storage: GavixStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("Bookmarks — GAVIX")
        self.resize(600, 480)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GavixColors.BG_MAIN};
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QListWidget {{
                background-color: {GavixColors.BG_SURFACE};
                border: 1px solid {GavixColors.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 6px;
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {GavixColors.BG_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {GavixColors.BG_RAISED};
                color: {GavixColors.EMERALD};
            }}
        """)
        self._init_ui()
        self._load_bookmarks()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("★ Saved Bookmarks", self)
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {GavixColors.EMERALD};")
        layout.addWidget(header)

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget, stretch=1)

        btn_row = QHBoxLayout()
        self.btn_open = QPushButton("Open in Tab", self)
        self.btn_open.setStyleSheet(f"background-color: {GavixColors.BG_RAISED}; color: {GavixColors.EMERALD};")
        self.btn_open.clicked.connect(self._on_open_clicked)
        btn_row.addWidget(self.btn_open)

        self.btn_delete = QPushButton("Delete Bookmark", self)
        self.btn_delete.setStyleSheet("background-color: rgba(239, 68, 68, 0.2); color: #EF4444;")
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        btn_row.addWidget(self.btn_delete)

        btn_row.addStretch()

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

    def _load_bookmarks(self):
        self.list_widget.clear()
        bookmarks = self.storage.get_bookmarks()
        if not bookmarks:
            item = QListWidgetItem("No saved bookmarks yet.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return

        for b in bookmarks:
            title = b["title"] or b["url"]
            item = QListWidgetItem(f"{title}\n{b['url']}")
            item.setData(Qt.ItemDataRole.UserRole, b["url"])
            self.list_widget.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.open_url_requested.emit(url)
            self.close()

    def _on_open_clicked(self):
        item = self.list_widget.currentItem()
        if item:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.open_url_requested.emit(url)
                self.close()

    def _on_delete_clicked(self):
        item = self.list_widget.currentItem()
        if item:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url and self.storage.remove_bookmark(url):
                self._load_bookmarks()


class GavixHistoryDialog(QDialog):
    """Modal dialog displaying local browsing history."""

    open_url_requested = Signal(str)

    def __init__(self, storage: GavixStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("Browsing History — GAVIX")
        self.resize(680, 520)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GavixColors.BG_MAIN};
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QListWidget {{
                background-color: {GavixColors.BG_SURFACE};
                border: 1px solid {GavixColors.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 6px;
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {GavixColors.BG_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {GavixColors.BG_RAISED};
                color: {GavixColors.EMERALD};
            }}
        """)
        self._init_ui()
        self._load_history()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("⏱ Browsing History", self)
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {GavixColors.EMERALD};")
        layout.addWidget(header)

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget, stretch=1)

        btn_row = QHBoxLayout()
        self.btn_open = QPushButton("Open in Tab", self)
        self.btn_open.setStyleSheet(f"background-color: {GavixColors.BG_RAISED}; color: {GavixColors.EMERALD};")
        self.btn_open.clicked.connect(self._on_open_clicked)
        btn_row.addWidget(self.btn_open)

        self.btn_clear = QPushButton("Clear All History", self)
        self.btn_clear.setStyleSheet("background-color: rgba(239, 68, 68, 0.2); color: #EF4444;")
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        btn_row.addWidget(self.btn_clear)

        btn_row.addStretch()

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

    def _load_history(self):
        self.list_widget.clear()
        entries = self.storage.get_history(limit=150)
        if not entries:
            item = QListWidgetItem("No local browsing history recorded yet.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return

        for e in entries:
            title = e["title"] or e["url"]
            ts = e["visited_at"][:19].replace("T", " ")
            item = QListWidgetItem(f"{title} ({ts})\n{e['url']}")
            item.setData(Qt.ItemDataRole.UserRole, e["url"])
            self.list_widget.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.open_url_requested.emit(url)
            self.close()

    def _on_open_clicked(self):
        item = self.list_widget.currentItem()
        if item:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.open_url_requested.emit(url)
                self.close()

    def _on_clear_clicked(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear History",
            "Are you sure you want to delete all local history records? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_history()
            self._load_history()


class GavixClearDataDialog(QDialog):
    """Modal dialog allowing users to selectively clear local browsing data."""

    data_cleared = Signal()

    def __init__(self, storage: GavixStorage, web_profile=None, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.web_profile = web_profile
        self.setWindowTitle("Clear Browsing Data — GAVIX")
        self.resize(460, 320)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GavixColors.BG_MAIN};
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QCheckBox {{
                font-size: 13px;
                padding: 4px;
            }}
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QLabel("Clear Browsing Data", self)
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {GavixColors.EMERALD};")
        layout.addWidget(header)

        desc = QLabel("Select which local data items you wish to remove from this device:", self)
        desc.setStyleSheet(f"color: {GavixColors.TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(desc)

        self.chk_history = QCheckBox("Browsing History (Local SQLite visit records)", self)
        self.chk_history.setChecked(True)
        layout.addWidget(self.chk_history)

        self.chk_cache = QCheckBox("Cached Web Data (Temporary page assets)", self)
        self.chk_cache.setChecked(True)
        layout.addWidget(self.chk_cache)

        self.chk_cookies = QCheckBox("Cookies & Site Data (Website sign-ins and session state)", self)
        self.chk_cookies.setChecked(False)
        layout.addWidget(self.chk_cookies)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.clicked.connect(self.close)
        btn_row.addWidget(btn_cancel)

        btn_confirm = QPushButton("Clear Selected Data", self)
        btn_confirm.setStyleSheet("background-color: #EF4444; color: #FFFFFF; font-weight: bold; border-radius: 8px;")
        btn_confirm.clicked.connect(self._on_clear_confirmed)
        btn_row.addWidget(btn_confirm)

        layout.addLayout(btn_row)

    def _on_clear_confirmed(self):
        if self.chk_history.isChecked():
            self.storage.clear_history()

        if self.web_profile:
            if self.chk_cache.isChecked():
                self.web_profile.clearHttpCache()
            if self.chk_cookies.isChecked():
                cookie_store = self.web_profile.cookieStore()
                if cookie_store:
                    cookie_store.deleteAllCookies()

        QMessageBox.information(self, "Data Cleared", "Selected browsing data has been successfully cleared.")
        self.data_cleared.emit()
        self.close()
