"""Orchestrate ingestion: bib -> PDFs -> chunks -> ChromaDB."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from r2.rag.config import RAGConfig, get_config
from r2.rag.ingest.bib import BibEntry, parse_bib
from r2.rag.ingest.chunker import Chunk, chunk_document
from r2.rag.ingest.pdf import extract_pdf
from r2.rag.retrieval.embedder import Embedder
from r2.rag.retrieval.store import ChromaStore

logger = logging.getLogger(__name__)


@dataclass
class IngestStats:
    total: int = 0
    indexed: int = 0
    skipped_exists: int = 0
    skipped_no_pdf: int = 0
    skipped_excluded: int = 0
    removed_excluded: int = 0
    failed: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Total entries:    {self.total}",
            f"Indexed:          {self.indexed}",
            f"Skipped (exists): {self.skipped_exists}",
            f"Skipped (no PDF): {self.skipped_no_pdf}",
            f"Skipped (excluded):{self.skipped_excluded}",
            f"Removed (excluded):{self.removed_excluded}",
            f"Failed:           {self.failed}",
        ]
        if self.errors:
            lines.append("Errors:")
            for citekey, msg in self.errors:
                lines.append(f"  {citekey}: {msg}")
        return "\n".join(lines)


def _get_cited_keys(paper_path: Path) -> set[str]:
    """Parse Typst file for @citekey patterns."""
    if not paper_path.exists():
        logger.warning("Paper file not found: %s", paper_path)
        return set()

    text = paper_path.read_text(encoding="utf-8")
    # Typst citations: @citekey or @citekey[...] — capture the citekey part
    keys = set(re.findall(r"@([a-zA-Z0-9_:.-]+)", text))
    return keys


def _parse_pdf_filename(stem: str) -> tuple[str, str, str]:
    """Best-effort metadata extraction from a PDF filename.

    Tries patterns like 'Author2020_Title', 'Author_2020_Title', etc.
    Returns (author, year, title). Falls back to (stem, '', stem).
    """
    # Pattern: AuthorName2020_Some_Title or AuthorName_2020_Some_Title
    m = re.match(r"^([A-Za-z]+?)[\s_-]*(\d{4})[\s_-]*(.*)", stem)
    if m:
        author = m.group(1)
        year = m.group(2)
        title = m.group(3).replace("_", " ").replace("-", " ").strip()
        if not title:
            title = stem
        return author, year, title

    # Pattern: 2020_AuthorName_Title
    m = re.match(r"^(\d{4})[\s_-]+([A-Za-z]+?)[\s_-]+(.*)", stem)
    if m:
        year = m.group(1)
        author = m.group(2)
        title = m.group(3).replace("_", " ").replace("-", " ").strip()
        if not title:
            title = stem
        return author, year, title

    # No pattern matched
    return stem, "", stem


def _index_entry(
    citekey: str,
    pdf_path: Path,
    author: str,
    title: str,
    year: str,
    config: RAGConfig,
    embedder: Embedder,
    store: ChromaStore,
    force: bool,
    stats: IngestStats,
) -> None:
    """Index a single PDF entry (shared logic for bib and folder sources)."""
    # Skip if already indexed (unless force)
    if not force and store.has_citekey(citekey):
        stats.skipped_exists += 1
        return

    if not pdf_path.exists():
        stats.skipped_no_pdf += 1
        return

    try:
        # Extract text
        pages = extract_pdf(pdf_path)
        if not pages:
            stats.skipped_no_pdf += 1
            return

        # Chunk
        chunks = chunk_document(
            pages=pages,
            citekey=citekey,
            author=author,
            title=title,
            year=year,
            target_tokens=config.chunk_size,
            overlap_tokens=config.chunk_overlap,
        )

        if not chunks:
            stats.skipped_no_pdf += 1
            return

        # Embed
        texts = [c.text for c in chunks]
        embeddings = embedder.embed_texts(texts)

        # Upsert
        if force and store.has_citekey(citekey):
            store.delete_citekey(citekey)

        store.upsert_chunks(chunks, embeddings)
        stats.indexed += 1
        logger.info("Indexed %s (%d chunks)", citekey, len(chunks))

    except Exception as e:
        stats.failed += 1
        stats.errors.append((citekey, str(e)))
        logger.error("Failed to index %s: %s", citekey, e)


def run_ingest(
    config: RAGConfig | None = None,
    force: bool = False,
    cited_only: bool = False,
    source: str = "all",
) -> IngestStats:
    """Run the full ingestion pipeline.

    Args:
        config: RAG configuration (uses default if None).
        force: Re-index already indexed papers.
        cited_only: Only index papers cited in the paper (bib source only).
        source: Which sources to index -- "bib", "dir", or "all" (default).
    """
    if config is None:
        config = get_config()

    stats = IngestStats()
    embedder = Embedder(config.embedding_model)
    store = ChromaStore(config.resolve(config.chromadb_dir))

    # --- Bib source ---
    if source in ("bib", "all"):
        bib_path = config.resolve(config.bib_path)
        if bib_path.exists():
            logger.info("Parsing bibliography: %s", bib_path)
            entries = parse_bib(bib_path)
            bib_count = len(entries)
            logger.info("Found %d bib entries", bib_count)

            # Filter to cited-only if requested
            if cited_only:
                paper_path = config.resolve(config.paper_path)
                cited_keys = _get_cited_keys(paper_path)
                logger.info("Paper cites %d keys", len(cited_keys))
                entries = {k: v for k, v in entries.items() if k in cited_keys}
                bib_count = len(entries)
                logger.info("Filtered to %d cited entries", bib_count)

            stats.total += bib_count

            for citekey, entry in entries.items():
                # Entries tagged "exclude": skip and remove from index
                if "exclude" in entry.keywords:
                    if store.has_citekey(citekey):
                        n = store.delete_citekey(citekey)
                        stats.removed_excluded += 1
                        logger.info("Removed excluded entry: %s (%d chunks)", citekey, n)
                    stats.skipped_excluded += 1
                    continue
                if entry.pdf_path is None:
                    stats.skipped_no_pdf += 1
                    continue
                _index_entry(
                    citekey=citekey,
                    pdf_path=entry.pdf_path,
                    author=entry.author,
                    title=entry.title,
                    year=entry.year,
                    config=config,
                    embedder=embedder,
                    store=store,
                    force=force,
                    stats=stats,
                )
        elif source == "bib":
            logger.warning("Bib file not found: %s", bib_path)

    # --- PDF directory source ---
    if source in ("dir", "all") and config.pdf_dir:
        pdf_dir = config.resolve(config.pdf_dir)
        if pdf_dir.is_dir():
            pdfs = sorted(pdf_dir.glob("*.pdf"))
            logger.info("Found %d PDFs in %s", len(pdfs), pdf_dir)
            stats.total += len(pdfs)

            for pdf_path in pdfs:
                citekey = f"dir__{pdf_path.stem}"
                author, year, title = _parse_pdf_filename(pdf_path.stem)
                _index_entry(
                    citekey=citekey,
                    pdf_path=pdf_path,
                    author=author,
                    title=title,
                    year=year,
                    config=config,
                    embedder=embedder,
                    store=store,
                    force=force,
                    stats=stats,
                )
        elif source == "dir":
            logger.warning("PDF directory not found: %s", pdf_dir)

    return stats
