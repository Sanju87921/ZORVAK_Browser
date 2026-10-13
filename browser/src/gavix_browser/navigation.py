"""
GAVIX Browser - Navigation and Omnibox Routing Logic.
Parses user input in the address bar and decides whether to navigate directly
or route to search.
"""

import re
from urllib.parse import urlparse, quote_plus

# Common top-level domains for hostname detection
COMMON_TLDS = {
    "com", "org", "net", "in", "edu", "gov", "mil", "io", "ai", "co",
    "dev", "app", "me", "info", "biz", "xyz", "online", "tech", "site"
}

SAFE_SCHEMES = {"http", "https", "file", "about", "gavix"}


def is_valid_url_or_domain(text: str) -> tuple[bool, str]:
    """
    Evaluates whether input string represents a direct URL/domain or a search query.
    Returns: (is_url: bool, target_url: str)
    """
    text = text.strip()
    if not text:
        return False, ""

    # Check for localhost / loopback addresses
    if text.startswith("localhost") or text.startswith("127.0.0.1"):
        return True, f"http://{text}"

    # Check for explicit scheme (e.g. https://, http://, about:blank)
    if "://" in text or text.startswith("about:"):
        parsed = urlparse(text)
        if parsed.scheme.lower() in SAFE_SCHEMES:
            return True, text
        # Reject unsupported or unsafe schemes like javascript:, data:, etc.
        return False, ""

    # Check if input looks like a domain name with no spaces (e.g., example.com, test.in/path)
    if " " not in text:
        # Check for hostname with port, e.g. 192.168.1.1:8000
        ip_port_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$"
        if re.match(ip_port_pattern, text):
            return True, f"http://{text}"

        domain_pattern = r"^([a-zA-Z0-9-]+\.)+([a-zA-Z]{2,})(:[0-9]+)?(/.*)?$"
        match = re.match(domain_pattern, text)
        if match:
            # Check if TLD is reasonable
            parts = text.split("/")[0].split(":")[0].split(".")
            tld = parts[-1].lower()
            if tld in COMMON_TLDS or len(tld) in [2, 3, 4]:
                # Default to HTTPS for modern web security
                return True, f"https://{text}"

    return False, ""


def is_search_query(text: str) -> tuple[bool, str]:
    """
    Determines if input is a search query or a direct URL.
    Returns: (is_query: bool, resolved_content: str)
    """
    is_url, url = is_valid_url_or_domain(text)
    if is_url:
        return False, url
    return True, text.strip()


def resolve_address_input(text: str, search_base_url: str = "http://127.0.0.1:8000") -> str:
    """
    Resolves address bar input into either a direct URL or GAVIX Search API URL.
    """
    is_query, content = is_search_query(text)
    if not is_query:
        return content

    # Default to search query routing
    query = quote_plus(content)
    return f"{search_base_url.rstrip('/')}/api/v1/search?q={query}"
