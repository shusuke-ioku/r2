# Skeptrustive Review Output Template

Use this template for all skeptrustive reviews. Adjust scope as needed---a single-claim check can omit the Literature Background and Summary Verdict sections.

---

```
## Skeptrustive Review: [Title or Section Name]

### Literature Background
- **Papers surveyed**: [List key papers found via RAG search, with brief relevance notes]
- **Notable citation gaps**: [Papers the target should cite but doesn't. Explain why each matters.]
- **Prior art concerns**: [Any overlap with existing work that threatens novelty. Be specific about what overlaps and what doesn't.]

If you skipped the literature search (because the user asked for logic-only review), state that explicitly and note that literature-grounded objections may be missing.

---

### Claim 1: [One-sentence statement of the claim in its strongest form]
- **Objection**: [The strongest attack. Steelman the claim first, then identify the real vulnerability. Cite published work where possible.]
- **Threat type**: [From the taxonomy: logical gap, empirical weakness, identification failure, alternative explanation, scope overreach, measurement concern, missing evidence, or non-novelty]
- **Severity**: Fatal / Serious / Minor
- **Constructive fix**: [Concrete suggestion: what to do, how to do it, what data or analysis is needed]
- **Feasibility**: Easy / Moderate / Hard
- **Notes**: [Optional. Additional context, related issues, or caveats about the fix.]

### Claim 2: [...]
[Repeat for each claim]

---

## Summary Verdict

- **Strongest elements**: [What survives scrutiny. Be specific---name the claims or analyses that hold up well and why.]
- **Critical fixes needed**: [Fatal and serious items, ranked by importance. The author should address these in order.]
- **Quick wins**: [Minor items that are easy to fix. These improve polish without requiring major effort.]
- **Overall assessment**: [One honest paragraph. What is the paper's current state? Is it close to publishable or does it need major revision? What is the single most important thing to fix?]
```

---

## Guidance on Each Section

### Literature Background
This section establishes your credibility as a reviewer. It shows you did your homework. It also serves the author by surfacing papers they may have missed. Do not list papers for the sake of listing them---each one should connect to a specific gap, contradiction, or alternative explanation you raise later.

### Claim-level entries
Each claim entry is self-contained. A reader should be able to understand the objection, its severity, and the fix without reading any other entry. This matters because authors often share specific review points with coauthors or advisors.

The one-sentence claim statement should be the *steelmanned* version. If you find yourself stating the claim in a way the author would disagree with, you have not steelmanned enough.

### Summary Verdict
The overall assessment should be honest but not cruel. Avoid vague praise ("interesting paper") and vague criticism ("needs more work"). Be specific: "The identification strategy is sound but the mechanism evidence in Section 4 relies on a single proxy that three published papers have criticized. Addressing this---either by adding the alternative proxy from [Author Year] or by reframing the mechanism claim as suggestive---would move this from major-revision territory to minor-revision."
