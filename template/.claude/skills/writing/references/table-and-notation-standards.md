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

### Sections and Content

- **Section labels**: `[_Controls_]` and `[_Fit Statistics_]` (italic), each followed by `table.cell(colspan: N, "")`.
- **Coefficients**: point estimates in `$...$`, standard errors in parentheses via `#linebreak()`.
- **Stars**: `$^(*)$`, `$^(**)$`, `$^(***)$`.
- **Notes**: `table-note(...)` in a spanning `table.cell`, or via the second argument of `caption-with-note`.

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
