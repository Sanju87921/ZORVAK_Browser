"""
GAVIX Browser - Main Application Shell (Step 4 - Storage, Bookmarks, History Integrated).
"""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QToolButton,
    QProgressBar,
    QLabel,
    QStatusBar,
    QMessageBox
)

from gavix_browser.theme import GavixColors, get_app_stylesheet
from gavix_browser.navigation import resolve_address_input, is_search_query
from gavix_browser.tabs import GavixTabWidget, GavixTab
from gavix_browser.storage import GavixStorage
from gavix_browser.storage_dialogs import (
    GavixBookmarksDialog,
    GavixHistoryDialog,
    GavixClearDataDialog
)
from gavix_browser.ai_panel import GavixAiPanel


class GavixMainWindow(QMainWindow):
    """Primary desktop browser window for GAVIX."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GAVIX — Gateway for Advanced Virtual Internet Experience")
        self.resize(1280, 800)
        self.setMinimumSize(960, 600)

        # Initialize local SQLite storage
        self.storage = GavixStorage()

        # Apply global theme
        self.setStyleSheet(get_app_stylesheet())

        # Load app icon if available
        self._set_app_icon()

        # Build UI layout
        self._init_ui()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Open initial default tab with GAVIX Home
        self.tab_widget.new_tab()

    def _set_app_icon(self):
        """Loads GAVIX emblem/banner icon if present."""
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        for candidate in ["gavix_icon.png", "gavix_banner.png", "bg_image.png"]:
            icon_path = assets_dir / candidate
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

    def _init_ui(self):
        """Builds the main window visual hierarchy."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Navigation Bar (Chrome)
        self.top_bar = self._create_top_bar()
        root_layout.addWidget(self.top_bar)

        # 2. Loading Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        root_layout.addWidget(self.progress_bar)

        # 3. Main Workspace Area (Nav Rail + Multi-Tab Viewport)
        workspace = QWidget(self)
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        # 3A. Left Navigation Rail
        self.nav_rail = self._create_nav_rail()
        workspace_layout.addWidget(self.nav_rail)

        # 3B. Multi-Tab Container
        self.tab_widget = GavixTabWidget(self)
        self.tab_widget.tab_state_changed.connect(self._sync_active_tab)
        self.tab_widget.tab_created.connect(self._bind_tab_signals)
        workspace_layout.addWidget(self.tab_widget, stretch=1)

        # 3C. Right AI Assistant Side Panel (Collapsible)
        self.ai_panel = GavixAiPanel(self)
        self.ai_panel.close_requested.connect(self._on_toggle_ai_panel)
        self.ai_panel.hide()  # Collapsed by default
        workspace_layout.addWidget(self.ai_panel)

        root_layout.addWidget(workspace, stretch=1)

        # 4. Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("GAVIX Ready — System Online")

    def _create_top_bar(self) -> QWidget:
        """Creates the top chrome toolbar containing navigation and address input."""
        top_bar = QWidget(self)
        top_bar.setObjectName("TopBar")
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Brand Emblem Logo
        brand_label = QLabel(top_bar)
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        icon_path = assets_dir / "gavix_icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            brand_label.setPixmap(pixmap)
            brand_label.setToolTip("GAVIX Browser")
            brand_label.setStyleSheet("padding-right: 4px;")
        else:
            brand_label.setText("GAVIX")
            brand_label.setStyleSheet(
                f"color: {GavixColors.EMERALD}; font-weight: 800; font-size: 14px; letter-spacing: 2px; padding-right: 6px;"
            )
        layout.addWidget(brand_label)

        # Navigation Controls Cluster
        self.btn_back = QToolButton(top_bar)
        self.btn_back.setText("◀")
        self.btn_back.setToolTip("Back (Alt+Left)")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._on_back_clicked)
        layout.addWidget(self.btn_back)

        self.btn_forward = QToolButton(top_bar)
        self.btn_forward.setText("▶")
        self.btn_forward.setToolTip("Forward (Alt+Right)")
        self.btn_forward.setEnabled(False)
        self.btn_forward.clicked.connect(self._on_forward_clicked)
        layout.addWidget(self.btn_forward)

        self.btn_reload = QToolButton(top_bar)
        self.btn_reload.setText("↻")
        self.btn_reload.setToolTip("Reload (Ctrl+R)")
        self.btn_reload.clicked.connect(self._on_reload_clicked)
        layout.addWidget(self.btn_reload)

        self.btn_home = QToolButton(top_bar)
        self.btn_home.setText("⌂")
        self.btn_home.setToolTip("Home (GAVIX New Tab)")
        self.btn_home.clicked.connect(self._on_home_clicked)
        layout.addWidget(self.btn_home)

        # Address Bar / Omnibox
        self.address_bar = QLineEdit(top_bar)
        self.address_bar.setObjectName("AddressBar")
        self.address_bar.setPlaceholderText("Search with GAVIX or enter web address...")
        self.address_bar.returnPressed.connect(self._on_address_entered)
        layout.addWidget(self.address_bar, stretch=1)

        # Action Buttons Cluster
        self.btn_bookmark = QToolButton(top_bar)
        self.btn_bookmark.setText("★")
        self.btn_bookmark.setToolTip("Bookmark this page (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self._on_bookmark_toggle_clicked)
        layout.addWidget(self.btn_bookmark)

        self.btn_clear_data = QToolButton(top_bar)
        self.btn_clear_data.setText("🧹")
        self.btn_clear_data.setToolTip("Clear Browsing Data")
        self.btn_clear_data.clicked.connect(self._on_clear_data_clicked)
        layout.addWidget(self.btn_clear_data)

        self.btn_settings = QToolButton(top_bar)
        self.btn_settings.setText("⚙")
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.clicked.connect(self._on_clear_data_clicked)
        layout.addWidget(self.btn_settings)

        return top_bar

    def _create_nav_rail(self) -> QWidget:
        """Creates the left navigation rail according to specification."""
        rail = QWidget(self)
        rail.setObjectName("NavRail")
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.setSpacing(10)

        self.rail_home = QToolButton(rail)
        self.rail_home.setText("⌂\nHome")
        self.rail_home.setProperty("active", "true")
        self.rail_home.clicked.connect(self._on_home_clicked)
        layout.addWidget(self.rail_home)

        self.rail_ai = QToolButton(rail)
        self.rail_ai.setText("✦\nAI")
        self.rail_ai.setToolTip("Toggle GAVIX AI Assistant (Ctrl+I)")
        self.rail_ai.clicked.connect(self._on_toggle_ai_panel)
        layout.addWidget(self.rail_ai)

        self.rail_bookmarks = QToolButton(rail)
        self.rail_bookmarks.setText("★\nMarks")
        self.rail_bookmarks.setToolTip("Bookmarks (Ctrl+B)")
        self.rail_bookmarks.clicked.connect(self._on_open_bookmarks_dialog)
        layout.addWidget(self.rail_bookmarks)

        self.rail_history = QToolButton(rail)
        self.rail_history.setText("⏱\nHistory")
        self.rail_history.setToolTip("Browsing History (Ctrl+H)")
        self.rail_history.clicked.connect(self._on_open_history_dialog)
        layout.addWidget(self.rail_history)

        self.rail_downloads = QToolButton(rail)
        self.rail_downloads.setText("↓\nDown")
        self.rail_downloads.setToolTip("Downloads (Ctrl+J)")
        layout.addWidget(self.rail_downloads)

        layout.addStretch()

        self.rail_settings = QToolButton(rail)
        self.rail_settings.setText("⚙\nConfig")
        self.rail_settings.setToolTip("Settings & Privacy")
        self.rail_settings.clicked.connect(self._on_clear_data_clicked)
        layout.addWidget(self.rail_settings)

        return rail

    def _setup_shortcuts(self):
        """Configures standard desktop browser keyboard shortcuts."""
        QShortcut(QKeySequence("Ctrl+T"), self, self._on_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self._on_close_current_tab)
        QShortcut(QKeySequence("Ctrl+L"), self, self._on_focus_address_bar)
        QShortcut(QKeySequence("Ctrl+R"), self, self._on_reload_clicked)
        QShortcut(QKeySequence("F5"), self, self._on_reload_clicked)
        QShortcut(QKeySequence("Alt+Left"), self, self._on_back_clicked)
        QShortcut(QKeySequence("Alt+Right"), self, self._on_forward_clicked)
        QShortcut(QKeySequence("Ctrl+D"), self, self._on_bookmark_toggle_clicked)
        QShortcut(QKeySequence("Ctrl+H"), self, self._on_open_history_dialog)
        QShortcut(QKeySequence("Ctrl+B"), self, self._on_open_bookmarks_dialog)
        QShortcut(QKeySequence("Ctrl+I"), self, self._on_toggle_ai_panel)

    @property
    def current_tab(self) -> GavixTab | None:
        return self.tab_widget.current_gavix_tab()

    @property
    def web_view(self):
        if self.current_tab:
            return self.current_tab.web_view
        return None

    def _bind_tab_signals(self, tab: GavixTab):
        """Binds signals once per tab to avoid duplicate handlers."""
        tab.url_updated.connect(self._on_tab_url_updated)
        tab.title_updated.connect(self._on_tab_title_updated)
        tab.progress_updated.connect(self._on_tab_progress_updated)
        tab.loading_started.connect(self._on_tab_loading_started)
        tab.loading_finished.connect(lambda ok, t=tab: self._on_tab_loading_finished(ok, t))

    def _sync_active_tab(self):
        """Synchronizes address bar, title, and buttons with the currently selected tab."""
        tab = self.current_tab
        if not tab:
            return

        # Update address bar
        if tab.is_home:
            self.address_bar.setText("")
            self.setWindowTitle("GAVIX — Gateway for Advanced Virtual Internet Experience")
            self._update_bookmark_icon(False)
        else:
            url_str = tab.web_view.url().toString()
            self.address_bar.setText(url_str)
            title = tab.web_view.title()
            if title:
                self.setWindowTitle(f"{title} — GAVIX")
            self._update_bookmark_icon(self.storage.is_bookmarked(url_str))

        # Update navigation buttons
        self._update_nav_buttons()

    def _update_nav_buttons(self):
        """Safely updates back/forward button states from active tab."""
        tab = self.current_tab
        if tab and hasattr(tab, "web_view") and tab.web_view:
            page = tab.web_view.page()
            if page:
                history = page.history()
                if history:
                    self.btn_back.setEnabled(history.canGoBack())
                    self.btn_forward.setEnabled(history.canGoForward())
                    return
        self.btn_back.setEnabled(False)
        self.btn_forward.setEnabled(False)

    def _update_bookmark_icon(self, is_saved: bool):
        """Updates the top bar bookmark icon based on current page status."""
        if is_saved:
            self.btn_bookmark.setStyleSheet(f"color: {GavixColors.EMERALD}; font-weight: bold;")
            self.btn_bookmark.setToolTip("Bookmarked! Click to remove (Ctrl+D)")
        else:
            self.btn_bookmark.setStyleSheet("")
            self.btn_bookmark.setToolTip("Bookmark this page (Ctrl+D)")

    # --- Tab Event Handlers ---

    def _on_tab_url_updated(self, url_str: str):
        sender_tab = self.sender()
        if sender_tab == self.current_tab:
            self.address_bar.setText(url_str)
            self._update_nav_buttons()
            self._update_bookmark_icon(self.storage.is_bookmarked(url_str))

    def _on_tab_title_updated(self, title: str):
        sender_tab = self.sender()
        if sender_tab == self.current_tab:
            if sender_tab.is_home:
                self.setWindowTitle("GAVIX — Gateway for Advanced Virtual Internet Experience")
            elif title:
                self.setWindowTitle(f"{title} — GAVIX")

    def _on_tab_loading_started(self):
        sender_tab = self.sender()
        if sender_tab == self.current_tab:
            self.btn_reload.setText("✕")
            self.btn_reload.setToolTip("Stop loading (Esc)")
            self.progress_bar.setValue(10)
            self.progress_bar.show()
            self.status_bar.showMessage("Connecting...")

    def _on_tab_progress_updated(self, progress: int):
        sender_tab = self.sender()
        if sender_tab == self.current_tab:
            self.progress_bar.setValue(progress)
            self.status_bar.showMessage(f"Loading... {progress}%")

    def _on_tab_loading_finished(self, success: bool, tab: GavixTab):
        # Record into history on completed load
        if success and not tab.is_home:
            url_str = tab.web_view.url().toString()
            title_str = tab.web_view.title() or url_str
            self.storage.add_history_entry(url_str, title_str, status="success")

        if tab == self.current_tab:
            self.btn_reload.setText("↻")
            self.btn_reload.setToolTip("Reload (Ctrl+R)")
            self.progress_bar.hide()
            self.progress_bar.setValue(0)
            self._update_nav_buttons()

            if success:
                self.status_bar.showMessage("Done", 3000)
            else:
                self.status_bar.showMessage("Navigation interrupted or page failed to load", 4000)

    # --- Slot Handlers ---

    def _on_new_tab(self):
        self.tab_widget.new_tab()

    def _on_close_current_tab(self):
        curr_idx = self.tab_widget.currentIndex()
        if curr_idx != -1:
            self.tab_widget.close_tab(curr_idx)

    def _on_focus_address_bar(self):
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def _on_address_entered(self):
        """Resolves address bar input and routes active tab."""
        tab = self.current_tab
        if not tab:
            return

        text = self.address_bar.text().strip()
        if not text:
            return

        is_query, target = is_search_query(text)
        if is_query:
            tab.execute_search(target)
        else:
            tab.navigate_to(target)

    def _on_back_clicked(self):
        if self.current_tab and self.current_tab.web_view:
            self.current_tab.web_view.back()

    def _on_forward_clicked(self):
        if self.current_tab and self.current_tab.web_view:
            self.current_tab.web_view.forward()

    def _on_reload_clicked(self):
        if not self.current_tab or not self.current_tab.web_view:
            return

        if self.btn_reload.text() == "✕":
            self.current_tab.web_view.stop()
        else:
            self.current_tab.web_view.reload()

    def _on_home_clicked(self):
        if self.current_tab:
            self.current_tab.load_home()

    def _on_bookmark_toggle_clicked(self):
        tab = self.current_tab
        if not tab or tab.is_home:
            return

        url_str = tab.web_view.url().toString()
        title_str = tab.web_view.title() or url_str

        if self.storage.is_bookmarked(url_str):
            self.storage.remove_bookmark(url_str)
            self._update_bookmark_icon(False)
            self.status_bar.showMessage("Bookmark removed", 3000)
        else:
            self.storage.add_bookmark(url_str, title_str)
            self._update_bookmark_icon(True)
            self.status_bar.showMessage("Page bookmarked ★", 3000)

    def _on_open_bookmarks_dialog(self):
        dialog = GavixBookmarksDialog(self.storage, self)
        dialog.open_url_requested.connect(lambda url: self.current_tab.navigate_to(url) if self.current_tab else None)
        dialog.exec()

    def _on_open_history_dialog(self):
        dialog = GavixHistoryDialog(self.storage, self)
        dialog.open_url_requested.connect(lambda url: self.current_tab.navigate_to(url) if self.current_tab else None)
        dialog.exec()

    def _on_clear_data_clicked(self):
        profile = None
        if self.current_tab and hasattr(self.current_tab.web_view, "_profile"):
            profile = self.current_tab.web_view._profile
        dialog = GavixClearDataDialog(self.storage, web_profile=profile, parent=self)
        dialog.data_cleared.connect(self._sync_active_tab)
        dialog.exec()

    def _on_toggle_ai_panel(self):
        """Toggles visibility of the GAVIX AI Side Panel."""
        if self.ai_panel.isHidden():
            self.ai_panel.show()
            self.status_bar.showMessage("GAVIX AI Panel Opened", 2500)
        else:
            self.ai_panel.hide()
            self.status_bar.showMessage("GAVIX AI Panel Closed", 2500)
