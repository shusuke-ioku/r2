"""r2 CLI — AI-driven research environment."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import click

from r2 import __version__


# ---------------------------------------------------------------------------
# Lazy group — loads commands from another Click group on demand
# ---------------------------------------------------------------------------

class _LazyGroup(click.Group):
    """A Click group that lazily loads commands from another CLI module."""

    def __init__(self, *args, import_path: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._import_path = import_path
        self._loaded: click.Group | None = None

    def _load(self) -> click.Group:
        if self._loaded is None:
            module_path, attr = self._import_path.rsplit(":", 1)
            mod = importlib.import_module(module_path)
            self._loaded = getattr(mod, attr)
        return self._loaded

    def list_commands(self, ctx: click.Context) -> list[str]:
        return self._load().list_commands(ctx)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        return self._load().get_command(ctx, cmd_name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_template_dir() -> Path | None:
    """Locate the Copier template directory shipped with r2."""
    pkg_dir = Path(__file__).resolve().parent
    candidates = [
        pkg_dir.parent.parent / "template",  # editable install / dev
        pkg_dir / "template",  # bundled inside package
    ]
    for c in candidates:
        if (c / "copier.yml").exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Main CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(__version__, prog_name="r2")
def cli() -> None:
    """r2 — AI-driven research environment for academic papers."""


# ---------------------------------------------------------------------------
# r2 init
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("path", default=".")
@click.option("--defaults", is_flag=True, help="Accept all Copier defaults.")
def init(path: str, defaults: bool) -> None:
    """Scaffold a new research project at PATH."""
    from copier import run_copy

    template_dir = _find_template_dir()
    if template_dir is None:
        click.echo("Error: could not locate the r2 template directory.", err=True)
        raise SystemExit(1)

    # Derive a sensible default project_name from the destination path
    dest = Path(path).resolve()
    default_name = dest.name if dest.name != "." else Path.cwd().name

    click.echo(f"Scaffolding project at {path} ...")
    try:
        run_copy(
            str(template_dir),
            str(dest),
            defaults=defaults,
            data={"project_name": default_name} if defaults else None,
            unsafe=True,  # allow local template path
        )
        click.echo(f"\nProject created at {dest}/")
        click.echo("Next steps:")
        click.echo(f"  cd {dest}")
        click.echo("  cp .env.example .env   # add your API keys")
        click.echo("  git init && git add -A && git commit -m 'Initial scaffold'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# r2 update
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--defaults", is_flag=True, help="Accept all Copier defaults.")
def update(defaults: bool) -> None:
    """Update framework files from the latest r2 template.

    Merges upstream changes with local edits. Requires a git repo with clean tree.
    """
    cmd = ["copier", "update"]
    if defaults:
        cmd.append("--defaults")

    click.echo("Updating framework files ...")
    result = subprocess.run(cmd)
    raise SystemExit(result.returncode)


# ---------------------------------------------------------------------------
# r2 rag — delegates to r2.rag.cli
# ---------------------------------------------------------------------------

cli.add_command(
    _LazyGroup(
        name="rag",
        import_path="r2.rag.cli:cli",
        help="RAG system — index, search, download, and query research literature.",
    )
)


# ---------------------------------------------------------------------------
# r2 skills — delegates to r2.skills_engine.cli
# ---------------------------------------------------------------------------

cli.add_command(
    _LazyGroup(
        name="skills",
        import_path="r2.skills_engine.cli:cli",
        help="Skills engine — semantic skill dispatch and management.",
    )
)
