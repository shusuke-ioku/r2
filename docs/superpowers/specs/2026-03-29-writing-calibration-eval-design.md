# Writing-Calibration Eval Infrastructure

**Date**: 2026-03-29
**Status**: Approved design
**Feature**: `dev/calibration/writing-calibration/`

## Problem

The writing-calibration feature refactored `writing`, `proofreading`, and `polishing` skills around a shared `manuscript-calibration.md` reference layer, grounded in an 80-paper corpus. But the feature cannot prove the refactor helped: all 3 evals in `eval-set.json` are `"grading": "human"`, `history.json` is empty, and no baseline snapshot exists. The spec's own criterion 3 (integrated eval set) is unmet.

## Solution

Build an automated hybrid eval infrastructure: synthetic fixtures with planted anti-patterns, structural checks that run programmatically, and LLM-as-judge prompts for judgment calls that require reading comprehension.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Grading approach | Hybrid (structural + LLM-as-judge) | Structural catches countable signals cheaply; LLM-as-judge handles judgment calls |
| Fixture type | Synthetic with planted anti-patterns | Known answer key enables deterministic grading |
| Fixture granularity | Atomic (one anti-pattern family per fixture) | Pass/fail maps directly to one skill behavior; regressions are diagnosable |
| Fixture count | 8 across 3 skills | Covers all major anti-pattern families |
| Runner | Python script in `scripts/` | Matches existing `dev/scripts/` convention |
| LLM-as-judge execution | Generate prompts for manual run | No API key dependency; upgrade to direct API later |

## Directory Structure

```
dev/calibration/writing-calibration/
├── eval/
│   ├── eval-set.json              # 8 atomic fixtures with structural + judge criteria
│   ├── fixtures/                   # synthetic manuscript excerpts
│   │   ├── writing/
│   │   │   ├── intro-background-accretion.md
│   │   │   ├── intro-fragmentation.md
│   │   │   ├── results-drift.md
│   │   │   └── conclusion-soft-landing.md
│   │   ├── proofreading/
│   │   │   ├── delayed-finding.md
│   │   │   ├── broken-continuity.md
│   │   │   └── calibration-break.md
│   │   └── polishing/
│   │       └── integrated-section-set.md
│   └── rubrics/                    # per-fixture grading criteria
│       └── <fixture-name>.json
├── scripts/
│   └── run_eval.py                 # eval runner
├── results/                        # graded outputs per run
│   └── <timestamp>/
│       ├── outputs/                # skill outputs saved here manually
│       ├── structural-results.json
│       └── judge-prompts/
│           └── <fixture-name>-judge.md
└── history.json                    # scored runs appended here
```

## Fixture Design

Each fixture is a Markdown file with YAML frontmatter specifying planted anti-patterns and expected grading criteria.

### Frontmatter Schema

```yaml
---
fixture: <name>
skill: writing | proofreading | polishing
planted_antipatterns:
  - id: <antipattern-name>
    location: <where in the text>
    description: <what's wrong>
expected_behavior:
  - <human-readable expectation for what the skill should do>
structural_checks:
  - type: <check-type>
    <check-specific-params>
judge_criteria:
  - <criterion the LLM-as-judge evaluates>
---
```

### Structural Check Types

| Check type | Parameters | Runs on | Logic |
|------------|-----------|---------|-------|
| `max_paragraph_count` | `target`, `threshold` | skill output | count paragraphs in target section, fail if > threshold |
| `min_words_per_paragraph` | `target`, `threshold` | skill output | mean words per paragraph, fail if < threshold |
| `finding_by_paragraph` | `threshold` | skill output | paragraph index of first ownership verb (`I show`, `we find`, etc.), fail if > threshold |
| `absent_phrase` | `phrases` | skill output | fail if any listed phrase appears |
| `present_phrase` | `phrases` | skill output | fail if any listed phrase is absent |
| `max_word_count` | `target`, `threshold` | skill output | word count of target section, fail if > threshold |
| `same_paragraph` | `phrases` | skill output | fail if the listed phrases appear in different paragraphs |
| `issue_category_rank` | `expected_top_categories`, `n` | skill output (report) | fail if the top-n issues are not from the expected categories |
| `line_edit_ratio` | `max_ratio` | skill output (report) | fail if proportion of word-choice/grammar issues exceeds max_ratio |

### The 8 Fixtures

#### Writing Skill (4 fixtures)

**1. `intro-background-accretion.md`**
- Planted: 3 paragraphs of broad democratic-breakdown motivation, "scholars have argued" hearsay CW, finding deferred to paragraph 5
- Structural checks: `finding_by_paragraph` <= 3, `max_paragraph_count` <= 4, `absent_phrase` ["scholars have argued", "the literature suggests"]
- Judge criteria: rewrite compresses motivation into one paragraph and moves ownership forward

**2. `intro-fragmentation.md`**
- Planted: 7 micro-paragraphs each <80 words covering puzzle, lit, gap, method, data, finding, contribution separately
- Structural checks: `max_paragraph_count` <= 4, `min_words_per_paragraph` >= 150
- Judge criteria: rewrite merges thin paragraphs into dense argumentative units without losing content

**3. `results-drift.md`**
- Planted: paragraph 1 says "Table 1 reports...", paragraph 2 states the actual finding, coefficients arrive sentence 4 of paragraph 2
- Structural checks: `same_paragraph` ["Table 1", main-finding-phrase], `finding_by_paragraph` <= 1 (within the results section)
- Judge criteria: rewrite places table reference and substantive result in the same paragraph with magnitude within 2 sentences

**4. `conclusion-soft-landing.md`**
- Planted: 5-paragraph conclusion re-running the paper, ending with "more research is needed" and generic future-work
- Structural checks: `max_paragraph_count` <= 3, `max_word_count` <= 700, `absent_phrase` ["more research is needed"]
- Judge criteria: rewrite closes on implication, not recap or apology

#### Proofreading Skill (3 fixtures)

**5. `delayed-finding.md`**
- Planted: intro where finding appears at paragraph 4 after 3 paragraphs of case context and literature staging
- Structural checks: `issue_category_rank` top-3 includes "section form deviation" or "background accretion", `line_edit_ratio` <= 0.3
- Judge criteria: report diagnoses delayed finding as a reader-state problem, not a word-choice problem; does not devote majority of report to sentence-level fixes

**6. `broken-continuity.md`**
- Planted: "organizational density" used in paragraph 2 without definition (defined in paragraph 8); results section references "the mechanism described in Section 4" when reader is in Section 3
- Structural checks: `present_phrase` in issue list ["undefined", "forward reference" or "not yet"], `line_edit_ratio` <= 0.3
- Judge criteria: report identifies both continuity breaks with correct location; proposes structural fix (move definition, reorder sections) not just rewording

**7. `calibration-break.md`**
- Planted: paper uses IV design but hedges main finding with "may suggest", "appears to be consistent with", "tentatively indicates"
- Structural checks: `issue_category_rank` top-3 includes "calibration break", `line_edit_ratio` <= 0.3
- Judge criteria: report flags underhedging as a calibration failure that damages reader trust; does NOT spend the majority of the report on word-choice or AI-tell cleanup

#### Polishing Skill (1 fixture)

**8. `integrated-section-set.md`**
- Planted: intro with background accretion (1 problem), results section with drift (1 problem), conclusion with soft landing (1 problem)
- Structural checks: synthesis mentions all 3 sections, routes intro issue to writing or calibration assessor, routes results issue correctly, ranks manuscript-level issues above word-choice
- Judge criteria: the revision plan prioritizes structural manuscript issues over surface polish; assessor reports are distinguishable (proofreader catches reader-state, calibration assessor catches norms, humanizer catches AI tells — not all three flagging the same things)

## Runner: `run_eval.py`

### Workflow

```
1. User runs skill on fixture manually, saves output to results/<timestamp>/outputs/<fixture>.md
2. User runs: python scripts/run_eval.py --timestamp <timestamp> [--fixture <name>]
3. Runner reads fixtures, parses frontmatter for expected checks
4. Runner reads skill output from results/<timestamp>/outputs/
5. Runner executes structural checks → writes structural-results.json
6. Runner generates LLM-as-judge prompts → writes to judge-prompts/
7. Runner appends structural pass/fail to history.json
8. User runs judge prompts manually, records pass/fail back into results
```

### CLI Interface

```
python scripts/run_eval.py --timestamp 2026-03-29T14:30 [--fixture intro-background-accretion] [--skill writing]
```

- `--timestamp`: required, identifies the results directory
- `--fixture`: optional, run only one fixture (default: all)
- `--skill`: optional, run only fixtures for one skill (default: all)

### Output: `structural-results.json`

```json
{
  "timestamp": "2026-03-29T14:30",
  "results": [
    {
      "fixture": "intro-background-accretion",
      "skill": "writing",
      "checks": [
        {"check": "max_paragraph_count", "threshold": 4, "actual": 3, "pass": true},
        {"check": "finding_by_paragraph", "threshold": 3, "actual": 2, "pass": true},
        {"check": "absent_phrase", "phrases": ["scholars have argued"], "found": false, "pass": true}
      ],
      "structural_pass": true,
      "judge_pending": true
    }
  ]
}
```

### Output: Judge Prompt

Each `<fixture>-judge.md` contains:
1. The original fixture (with planted anti-patterns listed)
2. The skill output
3. The judge criteria from the fixture frontmatter
4. Instructions to return pass/fail per criterion with one-sentence reasoning

### Output: `history.json` Update

```json
{
  "feature": "writing-calibration",
  "runs": [
    {
      "timestamp": "2026-03-29T14:30",
      "structural": {"pass": 7, "fail": 1, "total": 8},
      "judge": {"pass": null, "fail": null, "total": 8, "pending": true},
      "notes": ""
    }
  ]
}
```

## Fixture Content Guidelines

Each synthetic fixture should read like a plausible political science manuscript excerpt. Use the calibration corpus as a style reference:

- **Topic**: democratic institutions, authoritarian consolidation, electoral behavior, or similar (matches the user's research domain)
- **Length**: intro fixtures ~500-800 words, results fixtures ~300-500 words, conclusion fixtures ~400-600 words, integrated fixture ~1200-1800 words
- **Anti-patterns**: planted naturally — not cartoonishly bad, but clearly violating the manuscript-calibration norms
- **Signal strength**: each planted anti-pattern should be unambiguous enough that a well-calibrated skill should catch it, but realistic enough that it tests genuine skill discrimination

## Scope Boundaries

**In scope for this spec:**
- 8 synthetic fixtures
- Per-fixture rubric JSON files
- `run_eval.py` with structural checks and judge-prompt generation
- Updated `eval-set.json` and `history.json` schema

**Out of scope (future work):**
- Real corpus excerpts as fixtures
- Direct API calls for LLM-as-judge
- Automated skill invocation (user runs skills manually)
- Baseline snapshot of pre-refactor skill behavior (separate task)
- Corpus-wide results/conclusion analysis (Phase 2 of the improvement plan)
