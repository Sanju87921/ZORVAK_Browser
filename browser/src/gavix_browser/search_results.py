"""
GAVIX Browser - Search Results Page Renderer.
Builds a dark, responsive search results view with honest telemetry badges,
sanitized snippets (XSS-safe), empty states, and offline retry actions.
"""

import html
from urllib.parse import urlparse
from gavix_browser.search_client import SearchResponse


def render_search_results_html(response: SearchResponse) -> str:
    """Generates a complete, beautiful HTML results page for a SearchResponse."""
    query_escaped = html.escape(response.query)

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
      background-color: #080B10;
      color: #F1F5F9;
      font-family: 'Segoe UI', system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 80vh;
      margin: 0;
      padding: 24px;
      text-align: center;
    }}
    .error-card {{
      background: rgba(18, 24, 34, 0.85);
      border: 1px solid rgba(239, 68, 68, 0.35);
      border-radius: 16px;
      padding: 36px 40px;
      max-width: 540px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    }}
    .icon {{
      font-size: 42px;
      color: #EF4444;
      margin-bottom: 16px;
    }}
    h2 {{
      font-size: 22px;
      margin-bottom: 12px;
    }}
    p {{
      color: #94A3B8;
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 24px;
    }}
    .btn {{
      background: linear-gradient(135deg, #00E599, #06B6D4);
      color: #080B10;
      font-weight: 700;
      padding: 12px 28px;
      border-radius: 10px;
      text-decoration: none;
      display: inline-block;
      cursor: pointer;
      border: none;
      font-size: 14px;
      transition: transform 0.2s;
    }}
    .btn:hover {{
      transform: scale(1.04);
    }}
    .dev-note {{
      margin-top: 20px;
      font-size: 12px;
      color: #64748B;
    }}
  </style>
</head>
<body>
  <div class="error-card">
    <div class="icon">⚠</div>
    <h2>GAVIX Search Offline</h2>
    <p>{err_msg}</p>
    <button class="btn" onclick="window.location.reload()">Retry Search</button>
    <div class="dev-note">Target API endpoint: <code>/api/v1/search</code></div>
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
      background-color: #080B10;
      color: #F1F5F9;
      font-family: 'Segoe UI', system-ui, sans-serif;
      padding: 30px 48px;
      margin: 0;
    }}
    .search-header {{
      max-width: 780px;
      margin-bottom: 30px;
    }}
    .query-title {{
      font-size: 20px;
      color: #94A3B8;
    }}
    .query-title span {{
      color: #00E599;
      font-weight: 600;
    }}
    .empty-card {{
      background: rgba(18, 24, 34, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 32px;
      max-width: 680px;
      margin-top: 20px;
    }}
    h3 {{
      font-size: 18px;
      margin-bottom: 8px;
    }}
    p {{
      color: #94A3B8;
      font-size: 14px;
      line-height: 1.6;
    }}
    .badge {{
      display: inline-block;
      background: rgba(0, 229, 153, 0.12);
      color: #00E599;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      margin-top: 14px;
    }}
  </style>
</head>
<body>
  <div class="search-header">
    <div class="query-title">Results for: <span>"{query_escaped}"</span></div>
    <div class="empty-card">
      <h3>No results found in current GAVIX index</h3>
      <p>Amar's crawler and indexer currently contain a limited set of documents. Try broader keywords or search terms related to indexed domains.</p>
      <div class="badge">{html.escape(response.index_status.coverage_note)}</div>
    </div>
  </div>
</body>
</html>
"""

    # 3. Successful Results List
    results_html = []
    for item in response.results:
        t_esc = html.escape(item.title)
        u_esc = html.escape(item.url)
        s_esc = html.escape(item.snippet)
        try:
            domain = html.escape(urlparse(item.url).netloc)
        except Exception:
            domain = ""

        date_tag = f"<span class='date-badge'>{html.escape(item.last_crawled)}</span>" if item.last_crawled else ""

        results_html.append(f"""
        <article class="result-item">
          <div class="result-domain">{domain} {date_tag}</div>
          <h2 class="result-title"><a href="{u_esc}">{t_esc}</a></h2>
          <div class="result-url">{u_esc}</div>
          <p class="result-snippet">{s_esc}</p>
        </article>
        """)

    rendered_items = "\n".join(results_html)
    count_str = f"About {response.total_estimate} results" if response.total_estimate > 0 else f"{len(response.results)} results"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{query_escaped} - GAVIX Search</title>
  <style>
    body {{
      background-color: #080B10;
      color: #F1F5F9;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      margin: 0;
      padding: 24px 48px;
    }}

    .results-container {{
      max-width: 760px;
    }}

    .meta-bar {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 20px;
      margin-bottom: 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 13px;
      color: #94A3B8;
    }}

    .query-highlight {{
      color: #00E599;
      font-weight: 600;
    }}

    .coverage-pill {{
      background: rgba(0, 229, 153, 0.1);
      color: #00E599;
      border: 1px solid rgba(0, 229, 153, 0.25);
      border-radius: 20px;
      padding: 3px 10px;
      font-size: 11px;
    }}

    .result-item {{
      margin-bottom: 28px;
      background: rgba(18, 24, 34, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 18px 22px;
      transition: all 0.2s ease;
    }}

    .result-item:hover {{
      background: rgba(24, 34, 48, 0.7);
      border-color: rgba(0, 229, 153, 0.3);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }}

    .result-domain {{
      font-size: 12px;
      color: #94A3B8;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}

    .date-badge {{
      background: rgba(255, 255, 255, 0.06);
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 10px;
      color: #64748B;
    }}

    .result-title {{
      margin: 0 0 4px;
      font-size: 18px;
      font-weight: 600;
    }}

    .result-title a {{
      color: #00E599;
      text-decoration: none;
      transition: color 0.15s;
    }}

    .result-title a:hover {{
      color: #06B6D4;
      text-decoration: underline;
    }}

    .result-url {{
      font-size: 12px;
      color: #64748B;
      margin-bottom: 8px;
      word-break: break-all;
    }}

    .result-snippet {{
      margin: 0;
      font-size: 14px;
      line-height: 1.55;
      color: #CBD5E1;
    }}
  </style>
</head>
<body>
  <div class="results-container">
    <div class="meta-bar">
      <span>{count_str} for <span class="query-highlight">"{query_escaped}"</span></span>
      <span class="coverage-pill">{html.escape(response.index_status.coverage_note)}</span>
    </div>

    <main>
      {rendered_items}
    </main>
  </div>
</body>
</html>
"""
