"""Fetch full page content from URLs.

Three-tier approach:
1. httpx + BeautifulSoup (fast, no JS) — default
2. Playwright headless Chromium (JS rendering)
3. Lightpanda (lightweight JS fallback)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class FetchResult:
    """Result of fetching a URL."""

    url: str
    title: str = ""
    content: str = ""
    error: str | None = None

    def format(self) -> str:
        if self.error:
            return f"ERROR fetching {self.url}: {self.error}"
        parts = []
        if self.title:
            parts.append(f"# {self.title}")
        parts.append(f"Source: {self.url}\n")
        parts.append(self.content)
        return "\n".join(parts)


def _extract_text_bs4(html: str) -> tuple[str, str]:
    """Extract title and main text content from HTML using BeautifulSoup."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Try to find main content area
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main is None:
        main = soup

    text = main.get_text(separator="\n", strip=True)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text


def _fetch_httpx(url: str, timeout: int = 30) -> tuple[str, str | None]:
    """Fetch URL via httpx. Returns (html, error)."""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": _BROWSER_UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return "", f"HTTP {resp.status_code}"
            return resp.text, None
    except Exception as e:
        return "", str(e)


def _fetch_playwright(url: str, timeout: int = 30000) -> tuple[str, str | None]:
    """Fetch URL via Playwright headless Chromium. Returns (html, error)."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=_BROWSER_UA)
            page.goto(url, timeout=timeout, wait_until="networkidle")
            html = page.content()
            browser.close()
            return html, None
    except ImportError:
        return "", "Playwright not installed"
    except Exception as e:
        return "", f"Playwright error: {e}"


def _fetch_lightpanda(url: str, timeout_ms: int = 20000) -> tuple[str, str | None]:
    """Fetch URL via Lightpanda browser. Returns (html, error)."""
    import shutil
    import subprocess
    from pathlib import Path

    # Check project .venv first, then PATH
    project_root = Path(__file__).resolve().parent.parent.parent
    lp_bin = project_root / ".venv" / "bin" / "lightpanda"
    if not lp_bin.is_file():
        lp_path = shutil.which("lightpanda")
        if not lp_path:
            return "", "Lightpanda not found"
        lp_bin = Path(lp_path)

    try:
        result = subprocess.run(
            [
                str(lp_bin),
                "fetch",
                "--dump", "html",
                "--with_frames",
                "--http_timeout", str(timeout_ms),
                "--log_level", "error",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_ms / 1000 + 10,
        )
        html = result.stdout
        if not html or len(html) < 100:
            return "", "Lightpanda returned empty response"
        return html, None
    except Exception as e:
        return "", f"Lightpanda error: {e}"


def web_fetch(
    url: str,
    js: bool = False,
    max_length: int = 50000,
) -> FetchResult:
    """Fetch and extract content from a URL.

    Args:
        url: The URL to fetch.
        js: If True, use Playwright for JS rendering. Default: httpx (faster).
        max_length: Maximum content length in characters.

    Returns:
        FetchResult with extracted text content.
    """
    html = ""
    error = None

    if js:
        # Tier 1: Playwright
        html, error = _fetch_playwright(url)
        if error:
            logger.info(f"Playwright failed, trying Lightpanda: {error}")
            # Tier 2: Lightpanda fallback
            html, error = _fetch_lightpanda(url)
            if error:
                logger.info(f"Lightpanda failed, falling back to httpx: {error}")
                # Tier 3: plain httpx
                html, error = _fetch_httpx(url)
    else:
        # Tier 1: plain httpx
        html, error = _fetch_httpx(url)
        if error:
            logger.info(f"httpx failed: {error}")

    if error and not html:
        return FetchResult(url=url, error=error)

    title, content = _extract_text_bs4(html)

    if max_length and len(content) > max_length:
        content = content[:max_length] + "\n\n[... truncated ...]"

    return FetchResult(url=url, title=title, content=content)
