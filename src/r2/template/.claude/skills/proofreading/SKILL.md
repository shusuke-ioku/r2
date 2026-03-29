---
name: proofreading
description: >
  Evaluates the flow and readability of paper/paper.typ by reading it sequentially
  from beginning to end, exactly as a first-time reader would. Flags issues that
  prevent understanding: unclear transitions, missing context, logical gaps, undefined
  terms, abrupt topic shifts, buried key claims, redundancy, and pacing problems.
  Suggests concrete improvements for each issue. Trigger this skill whenever the user
  says "proofread", "check the flow", "read through the paper", "does this make sense",
  "reader experience", "is the argument clear", "evaluate readability", "check coherence",
  "flow check", "is this easy to follow", "walk through the paper", "simulate a reader",
  "would a reader understand this", "check the narrative", "is the structure clear",
  or any request about whether the paper reads well as a whole. Also trigger when the
  user asks you to "read it like a reviewer would" or "pretend you're reading this for
  the first time". This skill differs from review (which stress-tests claims) and
  writing (which polishes prose at the sentence level) --- it evaluates the reader's
  cumulative experience across the entire manuscript.
---

# Proofreader

Simulate a first-time reader. Flag every moment where understanding breaks down.

## Why This Skill Exists

The writing skill optimizes prose density and calibration at the paragraph level. The review skill stress-tests arguments and identification strategy. Neither catches the problems that emerge only when someone reads the paper front-to-back: a term used before it is defined, a result that assumes context from a section the reader hasn't reached yet, a transition that makes sense to the author (who knows where the argument is going) but baffles a newcomer. These are flow problems, and they are invisible to the person who wrote the paper. The only way to find them is to simulate the experience of a naive reader encountering each sentence in order.

## Core Principle: The Reader's State Machine

At every point in the paper, the reader carries a mental state: what they know so far, what they expect next, and what questions are open. Flow breaks when the text assumes knowledge the reader does not yet have, answers a question the reader never asked, or fails to answer a question the text itself raised.

Your job is to track this state explicitly. As you read each paragraph, maintain a running model of:

- **What the reader knows** (concepts, terms, findings introduced so far)
- **What the reader expects** (what the previous paragraph set up as the next topic)
- **What questions are open** (puzzles, tensions, or promises the text has raised but not yet resolved)

A flow issue occurs whenever the text violates this state: using a term not yet in the "knows" set, pivoting away from what the reader "expects," or closing the paper with questions still "open."

## Non-Negotiable: Surface Every Logical Flaw

Logical gaps are the highest-priority class of issue in this skill. A reader who encounters an undefined term can guess from context. A reader who hits a pacing problem can skim. But a reader who encounters a broken logical chain --- a claim that does not follow from the evidence, a causal step that is asserted but never justified, an argument that quietly shifts its terms midstream --- loses trust in the entire paper. Reviewers reject papers for logical gaps, not for rough transitions.

When reading the paper, interrogate every inferential step:
- Does claim B actually follow from claim A, or does the text merely place them next to each other?
- When the paper says "therefore," "thus," "this suggests," or "as a result" --- is the inference actually warranted?
- When the paper moves from historical narrative to analytical claim, is the bridge explicit?
- Are there places where the author clearly knows the connection (because they wrote it) but the reader cannot reconstruct it from what is on the page?

Do not let a single logical gap pass unremarked. It is better to flag ten gaps and have the user dismiss five as intentional than to miss one that a reviewer catches. If you are uncertain whether something is a logical gap, flag it anyway and note your uncertainty --- the user can decide.

## Workflow

### 0. Load section-forms.md

Before reading the paper, load `.claude/skills/writing/references/section-forms.md`. This file defines the standard APSR/AJPS section structures---paragraph templates, quantitative benchmarks, assertiveness hierarchy, and "Things APSR Papers Never Do" lists---extracted from 20+ audited papers. Use it as the structural benchmark throughout your reading. Every section of the manuscript should conform to the corresponding section form; deviations are flagged as "Section form deviation" (see category below).

### 1. Read the full paper sequentially

Read `paper/paper.typ` from the first line to the last. Do not skip sections, do not jump ahead, do not skim. The entire point is to experience the paper in the order a reader would.

As you read, take notes on your evolving mental state. When something feels off --- a moment of confusion, a term you don't recognize, a paragraph that seems to come from nowhere --- mark it immediately. Do not rationalize it away ("oh, they probably explain this later"). If the reader would be confused *at this point*, it is a flow issue regardless of what comes later.

### 2. Classify each issue

For every issue you flag, classify it using one of these categories:

**Forward reference** --- The text uses a concept, term, dataset, or result that has not yet been introduced. The reader encounters something they cannot understand without information that appears later (or never appears).

Example: "The organizational density measure captures..." when organizational density has not been defined yet.

**Expectation violation** --- The previous paragraph set up a specific expectation (explicitly or implicitly), and the next paragraph goes somewhere else entirely. The reader feels a jolt --- "wait, I thought we were talking about X."

Example: A paragraph ends by raising the puzzle of why rural areas were disproportionately affected, but the next paragraph discusses parliamentary vote shares with no bridge.

**Logical gap** --- The argument skips a step. The conclusion of a paragraph does not follow from its premises without an intermediate claim that is missing. The reader can sense the destination but cannot trace the path. This is the single most important category. A paper with beautiful prose but broken logic fails; a paper with rough prose but airtight logic succeeds. Treat every logical gap as a potential rejection reason.

Logical gaps come in many forms --- watch for all of them:
- *Missing intermediate step*: A leads to C, but the B connecting them is never stated.
- *Unsupported causal claim*: The text asserts X causes Y without explaining the mechanism or citing evidence.
- *Non sequitur transition*: Two adjacent paragraphs or sentences that feel connected by proximity but have no actual logical link.
- *Circular reasoning*: The conclusion restates a premise as if it were a new insight.
- *Scope mismatch*: Evidence about one context is used to support a claim about a different context without justifying the transfer.
- *Implicit assumption*: The argument relies on a premise that is never stated --- the reader must supply it themselves, and may not.

Example: "Economic hardship radicalized the countryside" followed immediately by "Radical officers exploited this organizational infrastructure" --- the connection between economic hardship and organizational infrastructure is never made explicit. The reader is left wondering: did economic hardship *create* the infrastructure? Did it merely make existing infrastructure available for exploitation? The missing link undermines the entire causal chain.

**Undefined term** --- A technical term, foreign-language term, historical reference, or acronym is used without definition or sufficient context for a non-specialist reader to understand it.

Example: a specialized term without explaining what it is, or an acronym without spelling it out first.

**Buried claim** --- A key claim or finding is tucked inside a subordinate clause, a long paragraph, or a parenthetical, when it deserves prominence. The reader might miss it entirely.

Example: The paper's main causal finding appears in the middle of a paragraph about robustness checks instead of getting its own clear statement.

**Redundancy** --- The same point, evidence, or framing appears in multiple places without adding anything new. The reader thinks "didn't I already read this?" and starts skimming.

Example: The introduction previews the mechanism, the theory section restates it identically, and the results section explains it a third time with the same wording.

**Exception --- strategic restatement.** Top APSR/AJPS papers restate their main finding 3-5 times: abstract, introduction, results, end of results, conclusion. Each restatement adds something --- precision, quantification, theoretical context, or implications. This is standard practice, not redundancy. Flag restatement as redundancy only when successive iterations use identical wording and add no new information. Progressive restatement (each time more precise) is a feature, not a bug.

**Pacing problem** --- A section is too compressed (rushing through material that needs space) or too drawn out (belaboring a point that could be made in half the words). The reader either loses the thread from overload or loses interest from repetition.

**Dangling thread** --- The text raises a question, promises an explanation, or introduces a tension that is never resolved. The reader reaches the end still wondering about it.

Example: The introduction mentions that the paper addresses "why democratic institutions failed to self-correct" but the conclusion never returns to this question.

**Overclaiming** --- The text makes a claim that exceeds what the research design supports. Overclaiming is real and worth catching, but the threshold must track the identification strategy. Flagging confident language for a well-identified finding is a false positive that weakens the paper. (Evidence base: `writing/references/calibration-report.md`, audit of published APSR/AJPS papers.)

**What IS overclaiming (flag these):**
- *Causal language without identification*: "X caused Y" when the design is cross-sectional without an instrument, sensitivity test, or quasi-experimental variation.
- *Universalizing from a specific case*: "radicals always bypass gatekeeping through civic organizations" when the paper documents one historical case.
- *Strength mismatch*: A $p < 0.10$ result described as "confirming" rather than reported with its p-value. A placebo test described as "confirming" when it merely "fails to reject."
- *Omitting hedges on indirect evidence*: Betweenness centrality described as "coordinated" when the data show only co-membership.

**What is NOT overclaiming (do not flag):**
- Causal verbs for DiD, IV, event study, or RDD designs: "reduces," "produces," "resulted in" are standard APSR/AJPS practice (Grumbach 2022: "reduces"; Dasgupta & Ziblatt 2022: "resulted in"; Claassen 2019: "produce").
- "Shows," "demonstrates," "reveals," "finds" for a paper's main finding with clean identification.
- "Drives" or "contributed to" for cross-sectional results with Oster tests, extensive controls, and a plausible mechanism (Abramson & Carter 2016: "drives"; Grzymala-Busse 2023: "contributed to").
- Flat assertions of null results on competing explanations: "has no measurable effect" (King et al. 2013, APSR).

**The test:** does the verb exceed what the research design supports? Not: does the verb sound too confident? Underclaiming --- hedging a well-identified finding --- is as damaging as overclaiming. It signals the author does not trust the identification strategy.

Use the assertiveness hierarchy from `section-forms.md` to calibrate: CW should be stated as fact, synthesis as logical consequence, challenges directly, main findings flatly, mechanism evidence with measured confidence, and only speculation beyond the data gets honest hedging.

**Too conceding** --- The mirror of overclaiming. The text hedges or qualifies beyond what the assertiveness hierarchy warrants. This is as damaging as overclaiming at APSR---it signals the author does not trust their own argument.

**What IS too conceding (flag these):**
- CW attributed to "scholars" or "the literature" instead of stated as fact: "Scholars have argued that..." / "The literature suggests..."
- Synthesis disclaimed as the author's construction: "Together, these literatures produce what I call..." / "The expectation is a cumulative implication, not any single work's claim"
- Challenge softened: "While the prevailing view has considerable merit, this paper offers an alternative perspective..."
- Main finding hedged with "suggests" or "may" when the design supports causal verbs
- Apologetic framing: "This paper attempts to shed some light on..."
- Limitations in the introduction

**What is NOT too conceding (do not flag):**
- "Suggests" or "is consistent with" for secondary findings or mechanism tests
- "Provides evidence that" for indirect evidence
- Reporting p-values for marginal results without labeling them "significant"
- Inline, brief caveats in methods or results about specific design limitations

**Severity:** Rate as "Causes confusion" because too-conceding prose signals insecurity and weakens the reader's trust in the contribution. If pervasive (3+ instances in a section), rate as "Blocks comprehension" because the cumulative effect makes the reader unsure what the paper actually claims.

**Section form deviation** --- A section does not follow the standard APSR/AJPS structure defined in `section-forms.md`. This is a structural problem, not a prose problem---the section's organization departs from the expected form without justification.

**Flag when:**
- Introduction does not state the finding by paragraph 2--3
- Introduction opens with "This paper..." or a literature review ("Smith 2020 argues...") as the first sentence
- Introduction uses "scholars have argued" or "the literature suggests" to introduce CW
- Results paragraph separates the table reference from the finding (finding in a different paragraph)
- Conclusion exceeds 1000 words, introduces new analysis, or contains a standalone limitations paragraph
- Paper contains a standalone limitations section (should be scattered inline, 100--300 words total)
- Roadmap sentence appears ("This paper proceeds as follows...")

**Severity:** Rate as "Causes confusion" by default. Rate as "Blocks comprehension" if the deviation fundamentally misstructures the argument (e.g., finding deferred past paragraph 4 of the introduction).

### 3. Assess severity

For each issue, rate how badly it disrupts understanding:

- **Blocks comprehension**: The reader cannot follow the argument past this point without re-reading or guessing. Must fix.
- **Causes confusion**: The reader can push through but loses confidence in the argument or their understanding of it. Should fix.
- **Minor friction**: The reader notices something slightly off but can continue without real trouble. Fix if easy.

### 4. Suggest concrete fixes

For every issue, propose a specific fix. Not "improve the transition" but "add a sentence after paragraph 3 of Section 2 that connects X to Y by stating Z." The fix should be something the user (or the writing skill) can implement directly.

When possible, suggest the actual sentence or bridge phrase. When the fix requires restructuring (e.g., moving a paragraph), describe the new order and why it works better.

### 5. Humanizer pass

Scan every paragraph for AI-writing tells (full pattern catalog in `.claude/skills/humanizer/SKILL.md`). Flag any instance as a flow issue under a new category:

**AI-writing tell** --- A word, phrase, or structural pattern that signals machine-generated text. These erode reader trust even when the content is sound, because reviewers and editors are increasingly attuned to them.

The most common tells in academic prose:
- Significance inflation: "pivotal," "crucial," "fundamental," "serves as a testament"
- Superficial -ing phrases: "highlighting," "underscoring," "emphasizing," "reflecting," "showcasing"
- Copula avoidance: "serves as," "stands as," "functions as" instead of "is"
- Rule of three: forcing ideas into triads
- Negative parallelisms: "not only X but Y," "it's not just X, it's Y"
- Synonym cycling: rotating through synonyms for the same referent
- Em dash overuse: more than one per paragraph
- AI vocabulary: "Additionally," "delve," "landscape" (abstract), "tapestry," "interplay," "nuanced," "multifaceted"

Rate severity as **Minor friction** unless the pattern is pervasive (3+ instances in a section), in which case rate as **Causes confusion** because the cumulative effect signals inauthenticity.

### 6. Produce output

**Always present findings as a numbered checklist** so the user can select which items to implement. Organize in reading order. For each item, provide a one-line summary with the line number, category, and severity in parentheses. After the checklist, include a collapsible or clearly separated detail section with the full analysis for each item (reader's experience, suggested fix).

Format:

```
- [ ] **1.** Line XX: One-line description of the issue (Category; Severity)
- [ ] **2.** Line XX: One-line description (Category; Severity)
...
```

Then for each item, provide the detailed analysis:

```
### 1. [Section name], line XX

**Category:** [one of the ten categories above]
**Severity:** [Blocks comprehension / Causes confusion / Minor friction]

**What happens to the reader:** [describe the reader's experience]

**Suggested fix:** [concrete, implementable suggestion]
```

After all individual issues, provide:

**Overall flow assessment** --- A short (3--5 sentence) summary of how the paper reads as a whole. What is the dominant flow problem (if any)? Where does the paper read most smoothly? What is the single highest-priority structural change?

## Hard Constraint: Abstract Length

The abstract must never exceed 150 words. If it does, flag it as a pacing problem with severity "Blocks comprehension" and suggest cuts.

## What This Skill Does NOT Do

- **Prose polish**: It does not rewrite sentences for density or style (that is the writing skill's job).
- **Argument stress-testing**: It does not evaluate whether claims are well-supported or identification is valid (that is the review skill's job).
- **Line editing**: It does not catch typos, grammar errors, or formatting issues.

The proofreader asks one question only: "Can a first-time reader follow this?" If the answer is no, it explains exactly where and why, and how to fix it.

## Scoping

The user may ask you to proofread the whole paper or a specific section. Adjust accordingly:

- **Full paper**: Read everything. This is the default and most valuable mode.
- **Specific section(s)**: Read the requested section(s), but also skim what comes before to build the reader's state at the point where the section begins. You cannot evaluate flow without knowing what the reader already knows.
