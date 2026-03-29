# Feedback Template

Fill in every section. If a section is genuinely not applicable, write "N/A"
with a one-line explanation of why.

## Source

[Author (Year). Title. Venue.]

## Core Claim (3-5 bullets)

State the paper's main argument in your own words. Each bullet should be a
self-contained claim, not a section summary. Focus on what the paper argues,
not what it "discusses" or "explores."

1.
2.
3.

## Strongest Contributions

What does this source do well? Be specific -- name the exact design choice,
theoretical move, or empirical finding that is genuinely strong. Avoid generic
praise ("interesting contribution").

1.
2.

## Main Weaknesses / Risks

Identify the most consequential limitations. Prioritize threats that matter
for whether the user should rely on this source. For each weakness, note
whether it is fixable (the author could address it with more data or analysis)
or structural (inherent to the design).

1.
2.
3.

## What Changes in My Project

Translate the evaluation into concrete project-level decisions.

- **Keep**: What in the current project is validated or supported by this
  source? (Be specific: name the section, variable, or modeling choice.)
- **Revise**: What should change in light of this source? (A framing shift, an
  additional control, a different way of discussing a mechanism, etc.)
- **Drop**: What should the project stop doing or stop citing based on this
  source? (If nothing, say so.)

## Actionable Edits

For each edit, name the specific file and location that would change. An edit
without a target is not actionable.

1. **Theory edits**: Changes to theoretical framing or mechanism discussion in
   `paper/paper.typ`.
2. **Model / specification edits**: Changes to regression specifications,
   controls, or sample definitions in `analysis/scripts/`.
3. **Data / codebook edits**: New variables, recoding, or documentation updates
   in `analysis/data/codebook.md`.
4. **Manuscript framing edits**: Changes to how the paper positions itself
   relative to the literature, including updates to relevant MOCs in `library/lit/`
   and atomic paper notes in `library/papers/`.

## Priority List

- **P0 (do now)**: Edits that affect the paper's correctness or a reviewer
  would flag as an error. These cannot wait.
- **P1 (do next)**: Edits that meaningfully improve the paper but are not
  urgent. Schedule for the next revision pass.
- **P2 (optional)**: Nice-to-have improvements, future extensions, or
  speculative ideas worth recording but not acting on immediately.
