"""Semantic skill matching: task description → ranked skill recommendations."""

from __future__ import annotations

import logging

from r2.skills_engine.config import SkillsConfig, get_config
from r2.skills_engine.indexer import _configure_cognee, discover_skills
from r2.skills_engine.models import DispatchResult

logger = logging.getLogger(__name__)


async def dispatch(
    query: str,
    top_k: int | None = None,
    config: SkillsConfig | None = None,
) -> list[DispatchResult]:
    """Find skills matching a task description using cognee semantic search.

    Args:
        query: Task description (e.g. "run the analysis pipeline")
        top_k: Max number of results (default from config)
        config: Optional config override

    Returns:
        Ranked list of DispatchResult sorted by confidence (descending).
    """
    import cognee
    from cognee.modules.search.types import SearchType

    if config is None:
        config = get_config()
    if top_k is None:
        top_k = config.default_top_k

    _configure_cognee(config)

    # Search cognee for matching chunks
    try:
        results = await cognee.search(
            query_type=SearchType.CHUNKS,
            query_text=query,
            datasets=[config.dataset_name],
            top_k=top_k * 3,  # over-fetch to get enough unique skills
        )
    except Exception as e:
        logger.warning("cognee CHUNKS search failed: %s", e)
        results = []

    # Parse results into dispatch recommendations
    all_skills = {s.name: s for s in discover_skills(config)}
    dispatch_results: list[DispatchResult] = []
    seen_skills: set[str] = set()

    for search_result in results or []:
        # SearchResult has .search_result field with actual content
        text = _extract_text(search_result)
        matched_skill = _extract_skill_name(text, all_skills)
        if matched_skill and matched_skill not in seen_skills:
            seen_skills.add(matched_skill)
            skill = all_skills[matched_skill]
            confidence = _compute_confidence(search_result, len(dispatch_results))
            dispatch_results.append(
                DispatchResult(
                    skill_name=matched_skill,
                    confidence=confidence,
                    reason=f"Semantic match for: {query[:100]}",
                    description=skill.description[:200],
                )
            )

    # Sort by confidence descending
    dispatch_results.sort(key=lambda r: r.confidence, reverse=True)
    return dispatch_results[:top_k]


def _extract_text(search_result: object) -> str:
    """Extract text content from a cognee SearchResult."""
    # cognee SearchResult has .search_result attribute
    if hasattr(search_result, "search_result"):
        inner = search_result.search_result
        if isinstance(inner, str):
            return inner
        if hasattr(inner, "text"):
            return str(inner.text)
        if isinstance(inner, dict):
            return inner.get("text", str(inner))
        return str(inner)
    if isinstance(search_result, dict):
        return search_result.get("text", str(search_result))
    return str(search_result)


def _extract_skill_name(text: str, skills: dict[str, object]) -> str | None:
    """Try to find which skill a search result belongs to."""
    text_lower = text.lower()
    # Look for "Skill: <name>" pattern (from our document format)
    for name in skills:
        if f"skill: {name.lower()}" in text_lower:
            return name
    # Fallback: check if skill name appears in the text
    for name in skills:
        if name.lower() in text_lower:
            return name
    return None


def _compute_confidence(result: object, rank: int) -> float:
    """Extract or compute a confidence score from a cognee search result.

    Uses the result's score if available, otherwise estimates from rank position.
    """
    # Try to get score from the search result
    inner = getattr(result, "search_result", result)

    for obj in (result, inner):
        if isinstance(obj, dict):
            score = obj.get("score", obj.get("relevance_score", obj.get("similarity", None)))
            if score is not None:
                return float(score)
            distance = obj.get("distance", None)
            if distance is not None:
                return max(0.0, 1.0 - float(distance))
        else:
            for attr in ("score", "relevance_score", "similarity"):
                if hasattr(obj, attr):
                    val = getattr(obj, attr)
                    if val is not None:
                        return float(val)
            if hasattr(obj, "distance"):
                val = getattr(obj, "distance")
                if val is not None:
                    return max(0.0, 1.0 - float(val))

    # Estimate from rank position (first result = highest confidence)
    return max(0.1, 1.0 - (rank * 0.15))
