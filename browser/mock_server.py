"""
GAVIX Search - Mock API Server for Local Development and Testing.
Implements the contract agreed with Amar (Section 8 of MVP spec).
Runs at http://127.0.0.1:8000/api/v1/search
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SAMPLE_DATABASE = [
    {
        "keywords": ["karnataka", "scholarship", "engineering", "education"],
        "title": "Karnataka State Scholarship Portal (SSP)",
        "url": "https://ssp.postmatric.karnataka.gov.in",
        "snippet": "Official Karnataka state portal for post-matric and technical education scholarships for 2026-2027.",
        "source": "gavix_index",
        "last_crawled": "2026-10-12"
    },
    {
        "keywords": ["hampi", "heritage", "tourism", "karnataka", "travel"],
        "title": "Hampi Stays & Heritage Guide",
        "url": "https://hampistays.com",
        "snippet": "Explore UNESCO World Heritage monuments, Vijayanagara architecture, and verified accommodations in Hampi.",
        "source": "gavix_index",
        "last_crawled": "2026-10-10"
    },
    {
        "keywords": ["python", "pyside6", "qt", "browser", "development"],
        "title": "Qt for Python (PySide6) Documentation",
        "url": "https://doc.qt.io/qtforpython-6/",
        "snippet": "Official Python bindings for Qt 6. Complete API guides for QtWebEngine, GUI widgets, and desktop architectures.",
        "source": "gavix_index",
        "last_crawled": "2026-10-09"
    },
    {
        "keywords": ["gavix", "browser", "privacy", "search"],
        "title": "GAVIX: Gateway for Advanced Virtual Internet Experience",
        "url": "https://gavix.org",
        "snippet": "Decentralized, privacy-first desktop web platform with isolated local storage and independent indexing.",
        "source": "gavix_index",
        "last_crawled": "2026-10-12"
    }
]


class GavixMockSearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/search":
            query_params = parse_qs(parsed.query)
            q = query_params.get("q", [""])[0].lower().strip()
            page = int(query_params.get("page", ["1"])[0])
            limit = int(query_params.get("limit", ["10"])[0])

            # Filter matching results
            matched = []
            if q:
                tokens = q.split()
                for doc in SAMPLE_DATABASE:
                    if any(t in doc["title"].lower() or t in doc["snippet"].lower() or t in doc["keywords"] for t in tokens):
                        matched.append(doc)
            else:
                matched = SAMPLE_DATABASE

            response_data = {
                "query": q,
                "page": page,
                "limit": limit,
                "total_estimate": len(matched),
                "results": matched,
                "index_status": {
                    "documents_indexed": 1250,
                    "coverage_note": "Results are limited to pages currently indexed by GAVIX."
                }
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silent or minimal logging
        pass


def run_mock_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, GavixMockSearchHandler)
    print(f"GAVIX Mock Search API running at http://127.0.0.1:{port}/api/v1/search")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_mock_server()
