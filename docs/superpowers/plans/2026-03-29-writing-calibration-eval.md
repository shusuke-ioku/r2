# Writing-Calibration Eval Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 8 atomic synthetic fixtures with hybrid grading (structural checks + LLM-as-judge prompts) so the writing-calibration feature can measure skill improvement without human judgment.

**Architecture:** Each fixture is a Markdown file with YAML frontmatter listing planted anti-patterns and expected structural checks. A Python runner (`run_eval.py`) reads skill outputs saved by the user, runs structural checks, generates LLM-as-judge prompts, and updates `history.json`.

**Tech Stack:** Python 3.12 (stdlib only: `argparse`, `json`, `re`, `pathlib`, `datetime`, `yaml` via simple custom parser — no pip dependencies)

**Base directory:** `dev/calibration/writing-calibration/` (all paths below are relative to this)

---

### Task 1: Scaffold directory structure and update eval-set.json

**Files:**
- Create: `eval/fixtures/writing/` (directory)
- Create: `eval/fixtures/proofreading/` (directory)
- Create: `eval/fixtures/polishing/` (directory)
- Create: `eval/rubrics/` (directory)
- Create: `results/` (directory)
- Modify: `eval/eval-set.json`

- [ ] **Step 1: Create directories**

```bash
cd "dev/calibration/writing-calibration"
mkdir -p eval/fixtures/writing eval/fixtures/proofreading eval/fixtures/polishing eval/rubrics results
```

- [ ] **Step 2: Replace eval-set.json with new atomic fixture list**

Replace the contents of `eval/eval-set.json` with:

```json
{
  "feature_name": "writing-calibration",
  "created": "2026-03-29",
  "description": "Atomic synthetic fixtures with hybrid grading for writing, proofreading, and polishing skills",
  "fixtures": [
    {
      "id": 1,
      "name": "intro-background-accretion",
      "skill": "writing",
      "path": "fixtures/writing/intro-background-accretion.md",
      "rubric": "rubrics/intro-background-accretion.json"
    },
    {
      "id": 2,
      "name": "intro-fragmentation",
      "skill": "writing",
      "path": "fixtures/writing/intro-fragmentation.md",
      "rubric": "rubrics/intro-fragmentation.json"
    },
    {
      "id": 3,
      "name": "results-drift",
      "skill": "writing",
      "path": "fixtures/writing/results-drift.md",
      "rubric": "rubrics/results-drift.json"
    },
    {
      "id": 4,
      "name": "conclusion-soft-landing",
      "skill": "writing",
      "path": "fixtures/writing/conclusion-soft-landing.md",
      "rubric": "rubrics/conclusion-soft-landing.json"
    },
    {
      "id": 5,
      "name": "delayed-finding",
      "skill": "proofreading",
      "path": "fixtures/proofreading/delayed-finding.md",
      "rubric": "rubrics/delayed-finding.json"
    },
    {
      "id": 6,
      "name": "broken-continuity",
      "skill": "proofreading",
      "path": "fixtures/proofreading/broken-continuity.md",
      "rubric": "rubrics/broken-continuity.json"
    },
    {
      "id": 7,
      "name": "calibration-break",
      "skill": "proofreading",
      "path": "fixtures/proofreading/calibration-break.md",
      "rubric": "rubrics/calibration-break.json"
    },
    {
      "id": 8,
      "name": "integrated-section-set",
      "skill": "polishing",
      "path": "fixtures/polishing/integrated-section-set.md",
      "rubric": "rubrics/integrated-section-set.json"
    }
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/eval-set.json eval/fixtures/ eval/rubrics/ results/
git commit -m "scaffold: eval directory structure and atomic fixture list"
```

---

### Task 2: Write fixture — intro-background-accretion

**Files:**
- Create: `eval/fixtures/writing/intro-background-accretion.md`
- Create: `eval/rubrics/intro-background-accretion.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/writing/intro-background-accretion.md`:

```markdown
---
fixture: intro-background-accretion
skill: writing
planted_antipatterns:
  - id: background-accretion
    location: paragraphs 1-3
    description: Three paragraphs on broad democratic-breakdown motivation before the paper takes ownership
  - id: hearsay-cw
    location: paragraph 1, sentence 2
    description: Uses "scholars have argued" to introduce conventional wisdom
  - id: delayed-finding
    location: paragraph 5
    description: Main finding does not appear until paragraph 5
  - id: roadmap
    location: paragraph 5, final sentences
    description: Ends with a section-by-section roadmap
expected_behavior:
  - The rewrite places the finding by paragraph 2-3
  - The rewrite uses 2-4 dense paragraphs, not 5+
  - "Scholars have argued" is replaced with flat CW assertion
  - The roadmap is removed or placed only after the answer is clear
structural_checks:
  - type: max_paragraph_count
    threshold: 4
  - type: finding_by_paragraph
    threshold: 3
  - type: absent_phrase
    phrases: ["scholars have argued", "the literature suggests"]
judge_criteria:
  - The rewrite compresses broad motivation into one paragraph and moves argumentative ownership forward
  - The conventional wisdom is stated as fact, not attributed to "scholars"
  - The rewrite reads like a top-tier intro: dense, assertive, front-loaded
---

## Task

Rewrite this manuscript introduction using the writing skill. Target a top-tier political science submission.

## Current Draft

Democratic erosion has attracted enormous attention in comparative politics. The study of democratic breakdown matters because understanding why regimes fail can help protect them in the future. Scholars have argued that the interaction between elites, institutions, and mass publics determines the fate of democratic governance under stress. This line of inquiry has produced a rich body of knowledge spanning multiple historical periods and geographic regions.

A related area of inquiry concerns the role of economic shocks in weakening democratic commitment. When economic conditions deteriorate, political actors may recalculate the costs and benefits of supporting democratic institutions. Trade disruptions, financial crises, and international sanctions can all alter the incentive structures facing both elites and voters. Understanding how these mechanisms work in specific historical contexts remains a central challenge for the discipline.

The interwar period offers a particularly informative setting for studying these dynamics. Japan's experience between 1930 and 1942 illustrates how a functioning parliamentary system can collapse under the combined weight of geopolitical isolation and domestic organizational mobilization. The economic pressures created by international sanctions reshaped the political landscape in ways that are still debated by historians and political scientists.

This paper examines the Japanese case in detail. Using newly digitized legislative records and firm-level procurement data, it traces the behavioral responses of legislators to economic shocks associated with international sanctions and military procurement expansion during the 1930s.

I find that legislators whose firms were exposed to sanctions shifted their voting patterns toward authoritarian alignment, while legislators linked to military procurement showed no comparable shift. The effect is concentrated among legislators embedded in dense right-wing civic networks, suggesting that organizational infrastructure amplified the political impact of economic pressure. The paper proceeds as follows. Section 2 reviews the literature on democratic erosion. Section 3 introduces the historical context. Section 4 describes the data. Section 5 presents the empirical strategy and results. Section 6 evaluates robustness and mechanisms. Section 7 concludes.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/intro-background-accretion.json`:

```json
{
  "fixture": "intro-background-accretion",
  "skill": "writing",
  "structural_checks": [
    {
      "type": "max_paragraph_count",
      "threshold": 4,
      "description": "Rewritten intro should have at most 4 paragraphs"
    },
    {
      "type": "finding_by_paragraph",
      "threshold": 3,
      "ownership_verbs": ["I find", "I show", "I argue", "I demonstrate", "we find", "we show", "this paper shows", "this paper finds"],
      "description": "An ownership verb should appear by paragraph 3"
    },
    {
      "type": "absent_phrase",
      "phrases": ["scholars have argued", "the literature suggests", "scholars suggest"],
      "description": "Hearsay CW phrases should be absent"
    }
  ],
  "judge_criteria": [
    "The rewrite compresses paragraphs 1-3 of the original into at most one paragraph of motivation",
    "The main finding (sanctions-exposed legislators shifted toward authoritarian alignment) appears early and is stated flatly",
    "The roadmap is removed or reduced to at most one sentence after the answer is already clear"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/writing/intro-background-accretion.md eval/rubrics/intro-background-accretion.json
git commit -m "fixture: intro-background-accretion with rubric"
```

---

### Task 3: Write fixture — intro-fragmentation

**Files:**
- Create: `eval/fixtures/writing/intro-fragmentation.md`
- Create: `eval/rubrics/intro-fragmentation.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/writing/intro-fragmentation.md`:

```markdown
---
fixture: intro-fragmentation
skill: writing
planted_antipatterns:
  - id: intro-fragmentation
    location: entire intro
    description: 7 micro-paragraphs each under 80 words; each does thin argumentative work
expected_behavior:
  - The rewrite merges thin paragraphs into 2-4 dense argumentative units
  - Mean words per paragraph should be at least 150
  - No content is lost, just consolidated
structural_checks:
  - type: max_paragraph_count
    threshold: 4
  - type: min_words_per_paragraph
    threshold: 150
judge_criteria:
  - The rewrite merges related argumentative moves rather than just concatenating adjacent paragraphs
  - Each output paragraph has one clear job and carries real argumentative weight
---

## Task

Rewrite this manuscript introduction using the writing skill. The current draft fragments the argument into too many thin paragraphs. Target a top-tier political science submission.

## Current Draft

Why do some excluded political factions succeed at undermining democratic institutions while others fail?

This question sits at the intersection of research on democratic backsliding, elite coordination, and contentious politics. Existing work has focused on institutional weakness and mass polarization as the primary drivers.

This paper offers an alternative. It argues that organizational infrastructure outside of formal institutions enabled excluded factions to coordinate anti-democratic pressure.

The empirical setting is interwar Japan, where right-wing civic organizations provided coordination capacity to sanctioned elites who had been shut out of both parties and the military hierarchy.

I use newly digitized records of legislative voting, firm procurement contracts, and right-wing organizational membership to measure the behavioral consequences of economic shocks.

The findings show that sanction-exposed legislators in organizationally dense prefectures shifted sharply toward authoritarian alignment, while those in sparse prefectures did not.

This contributes to the literature on democratic erosion by identifying a mechanism through which economic shocks translate into anti-democratic mobilization: organizational infrastructure amplifies elite defection from democratic norms.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/intro-fragmentation.json`:

```json
{
  "fixture": "intro-fragmentation",
  "skill": "writing",
  "structural_checks": [
    {
      "type": "max_paragraph_count",
      "threshold": 4,
      "description": "Rewritten intro should have at most 4 paragraphs"
    },
    {
      "type": "min_words_per_paragraph",
      "threshold": 150,
      "description": "Mean words per paragraph should be at least 150"
    }
  ],
  "judge_criteria": [
    "The rewrite merges related argumentative moves into dense units, not just concatenates adjacent paragraphs",
    "Each output paragraph has one clear job: CW/puzzle, answer/finding, method/credibility, contribution"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/writing/intro-fragmentation.md eval/rubrics/intro-fragmentation.json
git commit -m "fixture: intro-fragmentation with rubric"
```

---

### Task 4: Write fixture — results-drift

**Files:**
- Create: `eval/fixtures/writing/results-drift.md`
- Create: `eval/rubrics/results-drift.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/writing/results-drift.md`:

```markdown
---
fixture: results-drift
skill: writing
planted_antipatterns:
  - id: results-drift
    location: paragraphs 1-2
    description: Table reference in paragraph 1 (pure setup), actual finding in paragraph 2, coefficient magnitude delayed to sentence 4
  - id: unstaked-coefficients
    location: paragraph 2
    description: Coefficients presented without substantive interpretation until late
expected_behavior:
  - Table reference and finding appear in the same paragraph
  - Coefficient direction and magnitude appear within 2 sentences of the table reference
structural_checks:
  - type: same_paragraph
    phrases: ["Table 2", "positive and statistically"]
  - type: finding_by_paragraph
    threshold: 1
judge_criteria:
  - The rewrite places the table reference and the substantive result in the same paragraph
  - Magnitude is quantified early, not deferred behind specification details
---

## Task

Rewrite this results section using the writing skill. Target a top-tier political science submission.

## Current Draft

Table 2 reports the main results from the interaction models. Column 1 presents the baseline specification with prefecture and year fixed effects. Column 2 adds industry-specific controls for sectoral employment shares. Column 3 adds a measure of local police capacity to address the concern that state repressive infrastructure might confound the relationship. Column 4 restricts the sample to prefectures outside the three largest metropolitan areas. All specifications cluster standard errors at the prefecture level.

The interaction between sanctions exposure and organizational density is positive across all four columns. The coefficient in Column 1 indicates that a one-standard-deviation increase in organizational density is associated with a 4.2 percentage point increase in authoritarian voting among sanction-exposed legislators relative to unexposed legislators. This effect is precisely estimated, with a 95% confidence interval of [2.1, 6.3]. The magnitude is substantively meaningful: it is equivalent to roughly one-third of the mean shift in authoritarian voting observed across the full sample during the 1936--1942 period. The robustness checks in Columns 2--4 produce similar point estimates, ranging from 3.8 to 4.5 percentage points.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/results-drift.json`:

```json
{
  "fixture": "results-drift",
  "skill": "writing",
  "structural_checks": [
    {
      "type": "same_paragraph",
      "phrases": ["Table 2", "percentage point"],
      "description": "Table reference and quantified result should appear in the same paragraph"
    },
    {
      "type": "finding_by_paragraph",
      "threshold": 1,
      "ownership_verbs": ["positive", "increase", "associated with", "indicates", "shows"],
      "description": "The substantive finding should appear in the first paragraph"
    }
  ],
  "judge_criteria": [
    "The rewrite places the table reference and the core finding (direction + magnitude) in the same paragraph",
    "Specification details (columns, controls) are subordinate to the main result, not front-loaded"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/writing/results-drift.md eval/rubrics/results-drift.json
git commit -m "fixture: results-drift with rubric"
```

---

### Task 5: Write fixture — conclusion-soft-landing

**Files:**
- Create: `eval/fixtures/writing/conclusion-soft-landing.md`
- Create: `eval/rubrics/conclusion-soft-landing.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/writing/conclusion-soft-landing.md`:

```markdown
---
fixture: conclusion-soft-landing
skill: writing
planted_antipatterns:
  - id: soft-landing
    location: paragraphs 3-5
    description: Conclusion closes with diffuse recap, generic caution, and "more research is needed" filler
  - id: recap-fatigue
    location: paragraphs 1-3
    description: First three paragraphs re-run the entire paper instead of closing on implication
expected_behavior:
  - Conclusion should be at most 3 paragraphs and 700 words
  - "more research is needed" should be absent
  - The ending should state the implication, not apologize or recap
structural_checks:
  - type: max_paragraph_count
    threshold: 3
  - type: max_word_count
    threshold: 700
  - type: absent_phrase
    phrases: ["more research is needed", "future work should", "caution is warranted"]
judge_criteria:
  - The rewrite closes on implication, not on recap or apology
  - The rewrite is compressed without losing the main takeaway
---

## Task

Rewrite this manuscript conclusion using the writing skill. Target a top-tier political science submission.

## Current Draft

This paper has examined the relationship between economic sanctions, organizational infrastructure, and democratic erosion in interwar Japan. It has drawn on newly digitized legislative records and firm-level procurement data to trace how legislators responded to the dual shocks of international sanctions and military procurement expansion during the 1930s.

The analysis has shown that legislators exposed to sanctions shifted their voting behavior toward authoritarian alignment, especially in prefectures with dense right-wing organizational networks. The paper has also demonstrated that procurement linkages did not produce comparable behavioral shifts, suggesting that the mechanism is specific to exclusionary economic shocks rather than to economic dependence on the state in general.

These findings contribute to several literatures. They speak to work on democratic backsliding by identifying organizational infrastructure as a transmission mechanism. They also contribute to the study of sanctions by showing that economic pressure can have unintended domestic political consequences. Finally, they engage with research on authoritarian consolidation by demonstrating that elite realignment can be organizationally mediated.

Of course, the historical setting is specific. Interwar Japan was a single case, and it is important to exercise caution in generalizing these findings to other contexts. The measurement of organizational density is inevitably imperfect, and alternative measures might yield somewhat different results. It is also possible that unobserved factors correlated with both organizational density and authoritarian voting drive some of the observed association, despite the robustness checks presented above.

More research is needed to understand how organizational infrastructure shapes democratic outcomes in other settings. Future work should examine additional historical cases of democratic collapse, should continue refining the measurement of civic organizations, and should explore whether the mechanisms identified here operate in contemporary contexts of democratic backsliding.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/conclusion-soft-landing.json`:

```json
{
  "fixture": "conclusion-soft-landing",
  "skill": "writing",
  "structural_checks": [
    {
      "type": "max_paragraph_count",
      "threshold": 3,
      "description": "Conclusion should have at most 3 paragraphs"
    },
    {
      "type": "max_word_count",
      "threshold": 700,
      "description": "Conclusion should be under 700 words"
    },
    {
      "type": "absent_phrase",
      "phrases": ["more research is needed", "future work should", "caution is warranted"],
      "description": "Generic future-work and caution filler should be absent"
    }
  ],
  "judge_criteria": [
    "The rewrite ends on what the finding changes (implication), not on what remains unknown",
    "Recap is compressed to at most one paragraph restating the finding with 'so what'"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/writing/conclusion-soft-landing.md eval/rubrics/conclusion-soft-landing.json
git commit -m "fixture: conclusion-soft-landing with rubric"
```

---

### Task 6: Write fixture — delayed-finding (proofreading)

**Files:**
- Create: `eval/fixtures/proofreading/delayed-finding.md`
- Create: `eval/rubrics/delayed-finding.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/proofreading/delayed-finding.md`:

```markdown
---
fixture: delayed-finding
skill: proofreading
planted_antipatterns:
  - id: background-accretion
    location: paragraphs 1-3
    description: Three paragraphs of case context and literature before the paper takes ownership
  - id: delayed-finding
    location: paragraph 4
    description: Finding does not appear until paragraph 4
expected_behavior:
  - Report identifies delayed finding as a top-3 issue
  - Report categorizes it as section form deviation or background accretion, not a word-choice problem
  - Report does not spend the majority of space on sentence-level fixes
structural_checks:
  - type: issue_category_rank
    expected_top_categories: ["section form deviation", "background accretion"]
    n: 3
  - type: line_edit_ratio
    max_ratio: 0.3
judge_criteria:
  - The report diagnoses the delayed finding as a structural/placement problem, not a prose polish issue
  - The proposed fix involves moving the finding forward, not rewriting individual sentences
  - The report does not devote the majority of its analysis to word-choice or grammar
---

## Task

Read this manuscript introduction as a first-time reader using the proofreading skill. Report the highest-priority flow and structure problems in reading order.

## Introduction Draft

The collapse of Japan's Taisho democracy in the 1930s stands as one of the most dramatic instances of democratic erosion in the twentieth century. Between 1925 and 1932, Japan maintained a functioning parliamentary system with competitive elections, a relatively free press, and civilian control over the cabinet. Yet by 1940, all political parties had dissolved, the Diet had become a rubber stamp, and the military dominated policymaking. Understanding how this transformation occurred has occupied historians for decades.

Several factors contributed to Japan's democratic collapse. The global depression severely disrupted trade-dependent industries, creating widespread economic hardship. The military's prestige grew after a series of incidents in Manchuria and China. Assassinations of political leaders in 1932 and 1936 signaled that democratic politicians faced physical danger. Meanwhile, right-wing civic organizations expanded rapidly in rural areas, offering an alternative political infrastructure outside the established parties. These organizations drew on agrarian discontent, nationalist ideology, and patron-client networks rooted in local communities.

The literature on democratic backsliding in interwar Japan has focused primarily on institutional explanations: the weakness of the constitutional framework, the independence of the military from civilian authority, and the failure of political parties to build durable coalitions. These are important factors, but they do not fully explain the geographic variation in authoritarian realignment. Some prefectures experienced sharp shifts toward authoritarian politics while others remained relatively stable, even controlling for economic conditions and military presence.

I argue that organizational infrastructure outside formal institutions explains this variation. Specifically, I show that sanctions-exposed legislators in prefectures with dense right-wing organizational networks shifted their voting patterns toward authoritarian alignment at substantially higher rates than legislators in organizationally sparse prefectures. The effect is concentrated among legislators whose firms lost access to international markets, and it operates through organizational coordination rather than through ideological conversion.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/delayed-finding.json`:

```json
{
  "fixture": "delayed-finding",
  "skill": "proofreading",
  "structural_checks": [
    {
      "type": "issue_category_rank",
      "expected_top_categories": ["section form deviation", "background accretion", "delayed finding"],
      "n": 3,
      "description": "Top-3 issues should include structural/placement categories"
    },
    {
      "type": "line_edit_ratio",
      "max_ratio": 0.3,
      "line_edit_categories": ["word choice", "grammar", "AI-writing tell", "sentence-level"],
      "description": "No more than 30% of flagged issues should be line-level"
    }
  ],
  "judge_criteria": [
    "The report diagnoses the delayed finding as a reader-state failure, not a prose problem",
    "The proposed fix involves structural reordering (move finding to paragraph 2-3), not sentence rewording",
    "The report stays within the proofreading role boundary and does not attempt to rewrite the intro"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/proofreading/delayed-finding.md eval/rubrics/delayed-finding.json
git commit -m "fixture: delayed-finding (proofreading) with rubric"
```

---

### Task 7: Write fixture — broken-continuity (proofreading)

**Files:**
- Create: `eval/fixtures/proofreading/broken-continuity.md`
- Create: `eval/rubrics/broken-continuity.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/proofreading/broken-continuity.md`:

```markdown
---
fixture: broken-continuity
skill: proofreading
planted_antipatterns:
  - id: undefined-term
    location: paragraph 2
    description: "organizational density" used in paragraph 2 but not defined until paragraph 5
  - id: forward-reference
    location: paragraph 4
    description: Results section references "the mechanism described in Section 4" when reader is still in Section 3
expected_behavior:
  - Report flags the undefined term with its exact location
  - Report flags the forward reference as a reader-state break
  - Proposed fixes are structural (move definition earlier, reorder sections), not just rewording
structural_checks:
  - type: present_phrase
    phrases: ["undefined", "not yet defined", "before it is defined", "used before"]
  - type: present_phrase
    phrases: ["forward reference", "not yet reached", "Section 4", "hasn't read"]
  - type: line_edit_ratio
    max_ratio: 0.3
judge_criteria:
  - The report identifies both continuity breaks with correct paragraph locations
  - The proposed fixes are structural (move definition up, fix section ordering) not cosmetic
  - The report does not spend the majority of space on word-choice or grammar issues
---

## Task

Read these manuscript sections as a first-time reader using the proofreading skill. Report the highest-priority flow and structure problems in reading order.

## Section 3: Empirical Strategy

The identification strategy exploits the exogenous timing of international sanctions against Japan in 1938 combined with cross-sectional variation in organizational density across prefectures. The interaction between sanctions exposure and organizational density provides the key source of variation.

I estimate a difference-in-differences model where the treatment is sanctions exposure and the moderating variable is organizational density. Prefectures with higher organizational density should show a stronger shift toward authoritarian voting after sanctions, if the organizational coordination mechanism is correct.

The main specification includes prefecture and year fixed effects, industry-specific controls, and a measure of local military presence. Standard errors are clustered at the prefecture level to address serial correlation within prefectures over time.

An important concern is that organizational density may be correlated with unobserved factors that independently drive authoritarian alignment. To address this, I exploit the mechanism described in Section 4 to construct an instrumental variable based on the historical distribution of Shinto shrine networks, which predict organizational density but are plausibly exogenous to short-run political preferences.

## Section 4: Data

The analysis draws on three original datasets. The first is a complete digitization of Diet voting records from 1932 to 1942, covering 2,847 roll-call votes across 466 legislators.

The second is a prefecture-level panel of right-wing organizational membership compiled from Home Ministry surveillance records. The organizational density measure counts the number of registered right-wing civic organizations per 100,000 residents in each prefecture as of 1935. This measure captures the local organizational infrastructure available to excluded political factions.

The third dataset links individual legislators to their firms' trade exposure using customs records, allowing measurement of sanctions exposure at the legislator level.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/broken-continuity.json`:

```json
{
  "fixture": "broken-continuity",
  "skill": "proofreading",
  "structural_checks": [
    {
      "type": "present_phrase",
      "phrases": ["undefined", "not yet defined", "before it is defined", "used before", "not introduced"],
      "description": "Report should flag the undefined term issue"
    },
    {
      "type": "present_phrase",
      "phrases": ["forward reference", "not yet reached", "Section 4", "hasn't read", "reader has not"],
      "description": "Report should flag the forward reference issue"
    },
    {
      "type": "line_edit_ratio",
      "max_ratio": 0.3,
      "line_edit_categories": ["word choice", "grammar", "AI-writing tell", "sentence-level"],
      "description": "No more than 30% of issues should be line-level"
    }
  ],
  "judge_criteria": [
    "The report identifies both continuity breaks with correct locations (paragraph 2 of Section 3 for undefined term, paragraph 4 of Section 3 for forward reference)",
    "The proposed fixes are structural: move the organizational density definition before its first use, fix the section ordering so Section 4 is not referenced before the reader reaches it"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/proofreading/broken-continuity.md eval/rubrics/broken-continuity.json
git commit -m "fixture: broken-continuity (proofreading) with rubric"
```

---

### Task 8: Write fixture — calibration-break (proofreading)

**Files:**
- Create: `eval/fixtures/proofreading/calibration-break.md`
- Create: `eval/rubrics/calibration-break.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/proofreading/calibration-break.md`:

```markdown
---
fixture: calibration-break
skill: proofreading
planted_antipatterns:
  - id: calibration-break-underconfidence
    location: paragraphs 1-2
    description: Paper uses IV design but hedges main finding with "may suggest", "appears to be consistent with", "tentatively indicates"
expected_behavior:
  - Report flags the hedging as a calibration break that damages reader trust
  - Report notes that the IV design warrants stronger language
  - Report does NOT spend the majority of space on word-choice, grammar, or AI-tell cleanup
structural_checks:
  - type: issue_category_rank
    expected_top_categories: ["calibration break", "calibration"]
    n: 3
  - type: line_edit_ratio
    max_ratio: 0.3
judge_criteria:
  - The report flags the mismatch between design strength (IV) and prose confidence (hedged) as the primary issue
  - The report does not flag the hedging as an overclaiming problem or adjudicate the research design in detail
  - The report routes sentence-level repair to the writing skill rather than doing it inline
---

## Task

Read this results section as a first-time reader using the proofreading skill. Report the highest-priority flow and structure problems in reading order.

## Results Draft

The estimation strategy relies on an instrumental variable constructed from historical Shinto shrine networks, which predict right-wing organizational density but are plausibly exogenous to short-run political preferences. The first-stage F-statistic is 28.4, well above conventional thresholds. The exclusion restriction is supported by a series of placebo tests showing no relationship between shrine density and pre-sanctions political alignment.

The IV estimates may suggest that organizational density amplified the effect of sanctions on authoritarian voting. The results appear to be consistent with the hypothesis that legislators in organizationally dense prefectures shifted their voting patterns after the sanctions shock. The point estimate tentatively indicates that a one-standard-deviation increase in organizational density is associated with a 4.2 percentage point increase in authoritarian voting among sanction-exposed legislators. This effect appears to be precisely estimated, with a confidence interval of [2.1, 6.3]. These patterns are broadly in line with the prediction that organizational infrastructure matters, though the evidence should be interpreted with appropriate caution given the historical nature of the data.

The magnitude of this estimated relationship is not trivial. It is roughly equivalent to one-third of the mean shift in authoritarian voting observed across the full sample. The robustness of this possible association is further supported by the stability of the estimates across specifications that add industry controls, exclude metropolitan prefectures, and use alternative measures of organizational presence.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/calibration-break.json`:

```json
{
  "fixture": "calibration-break",
  "skill": "proofreading",
  "structural_checks": [
    {
      "type": "issue_category_rank",
      "expected_top_categories": ["calibration break", "calibration", "too conceding"],
      "n": 3,
      "description": "Top-3 issues should include a calibration-related category"
    },
    {
      "type": "line_edit_ratio",
      "max_ratio": 0.3,
      "line_edit_categories": ["word choice", "grammar", "AI-writing tell", "sentence-level"],
      "description": "No more than 30% of issues should be line-level"
    }
  ],
  "judge_criteria": [
    "The report identifies the mismatch between IV design strength (F=28.4, clean exclusion restriction) and hedged prose ('may suggest', 'tentatively indicates') as a calibration failure",
    "The report frames this as a reader-trust problem, not a detailed research-design adjudication",
    "The report routes sentence-level verb replacement to the writing skill"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/proofreading/calibration-break.md eval/rubrics/calibration-break.json
git commit -m "fixture: calibration-break (proofreading) with rubric"
```

---

### Task 9: Write fixture — integrated-section-set (polishing)

**Files:**
- Create: `eval/fixtures/polishing/integrated-section-set.md`
- Create: `eval/rubrics/integrated-section-set.json`

- [ ] **Step 1: Write the fixture**

Create `eval/fixtures/polishing/integrated-section-set.md`:

```markdown
---
fixture: integrated-section-set
skill: polishing
planted_antipatterns:
  - id: intro-background-accretion
    location: introduction, paragraphs 1-2
    description: Two paragraphs of broad motivation before the paper takes ownership
  - id: results-drift
    location: results section, paragraphs 1-2
    description: Table reference in paragraph 1, finding in paragraph 2
  - id: conclusion-soft-landing
    location: conclusion, paragraph 2
    description: Ends with "more research is needed" and generic future-work filler
expected_behavior:
  - The synthesis mentions all 3 sections and identifies the manuscript-level issues
  - The revision plan routes intro issue to writing or calibration assessor
  - The revision plan prioritizes manuscript-level structural issues above word-choice
  - Assessor reports are distinguishable in focus
structural_checks:
  - type: present_phrase
    phrases: ["introduction", "results", "conclusion"]
  - type: present_phrase
    phrases: ["background accretion", "delayed", "ownership"]
  - type: present_phrase
    phrases: ["drift", "table", "same paragraph"]
  - type: present_phrase
    phrases: ["soft landing", "more research", "implication"]
judge_criteria:
  - The synthesis identifies all three planted problems as manuscript-level issues
  - The revision plan ranks these above surface-level word-choice or AI-tell concerns
  - The assessor reports show distinct perspectives (proofreader on reader-state, calibration assessor on norms, humanizer on AI tells)
---

## Task

Assess these manuscript sections for publication polish using the polishing skill. Synthesize the issues into a revision plan and prioritize the fixes.

## Introduction

Democratic breakdown has been studied from many angles. The literature on regime transitions, authoritarian consolidation, and elite coordination has produced valuable insights about why and how democracies fail. These contributions are important because they illuminate the fragility of institutional arrangements under conditions of stress and political competition. Understanding these dynamics remains a central challenge for comparative politics.

This paper examines democratic erosion in interwar Japan. It studies how excluded right-wing factions used civic organizations to coordinate political pressure on parliamentary institutions. I argue that sanctions-exposed legislators in organizationally dense prefectures shifted toward authoritarian alignment at higher rates than their counterparts in sparse prefectures. The evidence is consistent with an organizational coordination mechanism rather than ideological conversion.

## Results

Table 2 reports the main interaction results. Column 1 includes the baseline specification with prefecture and year fixed effects. Column 2 adds industry controls. Column 3 adds local military presence. Column 4 excludes metropolitan prefectures.

The interaction between sanctions exposure and organizational density is positive and precisely estimated across all specifications. A one-standard-deviation increase in organizational density is associated with a 4.2 percentage point increase in authoritarian voting among sanction-exposed legislators. This is roughly one-third of the mean shift observed across the full sample.

## Conclusion

This paper has shown that organizational infrastructure amplified the political impact of economic sanctions in interwar Japan. Sanctions-exposed legislators embedded in dense right-wing networks shifted toward authoritarian alignment; those in sparse networks did not. The mechanism is organizational coordination, not ideological conversion.

These findings matter beyond the Japanese case. They suggest that democratic erosion may be accelerated by civic infrastructure that operates outside formal institutional channels. More research is needed on how organizational networks shape democratic outcomes in other contexts. Future work should explore additional cases of democratic breakdown and should continue developing better measures of organizational capacity.
```

- [ ] **Step 2: Write the rubric**

Create `eval/rubrics/integrated-section-set.json`:

```json
{
  "fixture": "integrated-section-set",
  "skill": "polishing",
  "structural_checks": [
    {
      "type": "present_phrase",
      "phrases": ["introduction", "intro"],
      "description": "Synthesis should mention the introduction"
    },
    {
      "type": "present_phrase",
      "phrases": ["results"],
      "description": "Synthesis should mention the results section"
    },
    {
      "type": "present_phrase",
      "phrases": ["conclusion"],
      "description": "Synthesis should mention the conclusion"
    },
    {
      "type": "present_phrase",
      "phrases": ["background accretion", "delayed finding", "ownership", "motivation"],
      "description": "Synthesis should identify the intro problem"
    },
    {
      "type": "present_phrase",
      "phrases": ["drift", "table reference", "same paragraph", "separated"],
      "description": "Synthesis should identify the results placement problem"
    },
    {
      "type": "present_phrase",
      "phrases": ["soft landing", "more research", "implication", "future work"],
      "description": "Synthesis should identify the conclusion problem"
    }
  ],
  "judge_criteria": [
    "The synthesis identifies all three planted problems as manuscript-level structural issues",
    "The revision plan ranks structural fixes (intro timing, results placement, conclusion closure) above surface polish",
    "Assessor reports show distinct focus areas, not redundant flagging of the same things"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add eval/fixtures/polishing/integrated-section-set.md eval/rubrics/integrated-section-set.json
git commit -m "fixture: integrated-section-set (polishing) with rubric"
```

---

### Task 10: Write run_eval.py — core framework and structural checks

**Files:**
- Create: `scripts/run_eval.py`

- [ ] **Step 1: Write the runner**

Create `scripts/run_eval.py`:

```python
#!/usr/bin/env python3
"""
Eval runner for writing-calibration fixtures.

Usage:
    python scripts/run_eval.py --timestamp 2026-03-29T14-30 [--fixture NAME] [--skill SKILL]

Workflow:
    1. User runs a skill on a fixture manually and saves output to:
       results/<timestamp>/outputs/<fixture-name>.md
    2. User runs this script to grade the output.
    3. Script runs structural checks and generates LLM-as-judge prompts.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE / "eval"
RESULTS_DIR = BASE / "results"
HISTORY_FILE = BASE / "history.json"


# ---------------------------------------------------------------------------
# YAML frontmatter parser (no external dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown. Returns (metadata, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    yaml_block = text[3:end].strip()
    body = text[end + 3:].strip()
    return _parse_yaml(yaml_block), body


def _parse_yaml(block: str) -> dict:
    """Minimal YAML parser for flat and simple nested structures."""
    result = {}
    current_key = None
    current_list = None

    for line in block.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if current_list is not None:
                # Check if it's a dict item (has colon)
                if ": " in item_text and not item_text.startswith('"'):
                    # Dict-style list item
                    if isinstance(current_list, list) and (not current_list or isinstance(current_list[-1], dict)):
                        if not current_list or all(k in current_list[-1] for k in []):
                            current_list.append({})
                        k, v = item_text.split(": ", 1)
                        current_list[-1][k.strip()] = _parse_value(v.strip())
                    else:
                        current_list.append(_parse_value(item_text))
                else:
                    current_list.append(_parse_value(item_text))
            continue

        # Key: value pair
        if ": " in stripped:
            k, v = stripped.split(": ", 1)
            k = k.strip()
            v = v.strip()

            # Flush previous list
            if current_list is not None and current_key:
                result[current_key] = current_list
                current_list = None

            if v == "" or v == "[]":
                current_key = k
                current_list = []
            else:
                result[k] = _parse_value(v)
                current_key = k
                current_list = None
        # Indented key in a list-of-dicts
        elif ":" in stripped and current_list is not None:
            k, v = stripped.split(":", 1)
            if current_list and isinstance(current_list[-1], dict):
                current_list[-1][k.strip()] = _parse_value(v.strip())

    if current_list is not None and current_key:
        result[current_key] = current_list

    return result


def _parse_value(v: str):
    """Parse a YAML scalar value."""
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        if not inner.strip():
            return []
        return [_parse_value(x.strip()) for x in inner.split(",")]
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


# ---------------------------------------------------------------------------
# Text analysis helpers
# ---------------------------------------------------------------------------

def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs (separated by blank lines)."""
    # Remove markdown headers for paragraph counting
    lines = text.strip().split("\n")
    content_lines = [l for l in lines if not l.startswith("#")]
    text_clean = "\n".join(content_lines).strip()
    paragraphs = re.split(r"\n\s*\n", text_clean)
    return [p.strip() for p in paragraphs if p.strip()]


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def words_per_paragraph(paragraphs: list[str]) -> float:
    """Mean words per paragraph."""
    if not paragraphs:
        return 0.0
    return sum(word_count(p) for p in paragraphs) / len(paragraphs)


OWNERSHIP_VERBS_DEFAULT = [
    "I find", "I show", "I argue", "I demonstrate",
    "we find", "we show", "we argue", "we demonstrate",
    "this paper shows", "this paper finds", "this paper demonstrates",
]


def finding_paragraph_index(paragraphs: list[str], verbs: list[str] | None = None) -> int | None:
    """Return 1-based index of first paragraph containing an ownership verb."""
    verbs = verbs or OWNERSHIP_VERBS_DEFAULT
    for i, para in enumerate(paragraphs):
        lower = para.lower()
        for verb in verbs:
            if verb.lower() in lower:
                return i + 1
    return None


def phrase_present(text: str, phrase: str) -> bool:
    """Check if phrase appears in text (case-insensitive)."""
    return phrase.lower() in text.lower()


def phrases_in_same_paragraph(paragraphs: list[str], phrases: list[str]) -> bool:
    """Check if all phrases appear in at least one common paragraph."""
    for para in paragraphs:
        lower = para.lower()
        if all(p.lower() in lower for p in phrases):
            return True
    return False


# ---------------------------------------------------------------------------
# Structural check runner
# ---------------------------------------------------------------------------

def run_structural_check(check: dict, output_text: str) -> dict:
    """Run a single structural check on the skill output. Returns result dict."""
    check_type = check["type"]
    paragraphs = split_paragraphs(output_text)
    result = {"check": check_type, "pass": False}

    if check_type == "max_paragraph_count":
        threshold = check["threshold"]
        actual = len(paragraphs)
        result.update({"threshold": threshold, "actual": actual, "pass": actual <= threshold})

    elif check_type == "min_words_per_paragraph":
        threshold = check["threshold"]
        actual = round(words_per_paragraph(paragraphs), 1)
        result.update({"threshold": threshold, "actual": actual, "pass": actual >= threshold})

    elif check_type == "finding_by_paragraph":
        threshold = check["threshold"]
        verbs = check.get("ownership_verbs", None)
        actual = finding_paragraph_index(paragraphs, verbs)
        passed = actual is not None and actual <= threshold
        result.update({"threshold": threshold, "actual": actual, "pass": passed})

    elif check_type == "absent_phrase":
        phrases = check["phrases"]
        found = [p for p in phrases if phrase_present(output_text, p)]
        result.update({"phrases": phrases, "found": found, "pass": len(found) == 0})

    elif check_type == "present_phrase":
        phrases = check["phrases"]
        found = [p for p in phrases if phrase_present(output_text, p)]
        result.update({"phrases": phrases, "found": found, "pass": len(found) > 0})

    elif check_type == "max_word_count":
        threshold = check["threshold"]
        actual = word_count(output_text)
        result.update({"threshold": threshold, "actual": actual, "pass": actual <= threshold})

    elif check_type == "same_paragraph":
        phrases = check["phrases"]
        passed = phrases_in_same_paragraph(paragraphs, phrases)
        result.update({"phrases": phrases, "pass": passed})

    elif check_type == "issue_category_rank":
        expected = [c.lower() for c in check["expected_top_categories"]]
        n = check["n"]
        categories = extract_issue_categories(output_text)
        top_n = [c.lower() for c in categories[:n]]
        matched = any(any(e in t for e in expected) for t in top_n)
        result.update({
            "expected_top_categories": expected,
            "actual_top_n": top_n,
            "n": n,
            "pass": matched,
        })

    elif check_type == "line_edit_ratio":
        max_ratio = check["max_ratio"]
        le_cats = [c.lower() for c in check.get("line_edit_categories", [
            "word choice", "grammar", "ai-writing tell", "sentence-level",
        ])]
        categories = extract_issue_categories(output_text)
        if not categories:
            result.update({"max_ratio": max_ratio, "actual_ratio": 0.0, "pass": True})
        else:
            line_count = sum(1 for c in categories if any(le in c.lower() for le in le_cats))
            ratio = round(line_count / len(categories), 2)
            result.update({"max_ratio": max_ratio, "actual_ratio": ratio, "pass": ratio <= max_ratio})

    else:
        result.update({"error": f"unknown check type: {check_type}", "pass": False})

    return result


def extract_issue_categories(text: str) -> list[str]:
    """Extract issue categories from a proofreading/polishing report.

    Looks for patterns like:
      **Category:** ...
      **Type:** ...
      ### N. Category Name
      - **Category**: ...
    """
    categories = []

    # Pattern 1: **Category:** value
    for match in re.finditer(r"\*\*(?:Category|Type)\s*[:]\*\*\s*(.+)", text, re.IGNORECASE):
        categories.append(match.group(1).strip().rstrip("*"))

    # Pattern 2: ### N. Category Name or ### Issue N: Category
    if not categories:
        for match in re.finditer(r"###\s*(?:Issue\s+)?\d+[.:]\s*(.+)", text):
            cat = match.group(1).strip()
            # Strip trailing markdown
            cat = re.sub(r"\s*\*+$", "", cat)
            categories.append(cat)

    return categories


# ---------------------------------------------------------------------------
# Judge prompt generator
# ---------------------------------------------------------------------------

def generate_judge_prompt(fixture_path: Path, rubric: dict, output_text: str) -> str:
    """Generate an LLM-as-judge grading prompt."""
    fixture_text = fixture_path.read_text()
    criteria = rubric.get("judge_criteria", [])

    prompt = f"""# Eval Judge: {rubric['fixture']}

## Instructions

You are grading the output of the `{rubric['skill']}` skill against a synthetic fixture with known planted anti-patterns. For each criterion below, return PASS or FAIL with a one-sentence justification.

## Original Fixture

```markdown
{fixture_text}
```

## Skill Output

```markdown
{output_text}
```

## Criteria

"""
    for i, criterion in enumerate(criteria, 1):
        prompt += f"{i}. {criterion}\n"

    prompt += """
## Response Format

For each criterion, respond with exactly:

**Criterion N:** PASS | FAIL — [one sentence justification]
"""
    return prompt


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

def load_history() -> dict:
    """Load history.json, creating it if needed."""
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"feature": "writing-calibration", "runs": []}


def save_history(history: dict):
    """Save history.json."""
    HISTORY_FILE.write_text(json.dumps(history, indent=2) + "\n")


def append_run(timestamp: str, results: list[dict]):
    """Append a run to history.json."""
    history = load_history()

    pass_count = sum(1 for r in results if r["structural_pass"])
    fail_count = len(results) - pass_count

    run = {
        "timestamp": timestamp,
        "structural": {"pass": pass_count, "fail": fail_count, "total": len(results)},
        "judge": {"pass": None, "fail": None, "total": len(results), "pending": True},
        "notes": "",
    }
    history["runs"].append(run)
    save_history(history)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_eval_set() -> dict:
    """Load the eval-set.json fixture list."""
    path = EVAL_DIR / "eval-set.json"
    return json.loads(path.read_text())


def run_fixture(fixture_meta: dict, timestamp: str) -> dict:
    """Run all checks for one fixture and generate judge prompt."""
    name = fixture_meta["name"]
    skill = fixture_meta["skill"]
    fixture_path = EVAL_DIR / fixture_meta["path"]
    rubric_path = EVAL_DIR / fixture_meta["rubric"]

    # Load fixture and rubric
    rubric = json.loads(rubric_path.read_text())

    # Load skill output
    output_dir = RESULTS_DIR / timestamp / "outputs"
    output_path = output_dir / f"{name}.md"
    if not output_path.exists():
        return {
            "fixture": name,
            "skill": skill,
            "error": f"Output not found: {output_path}",
            "checks": [],
            "structural_pass": False,
            "judge_pending": True,
        }

    output_text = output_path.read_text()

    # Run structural checks
    checks = []
    for check_spec in rubric.get("structural_checks", []):
        result = run_structural_check(check_spec, output_text)
        checks.append(result)

    structural_pass = all(c["pass"] for c in checks)

    # Generate judge prompt
    judge_dir = RESULTS_DIR / timestamp / "judge-prompts"
    judge_dir.mkdir(parents=True, exist_ok=True)
    judge_prompt = generate_judge_prompt(fixture_path, rubric, output_text)
    (judge_dir / f"{name}-judge.md").write_text(judge_prompt)

    return {
        "fixture": name,
        "skill": skill,
        "checks": checks,
        "structural_pass": structural_pass,
        "judge_pending": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Run writing-calibration eval checks")
    parser.add_argument("--timestamp", required=True, help="Results directory timestamp")
    parser.add_argument("--fixture", help="Run only this fixture (by name)")
    parser.add_argument("--skill", help="Run only fixtures for this skill")
    args = parser.parse_args()

    eval_set = load_eval_set()
    fixtures = eval_set["fixtures"]

    if args.fixture:
        fixtures = [f for f in fixtures if f["name"] == args.fixture]
    if args.skill:
        fixtures = [f for f in fixtures if f["skill"] == args.skill]

    if not fixtures:
        print("No matching fixtures found.", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    output_dir = RESULTS_DIR / args.timestamp / "outputs"
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}", file=sys.stderr)
        print(f"Save skill outputs to {output_dir}/<fixture-name>.md first.", file=sys.stderr)
        sys.exit(1)

    results = []
    for fixture_meta in fixtures:
        result = run_fixture(fixture_meta, args.timestamp)
        results.append(result)

        # Print result
        status = "PASS" if result["structural_pass"] else "FAIL"
        if "error" in result:
            status = "SKIP"
        print(f"  [{status}] {result['fixture']} ({result['skill']})")
        for check in result.get("checks", []):
            check_status = "ok" if check["pass"] else "FAIL"
            print(f"    {check_status}: {check['check']} — {_check_summary(check)}")

    # Save structural results
    results_file = RESULTS_DIR / args.timestamp / "structural-results.json"
    results_data = {"timestamp": args.timestamp, "results": results}
    results_file.write_text(json.dumps(results_data, indent=2) + "\n")
    print(f"\nStructural results: {results_file}")

    # Update history
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        append_run(args.timestamp, valid_results)
        print(f"History updated: {HISTORY_FILE}")

    # Summary
    judge_dir = RESULTS_DIR / args.timestamp / "judge-prompts"
    judge_files = list(judge_dir.glob("*-judge.md")) if judge_dir.exists() else []
    if judge_files:
        print(f"\nJudge prompts generated ({len(judge_files)} files):")
        for f in sorted(judge_files):
            print(f"  {f}")


def _check_summary(check: dict) -> str:
    """One-line summary of a check result."""
    ct = check["check"]
    if ct in ("max_paragraph_count", "min_words_per_paragraph", "max_word_count", "finding_by_paragraph"):
        return f"threshold={check.get('threshold')}, actual={check.get('actual')}"
    if ct == "absent_phrase":
        found = check.get("found", [])
        return f"found={found}" if found else "none found (good)"
    if ct == "present_phrase":
        found = check.get("found", [])
        return f"found={found}" if found else "none found (bad)"
    if ct == "same_paragraph":
        return "phrases in same paragraph" if check["pass"] else "phrases in different paragraphs"
    if ct == "issue_category_rank":
        return f"top-{check.get('n')}: {check.get('actual_top_n')}"
    if ct == "line_edit_ratio":
        return f"ratio={check.get('actual_ratio')}, max={check.get('max_ratio')}"
    return str(check)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x scripts/run_eval.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/run_eval.py
git commit -m "feat: eval runner with structural checks and judge prompt generation"
```

---

### Task 11: End-to-end validation with a mock output

**Files:**
- Create: `results/test-run/outputs/intro-background-accretion.md` (temporary)

This task validates that the runner works end-to-end.

- [ ] **Step 1: Create a mock passing output for one fixture**

Create `results/test-run/outputs/intro-background-accretion.md`:

```markdown
Elite alignment plays a central role in the consolidation of authoritarian rule. When democratic checks weaken, the question is not whether elites respond but how different types of economic exposure shape their response. In interwar Japan, international sanctions against key industries created a natural experiment: legislators whose firms lost access to foreign markets faced acute pressure to seek alternative political arrangements, while legislators linked to military procurement — which expanded under the same geopolitical conditions — faced no comparable shock.

I show that sanctions-exposed legislators shifted their voting patterns toward authoritarian alignment, but only in prefectures with dense right-wing organizational networks. The effect is large: a one-standard-deviation increase in organizational density is associated with a 4.2 percentage point increase in authoritarian voting among exposed legislators. Legislators linked to military procurement showed no comparable shift, suggesting that the mechanism is specific to exclusionary economic shocks rather than to state dependence in general.

The identification strategy exploits the interaction between firm-level sanctions exposure and prefecture-level organizational density, using an instrumental variable based on historical Shinto shrine networks. The IV estimates confirm the OLS pattern, and a series of placebo tests support the exclusion restriction.

These findings contribute to the study of democratic erosion by identifying organizational infrastructure as a transmission mechanism through which economic pressure translates into anti-democratic elite mobilization. They also show that not all economic linkages to the state produce authoritarian alignment — the distinction between exclusionary shocks and inclusive procurement matters for how elites respond to democratic stress.
```

- [ ] **Step 2: Run the eval runner on the mock output**

```bash
cd "dev/calibration/writing-calibration"
python3 scripts/run_eval.py --timestamp test-run --fixture intro-background-accretion
```

Expected output:
```
  [PASS] intro-background-accretion (writing)
    ok: max_paragraph_count — threshold=4, actual=4
    ok: finding_by_paragraph — threshold=3, actual=2
    ok: absent_phrase — none found (good)

Structural results: results/test-run/structural-results.json
History updated: history.json

Judge prompts generated (1 files):
  results/test-run/judge-prompts/intro-background-accretion-judge.md
```

- [ ] **Step 3: Verify outputs exist**

```bash
cat results/test-run/structural-results.json | python3 -m json.tool
ls results/test-run/judge-prompts/
cat history.json | python3 -m json.tool
```

- [ ] **Step 4: Clean up test run**

```bash
rm -rf results/test-run
# Reset history.json to remove test entry
python3 -c "
import json
h = json.loads(open('history.json').read())
h['runs'] = [r for r in h['runs'] if r['timestamp'] != 'test-run']
open('history.json', 'w').write(json.dumps(h, indent=2) + '\n')
"
```

- [ ] **Step 5: Commit everything**

```bash
git add -A
git commit -m "feat: complete eval infrastructure — 8 fixtures, rubrics, runner, tested"
```

---

## Self-Review

**Spec coverage:**
- 8 atomic fixtures: Tasks 2-9 (all covered)
- Per-fixture rubric JSON: Tasks 2-9 (rubric written alongside each fixture)
- `run_eval.py` with structural checks + judge prompts: Task 10
- Updated `eval-set.json`: Task 1
- Updated `history.json` schema: Task 10 (runner updates it)
- Directory structure: Task 1

**Placeholder scan:** No TBDs, TODOs, or "implement later" found. All fixtures have complete manuscript text. All rubrics have complete check specifications. Runner has complete Python code.

**Type consistency:** `fixture_meta["name"]`, `fixture_meta["skill"]`, `fixture_meta["path"]`, `fixture_meta["rubric"]` match `eval-set.json` schema. Rubric JSON keys (`fixture`, `skill`, `structural_checks`, `judge_criteria`) match what the runner reads. Check types in rubrics match the runner's `run_structural_check` dispatch.
