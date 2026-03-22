"""Parse ref.bib to extract metadata and PDF paths per citekey."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import bibtexparser


@dataclass
class BibEntry:
    citekey: str
    author: str
    title: str
    year: str
    journal: str
    pdf_path: Path | None
    keywords: list[str]

    @property
    def short_cite(self) -> str:
        """Format as 'Author (Year)' for citations."""
        if self.author:
            # Take first author surname
            first = self.author.split(" and ")[0].split(",")[0].strip()
            et_al = " et al." if " and " in self.author else ""
            return f"{first}{et_al} ({self.year})"
        return f"({self.citekey}, {self.year})"


def _extract_first_pdf(file_field: str) -> Path | None:
    """Extract first valid PDF path from bib file field.

    Handles semicolon-separated multiple paths.
    """
    if not file_field:
        return None
    # Split on semicolons for multiple file entries
    candidates = file_field.split(";")
    for candidate in candidates:
        candidate = candidate.strip()
        # Remove any Zotero type prefix like "Full Text:"
        if ":" in candidate and not candidate.startswith("/"):
            candidate = candidate.split(":", 1)[1].strip()
        p = Path(candidate)
        if p.suffix.lower() == ".pdf" and p.exists():
            return p
    return None


def parse_bib(bib_path: Path) -> dict[str, BibEntry]:
    """Parse a .bib file and return {citekey: BibEntry} dict."""
    with open(bib_path, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f)

    entries: dict[str, BibEntry] = {}
    for entry in bib_db.entries:
        citekey = entry.get("ID", "")
        if not citekey:
            continue

        pdf_path = _extract_first_pdf(entry.get("file", ""))
        keywords_raw = entry.get("keywords", "")
        keywords = [k.strip().lower() for k in keywords_raw.split(",") if k.strip()]

        entries[citekey] = BibEntry(
            citekey=citekey,
            author=entry.get("author", ""),
            title=_clean_latex(entry.get("title", "")),
            year=entry.get("year", ""),
            journal=entry.get("journal", ""),
            pdf_path=pdf_path,
            keywords=keywords,
        )

    return entries


def _clean_latex(text: str) -> str:
    """Remove common LaTeX markup from bib fields."""
    # Remove {{ }} wrappers
    text = re.sub(r"\{\{(.+?)\}\}", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    # Remove common LaTeX accents
    text = re.sub(r"\\['\"`^~=.](\\?\w)", r"\1", text)
    return text.strip()
