"""
GAVIX Browser - Main Application Shell (Step 4 - Storage, Bookmarks, History Integrated).
"""

from pathlib import Path
from PySide6.QtCore import Qt, QByteArray, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
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
from gavix_browser.downloads import GavixDownloadManager, GavixDownloadsDialog
from PySide6.QtWebEngineCore import QWebEngineProfile


class GavixMainWindow(QMainWindow):
    """Primary desktop browser window for GAVIX."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GAVIX — Gateway for Advanced Virtual Internet Experience")
        self.resize(1280, 800)
        self.setMinimumSize(960, 600)

        # Initialize local SQLite storage
        self.storage = GavixStorage()

        # Initialize Download Manager
        self.download_manager = GavixDownloadManager(self)
        QWebEngineProfile.defaultProfile().downloadRequested.connect(
            self.download_manager.handle_download_request
        )
        self.download_manager.download_started.connect(self._on_download_started)
        self.download_manager.download_finished.connect(self._on_download_finished)

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
        """Builds the main window visual hierarchy matching desktop browser chrome:
        1. Top Tab Bar (Tabs + New Tab '+' button)
        2. Navigation / Address Bar (Back, Forward, Reload, Address Input, Security & Actions)
        3. Main Workspace Area (Left Navigation Rail + Web Content Viewport)
        """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Multi-Tab Container
        self.tab_widget = GavixTabWidget(self)
        self.tab_widget.tab_state_changed.connect(self._sync_active_tab)
        self.tab_widget.tab_created.connect(self._bind_tab_signals)

        # 1. Top Tab Bar Container (Chrome tabs at the very top of the window)
        top_tab_bar_widget = QWidget(self)
        top_tab_bar_widget.setObjectName("TopTabBar")
        top_tab_layout = QHBoxLayout(top_tab_bar_widget)
        top_tab_layout.setContentsMargins(6, 4, 6, 0)
        top_tab_layout.setSpacing(0)
        top_tab_layout.addWidget(self.tab_widget.tabBar())
        root_layout.addWidget(top_tab_bar_widget)

        # 2. Top Navigation Bar (Address / Omnibox & controls)
        self.top_bar = self._create_top_bar()
        root_layout.addWidget(self.top_bar)

        # 3. Loading Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        root_layout.addWidget(self.progress_bar)

        # 4. Main Workspace Area (Left Navigation Rail + Multi-Tab Viewport)
        workspace = QWidget(self)
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        # 4A. Left Navigation Rail (Visible 78px sidebar matching reference design)
        self.nav_rail = self._create_nav_rail()
        workspace_layout.addWidget(self.nav_rail)

        # 4B. Web Viewport Content Stack
        workspace_layout.addWidget(self.tab_widget, stretch=1)

        # 4C. Right AI Assistant Side Panel (Collapsible)
        self.ai_panel = GavixAiPanel(self)
        self.ai_panel.close_requested.connect(self._on_toggle_ai_panel)
        self.ai_panel.hide()  # Collapsed by default
        workspace_layout.addWidget(self.ai_panel)

        root_layout.addWidget(workspace, stretch=1)

        # 5. Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("GAVIX Ready — System Online")

    def _create_top_bar(self) -> QWidget:
        """Creates the top chrome toolbar containing navigation and address input."""
        top_bar = QWidget(self)
        top_bar.setObjectName("TopBar")
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Sidebar Toggle (Hidden as sidebar is permanently visible)
        self.btn_sidebar = QToolButton(top_bar)
        self.btn_sidebar.setText("☰")
        self.btn_sidebar.setToolTip("Toggle Tools & Bookmarks Panel (Ctrl+M)")
        self.btn_sidebar.clicked.connect(self._on_toggle_nav_rail)
        self.btn_sidebar.hide()

        # Navigation Controls Cluster
        self.btn_back = QToolButton(top_bar)
        self.btn_back.setText("←")
        self.btn_back.setToolTip("Back (Alt+Left)")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._on_back_clicked)
        layout.addWidget(self.btn_back)

        self.btn_forward = QToolButton(top_bar)
        self.btn_forward.setText("→")
        self.btn_forward.setToolTip("Forward (Alt+Right)")
        self.btn_forward.setEnabled(False)
        self.btn_forward.clicked.connect(self._on_forward_clicked)
        layout.addWidget(self.btn_forward)

        self.btn_reload = QToolButton(top_bar)
        self.btn_reload.setText("↻")
        self.btn_reload.setToolTip("Reload (Ctrl+R)")
        self.btn_reload.clicked.connect(self._on_reload_clicked)
        layout.addWidget(self.btn_reload)

        # Address Bar / Omnibox
        self.address_bar = QLineEdit(top_bar)
        self.address_bar.setObjectName("AddressBar")
        self.address_bar.setPlaceholderText("Search GAVIX or type a URL")
        self.address_bar.returnPressed.connect(self._on_address_entered)
        layout.addWidget(self.address_bar, stretch=1)

        # GAVIX Shield Protection Indicator
        self.btn_shield = QToolButton(top_bar)
        self.btn_shield.setText("🛡")
        self.btn_shield.setToolTip("GAVIX Shield: Tracker & Ad Protection (Active)")
        self.btn_shield.setStyleSheet(f"color: {GavixColors.EMERALD}; font-size: 13px;")
        self.btn_shield.clicked.connect(self._on_shield_clicked)
        layout.addWidget(self.btn_shield)

        # Action Buttons Cluster
        self.btn_settings = QToolButton(top_bar)
        self.btn_settings.setText("⚙")
        self.btn_settings.setToolTip("Settings & Privacy")
        self.btn_settings.clicked.connect(self._on_clear_data_clicked)
        layout.addWidget(self.btn_settings)

        self.btn_bookmark = QToolButton(top_bar)
        self.btn_bookmark.setText("★")
        self.btn_bookmark.setToolTip("Bookmark this page (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self._on_bookmark_toggle_clicked)
        layout.addWidget(self.btn_bookmark)

        self.btn_downloads = QToolButton(top_bar)
        self.btn_downloads.setText("↓")
        self.btn_downloads.setToolTip("Downloads (Ctrl+J)")
        self.btn_downloads.clicked.connect(self._on_open_downloads_dialog)
        layout.addWidget(self.btn_downloads)

        self.btn_profile = QToolButton(top_bar)
        self.btn_profile.setText("👤")
        self.btn_profile.setToolTip("Profile: Default (Isolated Session)")
        layout.addWidget(self.btn_profile)

        return top_bar

    def _create_nav_icon(self, svg_body: str, stroke_width: str = "2", is_active: bool = False) -> QIcon:
        """Renders high-DPI vector icons in normal muted and active emerald states."""
        def render_state(stroke_color: str) -> QPixmap:
            svg_xml = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
                f'fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" '
                f'stroke-linecap="round" stroke-linejoin="round">{svg_body}</svg>'
            )
            renderer = QSvgRenderer(QByteArray(svg_xml.encode("utf-8")))
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap

        normal_color = "#00E599" if is_active else "#94A3B8"
        icon = QIcon()
        icon.addPixmap(render_state(normal_color), QIcon.Mode.Normal)
        icon.addPixmap(render_state("#00E599"), QIcon.Mode.Active)
        icon.addPixmap(render_state("#00E599"), QIcon.Mode.Selected)
        return icon

    def _create_nav_rail(self) -> QWidget:
        """Creates the left navigation rail according to specification."""
        rail = QWidget(self)
        rail.setObjectName("NavRail")
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.setSpacing(8)

        # 1. Home (Active state matching Screenshot 1)
        self.rail_home = QToolButton(rail)
        home_icon = self._create_nav_icon(
            '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
            is_active=True
        )
        self.rail_home.setIcon(home_icon)
        self.rail_home.setIconSize(QSize(22, 22))
        self.rail_home.setText("Home")
        self.rail_home.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_home.setProperty("active", "true")
        self.rail_home.setToolTip("GAVIX Home (Alt+Home)")
        self.rail_home.clicked.connect(self._on_home_clicked)
        layout.addWidget(self.rail_home)

        # 2. Search
        self.rail_search = QToolButton(rail)
        search_icon = self._create_nav_icon(
            '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'
        )
        self.rail_search.setIcon(search_icon)
        self.rail_search.setIconSize(QSize(22, 22))
        self.rail_search.setText("Search")
        self.rail_search.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_search.setToolTip("Focus Search (Ctrl+L)")
        self.rail_search.clicked.connect(self._on_focus_address_bar)
        layout.addWidget(self.rail_search)

        # 3. Bookmarks
        self.rail_bookmarks = QToolButton(rail)
        bookmarks_icon = self._create_nav_icon(
            '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>'
        )
        self.rail_bookmarks.setIcon(bookmarks_icon)
        self.rail_bookmarks.setIconSize(QSize(22, 22))
        self.rail_bookmarks.setText("Bookmarks")
        self.rail_bookmarks.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_bookmarks.setToolTip("Bookmarks (Ctrl+B)")
        self.rail_bookmarks.clicked.connect(lambda: self._navigate_or_open_tab("gavix://bookmarks"))
        layout.addWidget(self.rail_bookmarks)

        # 4. History
        self.rail_history = QToolButton(rail)
        history_icon = self._create_nav_icon(
            '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
        )
        self.rail_history.setIcon(history_icon)
        self.rail_history.setIconSize(QSize(22, 22))
        self.rail_history.setText("History")
        self.rail_history.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_history.setToolTip("Browsing History (Ctrl+H)")
        self.rail_history.clicked.connect(lambda: self._navigate_or_open_tab("gavix://history"))
        layout.addWidget(self.rail_history)

        # 5. Downloads
        self.rail_downloads = QToolButton(rail)
        downloads_icon = self._create_nav_icon(
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>'
        )
        self.rail_downloads.setIcon(downloads_icon)
        self.rail_downloads.setIconSize(QSize(22, 22))
        self.rail_downloads.setText("Downloads")
        self.rail_downloads.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_downloads.setToolTip("Downloads (Ctrl+J)")
        self.rail_downloads.clicked.connect(lambda: self._navigate_or_open_tab("gavix://downloads"))
        layout.addWidget(self.rail_downloads)

        # 6. Extensions
        self.rail_extensions = QToolButton(rail)
        extensions_icon = self._create_nav_icon(
            '<path d="M19.439 7.85c0-1.57.94-2.85 2.1-2.85V3a1 1 0 0 0-1-1h-2a2 2 0 0 0-2 2c0 1.1-.9 2-2 2s-2-.9-2-2a2 2 0 0 0-2-2H8.5a1 1 0 0 0-1 1v2c1.16 0 2.1 1.28 2.1 2.85s-.94 2.85-2.1 2.85V15a1 1 0 0 0 1 1h2a2 2 0 0 0 2-2c0-1.1.9-2 2-2s2 .9 2 2a2 2 0 0 0 2 2h2a1 1 0 0 0 1-1v-4.3c-1.16 0-2.1-1.28-2.1-2.85z"/>'
        )
        self.rail_extensions.setIcon(extensions_icon)
        self.rail_extensions.setIconSize(QSize(22, 22))
        self.rail_extensions.setText("Extensions")
        self.rail_extensions.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_extensions.setToolTip("GAVIX Extensions (Shield Protected)")
        self.rail_extensions.clicked.connect(self._on_shield_clicked)
        layout.addWidget(self.rail_extensions)

        layout.addStretch()

        # 7. Settings (Pinned at bottom)
        self.rail_settings = QToolButton(rail)
        settings_icon = self._create_nav_icon(
            '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
        )
        self.rail_settings.setIcon(settings_icon)
        self.rail_settings.setIconSize(QSize(22, 22))
        self.rail_settings.setText("Settings")
        self.rail_settings.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.rail_settings.setToolTip("Settings & Privacy")
        self.rail_settings.clicked.connect(lambda: self._navigate_or_open_tab("gavix://settings"))
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
        QShortcut(QKeySequence("Ctrl+J"), self, self._on_open_downloads_dialog)
        QShortcut(QKeySequence("Ctrl+I"), self, self._on_toggle_ai_panel)
        QShortcut(QKeySequence("Ctrl+M"), self, self._on_toggle_nav_rail)

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

    def _on_download_started(self, d_id: int, filename: str):
        self.status_bar.showMessage(f"Downloading {filename}...", 4000)

    def _on_download_finished(self, d_id: int, success: bool):
        if success:
            self.status_bar.showMessage("Download completed! Saved to Downloads.", 5000)
        else:
            self.status_bar.showMessage("Download was cancelled or interrupted.", 4000)

    def _on_open_downloads_dialog(self):
        dialog = GavixDownloadsDialog(self.download_manager, self)
        dialog.exec()

    def _on_toggle_nav_rail(self):
        """Toggles visibility of the collapsible left navigation rail."""
        if self.nav_rail.isVisible():
            self.nav_rail.hide()
            self.status_bar.showMessage("Navigation Rail Collapsed", 2000)
        else:
            self.nav_rail.show()
            self.status_bar.showMessage("Navigation Rail Expanded", 2000)

    def _navigate_or_open_tab(self, url: str):
        """Navigates current tab or opens a tab with the specified URL."""
        if self.current_tab:
            self.current_tab.navigate_to(url)
        else:
            self.tab_widget.new_tab(url)

    def _on_shield_clicked(self):
        """Displays GAVIX Shield protection status dialog."""
        QMessageBox.information(
            self,
            "GAVIX Shield",
            "🛡 GAVIX Shield Active & Enforced\n\n"
            "• Anti-Fingerprinting Protection: ON\n"
            "• Tracker & Ad Telemetry: Blocked\n"
            "• Partitioned Cookie Storage: Enforced\n"
            "• Secure DNS & WebRTC Leak Protection: Active"
        )

