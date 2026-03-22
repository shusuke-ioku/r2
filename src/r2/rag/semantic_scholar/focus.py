"""Focus modes for filtering Semantic Scholar results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FocusConfig:
    """Configuration for a focus mode."""

    name: str
    description: str
    venues: list[str] = field(default_factory=list)
    min_citations: int = 0
    year_range: tuple[int, int] | None = None
    publication_types: list[str] = field(default_factory=list)
    over_fetch_factor: int = 3  # fetch N*factor, then filter client-side

    def matches(self, paper) -> bool:
        """Check if a paper passes this focus filter."""
        # Citation floor
        if paper.citation_count < self.min_citations:
            return False

        # Year range
        if self.year_range and paper.year:
            if paper.year < self.year_range[0] or paper.year > self.year_range[1]:
                return False

        # Publication type
        if self.publication_types:
            if not any(t in paper.publication_types for t in self.publication_types):
                # Be lenient: if paper has no type info, let it through
                if paper.publication_types:
                    return False

        # Venue filtering (case-insensitive substring match)
        if self.venues:
            paper_venue = (paper.venue or "").lower()
            pub_venue = (paper.publication_venue or "").lower()
            combined = f"{paper_venue} {pub_venue}"
            if not any(v.lower() in combined for v in self.venues):
                return False

        return True


# Top political science and economics journals
_TOP_JOURNALS = [
    # Political science
    "American Political Science Review",
    "American Journal of Political Science",
    "Journal of Politics",
    "Comparative Political Studies",
    "World Politics",
    "International Organization",
    "British Journal of Political Science",
    "Annual Review of Political Science",
    "Political Analysis",
    "Political Science Research and Methods",
    "Journal of Conflict Resolution",
    "Comparative Politics",
    "Political Geography",
    "European Journal of Political Research",
    "Journal of Peace Research",
    "Journal of European Public Policy",
    # Economics
    "American Economic Review",
    "Quarterly Journal of Economics",
    "Journal of Political Economy",
    "Econometrica",
    "Review of Economic Studies",
    "Review of Economics and Statistics",
    "Journal of Economic Literature",
    "Economic Journal",
    "Journal of the European Economic Association",
    "Journal of Development Economics",
    "Journal of Economic History",
    "Explorations in Economic History",
    # Interdisciplinary / History
    "Journal of Economic Growth",
    "Journal of Economic Perspectives",
    "Journal of Comparative Economics",
]


FOCUS_MODES: dict[str, FocusConfig] = {
    "broad": FocusConfig(
        name="broad",
        description="No filters (default)",
    ),
    "top_journals": FocusConfig(
        name="top_journals",
        description="Top political science and economics journals, 10+ citations",
        venues=_TOP_JOURNALS,
        min_citations=10,
        publication_types=["JournalArticle"],
    ),
    "classical": FocusConfig(
        name="classical",
        description="Seminal works (200+ citations, 1950-2015)",
        min_citations=200,
        year_range=(1950, 2015),
    ),
    "recent": FocusConfig(
        name="recent",
        description="Recent papers (2020-2026), no citation floor",
        year_range=(2020, 2026),
    ),
}
