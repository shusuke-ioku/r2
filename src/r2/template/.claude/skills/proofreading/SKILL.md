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

**Pacing problem** --- A section is too compressed (rushing through material that needs space) or too drawn out (belaboring a point that could be made in half the words). The reader either loses the thread from overload or loses interest from repetition.

**Dangling thread** --- The text raises a question, promises an explanation, or introduces a tension that is never resolved. The reader reaches the end still wondering about it.

Example: The introduction mentions that the paper addresses "why democratic institutions failed to self-correct" but the conclusion never returns to this question.

**Overclaiming** --- The text makes a causal, universal, or definitive claim that the evidence does not support at the stated strength. The most common forms:
- *Causal language for associational evidence*: "X drove Y" or "X was driven by Y" when the research design identifies a correlation or a suggestive pattern, not a clean causal effect. Watch especially for verbs like "drove," "caused," "produced," "generated," "determined" in contexts where the identification strategy supports only association, plausible mechanism, or suggestive evidence.
- *Universalizing from a specific case*: "radicals always bypass gatekeeping through civic organizations" when the paper documents one historical case.
- *Omitting hedges where the evidence is indirect*: A network analysis shows betweenness centrality but the text says the person "coordinated" the conspiracy, when the data show only organizational co-membership.
- *Strength mismatch between evidence and claim*: A marginally significant result ($p < 0.10$) described without qualification, or a placebo test described as "confirming" when it merely "fails to reject."

Overclaiming is insidious because it sounds confident and authoritative --- exactly the tone authors aim for. But reviewers are trained to catch it, and a single overclaim can undermine trust in the entire paper. When in doubt, flag it. The fix is usually a single word: "driven by" → "associated with," "confirms" → "is consistent with," "shows" → "suggests."

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

**Category:** [one of the eight categories above]
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
