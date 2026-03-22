# Deep Research Report Template

Use this exact structure for every report. Every section is required. If a
section has nothing to report, explain why rather than omitting it.

---

## Template

```markdown
# Literature Survey: [Topic]

**Date**: YYYY-MM-DD
**Research question**: [The question that motivated this survey]
**Scope**: [Disciplines, time period, theoretical/empirical, geographic focus]
**Search strategy**: [Brief summary of queries run, databases used, focus modes]

## Key Themes

Organize the literature into 3-6 thematic clusters. Each theme gets a
subsection. Within each theme:

- State the theme as a claim or finding (not "Theme 1: Economic shocks")
- Summarize what the literature collectively says
- Note agreement and disagreement across papers
- Cite specific papers with author-year format

### [Theme title as a claim, e.g., "Economic shocks increase support for extremist parties"]

[Synthesis paragraph(s). Cite as Author (Year) or Author1 & Author2 (Year).]

### [Next theme...]

[...]

## Mechanisms & Causal Pathways

What causal mechanisms does the literature propose? How well-identified are
they? Note which mechanisms have strong empirical support vs. theoretical
speculation.

## Debates & Tensions

Where does the literature disagree? What are the unresolved questions?
Characterize both sides fairly.

## Gaps & Opportunities

What remains unstudied or underexplored? Where could new work contribute?
Be specific -- "more research is needed" is not useful. Instead: "No study
has examined [X] using [Y] in the context of [Z]."

## Connection to This Project

How do these findings relate to the user's paper? What should be cited,
what challenges the argument, what supports it, what suggests new analyses?

Be specific about where in the paper these connections matter (e.g.,
"relevant for the mechanism discussion in Section 3" or "challenges the
identification assumption that...").

## Papers to Index for RAG

Papers and books discovered through external search that are NOT yet in
the local Zotero library but should be acquired and indexed for full-text
analysis. For each entry:

| Priority | Author(s) | Year | Title | Why index? | Identifier |
|----------|-----------|------|-------|------------|------------|
| HIGH | ... | ... | ... | [Why this paper matters for the project] | DOI or S2 ID |
| MEDIUM | ... | ... | ... | ... | ... |
| LOW | ... | ... | ... | ... | ... |

Priority levels:
- **HIGH**: Directly relevant to the paper's argument or identification;
  should read in full before next revision
- **MEDIUM**: Provides useful context or methodology; worth indexing for
  future reference
- **LOW**: Tangentially relevant; index if time permits

If no new papers need indexing, explain why (e.g., "the local library
already covers this topic comprehensively").

## Bibliography

Full list of all sources cited in this report, formatted as:

- Author(s) (Year). Title. *Venue*. [DOI if available]

Sort alphabetically by first author surname.
```

---

## Guidance

### On the "Papers to Index" section

This is the most actionable part of the report. The user can take this list
and add these papers to Zotero, then re-index RAG to make them available
for full-text search. Prioritization helps the user decide what to read
first.

To determine whether a paper is already indexed locally:
- Check if the citekey appeared in `rag_search` results
- If unsure, mention it and let the user verify

For each paper, include enough identifying information (DOI, Semantic
Scholar ID) that the user can find and acquire it without additional
searching.

### On thematic organization

Bad: "Smith (2020) studies trade shocks. Jones (2019) studies immigration.
Lee (2021) studies financial crises."

Good: "Economic shocks of various kinds -- trade (Smith 2020), immigration
(Jones 2019), financial crises (Lee 2021) -- consistently increase support
for radical parties, though the magnitude varies with institutional context."

### On the connection to this project

The user's project topic is described in CLAUDE.md and the paper's abstract.
Any survey should connect back to the paper's core argument, mechanisms,
and empirical strategy. Read the abstract before writing this section.
