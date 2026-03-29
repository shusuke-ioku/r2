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

Manuscript-first prose generation and revision. This skill writes paragraphs and sections; it does not simulate a naive reader end-to-end and it does not orchestrate whole-paper convergence loops.

## Core Principles

All manuscript-writing rules derive from four principles: **density**, **placement**, **calibration**, and **assertiveness**.

### Density

Pack every paragraph with substance. Strip every word that does not carry weight. A compact five-sentence paragraph beats a diffuse ten-sentence one.

**Match detail to context.** The introduction and contributions move the argument forward---details, caveats, and background belong in the body sections or footnotes, not here. When writing any section, ask: does the reader need this information _at this point_ to follow the argument? If not, cut it or move it downstream. The introduction should flow smoothly at the level of claims and evidence; methodological nuances, historical background, and qualifying caveats that interrupt that flow belong in the sections where they are directly relevant. Over-specifying in the wrong place is as damaging as under-specifying: it buries the signal and breaks the reader's momentum.

Why this matters: Reviewers form impressions within the first page. Filler signals that the author isn't sure what the point is. In a historical case study where the empirical contribution must speak loudly, loose prose buries the signal.

### Placement

Put the most important claim where the reader expects to find it. In manuscript prose, the largest failures are usually placement failures, not word-choice failures: findings arrive too late, magnitudes too late, contributions too late, or a paragraph's point appears only at the end.

Why this matters: the calibration corpus shows that top-tier manuscripts front-load findings, use compact intro structures, and put the result in the same paragraph as the evidence pointer.

### Calibration

Match every claim to the research design. A DiD finding supports causal verbs. A cross-sectional correlation does not. The verb must track the identification strategy, not some generic caution.

**Be assertive on main findings.** Top APSR/AJPS papers state main results flatly: "reduces," "produces," "resulted in," "demonstrates" (see `references/calibration-report.md` for the evidence base from audited APSR/AJPS papers). They reserve hedging for auxiliary tests and mechanism explorations. Uniform hedging---qualifying every result equally---reads as uncertainty about the paper's own contribution. If the identification strategy supports the claim, state it without apology.

**Hedge asymmetrically.** Main findings get flat assertions with precise verbs. Secondary findings get moderate hedging ("suggests," "is consistent with"). Mechanism tests get "provides evidence that." For marginal results (p < 0.10), report the p-value and let readers judge---do not label them "marginally significant."

**Design-calibrated verb hierarchy:**
- DiD / event study / RCT: "reduces," "increases," "produces," "resulted in"
- IV / RDD: "the effect of X on Y," "increases," "establishes"
- Panel FE with strong controls: "produces," "is associated with," "contributed to"
- Cross-section with Oster/sensitivity tests: "drives," "is associated with," "predicts"
- Descriptive / observational: "shows," "finds," "reveals," "demonstrates"
- Formal model results: "confirms," "implies," "indicates"

Why this matters: Reviewers at APSR/AJPS expect confidence that matches the design. Excessive hedging is as damaging as overclaiming---it signals the author does not trust the identification strategy. If you hedge your main finding, the reviewer will wonder why you published it.

### Assertiveness

State conventional wisdom flatly. Challenge it directly. Never over-attribute or over-qualify established knowledge. This principle governs how the paper engages the literature---distinct from Calibration, which governs how it reports its own findings.

**The assertiveness hierarchy:**
1. Established facts / conventional wisdom: **State as fact.** "Democracy has two institutional gatekeepers." Not "Scholars have argued that democracy has two institutional gatekeepers."
2. Your synthesis of multiple literatures: **State as logical consequence.** "When both gates hold, breakdown should not occur." Not "Together, these literatures produce what I call a 'two-gates' expectation."
3. Your challenge to conventional wisdom: **State directly.** "I show instead that..." / "This paper demonstrates..."
4. Main findings: flat assertion (governed by Calibration above).
5. Mechanism evidence: measured confidence.
6. Speculation beyond the data: honest hedging.

**What "too conceding" looks like** (never found in published APSR papers):
- Over-attributing CW: "The literature generally suggests..." → Just state it.
- Over-qualifying synthesis: "The expectation is a cumulative implication, not any single work's claim" → Delete.
- Apologetic framing: "This paper attempts to shed some light on..." → "This paper identifies..."
- Charitable dismissal: "While X has considerable merit, this paper offers an alternative..." → "X does not account for [pattern]. This paper shows..."

Why this matters: The reader is a political scientist. They know the field's conventional wisdom. Attributing it to "the literature" or qualifying that your synthesis is "not any single work's claim" wastes space and signals insecurity. In 20+ audited APSR papers, zero use "scholars have argued that" to introduce conventional wisdom. They state it as fact and move on.

Load `references/section-forms.md` for the full assertiveness hierarchy with APSR examples and anti-patterns.

## Shared Reference Layer

Load these references before writing:

1. `references/section-forms.md`
2. `references/manuscript-calibration.md`
3. `references/prose-standards.md`
4. `references/table-and-notation-standards.md` only when writing tables, captions, or equations

Treat `manuscript-calibration.md` as the shared empirical ground truth across `writing`, `proofreading`, and `polishing`.

## Role Boundaries

- Use this skill to draft, rewrite, compress, and sharpen manuscript prose.
- Do not use this skill as the primary whole-paper reader-experience evaluator; that is `proofreading`.
- Do not run multi-round orchestration here; that is `polishing`.
- Use `humanizer` as a final cleanup pass, not as the main writing logic.

## Workflow

### 1. Read context first

Read surrounding sections, the abstract, and contribution claims in `paper/paper.typ` before writing anything. Inconsistency between what the introduction promises and what the body delivers is the most common manuscript flaw, and it is entirely preventable by reading first.

**Context-aware writing:** Always consider what the reader already knows at the point you are writing. Do not re-introduce concepts, datasets, variables, or terminology that have already been explained earlier in the paper. Use short references ("organizational density," not "organizational density, the count of existing organizations per 100,000 population") for anything the reader has already encountered. The level of detail in an explanation should match its novelty to the reader at that specific location in the manuscript---first mention gets full explanation, subsequent mentions get none.

### 2. Load the section form and manuscript norm

Before drafting any section, identify:

- the section type from `section-forms.md`
- the paragraph-density and timing norms from `manuscript-calibration.md`
- the design-calibrated verb target from `prose-standards.md`

Do not draft until you know where the main finding, design, and contribution should appear.

### 3. Map the argument chain

Identify what claim each paragraph needs to make. One idea per paragraph. If a paragraph serves two purposes, split it. If you cannot state a paragraph's point in one sentence, the paragraph needs restructuring, not more sentences.

### 4. Draft with the right mode

**Before drafting any section**, follow the standard form for that section type. Deviation requires a specific reason.

**Body paragraphs (lit review, theory, discussion):** Open every paragraph with a **topic sentence that states a claim**, not a literature summary. The most important claim goes in the first or second sentence. Then fill in evidence and citations. Readers skim topic sentences to follow the argument---if they summarize literature instead of making claims, the argument disappears.

- Bad: "Several scholars have studied the relationship between economic conditions and radical mobilization (Smith 2020; Jones 2021)."
- Good: "Peripheral status---not poverty---is the critical precondition for radical mobilization."

**Results paragraphs:** Table-reference and purpose-statement openers are standard: "Table 1 reports the main results" or "In this section we test our prediction that..." The claim follows immediately after the table reference. In APSR/AJPS, roughly half of results paragraphs open this way. Claim-first is also fine for results---both patterns are standard.

**Introduction:** Follow the paragraph-by-paragraph template in `references/section-forms.md` strictly, but also obey the corpus-level warning from `references/manuscript-calibration.md`: do not simulate sophistication by splitting the introduction into too many short paragraphs. Top-tier intros in the local corpus are short in paragraph count and dense in argumentative content. Put the finding in paragraph 2--3.

**Intro rewrite recipe:** When an intro is weak, rebuild it in this order:
1. one opening paragraph that states the conventional wisdom, puzzle, or motivating fact
2. one paragraph that states the paper's answer and main finding flatly
3. one paragraph that explains how the paper knows
4. one contribution paragraph, plus a roadmap only if the structure truly needs it

**Results:** Use the top-tier pattern observed in the local PDFs and audits: table-reference or purpose-statement openers are fine, but the result belongs in the same paragraph as the table pointer. Quantify quickly. Robustness and mechanisms should not steal the narrative center from the main estimate.

**Conclusion:** Compress aggressively. The conclusion should restate the finding with "so what," not relitigate every caveat.

**Conclusion rewrite recipe:** When a conclusion is weak, replace recap-heavy prose with:
1. one paragraph restating the finding and what it changes
2. one paragraph on broader implication
3. at most one short future-research sentence if it genuinely follows from the finding

### 5. Apply prose standards

Use `references/prose-standards.md` for precision, calibration, citation practice, and introduction structure.

### 6. Cut and place

- Move the main claim to the first or second sentence unless the section form specifically calls for a different opener.
- Merge or split paragraphs until each paragraph has one clear job.
- If a transition sentence only tells the reader that you are moving on, cut it and fix the structure instead.
- In results paragraphs, cut any sentence that delays coefficient direction, magnitude, or the substantive takeaway.

### 7. Humanizer pass

After drafting or revising, scan every paragraph for AI-writing tells (full pattern catalog in `../humanizer/SKILL.md`). The most damaging patterns in manuscript prose:

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

Before moving on from any paragraph, verify against `references/section-forms.md`:

**All paragraphs:**
- Topic sentence states a claim (body) or follows the section-forms template (intro/results/conclusion)
- Every claim matches the evidence (no verbs too strong or too weak for the design)
- Compact: no sentence can be cut or merged without losing information
- Flows from the previous paragraph and sets up the next
- No AI-writing tells from the humanizer checklist above
- Paragraph shape matches the shared corpus norms in `references/manuscript-calibration.md`

**Introduction (section-forms validation):**
- CW stated as fact, not attributed to "scholars" or "the literature"
- Synthesis stated as logical consequence, not as "what I call" or "a cumulative implication"
- Finding appears by paragraph 2--3
- Does NOT open with "This paper...", a literature review, or a definition
- No "may" or "might" on the main finding; no passive voice on findings
- No roadmap by default; if used, it appears only after the answer and method are already clear; no limitations apology
- Not fragmented into too many short paragraphs for the amount of argumentative work being done

**Results (section-forms validation):**
- Finding appears in the same paragraph as the table reference
- Magnitude quantified (standard deviations, percentage points)
- Nulls on competitors stated flatly as positive evidence
- Robustness and mechanism paragraphs clearly subordinate to the main result

**Conclusion (section-forms validation):**
- Under 1000 words; 2--3 paragraphs
- Restates finding with "so what," not verbatim recapitulation
- No new analysis, no extensive re-qualification, no standalone limitations

If any check fails, rewrite before moving on. Do not leave problems for a later pass---they accumulate and degrade the whole section.

## Fact-Checking Obligation

Verify every factual claim before writing it, even when the user explicitly requests specific content. Check dates, names, places, and characterizations against sources (RAG, PDFs, existing notes in `notes/`). If a claim cannot be verified, flag it to the user rather than writing it.

Why this is non-negotiable: A single wrong date or mischaracterized source in a historical paper can sink the manuscript's credibility with area-specialist reviewers. The user's role is to direct; the agent's role is to ensure accuracy.

## Citation and Abstract Rules

Follow `.claude/rules/citation-rules.md` (canonical source for citation practice, abstract length, Typst compilation, and bibliography rules).

## Quick-Reference: Common Fixes

**Weak topic sentences** --- Flip the structure. Lead with the claim, follow with the evidence. If the paragraph starts with "Scholars have shown..." rewrite so it starts with what you want the reader to believe.

**Overclaiming** --- Use verbs that match the research design. Underclaiming is as damaging as overclaiming.
- Bad: "This paper attempts to shed some light on..." (apologetic)
- Good: "This paper identifies..." (confident, appropriate for clean identification)
- Bad: "demonstrates a general mechanism" (universalizing from one case)
- Good: "documents," "shows," "finds" (for the case studied)
- Bad: "suggests" for a main DiD finding (underclaiming---signals distrust of own design)
- Good: "reduces," "produces," "resulted in" (appropriate for DiD/event study)

**Filler phrases to delete on sight**: "It is worth noting that...", "Importantly,...", "very", "quite", "relatively", "somewhat", "crucial", "fundamental", "groundbreaking"

**Vague referents across section boundaries** --- When a new section opens with a pronoun or generic noun phrase ("The conspirators," "They," "This group"), the reader may have lost the antecedent. At the start of a new section or after a heading, re-anchor the referent with enough specificity that the paragraph is intelligible without re-reading the previous section. "The May 15 conspirators" or "the naval officers and agrarian nationalists who assassinated Inukai" beats "The conspirators."

**Citation dumps** --- If a parenthetical contains more than 3--4 citations, ask whether each one does distinct work. Cluster related citations and explain what each group contributes. Citations demonstrate positioning, not reading volume.

**Intro fragmentation** --- If the introduction is accumulating many short paragraphs, stop. Rebuild the intro around 2--4 dense units: CW/puzzle, answer/finding, credibility, contributions. The local calibration corpus shows that top-tier intros are denser than non-top intros, not more segmented.

**Background accretion** --- If the introduction keeps explaining why the topic matters without saying what this paper shows, cut that material ruthlessly. Replace broad importance claims with argumentative ownership: what is the paper's answer, and why should the reader believe it?

**Results drift** --- If a results paragraph spends several sentences on setup before reporting the estimate, move the estimate up. The table reference and the substantive result belong together.

**Soft landing conclusion** --- If the conclusion ends with "more research is needed," generic caution, or diffuse recap, rebuild it around the paper's implication. A strong manuscript ends by telling the reader what changed, not by retreating.
