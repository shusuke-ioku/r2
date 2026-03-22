---
name: slides
description: >
  Creates and updates presentation slides (talk/slides.typ) and talking notes
  (talk/notes.md) to stay synchronized with the manuscript (paper/paper.typ).
  TRIGGER THIS SKILL whenever the user does ANY of the following: create slides,
  update slides, add a slide, revise a slide, sync slides with the paper, build
  a presentation, prepare a talk, make a deck, write talking notes, update notes,
  or anything that touches talk/slides.typ or talk/notes.md. Also trigger when
  the user says "update the talk," "sync the presentation," "add a slide for X,"
  "the slides are out of date," "prepare slides," "build the deck," "write notes,"
  or "update the notes." Also trigger whenever the paper's results, figures,
  argument, or structure change---the slides and notes must stay in sync. If the
  task involves talk/slides.typ, talk/notes.md, or presentation content in any
  way, this skill applies.
---

# Slides & Talking Notes

## Core Principle: Script First, Slides Second

**The talking script (`talk/notes.md`) is the primary artifact. Slides (`talk/slides.typ`) exist only to support the listener's comprehension of what the speaker is saying.** This means:

1. Always compose or update the **script first** — decide what to say, in what order, with what emphasis.
2. Then compose or update the **slides to facilitate** the script — each slide shows only what helps listeners follow the spoken argument (key terms, figures, tables, takeaway bullets).
3. Never design slides first and then write notes to match. The talk drives the visuals, not the other way around.

Keep both files synchronized with `paper/paper.typ` and presentation-ready at all times.

## Design Constraints

The slides follow a strict visual system. Every edit must preserve it.

### Single-line rule

Every bullet, sentence, or text fragment must fit on a single line at 22pt PT Sans on a 4:3 slide with 3em margins. This is the hardest constraint to enforce and the most important.

**How to enforce it:**
- Bullet text: aim for ~55 characters max (including the bullet marker). Anything longer will wrap.
- Equations: keep inline; break complex equations across multiple `one-by-one` steps rather than one long line.
- Table cells: abbreviate headers and use short labels. Prefer symbols over words when unambiguous.
- After every edit, compile with `typst compile --root . talk/slides.typ` and visually verify by opening the PDF. If a line wraps, shorten it---never increase margins or shrink font to compensate.
- Prefer em dashes (---) to parenthetical asides; they are shorter and scan faster.
- When condensing paper prose into bullet text, rewrite from scratch for the slide medium. Never paste paper sentences onto slides.

### Current design system

These rules are extracted from `talk/style.typ` and the existing slides. Follow them exactly:

| Element | Rule |
|---------|------|
| Page numbers | None. No footer, no slide counter. |
| Font | PT Sans, 22pt base. **Never shrink text** unless content physically cannot fit on one slide after all other options (rewording, splitting across slides, abbreviating) are exhausted. Smaller text is a last resort, not a layout tool. |
| Aspect ratio | 4:3 (`presentation-4-3`). |
| Margins | `top: 3em, rest: 3em`. |
| Animations | `one-by-one` from Polylux, with custom `section-gap: 0.4em` spacing between items. |
| Headings | Centered, 0.7em size. Set via `= Heading Text` inside `#slide[...]`. |
| Vertical alignment | `#set align(horizon)` at the top of almost every slide body. |
| Lists | **No top-level bullets.** Top-level content is plain text or `one-by-one` blocks. When sub-lists are used: `•` (bullet) for first level, `‣` (triangle) for second level, `–` (dash) for third. Indent: 1em. |
| Citations | 0.8em, grey (`rgb(169,169,169)`). Inline `@key` syntax. **Cite aggressively:** attach a citation to every empirical claim, theoretical concept, and literature reference on slides. More citations = more credibility. **`#linebreak()` is ONLY for citation overflow:** if a citation at the end makes the line too long, put `#linebreak()` before the citation so it drops to the next line. Do NOT use `#linebreak()` for any other purpose — use `one-by-one` blocks, list items, or natural paragraph flow instead. |
| Images | Relative paths starting with `../analysis/output/figures/`. Width varies per slide. **Always centered** (`#align(center)[#image(...)]`). |
| Arrows | Use `arrow.r.filled` (`$arrow.r.filled$`) as the default arrow symbol. Never use `→` or `arrow.r`. |
| Tables | `stroke: none` with manual `table.hline()` separators. **Maximize information:** include as many columns/rows as fit on one slide without wrapping. Abbreviate headers and use symbols to save space, but do not drop informative content just to look clean. |
| Handout mode | `#enable-handout-mode(true)` at the top of the file. |
| Title slide | Uses `#title-slide(title:, subtitle:, author:)`. |
| Bibliography | At the end: `#bibliography("../ref.bib")` with APSA style. |
| Section comments | `// ====` block-comment dividers between slides, `// %%%%` for major sections. |

### Structural patterns

- Each slide is `#slide[...]`. Never use `#pagebreak()` except before the bibliography.
- Content-heavy slides use `one-by-one[...][...][...]` to reveal items sequentially. **Each block should contain a meaningful chunk** (a full point with its sub-items, or a paragraph-level idea) — not one line per block. Put multiple related lines, list items, and their citations together in a single `][` block. Only split into separate blocks when there is a genuine pause point in the presentation.
- Figure slides: brief heading, then centered `#image(...)`, then interpretation text below **on the same slide**. Interpretation is mandatory — never show a figure without explaining what the audience should see. Use smaller text (e.g., `#text(size: 0.8em)[...]`) for interpretation lines so the image stays full-width; never shrink the image to make room. **One image per slide — never put two images on the same slide.** If the paper has a two-panel (2-column) figure, **always split**: generate separate single-panel plot files via R (add to the appropriate script) if they don't already exist, then show each panel on its own slide. Never display a combined multi-panel image on a slide.
- Result slides **must show two things**: (1) the model specification and (2) a simplified coefficient table. Present spec first via `one-by-one`, then the coeftable, then interpretation lines. Never show results without making the specification visible. **Use display math** (`$ ... $` on its own line) for model specification equations — never inline math. Display math is centered and readable.
- Two-column layout uses `#grid(columns: (...), ...)` — but only for text/table content, never for placing two images side by side.

## First Step: Ask About Talking Time and Formality

**Before doing any work on slides or notes, always ask the user two things together:**

1. **Talking time** — How many minutes is the talk? This drives slide count, detail level, and per-slide time budgets.
2. **Formality level (0–10)** — How formal is the setting? This drives the tone of the talking notes.
   - **0** = casual chat with friends/lab mates (colloquial, contractions, humor OK)
   - **3** = brown bag / workshop (relaxed but structured)
   - **5** = conference presentation (professional, clear, moderate formality)
   - **7** = invited talk / seminar (polished, authoritative)
   - **10** = job talk / keynote (maximally precise, no informality, every sentence deliberate)

**This is mandatory.** Do not skip this step even if there is an existing time allocation in `talk/notes.md` — the user may have a different slot or audience this time. Ask both questions in a single message.

If the user has already specified both values in the current conversation, do not ask again.

## Sync Protocol

When the paper changes, the slides and notes must follow. Run this protocol whenever:
- The user edits `paper/paper.typ` (results, argument, framing, figures)
- Analysis outputs change (new figures, updated tables)
- The user explicitly asks to sync

### Steps

1. **Ask about talking time and formality** (see above).
2. **Read the paper.** Read `paper/paper.typ` (at minimum: abstract, introduction, and any changed sections).
3. **Read the existing script and slides.** Read `talk/notes.md` and `talk/slides.typ` in full.
4. **Diff the argument.** Identify every place where the script/slides now diverge from the paper:
   - Changed numbers, coefficients, significance levels
   - New or removed figures
   - Reframed arguments or contributions
   - New robustness checks or mechanisms
5. **Update the script first.** Edit `talk/notes.md` to resolve every divergence. Decide what to say, in what order, with what emphasis. The script is the primary artifact.
6. **Proofread the script (mandatory).** Before touching slides, re-read the entire script end-to-end and check for:
   - **Logical gaps:** Does each slide's narration follow from the previous one? Is every claim set up before it is made?
   - **Speech flow:** Read it as if speaking aloud. Flag awkward phrasing, run-on sentences, or places where the speaker would stumble.
   - **Missing transitions:** Every slide should open with a bridge from the previous one. If the bridge is missing, add it.
   - **Redundancy:** If the same point is made twice, cut the weaker version.
   - **Overclaiming:** Check every causal claim, generalization, and interpretation against the evidence the paper actually provides. Downgrade language that oversteps (e.g., "proves" → "suggests," "caused" → "is associated with," "all" → "in this case"). The talk must never promise more than the data delivers.
   - **Self-correct** all issues found before proceeding. Do not move to step 7 until the script reads cleanly from start to finish.
7. **Update slides to match the script.** Edit `talk/slides.typ` so each slide supports the corresponding script section. Add visuals (figures, tables, key phrases) that help listeners follow the spoken argument. Remove slide content that has no corresponding narration.
8. **Enforce single-line rule.** After every slide edit, check that no text wraps. Rewrite any line that exceeds ~55 characters.
9. **Compile and verify.** Run `typst compile --root . talk/slides.typ` and fix all errors.

### What to sync

| Paper element | Slide element | Notes element |
|---------------|---------------|---------------|
| Abstract framing | Title slide subtitle, motivation slide | Motivation notes |
| Key numbers (coefficients, SEs, p-values) | Results table, interpretation bullets | Results narration |
| Figure files | `#image(...)` paths and captions. **For any 2-column figure in the paper, generate individual single-panel plots in the R script** (e.g., `fig_esplot_left.png`, `fig_esplot_right.png`) and use those on slides — never the combined image. | Figure walk-through text |
| Contribution claims | Conclusion slide | Conclusion wrap-up |
| Robustness checks | Robustness slide grid | Robustness narration |
| Identification strategy | ID strategy slide | ID strategy explanation |

### What NOT to sync

- Literature review depth: slides do not reproduce the full lit review, but **cite aggressively** on every claim.
- Methodological details: slides state the design, not the derivation.
- Appendix material: only include if it strengthens the talk flow.

## Writing for Slides (Not Paper)

Slides exist to help the audience follow the spoken script. Every element on a slide must answer: "What does the listener need to *see* right now to understand what the speaker is *saying*?"

- **Show, don't duplicate.** If the speaker says it, the slide doesn't need to spell it out. Slides show figures, tables, key terms, and takeaway phrases — not transcriptions of the talk.
- **One claim per bullet.** If a bullet has a comma followed by a second clause, split it.
- **No full sentences** unless they are a punchline (bold, centered, set apart).
- **Lead with the finding, not the method.** "NP orgs +100% after shock" not "DiD estimates show..."
- **Bold key phrases** sparingly: one bold per slide maximum, for the single most important takeaway.
- **Equations:** only include if they clarify the identification strategy. Typeset inline; never let an equation be the only content on a slide.
- **Slide–script alignment.** Each slide corresponds to a section of the script. If a script section has no visual that would help the listener, consider whether it needs its own slide or can share one with an adjacent section.

## Talking Notes

Every slide must have a corresponding entry in `talk/notes.md`. The notes are the speaker's script — what the presenter actually says while the slide is on screen.

### File format

`talk/notes.md` uses this structure:

```markdown
# Talking Notes: [Paper Short Title] (~[total]min, formality: [N]/10)

## Slide N: [Slide Heading] (~X min)

[Narration text — what to say out loud.]

---
```

- The top-level heading includes the total talk time and the formality level.
- Each `## Slide N:` section matches a slide in `talk/slides.typ` by order.
- The `(~X min)` annotation is the time budget for that slide.
- `---` separates slides.

### Time budget

The total talk time (specified by the user) must be allocated across slides. Rules:

- Title slide: 0 min (no narration).
- Motivation / framing slides: ~1.5–2 min each.
- Data / methods slides: ~1–1.5 min each.
- Results slides: ~1–1.5 min each (longer if the table is complex).
- Robustness / supplementary slides: ~0.5 min each.
- Conclusion: ~1 min.
- Sum of per-slide times must equal the total talk time (allow ±0.5 min slack).

When the user changes the total talk time, redistribute across slides proportionally. If talk time is cut, cut robustness and data description slides first; protect motivation and results.

### Writing notes (not slides)

Notes are spoken prose, not bullet points. Write them as the presenter would actually say the words. **The formality level (0–10) set by the user controls the register:**

| Formality | Tone | Example phrasing |
|-----------|------|-------------------|
| 0–2 | Casual, contractions, humor OK | "So here's the cool part..." |
| 3–4 | Relaxed but structured | "What's interesting here is..." |
| 5–6 | Professional, clear | "The key finding is..." |
| 7–8 | Polished, authoritative | "This result demonstrates..." |
| 9–10 | Maximally precise, deliberate | "The evidence indicates that..." |

Calibrate vocabulary, sentence length, hedging, and personality accordingly. At low formality, be natural and direct; at high formality, be exact and measured.

- **One idea per sentence.** If a sentence has two clauses joined by "and," split it.
- **Signal transitions explicitly.** Start slides with a bridge from the previous one: "So we've established X. Now the question is Y." The audience needs these signposts.
- **Name what the audience sees.** When a figure or table is on screen, tell the audience what to look at: "On the left panel, you see..." "The solid line is..."
- **Rehearsal-ready.** The notes should be readable aloud at natural speaking pace and fill roughly the allocated time. Rough guide: ~150 words per minute of speaking.
- **Bracketed stage directions** for animation cues: `[next click]`, `[point to figure]`, `[pause]`.
- **Do not duplicate slide text verbatim.** The notes explain and contextualize what the slides show. Reading bullets aloud is bad presenting.

### When to update notes and slides

The script is updated first whenever:
- The paper changes (new results, reframed argument, new figures).
- The total talk time or formality level changes.
- The user explicitly asks to update the talk.

Then slides are updated to match the revised script. If only a slide's visual layout needs fixing (e.g., a wrapping line), the slide can be edited without touching the script. But any change to *what is communicated* must start in the script.

## Compilation

After any edit:

```bash
typst compile --root . talk/slides.typ
```

If compilation fails, fix errors immediately---do not leave broken slides. Common issues:
- Missing figure files (check `../analysis/output/figures/` paths)
- Citation keys not in `../ref.bib`
- Typst syntax errors in table or equation markup
