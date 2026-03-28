---
name: writing
description: >
  Enforces precise, dense academic prose for this project's manuscript (paper/paper.typ).
  TRIGGER THIS SKILL whenever the user does ANY of the following: write prose, draft a
  section, rewrite or revise paragraphs, tighten language, improve sentences, fix
  overclaiming, polish the manuscript, rewrite for clarity, sharpen argument, condense
  text, edit the introduction, revise the literature review, draft contributions,
  format or fix citations, write equations, format or create tables, add figure captions,
  or anything that touches text quality in the paper. Also trigger when the user says
  "make this better," "clean this up," "this reads poorly," "too wordy," "tighten this,"
  "this overclaims," "fix the flow," or "rewrite." If the task involves paper/paper.typ
  prose, tables, or equations in any way, this skill applies---even if the user does not
  explicitly ask for writing help.
---

# Writer

Maximum intellectual impact per word. Every sentence earns its place.

## Three Principles

All writing rules derive from three principles: **density**, **flow**, and **calibration**. Internalize the reasoning behind each.

### Density

Pack every paragraph with substance. Strip every word that does not carry weight. A compact five-sentence paragraph beats a diffuse ten-sentence one.

**Match detail to context.** The introduction and contributions move the argument forward---details, caveats, and background belong in the body sections or footnotes, not here. When writing any section, ask: does the reader need this information _at this point_ to follow the argument? If not, cut it or move it downstream. The introduction should flow smoothly at the level of claims and evidence; methodological nuances, historical background, and qualifying caveats that interrupt that flow belong in the sections where they are directly relevant. Over-specifying in the wrong place is as damaging as under-specifying: it buries the signal and breaks the reader's momentum.

Why this matters: Reviewers form impressions within the first page. Filler signals that the author isn't sure what the point is. In a historical case study where the empirical contribution must speak loudly, loose prose buries the signal.

### Flow

Every sentence follows naturally from the one before. Every paragraph answers the question raised by the previous one. If a transition feels forced ("Turning now to..."), the structure is wrong---fix the structure, not the transition.

**Topic shifts:** When moving between sections or major ideas, state the argument or finding directly---never frame the shift as a question. A topic sentence like "The organizational surge also reshaped parliamentary politics" is stronger than "Did the organizational surge reshape parliamentary politics?" Questions defer the point; statements advance it.

Why this matters: Forced transitions are a symptom of disorganized argument, not a cosmetic problem. Readers who lose the thread stop trusting the analysis.

### Calibration

Match every claim precisely to the evidence. A local average treatment effect is not a universal law. A suggestive correlation is not a causal finding.

Why this matters: Reviewers will assume overclaiming unless verbs are precisely calibrated. "Documents" and "identifies" are strong enough when the identification strategy supports them. "Demonstrates a general mechanism" will get the paper desk-rejected. The narrower the evidence base, the more precise the verbs must be. Get the verb right.

## Workflow

### 1. Read context first

Read surrounding sections, the abstract, and contribution claims in `paper/paper.typ` before writing anything. Inconsistency between what the introduction promises and what the body delivers is the most common manuscript flaw, and it is entirely preventable by reading first.

**Context-aware writing:** Always consider what the reader already knows at the point you are writing. Do not re-introduce concepts, datasets, variables, or terminology that have already been explained earlier in the paper. Use short references ("organizational density," not "organizational density, the count of existing organizations per 100,000 population") for anything the reader has already encountered. The level of detail in an explanation should match its novelty to the reader at that specific location in the manuscript---first mention gets full explanation, subsequent mentions get none.

### 2. Map the argument chain

Identify what claim each paragraph needs to make. One idea per paragraph. If a paragraph serves two purposes, split it. If you cannot state a paragraph's point in one sentence, the paragraph needs restructuring, not more sentences.

### 3. Draft with the right mode

**Body paragraphs (lit review, theory, results, discussion):** Open every paragraph with a **topic sentence that states a claim**, not a literature summary. The most important claim goes in the first or second sentence. Then fill in evidence and citations. Readers skim topic sentences to follow the argument---if they summarize literature instead of making claims, the argument disappears.

- Bad: "Several scholars have studied the relationship between economic conditions and radical mobilization (Smith 2020; Jones 2021)."
- Good: "Peripheral status---not poverty---is the critical precondition for radical mobilization."

**Introduction and abstract: prioritize punch over structure.** The topic-sentence rule is suspended here. These sections sell the paper. Lead with the most arresting framing---a vivid fact, a striking puzzle, a bold claim. Hook the reader immediately, then deliver the argument. A punchy opening that makes a reviewer want to keep reading is worth more than a technically correct topic sentence that bores them. Write the intro as if the reader will stop after three sentences unless you give them a reason not to.

### 4. Apply prose standards

Load `references/prose-standards.md` for the full style rules on precision, calibration, citation practice, and introduction structure. Read it whenever writing or revising prose---it contains the detailed rules that keep the manuscript consistent.

### 5. Apply table and notation standards

Load `references/table-and-notation-standards.md` when writing tables, figure captions, or equations. The paper's tables follow a strict Typst format; deviations break visual consistency and signal carelessness to reviewers.

### 6. Cut ruthlessly

Remove any sentence that does not advance the paragraph's single point. Test: if cutting a sentence changes nothing about what the reader understands, it was filler.

### 7. Humanizer pass

After drafting or revising, scan every paragraph for AI-writing tells (full pattern catalog in `../humanizer/SKILL.md`). The most damaging patterns in academic prose:

- **Significance inflation:** "pivotal," "crucial," "fundamental," "groundbreaking," "serves as a testament" --- delete or replace with precise verbs
- **Superficial -ing phrases:** "highlighting," "underscoring," "emphasizing," "reflecting," "showcasing" --- these add fake depth; cut them or rewrite as main clauses with actual content
- **Copula avoidance:** "serves as," "stands as," "functions as" --- just write "is"
- **Rule of three:** forcing ideas into triads ("innovation, inspiration, and insights") --- use the natural number of items
- **Negative parallelisms:** "not only X but Y," "it's not just X, it's Y" --- state the point directly
- **Synonym cycling:** rotating through synonyms to avoid repetition ("the movement... the faction... the group... the organization") --- repeat the clearest noun
- **Em dash overuse:** more than one em dash per paragraph is a tell; prefer commas, periods, or parentheses
- **AI vocabulary:** "Additionally," "delve," "landscape" (abstract), "tapestry," "interplay," "nuanced," "multifaceted" --- replace with concrete language

If any pattern appears, rewrite before moving on.

### 8. Self-check every paragraph

Before moving on from any paragraph, verify:
- Body paragraphs: topic sentence states a claim, not a literature summary
- Intro/abstract: opening is punchy and hooks immediately
- Every claim matches the evidence (no verbs too strong for the design)
- Compact: no sentence can be cut or merged without losing information
- Flows from the previous paragraph and sets up the next
- No AI-writing tells from the humanizer checklist above

If any check fails, rewrite before moving on. Do not leave problems for a later pass---they accumulate and degrade the whole section.

## Fact-Checking Obligation

Verify every factual claim before writing it, even when the user explicitly requests specific content. Check dates, names, places, and characterizations against sources (RAG, PDFs, existing notes in `notes/`). If a claim cannot be verified, flag it to the user rather than writing it.

Why this is non-negotiable: A single wrong date or mischaracterized source in a historical paper can sink the manuscript's credibility with area-specialist reviewers. The user's role is to direct; the agent's role is to ensure accuracy.

## Citation and Abstract Rules

Follow `.claude/rules/citation-rules.md` (canonical source for citation practice, abstract length, Typst compilation, and bibliography rules).

## Quick-Reference: Common Fixes

**Weak topic sentences** --- Flip the structure. Lead with the claim, follow with the evidence. If the paragraph starts with "Scholars have shown..." rewrite so it starts with what you want the reader to believe.

**Overclaiming** --- Use verbs that match the research design.
- Bad: "This paper attempts to shed some light on..."
- Good: "This paper identifies..."
- Bad: "demonstrates a general mechanism"
- Good: "documents," "provides evidence consistent with"

**Filler phrases to delete on sight**: "It is worth noting that...", "Importantly,...", "very", "quite", "relatively", "somewhat", "crucial", "fundamental", "groundbreaking"

**Vague referents across section boundaries** --- When a new section opens with a pronoun or generic noun phrase ("The conspirators," "They," "This group"), the reader may have lost the antecedent. At the start of a new section or after a heading, re-anchor the referent with enough specificity that the paragraph is intelligible without re-reading the previous section. "The May 15 conspirators" or "the naval officers and agrarian nationalists who assassinated Inukai" beats "The conspirators."

**Citation dumps** --- If a parenthetical contains more than 3--4 citations, ask whether each one does distinct work. Cluster related citations and explain what each group contributes. Citations demonstrate positioning, not reading volume.
