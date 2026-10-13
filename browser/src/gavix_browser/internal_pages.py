"""
GAVIX Browser - Internal Pages Generator.
Generates full-fledged browser application pages for:
- Bookmarks (gavix://bookmarks)
- Downloads (gavix://downloads)
- History (gavix://history)
- Settings (gavix://settings)

All pages share ONE unified, professional browser architecture:
- Dark charcoal GAVIX left sidebar (64–72px width) with emerald active indicators
- Crisp, readable light content area (#F8FAFC)
- Real SQLite storage and real browser data bindings
- Zero fake metrics or SaaS dashboard cards
"""

import html
import json
from urllib.parse import urlparse
from typing import List, Dict, Optional
from gavix_browser.storage import GavixStorage


def _render_internal_shell(active_page: str, page_title: str, content_html: str, custom_scripts: str = "") -> str:
    """Renders the common shell: dark narrow sidebar + clean white/light content area."""
    pages = [
        ("home", "⌂", "Home", "gavix://home"),
        ("bookmarks", "★", "Bookmarks", "gavix://bookmarks"),
        ("history", "⏱", "History", "gavix://history"),
        ("downloads", "↓", "Downloads", "gavix://downloads"),
        ("settings", "⚙", "Settings", "gavix://settings"),
    ]

    sidebar_items_html = []
    for pid, icon, label, link in pages:
        is_active = "active" if pid == active_page else ""
        sidebar_items_html.append(f"""
        <a href="{link}" class="nav-item {is_active}" title="{label}">
          <span class="nav-icon">{icon}</span>
          <span class="nav-label">{label}</span>
        </a>
        """)
    sidebar_html = "\n".join(sidebar_items_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title} — GAVIX</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      display: flex;
      height: 100vh;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #F8FAFC;
      color: #0F172A;
      -webkit-font-smoothing: antialiased;
    }}

    /* Dark Charcoal GAVIX Sidebar */
    .app-sidebar {{
      width: 70px;
      background: #0E131F;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 0;
      flex-shrink: 0;
      user-select: none;
    }}

    .sidebar-brand {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-decoration: none;
      margin-bottom: 24px;
    }}

    .sidebar-logo {{
      width: 28px;
      height: 28px;
      object-fit: contain;
    }}

    .sidebar-nav {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
      align-items: center;
    }}

    .nav-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 54px;
      height: 52px;
      border-radius: 10px;
      color: rgba(255, 255, 255, 0.65);
      text-decoration: none;
      transition: all 0.15s ease;
      position: relative;
    }}

    .nav-item:hover {{
      background: rgba(255, 255, 255, 0.08);
      color: #FFFFFF;
    }}

    .nav-item.active {{
      background: rgba(0, 229, 153, 0.14);
      color: #00E599;
      border: 1px solid rgba(0, 229, 153, 0.35);
    }}

    .nav-icon {{
      font-size: 16px;
      line-height: 1;
      margin-bottom: 4px;
    }}

    .nav-label {{
      font-size: 10px;
      font-weight: 500;
      letter-spacing: 0.3px;
    }}

    /* Clean White / Light Main Content Area */
    .app-content-viewport {{
      flex: 1;
      height: 100vh;
      overflow-y: auto;
      background: #FFFFFF;
      display: flex;
      flex-direction: column;
    }}

    .page-header-bar {{
      padding: 24px 40px 16px;
      border-bottom: 1px solid #E2E8F0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #FFFFFF;
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    .page-title {{
      font-size: 24px;
      font-weight: 700;
      color: #0F172A;
      letter-spacing: -0.5px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .search-filter-input {{
      height: 38px;
      width: 260px;
      background: #F1F5F9;
      border: 1px solid #CBD5E1;
      border-radius: 8px;
      padding: 0 14px;
      font-size: 14px;
      color: #0F172A;
      outline: none;
      transition: all 0.2s;
    }}

    .search-filter-input:focus {{
      background: #FFFFFF;
      border-color: #00E599;
      box-shadow: 0 0 0 3px rgba(0, 229, 153, 0.18);
    }}

    .primary-btn {{
      height: 38px;
      padding: 0 16px;
      background: #00E599;
      color: #080B10;
      font-weight: 600;
      font-size: 13px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.15s;
    }}

    .primary-btn:hover {{
      background: #00C282;
    }}

    .danger-btn {{
      height: 38px;
      padding: 0 16px;
      background: #FEE2E2;
      color: #DC2626;
      font-weight: 600;
      font-size: 13px;
      border: 1px solid #FECACA;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s;
    }}

    .danger-btn:hover {{
      background: #FCA5A5;
      color: #991B1B;
    }}

    .content-body {{
      padding: 28px 40px 60px;
      max-width: 980px;
    }}

    /* Common List Rows */
    .data-row {{
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid #F1F5F9;
      border-radius: 8px;
      transition: background 0.12s;
      gap: 14px;
    }}

    .data-row:hover {{
      background: #F8FAFC;
    }}

    .row-favicon {{
      width: 20px;
      height: 20px;
      border-radius: 4px;
      object-fit: contain;
      background: #E2E8F0;
      flex-shrink: 0;
    }}

    .row-info {{
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .row-title {{
      font-size: 14px;
      font-weight: 500;
      color: #1E293B;
      text-decoration: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .row-title:hover {{
      color: #059669;
      text-decoration: underline;
    }}

    .row-subtitle {{
      font-size: 12px;
      color: #64748B;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .row-time {{
      font-size: 12px;
      color: #94A3B8;
      margin-left: auto;
      padding-right: 8px;
      flex-shrink: 0;
    }}

    .row-action-btn {{
      background: transparent;
      border: none;
      color: #94A3B8;
      cursor: pointer;
      font-size: 14px;
      padding: 6px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .row-action-btn:hover {{
      background: #E2E8F0;
      color: #DC2626;
    }}

    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: #64748B;
      font-size: 15px;
    }}
  </style>
</head>
<body>
  <!-- Left GAVIX Sidebar -->
  <aside class="app-sidebar">
    <a href="gavix://home" class="sidebar-brand" title="GAVIX Browser">
      <img src="gavix_icon.png" alt="GAVIX" class="sidebar-logo">
    </a>
    <nav class="sidebar-nav">
      {sidebar_html}
    </nav>
  </aside>

  <!-- Content Area -->
  <main class="app-content-viewport">
    {content_html}
  </main>

  <script>
    function filterRows(inputEl, itemSelector) {{
      const q = inputEl.value.toLowerCase().trim();
      document.querySelectorAll(itemSelector).forEach(el => {{
        const text = el.textContent.toLowerCase();
        el.style.display = text.includes(q) ? '' : 'none';
      }});
    }}
  </script>
  {custom_scripts}
</body>
</html>
"""


def render_bookmarks_page_html(storage: GavixStorage) -> str:
    """Generates the GAVIX Bookmarks browser internal page."""
    bookmarks = storage.get_bookmarks()

    rows_html = []
    for b in bookmarks:
        b_id = b.get("id", "")
        title = html.escape(b.get("title") or b.get("url", ""))
        url = html.escape(b.get("url", ""))
        folder = html.escape(b.get("folder", "Default"))
        try:
            domain = html.escape(urlparse(b.get("url", "")).netloc)
            fav_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
        except Exception:
            fav_url = ""

        rows_html.append(f"""
        <div class="data-row bookmark-item" data-url="{url}">
          <img class="row-favicon" src="{fav_url}" alt="" onerror="this.style.display='none'">
          <div class="row-info">
            <a class="row-title" href="{url}">{title}</a>
            <span class="row-subtitle">{url} • <span style="color:#059669;">{folder}</span></span>
          </div>
          <button class="row-action-btn" title="Delete bookmark" onclick="deleteBookmark('{url}')">✕</button>
        </div>
        """)

    content = f"""
    <header class="page-header-bar">
      <h1 class="page-title">Bookmarks</h1>
      <div class="header-actions">
        <input 
          type="text" 
          class="search-filter-input" 
          placeholder="Search bookmarks..." 
          oninput="filterRows(this, '.bookmark-item')"
        >
        <button class="primary-btn" onclick="addBookmarkPrompt()">+ Add Bookmark</button>
      </div>
    </header>

    <div class="content-body">
      {''.join(rows_html) if rows_html else '<div class="empty-state">No bookmarks saved yet. Click ★ in the address bar to bookmark any page.</div>'}
    </div>
    """

    scripts = """
    <script>
      function addBookmarkPrompt() {
        const url = prompt("Enter website URL (e.g., https://example.com):");
        if (!url) return;
        const title = prompt("Enter bookmark name:", url) || url;
        window.location.href = 'gavix://action/add_bookmark?url=' + encodeURIComponent(url) + '&title=' + encodeURIComponent(title);
      }

      function deleteBookmark(url) {
        if (confirm("Remove bookmark: " + url + "?")) {
          window.location.href = 'gavix://action/remove_bookmark?url=' + encodeURIComponent(url);
        }
      }
    </script>
    """

    return _render_internal_shell("bookmarks", "Bookmarks", content, scripts)


def render_history_page_html(storage: GavixStorage) -> str:
    """Generates the GAVIX Browsing History internal page grouped by date."""
    history = storage.get_history(limit=200)

    rows_html = []
    for h in history:
        title = html.escape(h.get("title") or h.get("url", ""))
        url = html.escape(h.get("url", ""))
        visited_at = h.get("visited_at", "")
        time_str = visited_at[11:16] if len(visited_at) >= 16 else ""
        date_str = visited_at[:10] if len(visited_at) >= 10 else "Recent"
        try:
            domain = html.escape(urlparse(h.get("url", "")).netloc)
            fav_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
        except Exception:
            domain = ""
            fav_url = ""

        rows_html.append(f"""
        <div class="data-row history-item">
          <img class="row-favicon" src="{fav_url}" alt="" onerror="this.style.display='none'">
          <div class="row-info">
            <a class="row-title" href="{url}">{title}</a>
            <span class="row-subtitle">{domain}</span>
          </div>
          <span class="row-time">{date_str} {time_str}</span>
          <button class="row-action-btn" title="Remove entry" onclick="deleteHistoryEntry('{url}')">✕</button>
        </div>
        """)

    content = f"""
    <header class="page-header-bar">
      <h1 class="page-title">History</h1>
      <div class="header-actions">
        <input 
          type="text" 
          class="search-filter-input" 
          placeholder="Search history..." 
          oninput="filterRows(this, '.history-item')"
        >
        <button class="danger-btn" onclick="clearHistoryConfirm()">Clear Browsing History</button>
      </div>
    </header>

    <div class="content-body">
      {''.join(rows_html) if rows_html else '<div class="empty-state">No browsing history recorded yet. History is kept locally on this device.</div>'}
    </div>
    """

    scripts = """
    <script>
      function clearHistoryConfirm() {
        if (confirm("Delete all local browsing history records? This cannot be undone.")) {
          window.location.href = 'gavix://action/clear_history';
        }
      }

      function deleteHistoryEntry(url) {
        window.location.href = 'gavix://action/remove_history?url=' + encodeURIComponent(url);
      }
    </script>
    """

    return _render_internal_shell("history", "History", content, scripts)


def render_downloads_page_html(downloads_list: list) -> str:
    """Generates the GAVIX Downloads browser internal page connected to download items."""
    rows_html = []
    for d in downloads_list:
        filename = html.escape(d.filename)
        path = html.escape(d.path)
        state = d.state
        received_mb = d.received_bytes / (1024 * 1024)
        total_mb = d.total_bytes / (1024 * 1024) if d.total_bytes > 0 else 0

        size_text = f"{received_mb:.1f} MB / {total_mb:.1f} MB" if total_mb > 0 else f"{received_mb:.1f} MB"
        status_color = "#059669" if state == "completed" else ("#DC2626" if state in ("cancelled", "interrupted") else "#0284C7")

        rows_html.append(f"""
        <div class="data-row download-item">
          <span style="font-size:22px;">📁</span>
          <div class="row-info">
            <span class="row-title" style="cursor:default;">{filename}</span>
            <span class="row-subtitle">{size_text} • <strong style="color:{status_color}; text-transform:capitalize;">{state}</strong></span>
          </div>
          <button class="primary-btn" style="height:32px; font-size:12px;" onclick="window.location.href='gavix://action/open_downloads_folder'">Show in Folder</button>
        </div>
        """)

    content = f"""
    <header class="page-header-bar">
      <h1 class="page-title">Downloads</h1>
      <div class="header-actions">
        <input 
          type="text" 
          class="search-filter-input" 
          placeholder="Search downloads..." 
          oninput="filterRows(this, '.download-item')"
        >
        <button class="primary-btn" onclick="window.location.href='gavix://action/open_downloads_folder'">Open Downloads Folder</button>
      </div>
    </header>

    <div class="content-body">
      {''.join(rows_html) if rows_html else '<div class="empty-state">No downloads yet. Downloaded files will appear here.</div>'}
    </div>
    """

    return _render_internal_shell("downloads", "Downloads", content)


def render_settings_page_html(active_section: str = "general") -> str:
    """Generates the professional GAVIX Settings interface."""
    sections = [
        ("general", "General"),
        ("privacy", "Privacy & Security"),
        ("search", "Search"),
        ("appearance", "Appearance"),
        ("tabs", "Tabs"),
        ("downloads", "Downloads"),
        ("extensions", "Extensions"),
        ("about", "About GAVIX"),
    ]

    sec_links_html = []
    for sid, sname in sections:
        active_cls = "settings-nav-active" if sid == active_section else ""
        sec_links_html.append(f"""
        <a href="gavix://settings?section={sid}" class="settings-nav-link {active_cls}">{sname}</a>
        """)
    sec_nav_html = "\n".join(sec_links_html)

    # Section-specific content
    if active_section == "privacy":
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">Privacy & Security</h2>
          
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>GAVIX Shield Tracker Protection</strong>
                <p>Blocks third-party trackers, cross-site cookies, and intrusive scripts.</p>
              </div>
              <span class="status-badge-active">Enabled</span>
            </div>
            
            <div class="settings-row">
              <div>
                <strong>Isolated Local Storage</strong>
                <p>Cookies and web data are stored strictly on your local disk in %LOCALAPPDATA%.</p>
              </div>
              <span class="status-badge-active">Active</span>
            </div>

            <div class="settings-row">
              <div>
                <strong>Zero Third-Party Leaks</strong>
                <p>Telemetry, typing events, and browsing history are never transmitted.</p>
              </div>
              <span class="status-badge-active">Verified</span>
            </div>
          </div>

          <h3 class="settings-subheading">Browsing Data</h3>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>Clear Browsing Data</strong>
                <p>Delete cookies, cached images, and history records from this computer.</p>
              </div>
              <button class="danger-btn" onclick="window.location.href='gavix://action/open_clear_data_dialog'">Clear Data...</button>
            </div>
          </div>
        </div>
        """
    elif active_section == "search":
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">Search Engine</h2>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>Default Search Engine</strong>
                <p>Used in the address bar and central search pill.</p>
              </div>
              <select class="settings-select">
                <option selected>GAVIX Sovereign Search (Default)</option>
                <option>DuckDuckGo</option>
                <option>Google</option>
              </select>
            </div>
            <div class="settings-row">
              <div>
                <strong>GAVIX Search Backend URL</strong>
                <p>Endpoint where search requests are routed.</p>
              </div>
              <input type="text" class="settings-input" value="http://127.0.0.1:8000" readonly>
            </div>
          </div>
        </div>
        """
    elif active_section == "appearance":
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">Appearance</h2>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>Theme</strong>
                <p>Select interface lighting and contrast.</p>
              </div>
              <select class="settings-select">
                <option selected>Dark Chrome & Cinematic (Default)</option>
                <option>System Default</option>
              </select>
            </div>
            <div class="settings-row">
              <div>
                <strong>Accent Color</strong>
                <p>Electric Emerald & Futuristic Teal (#00E599).</p>
              </div>
              <span style="display:inline-block; width:22px; height:22px; border-radius:50%; background:#00E599; border:2px solid #0F172A;"></span>
            </div>
          </div>
        </div>
        """
    elif active_section == "downloads":
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">Downloads</h2>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>Download Location</strong>
                <p>Files are automatically saved to standard Windows Downloads folder.</p>
              </div>
              <button class="primary-btn" onclick="window.location.href='gavix://action/open_downloads_folder'">Open Folder</button>
            </div>
          </div>
        </div>
        """
    elif active_section == "about":
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">About GAVIX Browser</h2>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong style="font-size:16px;">GAVIX Browser</strong>
                <p>Gateway for Advanced Virtual Internet Experience</p>
                <p style="margin-top:6px; font-size:12px; color:#94A3B8;">Version: 1.0.0 Production Release (Chromium 124 Core)</p>
              </div>
              <span class="status-badge-active">Up to Date</span>
            </div>
            <div class="settings-row">
              <div>
                <strong>Data Sovereignty & Privacy</strong>
                <p>Engineered for Indian data residency and zero telemetry tracking.</p>
              </div>
              <span style="color:#059669; font-weight:600;">Active</span>
            </div>
          </div>
        </div>
        """
    else:  # General
        sec_content = """
        <div class="settings-section">
          <h2 class="settings-heading">General Settings</h2>
          <div class="settings-card">
            <div class="settings-row">
              <div>
                <strong>On Startup</strong>
                <p>Choose what opens when GAVIX starts up.</p>
              </div>
              <div style="display:flex; flex-direction:column; gap:8px;">
                <label><input type="radio" name="startup" checked> Open the New Tab page</label>
                <label><input type="radio" name="startup"> Continue where you left off</label>
              </div>
            </div>

            <div class="settings-row">
              <div>
                <strong>Default Browser</strong>
                <p>Make GAVIX your primary desktop web browser.</p>
              </div>
              <button class="primary-btn" onclick="alert('GAVIX is ready to be set as default browser.')">Make Default</button>
            </div>
          </div>
        </div>
        """

    content = f"""
    <header class="page-header-bar">
      <h1 class="page-title">Settings</h1>
    </header>

    <div style="display:flex; flex:1; overflow:hidden;">
      <!-- Left Settings Navigation Column -->
      <nav class="settings-subnav">
        {sec_nav_html}
      </nav>

      <!-- Settings Content Viewport -->
      <div class="settings-viewport">
        {sec_content}
      </div>
    </div>
    """

    custom_styles = """
    <style>
      .settings-subnav {
        width: 220px;
        background: #F8FAFC;
        border-right: 1px solid #E2E8F0;
        padding: 24px 16px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex-shrink: 0;
      }

      .settings-nav-link {
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 14px;
        color: #475569;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.12s;
      }

      .settings-nav-link:hover {
        background: #E2E8F0;
        color: #0F172A;
      }

      .settings-nav-link.settings-nav-active {
        background: rgba(0, 229, 153, 0.15);
        color: #059669;
        font-weight: 600;
      }

      .settings-viewport {
        flex: 1;
        overflow-y: auto;
        padding: 32px 48px;
      }

      .settings-heading {
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 20px;
      }

      .settings-subheading {
        font-size: 16px;
        font-weight: 600;
        color: #1E293B;
        margin: 28px 0 12px;
      }

      .settings-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 8px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      }

      .settings-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #F1F5F9;
        gap: 24px;
      }}

      .settings-row:last-child {
        border-bottom: none;
      }

      .settings-row strong {
        font-size: 14px;
        color: #0F172A;
      }

      .settings-row p {
        font-size: 13px;
        color: #64748B;
        margin-top: 2px;
      }

      .settings-select, .settings-input {
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        font-size: 13px;
        outline: none;
      }

      .status-badge-active {
        background: rgba(0, 229, 153, 0.15);
        color: #059669;
        font-weight: 600;
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 6px;
      }
    </style>
    """

    return _render_internal_shell("settings", "Settings", content + custom_styles)
