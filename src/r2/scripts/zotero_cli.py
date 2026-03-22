"""CLI for Zotero local API (replaces zotero-mcp-server).

Requires Zotero desktop running with the MCP plugin (HTTP API on port 23119).
Usage: python zotero_cli.py <command> [options]
"""

from __future__ import annotations

import json
import sys

import click
import httpx

ZOTERO_BASE = "http://127.0.0.1:23119"
TIMEOUT = 30.0


def _get(endpoint: str, params: dict | None = None) -> dict | str:
    """GET request to Zotero local API."""
    url = f"{ZOTERO_BASE}{endpoint}"
    params = {k: v for k, v in (params or {}).items() if v is not None}
    resp = httpx.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "")
    if "json" in ct:
        return resp.json()
    return resp.text


def _post(endpoint: str, payload: dict) -> dict | str:
    """POST request to Zotero local API."""
    url = f"{ZOTERO_BASE}{endpoint}"
    resp = httpx.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "")
    if "json" in ct:
        return resp.json()
    return resp.text


def _output(data):
    """Print result as formatted JSON or plain text."""
    if isinstance(data, (dict, list)):
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        click.echo(data)


@click.group()
def cli():
    """Zotero local API client. Requires Zotero desktop with MCP plugin running."""
    pass


@cli.command()
def ping():
    """Check connection to Zotero."""
    _output(_get("/ping"))


@cli.command()
@click.argument("query", required=False)
@click.option("--title", default=None, help="Search by title")
@click.option("--key", default=None, help="Get item by key")
@click.option("--tags", default=None, help="Filter by tags")
@click.option("--tag-mode", default=None, type=click.Choice(["any", "all", "none"]))
@click.option("--year-range", default=None, help="Year range (e.g. '2020-2023')")
@click.option("--sort", default=None, type=click.Choice(["relevance", "date", "title", "year"]))
@click.option("--direction", default=None, type=click.Choice(["asc", "desc"]))
def search(query, title, key, tags, tag_mode, year_range, sort, direction):
    """Search the Zotero library."""
    params = {
        "q": query, "title": title, "key": key, "tags": tags,
        "tagMode": tag_mode, "yearRange": year_range,
        "sort": sort, "direction": direction,
    }
    _output(_get("/search", params))


@cli.command("get-item")
@click.argument("key")
def get_item(key: str):
    """Get a Zotero item by its key."""
    _output(_get("/search", {"key": key}))


@cli.command("find-item")
@click.option("--doi", default=None, help="Find by DOI")
@click.option("--isbn", default=None, help="Find by ISBN")
def find_item(doi, isbn):
    """Find an item by DOI or ISBN."""
    q = doi or isbn
    if not q:
        click.echo("Provide --doi or --isbn", err=True)
        sys.exit(1)
    _output(_get("/search", {"q": q}))


@cli.command()
def collections():
    """List all collections."""
    _output(_get("/collections"))


@cli.command("search-collections")
@click.argument("query")
def search_collections(query: str):
    """Search collections by name."""
    _output(_get("/collections/search", {"q": query}))


@cli.command("collection-details")
@click.argument("collection_key")
def collection_details(collection_key: str):
    """Get details of a collection."""
    _output(_get(f"/collections/{collection_key}"))


@cli.command("collection-items")
@click.argument("collection_key")
def collection_items(collection_key: str):
    """Get items in a collection."""
    _output(_get(f"/collections/{collection_key}/items"))


@cli.command("pdf-content")
@click.argument("item_key")
@click.option("--page", default=None, type=int, help="Specific page number")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def pdf_content(item_key: str, page: int | None, fmt: str):
    """Extract PDF text from a Zotero item."""
    params = {"format": fmt}
    if page is not None:
        params["page"] = str(page)
    _output(_get(f"/items/{item_key}/pdf-content", params))


@cli.command("search-annotations")
@click.argument("query", required=False)
@click.option("--type", "ann_type", default=None, help="note, highlight, annotation, ink, text, image")
@click.option("--tags", default=None)
@click.option("--color", default=None)
@click.option("--has-comment", is_flag=True, default=None)
@click.option("--item-key", default=None, help="Restrict to a specific item")
@click.option("--sort", default=None)
@click.option("--direction", default=None, type=click.Choice(["asc", "desc"]))
@click.option("--limit", default=None, type=int)
@click.option("--offset", default=None, type=int)
@click.option("--detailed", is_flag=True, default=None)
def search_annotations(query, ann_type, tags, color, has_comment, item_key, sort, direction, limit, offset, detailed):
    """Search annotations across the library."""
    params = {
        "q": query, "type": ann_type, "tags": tags, "color": color,
        "hasComment": "true" if has_comment else None,
        "itemKey": item_key, "sort": sort, "direction": direction,
        "limit": limit, "offset": offset,
        "detailed": "true" if detailed else None,
    }
    _output(_get("/annotations/search", params))


@cli.command("item-notes")
@click.argument("item_key")
@click.option("--limit", default=None, type=int)
@click.option("--offset", default=None, type=int)
def item_notes(item_key: str, limit, offset):
    """Get notes for a Zotero item."""
    _output(_get(f"/items/{item_key}/notes", {"limit": limit, "offset": offset}))


@cli.command("item-annotations")
@click.argument("item_key")
@click.option("--type", "ann_type", default=None)
@click.option("--color", default=None)
@click.option("--limit", default=None, type=int)
@click.option("--offset", default=None, type=int)
def item_annotations(item_key: str, ann_type, color, limit, offset):
    """Get annotations for a Zotero item."""
    params = {"type": ann_type, "color": color, "limit": limit, "offset": offset}
    _output(_get(f"/items/{item_key}/annotations", params))


@cli.command("get-annotation")
@click.argument("annotation_id")
def get_annotation(annotation_id: str):
    """Get a single annotation by ID."""
    _output(_get(f"/annotations/{annotation_id}"))


@cli.command("get-annotations-batch")
@click.argument("ids", nargs=-1, required=True)
def get_annotations_batch(ids: tuple[str, ...]):
    """Get multiple annotations by ID.

    IDS: one or more annotation IDs.
    """
    _output(_post("/annotations/batch", {"ids": list(ids)}))


if __name__ == "__main__":
    cli()
