# Calibration Assessor: Evaluation Criteria

Derived from an empirical audit of published APSR/AJPS papers (calibration-report.md). Every check maps to a specific finding from that audit. When evaluating, cite the finding number.

---

## Verb Calibration (Finding 1 + Finding 3)

For each statement of a finding, check that the verb matches the research design:

| Research Design | Appropriate Verbs | Flag If |
|---|---|---|
| RCT / natural experiment | causes, increases, reduces | — |
| DiD / event study | reduces, produces, resulted in, drives | "suggests," "provides evidence" |
| IV / RDD | effect of, increases, establishes | "may increase" |
| Panel FE with strong controls | produces, is associated with, contributed to | "might be associated" |
| Cross-section + Oster/sensitivity | drives, is associated with, predicts | causal verbs without identification |
| Descriptive / observational | shows, finds, reveals, demonstrates | "proves," "establishes" |
| Formal model results | confirms, implies, indicates, shows | "suggests" (math is certain) |

**The test**: does the verb exceed OR fall below what the design supports? Underclaiming is as damaging as overclaiming.

**Non-top-journal tells** (from contrast group): "suggest," "propose," "argue," "I think it is fair to argue," "hopefully helpful." These verbs in main findings signal non-top-journal prose.

---

## Hedge Asymmetry (Finding 2)

Count hedge phrases per results paragraph. Compare against APSR norms:

| Finding Type | Acceptable Hedges Per Paragraph | Flag If |
|---|---|---|
| Main finding | 0–1 | >1 hedge phrase |
| Secondary finding | 1–2 | >2 or 0 (if design is weak) |
| Mechanism test | 1–3 | 0 (should acknowledge indirectness) |
| Null on competitor | 0 (state flatly as positive evidence) | any hedging ("may not have an effect") |

**Hedge phrases to count**: suggests, may, might, could, appears to, seems to, is consistent with, provides some evidence, potentially, possibly, to some extent.

**Flag uniform hedging**: if every finding in the results section gets the same hedge level regardless of design strength, flag the pattern. Top papers differentiate sharply.

---

## Limitation Placement (Finding 4)

| Check | Flag If |
|---|---|
| Standalone limitations section | Any standalone section exists (no audited APSR paper has one) |
| Total limitation words | >300 words across entire paper |
| Limitations in introduction | Any caveat or apology in the intro |
| Limitation in conclusion | Extensive re-qualification in conclusion |

Limitations should be: brief, inline, scattered across methods and results, often in footnotes.

---

## Topic Sentences (Finding 5)

**Theory / lit review paragraphs**: Every paragraph must open with a topic sentence that states a **claim**, not a literature summary.

- Flag: "Several scholars have studied the relationship between X and Y (Smith 2020; Jones 2021)."
- Pass: "Peripheral status---not poverty---is the critical precondition for radical mobilization."

**Results paragraphs**: Two standard openers (approximately 50/50 in APSR):
- Table-reference: "Table 1 reports the main results." → Pass
- Claim-first: "The results show a sharp divergence." → Pass
- Literature summary: "Previous studies have found mixed results." → Flag

In either case, the finding must appear in the same paragraph as the table reference.

---

## Introduction Timing (Finding 6)

The main finding must appear by paragraph 2–3, on page 1 (the vast majority of audited papers).

| Check | Flag Level |
|---|---|
| Finding by paragraph 2–3 | Pass |
| Finding in paragraph 4 | Important |
| Finding deferred past paragraph 4 | Critical |
| Finding absent from introduction | Critical |

Additional intro checks (from section-forms.md):
- Opening sentence: NOT "This paper..." or a literature review or a definition
- CW: stated as fact, not attributed to "scholars" or "the literature"
- Synthesis: stated as logical consequence, not "what I call" / "cumulative implication"
- Intro ownership: by paragraph 2–3 the reader should know what this manuscript argues or finds, not just why the topic matters
- Contributions: one paragraph each, framed against specific prior work
- No roadmap by default; if present, it comes only after the answer and method are already clear
- No "may" / "might" on the main finding
- No passive voice on findings

**Flag "background accretion"** when an introduction spends two paragraphs on broad motivation, field significance, or case setup before the manuscript takes ownership of its own answer.

---

## Conclusion Checks (Finding 7)

| Check | Flag Level |
|---|---|
| Conclusion > 700 words | Important |
| Conclusion > 1,000 words | Critical |
| Introduces new analysis | Critical |
| Extensively re-qualifies results | Important |
| Contains standalone limitations paragraph | Critical |

Standard conclusion: 2–3 paragraphs, 300–700 words. Summary with "so what" → broader implications → (optional) future research.

**Flag "soft landing"** when the conclusion closes with diffuse recap, generic caution, or "more research is needed" filler instead of stating the manuscript's implication.

---

## Restatement Strategy (Finding 8)

The main finding should appear in 3–5 locations, each adding something new:

| Location | What It Should Add |
|---|---|
| Abstract | Short, punchy, with design and magnitude |
| Introduction (para 2–3) | Framing and contribution context |
| Results section | Specific coefficients and standard errors |
| End of results / pre-robustness | Summary before addressing threats |
| Conclusion | Implications and "so what" |

**Flag**: any expected location missing. **Flag**: verbatim repetition (same wording, no new information). **Pass**: progressive restatement (each iteration more precise).

---

## Paragraph Length (Finding 9)

| Section | Typical Range | Flag If |
|---|---|---|
| Introduction | 4–8 sentences | >10 |
| Theory / lit review | 5–8 sentences | >10 |
| Results | 4–7 sentences | >7 |
| Conclusion | 5–8 sentences | >10 |

Results paragraphs should be the tightest in the paper.

---

## Voice (Finding 10)

| Pattern | Flag? |
|---|---|
| "I show," "I find," "I argue" | Pass (single-author standard) |
| "We show," "We find" | Pass (multi-author standard) |
| Active voice for findings | Pass |
| "It was found that..." | Flag (passive hedging) |
| "It could be argued that..." | Flag |
| "It might be suggested that..." | Flag |
| "The results are reported in Table 1" | Pass (standard table reference) |

---

## Assertiveness Hierarchy (from prose-standards.md + section-forms.md)

| Context | Required Level | Flag If |
|---|---|---|
| Established fact / CW | State as fact | "Scholars have argued..." / "The literature suggests..." |
| Your synthesis of literatures | Logical consequence | "What I call..." / "A cumulative implication" |
| Your challenge to CW | State directly | "While the prevailing view has merit..." (too charitable) |
| Main findings (well-identified) | Flat assertion | "suggests" / "may" / "might" / passive |
| Secondary findings | Moderate confidence | Flat assertion (overclaiming) |
| Mechanism evidence | Measured confidence | Flat assertion (overclaiming) |
| Speculation beyond data | Honest hedging | Flat assertion (overclaiming) |

---

## Citation Practice (from prose-standards.md)

| Check | Flag If |
|---|---|
| Parenthetical dumps | >4 citations in one parenthetical without explaining what each group contributes |
| Decorative citations | Citations that do no work (don't support a claim, mark a contrast, or identify a gap) |
| Prose citation misuse | Using prose citation ("Smith (2020) argues...") for background consensus (should be parenthetical) |
| Orphan citations | Cited paper not read via RAG or PDF |

---

## Word-Budget Analysis

Not an issue-flagging category — a structural analysis:

1. Count words per section (strip Typst markup via regex)
2. Map each section to its type by heading text
3. Compare against section-forms.md quantitative benchmarks
4. Report: section name, current words, benchmark range, gap, recommended delta
5. Flag sections >30% below benchmark as "Word-budget gap" (Important)
6. Flag sections >30% above benchmark as "Word-budget gap" (Important)

---

## Overclaiming (moved from proofreading)

The text makes a claim that exceeds what the research design supports.

**What IS overclaiming (flag)**:
- Causal language without identification
- Universalizing from a specific case ("radicals always...")
- Strength mismatch (p < 0.10 described as "confirming")
- Omitting hedges on indirect evidence

**What is NOT overclaiming (do not flag)**:
- Causal verbs for DiD/IV/event study designs
- "Shows," "demonstrates" for main findings with clean identification
- "Drives," "contributed to" for cross-section with Oster tests
- Flat assertions of nulls on competing explanations

---

## Underclaiming / Too-Conceding (moved from proofreading)

The mirror of overclaiming. The text hedges beyond what the assertiveness hierarchy warrants.

**What IS too-conceding (flag)**:
- CW attributed to "scholars" instead of stated as fact
- Synthesis disclaimed ("what I call," "cumulative implication")
- Challenge softened ("While the prevailing view has merit...")
- Main finding hedged with "suggests" or "may" when design supports causal verbs
- Apologetic framing ("This paper attempts to shed some light...")
- Limitations in the introduction

**Severity**: "Important" for individual instances. "Critical" if pervasive (3+ in one section), because the cumulative effect makes the reader unsure what the paper claims.
