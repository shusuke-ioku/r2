"""Data types for Semantic Scholar API responses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class S2Author:
    """A Semantic Scholar author."""

    author_id: str
    name: str

    @classmethod
    def from_api(cls, data: dict) -> S2Author:
        return cls(
            author_id=data.get("authorId") or "",
            name=data.get("name") or "Unknown",
        )


@dataclass
class S2Paper:
    """A paper from Semantic Scholar."""

    paper_id: str
    title: str
    year: int | None = None
    abstract: str | None = None
    venue: str = ""
    publication_venue: str = ""
    citation_count: int = 0
    authors: list[S2Author] = field(default_factory=list)
    external_ids: dict[str, str] = field(default_factory=dict)
    url: str = ""
    open_access_pdf: str | None = None
    publication_types: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> S2Paper:
        authors = [S2Author.from_api(a) for a in (data.get("authors") or [])]
        ext_ids = data.get("externalIds") or {}
        oa = data.get("openAccessPdf") or {}
        pub_venue = data.get("publicationVenue") or {}

        return cls(
            paper_id=data.get("paperId") or "",
            title=data.get("title") or "Untitled",
            year=data.get("year"),
            abstract=data.get("abstract"),
            venue=data.get("venue") or "",
            publication_venue=pub_venue.get("name") or "" if isinstance(pub_venue, dict) else "",
            citation_count=data.get("citationCount") or 0,
            authors=authors,
            external_ids=ext_ids,
            url=data.get("url") or "",
            open_access_pdf=oa.get("url") if isinstance(oa, dict) else None,
            publication_types=data.get("publicationTypes") or [],
        )

    @property
    def first_author(self) -> str:
        if not self.authors:
            return "Unknown"
        return self.authors[0].name.split()[-1]  # last name

    @property
    def author_str(self) -> str:
        if not self.authors:
            return "Unknown"
        if len(self.authors) == 1:
            return self.authors[0].name
        if len(self.authors) == 2:
            return f"{self.authors[0].name} and {self.authors[1].name}"
        return f"{self.authors[0].name} et al."

    @property
    def citation(self) -> str:
        """Short citation: Author (Year)."""
        year = self.year or "n.d."
        return f"{self.first_author} ({year})"

    def format_short(self) -> str:
        """One-line summary."""
        cites = f"[{self.citation_count} cites]" if self.citation_count else ""
        venue = f" — {self.venue}" if self.venue else ""
        return f"{self.author_str} ({self.year or 'n.d.'}). {self.title}{venue} {cites}"

    def format_detail(self) -> str:
        """Full detail with abstract."""
        lines = [
            f"**{self.title}**",
            f"Authors: {self.author_str}",
            f"Year: {self.year or 'n.d.'}",
        ]
        if self.venue:
            lines.append(f"Venue: {self.venue}")
        lines.append(f"Citations: {self.citation_count}")
        if self.external_ids.get("DOI"):
            lines.append(f"DOI: {self.external_ids['DOI']}")
        lines.append(f"S2 ID: {self.paper_id}")
        if self.url:
            lines.append(f"URL: {self.url}")
        if self.open_access_pdf:
            lines.append(f"PDF: {self.open_access_pdf}")
        lines.append("")
        if self.abstract:
            lines.append(f"Abstract: {self.abstract}")
        else:
            lines.append("(No abstract available)")
        return "\n".join(lines)


@dataclass
class S2Citation:
    """A citation link between two papers."""

    citing_paper: S2Paper
    context: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict, key: str = "citingPaper") -> S2Citation:
        paper_data = data.get(key) or {}
        return cls(
            citing_paper=S2Paper.from_api(paper_data),
            context=data.get("contexts") or [],
        )
