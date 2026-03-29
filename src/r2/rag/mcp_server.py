"""MCP server wrapping RAG search, query, and index status."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from r2.rag.config import get_config
from r2.rag.generation.prompts import (
    DECOMPOSITION_INSTRUCTIONS,
    DEEP_RAG_SYNTHESIS,
    LIT_DEEP_RESEARCH,
    LIT_DEEP_RESEARCH_EXTERNAL_ONLY,
    SELF_RAG_SYNTHESIS,
    TEMPLATES,
    format_context,
)
from r2.rag.retrieval.search import SearchResult, search as do_search
from r2.rag.retrieval.store import ChromaStore
from r2.rag.openalex.client import OpenAlexClient
from r2.rag.scopus.client import ScopusClient
from r2.rag.semantic_scholar.client import SemanticScholarClient
from r2.rag.semantic_scholar.focus import FOCUS_MODES
from r2.rag.semantic_scholar.types import S2Paper

mcp = FastMCP("rag", instructions="Search and query your Zotero library via RAG")


@mcp.tool()
def rag_search(query: str, n_results: int = 10, citekey: str | None = None) -> str:
    """Search the indexed Zotero library for relevant paper chunks.

    Args:
        query: Semantic search query (e.g. "ideology and mobilization")
        n_results: Number of results to return (default 10)
        citekey: Optional citekey to restrict search to a single paper
    """
    config = get_config()
    results = do_search(
        query=query,
        n_results=n_results,
        citekey_filter=citekey,
        config=config,
    )

    if not results:
        return "No results found."

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.citation} ({r.typst_cite})\n"
            f"Section: {r.section} | Distance: {r.distance:.4f}\n"
            f"{r.text}\n"
        )
    return "\n---\n".join(parts)


@mcp.tool()
def rag_query(
    query: str,
    prompt_type: str = "synthesis",
    n_results: int = 15,
    citekey: str | None = None,
) -> str:
    """Retrieve relevant paper chunks and return a formatted prompt for the calling LLM to synthesize.

    No separate API call is made -- the calling LLM (Claude Code / Codex) does the generation directly,
    saving API costs.

    Args:
        query: Research question (e.g. "how do papers frame ideology vs material conditions")
        prompt_type: Template - "literature_review", "framing", or "synthesis"
        n_results: Number of chunks to retrieve for context (default 15)
        citekey: Optional citekey to restrict to a single paper
    """
    config = get_config()
    results = do_search(
        query=query,
        n_results=n_results,
        citekey_filter=citekey,
        config=config,
    )

    if not results:
        return "No results found in the index."

    template = TEMPLATES.get(prompt_type)
    if template is None:
        available = ", ".join(TEMPLATES.keys())
        return f"Unknown prompt type '{prompt_type}'. Available: {available}"

    context = format_context(results)
    return template.format(query=query, context=context)


def _deduplicate(all_results: list[SearchResult]) -> list[SearchResult]:
    """Deduplicate by citekey+chunk_idx, keeping the result with smallest distance."""
    seen: dict[str, SearchResult] = {}
    for r in all_results:
        key = f"{r.citekey}__{r.chunk_idx}"
        if key not in seen or r.distance < seen[key].distance:
            seen[key] = r
    return sorted(seen.values(), key=lambda r: r.distance)


@mcp.tool()
def rag_self_query(
    query: str,
    n_results: int = 20,
    citekey: str | None = None,
) -> str:
    """Over-retrieve chunks and return a Self-RAG prompt for the calling LLM to grade and filter.

    Returns more chunks than standard search along with instructions for the calling LLM
    to assess relevance (RELEVANT/PARTIAL/IRRELEVANT), discard noise, and synthesize
    with confidence annotations (HIGH/MEDIUM/LOW).

    Args:
        query: Research question (e.g. "how did economic shocks affect right-wing organizing")
        n_results: Number of chunks to over-retrieve for filtering (default 20)
        citekey: Optional citekey to restrict to a single paper
    """
    config = get_config()
    results = do_search(
        query=query,
        n_results=n_results,
        citekey_filter=citekey,
        config=config,
    )

    if not results:
        return "No results found."

    context = format_context(results)
    return SELF_RAG_SYNTHESIS.format(
        n_chunks=len(results),
        query=query,
        context=context,
    )


@mcp.tool()
def rag_deep_query(
    query: str,
    sub_questions: list[str] | None = None,
    n_per_query: int = 8,
    citekey: str | None = None,
) -> str:
    """DeepRAG: decompose complex queries into sub-questions with iterative retrieval.

    Call without sub_questions to get decomposition instructions.
    Call with sub_questions to retrieve for each and get a synthesis prompt.

    Args:
        query: Original research question
        sub_questions: List of 3-5 atomic sub-questions (omit for decomposition instructions)
        n_per_query: Chunks to retrieve per sub-question (default 8)
        citekey: Optional citekey to restrict to a single paper
    """
    if not sub_questions:
        return DECOMPOSITION_INSTRUCTIONS.format(query=query)

    config = get_config()
    all_results: list[SearchResult] = []
    for sq in sub_questions:
        results = do_search(
            query=sq,
            n_results=n_per_query,
            citekey_filter=citekey,
            config=config,
        )
        all_results.extend(results)

    if not all_results:
        return "No results found for any sub-question."

    unique = _deduplicate(all_results)
    context = format_context(unique)
    sub_q_str = "\n".join(f"  {i}. {sq}" for i, sq in enumerate(sub_questions, 1))

    return DEEP_RAG_SYNTHESIS.format(
        query=query,
        sub_questions=sub_q_str,
        n_total=len(all_results),
        n_unique=len(unique),
        context=context,
    )


@mcp.tool()
def rag_index(source: str = "all", force: bool = False) -> str:
    """Index PDFs into the vector store.

    Args:
        source: Which source to index -- "bib" (from corpus.bib), "dir" (from pdf_dir folder), or "all" (both)
        force: Re-index already indexed papers (default False)
    """
    from r2.rag.ingest.pipeline import run_ingest

    config = get_config()
    stats = run_ingest(config=config, force=force, source=source)
    return stats.summary()


@mcp.tool()
def rag_index_status() -> str:
    """Show statistics about the current RAG index."""
    config = get_config()
    store = ChromaStore(config.resolve(config.chromadb_dir))

    total_chunks = store.count()
    citekey_stats = store.citekey_stats()

    info = {
        "total_chunks": total_chunks,
        "indexed_papers": len(citekey_stats),
        "avg_chunks_per_paper": round(total_chunks / max(len(citekey_stats), 1), 1),
        "top_papers": dict(sorted(citekey_stats.items(), key=lambda x: -x[1])[:10]),
    }
    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# Semantic Scholar helpers
# ---------------------------------------------------------------------------

def _get_s2_client() -> SemanticScholarClient:
    """Create a Semantic Scholar client from config."""
    config = get_config()
    return SemanticScholarClient(
        api_key=config.semantic_scholar_api_key,
        base_url=config.semantic_scholar_base_url,
        rate_limit=config.semantic_scholar_rate_limit,
    )


def _get_oa_client() -> OpenAlexClient:
    """Create an OpenAlex client from config."""
    config = get_config()
    return OpenAlexClient(
        api_key=config.openalex_api_key,
        base_url=config.openalex_base_url,
        rate_limit=config.openalex_rate_limit,
    )


def _get_scopus_client() -> ScopusClient:
    """Create a Scopus client from config."""
    config = get_config()
    return ScopusClient(
        api_key=config.scopus_api_key,
        base_url=config.scopus_base_url,
        rate_limit=config.scopus_rate_limit,
    )


def _dedupe_papers(papers: list[S2Paper]) -> list[S2Paper]:
    """Deduplicate papers by DOI (preferred) or title similarity."""
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[S2Paper] = []
    for p in papers:
        doi = (p.external_ids.get("DOI") or "").lower().strip()
        title_key = p.title.lower().strip()
        if doi and doi in seen_dois:
            continue
        if title_key in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        seen_titles.add(title_key)
        unique.append(p)
    return unique


def _format_s2_papers(papers: list[S2Paper], include_abstract: bool = True) -> str:
    """Format a list of S2 papers for display."""
    if not papers:
        return "No papers found."
    parts = []
    for i, p in enumerate(papers, 1):
        if include_abstract:
            parts.append(f"[{i}] {p.format_detail()}")
        else:
            parts.append(f"[{i}] {p.format_short()}")
    return "\n\n---\n\n".join(parts)


def _format_s2_context(papers: list[S2Paper]) -> str:
    """Format S2 papers as context for deep research prompts."""
    parts = []
    for i, p in enumerate(papers, 1):
        header = f"[E{i}] {p.author_str} ({p.year or 'n.d.'}). {p.title}"
        if p.venue:
            header += f". {p.venue}"
        header += f" [{p.citation_count} citations]"
        if p.abstract:
            body = f"Abstract: {p.abstract}"
        else:
            body = "(abstract unavailable — do not cite)"
        parts.append(f"{header}\n{body}")
    return "\n\n---\n\n".join(parts)


def _slugify(text: str, max_words: int = 5) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    words = text.split()[:max_words]
    return "-".join(words)


def _save_report(query: str, content: str, config=None) -> str:
    """Save a deep research report to lit/ directory. Returns the file path."""
    if config is None:
        config = get_config()
    lit_dir = config.project_root / "notes" / "lit"
    lit_dir.mkdir(exist_ok=True)

    slug = _slugify(query)
    today = date.today().isoformat()
    filename = f"{today}_{slug}.md"
    filepath = lit_dir / filename

    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


# ---------------------------------------------------------------------------
# Semantic Scholar MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def lit_search(
    query: str,
    focus: str = "broad",
    n_results: int = 20,
    year: str | None = None,
    min_citations: int | None = None,
    source: str = "all",
) -> str:
    """Search Semantic Scholar, OpenAlex, and Scopus for papers. Returns full abstracts for thorough survey.

    Args:
        query: Search query (e.g. "trade shocks political extremism")
        focus: Focus mode — "broad" (default), "top_journals", "classical", "recent"
        n_results: Number of results to return (default 20)
        year: Year range filter (e.g. "2020-2025" or "2020-")
        min_citations: Minimum citation count (overrides focus default)
        source: Which API(s) to search — "all" (default), "s2", "oa", "scopus", or comma-separated (e.g. "s2,oa")
    """
    all_papers: list[S2Paper] = []
    sources_used: list[str] = []
    active = {s.strip() for s in source.split(",")} if "," in source else {source}
    use_all = "all" in active or "both" in active

    # Semantic Scholar
    if use_all or "s2" in active:
        s2 = _get_s2_client()
        try:
            s2_papers = s2.search(
                query=query,
                n_results=n_results,
                focus=focus,
                year=year,
                min_citations=min_citations,
            )
            all_papers.extend(s2_papers)
            sources_used.append(f"S2: {len(s2_papers)}")
        except Exception as e:
            sources_used.append(f"S2: error ({e})")
        finally:
            s2.close()

    # OpenAlex
    if use_all or "oa" in active:
        oa = _get_oa_client()
        try:
            oa_papers = oa.search(
                query=query,
                n_results=n_results,
                focus=focus,
                year=year,
                min_citations=min_citations,
            )
            all_papers.extend(oa_papers)
            sources_used.append(f"OA: {len(oa_papers)}")
        except Exception as e:
            sources_used.append(f"OA: error ({e})")
        finally:
            oa.close()

    # Scopus
    if use_all or "scopus" in active:
        sc = _get_scopus_client()
        try:
            sc_papers = sc.search(
                query=query,
                n_results=n_results,
                focus=focus,
                year=year,
                min_citations=min_citations,
            )
            all_papers.extend(sc_papers)
            sources_used.append(f"Scopus: {len(sc_papers)}")
        except Exception as e:
            sources_used.append(f"Scopus: error ({e})")
        finally:
            sc.close()

    # Deduplicate and limit
    papers = _dedupe_papers(all_papers)[:n_results]

    if not papers:
        focus_info = FOCUS_MODES.get(focus)
        hint = f" (focus={focus}: {focus_info.description})" if focus_info else ""
        return f"No papers found for '{query}'{hint}. Try a broader query or focus='broad'."

    header = f"Found {len(papers)} papers [{', '.join(sources_used)}]"
    if focus != "broad":
        focus_info = FOCUS_MODES[focus]
        header += f" (focus={focus}: {focus_info.description})"
    header += ":\n\n"

    return header + _format_s2_papers(papers, include_abstract=True)


@mcp.tool()
def lit_paper(paper_id: str) -> str:
    """Get detailed information about a specific paper from Semantic Scholar.

    Args:
        paper_id: Semantic Scholar paper ID, DOI (prefix with "DOI:"),
                  ArXiv ID ("ARXIV:..."), or ACL ID ("ACL:...")
    """
    client = _get_s2_client()
    try:
        paper = client.get_paper(paper_id)
    finally:
        client.close()

    return paper.format_detail()


@mcp.tool()
def lit_citations(paper_id: str, n_results: int = 10) -> str:
    """Get papers that cite a given paper (forward citations).

    Args:
        paper_id: Semantic Scholar paper ID or other identifier
        n_results: Number of citing papers to return (default 10)
    """
    client = _get_s2_client()
    try:
        papers = client.get_citations(paper_id, n_results=n_results)
    finally:
        client.close()

    if not papers:
        return "No citations found."

    return f"Papers citing this work ({len(papers)} results):\n\n" + _format_s2_papers(
        papers, include_abstract=True
    )


@mcp.tool()
def lit_references(paper_id: str, n_results: int = 10) -> str:
    """Get papers referenced by a given paper (backward citations / bibliography).

    Args:
        paper_id: Semantic Scholar paper ID or other identifier
        n_results: Number of referenced papers to return (default 10)
    """
    client = _get_s2_client()
    try:
        papers = client.get_references(paper_id, n_results=n_results)
    finally:
        client.close()

    if not papers:
        return "No references found."

    return f"References from this paper ({len(papers)} results):\n\n" + _format_s2_papers(
        papers, include_abstract=True
    )


@mcp.tool()
def lit_deep_research(
    query: str,
    focus: str = "broad",
    n_external: int = 20,
    n_local: int = 15,
    year: str | None = None,
    min_citations: int | None = None,
) -> str:
    """Combined deep research: local Zotero RAG + Semantic Scholar + OpenAlex + Scopus.

    Retrieves full-text evidence from indexed papers AND abstracts from the broader
    literature (Semantic Scholar, OpenAlex, and Scopus), then returns a synthesis
    prompt for the LLM to produce a thorough literature survey.

    IMPORTANT: After you synthesize the results, call lit_save_report to save the
    completed report to library/lit/YYYY-MM-DD_short-title.md.

    Args:
        query: Research question (e.g. "How do trade shocks affect political extremism?")
        focus: Focus mode for external search — "broad", "top_journals", "classical", "recent"
        n_external: Number of external papers to return after dedup (default 20)
        n_local: Number of local chunks from Zotero RAG (default 15)
        year: Year range for external search (e.g. "2020-2025")
        min_citations: Minimum citation count for external papers
    """
    config = get_config()

    # Local RAG search
    local_results = do_search(query=query, n_results=n_local, config=config)

    # External search from all sources
    all_external: list[S2Paper] = []
    sources_used: list[str] = []

    # Semantic Scholar
    s2 = _get_s2_client()
    try:
        s2_papers = s2.search(
            query=query,
            n_results=n_external,
            focus=focus,
            year=year,
            min_citations=min_citations,
        )
        all_external.extend(s2_papers)
        sources_used.append(f"S2: {len(s2_papers)}")
    except Exception as e:
        sources_used.append(f"S2: error ({e})")
    finally:
        s2.close()

    # OpenAlex
    oa = _get_oa_client()
    try:
        oa_papers = oa.search(
            query=query,
            n_results=n_external,
            focus=focus,
            year=year,
            min_citations=min_citations,
        )
        all_external.extend(oa_papers)
        sources_used.append(f"OA: {len(oa_papers)}")
    except Exception as e:
        sources_used.append(f"OA: error ({e})")
    finally:
        oa.close()

    # Scopus
    sc = _get_scopus_client()
    try:
        sc_papers = sc.search(
            query=query,
            n_results=n_external,
            focus=focus,
            year=year,
            min_citations=min_citations,
        )
        all_external.extend(sc_papers)
        sources_used.append(f"Scopus: {len(sc_papers)}")
    except Exception as e:
        sources_used.append(f"Scopus: error ({e})")
    finally:
        sc.close()

    external_papers = _dedupe_papers(all_external)[:n_external]

    # Build the prompt
    if local_results:
        local_context = format_context(local_results)
        external_context = _format_s2_context(external_papers) if external_papers else "(No external papers found.)"
        result = LIT_DEEP_RESEARCH.format(
            query=query,
            local_context=local_context,
            external_context=external_context,
        )
    elif external_papers:
        external_context = _format_s2_context(external_papers)
        result = LIT_DEEP_RESEARCH_EXTERNAL_ONLY.format(
            query=query,
            external_context=external_context,
        )
    else:
        return "No results found in local library, Semantic Scholar, OpenAlex, or Scopus."

    # Metadata footer
    focus_info = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])
    footer = (
        f"\n\n---\n"
        f"*Deep research — {date.today().isoformat()}*\n"
        f"*Local chunks: {len(local_results)} | External papers: {len(external_papers)} [{', '.join(sources_used)}]*\n"
        f"*Focus: {focus} ({focus_info.description})*\n"
        f"\n**After synthesizing, call `lit_save_report` with your completed report.**\n"
    )

    return result + footer


@mcp.tool()
def lit_download(
    identifier: str,
    paper_type: str | None = None,
    filename: str | None = None,
    title: str | None = None,
    auto_index: bool = True,
) -> str:
    """Download a paper, add to Zotero, and index into RAG — all in one step.

    This is the single tool for acquiring a new paper. One call does everything:
      1. Downloads the PDF via Sci-Hub
      2. Adds the item to Zotero with full metadata (resolved via CrossRef for DOIs)
         and attaches the PDF
      3. Indexes the PDF into the RAG vector store for full-text search

    Args:
        identifier: DOI (e.g. "10.1017/S0003055420000933"), PMID, or paper title.
                    Auto-detects the type if paper_type is not specified.
        paper_type: "doi", "pmid", or "title". Auto-detected from identifier if omitted.
        filename: Custom filename (without .pdf). Auto-generated from identifier if omitted.
        title: Paper title (helps Zotero metadata when DOI lookup fails).
        auto_index: Index the PDF into RAG after download (default True).
    """
    from r2.rag.download import download_paper

    config = get_config()
    out_dir = config.resolve(config.download_dir)
    scihub_url = config.scihub_url or None
    proxies = {"http": config.download_proxy, "https": config.download_proxy} if config.download_proxy else None

    result = download_paper(
        identifier=identifier,
        paper_type=paper_type,
        out_dir=out_dir,
        filename=filename,
        scihub_url=scihub_url,
        proxies=proxies,
        zotero_library_id=config.zotero_library_id or None,
        zotero_api_key=config.zotero_api_key or None,
        title=title,
    )

    if result.success and auto_index:
        from r2.rag.ingest.pipeline import run_ingest

        stats = run_ingest(config=config, force=False, source="dir")
        return f"{result.format()}\n\nAuto-indexed: {stats.summary()}"

    return result.format()


@mcp.tool()
def lit_download_batch(
    papers: list[dict],
    auto_index: bool = False,
) -> str:
    """Download multiple papers via Sci-Hub in batch, adding each to Zotero.

    Use this after a deep research report to download papers from the
    "Papers to Index" table. Each entry needs at minimum an "id" field.
    Every successfully downloaded paper is automatically added to Zotero
    with metadata and the PDF attached.

    Args:
        papers: List of paper dicts. Each dict should have:
                - "id" (required): DOI, PMID, or title
                - "type" (optional): "doi", "pmid", or "title" (auto-detected if omitted)
                - "filename" (optional): custom filename without .pdf extension
                - "title" (optional): paper title for Zotero metadata
                Example: [{"id": "10.1017/S0003055420000933", "filename": "acemoglu_2020"}]
        auto_index: If True, index all successfully downloaded PDFs into RAG after downloads.
    """
    from r2.rag.download import download_batch

    config = get_config()
    out_dir = config.resolve(config.download_dir)
    scihub_url = config.scihub_url or None
    proxies = {"http": config.download_proxy, "https": config.download_proxy} if config.download_proxy else None

    results = download_batch(
        identifiers=papers,
        out_dir=out_dir,
        scihub_url=scihub_url,
        proxies=proxies,
        zotero_library_id=config.zotero_library_id or None,
        zotero_api_key=config.zotero_api_key or None,
    )

    succeeded = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    lines = [f"Downloaded {len(succeeded)}/{len(results)} papers:"]
    for r in results:
        lines.append(f"  {r.format()}")

    if succeeded and auto_index:
        from r2.rag.ingest.pipeline import run_ingest

        stats = run_ingest(config=config, force=False, source="dir")
        lines.append(f"\nAuto-indexed: {stats.summary()}")

    if failed:
        lines.append(f"\n{len(failed)} failed — check DOIs or try with explicit paper_type.")

    return "\n".join(lines)


@mcp.tool()
def lit_save_report(query: str, report: str) -> str:
    """Save a completed literature review report to lit/YYYY-MM-DD_short-title.md.

    Call this after you have synthesized the results from lit_deep_research (or any
    other literature review tool) into a finished report.

    Args:
        query: The original research query (used to generate the filename slug)
        report: The completed report content (markdown)
    """
    saved_path = _save_report(query, report)
    return f"Report saved to: {saved_path}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
