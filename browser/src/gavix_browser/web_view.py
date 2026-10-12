"""
GAVIX Browser - Web View Component.
Encapsulates QWebEngineView with secure default profiles and navigation hooks.
"""

import os
from pathlib import Path
from PySide6.QtCore import Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineSettings
)


class GavixWebPage(QWebEnginePage):
    """Custom WebPage enforcing GAVIX security policies."""

    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)

    def certificateError(self, certificate_error) -> bool:
        """
        Enforce strict TLS security. Do not silently ignore SSL/TLS certificate errors.
        """
        # Reject invalid certificates
        return False


class GavixWebView(QWebEngineView):
    """The central web rendering surface for GAVIX."""

    # Custom signals for UI updates
    page_title_changed = Signal(str)
    page_url_changed = Signal(str)
    loading_progress = Signal(int)
    loading_started = Signal()
    loading_finished = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_profile()
        self._setup_signals()

    def _setup_profile(self):
        """Initializes a persistent local profile for GAVIX."""
        # Store profile in local app data directory
        app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / ".gavix"))
        profile_path = os.path.join(app_data, "GavixBrowser", "profile")
        os.makedirs(profile_path, exist_ok=True)

        self._profile = QWebEngineProfile("GavixProfile", self)
        self._profile.setPersistentStoragePath(profile_path)
        self._profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )

        # Configure safe web engine settings
        settings = self._profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Set GAVIX customized User-Agent
        default_ua = self._profile.httpUserAgent()
        gavix_ua = f"{default_ua} GavixBrowser/0.1"
        self._profile.setHttpUserAgent(gavix_ua)

        # Attach custom page
        self._page = GavixWebPage(self._profile, self)
        self.setPage(self._page)

    def _setup_signals(self):
        """Wire web engine events to internal signals."""
        self.loadStarted.connect(self.loading_started.emit)
        self.loadProgress.connect(self.loading_progress.emit)
        self.loadFinished.connect(self.loading_finished.emit)
        self.titleChanged.connect(self.page_title_changed.emit)
        self.urlChanged.connect(lambda qurl: self.page_url_changed.emit(qurl.toString()))

    def navigate_to(self, url_str: str):
        """Navigates safely to a given URL string."""
        if not url_str:
            return
        qurl = QUrl(url_str)
        if qurl.isValid():
            self.load(qurl)
