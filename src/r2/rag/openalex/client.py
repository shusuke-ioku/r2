"""OpenAlex API client with rate limiting and retry."""

from __future__ import annotations

import time

import httpx

from r2.rag.semantic_scholar.focus import FOCUS_MODES, FocusConfig
from r2.rag.semantic_scholar.types import S2Author, S2Paper


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """Reconstruct abstract text from OpenAlex abstract_inverted_index."""
    if not inverted_index:
        return None
    pos_word = []
    for word, positions in inverted_index.items():
        for pos in positions:
            pos_word.append((pos, word))
    pos_word.sort()
    return " ".join(w for _, w in pos_word)


def _parse_work(data: dict) -> S2Paper:
    """Convert an OpenAlex Work object to an S2Paper."""
    # Authors
    authors = []
    for authorship in data.get("authorships") or []:
        author = authorship.get("author") or {}
        authors.append(S2Author(
            author_id=author.get("id") or "",
            name=author.get("display_name") or "Unknown",
        ))

    # Venue from primary_location.source
    venue = ""
    publication_venue = ""
    loc = data.get("primary_location") or {}
    source = loc.get("source") or {}
    if source:
        venue = source.get("display_name") or ""
        publication_venue = venue

    # DOI
    doi_raw = data.get("doi") or ""
    doi = doi_raw.replace("https://doi.org/", "") if doi_raw else ""

    # External IDs
    external_ids: dict[str, str] = {}
    if doi:
        external_ids["DOI"] = doi
    ids = data.get("ids") or {}
    if ids.get("pmid"):
        external_ids["PubMed"] = str(ids["pmid"]).replace("https://pubmed.ncbi.nlm.nih.gov/", "")
    openalex_id = (data.get("id") or "").replace("https://openalex.org/", "")
    if openalex_id:
        external_ids["OpenAlex"] = openalex_id

    # Open access PDF
    oa = data.get("open_access") or {}
    oa_pdf = oa.get("oa_url")
    if not oa_pdf:
        oa_pdf = loc.get("pdf_url")

    # Publication types
    pub_type = data.get("type") or ""
    publication_types = [pub_type] if pub_type else []

    # Abstract
    abstract = _reconstruct_abstract(data.get("abstract_inverted_index"))

    return S2Paper(
        paper_id=openalex_id,
        title=data.get("title") or data.get("display_name") or "Untitled",
        year=data.get("publication_year"),
        abstract=abstract,
        venue=venue,
        publication_venue=publication_venue,
        citation_count=data.get("cited_by_count") or 0,
        authors=authors,
        external_ids=external_ids,
        url=f"https://openalex.org/{openalex_id}" if openalex_id else "",
        open_access_pdf=oa_pdf,
        publication_types=publication_types,
    )


class OpenAlexClient:
    """Sync client for the OpenAlex API."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.openalex.org",
        rate_limit: float = 0.2,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.rate_limit = rate_limit
        self._last_request: float = 0.0

        self._client = httpx.Client(
            headers={"Accept": "application/json"},
            timeout=30.0,
        )

    def _throttle(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request = time.monotonic()

    def _get(self, path: str, params: dict | None = None, max_retries: int = 3) -> dict:
        url = f"{self.base_url}{path}"
        if params is None:
            params = {}
        if self.api_key:
            params["api_key"] = self.api_key

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
        """Search for works by keyword query.

        Args:
            query: Search query string.
            n_results: Number of results to return after filtering.
            focus: Focus mode name (broad, top_journals, classical, recent).
            year: Year range filter (e.g. "2020-2025" or "2020-").
            min_citations: Minimum citation count override.
        """
        focus_config = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])
        fetch_n = n_results * focus_config.over_fetch_factor

        # Build filter string
        filters: list[str] = []

        # Year filter
        if year:
            # Convert S2 format "2020-2025" or "2020-" to OpenAlex format
            if "-" in year:
                parts = year.split("-")
                start = parts[0]
                end = parts[1] if parts[1] else ""
                if start and end:
                    filters.append(f"publication_year:{start}-{end}")
                elif start:
                    filters.append(f"publication_year:>={start}")
            else:
                filters.append(f"publication_year:{year}")
        elif focus_config.year_range:
            filters.append(
                f"publication_year:{focus_config.year_range[0]}-{focus_config.year_range[1]}"
            )

        # Citation count filter
        effective_min_cites = min_citations if min_citations is not None else focus_config.min_citations
        if effective_min_cites:
            filters.append(f"cited_by_count:>={effective_min_cites}")

        params: dict = {
            "search": query,
            "per_page": min(fetch_n, 100),
            "select": "id,doi,title,display_name,publication_year,cited_by_count,"
                      "abstract_inverted_index,authorships,primary_location,"
                      "open_access,type,ids",
        }
        if filters:
            params["filter"] = ",".join(filters)

        data = self._get("/works", params=params)
        papers = [_parse_work(w) for w in (data.get("results") or [])]

        # Client-side venue/type filtering (same as S2)
        if focus_config.venues or focus_config.publication_types:
            papers = [p for p in papers if focus_config.matches(p)]

        return papers[:n_results]

    def get_paper(self, paper_id: str) -> S2Paper:
        """Get details for a single work.

        Args:
            paper_id: OpenAlex ID (e.g. "W123456"), DOI, or full URL.
        """
        # Normalize ID
        if paper_id.startswith("https://doi.org/"):
            path = f"/works/doi:{paper_id.replace('https://doi.org/', '')}"
        elif paper_id.startswith("10."):
            path = f"/works/doi:{paper_id}"
        elif paper_id.startswith("DOI:"):
            path = f"/works/doi:{paper_id[4:]}"
        elif paper_id.startswith("https://openalex.org/"):
            oa_id = paper_id.replace("https://openalex.org/", "")
            path = f"/works/{oa_id}"
        else:
            path = f"/works/{paper_id}"

        params = {
            "select": "id,doi,title,display_name,publication_year,cited_by_count,"
                      "abstract_inverted_index,authorships,primary_location,"
                      "open_access,type,ids,referenced_works",
        }
        data = self._get(path, params=params)
        return _parse_work(data)

    def get_citations(self, paper_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get papers that cite the given work (forward citations).

        Args:
            paper_id: OpenAlex ID (e.g. "W123456").
            n_results: Max number of citing papers to return.
        """
        # Normalize to bare OpenAlex ID
        oa_id = paper_id.replace("https://openalex.org/", "")

        params: dict = {
            "filter": f"cites:{oa_id}",
            "per_page": min(n_results, 100),
            "sort": "cited_by_count:desc",
            "select": "id,doi,title,display_name,publication_year,cited_by_count,"
                      "abstract_inverted_index,authorships,primary_location,"
                      "open_access,type,ids",
        }
        data = self._get("/works", params=params)
        return [_parse_work(w) for w in (data.get("results") or [])]

    def get_references(self, paper_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get papers referenced by the given work (backward citations).

        Args:
            paper_id: OpenAlex ID (e.g. "W123456").
            n_results: Max number of referenced papers to return.
        """
        # Normalize to bare OpenAlex ID
        oa_id = paper_id.replace("https://openalex.org/", "")

        # First get the work to find its referenced_works
        params_work: dict = {
            "select": "referenced_works",
        }
        work_data = self._get(f"/works/{oa_id}", params=params_work)
        ref_ids = work_data.get("referenced_works") or []

        if not ref_ids:
            return []

        # Fetch the referenced works (up to n_results)
        ref_ids = ref_ids[:n_results]
        # Build an OR filter using OpenAlex IDs
        oa_ids = [rid.replace("https://openalex.org/", "") for rid in ref_ids]
        filter_str = "openalex:" + "|".join(oa_ids)

        params: dict = {
            "filter": filter_str,
            "per_page": min(len(oa_ids), 100),
            "select": "id,doi,title,display_name,publication_year,cited_by_count,"
                      "abstract_inverted_index,authorships,primary_location,"
                      "open_access,type,ids",
        }
        data = self._get("/works", params=params)
        return [_parse_work(w) for w in (data.get("results") or [])]

    def close(self) -> None:
        self._client.close()
