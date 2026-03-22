"""Semantic Scholar API client with rate limiting and retry."""

from __future__ import annotations

import time

import httpx

from r2.rag.semantic_scholar.focus import FOCUS_MODES, FocusConfig
from r2.rag.semantic_scholar.types import S2Citation, S2Paper

# Fields to request from the S2 API
_PAPER_FIELDS = ",".join([
    "paperId",
    "title",
    "year",
    "abstract",
    "venue",
    "publicationVenue",
    "citationCount",
    "authors",
    "externalIds",
    "url",
    "openAccessPdf",
    "publicationTypes",
])

_CITATION_FIELDS = ",".join([
    "paperId",
    "title",
    "year",
    "abstract",
    "venue",
    "citationCount",
    "authors",
    "externalIds",
    "url",
])


class SemanticScholarClient:
    """Sync client for the Semantic Scholar Graph API."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.semanticscholar.org/graph/v1",
        rate_limit: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.rate_limit = rate_limit
        self._last_request: float = 0.0

        headers = {"Accept": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key

        self._client = httpx.Client(
            headers=headers,
            timeout=30.0,
        )

    def _throttle(self) -> None:
        """Enforce rate limiting."""
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request = time.monotonic()

    def _get(self, path: str, params: dict | None = None, max_retries: int = 3) -> dict:
        """Make a GET request with retry on 429."""
        url = f"{self.base_url}{path}"
        for attempt in range(max_retries):
            self._throttle()
            resp = self._client.get(url, params=params)

            if resp.status_code == 429:
                wait = 2 ** attempt
                time.sleep(wait)
                continue

            resp.raise_for_status()
            return resp.json()

        raise httpx.HTTPStatusError(
            "Rate limited after retries",
            request=resp.request,
            response=resp,
        )

    def search(
        self,
        query: str,
        n_results: int = 10,
        focus: str = "broad",
        year: str | None = None,
        min_citations: int | None = None,
    ) -> list[S2Paper]:
        """Search for papers by keyword query.

        Args:
            query: Search query string.
            n_results: Number of results to return after filtering.
            focus: Focus mode name (broad, top_journals, classical, recent).
            year: Year range filter (e.g. "2020-2025" or "2020-").
            min_citations: Minimum citation count override.
        """
        focus_config = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])
        fetch_n = n_results * focus_config.over_fetch_factor

        params: dict = {
            "query": query,
            "limit": min(fetch_n, 100),  # S2 API max is 100
            "fields": _PAPER_FIELDS,
        }
        if year:
            params["year"] = year
        elif focus_config.year_range:
            params["year"] = f"{focus_config.year_range[0]}-{focus_config.year_range[1]}"

        if min_citations is not None:
            params["minCitationCount"] = min_citations
        elif focus_config.min_citations:
            params["minCitationCount"] = focus_config.min_citations

        data = self._get("/paper/search", params=params)
        papers = [S2Paper.from_api(p) for p in (data.get("data") or [])]

        # Client-side venue/type filtering
        if focus_config.venues or focus_config.publication_types:
            papers = [p for p in papers if focus_config.matches(p)]

        return papers[:n_results]

    def get_paper(self, paper_id: str) -> S2Paper:
        """Get details for a single paper.

        Args:
            paper_id: S2 paper ID, DOI (e.g. "DOI:10.1234/..."),
                      ArXiv ID, or other supported identifier.
        """
        params = {"fields": _PAPER_FIELDS}
        data = self._get(f"/paper/{paper_id}", params=params)
        return S2Paper.from_api(data)

    def get_citations(self, paper_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get papers that cite the given paper (forward citations).

        Args:
            paper_id: S2 paper ID or other identifier.
            n_results: Max number of citing papers to return.
        """
        params = {
            "fields": _CITATION_FIELDS,
            "limit": min(n_results, 100),
        }
        data = self._get(f"/paper/{paper_id}/citations", params=params)
        return [
            S2Citation.from_api(item, key="citingPaper").citing_paper
            for item in (data.get("data") or [])
        ]

    def get_references(self, paper_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get papers referenced by the given paper (backward citations).

        Args:
            paper_id: S2 paper ID or other identifier.
            n_results: Max number of referenced papers to return.
        """
        params = {
            "fields": _CITATION_FIELDS,
            "limit": min(n_results, 100),
        }
        data = self._get(f"/paper/{paper_id}/references", params=params)
        return [
            S2Citation.from_api(item, key="citedPaper").citing_paper
            for item in (data.get("data") or [])
        ]

    def close(self) -> None:
        self._client.close()
