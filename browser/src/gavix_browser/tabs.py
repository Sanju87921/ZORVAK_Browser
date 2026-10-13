"""
GAVIX Browser - Tab Management System.
Implements modern multi-tab browsing, individual web view isolation,
tab switching, closing, and automatic new-tab fallback.
"""

from pathlib import Path
from PySide6.QtCore import Signal, QUrl, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTabBar,
    QToolButton
)

from urllib.parse import unquote_plus, parse_qs, urlparse
from gavix_browser.web_view import GavixWebView
from gavix_browser.home_page import get_home_page_html
from gavix_browser.theme import GavixColors
from gavix_browser.search_client import GavixSearchClient
from gavix_browser.search_results import render_search_results_html
from gavix_browser.internal_pages import (
    render_bookmarks_page_html,
    render_history_page_html,
    render_downloads_page_html,
    render_settings_page_html
)
from gavix_browser.storage import GavixStorage


class GavixTab(QWidget):
    """Encapsulates a single tab containing its own GavixWebView."""

    title_updated = Signal(str)
    url_updated = Signal(str)
    progress_updated = Signal(int)
    loading_started = Signal()
    loading_finished = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_home = False
        self.current_search_query = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = GavixWebView(self)
        layout.addWidget(self.web_view)

        # Connect internal web events
        self.web_view.page_title_changed.connect(self._on_title_changed)
        self.web_view.page_url_changed.connect(self._on_url_changed)
        self.web_view.loading_progress.connect(self.progress_updated.emit)
        self.web_view.loading_started.connect(self.loading_started.emit)
        self.web_view.loading_finished.connect(self._on_loading_finished)
        self.web_view.urlChanged.connect(self._check_intercept_search)

    def cleanup(self):
        """Explicitly tears down web view and page before destruction."""
        if hasattr(self, "web_view") and self.web_view:
            self.web_view.stop()

    def load_home(self):
        """Loads the local GAVIX Home / New Tab experience."""
        self.is_home = True
        self.current_search_query = None
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        home_path = assets_dir / "home.html"
        if home_path.exists():
            self.web_view.load(QUrl.fromLocalFile(str(home_path)))
        else:
            html = get_home_page_html()
            self.web_view.setHtml(html, QUrl.fromLocalFile(str(home_path)))
        self.title_updated.emit("New Tab")
        self.url_updated.emit("")

    def execute_search(self, query: str):
        """Executes a search against GAVIX Search API and renders results view."""
        clean_q = query.strip()
        if not clean_q:
            return

        self.is_home = False
        self.current_search_query = clean_q
        self.loading_started.emit()
        self.progress_updated.emit(25)
        self.title_updated.emit(f"{clean_q} — GAVIX Search")
        self.url_updated.emit(f"gavix://search/?q={clean_q}")

        # Fetch results from configured GAVIX Search endpoint
        client = GavixSearchClient()
        response = client.search(clean_q)
        self.progress_updated.emit(75)

        # Render HTML results view
        html = render_search_results_html(response)
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        self.web_view.setHtml(html, QUrl.fromLocalFile(str(assets_dir / "home.html")))
        self.progress_updated.emit(100)
        self.loading_finished.emit(not response.is_error)

    def navigate_to(self, url: str):
        """Navigates to an external URL or web resource, intercepting search queries."""
        if not url or url == "gavix://home" or url == "about:blank" or url.endswith("home.html"):
            self.load_home()
            return

        # Check for search scheme
        if url.startswith("gavix://search/?q="):
            query = unquote_plus(url[len("gavix://search/?q="):])
            self.execute_search(query)
            return

        parsed = urlparse(url)
        if "/api/v1/search" in parsed.path:
            qs = parse_qs(parsed.query)
            query = qs.get("q", [""])[0]
            if query:
                self.execute_search(query)
                return

        # Internal pages routing
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        storage = GavixStorage()

        if url.startswith("gavix://bookmarks"):
            self.is_home = False
            self.current_search_query = None
            html = render_bookmarks_page_html(storage)
            self.web_view.setHtml(html, QUrl.fromLocalFile(str(assets_dir / "home.html")))
            self.title_updated.emit("Bookmarks — GAVIX")
            self.url_updated.emit("gavix://bookmarks")
            return

        if url.startswith("gavix://history"):
            self.is_home = False
            self.current_search_query = None
            html = render_history_page_html(storage)
            self.web_view.setHtml(html, QUrl.fromLocalFile(str(assets_dir / "home.html")))
            self.title_updated.emit("History — GAVIX")
            self.url_updated.emit("gavix://history")
            return

        if url.startswith("gavix://downloads"):
            self.is_home = False
            self.current_search_query = None
            # Retrieve downloads if parent main window has download manager
            downloads = []
            main_win = self.window()
            if hasattr(main_win, "download_manager"):
                downloads = main_win.download_manager.get_downloads()
            html = render_downloads_page_html(downloads)
            self.web_view.setHtml(html, QUrl.fromLocalFile(str(assets_dir / "home.html")))
            self.title_updated.emit("Downloads — GAVIX")
            self.url_updated.emit("gavix://downloads")
            return

        if url.startswith("gavix://settings"):
            self.is_home = False
            self.current_search_query = None
            parsed_s = urlparse(url)
            qs_s = parse_qs(parsed_s.query)
            section = qs_s.get("section", ["general"])[0]
            html = render_settings_page_html(section)
            self.web_view.setHtml(html, QUrl.fromLocalFile(str(assets_dir / "home.html")))
            self.title_updated.emit("Settings — GAVIX")
            self.url_updated.emit(url)
            return

        # Internal actions routing (e.g. bookmarks / history management)
        if url.startswith("gavix://action/"):
            action = url[len("gavix://action/"):].split("?")[0]
            parsed_act = urlparse(url)
            qs_act = parse_qs(parsed_act.query)
            if action == "add_bookmark":
                u = qs_act.get("url", [""])[0]
                t = qs_act.get("title", [""])[0]
                if u:
                    storage.add_bookmark(u, t)
                self.navigate_to("gavix://bookmarks")
                return
            elif action == "remove_bookmark":
                u = qs_act.get("url", [""])[0]
                if u:
                    storage.remove_bookmark(u)
                self.navigate_to("gavix://bookmarks")
                return
            elif action == "clear_history":
                storage.clear_history()
                self.navigate_to("gavix://history")
                return
            elif action == "remove_history":
                u = qs_act.get("url", [""])[0]
                # remove single history entry
                with storage._get_connection() as conn:
                    conn.execute("DELETE FROM history WHERE url = ?", (u,))
                    conn.commit()
                self.navigate_to("gavix://history")
                return
            elif action == "open_downloads_folder":
                import os
                os.startfile(str(Path.home() / "Downloads"))
                self.navigate_to("gavix://downloads")
                return
            elif action == "open_clear_data_dialog":
                main_win = self.window()
                if hasattr(main_win, "_on_clear_data_clicked"):
                    main_win._on_clear_data_clicked()
                self.navigate_to("gavix://settings?section=privacy")
                return

        self.is_home = False
        self.current_search_query = None
        self.web_view.navigate_to(url)

    def _check_intercept_search(self, qurl: QUrl):
        """Intercepts internal webpage navigation pointing to the search endpoint."""
        url_str = qurl.toString()
        if "/api/v1/search" in url_str:
            parsed = urlparse(url_str)
            qs = parse_qs(parsed.query)
            query = qs.get("q", [""])[0]
            if query and query != self.current_search_query:
                self.execute_search(query)

    def _on_title_changed(self, title: str):
        if self.is_home:
            self.title_updated.emit("New Tab")
        elif self.current_search_query:
            self.title_updated.emit(f"{self.current_search_query} — GAVIX Search")
        else:
            clean_title = title if title.strip() else "Untitled"
            self.title_updated.emit(clean_title)

    def _on_url_changed(self, url_str: str):
        if url_str in ("about:blank", "gavix://home") or url_str.endswith("home.html") or "assets/home.html" in url_str:
            self.is_home = True
            self.url_updated.emit("")
        elif self.current_search_query:
            self.url_updated.emit(f"gavix://search/?q={self.current_search_query}")
        else:
            self.is_home = False
            self.url_updated.emit(url_str)

    def _on_loading_finished(self, success: bool):
        self.loading_finished.emit(success)


class GavixTabWidget(QTabWidget):
    """Modern dark multi-tab manager for GAVIX."""

    tab_state_changed = Signal()
    tab_created = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)

        # Style tab bar
        self._setup_style()

        # Connect tab events
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_tab_changed)

        # Add '+' New Tab button in the tab bar
        self._add_new_tab_button()

    def _setup_style(self):
        """Applies specialized styling for dark tab headers."""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {GavixColors.BG_MAIN};
            }}

            QTabBar {{
                background-color: {GavixColors.BG_MAIN};
                qproperty-drawBase: 0;
            }}

            QTabBar::tab {{
                background-color: {GavixColors.BG_SURFACE};
                color: {GavixColors.TEXT_MUTED};
                border: 1px solid {GavixColors.BORDER_SUBTLE};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 7px 16px;
                margin-right: 4px;
                min-width: 120px;
                max-width: 200px;
                font-size: 12px;
            }}

            QTabBar::tab:hover {{
                background-color: {GavixColors.BG_HOVER};
                color: {GavixColors.TEXT_PRIMARY};
            }}

            QTabBar::tab:selected {{
                background-color: {GavixColors.BG_RAISED};
                color: {GavixColors.EMERALD};
                border-top: 2px solid {GavixColors.EMERALD};
                border-color: {GavixColors.BORDER_MUTED} {GavixColors.BORDER_MUTED} {GavixColors.BG_RAISED} {GavixColors.BORDER_MUTED};
                font-weight: 600;
            }}

            QTabBar::close-button {{
                image: none;
                subcontrol-position: right;
                padding: 2px;
                border-radius: 4px;
            }}

            QTabBar::close-button:hover {{
                background-color: rgba(239, 68, 68, 0.4);
                color: #FFFFFF;
            }}
        """)

    def _add_new_tab_button(self):
        """Adds a '+' button at the end of the tab bar."""
        self.btn_new_tab = QToolButton(self)
        self.btn_new_tab.setText("+")
        self.btn_new_tab.setToolTip("New Tab (Ctrl+T)")
        self.btn_new_tab.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                color: {GavixColors.TEXT_SECONDARY};
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
                margin: 2px 4px;
            }}
            QToolButton:hover {{
                background-color: {GavixColors.BG_HOVER};
                color: {GavixColors.EMERALD};
            }}
        """)
        self.btn_new_tab.clicked.connect(lambda: self.new_tab())
        self.setCornerWidget(self.btn_new_tab, Qt.Corner.TopRightCorner)

    def new_tab(self, url: str = None) -> GavixTab:
        """Opens a new tab, optionally loading an initial URL, and focuses it."""
        tab = GavixTab(self)
        idx = self.addTab(tab, "New Tab")

        # Connect signals
        tab.title_updated.connect(lambda t: self._update_tab_title(tab, t))

        if url:
            tab.navigate_to(url)
        else:
            tab.load_home()

        self.tab_created.emit(tab)
        self.setCurrentIndex(idx)
        return tab

    def close_tab(self, index: int):
        """Closes the specified tab. Ensures at least one tab remains open."""
        if index < 0 or index >= self.count():
            return

        widget = self.widget(index)
        self.removeTab(index)
        if widget:
            if hasattr(widget, "cleanup"):
                widget.cleanup()
            widget.deleteLater()

        # If all tabs were closed, immediately spawn a clean new tab
        if self.count() == 0:
            self.new_tab()

    def current_gavix_tab(self) -> GavixTab | None:
        """Returns the currently active GavixTab."""
        widget = self.currentWidget()
        if isinstance(widget, GavixTab):
            return widget
        return None

    def _update_tab_title(self, tab: GavixTab, title: str):
        idx = self.indexOf(tab)
        if idx != -1:
            # Truncate title for tab display
            short_title = (title[:22] + "...") if len(title) > 25 else title
            self.setTabText(idx, short_title)
            self.setTabToolTip(idx, title)

    def _on_current_tab_changed(self, index: int):
        self.tab_state_changed.emit()
