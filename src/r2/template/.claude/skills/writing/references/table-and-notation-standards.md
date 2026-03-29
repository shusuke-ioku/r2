# Table and Notation Standards

Detailed formatting rules for tables, figure captions, and equations in `paper/paper.typ`. Load this file whenever creating or editing any of these elements.

## Table Titles

Every table and figure title states the **finding**, not the content. A reader skimming titles alone should grasp the paper's argument. Titles are the first thing a reviewer reads after the abstract; they set expectations for what the table shows.

- Good: "Neither Economic Conditions nor Perpetrator Proximity Predict Mobilization"
- Bad: "Placebo Test Results"
- Good: "Organizational Growth Concentrates in Peripheral Regions"
- Bad: "Summary Statistics by Region"

## Standard Table Format

Every table in this paper uses exactly the same Typst format. Visual consistency signals careful craftsmanship; inconsistency signals rushed work. Before creating or editing any table, read at least one existing table in `paper/paper.typ` and replicate its structure precisely.

### Structure

- **Wrapper**: `#figure(block(width: 100%)[#set text(size: 0.8em) #table(...)])` with `caption-with-note(...)`.
- **Caption**: `caption-with-note([Finding-based title], [Note text])`.

### Rules and Lines

- **Stroke**: `stroke: none`; draw all rules via `table.hline()`.
  - Top and bottom borders: `table.hline(stroke: 1.2pt)`.
  - Major separators (below header row, above controls section): `table.hline(stroke: 0.4pt)` or `0.7pt`.
  - Minor separators (within controls or fit statistics): `table.hline(stroke: 0.2pt)`.

### Layout

- **Alignment**: first column `left`, all others `center`.
- **Inset**: `(x: 4pt, y: 4pt)`.
- **Column headers**: numbered `[(1)], [(2)], ...` in a dedicated row.

### Standard Information Set (Regression Tables)

Every regression table follows this exact row sequence. Do not omit sections, reorder them, or invent alternatives.

1. **Outcome row** — bold, spanning all columns: `table.cell(colspan: N)[*Outcome Name (unit)*]`
2. **Model numbers** — `[(1)], [(2)], ...` in a dedicated row
3. **Post-treatment window** — `[+12m], [+24m], [~Feb 36], [~Jul 37]` or equivalent
4. **Pre-treatment mean [SD]** — spanning all columns: `table.cell(colspan: N)[value [SD]]`. Include the group qualifier in brackets, e.g., `[Pre-treat. mean [SD] (NP)]`
5. `table.hline(stroke: 0.7pt)` — separates header from coefficients
6. **Coefficient rows** — bold variable name, estimate + SE (+ Conley SE in brackets if applicable), one row per coefficient. Use `#linebreak()` between estimate, parenthesized SE, and bracketed Conley SE
7. `table.hline(stroke: 0.2pt)` — separates coefficients from controls
8. **_Controls_ section** — italic label `[_Controls_]` with empty spanning cell, then one row per control (Yes/No)
9. `table.hline(stroke: 0.2pt)` or `0.4pt` — separates controls from fit statistics
10. **_Fit Statistics_ section** — italic label `[_Fit Statistics_]` with empty spanning cell, then: Observations (always), plus as applicable: Matched prefectures, Within $R^2$, $R^2$, Treated/Control prefectures, Pre/Post-treatment periods
11. `table.hline(stroke: 1.2pt)` — bottom border

**Descriptive statistics tables** follow a different pattern (see @tab:descriptive_stats): column headers are $N$, Mean, SD, Min, Max, plus group means; rows are variables grouped by panel (Panel A: Outcome, Panel B: Covariates).

### Sections and Content

- **Section labels**: `[_Controls_]` and `[_Fit Statistics_]` (italic), each followed by `table.cell(colspan: N, "")`.
- **Coefficients**: point estimates in `$...$`, standard errors in parentheses via `#linebreak()`.
- **Stars**: `$^(*)$`, `$^(**)$`, `$^(***)$`.
- **Star legend**: always in the caption note, never in the table body. Standard: `$.^(***) $: 0.01, $.^(**)$: 0.05, $.^(*)$: 0.1.`
- **SE description**: always in the caption note. State what's in parentheses and brackets, e.g., "Clustered (Prefecture & Month) standard errors in parentheses; Conley spatial SEs (100 km cutoff) in brackets."
- **Notes**: via the second argument of `caption-with-note`. Do not use inline `table-note(...)` unless spanning a footer row.

### Caption Note Checklist

Every regression table caption note must include all of the following:
1. What the SE in parentheses is (clustering structure or jackknife)
2. What the SE in brackets is, if present (Conley with distance cutoff)
3. Star significance thresholds
4. Sample description (which prefectures, what matching was applied)
5. Any non-obvious coding (e.g., "non-speakers coded as zero")

### What Not to Do

Do not invent alternative layouts, even if they seem cleaner for a specific table. Consistency across all tables matters more than local optimization. If an existing table deviates from this format, flag it and fix it.

## Notation

All equations must use a single, consistent notation throughout the paper. Notation inconsistency is one of the easiest things for reviewers to catch and one of the most damaging to perceived rigor.

Before writing or editing any equation:
1. Read all existing equations in `paper/paper.typ`.
2. Match subscript conventions, index letters, and indicator-function style exactly.
3. Define any new indices in the surrounding text.
4. Check for collisions---ensure no index letter is reused for a different meaning.

If existing notation is inconsistent, fix the inconsistency across all equations rather than matching whichever one is closest.
