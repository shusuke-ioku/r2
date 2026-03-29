---
name: polishing
description: >
  Loop-until-convergence manuscript polish for journal submission. Dispatches three
  parallel assessors (proofreader, calibration assessor, humanizer), synthesizes their
  reports into a prioritized revision plan, implements revisions section-by-section via
  manuscript-writer, and re-assesses until no Critical or Important issues remain.
  Grounded in the empirical APSR/AJPS audit (findings from calibration-report.md,
  section-forms from 20+ papers). TRIGGER on: "polish", "submission prep", "APSR prep",
  "rewrite for submission", "tighten the paper", "convergence loop", "polish for journal",
  "submission polish", "make this APSR-ready", "publication polish", "final polish".
---

# Polishing Framework

Loop-until-convergence manuscript polish. This skill orchestrates `writing`, `proofreading`, and `humanizer` around a shared manuscript-calibration standard rather than letting each assessor use its own disconnected style logic.

## Shared Ground Truth

All assessment and revision work in this skill must be anchored in:

- `.claude/skills/writing/references/section-forms.md`
- `.claude/skills/writing/references/manuscript-calibration.md`
- `.claude/skills/writing/references/prose-standards.md`

These references define the common manuscript target for all assessors.

## Architecture

```
Orchestrator (polisher agent)
│
└── LOOP until convergence:
    │
    ├── Phase 1: ASSESS (3 parallel read-only subagents)
    │   ├── Proofreader → flow, logic, pacing, terms, structure
    │   ├── Calibration Assessor → verbs, hedging, assertiveness, benchmarks, word budget
    │   └── Humanizer Assessor → AI-tell detection
    │
    ├── Phase 2: SYNTHESIZE
    │   ├── Merge 3 reports, deduplicate, resolve conflicts
    │   ├── Priority-rank: Critical → Important → Polish
    │   ├── Compute word budget per section
    │   └── Present revision plan to user
    │
    ├── Phase 3: IMPLEMENT (sequential, section by section)
    │   ├── Dispatch manuscript-writer per section
    │   ├── Verify: typst compile + word count after each
    │   └── Track running total
    │
    └── Phase 4: CONVERGE?
        ├── Re-assess edited sections only
        └── Stop if convergence criteria met
```

## Phase 1: Assessment

### Dispatch Protocol

Launch all 3 assessors in parallel using the Agent tool. Each gets:
1. The paper path: `paper/paper.typ`
2. Their specific reference files (listed below)
3. The output template: `references/assessment-template.md`
4. Scope: full paper (iteration 1) or specific sections (iteration 2+)
5. Read-only constraint: "Do not edit any files. Produce a report only."

### Assessor 1: Proofreader

**Agent**: `proofreader` (existing, subagent_type: `proofreader`)
**Skill**: proofreading (refactored: 9 categories, no humanizer pass, no overclaiming/too-conceding)
**Focus**: reader experience — flow, continuity, pacing, section placement, and reader-state breakdowns

**Dispatch prompt template**:
```
Read paper/paper.typ from beginning to end. Evaluate the reader's experience
using the proofreading skill. Produce a structured report per
.claude/skills/polishing/references/assessment-template.md.

Scope: [full paper | sections X, Y, Z]

Shared manuscript calibrations:
- Do NOT flag main finding restated 3-5× with progressive precision (Finding 8)
- Flag if finding not stated by intro paragraph 2-3 (Finding 6)
- Flag conclusions > 700 words or introducing new analysis (Finding 7)
- Use manuscript-calibration.md as the paragraph-density and section-placement benchmark

Output format: assessment-template.md categories for Proofreader.
```

### Assessor 2: Calibration Assessor

**Agent**: `calibration-assessor` (new, subagent_type: `calibration-assessor`)
**References**: calibration-categories.md, manuscript-calibration.md, calibration-report.md, section-forms.md, prose-standards.md
**Focus**: manuscript prose calibration — verbs, hedging, assertiveness, paragraph economy, section benchmarks, word budget

**Dispatch prompt template**:
```
Read paper/paper.typ. Evaluate prose calibration against APSR/AJPS norms.
Load and apply every check in .claude/skills/polishing/references/calibration-categories.md.
Produce a structured report per .claude/skills/polishing/references/assessment-template.md.

Scope: [full paper | sections X, Y, Z + full word-budget recalculation]

Key references to load:
- .claude/skills/polishing/references/calibration-categories.md (your evaluation criteria)
- .claude/skills/writing/references/manuscript-calibration.md (shared manuscript norms)
- .claude/skills/writing/references/calibration-report.md (evidence base)
- .claude/skills/writing/references/section-forms.md (benchmarks)
- .claude/skills/writing/references/prose-standards.md (assertiveness, citation rules)

Conservative bias correction: if the text matches what actual APSR papers do
per calibration-report.md, do NOT flag it. The empirical audit is ground truth.

Output format: assessment-template.md categories for Calibration Assessor.
```

### Assessor 3: Humanizer Assessor

**Agent**: a general-purpose subagent loaded with the humanizer skill
**Skill**: humanizer
**Focus**: AI-writing tells — vocabulary, patterns, rhythm

**Dispatch prompt template**:
```
Read paper/paper.typ. Scan every paragraph for AI-writing tells using the
full pattern catalog from .claude/skills/humanizer/SKILL.md. Produce a
structured report per .claude/skills/polishing/references/assessment-template.md.

Scope: [full paper | paragraphs in sections X, Y, Z]

Calibration: academic prose legitimately sounds more formal than blog posts.
Do NOT flag standard academic register as "soulless." Focus on patterns that
would make a reviewer think "this reads like AI-generated text."

Output format: assessment-template.md categories for Humanizer.
```

---

## Phase 2: Synthesis

After all 3 assessors return, the orchestrator synthesizes:

### Step 1: Build unified issue table

Collect all issues from all 3 reports. Tag each with: assessor, section, category, priority, word impact.

### Step 2: Deduplicate

Same paragraph flagged by 2+ assessors → merge into single issue. Take the highest priority. Note which assessors flagged it (consensus issues get extra weight).

### Step 3: Resolve conflicts

| Conflict Pattern | Resolution |
|---|---|
| "Expand section" + "cut filler in section" | Compatible: add new substance, remove existing filler |
| Proofreader says "compressed" + Calibration says "within budget" | Proofreader wins (reader experience > arithmetic) |
| Calibration flags verb + Humanizer flags same sentence for AI tell | Both valid, merge: rewrite to fix both |
| Genuine disagreement | More specific diagnosis wins |

### Step 4: Priority-rank

Combine into three tiers:

**Critical** (must fix before submission):
- Structural deviations: finding deferred past intro para 4, standalone limitations section
- Logical gaps (from proofreader)
- Design-verb mismatch on main findings
- CW attributed to "scholars" as opening sentence

**Important** (should fix):
- Hedge asymmetry violations
- Topic-sentence failures (lit summary openers in theory/lit sections)
- Missing restatement locations
- Word-budget gaps > 30% of benchmark
- AI-tell clusters (3+ per section)
- Passive voice on core findings
- Contribution paragraphs not framed against specific prior work

**Polish** (fix if easy):
- Individual AI tells
- Minor pacing issues
- Single filler phrases
- Results paragraphs 1-2 sentences over benchmark

### Step 5: Conservative bias correction

From the 48-paper review calibration (March 2026): agents systematically over-flag.

Before finalizing the issue list:
- For each flagged issue, check: does the manuscript text match what actual APSR papers do per calibration-report.md?
- If yes → dismiss or downgrade to Polish
- Load `.claude/skills/review/references/common-errors.md` and check for known assessment failure modes

### Step 6: Compute word budget

1. Count words per section (strip Typst markup)
2. Map section → type by heading text
3. Load section-forms.md benchmarks:
   - Introduction: 1,500–2,500 words, 5–8 paragraphs
   - Theory/lit: 2,000–4,000 words, 8–15 paragraphs
   - Results subsections: 4–7 paragraphs, 4–7 sentences per paragraph
   - Conclusion: 300–700 words, 2–3 paragraphs
4. If user specified total target: distribute delta proportionally across sections with gaps
5. If no target: use section-forms midpoints as defaults
6. Output: word-budget table per section

### Step 7: Present revision plan

Format per `references/revision-plan-template.md`. Show:
- Word-budget table
- Issues by priority (Critical → Important → Polish)
- Consensus issues highlighted
- Conflicts resolved with reasoning
- Implementation order with rationale

**Wait for user approval before proceeding to Phase 3.**

---

## Phase 3: Implementation

### Implementation order

Default order (override if user specifies otherwise):
1. **Introduction** — most likely underweight; sets framing for everything else
2. **Conclusion** — bookend; "so what" should stabilize before body edits
3. **Body sections** — in order of issue density (most issues first)

### Per-section implementation

For each section with Critical or Important issues:

1. **Dispatch manuscript-writer agent** with:
   - The section's current text (read from paper.typ)
   - The filtered issue list for this section (from the revision plan)
   - The word budget for this section
   - Instruction: "Follow the writing skill and the shared manuscript-calibration references. Apply all listed fixes. Stay within the word budget."

2. **Verify after edit**:
   - `typst compile --root . paper/paper.typ` → must exit 0
   - Recount section words → within budget?
   - Read the edited section → does it address the listed issues?

3. **Track running total**: update cumulative word count. If overshooting total target, compress subsequent sections more. If undershooting, allow expansion.

4. **Skip clean sections**: if a section has only Polish-level issues and the user didn't explicitly request Polish fixes, skip it.

---

## Phase 4: Convergence Check

After implementation, re-assess to check for issues introduced by edits.

### Re-assessment scope

- **Sections**: only sections that were edited + their immediate neighbors (for transition continuity)
- **Assessors**: all 3, but scoped to the edited sections
- **Humanizer**: only edited paragraphs

### Convergence criteria

| Criterion | Threshold |
|---|---|
| Zero Critical issues | 0 remaining (non-negotiable) |
| Zero Important issues | 0 remaining, or user explicitly defers |
| Issue delta | < 3 new issues from re-assessment, all Polish level |
| Max iterations | 3 (configurable via user instruction) |
| Word count | Within ±500 of target (if target specified) |
| User override | "stop" at any checkpoint |

If **any** criterion triggers DONE → report results and stop.
If **none** triggers → present new issues to user, get approval, implement next iteration.

### Final output

When convergence is reached:
```
## Polish Complete — Iteration [N]

### Changes Made
[Section-by-section summary of what changed]

### Word Count
| Section | Before | After | Delta |
...
| Total | N | N | ±N |

### Remaining Issues
[Any deferred Polish-level issues, if any]

### Verification
- typst compile: [exit 0 / error]
- Abstract: [N words, under/over 150]
- Total words: [N, within/outside target band]
```

---

## Integration Map

| Existing Asset | Role in Framework |
|---|---|
| `writing` skill | Implementation standard. Manuscript-writer loads it for all edits. |
| `proofreading` skill | Assessor 1's evaluation criteria (9 categories). |
| `humanizer` skill | Assessor 3's pattern catalog. |
| `verification` skill | Gates each section completion + final completion. |
| `parallel-dispatch` skill | Governs parallel assessor dispatch. |
| `manuscript-writer` agent | Delegated to for section-level rewrites. |
| `calibration-report.md` | Assessor 2's evidence base (APSR/AJPS audit findings). |
| `section-forms.md` | Assessors 1+2's structural benchmarks. |
| `prose-standards.md` | Assessor 2's assertiveness + citation rules. |
| `review` skill | NOT invoked. Review is separate from polish. |

---

## Standalone vs. Polishing-Loop Usage

When the writing or proofreading skills are invoked **outside** the polishing loop (e.g., user asks to rewrite a single paragraph), they operate as before: the writing skill applies its 4 principles and steps 1–6; the proofreading skill reads sequentially and flags 9 categories. The polishing loop adds orchestration, convergence iteration, and word-budget discipline on top.
