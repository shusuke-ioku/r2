---
name: formal-modeling
description: >
  Develops formal game-theoretic and political-economy models for this project's
  manuscript (paper/paper.typ). TRIGGER this skill whenever the user does ANY of
  the following: write a formal model, draft a game-theoretic setup, define players
  and strategies, write assumptions, derive equilibrium, state a proposition, write
  a proof, check mathematical logic, verify a derivation, debug an equation, add
  or revise a theory section, formalize an argument, translate an intuition into a
  model, write comparative statics, check consistency of notation, or anything that
  touches formal theory, propositions, lemmas, proofs, or mathematical reasoning
  in the paper. Also trigger when the user says "formalize this", "write the model",
  "check the math", "is this proof correct", "derive the equilibrium", "add
  assumptions", or "what are the comparative statics". If the task involves formal
  modeling, game theory, proofs, or mathematical derivations in any way, this skill
  applies---even if the user does not explicitly ask for modeling help.
---

# Formal Modeler

Build models that illuminate mechanisms. Every assumption earns its place; every proposition has a proof.

## Three Principles

All modeling rules derive from three principles: **clarity**, **rigor**, and **parsimony**. Internalize the reasoning behind each.

### Clarity

A model exists to sharpen an argument, not to display technical facility. The reader should understand the economic intuition behind every assumption, every equilibrium, and every comparative static without needing to work through the algebra. If the math is correct but the intuition is opaque, the model has failed.

Why this matters: This paper is a political science manuscript aimed at a general audience of comparativists and Americanists, not a theory journal. The formal theory section must be accessible to readers who are comfortable with game trees and equilibrium concepts but do not regularly write proofs. Dense notation without verbal guidance will cause reviewers to skip the section entirely.

### Rigor

Every proposition must have a valid proof. Every proof must follow from the stated assumptions---no hidden steps, no hand-waving, no "it is straightforward to show." If a step is genuinely obvious, it takes one line to write; if it is not obvious, it takes longer, and that is fine.

Why this matters: A formal model with an incorrect proof is worse than no model at all. It signals either sloppiness or that the author does not fully understand the mechanism. Reviewers who catch an error in a proof will distrust the entire paper.

### Parsimony

Include only the moving parts necessary to generate the result. If an assumption can be dropped without changing the equilibrium characterization, drop it. If a player can be removed without losing the mechanism, remove them. The model should be the simplest structure that produces the key comparative static---the insight that economic distress combined with strong party gatekeeping increases backsliding risk through the extraparliamentary channel.

Why this matters: Overbuilt models obscure the mechanism. Reviewers ask "which of these 12 assumptions is doing the work?" and if you cannot answer cleanly, the model is too complex. The goal is a clean, portable result that other scholars can cite and extend.

## Workflow

### 1. Read context first

Before writing any model, read the paper's introduction, empirical strategy, and existing theory discussion in `paper/paper.typ`. The model must formalize the argument the paper already makes---it should not introduce mechanisms that the empirics cannot speak to. Also read `paper/notes/lit.md` Section 5 (focal events and collective action) and Section 1 (backsliding typologies) to understand the theoretical positioning.

### 2. Specify the environment

Define the model in this order:

1. **Players**: Who are the strategic actors? (e.g., incumbent party, radical challenger, voters/public)
2. **Actions/Strategies**: What can each player do? State the action sets precisely.
3. **Timing**: What is the sequence of moves? Draw the game tree or state the timing protocol.
4. **Information**: What does each player observe? Is this a game of complete or incomplete information?
5. **Payoffs**: What does each player maximize? Write the utility functions explicitly.
6. **Parameters**: What are the exogenous variables? (e.g., severity of economic distress, gatekeeping capacity, cost of extraparliamentary action)

State each element as a formal assumption. Number assumptions sequentially (Assumption 1, Assumption 2, ...).

### 3. Solve the model

Work backward from the last mover (backward induction / subgame perfection) or apply the appropriate equilibrium concept. For each step:

1. State what the player is optimizing
2. Write the first-order condition or decision rule
3. Derive the optimal strategy as a function of parameters
4. Substitute back into earlier players' problems

Document every algebraic step. Do not skip intermediate steps even if they seem routine---write them out, then decide in the editing phase whether to relegate some to an appendix.

### 4. State propositions and proofs

**Proposition format:**

Every proposition must:
- State the result in plain language first (one sentence), then formally
- Specify the conditions under which it holds (reference specific assumptions)
- Be self-contained: a reader should be able to understand what the proposition claims without reading the proof

**Proof format:**

Every proof must:
- Start by stating the proof strategy (direct proof, proof by contradiction, construction, etc.)
- Reference every assumption it uses by number
- Show every algebraic step (intermediate steps can go in appendix, but must exist)
- End with a clear conclusion that restates the proposition's claim
- Terminate with a QED marker

**Typst conventions for this paper:**
- Propositions: use `#prop[Title][Statement]`
- Proofs: use `#proof[Content]`
- Lemmas: use `#lem[Title][Statement]`
- Remarks: use `#rem[Title][Content]`
- Assumptions: use `#asp[Title][Statement]`
- Equations: use `#nneq($ ... $)` for numbered display equations
- Inline math: `$...$`

### 5. Derive comparative statics

After characterizing equilibrium, derive how the equilibrium changes with respect to key parameters. For each comparative static:

1. Take the derivative (implicit or explicit) of the equilibrium quantity with respect to the parameter
2. Sign the derivative using the model's assumptions
3. State the result as a corollary or part of the main proposition
4. Provide verbal intuition: "As [parameter] increases, [outcome] increases because [mechanism]"

The key comparative static for this paper should be: how does backsliding risk (probability of extraparliamentary action) change as (a) economic distress increases, (b) party gatekeeping capacity increases, and (c) both increase simultaneously.

### 6. Verify mathematical logic

Before finalizing, run this checklist on every proposition and proof:

**Logical consistency:**
- [ ] Does each step follow from the previous one?
- [ ] Are all assumptions used? (If an assumption is never invoked, it should be dropped---parsimony)
- [ ] Are no unstated assumptions smuggled in?
- [ ] Is the equilibrium concept appropriate for the information structure?

**Algebraic correctness:**
- [ ] Redo every derivation from scratch (do not copy-paste and modify)
- [ ] Check signs: does each inequality point the right way?
- [ ] Check boundary conditions: what happens at extreme parameter values?
- [ ] Verify second-order conditions where relevant

**Internal consistency:**
- [ ] Does the notation match the rest of `paper/paper.typ`?
- [ ] Are variable names consistent across all propositions?
- [ ] Do the comparative statics align with the verbal argument in the introduction?
- [ ] Does the equilibrium prediction match what the empirics find?

**Common errors to watch for:**
- Dividing by a quantity that could be zero
- Assuming a function is monotone without proving it
- Confusing necessary and sufficient conditions
- Using a result from one equilibrium in the analysis of another without justification
- Implicit assumption that parameters are in the interior of their domain

### 7. Connect to the empirics

After the model is complete, write a short subsection mapping model predictions to empirical tests:

- Which proposition corresponds to which regression table?
- Which parameter maps to which empirical variable?
- Are there predictions the model makes that the data cannot test? Flag these as directions for future work, not as claims.

This mapping is what makes the model worth including in the paper rather than being a standalone theory exercise.

## Model-Specific Context for This Paper

Read `paper/paper.typ` (especially the introduction and theory sections) to understand the paper's core argument before building any formal model. The model should capture:

- The paper's core mechanism (stated in the introduction)
- The key comparative statics that generate testable predictions
- An empirical mapping from model parameters to observable variables

Derive this context from the manuscript, not from assumptions.

## Citation Rules

- **Cite only what you have read:** Verify any cited theoretical result via RAG or PDF before referencing it. Never cite from title alone.
- **Zotero only:** Use `.claude/scripts/zotero_add.py` for missing references. Never edit `ref.bib` directly.

## Notation Standards

Load `references/notation-standards.md` when writing or editing any formal content. Consistency in notation across the model, the empirical sections, and the appendix is non-negotiable.

## Quick Reference: Common Issues

**Overbuilding** --- If you need more than 3-4 players or more than 2 stages to generate the result, the model is probably too complex. Strip it back and check whether a simpler structure delivers the same insight.

**Missing intuition** --- Every proposition needs a paragraph (before or after the proof) explaining in plain language why the result holds. "The proof is the intuition" is almost never true for a political science audience.

**Notation drift** --- The same quantity must have the same symbol everywhere. If organizational density is $D$ in the theory section, it cannot be "OrgDensity" in the empirical section without an explicit mapping.

**Proof by intimidation** --- Packing a proof with unnecessary generality or abstraction to make it look more impressive. This backfires with reviewers. State the result at the level of generality needed and no more.

**Unverified claims** --- Never write "it can be shown that" or "it is easy to verify." Either show it or put it in the appendix. If it truly is trivial, showing it takes one line.
