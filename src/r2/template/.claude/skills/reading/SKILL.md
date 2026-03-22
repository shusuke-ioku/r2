---
name: reading
description: >
  Critically reads social science papers, books, or chapters and generates
  structured, decision-relevant feedback for this project. Trigger aggressively:
  activate whenever the user asks to read, review, critique, summarize, or
  extract implications from any source -- including phrases like "read this
  paper," "what does X argue," "summarize this for me," "how should I cite X,"
  "does this paper help my argument," "review this chapter," "what are the
  implications of X for my project," "is this paper any good," or any request
  that involves evaluating an external scholarly work. Even a casual "take a
  look at this" about an academic source should trigger this skill. If in doubt,
  trigger -- the user never wants a bare summary.
---

# Critical Reader

## Why This Skill Exists

The user already has abstracts and can skim papers. What they cannot do quickly
is figure out how a source changes *their* project -- what to keep, revise, or
drop in their own manuscript, identification strategy, and data. Every output
from this skill must answer that question. A summary without project-level
implications is wasted effort.

## Workflow

### 1. Read the source thoroughly

Use RAG tools (`rag_search`, `rag_query`, `lit_search`, `lit_paper`,
`lit_deep_research`) or read the PDF directly. At minimum read the abstract,
introduction, theory/mechanism section, identification/methods section, and
conclusion. Skipping the methods section is not acceptable -- identification
strategy is the core of what needs evaluation.

If the source is a book or long chapter, read the introduction, the most
relevant substantive chapter, and the conclusion. State explicitly which parts
you read.

Do not critique based on a title, a second-hand description, or memory. If you
cannot access the text, tell the user and stop.

### 2. Evaluate against the critique framework

Open `references/critique-framework.md` and work through each lens:

1. **Question & contribution** -- Is the question clear? What exactly is new?
2. **Theory & mechanism** -- Are causal pathways specified and testable?
3. **Design & identification** -- What assumptions drive the result? What breaks them?
4. **Measurement** -- Do the variables actually capture the constructs claimed?
5. **Inference & interpretation** -- Do conclusions stay within what the design supports?
6. **Relevance to this project** -- What is directly usable, adaptable, or a warning?

The framework file has detailed sub-questions. Use them. Do not skip lenses
because the paper "seems solid" -- prestigious journals and famous authors
produce work with identifiable limitations just like everyone else. Evaluate
the evidence on its merits.

### 3. Produce structured output

Use the template in `references/feedback-template.md`. Every section is
required. The template has guidance on what belongs in each section -- follow it.

The most important section is **Actionable Edits**. For each proposed change,
identify the specific target:

- A section of `paper/paper.typ` (e.g., "Section 3, paragraph on mechanism")
- A script in `analysis/scripts/` (e.g., "add control in 30_main_results.R")
- An entry in `paper/notes/lit.md`
- A codebook update in `analysis/data/codebook.md`

If a source has no implications for the project, say so explicitly and explain
why. That is a valid and useful output.

### 4. Connect to the literature map

Check whether the source is already covered in `paper/notes/lit.md`. If
it is not and it is relevant, note that `lit.md` needs updating. If it is
already there, check whether the existing characterization is accurate given
your fresh reading.

## Citation Rules

- **Cite only what you have read:** Read the source thoroughly before recommending it for citation. Never cite from title alone.
- **Zotero only:** Use `.claude/scripts/zotero_add.py` or `lit_download` for missing references. Never edit `ref.bib` directly.
- **Never self-cite:** The user's own paper is not external literature. Never cite it as a source.

## Reasoning Principles

**Why not stop at summary?** The user can get a summary from the abstract.
They need to know what the source means for their specific project. Read
the paper's abstract in `paper/paper.typ` for context. Force yourself to
answer "so what?" for every finding.

**Why not defer to prestigious sources?** A paper in the APSR can have a weak
identification strategy. A working paper can have a brilliant one. Evaluate the
design, not the venue. The user needs honest assessment to decide what to
incorporate.

**Why flag uncertainty?** The user's paper will be reviewed by experts who will
notice if a borrowed claim rests on shaky evidence. Better to flag weakness now
than have a reviewer do it later. When evidence is ambiguous, say so.

**Why require causal scrutiny?** This project makes causal claims (radical
elites -> democratic erosion). Any source the user cites for causal reasoning
must itself have defensible causal identification, or the user needs to know
the limitation and frame accordingly.

## Common Failure Modes

**Recapping without recommending.** Every paragraph of output should connect
to the project. If you find yourself writing three paragraphs of summary,
stop and convert each point into a "keep / revise / drop" judgment.

**Vague action items.** "Consider incorporating this insight" is not
actionable. "Add a paragraph in Section 2 of paper.typ discussing X as a
competing mechanism, citing Y (2019, p. 34)" is actionable.

**Overlooking measurement issues.** Measurement problems are the most common
real-world threat to validity in historical political economy. Scrutinize how
key variables are operationalized, especially when the source's context
differs from the user's empirical context.

**Treating the user's own paper as a source.** The project's own paper is not
external literature. The literature review surveys external work only.
