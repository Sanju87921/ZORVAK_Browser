"""
GAVIX Browser - Download Manager Component.
Handles QWebEngineProfile downloadRequested events with progress tracking,
filename sanitization (path traversal protection), and safe folder opening.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QWidget,
    QFrame
)
from gavix_browser.theme import GavixColors


def sanitize_filename(filename: str) -> str:
    """Removes path traversal and illegal characters from suggested filenames."""
    # Strip directory components
    name = os.path.basename(filename).strip()
    # Strip illegal Windows characters: < > : " / \ | ? *
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return clean_name or "downloaded_file"


@dataclass
class DownloadItemState:
    id: int
    filename: str
    path: str
    total_bytes: int = 0
    received_bytes: int = 0
    state: str = "downloading"  # downloading, completed, cancelled, interrupted


class GavixDownloadManager(QObject):
    """Manages live downloads and tracks progress."""

    download_started = Signal(int, str)  # (id, filename)
    download_progress = Signal(int, int, int)  # (id, received, total)
    download_finished = Signal(int, bool)  # (id, success)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._downloads: Dict[int, DownloadItemState] = {}
        self._active_requests: Dict[int, QWebEngineDownloadRequest] = {}
        self._counter = 0

    def get_default_download_directory(self) -> str:
        """Returns the user's standard Downloads folder on Windows."""
        return str(Path.home() / "Downloads")

    def handle_download_request(self, download_item: QWebEngineDownloadRequest):
        """Hooked into QWebEngineProfile.downloadRequested."""
        self._counter += 1
        d_id = self._counter

        suggested_name = sanitize_filename(download_item.downloadFileName())
        dest_folder = self.get_default_download_directory()
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, suggested_name)

        # Handle file overwrite collision safely
        base, ext = os.path.splitext(suggested_name)
        collision_idx = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_folder, f"{base} ({collision_idx}){ext}")
            collision_idx += 1

        download_item.setDownloadDirectory(dest_folder)
        download_item.setDownloadFileName(os.path.basename(dest_path))

        state = DownloadItemState(
            id=d_id,
            filename=os.path.basename(dest_path),
            path=dest_path,
            total_bytes=download_item.totalBytes(),
            received_bytes=download_item.receivedBytes()
        )
        self._downloads[d_id] = state
        self._active_requests[d_id] = download_item

        # Connect download item Qt signals
        download_item.receivedBytesChanged.connect(lambda: self._on_bytes_changed(d_id))
        download_item.totalBytesChanged.connect(lambda: self._on_bytes_changed(d_id))
        download_item.stateChanged.connect(lambda: self._on_state_changed(d_id))

        download_item.accept()
        self.download_started.emit(d_id, state.filename)

    def _on_bytes_changed(self, d_id: int):
        req = self._active_requests.get(d_id)
        item = self._downloads.get(d_id)
        if req and item:
            item.received_bytes = req.receivedBytes()
            item.total_bytes = req.totalBytes()
            self.download_progress.emit(d_id, item.received_bytes, item.total_bytes)

    def _on_state_changed(self, d_id: int):
        req = self._active_requests.get(d_id)
        item = self._downloads.get(d_id)
        if not req or not item:
            return

        qt_state = req.state()
        if qt_state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            item.state = "completed"
            self.download_finished.emit(d_id, True)
        elif qt_state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            item.state = "cancelled"
            self.download_finished.emit(d_id, False)
        elif qt_state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            item.state = "interrupted"
            self.download_finished.emit(d_id, False)

    def get_downloads(self) -> List[DownloadItemState]:
        return list(reversed(list(self._downloads.values())))


class GavixDownloadsDialog(QDialog):
    """Modal dialog displaying active and completed downloads."""

    def __init__(self, manager: GavixDownloadManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Downloads — GAVIX")
        self.resize(600, 440)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GavixColors.BG_MAIN};
                color: {GavixColors.TEXT_PRIMARY};
            }}
        """)
        self._init_ui()
        self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("↓ File Downloads", self)
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {GavixColors.EMERALD};")
        layout.addWidget(header)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.container_widget = QWidget()
        self.items_layout = QVBoxLayout(self.container_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(8)
        scroll.setWidget(self.container_widget)

        layout.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        btn_open_folder = QPushButton("Open Downloads Folder", self)
        btn_open_folder.setStyleSheet(f"background-color: {GavixColors.BG_RAISED}; color: {GavixColors.EMERALD};")
        btn_open_folder.clicked.connect(self._on_open_folder_clicked)
        btn_row.addWidget(btn_open_folder)

        btn_row.addStretch()

        btn_close = QPushButton("Close", self)
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

    def _refresh(self):
        # Clear existing items
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        items = self.manager.get_downloads()
        if not items:
            lbl = QLabel("No downloads recorded in this session.", self.container_widget)
            lbl.setStyleSheet(f"color: {GavixColors.TEXT_MUTED}; font-size: 13px; padding: 20px;")
            self.items_layout.addWidget(lbl)
            self.items_layout.addStretch()
            return

        for item in items:
            card = QFrame(self.container_widget)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {GavixColors.BG_SURFACE};
                    border: 1px solid {GavixColors.BORDER_SUBTLE};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(8, 8, 8, 8)
            c_layout.setSpacing(6)

            top = QHBoxLayout()
            name_lbl = QLabel(item.filename, card)
            name_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
            top.addWidget(name_lbl, stretch=1)

            status_lbl = QLabel(item.state.upper(), card)
            status_color = GavixColors.EMERALD if item.state == "completed" else GavixColors.CYAN
            status_lbl.setStyleSheet(f"color: {status_color}; font-size: 11px; font-weight: bold;")
            top.addWidget(status_lbl)
            c_layout.addLayout(top)

            if item.state == "downloading" and item.total_bytes > 0:
                pbar = QProgressBar(card)
                pbar.setFixedHeight(4)
                pbar.setTextVisible(False)
                pbar.setMaximum(item.total_bytes)
                pbar.setValue(item.received_bytes)
                c_layout.addWidget(pbar)

            path_lbl = QLabel(item.path, card)
            path_lbl.setStyleSheet(f"color: {GavixColors.TEXT_MUTED}; font-size: 11px;")
            c_layout.addWidget(path_lbl)

            self.items_layout.addWidget(card)

        self.items_layout.addStretch()

    def _on_open_folder_clicked(self):
        folder = self.manager.get_default_download_directory()
        if os.path.exists(folder):
            os.startfile(folder)
