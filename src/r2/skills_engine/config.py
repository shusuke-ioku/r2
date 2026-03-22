"""Configuration via pydantic-settings with SKILLS_ env prefix."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from r2 import find_project_root


def _project_root() -> Path:
    return find_project_root()


class SkillsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SKILLS_",
        env_file=str(_project_root() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    skills_dir: str = ".claude/skills"
    cognee_data_dir: str = ".claude/skills_engine/.cognee"
    usage_db_path: str = ".claude/skills_engine/.usage.db"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Cognee
    dataset_name: str = "claude_skills"

    # LLM (for cognee's cognify step — uses Anthropic by default)
    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SKILLS_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
    )
    llm_provider: str = "anthropic"
    llm_model: str = "claude-haiku-4-5-20251001"

    # Dispatch
    default_top_k: int = 5
    confidence_threshold: float = 0.3

    @property
    def project_root(self) -> Path:
        return _project_root()

    def resolve(self, relpath: str) -> Path:
        """Resolve a path relative to project root."""
        return self.project_root / relpath


def get_config() -> SkillsConfig:
    return SkillsConfig()
