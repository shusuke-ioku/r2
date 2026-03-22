"""Configuration via pydantic-settings with RAG_ env prefix."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from r2 import find_project_root


def _project_root() -> Path:
    return find_project_root()


class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=str(_project_root() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths (relative to project root)
    bib_path: str = "ref.bib"
    pdf_dir: str = ""  # optional folder of loose PDFs (e.g. "rag/pdfs")
    paper_path: str = "paper/paper.typ"
    chromadb_dir: str = ".claude/rag/.chromadb"

    # Embedding (set RAG_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2 for Japanese support)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Generation
    generation_model: str = "claude-sonnet-4-20250514"
    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("RAG_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
    )

    # Chunking
    chunk_size: int = 800  # target tokens
    chunk_overlap: int = 100  # overlap tokens

    # Download (SciDownl / Sci-Hub)
    download_dir: str = ".claude/rag/pdfs"  # where downloaded PDFs land
    scihub_url: str = ""  # explicit mirror URL; empty = auto-select
    download_proxy: str = ""  # e.g. "socks5://127.0.0.1:7890"

    # Zotero
    zotero_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("RAG_ZOTERO_API_KEY", "ZOTERO_API_KEY"),
    )
    zotero_library_id: str = Field(
        default="",
        validation_alias=AliasChoices("RAG_ZOTERO_LIBRARY_ID", "ZOTERO_LIBRARY_ID"),
    )

    # Search defaults
    default_n_results: int = 10

    # Self-RAG / DeepRAG
    self_rag_n_retrieve: int = 20   # over-fetch for self-RAG filtering
    deep_rag_n_per_sub: int = 8     # chunks per sub-question

    # Semantic Scholar
    semantic_scholar_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "RAG_SEMANTIC_SCHOLAR_API_KEY", "SEMANTIC_SCHOLAR_API_KEY"
        ),
    )
    semantic_scholar_base_url: str = "https://api.semanticscholar.org/graph/v1"
    semantic_scholar_rate_limit: float = 1.0  # seconds between requests

    # OpenAlex
    openalex_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "RAG_OPENALEX_API_KEY", "OPENALEX_API_KEY"
        ),
    )
    openalex_base_url: str = "https://api.openalex.org"
    openalex_rate_limit: float = 0.2  # seconds between requests

    # Elsevier Scopus
    scopus_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "RAG_SCOPUS_API_KEY", "SCOPUS_API_KEY"
        ),
    )
    scopus_base_url: str = "https://api.elsevier.com"
    scopus_rate_limit: float = 0.2  # seconds between requests

    @property
    def project_root(self) -> Path:
        return _project_root()

    def resolve(self, relpath: str) -> Path:
        """Resolve a path relative to project root."""
        return self.project_root / relpath


def get_config() -> RAGConfig:
    return RAGConfig()
