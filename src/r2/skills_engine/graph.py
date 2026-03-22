"""Skill relationship discovery from cognee's knowledge graph."""

from __future__ import annotations

import logging

from r2.skills_engine.config import SkillsConfig, get_config
from r2.skills_engine.indexer import _configure_cognee, discover_skills
from r2.skills_engine.models import SkillRelationship

logger = logging.getLogger(__name__)


async def get_relationships(
    skill_name: str | None = None,
    config: SkillsConfig | None = None,
) -> list[SkillRelationship]:
    """Discover relationships between skills using cognee's knowledge graph.

    Args:
        skill_name: Optional skill name to filter relationships for.
        config: Optional config override.

    Returns:
        List of SkillRelationship objects.
    """
    import cognee
    from cognee.modules.search.types import SearchType

    if config is None:
        config = get_config()

    _configure_cognee(config)

    # Query the knowledge graph for relationships
    query = f"relationships between skill {skill_name}" if skill_name else "skill relationships and dependencies"

    try:
        results = await cognee.search(
            query_type=SearchType.GRAPH_COMPLETION,
            query_text=query,
            datasets=[config.dataset_name],
        )
    except Exception as e:
        logger.warning("cognee GRAPH_COMPLETION search failed: %s", e)
        results = []

    all_skills = {s.name for s in discover_skills(config)}
    relationships: list[SkillRelationship] = []

    for search_result in results or []:
        # Extract text from SearchResult
        inner = getattr(search_result, "search_result", search_result)
        text = str(inner)
        rels = _extract_relationships(text, all_skills)
        relationships.extend(rels)

    # Deduplicate
    seen = set()
    unique = []
    for r in relationships:
        key = (r.source, r.target, r.relationship)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Filter by skill_name if provided
    if skill_name:
        unique = [r for r in unique if r.source == skill_name or r.target == skill_name]

    return unique


def _extract_relationships(text: str, skill_names: set[str]) -> list[SkillRelationship]:
    """Extract skill relationships from cognee result text."""
    rels = []
    text_lower = text.lower()

    # Find all skill names mentioned in the text
    mentioned = [name for name in skill_names if name.lower() in text_lower]

    if len(mentioned) >= 2:
        # Create pairwise relationships for co-mentioned skills
        for i, src in enumerate(mentioned):
            for tgt in mentioned[i + 1 :]:
                rel_type = _infer_relationship_type(text_lower, src, tgt)
                rels.append(
                    SkillRelationship(
                        source=src,
                        target=tgt,
                        relationship=rel_type,
                    )
                )

    return rels


def _infer_relationship_type(text: str, src: str, tgt: str) -> str:
    """Infer the type of relationship from context."""
    relationship_keywords = {
        "depends_on": ["depends", "requires", "needs", "prerequisite", "before"],
        "complements": ["complement", "together", "alongside", "combined", "both"],
        "triggers": ["trigger", "activate", "invoke", "call", "dispatch"],
        "replaces": ["replace", "instead", "alternative", "substitute"],
        "extends": ["extend", "build on", "enhance", "augment"],
    }

    for rel_type, keywords in relationship_keywords.items():
        if any(kw in text for kw in keywords):
            return rel_type

    return "related_to"


async def get_all_relationships(config: SkillsConfig | None = None) -> list[SkillRelationship]:
    """Get all discovered relationships between skills."""
    return await get_relationships(skill_name=None, config=config)
