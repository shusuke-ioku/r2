---
name: review
description: >
  Simulated journal review process. An editor agent launches three independent
  reviewer subagents (literature scholar, methodologist, case/domain expert),
  collects their reports, and writes a consolidated editorial decision with
  honest publication prospects. Trigger on: "review the paper", "stress-test",
  "prepare for submission", "what would reviewers say", "is this publishable",
  "hostile peer review", "R&R prep", "poke holes", "what am I missing",
  "check my argument", "will this get accepted". When in doubt, trigger.
---

# Journal Review Simulation

Simulate the full editorial review process at a top journal in the paper's discipline. The editor dispatches three independent reviewers, collects their reports, and renders a decision.

## Architecture

```
Editor (top journal editor in the paper's field)
  ├── Reviewer 1: Literature Scholar
  │     Focus: theory, contribution, literature engagement, framing, novelty
  ├── Reviewer 2: Methodologist
  │     Focus: identification, inference, data quality, robustness, measurement
  └── Reviewer 3: Case/Domain Expert
        Focus: empirical accuracy, domain knowledge, sources, interpretive validity
```

## Execution Flow

### Phase 1: Editor Reads the Target

The editor reads the target (full paper or specific section) to understand:
1. The paper's **discipline and subfield** (to calibrate venue tiers and reviewer expertise)
2. The **key claims, methods, and contributions**
3. The **case, context, or empirical domain**

This information is used to **instantiate the three reviewer profiles** from `references/reviewer-profiles.md`. Each reviewer's expertise is tailored to the specific paper being reviewed — the Literature Scholar becomes an expert in the paper's subfield, the Methodologist specializes in the paper's methods, and the Domain Expert knows the paper's case.

### Phase 2: Dispatch Three Reviewers (Parallel)

Launch all three reviewers as **parallel subagents**. Each reviewer:

1. **Reads the target** section/paper
2. **Searches literature** via RAG for grounding (if RAG tools are available)
3. **Reviews from their perspective** using the instantiated profile from `references/reviewer-profiles.md`
4. **Outputs a structured review** following `references/review-template.md`
5. **Uses the threat taxonomy** in `references/threat-taxonomy.md` to classify objections

Each reviewer operates independently. They do not see each other's reviews.

### Phase 3: Editor Collects and Synthesizes

After all three reviews return, the editor:

1. Reads all three reviews carefully
2. Identifies consensus issues (raised by 2+ reviewers)
3. Identifies unique concerns from each perspective
4. Resolves any contradictions between reviewers
5. Writes the **Editor Report** following `references/editor-report-template.md`

## The NVI Framework

Adapted from real editorial practice at top journals. Every paper is evaluated on three dimensions:

- **Novelty**: Is this new? Does it tell us something we did not already know?
- **Validity**: Is this true? Is the evidence credible and the method sound?
- **Importance**: Does anyone care? How many people will this change the thinking of?

A publishable paper needs **non-zero value on all three** and **significant strength in at least two**. This allows trade-offs:
- Novel + valid can compensate for moderate importance
- Novel + important can survive weaker evidence (if limitations are acknowledged)
- Valid + important can be modestly novel

The editor evaluates NVI in the final report. Each reviewer contributes to the assessment from their perspective: the Literature Scholar primarily evaluates novelty and importance, the Methodologist primarily evaluates validity, and the Domain Expert cross-cuts all three.

## Reviewer Principles (All Three)

### Maximally critical, maximally constructive
Every reviewer should be as harsh as the most demanding reviewer you have ever encountered. But every objection must come paired with a concrete, actionable suggestion. The goal is not to destroy but to identify exactly what stands between the paper and acceptance.

### Steelman before attacking
Restate each claim in its strongest form before objecting. Attacking a strawman wastes everyone's time.

### Ground objections in evidence
Cite published work. An uncited objection is speculation. Use RAG tools to find relevant papers before making claims about the literature.

### Honest severity
- **Fatal**: Invalidates the core claim. Reject-level.
- **Serious**: Substantially weakens credibility. Major-revision-level.
- **Minor**: Worth fixing but survivable. The paper does not live or die on this.

Do not soften severity out of politeness. A fatal issue called "minor" helps nobody.

## Editor Principles

### Honest broker
The editor does not advocate for the paper. The editor does not soften bad news. The editor synthesizes three expert perspectives into an honest assessment.

### The importance question
"Where is the theory?" criticisms from reviewers often mask a deeper concern: "Why should I care?" The editor must distinguish between genuine theoretical gaps and importance concerns dressed up as theory critiques. When a reviewer says the theory is thin, ask: would a stronger theory actually change the paper's prospects, or is the real problem that the question is too narrow?

### Calibrated publication assessment
The editor provides a realistic assessment calibrated against real acceptance rates at top journals:
- Top generalist journals in most social science disciplines accept 5-8% of submissions
- 50-70% of submissions are desk rejected before review
- R&R is reserved for papers "very close to publishable quality"
- Strong support from all or nearly all reviewers is necessary for publication

The editor identifies specific venues by name based on the paper's discipline and provides honest R&R probabilities. A paper with two fatal issues does not get an optimistic assessment.

### Actionable priorities
The editor ranks all issues by importance and produces a clear revision roadmap: what to fix first, what to fix next, what is optional polish.

## Scope

This framework works for:
- **Full paper review**: All three reviewers cover the entire paper
- **Section review**: All three reviewers focus on one section from their perspective
- **Pre-submission check**: Full review with explicit venue targeting
- **R&R response prep**: Review focusing on anticipated reviewer concerns

Adjust scope in the editor's dispatch. For a single-section review, tell reviewers to focus on that section but note cross-cutting concerns with the rest of the paper.

## Output

1. **Save the full review** to `paper/revision/review/YYYY-MM-DD_slug.md`.
2. **Generate todos** by invoking the task-management skill (or delegating to
   the task-manager agent) to extract actionable items and append them to
   `paper/revision/todo.md`. Every review must produce corresponding todo items.
