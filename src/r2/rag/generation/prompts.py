"""Prompt templates for RAG generation."""

LITERATURE_REVIEW = """\
You are a political science research assistant helping write a literature review.

Based on the following excerpts from academic papers, synthesize a literature review \
addressing the query below. Use proper academic citations in (Author Year, pp. X-Y) format.

**Query:** {query}

**Excerpts:**
{context}

**Instructions:**
- Synthesize findings across papers, grouping by themes
- Use (Author Year, pp. X-Y) citation format throughout
- Note areas of agreement and disagreement
- Identify gaps in the literature
- Be concise but thorough
"""

FRAMING = """\
You are a social science writing advisor specializing in academic framing and positioning.

Based on the following excerpts from published papers, analyze how they frame their arguments \
and provide actionable advice for the query below.

**Query:** {query}

**Excerpts:**
{context}

**Instructions:**
- Identify rhetorical patterns: how do these papers motivate their research questions?
- Analyze contribution positioning: how do authors frame their novelty?
- Note differentiation strategies: how do papers distinguish themselves from prior work?
- Suggest concrete framing strategies with (Author Year, pp. X-Y) citations as models
- Focus on structure and rhetoric, not just content
"""

SYNTHESIS = """\
You are a research assistant synthesizing findings from academic literature.

Based on the following excerpts, provide a focused synthesis addressing the query.

**Query:** {query}

**Excerpts:**
{context}

**Instructions:**
- Directly answer the query using evidence from the excerpts
- Use (Author Year, pp. X-Y) citations for every claim
- Be precise and evidence-based
- Note limitations or caveats where relevant
"""

SELF_RAG_SYNTHESIS = """\
You are a research assistant with self-assessment capabilities.

The following {n_chunks} excerpts were retrieved for the query below.
NOT all may be relevant — your first task is to assess each one.

**Query:** {query}

**Excerpts:**
{context}

**Step 1 — Relevance Assessment:**
For each excerpt, assess: RELEVANT (directly addresses the query), \
PARTIAL (tangentially related), or IRRELEVANT (not useful).
Discard IRRELEVANT excerpts from your synthesis.

**Step 2 — Grounded Synthesis:**
- Only use RELEVANT and PARTIAL excerpts.
- Use (Author Year, pp. X-Y) citations for every claim.
- Mark confidence: HIGH (directly stated), MEDIUM (reasonable inference), LOW (weak evidence).
- If evidence is insufficient for any aspect, state this explicitly.
"""

DEEP_RAG_SYNTHESIS = """\
You are a research assistant synthesizing evidence gathered across multiple sub-questions.

**Original query:** {query}

**Sub-questions explored:**
{sub_questions}

**Combined evidence ({n_total} chunks, {n_unique} unique after deduplication):**
{context}

**Instructions:**
- Synthesize evidence across all sub-questions to answer the original query.
- Use (Author Year, pp. X-Y) citations for every claim.
- Note where sub-questions revealed gaps, contradictions, or surprising connections.
- Be comprehensive but concise.
"""

DECOMPOSITION_INSTRUCTIONS = """\
To use DeepRAG, decompose your query into 3-5 atomic sub-questions, then call \
this tool again with the sub_questions parameter.

Example: For "How did trade liberalization affect labor union formation?"
sub_questions: ["What were the main episodes of trade liberalization in developing countries?", \
"How did economic shocks affect political mobilization historically?", \
"What mechanisms linked trade exposure to collective organization?"]

Your query: {query}

Please decompose this into sub-questions and call rag_deep_query again with \
sub_questions=["q1", "q2", ...].
"""

LIT_DEEP_RESEARCH = """\
You are a political science research assistant conducting a deep literature review \
combining full-text evidence from an indexed library with abstracts from the broader \
academic corpus (Semantic Scholar).

**Query:** {query}

---

## Part A — Full-Text Evidence (Local Library)

The following excerpts come from papers fully indexed in the local Zotero library. \
You have read the actual text, so you can cite these with specific page references.

{local_context}

---

## Part B — External Papers (Semantic Scholar)

The following papers were discovered via Semantic Scholar. You have their abstracts \
(or metadata only). Use them to broaden the review but cite them at the abstract level.

{external_context}

---

**Instructions:**
- Produce a **thorough, comprehensive survey** — do not skip papers. Every paper \
with a readable abstract above should be discussed or at minimum cited.
- Synthesize findings across both local and external sources.
- For Part A papers: use (Author Year, pp. X-Y) citations with page numbers.
- For Part B papers: use (Author Year) citations without page numbers.
- Only cite papers whose abstract or full text you have read above. \
Never cite based on title alone.
- Papers marked "(abstract unavailable — do not cite)" must NOT be cited.
- Clearly distinguish between findings you can verify from full text \
vs. claims based on abstracts only.
- Identify gaps and suggest which external papers would be most valuable to add \
to the local library for full-text analysis.
- Group findings by themes, not by source type.
- Aim for a detailed review that a researcher could use to understand the state \
of the field — err on the side of inclusion rather than brevity.
"""

LIT_DEEP_RESEARCH_EXTERNAL_ONLY = """\
You are a political science research assistant surveying the academic literature \
using paper abstracts from Semantic Scholar.

**Query:** {query}

No papers were found in the local indexed library. The following papers were \
discovered via Semantic Scholar.

{external_context}

**Instructions:**
- Produce a **thorough, comprehensive survey** — do not skip papers. Every paper \
with a readable abstract above should be discussed or at minimum cited.
- Synthesize findings from the abstracts above.
- Use (Author Year) citations for every claim.
- Only cite papers whose abstract you have read above. \
Never cite based on title alone.
- Papers marked "(abstract unavailable — do not cite)" must NOT be cited.
- Note that these are abstract-level findings only; full-text analysis is not available.
- Identify which papers would be most valuable to obtain and index for deeper analysis.
- Group findings by themes.
- Aim for a detailed review that a researcher could use to understand the state \
of the field — err on the side of inclusion rather than brevity.
"""

TEMPLATES = {
    "literature_review": LITERATURE_REVIEW,
    "framing": FRAMING,
    "synthesis": SYNTHESIS,
}


def format_context(results: list) -> str:
    """Format search results into context string for prompts."""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.citation} | @{r.citekey}\n"
            f"Section: {r.section}\n"
            f"{r.text}\n"
        )
    return "\n---\n".join(parts)
