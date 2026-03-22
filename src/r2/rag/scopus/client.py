"""Elsevier Scopus API client with rate limiting and retry."""

from __future__ import annotations

import time

import httpx

from r2.rag.semantic_scholar.focus import FOCUS_MODES, FocusConfig
from r2.rag.semantic_scholar.types import S2Author, S2Paper


def _parse_entry(entry: dict) -> S2Paper:
    """Convert a Scopus search entry to an S2Paper."""
    # Authors - COMPLETE view provides full author list
    authors: list[S2Author] = []
    for a in entry.get("author") or []:
        given = a.get("given-name") or a.get("initials") or ""
        surname = a.get("surname") or a.get("authname") or ""
        name = f"{given} {surname}".strip() or "Unknown"
        authors.append(S2Author(
            author_id=a.get("authid") or "",
            name=name,
        ))
    # Fallback to dc:creator if no author list
    if not authors:
        creator = entry.get("dc:creator") or ""
        if creator:
            authors.append(S2Author(author_id="", name=creator))

    # DOI
    doi = entry.get("prism:doi") or ""

    # External IDs
    external_ids: dict[str, str] = {}
    if doi:
        external_ids["DOI"] = doi
    scopus_id = (entry.get("dc:identifier") or "").replace("SCOPUS_ID:", "")
    if scopus_id:
        external_ids["Scopus"] = scopus_id
    eid = entry.get("eid") or ""
    if eid:
        external_ids["EID"] = eid

    # Year from coverDate (YYYY-MM-DD)
    cover_date = entry.get("prism:coverDate") or ""
    year = int(cover_date[:4]) if cover_date and len(cover_date) >= 4 else None

    # Venue
    venue = entry.get("prism:publicationName") or ""

    # Citation count
    cite_str = entry.get("citedby-count") or "0"
    citation_count = int(cite_str) if cite_str.isdigit() else 0

    # Abstract (dc:description, available in COMPLETE view)
    abstract = entry.get("dc:description")

    # Open access
    oa_flag = entry.get("openaccessFlag")
    oa_pdf = None
    if oa_flag:
        # Try to find full-text link
        for link in entry.get("link") or []:
            if link.get("@ref") == "full-text":
                oa_pdf = link.get("@href")
                break

    # Scopus URL
    url = ""
    for link in entry.get("link") or []:
        if link.get("@ref") == "scopus":
            url = link.get("@href") or ""
            break

    # Publication type
    subtype = entry.get("subtypeDescription") or entry.get("subtype") or ""
    publication_types = [subtype] if subtype else []

    return S2Paper(
        paper_id=scopus_id,
        title=entry.get("dc:title") or "Untitled",
        year=year,
        abstract=abstract,
        venue=venue,
        publication_venue=venue,
        citation_count=citation_count,
        authors=authors,
        external_ids=external_ids,
        url=url,
        open_access_pdf=oa_pdf,
        publication_types=publication_types,
    )


class ScopusClient:
    """Sync client for the Elsevier Scopus Search API."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.elsevier.com",
        rate_limit: float = 0.2,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.rate_limit = rate_limit
        self._last_request: float = 0.0

        self._client = httpx.Client(
            headers={
                "Accept": "application/json",
                "X-ELS-APIKey": api_key,
            },
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

    def _build_query(
        self,
        query: str,
        focus: str = "broad",
        year: str | None = None,
        min_citations: int | None = None,
    ) -> str:
        """Build a Scopus query string with filters."""
        focus_config = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])

        # Base query
        q = f"TITLE-ABS-KEY({query})"

        # Year filter
        if year:
            if "-" in year:
                parts = year.split("-")
                start = parts[0]
                end = parts[1] if parts[1] else ""
                if start and end:
                    q += f" AND PUBYEAR > {int(start) - 1} AND PUBYEAR < {int(end) + 1}"
                elif start:
                    q += f" AND PUBYEAR > {int(start) - 1}"
            else:
                q += f" AND PUBYEAR = {year}"
        elif focus_config.year_range:
            q += f" AND PUBYEAR > {focus_config.year_range[0] - 1} AND PUBYEAR < {focus_config.year_range[1] + 1}"

        # Document type filter for journal articles
        if focus_config.publication_types and "JournalArticle" in focus_config.publication_types:
            q += " AND DOCTYPE(ar)"

        return q

    def search(
        self,
        query: str,
        n_results: int = 10,
        focus: str = "broad",
        year: str | None = None,
        min_citations: int | None = None,
    ) -> list[S2Paper]:
        """Search Scopus for papers.

        Args:
            query: Search query string.
            n_results: Number of results to return after filtering.
            focus: Focus mode name (broad, top_journals, classical, recent).
            year: Year range filter (e.g. "2020-2025" or "2020-").
            min_citations: Minimum citation count override.
        """
        focus_config = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])
        fetch_n = n_results * focus_config.over_fetch_factor

        scopus_query = self._build_query(query, focus, year, min_citations)

        params: dict = {
            "query": scopus_query,
            "count": min(fetch_n, 25),  # Scopus max per page is 25
            "view": "COMPLETE",
            "sort": "relevancy",
            "httpAccept": "application/json",
        }

        data = self._get("/content/search/scopus", params=params)
        entries = data.get("search-results", {}).get("entry") or []

        # Check for error entries (e.g. "Result set was empty")
        if entries and entries[0].get("error"):
            return []

        papers = [_parse_entry(e) for e in entries]

        # Apply citation floor
        effective_min_cites = min_citations if min_citations is not None else focus_config.min_citations
        if effective_min_cites:
            papers = [p for p in papers if p.citation_count >= effective_min_cites]

        # Client-side venue/type filtering
        if focus_config.venues or focus_config.publication_types:
            papers = [p for p in papers if focus_config.matches(p)]

        return papers[:n_results]

    def get_paper(self, scopus_id: str) -> S2Paper:
        """Get details for a single paper via Abstract Retrieval.

        Args:
            scopus_id: Scopus ID, EID, or DOI.
        """
        # Determine path based on ID format
        if scopus_id.startswith("10."):
            path = f"/content/abstract/doi/{scopus_id}"
        elif scopus_id.startswith("DOI:"):
            path = f"/content/abstract/doi/{scopus_id[4:]}"
        elif scopus_id.startswith("2-s2.0-"):
            path = f"/content/abstract/eid/{scopus_id}"
        else:
            path = f"/content/abstract/scopus_id/{scopus_id}"

        data = self._get(path, params={"httpAccept": "application/json"})
        resp = data.get("abstracts-retrieval-response", {})
        cd = resp.get("coredata", {})

        # Authors
        authors: list[S2Author] = []
        for a in (resp.get("authors", {}).get("author") or []):
            given = a.get("ce:given-name") or a.get("ce:initials") or ""
            surname = a.get("ce:surname") or ""
            name = f"{given} {surname}".strip() or "Unknown"
            authors.append(S2Author(
                author_id=a.get("@auid") or "",
                name=name,
            ))

        doi = cd.get("prism:doi") or ""
        external_ids: dict[str, str] = {}
        if doi:
            external_ids["DOI"] = doi
        sid = (cd.get("dc:identifier") or "").replace("SCOPUS_ID:", "")
        if sid:
            external_ids["Scopus"] = sid
        eid = cd.get("eid") or ""
        if eid:
            external_ids["EID"] = eid

        cover_date = cd.get("prism:coverDate") or ""
        year_val = int(cover_date[:4]) if cover_date and len(cover_date) >= 4 else None

        return S2Paper(
            paper_id=sid,
            title=cd.get("dc:title") or "Untitled",
            year=year_val,
            abstract=cd.get("dc:description"),
            venue=cd.get("prism:publicationName") or "",
            publication_venue=cd.get("prism:publicationName") or "",
            citation_count=int(cd.get("citedby-count") or 0),
            authors=authors,
            external_ids=external_ids,
            url=cd.get("prism:url") or "",
            open_access_pdf=None,
            publication_types=[cd.get("subtypeDescription") or ""],
        )

    def get_citations(self, scopus_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get papers that cite the given paper (forward citations via search refid).

        Args:
            scopus_id: Scopus ID.
            n_results: Max number of citing papers.
        """
        query = f"REF({scopus_id})"
        params: dict = {
            "query": query,
            "count": min(n_results, 25),
            "view": "COMPLETE",
            "sort": "citedby-count",
            "httpAccept": "application/json",
        }
        data = self._get("/content/search/scopus", params=params)
        entries = data.get("search-results", {}).get("entry") or []
        if entries and entries[0].get("error"):
            return []
        return [_parse_entry(e) for e in entries][:n_results]

    def get_references(self, scopus_id: str, n_results: int = 10) -> list[S2Paper]:
        """Get references from a paper via Abstract Retrieval.

        Note: Scopus references in the abstract retrieval are limited metadata.
        Falls back to search if needed.

        Args:
            scopus_id: Scopus ID.
            n_results: Max number of referenced papers.
        """
        # Use Abstract Retrieval with references view
        path = f"/content/abstract/scopus_id/{scopus_id}"
        params: dict = {
            "view": "REF",
            "httpAccept": "application/json",
        }
        try:
            data = self._get(path, params=params)
        except httpx.HTTPStatusError:
            return []

        resp = data.get("abstracts-retrieval-response", {})
        ref_list = resp.get("references", {}).get("reference") or []

        papers: list[S2Paper] = []
        for ref in ref_list[:n_results]:
            info = ref.get("ref-info", {})
            # Author
            author_group = info.get("ref-authors", {})
            auth_list = author_group.get("author") or []
            if isinstance(auth_list, dict):
                auth_list = [auth_list]
            authors = []
            for a in auth_list:
                name = a.get("ce:indexed-name") or a.get("ce:surname") or "Unknown"
                authors.append(S2Author(author_id="", name=name))

            title_info = info.get("ref-title", {})
            title = title_info.get("ref-titletext") or "Untitled"
            source = info.get("ref-sourcetitle") or ""
            year_str = info.get("ref-publicationyear", {}).get("@first") or ""
            year_val = int(year_str) if year_str.isdigit() else None

            ext_ids: dict[str, str] = {}
            refd_id = ref.get("@id") or ""
            if refd_id:
                ext_ids["ScopusRef"] = refd_id

            papers.append(S2Paper(
                paper_id=refd_id,
                title=title,
                year=year_val,
                abstract=None,
                venue=source,
                publication_venue=source,
                citation_count=0,
                authors=authors,
                external_ids=ext_ids,
                url="",
                open_access_pdf=None,
                publication_types=[],
            ))

        return papers

    def close(self) -> None:
        self._client.close()
