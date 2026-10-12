"""
Unit and integration tests for GAVIX Search client and results rendering.
"""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.search_client import (
    GavixSearchClient,
    SearchResponse,
    SearchResultItem,
    IndexStatus
)
from gavix_browser.search_results import render_search_results_html


def test_offline_search_error_handling():
    # Target an offline endpoint
    client = GavixSearchClient(base_url="http://127.0.0.1:9999", timeout=0.5)
    response = client.search("test offline")

    assert response.is_error is True
    assert response.is_offline is True
    assert "Could not connect" in response.error_message or "timed out" in response.error_message

    # Verify error HTML renders with Retry button
    html = render_search_results_html(response)
    assert "GAVIX Search Offline" in html
    assert "Retry Search" in html


def test_empty_search_results():
    response = SearchResponse(
        query="xyzrareword",
        results=[],
        index_status=IndexStatus(documents_indexed=100, coverage_note="Limited coverage")
    )
    html = render_search_results_html(response)
    assert "No results found in current GAVIX index" in html
    assert "Limited coverage" in html


def test_successful_search_results_and_xss_protection():
    # Ensure XSS injection in title or snippet is strictly sanitized
    response = SearchResponse(
        query="security test",
        results=[
            SearchResultItem(
                title="<script>alert(1)</script> Safe Title",
                url="https://gavix.org/docs",
                snippet="Bold <b>text</b> and <img src=x onerror=alert(2)> snippet."
            )
        ],
        index_status=IndexStatus(documents_indexed=500, coverage_note="Sample index")
    )
    html = render_search_results_html(response)

    # HTML must NOT contain unescaped executable scripts or tags
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<img src=x onerror=alert(2)>" not in html
    assert "&lt;img src=x onerror=alert(2)&gt;" in html
    assert "https://gavix.org/docs" in html
    assert "Sample index" in html
