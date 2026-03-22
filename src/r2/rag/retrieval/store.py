"""ChromaDB persistent vector store."""

from __future__ import annotations

from pathlib import Path

import chromadb

from r2.rag.ingest.chunker import Chunk

COLLECTION_NAME = "zotero_papers"


class ChromaStore:
    def __init__(self, persist_dir: Path):
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Upsert chunks with their embeddings into ChromaDB."""
        ids = [f"{c.metadata.citekey}__chunk{c.metadata.chunk_idx}" for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "citekey": c.metadata.citekey,
                "author": c.metadata.author,
                "title": c.metadata.title,
                "year": c.metadata.year,
                "start_page": c.metadata.start_page,
                "end_page": c.metadata.end_page,
                "section": c.metadata.section,
                "chunk_idx": c.metadata.chunk_idx,
            }
            for c in chunks
        ]

        # ChromaDB has a batch limit; chunk into batches of 500
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            self._collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        citekey_filter: str | None = None,
    ) -> dict:
        """Query the collection. Returns ChromaDB query result dict."""
        where = {"citekey": citekey_filter} if citekey_filter else None
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

    def has_citekey(self, citekey: str) -> bool:
        """Check if any chunks from this citekey exist."""
        result = self._collection.get(
            where={"citekey": citekey},
            limit=1,
            include=[],
        )
        return len(result["ids"]) > 0

    def delete_citekey(self, citekey: str) -> int:
        """Delete all chunks for a citekey. Returns count deleted."""
        result = self._collection.get(
            where={"citekey": citekey},
            include=[],
        )
        ids = result["ids"]
        if ids:
            self._collection.delete(ids=ids)
        return len(ids)

    def count(self) -> int:
        """Total number of chunks in the store."""
        return self._collection.count()

    def citekey_stats(self) -> dict[str, int]:
        """Return {citekey: chunk_count} for all indexed papers."""
        stats: dict[str, int] = {}
        total = self._collection.count()
        batch_size = 500
        for offset in range(0, total, batch_size):
            result = self._collection.get(
                include=["metadatas"],
                limit=batch_size,
                offset=offset,
            )
            for meta in result["metadatas"]:
                key = meta["citekey"]
                stats[key] = stats.get(key, 0) + 1
        return stats
