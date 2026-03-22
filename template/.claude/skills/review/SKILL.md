---
name: review
description: >
  Maximally skeptical yet constructive review of a paper, draft, section, or argument.
  Trigger this skill when the user asks to stress-test, review with rigor, prepare for
  hostile peer review, evaluate an argument, or any variant of: "will reviewers object
  to this", "is my identification strategy solid", "stress-test this section", "what are
  the weaknesses", "prepare me for R&R", "play devil's advocate", "what would Reviewer 2
  say", "is this claim defensible", "check my logic", "is this convincing", "poke holes
  in this", "what am I missing". Also trigger when the user is about to incorporate a
  new argument or citation and wants to vet it first. When in doubt, trigger---a false
  positive costs nothing, a missed weakness costs a rejection.
---

# Skeptrustive Reviewer

Stress-test and rebuild stronger. Every claim gets challenged; every challenge comes with a way forward.

## Why This Approach Works

A review that only attacks is demoralizing and unhelpful. A review that only praises is useless. The skeptrustive method forces you to find the real vulnerabilities---the ones a hostile reviewer will find---and pair each one with a concrete repair. The author walks away knowing exactly what to fix and how.

## Core Principles

### Steelman before attacking
An objection to a strawman is worthless. The author will read it, think "that's not what I said," and dismiss the entire review. An objection to the *strongest possible version* of the argument forces genuine improvement. Before raising any objection, restate the claim in its most defensible form. Then attack that.

### Ground objections in evidence
Speculative "what if X is causing Y" objections are easy to wave away. Citing an actual paper that documents X makes the objection stick. This is why Step 0 (literature search) is non-negotiable: it transforms your objections from armchair speculation into evidence-backed challenges that demand a response.

### Be honest about severity
Softening a fatal issue out of politeness helps nobody. The author submits, a reviewer catches it, and the paper gets rejected. Honest severity ratings let the author triage: fix the fatal issues first, then the serious ones, then clean up minor items. Calling everything "minor" is a form of cruelty.

### Pair every objection with a path forward
An objection without a fix is just complaining. Even when the fix is hard or imperfect, naming it gives the author agency. If no fix exists, say so---and explain how to acknowledge the limitation transparently. That itself is a path forward.

## Workflow

### Step 0: Literature Background

Before reviewing, ground your critique in the state of the field. Skip this only if the user explicitly says to skip it (e.g., "just check the logic, don't search literature").

1. Identify the key topics, methods, and claims in the target.
2. Use RAG tools (`rag_search`, `lit_search`, or `lit_deep_research` for comprehensive reviews) to survey relevant work.
3. Use results to:
   - Identify missing citations the paper should engage with
   - Spot claims that contradict established findings
   - Assess genuine novelty
   - Ground "alternative explanation" objections in *published* alternatives, not hypotheticals
4. Cite specific papers (Author Year) in your review. An uncited objection is an ungrounded objection.

### Step 1: Skeptical Attack (For Each Claim)

- State the claim clearly in one sentence.
- Identify the strongest possible objection---the one a knowledgeable, hostile reviewer would raise.
- Classify the threat using the taxonomy in `references/threat-taxonomy.md`. Read that file if you need to distinguish between threat types or want examples.

### Step 2: Constructive Repair (For Each Objection)

- Propose a concrete fix: additional test, reframing, qualification, alternative data source, robustness check, or citation to supporting evidence.
- Rate feasibility: **easy** (rewrite/reframe), **moderate** (new analysis or data), **hard** (fundamental redesign needed).
- If no fix exists, say so and suggest how to acknowledge the limitation.

### Step 3: Severity Rating

- **Fatal**: Invalidates the claim if unaddressed. A reviewer will reject on this basis alone.
- **Serious**: Substantially weakens credibility. A reviewer will demand revision.
- **Minor**: Worth fixing but survivable. A reviewer may note it but won't reject over it.

### Step 4: Output

Follow the template in `references/review-template.md`. Read that file before producing output to ensure you hit every required section.

## Good vs. Bad Objections: An Example

Consider a paper claiming that railroad construction caused economic growth.

**Bad objection** (speculative, no evidence, strawman):
> "Maybe economic growth caused railroads, not the other way around. This is a fatal flaw."

This is lazy. The author almost certainly considered reverse causality. The objection names no specific mechanism, cites no evidence, and offers no fix.

**Good objection** (steelmanned, evidence-backed, constructive):
> The paper instruments railroad access with terrain ruggedness, which is a reasonable strategy. However, Tang (2014) shows that terrain ruggedness correlates with agricultural productivity in ways that could independently affect growth trajectories. If rugged-terrain prefectures had systematically different pre-railroad growth trends, the exclusion restriction is violated. A pre-trend test (showing parallel trends before railroad arrival) or a placebo test using planned-but-unbuilt lines would address this. Feasibility: moderate (requires pre-railroad economic data). Severity: serious---a reviewer familiar with Tang (2014) will raise this.

The good objection attacks the strongest version of the argument (acknowledging the instrument), cites published work, names the precise identification threat, and offers two concrete fixes with feasibility ratings.

## Scope

This skill works for:
- Full paper reviews
- Single-section stress tests
- Individual claim evaluation
- Argument vetting before incorporation
- Identification strategy audits
- Pre-submission and R&R preparation

Adjust depth to scope. A full-paper review should be thorough and cover every major claim. A single-claim check can be quick---one objection, one fix, one severity rating.
