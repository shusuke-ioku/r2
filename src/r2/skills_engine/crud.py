"""Create, update, and delete skills (filesystem-first, then re-index)."""

from __future__ import annotations

import logging
from pathlib import Path

from r2.skills_engine.config import SkillsConfig, get_config
from r2.skills_engine.indexer import discover_skills, index_all, parse_skill
from r2.skills_engine.models import SkillRecord

logger = logging.getLogger(__name__)


def _write_skill_md(path: Path, name: str, description: str, body: str) -> None:
    """Write a SKILL.md file with YAML frontmatter."""
    content = (
        f"---\n"
        f"name: {name}\n"
        f"description: >\n"
        f"  {description}\n"
        f"---\n\n"
        f"{body}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


async def create_skill(
    name: str,
    description: str,
    body: str,
    config: SkillsConfig | None = None,
) -> SkillRecord:
    """Create a new skill: write SKILL.md and re-index.

    Args:
        name: Skill identifier (used as directory name).
        description: One-line description for dispatch matching.
        body: Full markdown body of the skill.
        config: Optional config override.

    Returns:
        The created SkillRecord.

    Raises:
        FileExistsError: If a skill with that name already exists.
    """
    if config is None:
        config = get_config()

    skill_dir = config.resolve(config.skills_dir) / name
    skill_path = skill_dir / "SKILL.md"

    if skill_path.exists():
        raise FileExistsError(f"Skill '{name}' already exists at {skill_path}")

    _write_skill_md(skill_path, name, description, body)
    logger.info("Created skill '%s' at %s", name, skill_path)

    # Re-index
    await index_all(force=True, config=config)

    return parse_skill(skill_path)


async def update_skill(
    name: str,
    description: str | None = None,
    body: str | None = None,
    config: SkillsConfig | None = None,
) -> SkillRecord:
    """Update an existing skill's description and/or body, then re-index.

    Args:
        name: Skill identifier.
        description: New description (None = keep existing).
        body: New body (None = keep existing).
        config: Optional config override.

    Returns:
        The updated SkillRecord.

    Raises:
        FileNotFoundError: If the skill doesn't exist.
    """
    if config is None:
        config = get_config()

    skill_path = config.resolve(config.skills_dir) / name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill '{name}' not found at {skill_path}")

    existing = parse_skill(skill_path)
    new_desc = description if description is not None else existing.description
    new_body = body if body is not None else existing.body

    _write_skill_md(skill_path, name, new_desc, new_body)
    logger.info("Updated skill '%s'", name)

    # Re-index
    await index_all(force=True, config=config)

    return parse_skill(skill_path)


async def delete_skill(
    name: str,
    confirm: bool = False,
    config: SkillsConfig | None = None,
) -> str:
    """Delete a skill directory and re-index.

    Args:
        name: Skill identifier.
        confirm: Must be True to actually delete. Safety flag.
        config: Optional config override.

    Returns:
        Status message.

    Raises:
        FileNotFoundError: If the skill doesn't exist.
        ValueError: If confirm is False.
    """
    if config is None:
        config = get_config()

    skill_dir = config.resolve(config.skills_dir) / name
    skill_path = skill_dir / "SKILL.md"

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill '{name}' not found at {skill_path}")

    if not confirm:
        raise ValueError(
            f"Deletion of skill '{name}' requires confirm=True. "
            f"This will remove {skill_dir} and all its contents."
        )

    # Remove all files in the skill directory
    import shutil
    shutil.rmtree(skill_dir)
    logger.info("Deleted skill '%s' at %s", name, skill_dir)

    # Re-index
    await index_all(force=True, config=config)

    return f"Skill '{name}' deleted successfully."


def list_skills(config: SkillsConfig | None = None) -> list[SkillRecord]:
    """List all registered skills."""
    return discover_skills(config)
