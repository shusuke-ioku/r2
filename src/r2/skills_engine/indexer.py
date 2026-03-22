"""Parse SKILL.md files and index them into cognee."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import yaml

from r2.skills_engine.config import SkillsConfig, get_config
from r2.skills_engine.models import SkillRecord

logger = logging.getLogger(__name__)

# Cache of indexed skill hashes (persisted as JSON alongside cognee data)
_HASH_CACHE_NAME = "skill_hashes.json"


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a SKILL.md file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    fm_str, body = match.groups()
    try:
        fm = yaml.safe_load(fm_str) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body.strip()


def _content_hash(text: str) -> str:
    """SHA-256 hash of file content for stale detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_skill(path: Path) -> SkillRecord:
    """Parse a single SKILL.md into a SkillRecord."""
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    return SkillRecord(
        name=fm.get("name", path.parent.name),
        description=fm.get("description", "").strip(),
        body=body,
        file_path=path,
        content_hash=_content_hash(text),
    )


def discover_skills(config: SkillsConfig | None = None) -> list[SkillRecord]:
    """Find and parse all SKILL.md files in the skills directory."""
    if config is None:
        config = get_config()
    skills_dir = config.resolve(config.skills_dir)
    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        try:
            skills.append(parse_skill(skill_md))
        except Exception as e:
            logger.warning("Failed to parse %s: %s", skill_md, e)
    return skills


def _load_hash_cache(config: SkillsConfig) -> dict[str, str]:
    """Load the hash cache from disk."""
    cache_path = config.resolve(config.cognee_data_dir) / _HASH_CACHE_NAME
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_hash_cache(config: SkillsConfig, cache: dict[str, str]) -> None:
    """Save the hash cache to disk."""
    cache_dir = config.resolve(config.cognee_data_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / _HASH_CACHE_NAME
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _configure_cognee(config: SkillsConfig) -> None:
    """Set up cognee's configuration before any operations.

    Must be called before every cognee operation because prune_system
    resets the config state.
    """
    import cognee

    # Disable multi-user access control and LLM connection test
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

    # Set data and system directories within our project
    data_dir = str(config.resolve(config.cognee_data_dir))
    system_dir = os.path.join(data_dir, ".system")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(system_dir, exist_ok=True)
    cognee.config.data_root_directory(data_dir)
    cognee.config.system_root_directory(system_dir)

    # Configure LLM for cognify step (Anthropic by default — same key as RAG)
    if config.anthropic_api_key:
        cognee.config.set_llm_config(
            {
                "llm_provider": "anthropic",
                "llm_model": f"anthropic/{config.llm_model}",
                "llm_api_key": config.anthropic_api_key,
            }
        )


async def index_all(force: bool = False, config: SkillsConfig | None = None) -> dict:
    """Index all skills into cognee. Returns stats dict.

    Args:
        force: Re-index all skills even if unchanged.
        config: Optional config override.
    """
    import cognee

    if config is None:
        config = get_config()

    _configure_cognee(config)

    skills = discover_skills(config)
    if not skills:
        return {"status": "no_skills_found", "indexed": 0, "skipped": 0}

    hash_cache = _load_hash_cache(config)
    to_index = []

    for skill in skills:
        cached_hash = hash_cache.get(skill.name, "")
        if force or cached_hash != skill.content_hash:
            to_index.append(skill)

    if not to_index and not force:
        return {
            "status": "up_to_date",
            "total_skills": len(skills),
            "indexed": 0,
            "skipped": len(skills),
        }

    # Reset cognee dataset for fresh index
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
    except Exception as e:
        logger.warning("Prune failed (may be first run): %s", e)

    # Re-apply config after prune (prune_system resets state)
    _configure_cognee(config)

    # Add all skills (index everything when any skill changes for consistency)
    for skill in skills:
        doc_text = skill.to_document()
        await cognee.add(doc_text, dataset_name=config.dataset_name)

    # Build knowledge graph
    try:
        await cognee.cognify()
    except Exception as e:
        logger.warning("cognify failed (vector search still works): %s", e)

    # Update hash cache
    now = datetime.now()
    new_cache = {}
    for skill in skills:
        skill.last_indexed = now
        new_cache[skill.name] = skill.content_hash
    _save_hash_cache(config, new_cache)

    return {
        "status": "indexed",
        "total_skills": len(skills),
        "indexed": len(to_index),
        "skipped": len(skills) - len(to_index),
        "skills": [s.name for s in to_index],
    }


async def ensure_indexed(config: SkillsConfig | None = None) -> None:
    """Check if index is stale and re-index if needed. Called on startup."""
    if config is None:
        config = get_config()

    skills = discover_skills(config)
    hash_cache = _load_hash_cache(config)

    needs_reindex = False
    for skill in skills:
        if hash_cache.get(skill.name, "") != skill.content_hash:
            needs_reindex = True
            break

    if needs_reindex:
        logger.info("Skills changed, re-indexing...")
        await index_all(force=False, config=config)
