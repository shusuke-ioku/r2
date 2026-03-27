"""r2 CLI — AI-driven research environment."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import click

from r2 import __version__


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GITHUB_REPO = "https://github.com/shusuke-ioku/r2.git"
# _subdirectory is declared in the repo-root copier.yml, so copier
# handles it automatically when cloning from the git URL.


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


def _resolve_template_source() -> str:
    """Return the best available template source.

    Prefers the GitHub repo (enables copier version tracking and ``r2 update``).
    Falls back to the bundled template directory when offline or repo is
    unreachable.
    """
    import subprocess

    try:
        subprocess.run(
            ["git", "ls-remote", _GITHUB_REPO, "HEAD"],
            capture_output=True, timeout=10, check=True,
        )
        return _GITHUB_REPO
    except Exception:
        local = _find_template_dir()
        if local is not None:
            return str(local)
        raise click.ClickException(
            "Cannot reach the r2 GitHub repo and no bundled template found."
        )


def _run_init(dest: Path, *, defaults: bool, data: dict | None = None) -> None:
    """Core init logic shared by ``r2 init`` and the ``r2 update`` fallback."""
    import shutil

    from copier import run_copy

    existing = dest.exists() and any(dest.iterdir())

    # --- back up user files ---
    backup_files = [".gitignore", "CLAUDE.md"]
    backups: dict[str, bytes] = {}
    if existing:
        for fname in backup_files:
            fp = dest / fname
            if fp.exists():
                backups[fname] = fp.read_bytes()

        claude_dir = dest / ".claude"
        if claude_dir.exists():
            backup_claude = dest / ".claude-backup-r2-init"
            if backup_claude.exists():
                shutil.rmtree(backup_claude)
            shutil.copytree(claude_dir, backup_claude)

    # --- resolve template source ---
    src = _resolve_template_source()
    is_git = src.startswith("https://") or src.startswith("git@")
    copy_kwargs: dict = dict(
        defaults=defaults,
        data=data,
        unsafe=True,
        overwrite=True,
    )
    if is_git:
        copy_kwargs["vcs_ref"] = "HEAD"

    try:
        run_copy(src, str(dest), **copy_kwargs)
    except Exception as e:
        # If git source failed, retry with bundled template
        if is_git:
            local = _find_template_dir()
            if local is not None:
                click.echo("Git source failed, using bundled template ...")
                copy_kwargs.pop("vcs_ref", None)
                run_copy(str(local), str(dest), **copy_kwargs)
            else:
                raise click.ClickException(f"Template copy failed: {e}")
        else:
            raise click.ClickException(f"Template copy failed: {e}")

    # --- write .copier-answers.yml for version tracking ---
    # Copier 9.x with _subdirectory doesn't always write this file, so we
    # create it ourselves to enable `r2 update` via `copier run_update`.
    if is_git:
        import yaml  # bundled with copier's deps

        answers = {
            "_src_path": _GITHUB_REPO,
            "_commit": "HEAD",
        }
        if data:
            answers.update(data)
        answers_path = dest / ".copier-answers.yml"
        if not answers_path.exists():
            answers_path.write_text(
                "# This file is auto-generated by r2 init. Do not edit.\n"
                + yaml.dump(answers, default_flow_style=False)
            )

    # --- clean up empty Jinja outputs ---
    for candidate in [dest / "paper" / "paper.typ", dest / "talk" / "slides.typ"]:
        if candidate.exists() and candidate.stat().st_size == 0:
            candidate.unlink()
            if candidate.parent.exists() and not any(candidate.parent.iterdir()):
                candidate.parent.rmdir()

    # --- restore user files ---
    restored: list[str] = []
    for fname, content in backups.items():
        (dest / fname).write_bytes(content)
        restored.append(fname)

    if existing:
        backup_claude = dest / ".claude-backup-r2-init"
        if backup_claude.exists():
            template_dir = _find_template_dir()
            _template_claude = template_dir / ".claude" if template_dir else None
            for item in backup_claude.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(backup_claude)
                    dest_file = dest / ".claude" / rel
                    # Restore files not provided by the template
                    if _template_claude is None or not (_template_claude / rel).exists():
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_file)
                        restored.append(f".claude/{rel}")
            shutil.rmtree(backup_claude)

    return restored


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
    dest = Path(path).resolve()
    default_name = dest.name if dest.name != "." else Path.cwd().name
    existing = dest.exists() and any(dest.iterdir())

    if existing:
        click.echo(f"Adding r2 framework to existing project at {path} ...")
    else:
        click.echo(f"Scaffolding project at {path} ...")

    restored = _run_init(
        dest,
        defaults=defaults,
        data={"project_name": default_name} if defaults else None,
    )

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

    If the project has a .copier-answers.yml (created by ``r2 init``),
    copier performs a three-way merge of upstream changes with your local
    edits. Otherwise falls back to a fresh ``r2 init .`` (safe — existing
    content is preserved).
    """
    dest = Path.cwd().resolve()
    answers_file = dest / ".copier-answers.yml"

    if answers_file.exists():
        from copier import run_update as _run_update

        click.echo("Updating framework files (three-way merge) ...")
        try:
            _run_update(
                str(dest),
                defaults=defaults,
                unsafe=True,
                overwrite=True,
            )
        except Exception as e:
            click.echo(f"Error during copier update: {e}", err=True)
            click.echo("Falling back to r2 init . ...")
            _run_init(dest, defaults=True)
    else:
        click.echo(
            "No .copier-answers.yml found — running r2 init . to apply latest "
            "template (safe: existing content is preserved)."
        )
        _run_init(dest, defaults=True)

    click.echo("Update complete.")


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
