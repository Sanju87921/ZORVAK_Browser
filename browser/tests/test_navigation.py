"""
Unit tests for GAVIX Browser navigation and omnibox routing.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from gavix_browser.navigation import is_valid_url_or_domain, resolve_address_input


def test_explicit_urls():
    is_url, url = is_valid_url_or_domain("https://example.com")
    assert is_url is True
    assert url == "https://example.com"

    is_url, url = is_valid_url_or_domain("http://mytest.org/page?query=1")
    assert is_url is True
    assert url == "http://mytest.org/page?query=1"


def test_domain_names_without_scheme():
    is_url, url = is_valid_url_or_domain("wikipedia.org")
    assert is_url is True
    assert url == "https://wikipedia.org"

    is_url, url = is_valid_url_or_domain("gavix.in/about")
    assert is_url is True
    assert url == "https://gavix.in/about"


def test_localhost_and_ip():
    is_url, url = is_valid_url_or_domain("localhost:8000")
    assert is_url is True
    assert url == "http://localhost:8000"

    is_url, url = is_valid_url_or_domain("127.0.0.1:3000")
    assert is_url is True
    assert url == "http://127.0.0.1:3000"


def test_unsafe_schemes_rejected():
    is_url, url = is_valid_url_or_domain("javascript:alert(1)")
    assert is_url is False

    is_url, url = is_valid_url_or_domain("data:text/html,<h1>hack</h1>")
    assert is_url is False


def test_search_query_routing():
    res = resolve_address_input("quantum computing news")
    assert "/api/v1/search?q=quantum+computing+news" in res

    res = resolve_address_input("how to bake sourdough bread")
    assert "/api/v1/search?q=how+to+bake+sourdough+bread" in res


def test_whitespace_trimmed():
    is_url, url = is_valid_url_or_domain("   https://example.com   ")
    assert is_url is True
    assert url == "https://example.com"
