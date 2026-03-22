"""MCP server exposing skill management tools via FastMCP."""

from __future__ import annotations

import asyncio
import json
import logging

from mcp.server.fastmcp import FastMCP

from r2.skills_engine.config import get_config

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "skills_engine",
    instructions="Dynamic skill management with semantic dispatch, usage tracking, and CRUD.",
)


# ---------------------------------------------------------------------------
# Helper to run async from sync context
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async coroutine, handling existing event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Tool 1: skill_search
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_search(query: str, top_k: int = 5) -> str:
    """Semantic search for skills matching a query.

    Returns skills ranked by semantic similarity to the query text.

    Args:
        query: Search query (e.g. "write academic prose" or "debug R script")
        top_k: Maximum number of results (default 5)
    """
    from r2.skills_engine.dispatch import dispatch

    config = get_config()
    results = _run(dispatch(query, top_k=top_k, config=config))

    if not results:
        return f"No skills found matching: {query}"

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.skill_name} (confidence: {r.confidence:.3f})\n"
            f"    {r.description}"
        )
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Tool 2: skill_dispatch
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_dispatch(task: str, top_k: int = 3) -> str:
    """Get ranked skill recommendations with confidence scores for a task.

    This is the primary dispatch tool — given a task description, returns
    the most relevant skills with confidence scores and reasons.

    Args:
        task: Task description (e.g. "run the analysis pipeline and check results")
        top_k: Maximum recommendations (default 3)
    """
    from r2.skills_engine.dispatch import dispatch
    from r2.skills_engine.usage import log_usage

    config = get_config()
    results = _run(dispatch(task, top_k=top_k, config=config))

    if not results:
        return json.dumps({"task": task, "recommendations": [], "message": "No matching skills found."})

    # Log usage for top recommendation
    if results:
        log_usage(
            skill_name=results[0].skill_name,
            query=task,
            confidence=results[0].confidence,
            config=config,
        )

    return json.dumps(
        {
            "task": task,
            "recommendations": [r.to_dict() for r in results],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool 3: skill_info
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_info(name: str) -> str:
    """Get full details about a named skill.

    Args:
        name: Skill name (e.g. "writing", "analysis", "debugging")
    """
    from r2.skills_engine.indexer import discover_skills

    config = get_config()
    skills = {s.name: s for s in discover_skills(config)}

    if name not in skills:
        available = ", ".join(sorted(skills.keys()))
        return f"Skill '{name}' not found. Available: {available}"

    skill = skills[name]
    return json.dumps(skill.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# Tool 4: skill_list
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_list() -> str:
    """List all registered skills with their descriptions."""
    from r2.skills_engine.indexer import discover_skills

    config = get_config()
    skills = discover_skills(config)

    if not skills:
        return "No skills found."

    parts = []
    for s in sorted(skills, key=lambda x: x.name):
        parts.append(f"- **{s.name}**: {s.description[:150]}")

    return f"Found {len(skills)} skills:\n\n" + "\n".join(parts)


# ---------------------------------------------------------------------------
# Tool 5: skill_create
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_create(name: str, description: str, body: str) -> str:
    """Create a new skill (writes SKILL.md and re-indexes).

    Args:
        name: Skill identifier (used as directory name, e.g. "data-viz")
        description: One-line trigger description for dispatch matching
        body: Full markdown body of the skill instructions
    """
    from r2.skills_engine.crud import create_skill

    config = get_config()
    try:
        skill = _run(create_skill(name, description, body, config=config))
        return json.dumps(
            {"status": "created", "skill": skill.to_dict()},
            indent=2,
        )
    except FileExistsError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# Tool 6: skill_update
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_update(
    name: str,
    description: str | None = None,
    body: str | None = None,
) -> str:
    """Update a skill's description or body, then re-index.

    Args:
        name: Skill name to update
        description: New description (omit to keep existing)
        body: New body (omit to keep existing)
    """
    from r2.skills_engine.crud import update_skill

    config = get_config()
    try:
        skill = _run(update_skill(name, description=description, body=body, config=config))
        return json.dumps(
            {"status": "updated", "skill": skill.to_dict()},
            indent=2,
        )
    except FileNotFoundError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# Tool 7: skill_delete
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_delete(name: str, confirm: bool = False) -> str:
    """Remove a skill (with confirmation flag).

    Args:
        name: Skill name to delete
        confirm: Must be True to actually delete. Safety flag to prevent accidental deletion.
    """
    from r2.skills_engine.crud import delete_skill

    config = get_config()
    try:
        msg = _run(delete_skill(name, confirm=confirm, config=config))
        return json.dumps({"status": "deleted", "message": msg})
    except (FileNotFoundError, ValueError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# Tool 8: skill_relationships
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_relationships(skill_name: str | None = None) -> str:
    """Show discovered skill dependencies and compositions from the knowledge graph.

    Args:
        skill_name: Optional skill name to filter relationships. Omit for all relationships.
    """
    from r2.skills_engine.graph import get_relationships

    config = get_config()
    try:
        rels = _run(get_relationships(skill_name=skill_name, config=config))
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

    if not rels:
        msg = f"No relationships found for '{skill_name}'." if skill_name else "No relationships discovered yet."
        return json.dumps({"relationships": [], "message": msg})

    return json.dumps(
        {
            "skill_name": skill_name,
            "relationships": [r.to_dict() for r in rels],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool 9: skill_usage
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_usage(skill_name: str | None = None, limit: int = 50) -> str:
    """Query usage history and patterns.

    Args:
        skill_name: Optional filter by skill name. Omit for all skills.
        limit: Max events to return (default 50)
    """
    from r2.skills_engine.usage import get_usage_stats, query_usage

    config = get_config()

    if skill_name:
        events = query_usage(skill_name=skill_name, limit=limit, config=config)
        return json.dumps(
            {"skill_name": skill_name, "events": events, "count": len(events)},
            indent=2,
        )
    else:
        stats = get_usage_stats(config=config)
        return json.dumps(stats, indent=2)


# ---------------------------------------------------------------------------
# Tool 10: skill_reindex
# ---------------------------------------------------------------------------

@mcp.tool()
def skill_reindex(force: bool = True) -> str:
    """Force re-indexing of all skills into cognee.

    Args:
        force: Re-index all skills even if unchanged (default True)
    """
    from r2.skills_engine.indexer import index_all

    config = get_config()
    stats = _run(index_all(force=force, config=config))
    return json.dumps(stats, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
