"""Lightpanda browser fallback for Sci-Hub downloads.

When the standard httpx-based Sci-Hub scraping fails (e.g., because the page
requires JavaScript execution to reveal the PDF link), this module uses the
Lightpanda headless browser to render the page and extract the PDF URL.

Lightpanda binary must be at .venv/bin/lightpanda (auto-detected).
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Sci-Hub mirrors to try with browser (ordered by reliability)
BROWSER_SCIHUB_MIRRORS = [
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.se",
]

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _find_lightpanda() -> str | None:
    """Find the lightpanda binary. Checks .venv/bin first, then PATH."""
    # Check project .venv
    project_root = Path(__file__).resolve().parent.parent.parent
    venv_bin = project_root / ".venv" / "bin" / "lightpanda"
    if venv_bin.is_file():
        return str(venv_bin)

    # Check system PATH
    path = shutil.which("lightpanda")
    if path:
        return path

    return None


def _extract_pdf_url_from_html(html: str, base_url: str) -> str | None:
    """Extract PDF URL from rendered HTML using multiple strategies."""
    # Strategy 1: citation_pdf_url meta tag (most reliable)
    match = re.search(
        r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"',
        html,
    )
    if match:
        pdf_path = match.group(1)
        # Resolve protocol-relative URLs
        if pdf_path.startswith("//"):
            return f"https:{pdf_path}"
        if pdf_path.startswith("/"):
            return f"{base_url.rstrip('/')}{pdf_path}"
        if not pdf_path.startswith("http"):
            return f"{base_url.rstrip('/')}/{pdf_path}"
        return pdf_path

    # Strategy 2: embed/iframe src with .pdf
    match = re.search(r'(?:src|href)="([^"]*\.pdf[^"]*)"', html)
    if match:
        pdf_path = match.group(1)
        if pdf_path.startswith("//"):
            return f"https:{pdf_path}"
        if pdf_path.startswith("/"):
            return f"{base_url.rstrip('/')}{pdf_path}"
        if not pdf_path.startswith("http"):
            return f"{base_url.rstrip('/')}/{pdf_path}"
        return pdf_path

    # Strategy 3: Look for download buttons/links with PDF URLs in onclick
    match = re.search(r'onclick="[^"]*location\.href\s*=\s*\'([^\']*\.pdf[^\']*)\'', html)
    if match:
        pdf_path = match.group(1)
        if not pdf_path.startswith("http"):
            return f"{base_url.rstrip('/')}/{pdf_path.lstrip('/')}"
        return pdf_path

    return None


def _download_pdf_from_url(pdf_url: str, out_file: str, referer: str | None = None) -> str | None:
    """Download PDF from URL. Returns None on success, error message on failure."""
    try:
        headers = {"User-Agent": _BROWSER_UA}
        if referer:
            headers["Referer"] = referer
        with httpx.Client(
            follow_redirects=True,
            timeout=30,
            headers=headers,
        ) as client:
            resp = client.get(pdf_url)
            if resp.status_code != 200:
                return f"PDF download returned {resp.status_code}"

            # Verify it looks like a PDF
            if not resp.content[:5].startswith(b"%PDF"):
                return "Downloaded content is not a valid PDF"

            Path(out_file).parent.mkdir(parents=True, exist_ok=True)
            Path(out_file).write_bytes(resp.content)
            logger.info(f"Browser fallback download succeeded: {out_file}")
            return None  # success

    except Exception as e:
        return f"PDF download failed: {e}"


def lightpanda_download(
    identifier: str,
    out_file: str,
    scihub_url: str | None = None,
    timeout_ms: int = 20000,
) -> str | None:
    """Download a paper via Lightpanda browser rendering of Sci-Hub pages.

    Uses lightpanda's fetch mode to render the page with JavaScript execution,
    then extracts the PDF URL from the rendered HTML and downloads it.

    Args:
        identifier: DOI or paper identifier.
        out_file: Path to save the downloaded PDF.
        scihub_url: Explicit Sci-Hub mirror URL (tries multiple if None).
        timeout_ms: HTTP timeout in milliseconds for lightpanda fetch.

    Returns:
        None on success, or an error message on failure.
    """
    lp_bin = _find_lightpanda()
    if lp_bin is None:
        return "Lightpanda binary not found (install to .venv/bin/lightpanda)"

    mirrors = [scihub_url] if scihub_url else BROWSER_SCIHUB_MIRRORS

    for mirror in mirrors:
        page_url = f"{mirror.rstrip('/')}/{identifier}"
        logger.info(f"Lightpanda browser fallback: {page_url}")

        try:
            result = subprocess.run(
                [
                    lp_bin,
                    "fetch",
                    "--dump", "html",
                    "--with_frames",
                    "--http_timeout", str(timeout_ms),
                    "--log_level", "error",
                    page_url,
                ],
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000 + 10,  # extra buffer over HTTP timeout
            )

            html = result.stdout
            if not html or len(html) < 200:
                logger.warning(f"Lightpanda returned empty/short HTML from {mirror}")
                continue

            # Check for DDoS-Guard / challenge pages
            if "DDoS-Guard" in html and "citation_pdf_url" not in html:
                logger.warning(f"DDoS-Guard challenge detected on {mirror}, trying next")
                continue

            # Extract PDF URL from rendered HTML
            pdf_url = _extract_pdf_url_from_html(html, mirror)
            if not pdf_url:
                logger.warning(f"No PDF URL found in Lightpanda-rendered HTML from {mirror}")
                continue

            logger.info(f"Found PDF URL via Lightpanda: {pdf_url}")

            # Rewrite the PDF URL domain to match the source mirror.
            # Sci-Hub pages often reference a different domain (e.g. sci-hub.cat)
            # that blocks external requests. The same storage path usually works
            # when accessed from the mirror we fetched from.
            import urllib.parse
            parsed_pdf = urllib.parse.urlparse(pdf_url)
            parsed_mirror = urllib.parse.urlparse(mirror)
            if parsed_pdf.netloc != parsed_mirror.netloc:
                rewritten_url = pdf_url.replace(
                    f"{parsed_pdf.scheme}://{parsed_pdf.netloc}",
                    f"{parsed_mirror.scheme}://{parsed_mirror.netloc}",
                )
                logger.info(f"Rewriting PDF URL to source mirror: {rewritten_url}")
                # Try rewritten URL first, fall back to original
                err = _download_pdf_from_url(rewritten_url, out_file, referer=page_url)
                if err:
                    logger.info(f"Rewritten URL failed, trying original: {pdf_url}")
                    err = _download_pdf_from_url(pdf_url, out_file, referer=page_url)
            else:
                err = _download_pdf_from_url(pdf_url, out_file, referer=page_url)
            if err:
                logger.warning(f"PDF download failed from {mirror}: {err}")
                continue

            return None  # success

        except subprocess.TimeoutExpired:
            logger.warning(f"Lightpanda timed out for {mirror}")
            continue
        except Exception as e:
            logger.warning(f"Lightpanda fallback failed for {mirror}: {e}")
            continue

    return "All Sci-Hub mirrors failed via Lightpanda browser fallback"
