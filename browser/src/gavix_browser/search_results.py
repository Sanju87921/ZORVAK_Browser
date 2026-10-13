"""
GAVIX Browser - Search Results Page Renderer.
Renders a clean, professional, readable search engine results page (light interface)
similar in structure to modern search engines with distinctive GAVIX branding.
"""

import html
from urllib.parse import urlparse, quote_plus
from gavix_browser.search_client import SearchResponse


def render_search_results_html(response: SearchResponse) -> str:
    """Generates a complete, clean, professional search results page for a SearchResponse."""
    query_escaped = html.escape(response.query)
    query_encoded = quote_plus(response.query)

    # 1. Error / Offline State
    if response.is_error:
        err_msg = html.escape(response.error_message)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{query_escaped} - GAVIX Search</title>
  <style>
    body {{
      background-color: #F8FAFC;
      color: #0F172A;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 85vh;
      margin: 0;
      padding: 24px;
      text-align: center;
    }}
    .error-card {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 36px 44px;
      max-width: 520px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }}
    .error-icon {{
      font-size: 38px;
      color: #EF4444;
      margin-bottom: 14px;
    }}
    h2 {{
      font-size: 20px;
      margin-bottom: 10px;
      color: #1E293B;
    }}
    p {{
      color: #64748B;
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 22px;
    }}
    .btn {{
      background: #00E599;
      color: #080B10;
      font-weight: 600;
      padding: 10px 24px;
      border-radius: 8px;
      text-decoration: none;
      display: inline-block;
      cursor: pointer;
      border: none;
      font-size: 14px;
      transition: background 0.15s;
    }}
    .btn:hover {{
      background: #00C282;
    }}
    .dev-note {{
      margin-top: 18px;
      font-size: 12px;
      color: #94A3B8;
    }}
  </style>
</head>
<body>
  <div class="error-card">
    <div class="error-icon">⚠</div>
    <h2>GAVIX Search Offline</h2>
    <p>{err_msg}</p>
    <button class="btn" onclick="window.location.reload()">Retry Search</button>
    <div class="dev-note">Endpoint: <code>/api/v1/search</code></div>
  </div>
</body>
</html>
"""

    # 2. Empty Results State
    if not response.results:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{query_escaped} - GAVIX Search</title>
  <style>
    body {{
      background-color: #FFFFFF;
      color: #0F172A;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
    }}
    header {{
      display: flex;
      align-items: center;
      padding: 16px 28px;
      border-bottom: 1px solid #E2E8F0;
      gap: 24px;
    }}
    .brand-link {{
      display: flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      color: #0F172A;
      font-weight: 700;
      font-size: 20px;
      letter-spacing: 1.5px;
    }}
    .brand-emblem {{
      width: 28px;
      height: 28px;
    }}
    .search-box {{
      flex: 1;
      max-width: 680px;
      display: flex;
      align-items: center;
      border: 1px solid #CBD5E1;
      border-radius: 26px;
      padding: 0 16px;
      height: 46px;
      background: #FFFFFF;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }}
    .search-box input {{
      flex: 1;
      border: none;
      outline: none;
      font-size: 15px;
      padding: 0 10px;
    }}
    .content-area {{
      max-width: 720px;
      margin: 40px auto;
      padding: 0 20px;
    }}
    .empty-card {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 32px;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 18px;
      color: #1E293B;
    }}
    p {{
      color: #64748B;
      font-size: 14px;
      line-height: 1.6;
      margin: 0 0 14px;
    }}
    .badge {{
      display: inline-block;
      background: rgba(0, 229, 153, 0.15);
      color: #059669;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
    }}
  </style>
</head>
<body>
  <header>
    <a href="gavix://home" class="brand-link">
      <img src="gavix_icon.png" alt="GAVIX" class="brand-emblem">
      <span>GAVIX</span>
    </a>
    <form class="search-box" onsubmit="event.preventDefault(); window.location.href='http://127.0.0.1:8000/api/v1/search?q=' + encodeURIComponent(this.q.value);">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="#64748B"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input type="text" name="q" value="{query_escaped}">
    </form>
  </header>
  <div class="content-area">
    <div class="empty-card">
      <h3>No results found in current GAVIX index</h3>
      <p>Amar's crawler and indexer currently contain a limited set of documents. Try broader keywords or search terms related to indexed domains.</p>
      <div class="badge">{html.escape(response.index_status.coverage_note)}</div>
    </div>
  </div>
</body>
</html>
"""

    # 3. Successful Organic Results List
    results_html = []
    for item in response.results:
        t_esc = html.escape(item.title)
        u_esc = html.escape(item.url)
        s_esc = html.escape(item.snippet)
        try:
            parsed = urlparse(item.url)
            domain = html.escape(parsed.netloc)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
        except Exception:
            domain = ""
            favicon_url = ""

        date_tag = f"<span class='date-badge'>{html.escape(item.last_crawled)}</span>" if item.last_crawled else ""

        results_html.append(f"""
        <article class="result-row">
          <div class="result-source-meta">
            <img class="result-favicon" src="{favicon_url}" alt="" onerror="this.style.display='none'">
            <div class="result-source-text">
              <span class="result-domain">{domain}</span>
              <span class="result-url-path">{u_esc}</span>
            </div>
            {date_tag}
          </div>
          <h2 class="result-title">
            <a href="{u_esc}">{t_esc}</a>
          </h2>
          <p class="result-snippet">{s_esc}</p>
        </article>
        """)

    rendered_items = "\n".join(results_html)

    # Result count formatting
    if response.total_estimate > 0:
        count_str = f"About {response.total_estimate:,} results"
    else:
        count_str = f"{len(response.results)} results"

    # Contextual Related Searches
    q_lower = response.query.lower().strip()
    related_queries = [
        f"what is {response.query}",
        f"{response.query} guide",
        f"{response.query} examples",
        f"latest {response.query} updates",
        f"{response.query} vs alternatives",
        f"how does {response.query} work"
    ]
    related_items_html = "\n".join([
        f'<div class="related-item" onclick="searchFor(\'{quote_plus(rq)}\')">'
        f'<svg viewBox="0 0 24 24"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>'
        f'<span>{html.escape(rq)}</span>'
        f'</div>'
        for rq in related_queries
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{query_escaped} - GAVIX Search</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: #FFFFFF;
      color: #1E293B;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
    }}

    /* Top Search Header */
    .search-header {{
      position: sticky;
      top: 0;
      background: #FFFFFF;
      border-bottom: 1px solid #E2E8F0;
      padding: 14px 28px 0;
      z-index: 100;
    }}

    .header-top-row {{
      display: flex;
      align-items: center;
      gap: 28px;
      margin-bottom: 14px;
    }}

    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 9px;
      text-decoration: none;
      color: #0F172A;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 2px;
      min-width: 120px;
      transition: opacity 0.15s;
    }}

    .brand-cluster:hover {{
      opacity: 0.85;
    }}

    .brand-emblem {{
      width: 28px;
      height: 28px;
      object-fit: contain;
    }}

    /* Omnibox Search Field */
    .search-input-form {{
      flex: 1;
      max-width: 680px;
      position: relative;
    }}

    .search-pill {{
      width: 100%;
      height: 48px;
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-radius: 24px;
      padding: 0 88px 0 44px;
      font-size: 15px;
      color: #0F172A;
      outline: none;
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
      transition: all 0.2s ease;
    }}

    .search-pill:hover {{
      border-color: #94A3B8;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }}

    .search-pill:focus {{
      border-color: #00E599;
      box-shadow: 0 0 0 3px rgba(0, 229, 153, 0.2), 0 3px 12px rgba(0, 0, 0, 0.08);
    }}

    .search-loupe {{
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      width: 18px;
      height: 18px;
      fill: #64748B;
      pointer-events: none;
    }}

    .search-actions-right {{
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .action-icon-btn {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: none;
      background: transparent;
      color: #64748B;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .action-icon-btn:hover {{
      background: #F1F5F9;
      color: #00E599;
    }}

    .action-icon-btn svg {{
      width: 17px;
      height: 17px;
      fill: currentColor;
    }}

    .header-right-tools {{
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .header-tool-btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 1px solid #E2E8F0;
      background: #F8FAFC;
      color: #475569;
      cursor: pointer;
      font-size: 15px;
      transition: all 0.15s;
    }}

    .header-tool-btn:hover {{
      background: #E2E8F0;
      color: #0F172A;
    }}

    .tool-shield {{
      color: #00E599;
      border-color: rgba(0, 229, 153, 0.4);
      background: rgba(0, 229, 153, 0.08);
    }}

    /* Category Nav Bar */
    .category-tabs-bar {{
      display: flex;
      align-items: center;
      gap: 20px;
      margin-left: 148px;
      font-size: 14px;
      overflow-x: auto;
    }}

    .tab-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 10px 4px 12px;
      color: #64748B;
      text-decoration: none;
      font-weight: 500;
      border-bottom: 3px solid transparent;
      cursor: pointer;
      white-space: nowrap;
      transition: color 0.15s;
    }}

    .tab-link:hover {{
      color: #0F172A;
    }}

    .tab-link.active {{
      color: #0F172A;
      font-weight: 600;
      border-bottom-color: #00E599;
    }}

    .tab-settings {{
      margin-left: auto;
      color: #64748B;
    }}

    /* Main Results Layout */
    .main-viewport {{
      max-width: 1220px;
      margin: 0 auto;
      padding: 16px 28px 60px 148px;
      display: flex;
      gap: 64px;
      align-items: flex-start;
    }}

    .results-col {{
      flex: 1;
      max-width: 720px;
    }}

    .stats-bar {{
      font-size: 13px;
      color: #64748B;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .coverage-tag {{
      background: #F1F5F9;
      color: #475569;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
    }}

    /* Individual Organic Result */
    .result-row {{
      margin-bottom: 30px;
      padding: 6px 10px;
      border-radius: 8px;
      transition: background 0.15s;
    }}

    .result-row:hover {{
      background: #F8FAFC;
    }}

    .result-source-meta {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
    }}

    .result-favicon {{
      width: 20px;
      height: 20px;
      border-radius: 4px;
      background: #E2E8F0;
      object-fit: contain;
    }}

    .result-source-text {{
      display: flex;
      flex-direction: column;
      line-height: 1.25;
    }}

    .result-domain {{
      font-size: 13px;
      font-weight: 500;
      color: #1E293B;
    }}

    .result-url-path {{
      font-size: 12px;
      color: #64748B;
      word-break: break-all;
    }}

    .date-badge {{
      margin-left: auto;
      font-size: 11px;
      color: #94A3B8;
    }}

    .result-title {{
      margin: 0 0 5px;
      font-size: 19px;
      font-weight: 500;
      line-height: 1.35;
    }}

    .result-title a {{
      color: #1D4ED8;
      text-decoration: none;
    }}

    .result-title a:hover {{
      text-decoration: underline;
    }}

    .result-snippet {{
      font-size: 14px;
      color: #475569;
      line-height: 1.58;
    }}

    /* Right Column — Related Searches */
    .related-col {{
      width: 300px;
      padding-top: 10px;
    }}

    .related-card {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 20px;
    }}

    .related-title {{
      font-size: 15px;
      font-weight: 600;
      color: #0F172A;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .related-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 10px;
      margin-bottom: 4px;
      border-radius: 8px;
      color: #334155;
      font-size: 13px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s;
    }}

    .related-item:hover {{
      background: #FFFFFF;
      color: #059669;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    }}

    .related-item svg {{
      width: 14px;
      height: 14px;
      fill: #94A3B8;
      flex-shrink: 0;
    }}

    /* Responsive */
    @media (max-width: 960px) {{
      .category-tabs-bar {{
        margin-left: 0;
      }}
      .main-viewport {{
        padding-left: 20px;
        flex-direction: column;
      }}
      .related-col {{
        width: 100%;
        max-width: 720px;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Search Header -->
  <header class="search-header">
    <div class="header-top-row">
      <a href="gavix://home" class="brand-cluster" title="GAVIX Home">
        <img src="gavix_icon.png" alt="GAVIX" class="brand-emblem">
        <span>GAVIX</span>
      </a>

      <form class="search-input-form" onsubmit="event.preventDefault(); searchFor(this.q.value);">
        <svg class="search-loupe" viewBox="0 0 24 24">
          <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 14z"/>
        </svg>
        <input 
          type="text" 
          name="q" 
          class="search-pill" 
          value="{query_escaped}" 
          autocomplete="off"
          placeholder="Search the web securely with GAVIX..."
        >
        <div class="search-actions-right">
          <button type="button" class="action-icon-btn" title="Voice Search" onclick="alert('GAVIX Voice Search Ready')">
            <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5-3c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
          </button>
          <button type="button" class="action-icon-btn" title="Visual Lens" onclick="alert('GAVIX Visual Lens Ready')">
            <svg viewBox="0 0 24 24"><path d="M21 6h-3.17L16 4H8L6.17 6H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-9 13c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.65 0-3 1.35-3 3s1.35 3 3 3 3-1.35 3-3-1.35-3-3-3z"/></svg>
          </button>
        </div>
      </form>

      <div class="header-right-tools">
        <button class="header-tool-btn tool-shield" title="GAVIX Shield: Protected">🛡</button>
        <button class="header-tool-btn" title="Bookmarks" onclick="window.location.href='gavix://bookmarks'">★</button>
        <button class="header-tool-btn" title="Settings" onclick="window.location.href='gavix://settings'">⚙</button>
      </div>
    </div>

    <!-- Category Tabs Navigation -->
    <nav class="category-tabs-bar">
      <span class="tab-link active" onclick="switchCategory('All')">All</span>
      <span class="tab-link" onclick="switchCategory('Images')">Images</span>
      <span class="tab-link" onclick="switchCategory('Videos')">Videos</span>
      <span class="tab-link" onclick="switchCategory('News')">News</span>
      <span class="tab-link" onclick="switchCategory('Maps')">Maps</span>
      <span class="tab-link" onclick="switchCategory('More')">More</span>
      <span class="tab-link tab-settings" onclick="window.location.href='gavix://settings'">Settings</span>
    </nav>
  </header>

  <!-- Main Viewport (Results + Related Searches) -->
  <main class="main-viewport">
    <div class="results-col">
      <div class="stats-bar">
        <span>{count_str}</span>
        <span class="coverage-tag">{html.escape(response.index_status.coverage_note)}</span>
      </div>

      <section class="results-list">
        {rendered_items}
      </section>
    </div>

    <aside class="related-col">
      <div class="related-card">
        <div class="related-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="#00E599"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <span>Related searches</span>
        </div>
        {related_items_html}
      </div>
    </aside>
  </main>

  <script>
    function searchFor(query) {{
      const q = query.trim();
      if (!q) return;
      window.location.href = 'http://127.0.0.1:8000/api/v1/search?q=' + encodeURIComponent(q);
    }}

    function switchCategory(cat) {{
      document.querySelectorAll('.tab-link').forEach(el => {{
        if (el.textContent.trim() === cat) {{
          el.classList.add('active');
        }} else if (!el.classList.contains('tab-settings')) {{
          el.classList.remove('active');
        }}
      }});
      if (cat !== 'All') {{
        alert('GAVIX ' + cat + ' search index connector is ready for backend integration.');
      }}
    }}
  </script>
</body>
</html>
"""
