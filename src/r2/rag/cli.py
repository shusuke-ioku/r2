"""Click CLI for the RAG system."""

from __future__ import annotations

import json
import logging
import sys

import click

from r2.rag.config import get_config


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """RAG system for querying your Zotero library."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    # Keep our own logger at INFO for progress messages even in non-verbose mode
    if not verbose:
        logging.getLogger("rag").setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Index & stats
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--force", is_flag=True, help="Re-index already indexed papers")
@click.option("--cited-only", is_flag=True, help="Only index papers cited in the paper")
@click.option("--source", type=click.Choice(["all", "bib", "dir"]), default="all",
              help="Which source to index: bib file, PDF directory, or both (default: all)")
@click.option("--pdf-dir", default=None, help="Override PDF directory path (relative to project root)")
def index(force: bool, cited_only: bool, source: str, pdf_dir: str | None):
    """Index PDFs from bib file and/or a PDF directory into the vector store."""
    from r2.rag.ingest.pipeline import run_ingest

    config = get_config()
    if pdf_dir is not None:
        config.pdf_dir = pdf_dir
    click.echo("Starting ingestion pipeline...")

    stats = run_ingest(config=config, force=force, cited_only=cited_only, source=source)
    click.echo("\n" + stats.summary())


@cli.command()
def stats():
    """Show index statistics."""
    from r2.rag.retrieval.store import ChromaStore

    config = get_config()
    store = ChromaStore(config.resolve(config.chromadb_dir))

    total_chunks = store.count()
    citekey_stats = store.citekey_stats()

    info = {
        "total_chunks": total_chunks,
        "indexed_papers": len(citekey_stats),
        "avg_chunks_per_paper": round(total_chunks / max(len(citekey_stats), 1), 1),
        "top_papers": dict(sorted(citekey_stats.items(), key=lambda x: -x[1])[:20]),
    }
    click.echo(json.dumps(info, indent=2))


@cli.command()
@click.argument("citekey")
def remove(citekey: str):
    """Remove a paper from the index."""
    from r2.rag.retrieval.store import ChromaStore

    config = get_config()
    store = ChromaStore(config.resolve(config.chromadb_dir))

    n = store.delete_citekey(citekey)
    if n > 0:
        click.echo(f"Removed {n} chunks for {citekey}")
    else:
        click.echo(f"No chunks found for {citekey}")


# ---------------------------------------------------------------------------
# Search & retrieval
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("query")
@click.option("-n", "--n-results", default=None, type=int, help="Number of results")
@click.option("--citekey", default=None, help="Filter to a specific citekey")
def search(query: str, n_results: int | None, citekey: str | None):
    """Search the index and display matching chunks."""
    from r2.rag.retrieval.search import search as do_search

    config = get_config()
    results = do_search(
        query=query,
        n_results=n_results,
        citekey_filter=citekey,
        config=config,
    )

    if not results:
        click.echo("No results found.")
        return

    for i, r in enumerate(results, 1):
        click.echo(f"\n{'='*60}")
        click.echo(f"[{i}] {r.citation}  ({r.typst_cite})")
        click.echo(f"    Distance: {r.distance:.4f} | Section: {r.section}")
        click.echo(f"    {r.text[:300]}...")


@cli.command("query")
@click.argument("query_text")
@click.option("-n", "--n-results", default=15, type=int, help="Number of chunks to retrieve")
@click.option("--prompt", "-p", default="synthesis",
              type=click.Choice(["literature_review", "framing", "synthesis"]),
              help="Prompt template to use")
@click.option("--citekey", default=None, help="Filter to a specific citekey")
@click.option("--raw", is_flag=True, help="Output the formatted prompt without calling the LLM")
def query_cmd(query_text: str, n_results: int, prompt: str, citekey: str | None, raw: bool):
    """Query the library with RAG: retrieve chunks then format a synthesis prompt.

    By default outputs the prompt for the calling LLM. Use --raw to see the raw prompt.
    """
    from r2.rag.generation.prompts import TEMPLATES, format_context
    from r2.rag.retrieval.search import search as do_search

    config = get_config()

    click.echo("Searching...", err=True)
    results = do_search(
        query=query_text,
        n_results=n_results,
        citekey_filter=citekey,
        config=config,
    )

    if not results:
        click.echo("No results found.")
        return

    template = TEMPLATES.get(prompt)
    if template is None:
        click.echo(f"Unknown prompt type '{prompt}'. Available: {', '.join(TEMPLATES.keys())}")
        return

    context = format_context(results)
    output = template.format(query=query_text, context=context)
    click.echo(output)


@cli.command("self-query")
@click.argument("query")
@click.option("-n", "--n-results", default=20, type=int, help="Number of chunks to over-retrieve")
@click.option("--citekey", default=None, help="Filter to a specific citekey")
def self_query(query: str, n_results: int, citekey: str | None):
    """Over-retrieve chunks and return a Self-RAG prompt for LLM grading."""
    from r2.rag.generation.prompts import SELF_RAG_SYNTHESIS, format_context
    from r2.rag.retrieval.search import search as do_search

    config = get_config()
    results = do_search(query=query, n_results=n_results, citekey_filter=citekey, config=config)

    if not results:
        click.echo("No results found.")
        return

    context = format_context(results)
    click.echo(SELF_RAG_SYNTHESIS.format(n_chunks=len(results), query=query, context=context))


@cli.command("deep-query")
@click.argument("query")
@click.option("--sub-questions", "-s", default=None, help="JSON array of sub-questions")
@click.option("-n", "--n-per-query", default=8, type=int, help="Chunks per sub-question")
@click.option("--citekey", default=None, help="Filter to a specific citekey")
def deep_query(query: str, sub_questions: str | None, n_per_query: int, citekey: str | None):
    """DeepRAG: decompose complex queries into sub-questions with iterative retrieval.

    Call without --sub-questions to get decomposition instructions.
    Call with --sub-questions '["q1", "q2", ...]' to retrieve and synthesize.
    """
    from r2.rag.generation.prompts import DECOMPOSITION_INSTRUCTIONS, DEEP_RAG_SYNTHESIS, format_context
    from r2.rag.retrieval.search import SearchResult, search as do_search

    if not sub_questions:
        click.echo(DECOMPOSITION_INSTRUCTIONS.format(query=query))
        return

    sqs = json.loads(sub_questions)
    config = get_config()
    all_results: list[SearchResult] = []
    for sq in sqs:
        results = do_search(query=sq, n_results=n_per_query, citekey_filter=citekey, config=config)
        all_results.extend(results)

    if not all_results:
        click.echo("No results found for any sub-question.")
        return

    # Deduplicate
    seen: dict[str, SearchResult] = {}
    for r in all_results:
        key = f"{r.citekey}__{r.chunk_idx}"
        if key not in seen or r.distance < seen[key].distance:
            seen[key] = r
    unique = sorted(seen.values(), key=lambda r: r.distance)

    context = format_context(unique)
    sub_q_str = "\n".join(f"  {i}. {sq}" for i, sq in enumerate(sqs, 1))

    click.echo(DEEP_RAG_SYNTHESIS.format(
        query=query, sub_questions=sub_q_str,
        n_total=len(all_results), n_unique=len(unique), context=context,
    ))


# ---------------------------------------------------------------------------
# Literature search (external APIs)
# ---------------------------------------------------------------------------

def _get_s2_client():
    from r2.rag.semantic_scholar.client import SemanticScholarClient
    config = get_config()
    return SemanticScholarClient(
        api_key=config.semantic_scholar_api_key,
        base_url=config.semantic_scholar_base_url,
        rate_limit=config.semantic_scholar_rate_limit,
    )


def _get_oa_client():
    from r2.rag.openalex.client import OpenAlexClient
    config = get_config()
    return OpenAlexClient(
        api_key=config.openalex_api_key,
        base_url=config.openalex_base_url,
        rate_limit=config.openalex_rate_limit,
    )


def _get_scopus_client():
    from r2.rag.scopus.client import ScopusClient
    config = get_config()
    return ScopusClient(
        api_key=config.scopus_api_key,
        base_url=config.scopus_base_url,
        rate_limit=config.scopus_rate_limit,
    )


def _dedupe_papers(papers):
    from r2.rag.semantic_scholar.types import S2Paper
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


def _format_s2_papers(papers, include_abstract=True):
    if not papers:
        return "No papers found."
    parts = []
    for i, p in enumerate(papers, 1):
        parts.append(f"[{i}] {p.format_detail() if include_abstract else p.format_short()}")
    return "\n\n---\n\n".join(parts)


def _format_s2_context(papers):
    parts = []
    for i, p in enumerate(papers, 1):
        header = f"[E{i}] {p.author_str} ({p.year or 'n.d.'}). {p.title}"
        if p.venue:
            header += f". {p.venue}"
        header += f" [{p.citation_count} citations]"
        body = f"Abstract: {p.abstract}" if p.abstract else "(abstract unavailable — do not cite)"
        parts.append(f"{header}\n{body}")
    return "\n\n---\n\n".join(parts)


@cli.command("lit-search")
@click.argument("query")
@click.option("--focus", default="broad", type=click.Choice(["broad", "top_journals", "classical", "recent"]))
@click.option("-n", "--n-results", default=20, type=int)
@click.option("--year", default=None, help="Year range (e.g. '2020-2025')")
@click.option("--min-citations", default=None, type=int)
@click.option("--source", default="all", help="APIs: all, s2, oa, scopus, or comma-separated")
def lit_search(query: str, focus: str, n_results: int, year: str | None, min_citations: int | None, source: str):
    """Search Semantic Scholar, OpenAlex, and Scopus for papers."""
    from r2.rag.semantic_scholar.focus import FOCUS_MODES

    all_papers = []
    sources_used = []
    active = {s.strip() for s in source.split(",")} if "," in source else {source}
    use_all = "all" in active

    if use_all or "s2" in active:
        s2 = _get_s2_client()
        try:
            papers = s2.search(query=query, n_results=n_results, focus=focus, year=year, min_citations=min_citations)
            all_papers.extend(papers)
            sources_used.append(f"S2: {len(papers)}")
        except Exception as e:
            sources_used.append(f"S2: error ({e})")
        finally:
            s2.close()

    if use_all or "oa" in active:
        oa = _get_oa_client()
        try:
            papers = oa.search(query=query, n_results=n_results, focus=focus, year=year, min_citations=min_citations)
            all_papers.extend(papers)
            sources_used.append(f"OA: {len(papers)}")
        except Exception as e:
            sources_used.append(f"OA: error ({e})")
        finally:
            oa.close()

    if use_all or "scopus" in active:
        sc = _get_scopus_client()
        try:
            papers = sc.search(query=query, n_results=n_results, focus=focus, year=year, min_citations=min_citations)
            all_papers.extend(papers)
            sources_used.append(f"Scopus: {len(papers)}")
        except Exception as e:
            sources_used.append(f"Scopus: error ({e})")
        finally:
            sc.close()

    papers = _dedupe_papers(all_papers)[:n_results]

    if not papers:
        focus_info = FOCUS_MODES.get(focus)
        hint = f" (focus={focus}: {focus_info.description})" if focus_info else ""
        click.echo(f"No papers found for '{query}'{hint}. Try a broader query or focus='broad'.")
        return

    header = f"Found {len(papers)} papers [{', '.join(sources_used)}]"
    if focus != "broad":
        focus_info = FOCUS_MODES[focus]
        header += f" (focus={focus}: {focus_info.description})"
    click.echo(header + ":\n")
    click.echo(_format_s2_papers(papers, include_abstract=True))


@cli.command("lit-paper")
@click.argument("paper_id")
def lit_paper(paper_id: str):
    """Get detailed info about a paper from Semantic Scholar.

    PAPER_ID: Semantic Scholar ID, DOI (prefix with "DOI:"), ArXiv ("ARXIV:..."), or ACL ("ACL:...")
    """
    client = _get_s2_client()
    try:
        paper = client.get_paper(paper_id)
    finally:
        client.close()
    click.echo(paper.format_detail())


@cli.command("lit-citations")
@click.argument("paper_id")
@click.option("-n", "--n-results", default=10, type=int)
def lit_citations(paper_id: str, n_results: int):
    """Get papers that cite a given paper (forward citations)."""
    client = _get_s2_client()
    try:
        papers = client.get_citations(paper_id, n_results=n_results)
    finally:
        client.close()
    if not papers:
        click.echo("No citations found.")
        return
    click.echo(f"Papers citing this work ({len(papers)} results):\n")
    click.echo(_format_s2_papers(papers, include_abstract=True))


@cli.command("lit-references")
@click.argument("paper_id")
@click.option("-n", "--n-results", default=10, type=int)
def lit_references(paper_id: str, n_results: int):
    """Get papers referenced by a given paper (backward citations)."""
    client = _get_s2_client()
    try:
        papers = client.get_references(paper_id, n_results=n_results)
    finally:
        client.close()
    if not papers:
        click.echo("No references found.")
        return
    click.echo(f"References from this paper ({len(papers)} results):\n")
    click.echo(_format_s2_papers(papers, include_abstract=True))


@cli.command("lit-deep-research")
@click.argument("query")
@click.option("--focus", default="broad", type=click.Choice(["broad", "top_journals", "classical", "recent"]))
@click.option("--n-external", default=20, type=int)
@click.option("--n-local", default=15, type=int)
@click.option("--year", default=None, help="Year range (e.g. '2020-2025')")
@click.option("--min-citations", default=None, type=int)
def lit_deep_research(query: str, focus: str, n_external: int, n_local: int, year: str | None, min_citations: int | None):
    """Combined deep research: local Zotero RAG + external APIs."""
    from datetime import date
    from r2.rag.generation.prompts import LIT_DEEP_RESEARCH, LIT_DEEP_RESEARCH_EXTERNAL_ONLY, format_context
    from r2.rag.retrieval.search import search as do_search
    from r2.rag.semantic_scholar.focus import FOCUS_MODES

    config = get_config()
    local_results = do_search(query=query, n_results=n_local, config=config)

    all_external = []
    sources_used = []

    for name, get_client in [("S2", _get_s2_client), ("OA", _get_oa_client), ("Scopus", _get_scopus_client)]:
        client = get_client()
        try:
            papers = client.search(query=query, n_results=n_external, focus=focus, year=year, min_citations=min_citations)
            all_external.extend(papers)
            sources_used.append(f"{name}: {len(papers)}")
        except Exception as e:
            sources_used.append(f"{name}: error ({e})")
        finally:
            client.close()

    external_papers = _dedupe_papers(all_external)[:n_external]

    if local_results:
        local_context = format_context(local_results)
        external_context = _format_s2_context(external_papers) if external_papers else "(No external papers found.)"
        result = LIT_DEEP_RESEARCH.format(query=query, local_context=local_context, external_context=external_context)
    elif external_papers:
        external_context = _format_s2_context(external_papers)
        result = LIT_DEEP_RESEARCH_EXTERNAL_ONLY.format(query=query, external_context=external_context)
    else:
        click.echo("No results found in local library, Semantic Scholar, OpenAlex, or Scopus.")
        return

    focus_info = FOCUS_MODES.get(focus, FOCUS_MODES["broad"])
    footer = (
        f"\n\n---\n"
        f"*Deep research — {date.today().isoformat()}*\n"
        f"*Local chunks: {len(local_results)} | External papers: {len(external_papers)} [{', '.join(sources_used)}]*\n"
        f"*Focus: {focus} ({focus_info.description})*\n"
    )
    click.echo(result + footer)


# ---------------------------------------------------------------------------
# Download & save
# ---------------------------------------------------------------------------

@cli.command("lit-download")
@click.argument("identifier")
@click.option("--type", "paper_type", default=None, help="doi, pmid, or title (auto-detected)")
@click.option("--filename", default=None, help="Custom filename without .pdf")
@click.option("--title", default=None, help="Paper title for Zotero metadata")
@click.option("--no-index", is_flag=True, help="Skip auto-indexing into RAG")
def lit_download(identifier: str, paper_type: str | None, filename: str | None, title: str | None, no_index: bool):
    """Download a paper via Sci-Hub, add to Zotero, and index into RAG."""
    from r2.rag.download import download_paper

    config = get_config()
    out_dir = config.resolve(config.download_dir)
    scihub_url = config.scihub_url or None
    proxies = {"http": config.download_proxy, "https": config.download_proxy} if config.download_proxy else None

    result = download_paper(
        identifier=identifier, paper_type=paper_type, out_dir=out_dir,
        filename=filename, scihub_url=scihub_url, proxies=proxies,
        zotero_library_id=config.zotero_library_id or None,
        zotero_api_key=config.zotero_api_key or None, title=title,
    )

    if result.success and not no_index:
        from r2.rag.ingest.pipeline import run_ingest
        # Point pdf_dir at download_dir so the dir source finds the downloaded PDF
        config.pdf_dir = config.download_dir
        stats = run_ingest(config=config, force=False, source="dir")
        click.echo(f"{result.format()}\n\nAuto-indexed: {stats.summary()}")
    else:
        click.echo(result.format())


@cli.command("lit-download-batch")
@click.argument("papers_json")
@click.option("--auto-index", is_flag=True, help="Index all downloaded PDFs into RAG after download")
def lit_download_batch(papers_json: str, auto_index: bool):
    """Download multiple papers via Sci-Hub in batch.

    PAPERS_JSON: JSON array of objects with "id" (required), "type", "filename", "title" keys.
    Example: '[{"id": "10.1017/S0003055420000933", "filename": "acemoglu_2020"}]'
    """
    from r2.rag.download import download_batch

    papers = json.loads(papers_json)
    config = get_config()
    out_dir = config.resolve(config.download_dir)
    scihub_url = config.scihub_url or None
    proxies = {"http": config.download_proxy, "https": config.download_proxy} if config.download_proxy else None

    results = download_batch(
        identifiers=papers, out_dir=out_dir, scihub_url=scihub_url, proxies=proxies,
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
        # Point pdf_dir at download_dir so the dir source finds downloaded PDFs
        config.pdf_dir = config.download_dir
        stats = run_ingest(config=config, force=False, source="dir")
        lines.append(f"\nAuto-indexed: {stats.summary()}")

    if failed:
        lines.append(f"\n{len(failed)} failed — check DOIs or try with explicit --type.")

    click.echo("\n".join(lines))


@cli.command("lit-save-report")
@click.argument("query")
@click.option("--file", "input_file", default="-", type=click.File("r"), help="Report content file (default: stdin)")
def lit_save_report(query: str, input_file):
    """Save a literature review report to notes/lit/YYYY-MM-DD_short-title.md.

    Reads report content from stdin or a file.
    """
    import re
    from datetime import date

    config = get_config()
    lit_dir = config.project_root / "notes" / "lit"
    lit_dir.mkdir(exist_ok=True)

    text = query.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    slug = "-".join(text.split()[:5])
    today = date.today().isoformat()
    filename = f"{today}_{slug}.md"
    filepath = lit_dir / filename

    content = input_file.read()
    filepath.write_text(content, encoding="utf-8")
    click.echo(f"Report saved to: {filepath}")
