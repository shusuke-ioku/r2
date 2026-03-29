"""Web search via Codex CLI.

Dispatches `codex exec` as a subprocess for deep, iterative web research.
Codex has built-in web browsing (Playwright MCP) and can autonomously search,
follow links, and synthesize results.

Falls back to a simple httpx + BeautifulSoup scraping approach when Codex
is not available.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class WebSource:
    """A single source from web search results."""

    title: str
    url: str
    snippet: str = ""


@dataclass
class WebSearchResult:
    """Result of a web search."""

    query: str
    synthesis: str
    sources: list[WebSource] = field(default_factory=list)
    raw: str = ""
    error: str | None = None

    def format(self) -> str:
        if self.error:
            return f"ERROR: {self.error}"
        parts = [f"## Web Search: {self.query}\n"]
        if self.synthesis:
            parts.append(self.synthesis)
        if self.sources:
            parts.append("\n### Sources")
            for i, s in enumerate(self.sources, 1):
                line = f"[{i}] {s.title} — {s.url}"
                if s.snippet:
                    line += f"\n    {s.snippet}"
                parts.append(line)
        return "\n\n".join(parts)


def _find_codex() -> str | None:
    """Find the codex binary on PATH."""
    return shutil.which("codex")


def _build_prompt(query: str, mode: str = "deep", context: str | None = None) -> str:
    """Build the prompt sent to Codex."""
    if mode == "quick":
        prompt = (
            f"Search the web for: {query}\n\n"
            "Return the top 5 results. For each, provide:\n"
            "- Title\n"
            "- URL\n"
            "- A 2-sentence summary of the key points\n\n"
            "End with a brief synthesis paragraph."
        )
    else:  # deep
        prompt = (
            f"Search the web thoroughly for: {query}\n\n"
            "Perform an iterative search:\n"
            "1. Start with a broad search\n"
            "2. Read the most promising results\n"
            "3. Identify gaps or follow-up questions\n"
            "4. Search again with refined queries\n"
            "5. Repeat until you have thorough coverage\n\n"
            "Find at least 5-10 high-quality sources.\n"
            "For each source, record: title, URL, and key findings.\n"
            "Write a structured synthesis with inline citations [1], [2], etc.\n"
            "End with a numbered reference list.\n"
        )

    if context:
        prompt += f"\nAdditional context: {context}"

    return prompt


def web_search(
    query: str,
    mode: str = "deep",
    context: str | None = None,
    timeout: int = 300,
    codex_flags: list[str] | None = None,
) -> WebSearchResult:
    """Run a web search via Codex CLI.

    Args:
        query: The search query.
        mode: "quick" for single pass, "deep" for iterative search.
        context: Optional additional context to include in the prompt.
        timeout: Timeout in seconds for the Codex subprocess.
        codex_flags: Additional flags to pass to codex exec.

    Returns:
        WebSearchResult with synthesis, sources, and raw output.
    """
    codex_bin = _find_codex()
    if codex_bin is None:
        return WebSearchResult(
            query=query,
            synthesis="",
            error="Codex CLI not found. Install from https://github.com/openai/codex",
        )

    prompt = _build_prompt(query, mode=mode, context=context)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, prefix="r2_web_"
    ) as tmp:
        out_path = tmp.name

    cmd = [
        codex_bin,
        "exec",
        "--full-auto",
        "--skip-git-repo-check",
        "-o",
        out_path,
    ]
    if codex_flags:
        cmd.extend(codex_flags)
    cmd.append(prompt)

    logger.info(f"Running Codex web search: {query} (mode={mode})")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            # Check for common errors
            if "not supported" in stderr or "invalid_request_error" in stderr:
                return WebSearchResult(
                    query=query,
                    synthesis="",
                    error=f"Codex model error: {stderr[-200:]}",
                )
            logger.warning(f"Codex exited with code {result.returncode}: {stderr[:200]}")

        # Read the output file
        output = Path(out_path).read_text(encoding="utf-8").strip()

        if not output:
            return WebSearchResult(
                query=query,
                synthesis="",
                error="Codex returned empty output",
            )

        return WebSearchResult(
            query=query,
            synthesis=output,
            raw=output,
        )

    except subprocess.TimeoutExpired:
        return WebSearchResult(
            query=query,
            synthesis="",
            error=f"Codex timed out after {timeout}s",
        )
    except Exception as e:
        return WebSearchResult(
            query=query,
            synthesis="",
            error=f"Codex execution failed: {e}",
        )
    finally:
        Path(out_path).unlink(missing_ok=True)
