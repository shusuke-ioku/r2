"""r2 CLI — AI-driven research environment."""

from __future__ import annotations

import importlib
import shutil
from pathlib import Path

import click

from r2 import __version__


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Files that should never be overwritten once they exist (user content).
_SKIP_IF_EXISTS = {"paper/paper.typ", "paper/style.typ", "talk/slides.typ", "ref.bib"}


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

def _find_template_dir() -> Path:
    """Locate the template directory shipped with r2."""
    pkg_dir = Path(__file__).resolve().parent
    candidates = [
        pkg_dir / "template",  # bundled inside package
        pkg_dir.parent.parent / "template",  # editable install / dev
    ]
    for c in candidates:
        if c.is_dir() and any(c.iterdir()):
            return c
    raise click.ClickException("Cannot locate the r2 template directory.")


def _template_files(template_dir: Path) -> dict[str, Path]:
    """Return {relative_path: absolute_path} for every file in the template."""
    result = {}
    for p in sorted(template_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(template_dir))
            # Skip copier metadata and Jinja templates (legacy)
            if rel == "copier.yml" or rel.endswith(".jinja"):
                continue
            result[rel] = p
    return result


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
def init(path: str) -> None:
    """Scaffold a new research project at PATH.

    Copies framework files (.claude/agents, skills, commands, rules).
    Never overwrites existing user content (paper.typ, ref.bib, etc.).

    To update an existing project, use the /update-r2 slash command
    inside Claude Code — it fetches the latest template from GitHub
    and merges changes intelligently.
    """
    dest = Path(path).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    existing = any(dest.iterdir())

    if existing:
        click.echo(f"Adding r2 framework to existing project at {path} ...")
    else:
        click.echo(f"Scaffolding project at {path} ...")

    template_dir = _find_template_dir()
    files = _template_files(template_dir)
    created, skipped = 0, 0

    for rel, src in files.items():
        dst = dest / rel

        if dst.exists():
            if rel in _SKIP_IF_EXISTS:
                skipped += 1
                continue
            if existing:
                # Don't overwrite user's existing framework files on re-init
                skipped += 1
                continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created += 1

    click.echo(f"\n  {created} files created, {skipped} existing files preserved.")

    if not existing:
        click.echo(f"\nProject created at {dest}/")
        click.echo("Next steps:")
        click.echo(f"  cd {dest}")
        click.echo("  cp .env.example .env   # add your API keys")
        click.echo("  git init && git add -A && git commit -m 'Initial scaffold'")
    else:
        click.echo(f"\nr2 framework added to {dest}/")
        click.echo("Next steps:")
        click.echo("  cp .env.example .env   # add your API keys")

    click.echo("\nTo update framework files later, run /update-r2 in Claude Code.")


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
