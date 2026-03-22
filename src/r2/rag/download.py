"""Paper download via SciDownl (Sci-Hub) with clean filenames, error handling,
and automatic Zotero integration.

Includes a direct Sci-Hub scraping fallback when scidownl fails."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Sci-Hub mirrors to try for direct scraping fallback (in order)
SCIHUB_MIRRORS = [
    "https://sci-hub.st",
    "https://sci-hub.se",
    "https://sci-hub.ru",
]

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class DownloadResult:
    """Result of a single paper download attempt."""

    identifier: str
    paper_type: str
    success: bool
    filepath: str | None = None
    error: str | None = None
    zotero_key: str | None = None
    zotero_error: str | None = None

    def format(self) -> str:
        parts = []
        if self.success:
            parts.append(f"OK  {self.identifier} -> {self.filepath}")
        else:
            parts.append(f"FAIL  {self.identifier} — {self.error}")
        if self.zotero_key:
            parts.append(f"  Zotero: added ({self.zotero_key})")
        elif self.zotero_error:
            parts.append(f"  Zotero: {self.zotero_error}")
        return "\n".join(parts)


def _sanitize_filename(name: str, max_len: int = 80) -> str:
    """Convert a string to a safe filename."""
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:max_len]


def _detect_paper_type(identifier: str) -> str:
    """Auto-detect whether identifier is a DOI, PMID, or title."""
    identifier = identifier.strip()
    # DOI patterns
    if identifier.startswith("10.") or identifier.startswith("https://doi.org/"):
        return "doi"
    # Pure numeric -> PMID
    if identifier.isdigit():
        return "pmid"
    # Otherwise treat as title
    return "title"


def _add_to_zotero(
    result: DownloadResult,
    library_id: str,
    api_key: str,
    title: str | None = None,
) -> None:
    """Add a successfully downloaded paper to Zotero. Mutates result in place."""
    from r2.rag.zotero import add_to_zotero

    zr = add_to_zotero(
        library_id=library_id,
        api_key=api_key,
        identifier=result.identifier,
        paper_type=result.paper_type,
        pdf_path=result.filepath,
        title=title,
    )
    if zr.success:
        result.zotero_key = zr.item_key
        if zr.error:  # partial success (item created but PDF attach failed)
            result.zotero_error = zr.error
    else:
        result.zotero_error = zr.error


def _direct_scihub_download(
    identifier: str,
    out_file: str,
    scihub_url: str | None = None,
) -> str | None:
    """Fallback: scrape Sci-Hub page directly to find and download the PDF.

    Returns None on success, or an error message on failure.
    """
    mirrors = [scihub_url] if scihub_url else SCIHUB_MIRRORS

    for mirror in mirrors:
        try:
            page_url = f"{mirror.rstrip('/')}/{identifier}"
            logger.info(f"Direct Sci-Hub fallback: {page_url}")

            with httpx.Client(
                follow_redirects=True,
                timeout=30,
                headers={"User-Agent": _BROWSER_UA},
            ) as client:
                resp = client.get(page_url)
                if resp.status_code != 200:
                    logger.warning(f"Sci-Hub page returned {resp.status_code} from {mirror}")
                    continue

                html = resp.text

                # Extract PDF URL from citation_pdf_url meta tag
                match = re.search(
                    r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"',
                    html,
                )
                if not match:
                    # Also try embedded iframe/embed src with .pdf
                    match = re.search(r'(?:src|href)="([^"]*\.pdf[^"]*)"', html)
                if not match:
                    logger.warning(f"No PDF URL found on {mirror} page")
                    continue

                pdf_path = match.group(1)

                # Resolve relative URL
                if pdf_path.startswith("/"):
                    pdf_url = f"{mirror.rstrip('/')}{pdf_path}"
                elif not pdf_path.startswith("http"):
                    pdf_url = f"{mirror.rstrip('/')}/{pdf_path}"
                else:
                    pdf_url = pdf_path

                logger.info(f"Downloading PDF from: {pdf_url}")
                pdf_resp = client.get(pdf_url)
                if pdf_resp.status_code != 200:
                    logger.warning(f"PDF download returned {pdf_resp.status_code}")
                    continue

                # Verify it looks like a PDF
                if not pdf_resp.content[:5].startswith(b"%PDF"):
                    logger.warning("Downloaded content is not a valid PDF")
                    continue

                Path(out_file).parent.mkdir(parents=True, exist_ok=True)
                Path(out_file).write_bytes(pdf_resp.content)
                logger.info(f"Direct Sci-Hub download succeeded: {out_file}")
                return None  # success

        except Exception as e:
            logger.warning(f"Direct Sci-Hub fallback failed for {mirror}: {e}")
            continue

    return "All Sci-Hub mirrors failed (both scidownl and direct scraping)"


def _lightpanda_download(
    identifier: str,
    out_file: str,
    scihub_url: str | None = None,
) -> str | None:
    """Fallback: use Lightpanda headless browser to render Sci-Hub and find PDF.

    Returns None on success, or an error message on failure.
    """
    try:
        from r2.rag.browser import lightpanda_download
        return lightpanda_download(
            identifier=identifier,
            out_file=out_file,
            scihub_url=scihub_url,
        )
    except ImportError:
        return "Lightpanda browser module not available"
    except Exception as e:
        return f"Lightpanda browser fallback error: {e}"


def download_paper(
    identifier: str,
    paper_type: str | None = None,
    out_dir: str | Path = "rag/pdfs",
    filename: str | None = None,
    scihub_url: str | None = None,
    proxies: dict | None = None,
    zotero_library_id: str | None = None,
    zotero_api_key: str | None = None,
    title: str | None = None,
) -> DownloadResult:
    """Download a single paper via Sci-Hub and add to Zotero.

    Args:
        identifier: DOI, PMID, or title.
        paper_type: "doi", "pmid", or "title". Auto-detected if None.
        out_dir: Directory to save the PDF.
        filename: Custom filename (without .pdf extension). Auto-generated if None.
        scihub_url: Explicit Sci-Hub mirror URL (auto-selected if None).
        proxies: Proxy dict, e.g. {"http": "socks5://127.0.0.1:7890"}.
        zotero_library_id: Zotero library ID for auto-add. Skips if None.
        zotero_api_key: Zotero API key for auto-add. Skips if None.
        title: Paper title (used for Zotero metadata when DOI lookup fails).

    Returns:
        DownloadResult with success status, filepath, and Zotero status.
    """
    try:
        from scidownl import scihub_download
    except ImportError:
        scihub_download = None
        logger.warning("scidownl not installed — will use direct Sci-Hub scraping only")

    if paper_type is None:
        paper_type = _detect_paper_type(identifier)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Build output filepath
    if filename:
        safe_name = _sanitize_filename(filename)
    elif paper_type == "doi":
        doi_part = identifier.replace("https://doi.org/", "")
        safe_name = _sanitize_filename(doi_part)
    else:
        safe_name = _sanitize_filename(identifier)

    out_file = str(out_path / f"{safe_name}.pdf")

    scidownl_ok = False
    if scihub_download is not None:
        try:
            scihub_download(
                keyword=identifier,
                paper_type=paper_type,
                scihub_url=scihub_url,
                out=out_file,
                proxies=proxies,
            )
            scidownl_ok = Path(out_file).exists() and Path(out_file).stat().st_size > 0
        except Exception as e:
            logger.warning(f"scidownl failed for {identifier}: {e}")

    # Fallback 1: direct Sci-Hub scraping if scidownl didn't produce a valid PDF
    if not scidownl_ok:
        logger.info(f"Trying direct Sci-Hub scraping fallback for {identifier}")
        fallback_err = _direct_scihub_download(
            identifier=identifier,
            out_file=out_file,
            scihub_url=scihub_url,
        )
        if fallback_err:
            # Fallback 2: Lightpanda browser rendering (handles JS-heavy pages)
            logger.info(f"Trying Lightpanda browser fallback for {identifier}")
            browser_err = _lightpanda_download(
                identifier=identifier,
                out_file=out_file,
                scihub_url=scihub_url,
            )
            if browser_err:
                return DownloadResult(
                    identifier=identifier,
                    paper_type=paper_type,
                    success=False,
                    error=f"All methods failed. httpx: {fallback_err}; browser: {browser_err}",
                )

    # Final verification
    if not (Path(out_file).exists() and Path(out_file).stat().st_size > 0):
        return DownloadResult(
            identifier=identifier,
            paper_type=paper_type,
            success=False,
            error="Download completed but PDF file not found or empty",
        )

    result = DownloadResult(
        identifier=identifier,
        paper_type=paper_type,
        success=True,
        filepath=out_file,
    )

    # Auto-add to Zotero
    if zotero_library_id and zotero_api_key:
        _add_to_zotero(result, zotero_library_id, zotero_api_key, title=title)

    return result


def download_batch(
    identifiers: list[dict],
    out_dir: str | Path = "rag/pdfs",
    scihub_url: str | None = None,
    proxies: dict | None = None,
    zotero_library_id: str | None = None,
    zotero_api_key: str | None = None,
) -> list[DownloadResult]:
    """Download multiple papers and add each to Zotero.

    Args:
        identifiers: List of dicts, each with keys:
            - "id": the DOI, PMID, or title (required)
            - "type": "doi", "pmid", or "title" (optional, auto-detected)
            - "filename": custom filename without .pdf (optional)
            - "title": paper title for Zotero metadata (optional)
        out_dir: Directory to save PDFs.
        scihub_url: Explicit Sci-Hub mirror URL.
        proxies: Proxy dict.
        zotero_library_id: Zotero library ID for auto-add.
        zotero_api_key: Zotero API key for auto-add.

    Returns:
        List of DownloadResult objects.
    """
    results = []
    for entry in identifiers:
        identifier = entry.get("id", "")
        if not identifier:
            continue
        result = download_paper(
            identifier=identifier,
            paper_type=entry.get("type"),
            out_dir=out_dir,
            filename=entry.get("filename"),
            scihub_url=scihub_url,
            proxies=proxies,
            zotero_library_id=zotero_library_id,
            zotero_api_key=zotero_api_key,
            title=entry.get("title"),
        )
        results.append(result)
        logger.info(result.format())
    return results
