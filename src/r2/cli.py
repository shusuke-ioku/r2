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
    """Scaffold a new research project at PATH.

    Safe to run on existing projects — never overwrites your files.
    Framework files (.claude/agents, skills, commands, rules) are added;
    existing content (paper/, analysis/, notes/) is never touched.
    """
    from copier import run_copy

    template_dir = _find_template_dir()
    if template_dir is None:
        click.echo("Error: could not locate the r2 template directory.", err=True)
        raise SystemExit(1)

    dest = Path(path).resolve()
    default_name = dest.name if dest.name != "." else Path.cwd().name
    existing = dest.exists() and any(dest.iterdir())

    if existing:
        click.echo(f"Adding r2 framework to existing project at {path} ...")
    else:
        click.echo(f"Scaffolding project at {path} ...")

    # Back up files that Copier would overwrite
    backup_files = [".gitignore", "CLAUDE.md"]
    backups: dict[str, bytes] = {}
    if existing:
        for fname in backup_files:
            fp = dest / fname
            if fp.exists():
                backups[fname] = fp.read_bytes()

        # Preserve everything in .claude/ that isn't part of the template
        claude_dir = dest / ".claude"
        if claude_dir.exists():
            import shutil
            backup_claude = dest / ".claude-backup-r2-init"
            if backup_claude.exists():
                shutil.rmtree(backup_claude)
            shutil.copytree(claude_dir, backup_claude)

    try:
        run_copy(
            str(template_dir),
            str(dest),
            defaults=defaults,
            data={"project_name": default_name} if defaults else None,
            unsafe=True,
            overwrite=True,  # Copier needs this to write into existing dirs
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    # Remove empty files produced by Jinja conditionals that rendered to nothing
    for candidate in [dest / "paper" / "paper.typ", dest / "talk" / "slides.typ"]:
        if candidate.exists() and candidate.stat().st_size == 0:
            candidate.unlink()
            # Remove empty parent dir too
            if candidate.parent.exists() and not any(candidate.parent.iterdir()):
                candidate.parent.rmdir()

    # Restore backed-up files (user's originals take priority)
    restored = []
    for fname, content in backups.items():
        fp = dest / fname
        fp.write_bytes(content)
        restored.append(fname)

    # Merge back non-template files from .claude/ backup
    if existing:
        backup_claude = dest / ".claude-backup-r2-init"
        if backup_claude.exists():
            import shutil
            # Restore files that the template doesn't provide
            # (e.g., settings.local.json, user's custom files)
            _template_claude = template_dir / ".claude"
            for item in backup_claude.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(backup_claude)
                    template_equiv = _template_claude / rel
                    dest_file = dest / ".claude" / rel
                    if not template_equiv.exists():
                        # Not a template file — restore the user's version
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_file)
                        restored.append(f".claude/{rel}")
            shutil.rmtree(backup_claude)

    if existing:
        click.echo(f"\nr2 framework added to {dest}/")
        if restored:
            click.echo(f"Preserved existing files: {', '.join(restored)}")
        click.echo("Next steps:")
        click.echo("  cp .env.example .env   # add your API keys")
    else:
        click.echo(f"\nProject created at {dest}/")
        click.echo("Next steps:")
        click.echo(f"  cd {dest}")
        click.echo("  cp .env.example .env   # add your API keys")
        click.echo("  git init && git add -A && git commit -m 'Initial scaffold'")


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
