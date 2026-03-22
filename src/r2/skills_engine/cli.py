"""Click CLI for the skills engine (replaces MCP server)."""

from __future__ import annotations

import asyncio
import json
import logging
import sys

import click

from r2.skills_engine.config import get_config


def _run(coro):
    """Run an async coroutine from sync context."""
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


def _output(data):
    """Print result as formatted JSON or plain text."""
    if isinstance(data, (dict, list)):
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        click.echo(data)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Skills engine: semantic dispatch, CRUD, usage tracking."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", stream=sys.stderr)


@cli.command()
@click.argument("query")
@click.option("-k", "--top-k", default=5, type=int, help="Max results (default 5)")
def search(query: str, top_k: int):
    """Semantic search for skills matching a query."""
    from r2.skills_engine.dispatch import dispatch

    config = get_config()
    results = _run(dispatch(query, top_k=top_k, config=config))

    if not results:
        click.echo(f"No skills found matching: {query}")
        return

    for i, r in enumerate(results, 1):
        click.echo(f"[{i}] {r.skill_name} (confidence: {r.confidence:.3f})")
        click.echo(f"    {r.description}")
        click.echo()


@cli.command()
@click.argument("task")
@click.option("-k", "--top-k", default=3, type=int, help="Max recommendations (default 3)")
def dispatch_cmd(task: str, top_k: int):
    """Get ranked skill recommendations for a task."""
    from r2.skills_engine.dispatch import dispatch
    from r2.skills_engine.usage import log_usage

    config = get_config()
    results = _run(dispatch(task, top_k=top_k, config=config))

    if not results:
        _output({"task": task, "recommendations": [], "message": "No matching skills found."})
        return

    log_usage(
        skill_name=results[0].skill_name,
        query=task,
        confidence=results[0].confidence,
        config=config,
    )

    _output({"task": task, "recommendations": [r.to_dict() for r in results]})


@cli.command()
@click.argument("name")
def info(name: str):
    """Get full details about a named skill."""
    from r2.skills_engine.indexer import discover_skills

    config = get_config()
    skills = {s.name: s for s in discover_skills(config)}

    if name not in skills:
        available = ", ".join(sorted(skills.keys()))
        click.echo(f"Skill '{name}' not found. Available: {available}")
        return

    _output(skills[name].to_dict())


@cli.command("list")
def list_cmd():
    """List all registered skills."""
    from r2.skills_engine.indexer import discover_skills

    config = get_config()
    skills = discover_skills(config)

    if not skills:
        click.echo("No skills found.")
        return

    click.echo(f"Found {len(skills)} skills:\n")
    for s in sorted(skills, key=lambda x: x.name):
        click.echo(f"  - {s.name}: {s.description[:150]}")


@cli.command()
@click.argument("name")
@click.option("--description", "-d", required=True, help="One-line trigger description")
@click.option("--body-file", type=click.File("r"), default=None, help="File with skill body (default: stdin)")
@click.option("--body", "body_text", default=None, help="Inline skill body text")
def create(name: str, description: str, body_file, body_text: str | None):
    """Create a new skill (writes SKILL.md and re-indexes)."""
    from r2.skills_engine.crud import create_skill

    if body_text:
        body = body_text
    elif body_file:
        body = body_file.read()
    else:
        click.echo("Reading body from stdin (Ctrl-D to end)...", err=True)
        body = sys.stdin.read()

    config = get_config()
    try:
        skill = _run(create_skill(name, description, body, config=config))
        _output({"status": "created", "skill": skill.to_dict()})
    except (FileExistsError, Exception) as e:
        _output({"status": "error", "message": str(e)})


@cli.command()
@click.argument("name")
@click.option("--description", "-d", default=None, help="New description (omit to keep existing)")
@click.option("--body-file", type=click.File("r"), default=None, help="File with new body")
@click.option("--body", "body_text", default=None, help="Inline new body text")
def update(name: str, description: str | None, body_file, body_text: str | None):
    """Update a skill's description or body."""
    from r2.skills_engine.crud import update_skill

    body = body_text or (body_file.read() if body_file else None)

    config = get_config()
    try:
        skill = _run(update_skill(name, description=description, body=body, config=config))
        _output({"status": "updated", "skill": skill.to_dict()})
    except (FileNotFoundError, Exception) as e:
        _output({"status": "error", "message": str(e)})


@cli.command()
@click.argument("name")
@click.option("--confirm", is_flag=True, help="Required to actually delete")
def delete(name: str, confirm: bool):
    """Delete a skill."""
    from r2.skills_engine.crud import delete_skill

    config = get_config()
    try:
        msg = _run(delete_skill(name, confirm=confirm, config=config))
        _output({"status": "deleted", "message": msg})
    except (FileNotFoundError, ValueError, Exception) as e:
        _output({"status": "error", "message": str(e)})


@cli.command()
@click.option("--skill", "skill_name", default=None, help="Filter to a specific skill")
def relationships(skill_name: str | None):
    """Show discovered skill dependencies from the knowledge graph."""
    from r2.skills_engine.graph import get_relationships

    config = get_config()
    try:
        rels = _run(get_relationships(skill_name=skill_name, config=config))
    except Exception as e:
        _output({"status": "error", "message": str(e)})
        return

    if not rels:
        msg = f"No relationships found for '{skill_name}'." if skill_name else "No relationships discovered yet."
        _output({"relationships": [], "message": msg})
        return

    _output({"skill_name": skill_name, "relationships": [r.to_dict() for r in rels]})


@cli.command()
@click.option("--skill", "skill_name", default=None, help="Filter by skill name")
@click.option("--limit", default=50, type=int)
def usage(skill_name: str | None, limit: int):
    """Query usage history and patterns."""
    from r2.skills_engine.usage import get_usage_stats, query_usage

    config = get_config()

    if skill_name:
        events = query_usage(skill_name=skill_name, limit=limit, config=config)
        _output({"skill_name": skill_name, "events": events, "count": len(events)})
    else:
        _output(get_usage_stats(config=config))


@cli.command()
@click.option("--force/--no-force", default=True, help="Re-index all even if unchanged (default: force)")
def reindex(force: bool):
    """Force re-indexing of all skills into cognee."""
    from r2.skills_engine.indexer import index_all

    config = get_config()
    stats = _run(index_all(force=force, config=config))
    _output(stats)


if __name__ == "__main__":
    cli()
