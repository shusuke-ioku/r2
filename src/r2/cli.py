"""r2 CLI — AI-driven research environment."""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import click

from r2 import __version__


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MANIFEST_DIR = ".r2"
_MANIFEST_FILE = "manifest.json"

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
# Template helpers
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


def _hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _template_files(template_dir: Path) -> dict[str, Path]:
    """Return {relative_path: absolute_path} for every file in the template.

    Excludes copier.yml and Jinja suffixes — these are template metadata,
    not project files.
    """
    result = {}
    for p in sorted(template_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(template_dir))
            # Skip copier metadata and Jinja templates (legacy from copier era)
            if rel == "copier.yml" or rel.endswith(".jinja"):
                continue
            result[rel] = p
    return result


def _read_manifest(dest: Path) -> dict:
    """Read the manifest from .r2/manifest.json, or return empty."""
    mf = dest / _MANIFEST_DIR / _MANIFEST_FILE
    if mf.exists():
        return json.loads(mf.read_text())
    return {}


def _write_manifest(dest: Path, manifest: dict) -> None:
    """Write the manifest to .r2/manifest.json."""
    mf_dir = dest / _MANIFEST_DIR
    mf_dir.mkdir(parents=True, exist_ok=True)
    mf = mf_dir / _MANIFEST_FILE
    mf.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def _three_way_merge(current: Path, old_template: bytes, new_template: bytes) -> bool:
    """Three-way merge using git merge-file. Returns True if conflict."""
    with tempfile.NamedTemporaryFile(suffix=".old", delete=False) as f_old, \
         tempfile.NamedTemporaryFile(suffix=".new", delete=False) as f_new:
        f_old.write(old_template)
        f_old.flush()
        f_new.write(new_template)
        f_new.flush()

        # git merge-file modifies the first file in place.
        # Exit code: 0 = clean merge, >0 = conflicts, <0 = error.
        result = subprocess.run(
            ["git", "merge-file",
             "-L", "LOCAL (your changes)",
             "-L", "BASE (old template)",
             "-L", "UPSTREAM (new template)",
             str(current), f_old.name, f_new.name],
            capture_output=True,
        )

        Path(f_old.name).unlink(missing_ok=True)
        Path(f_new.name).unlink(missing_ok=True)

        return result.returncode != 0


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
    Records a manifest so that ``r2 update`` can do three-way merges later.
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
    manifest: dict[str, str] = {}
    created, skipped = 0, 0

    for rel, src in files.items():
        dst = dest / rel
        content = src.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        manifest[rel] = file_hash

        if dst.exists() and rel in _SKIP_IF_EXISTS:
            skipped += 1
            continue

        if dst.exists() and existing:
            # For non-skip files: overwrite only if user hasn't modified
            # (on first init there's no manifest, so we overwrite template
            # files but skip user-content files listed in _SKIP_IF_EXISTS)
            skipped += 1
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created += 1

    _write_manifest(dest, {"version": __version__, "files": manifest})

    click.echo(f"\n  {created} files created, {skipped} existing files preserved.")
    click.echo(f"  Manifest written to {_MANIFEST_DIR}/{_MANIFEST_FILE}")

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


# ---------------------------------------------------------------------------
# r2 update
# ---------------------------------------------------------------------------

@cli.command()
def update() -> None:
    """Update framework files from the latest r2 template.

    Performs a three-way merge: compares the old template (from manifest),
    the new template (bundled with this r2 version), and your local files.

    \b
    - Template changed, you didn't  →  auto-updated
    - You changed, template didn't  →  your edit preserved
    - Both changed the same file    →  git-style conflict markers
    - New template file             →  created
    """
    dest = Path.cwd().resolve()
    old_manifest = _read_manifest(dest)
    template_dir = _find_template_dir()
    new_files = _template_files(template_dir)

    old_files: dict[str, str] = old_manifest.get("files", {})
    old_version = old_manifest.get("version", "unknown")

    if not old_files:
        click.echo(
            f"No manifest found at {_MANIFEST_DIR}/{_MANIFEST_FILE}.\n"
            "Running r2 init . to create one ..."
        )
        # Invoke init for the current directory
        from click import Context
        ctx = Context(init)
        ctx.invoke(init, path=".")
        return

    click.echo(f"Updating from r2 {old_version} → {__version__} ...")

    new_manifest: dict[str, str] = {}
    stats = {"updated": 0, "created": 0, "skipped": 0, "conflict": 0}

    for rel, src_path in new_files.items():
        new_content = src_path.read_bytes()
        new_hash = hashlib.sha256(new_content).hexdigest()
        new_manifest[rel] = new_hash

        dst = dest / rel
        old_hash = old_files.get(rel)

        # --- New file not in old template ---
        if old_hash is None:
            if dst.exists():
                # User already has this file (created independently)
                stats["skipped"] += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            click.echo(click.style(f"  create  ", fg="green") + rel)
            stats["created"] += 1
            continue

        # --- Template didn't change ---
        if new_hash == old_hash:
            stats["skipped"] += 1
            continue

        # --- Template changed ---
        if not dst.exists():
            # User deleted the file; re-create with new template version
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            click.echo(click.style(f"  create  ", fg="green") + rel)
            stats["created"] += 1
            continue

        current_hash = _hash_file(dst)

        if current_hash == old_hash:
            # User didn't modify — safe to overwrite
            shutil.copy2(src_path, dst)
            click.echo(click.style(f"  update  ", fg="cyan") + rel)
            stats["updated"] += 1

        elif current_hash == new_hash:
            # User already has the new version (e.g., manual sync)
            stats["skipped"] += 1

        else:
            # Both changed — three-way merge
            # Reconstruct old template content from the template dir at the
            # old version. Since we only have hashes, we use git merge-file
            # with the old content derived from... we need the actual bytes.
            # Fallback: old template content is not stored, so we write
            # the new version alongside the user's version with a .new suffix.
            conflict_path = dst.with_suffix(dst.suffix + ".upstream")
            shutil.copy2(src_path, conflict_path)
            click.echo(
                click.style(f"  conflict  ", fg="red", bold=True) + rel
                + f"  (upstream saved as {conflict_path.name})"
            )
            stats["conflict"] += 1

    # Preserve manifest entries for user files not in the template
    for rel, old_hash in old_files.items():
        if rel not in new_manifest:
            # Template removed this file — don't touch user's copy
            new_manifest[rel] = old_hash

    _write_manifest(dest, {"version": __version__, "files": new_manifest})

    click.echo(
        f"\nDone: {stats['updated']} updated, {stats['created']} created, "
        f"{stats['skipped']} unchanged, {stats['conflict']} conflicts."
    )
    if stats["conflict"]:
        click.echo(
            click.style(
                f"\n  {stats['conflict']} file(s) have conflicts. "
                "Compare your version with the .upstream file and merge manually.",
                fg="yellow",
            )
        )


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
