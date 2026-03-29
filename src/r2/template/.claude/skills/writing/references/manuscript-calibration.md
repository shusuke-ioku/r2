# Manuscript Calibration

Manuscript-first norms extracted from the local calibration corpus in `dev/calibration/`, combining:

- all 80 files in `dev/calibration/pdf/` through corpus-wide text extraction
- direct paper sampling from `dev/calibration/pdf/`
- `review-calibration/results/section_analysis.md`
- `review-calibration/results/rhetoric_analysis.md`
- `review-calibration/results/learnings.md`
- the existing APSR/AJPS section audit in `section-forms.md`

Load this file when writing, proofreading, or polishing manuscript prose. It is the shared reference layer across those skills.

## What the corpus says

### 1. Top-tier intros are short in paragraph count, not in argumentative ambition

From `section_analysis.md`:

- Top-tier usable intros: mean 2.5 paragraphs, median 3
- Non-top usable intros: mean 7.2 paragraphs, median 6
- Top-tier intros carry far more words per paragraph than non-top intros

Implication:

- Do not build introductions by stacking many short paragraphs.
- Prefer 2-4 substantial intro paragraphs that each do real argumentative work.
- Compression should come from denser paragraphs, not from deleting the finding or design.

### 2. Findings appear early and flatly

From `rhetoric_analysis.md`, direct PDF checks, and a corpus-wide pass across all 80 files:

- Top-tier intros usually state the main finding by paragraph 2-3
- Conventional wisdom is often stated flatly, then broken quickly
- Main results are rarely buried behind literature scene-setting
- First-person answer verbs in the opening text (`I show`, `we show`, `I find`, `we find`, `I argue`, `we argue`) appear in 41/50 top papers but only 15/30 non-top papers

Direct paper signals from sampled PDFs:

- `CAL069`: "I show that..." appears early and is followed by a quantified effect
- `CAL069`: the main results paragraph names `Table 1` and states the result in the same paragraph

Implication:

- Manuscript intros should reveal the answer early.
- Results sections should not separate table reference from claim.
- Avoid deferring the real contribution until after background exposition.
- Early argumentative ownership is one of the strongest full-corpus contrasts between stronger and weaker papers.

### 2b. Non-top intros often spend too long earning the right to exist

Direct contrast from sampled non-top papers such as `CAL032`, `CAL033`, and `CAL036`, reinforced by the corpus-wide ownership gap:

- the opening leans on broad topic importance, field motivation, or meta-level setup
- the paper's own answer arrives later
- the intro can feel like literature staging before argumentative ownership

Implication:

- Do not spend the first two intro paragraphs proving that the topic is important.
- By paragraph 2--3, the reader should know what *this manuscript* argues or finds.
- Background without ownership is a non-top signal.

### 3. Results prose is tight and coefficient-bearing

Observed pattern:

- Table/purpose opener is acceptable
- The claim appears immediately after the table opener
- Magnitude follows quickly
- Robustness is narrated as pressure on the main claim, not as a second paper

Implication:

- Results paragraphs should be among the shortest in the paper.
- State coefficient direction and magnitude early.
- Nulls on competing explanations should be stated cleanly, not hedged into mush.
- Robustness and mechanism tests should appear as pressure on the main finding, not as rival centers of gravity.

### 4. Conventional wisdom is stated as fact, not as hearsay

The rhetoric audit repeatedly shows:

- openers like "economic historians agree..." or direct factual assertions
- challenges stated directly
- almost no "scholars have argued that..." openings

Implication:

- Use citations to attribute, not verbs like "scholars argue" to soften obvious field knowledge.
- State the field's baseline expectation as something the reader already knows.
- Corpus-wide support is strong here: explicit hearsay phrases like `scholars have argued` or `the literature suggests` are almost absent in the opening texts.

### 5. Top-tier prose is assertive but not inflated

The corpus supports a narrower target than "be bold":

- strong identification gets flat verbs
- indirect evidence gets measured verbs
- top papers are not uniformly hedged
- top papers also avoid empty intensifiers and generic hype

Implication:

- Confidence must track design.
- Do not replace weak argument with loud adjectives.
- Underclaiming is also a calibration failure when the design is strong.

### 6. Paragraph density matters more than ornamental flow

The top-tier contrast is not just sentence-level polish. It is paragraph-level efficiency:

- topic sentence makes a claim or a purpose statement
- evidence sentences all serve that claim
- paragraphs rarely feel like assembled notes

Implication:

- Each paragraph should have one main job.
- Cut sentence-level redundancy before adding transitions.
- If a paragraph needs many bridge phrases to make sense, the structure is probably wrong.

### 7. Conclusions are brief and implication-heavy

From `section_analysis.md` and `section-forms.md`:

- standard conclusion target remains short
- conclusions should restate the finding with "so what"
- standalone limitations sections are non-top tells

Implication:

- Conclusions should compress, not reopen the paper.
- No extended caveat dump at the end.
- End on implication, not apology.

### 8. Roadmaps are optional and late

The local corpus does not support a blanket "never use a roadmap" rule. A corpus-wide pass found roadmap markers in only 9/80 files. Some strong papers use one briefly, but only after the reader already knows the argument and the evidence strategy.

Implication:

- If a roadmap appears, it should come after the answer and method are already clear.
- A roadmap cannot substitute for early argumentative disclosure.
- Default to no roadmap unless the structure truly benefits from one.

### 9. Future-work endings are uncommon

Across the full corpus, generic future-work signals are rare. `more research is needed` does not appear at all, and `future research` appears in only 7/80 endings.

Implication:

- Do not end conclusions with ritualized future-work filler.
- If future research appears, it should be brief and logically downstream of the finding.
- Conclusion closure should rest on implication, not on a generic look ahead.

## Common manuscript anti-patterns

These are recurring failures the integrated skills should catch.

### Intro anti-patterns

- opening with "This paper..."
- opening with a literature summary
- deferring the finding past paragraph 3
- spending two paragraphs on why the topic matters before saying what the paper does
- splitting one intro function across too many micro-paragraphs
- introducing contributions before the reader knows the result

### Body anti-patterns

- topic sentence summarizes literature instead of stating a claim
- paragraph contains both mechanism development and empirical interpretation
- transitions explain movement instead of making movement unnecessary
- evidence is listed without an argumentative point

### Results anti-patterns

- table reference in one paragraph, actual finding in the next
- coefficients presented without stakes
- robustness checks narrated at the same weight as the main result
- mechanism evidence written as if it were the causal main effect

### Conclusion anti-patterns

- re-running the whole paper
- adding fresh evidence
- ending with diffuse future-work filler
- apologizing for limitations instead of stating implications

## Role split across skills

Use this reference differently by skill:

- `writing`: generate or revise prose to match these norms
- `proofreading`: diagnose where reader experience departs from these norms
- `polishing`: orchestrate section-level assessment and revision using these norms as shared ground truth

## Decision rules

When tradeoffs appear, prefer:

1. early clarity over slow build
2. paragraph density over extra transitions
3. design-matched confidence over universal hedging
4. direct claims over literature throat-clearing
5. brief conclusions over comprehensive recaps
6. argumentative ownership over broad topical motivation
