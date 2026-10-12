"""
GAVIX Browser - Search API Client.
Communicates with Amar's GAVIX Search backend via HTTP.
Features configurable endpoints, honest telemetry parsing, timeout protection,
and fallback error states.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
import httpx


@dataclass
class SearchResultItem:
    title: str
    url: str
    snippet: str
    source: str = "gavix_index"
    last_crawled: str = ""


@dataclass
class IndexStatus:
    documents_indexed: int = 0
    coverage_note: str = "Results are limited to pages currently indexed by GAVIX."


@dataclass
class SearchResponse:
    query: str
    page: int = 1
    limit: int = 10
    total_estimate: int = 0
    results: List[SearchResultItem] = field(default_factory=list)
    index_status: IndexStatus = field(default_factory=IndexStatus)
    is_error: bool = False
    error_message: str = ""
    is_offline: bool = False


class GavixSearchClient:
    """HTTP Client for GAVIX Search API."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 4.0):
        # Respect GAVIX_SEARCH_BASE_URL environment variable
        self.base_url = (
            base_url
            or os.environ.get("GAVIX_SEARCH_BASE_URL")
            or "http://127.0.0.1:8000"
        ).rstrip("/")
        self.timeout = timeout

    def search(self, query: str, page: int = 1, limit: int = 10) -> SearchResponse:
        """
        Executes a search query against the configured GAVIX Search endpoint.
        Returns a structured SearchResponse. Never raises an uncaught exception.
        """
        clean_query = query.strip()
        if not clean_query:
            return SearchResponse(query="", results=[])

        endpoint = f"{self.base_url}/api/v1/search"
        params = {"q": clean_query, "page": page, "limit": limit}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(endpoint, params=params)

                if resp.status_code == 200:
                    data = resp.json()
                    results_list = []
                    for item in data.get("results", []):
                        # Filter only valid http/https URLs
                        item_url = item.get("url", "")
                        if item_url.startswith("http://") or item_url.startswith("https://"):
                            results_list.append(
                                SearchResultItem(
                                    title=item.get("title", "Untitled Result"),
                                    url=item_url,
                                    snippet=item.get("snippet", ""),
                                    source=item.get("source", "gavix_index"),
                                    last_crawled=item.get("last_crawled", "")
                                )
                            )

                    raw_status = data.get("index_status", {})
                    index_status = IndexStatus(
                        documents_indexed=raw_status.get("documents_indexed", 0),
                        coverage_note=raw_status.get(
                            "coverage_note",
                            "Results are limited to pages currently indexed by GAVIX."
                        )
                    )

                    return SearchResponse(
                        query=clean_query,
                        page=data.get("page", page),
                        limit=data.get("limit", limit),
                        total_estimate=data.get("total_estimate", len(results_list)),
                        results=results_list,
                        index_status=index_status
                    )
                else:
                    return SearchResponse(
                        query=clean_query,
                        is_error=True,
                        error_message=f"GAVIX Search returned HTTP status {resp.status_code}."
                    )

        except httpx.ConnectError:
            return SearchResponse(
                query=clean_query,
                is_error=True,
                is_offline=True,
                error_message=f"Could not connect to GAVIX Search at {self.base_url}. Ensure Amar's search service is running."
            )
        except httpx.TimeoutException:
            return SearchResponse(
                query=clean_query,
                is_error=True,
                is_offline=True,
                error_message=f"Request to GAVIX Search timed out after {self.timeout}s."
            )
        except Exception as e:
            return SearchResponse(
                query=clean_query,
                is_error=True,
                error_message=f"Search request failed: {str(e)}"
            )
