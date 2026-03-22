"""Search: query -> ranked results with citations."""

from __future__ import annotations

from dataclasses import dataclass

from r2.rag.config import RAGConfig, get_config
from r2.rag.retrieval.embedder import Embedder
from r2.rag.retrieval.store import ChromaStore


@dataclass
class SearchResult:
    citekey: str
    author: str
    title: str
    year: str
    section: str
    start_page: int
    end_page: int
    chunk_idx: int
    text: str
    distance: float
    citation: str
    typst_cite: str


def _format_citation(meta: dict) -> str:
    """Format a human-readable citation."""
    author = meta.get("author", "")
    year = meta.get("year", "")
    if author:
        first = author.split(" and ")[0].split(",")[0].strip()
        et_al = " et al." if " and " in author else ""
        author_str = f"{first}{et_al}"
    else:
        author_str = meta.get("citekey", "Unknown")

    pages = ""
    sp = meta.get("start_page", 0)
    ep = meta.get("end_page", 0)
    if sp and ep:
        pages = f", pp. {sp}-{ep}" if sp != ep else f", p. {sp}"

    return f"{author_str} ({year}{pages})"


def search(
    query: str,
    n_results: int | None = None,
    citekey_filter: str | None = None,
    config: RAGConfig | None = None,
) -> list[SearchResult]:
    """Search the vector store and return ranked results with citations."""
    if config is None:
        config = get_config()
    if n_results is None:
        n_results = config.default_n_results

    embedder = Embedder(config.embedding_model)
    store = ChromaStore(config.resolve(config.chromadb_dir))

    query_embedding = embedder.embed_query(query)
    raw = store.query(query_embedding, n_results=n_results, citekey_filter=citekey_filter)

    results: list[SearchResult] = []
    if not raw["ids"] or not raw["ids"][0]:
        return results

    for i, doc_id in enumerate(raw["ids"][0]):
        meta = raw["metadatas"][0][i]
        text = raw["documents"][0][i]
        distance = raw["distances"][0][i]

        results.append(SearchResult(
            citekey=meta["citekey"],
            author=meta.get("author", ""),
            title=meta.get("title", ""),
            year=meta.get("year", ""),
            section=meta.get("section", ""),
            start_page=meta.get("start_page", 0),
            end_page=meta.get("end_page", 0),
            chunk_idx=meta.get("chunk_idx", 0),
            text=text,
            distance=distance,
            citation=_format_citation(meta),
            typst_cite=f"@{meta['citekey']}",
        ))

    return results
