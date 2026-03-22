"""Zotero integration: add items by DOI and attach PDFs via pyzotero web API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx
from pyzotero import zotero

logger = logging.getLogger(__name__)


@dataclass
class ZoteroResult:
    """Result of a Zotero add operation."""

    success: bool
    item_key: str | None = None
    error: str | None = None

    def format(self) -> str:
        if self.success:
            return f"Zotero: added item {self.item_key}"
        return f"Zotero: failed — {self.error}"


def _resolve_doi_metadata(doi: str) -> dict | None:
    """Resolve a DOI to metadata via CrossRef API."""
    try:
        resp = httpx.get(
            f"https://api.crossref.org/works/{doi}",
            headers={"Accept": "application/json"},
            timeout=15,
            follow_redirects=True,
        )
        resp.raise_for_status()
        return resp.json().get("message", {})
    except Exception as e:
        logger.warning("CrossRef lookup failed for %s: %s", doi, e)
        return None


def _build_item_from_crossref(meta: dict, doi: str) -> dict:
    """Map CrossRef metadata to a Zotero item dict."""
    item_type = "journalArticle"
    # Detect book chapters / books
    cr_type = meta.get("type", "")
    if cr_type == "book-chapter":
        item_type = "bookSection"
    elif cr_type == "book":
        item_type = "book"

    creators = []
    for author in meta.get("author", []):
        creators.append({
            "creatorType": "author",
            "firstName": author.get("given", ""),
            "lastName": author.get("family", ""),
        })

    title_list = meta.get("title", [])
    title = title_list[0] if title_list else "Untitled"

    container = meta.get("container-title", [])
    venue = container[0] if container else ""

    # Extract year from date-parts
    year = ""
    date_parts = meta.get("published", {}).get("date-parts", [[]])
    if date_parts and date_parts[0]:
        year = str(date_parts[0][0])

    item = {
        "itemType": item_type,
        "title": title,
        "creators": creators,
        "DOI": doi,
        "url": f"https://doi.org/{doi}",
        "date": year,
        "volume": meta.get("volume", ""),
        "issue": meta.get("issue", ""),
        "pages": meta.get("page", ""),
    }

    if item_type == "journalArticle":
        item["publicationTitle"] = venue
    elif item_type == "bookSection":
        item["bookTitle"] = venue
    elif item_type == "book":
        item["publisher"] = meta.get("publisher", "")

    # Clean empty values
    return {k: v for k, v in item.items() if v}


def _build_minimal_item(title: str, doi: str | None = None) -> dict:
    """Build a minimal Zotero item when metadata resolution fails."""
    item = {
        "itemType": "journalArticle",
        "title": title,
    }
    if doi:
        item["DOI"] = doi
        item["url"] = f"https://doi.org/{doi}"
    return item


def add_to_zotero(
    library_id: str,
    api_key: str,
    identifier: str,
    paper_type: str = "doi",
    pdf_path: str | None = None,
    title: str | None = None,
) -> ZoteroResult:
    """Add a paper to Zotero and optionally attach a PDF.

    Args:
        library_id: Zotero user library ID.
        api_key: Zotero API key.
        identifier: DOI, PMID, or title used for the download.
        paper_type: "doi", "pmid", or "title".
        pdf_path: Path to the downloaded PDF to attach.
        title: Paper title (used as fallback if metadata lookup fails).
    """
    try:
        zot = zotero.Zotero(library_id, "user", api_key)
    except Exception as e:
        return ZoteroResult(success=False, error=f"Zotero connection failed: {e}")

    # Build the item
    doi = identifier if paper_type == "doi" else None

    # Try DOI metadata resolution
    item_data = None
    if doi:
        meta = _resolve_doi_metadata(doi)
        if meta:
            item_data = _build_item_from_crossref(meta, doi)

    # Fallback: minimal item
    if item_data is None:
        display_title = title or identifier
        item_data = _build_minimal_item(display_title, doi=doi)

    # Get template and merge
    try:
        template = zot.item_template(item_data.get("itemType", "journalArticle"))
        for key, value in item_data.items():
            if key in template:
                template[key] = value
            elif key == "creators":
                template["creators"] = value
        result = zot.create_items([template])
    except Exception as e:
        return ZoteroResult(success=False, error=f"Item creation failed: {e}")

    # Extract item key
    success_map = result.get("successful", result.get("success", {}))
    if not success_map:
        failed = result.get("failed", {})
        return ZoteroResult(success=False, error=f"Zotero rejected item: {failed}")

    item_key = None
    for v in success_map.values():
        if isinstance(v, dict):
            item_key = v.get("key") or v.get("data", {}).get("key")
        elif isinstance(v, str):
            item_key = v
        break

    if not item_key:
        return ZoteroResult(success=False, error="Could not extract item key from response")

    # Attach PDF
    if pdf_path and Path(pdf_path).exists():
        try:
            zot.attachment_simple([pdf_path], parentid=item_key)
        except Exception as e:
            logger.warning("PDF attachment failed for %s: %s", item_key, e)
            return ZoteroResult(
                success=True,
                item_key=item_key,
                error=f"Item created but PDF attach failed: {e}",
            )

    return ZoteroResult(success=True, item_key=item_key)
