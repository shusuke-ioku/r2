# Calibration Report: Writing Norms in APSR/AJPS Papers

Empirical audit of published APSR/AJPS papers and non-top-journal contrast papers. This report is the evidence base for all calibration rules in the writing and proofreading skills.

## Papers Audited

### Top journals (APSR/AJPS)
| Paper | Journal | Design |
|-------|---------|--------|
| Grumbach (2022) "Laboratories of Democratic Backsliding" | APSR | State-level panel, DiD |
| Naidu, Robinson & Young (2021) "Social Origins of Dictatorships" | APSR | Historical, cross-section + panel |
| Ahmed & Stasavage (2020) "Origins of Early Democracy" | APSR | Cross-section, IV |
| Abramson & Carter (2016) "Historical Origins of Territorial Disputes" | APSR | Cross-section, OLS + Cox |
| Grzymala-Busse (2023) "Tilly Goes to Church" | APSR | Grid-cell panel, two-way FE |
| Mayshar, Moav & Neeman (2017) "Geography, Transparency, and Institutions" | APSR | Formal model + historical cases |
| King, Pan & Roberts (2013) "How Censorship in China..." | APSR | Observational, scraping + prediction |
| Claassen (2019) "In the Mood for Democracy?" | APSR | Error-correction model, 135-country panel |
| Dasgupta & Ziblatt (2022) "Capital Meets Democracy" | AJPS | Pooled event study, country panel |
| Correa, Nandong & Shadmehr (2025) "Grievance Shocks and Protest" | AJPS | Formal model + interrupted time-series |

### Contrast group (non-top journals)
| Paper | Venue | Type |
|-------|-------|------|
| Gerschewski (2020) "Erosion or Decay?" | Democratization | Conceptual review |
| Riley (2010) *Civic Foundations of Fascism* | Cambridge UP (book) | Comparative-historical |
| Luo & Przeworski (2023) "Democracy and Its Vulnerabilities" | QJPS | Formal model |

---

## Finding 1: Claim Verbs Are Assertive, Not Hedged

### What top papers actually do

Main-finding verbs extracted from audited APSR/AJPS papers:

| Paper | Design | Primary verb for main finding |
|-------|--------|-------------------------------|
| Grumbach | DiD | "**reduces**" — "Republican control of state government reduces democratic performance" |
| King et al. | Observational | "**shows**" — "This clearly shows support for the collective action potential theory" |
| Claassen | ECM panel | "**produce**" — "changes in minoritarian democracy...produce a marked negative effect" |
| Dasgupta & Ziblatt | Event study | "**resulted in**" — "franchise extensions resulted in large increases in sovereign bond yields" |
| Abramson & Carter | Cross-section | "**demonstrates**" — "This again nicely demonstrates that the presence of multiple historical precedents drives the emergence of territorial claims" |
| Grzymala-Busse | Two-way FE | "**show**" — "I show instead that political fragmentation was the outcome of deliberate choices" |
| Ahmed & Stasavage | IV | "**establish**" — "This will establish that there is a strong correlation" |
| Correa et al. | Formal + ITS | "**show**" — "We show that a large sudden increase in aggregate grievances...will lead to protests" |
| Mayshar et al. | Formal model | "**confirm**" — "These results confirm that when transparency is sufficiently low..." |
| Naidu et al. | Cross-section | "**is consistent with**" — outlier; explicitly disclaims causality |

**The verb hierarchy actually used in top journals:**

| Research design | Verbs actually used | Notes |
|----------------|--------------------|----|
| RCT / natural experiment | causes, increases, reduces | Direct causal claims |
| DiD / panel FE / event study | reduces, produces, resulted in, drives | Causal verbs standard |
| IV | increases, effect of, establish | "Effect" language, sometimes "establish" |
| Cross-section with strong controls | is associated with, drives, contributed to | "Associated with" baseline; quasi-causal when mechanism is clear |
| Observational / descriptive | shows, finds, reveals, demonstrates | Confident but not causal |
| Formal model results | confirm, implies, indicates, show | Mathematical entailments stated flatly |

**Contrast:** Non-top papers use: "suggest," "propose," "argue," "I think it is fair to argue," "hopefully helpful," "I would suggest," "I believe."

### What the old skill prescribed

> Bad: "demonstrates a general mechanism" → Good: "documents," "provides evidence consistent with"

This was **wrong**. "Demonstrates" is used in APSR (Abramson & Carter 2016). "Provides evidence consistent with" is appropriate only for weak auxiliary tests, not for a paper's main finding.

**Revised verb guidance:** See prose-standards.md, Calibration section.

---

## Finding 2: Hedging Is Asymmetric, Not Uniform

### What top papers actually do

Top papers apply a sharp asymmetry:

- **Main findings: flat assertions, no hedging.** Grumbach: "a large negative relationship." King: "The results are unambiguous." Claassen: "These thermostatic effects are significant in all of the four models." Dasgupta: "The empirical analyses reveal that franchise extensions resulted in large increases."
- **Auxiliary findings: moderate hedging.** King: "we seem to have unearthed" (secondary implication). Correa: "Our analysis suggests" (empirical section of a theory paper, framed as "proof of concept"). Ahmed: "provides some evidence" (mechanism test).
- **Null covariates: flat, often turned into positive evidence.** Grumbach: "no relationship between polarization and democracy." King: "has no measurable effect." Grzymala-Busse: "is not associated with."

**Hedge density:** In results paragraphs of top papers, hedging phrases appear 0-1 times per paragraph for main results, 1-2 times for secondary results.

**Contrast:** Non-top papers hedge 3-5 times per paragraph. Gerschewski: ~4:1 hedged-to-unhedged ratio. Riley: ~2:1.

### What the old skill prescribed

The combined effect of the writing skill's Calibration principle, the overclaiming quick-reference, and the proofreading skill's Overclaiming category was to push hedging on every finding. The cumulative pressure produced more hedging than any top APSR paper.

**Revised guidance:** Hedge asymmetrically. State main findings flatly. Reserve hedging for genuinely uncertain auxiliary tests.

---

## Finding 3: Causal Language Tracks Design Strength

### What top papers actually do

Papers with quasi-experimental designs use causal verbs freely:
- **DiD:** Grumbach: "reduces" | Dasgupta: "resulted in"
- **Panel with FE:** Claassen: "produce" | Grzymala-Busse: "contributed to"
- **Cross-section with controls:** Abramson: "drives" | Ahmed: "correlation" (IV section uses "effect")

Papers without strong identification disclaim causality explicitly:
- Naidu et al.: "these results should ultimately not be interpreted as conclusive evidence of a unidirectional causal relationship"

**The line is not "causal vs. associational."** It is: **does the design support the verb?**

- DiD/event study/IV with parallel trends → causal verbs fine
- Cross-section with controls + Oster test → quasi-causal ("drives," "contributes to") fine
- Cross-section without identification → "associated with," "correlated with"
- Descriptive → "shows," "finds"

### What the old proofreading skill flagged

The old overclaiming category flagged "X drove Y" or "X was driven by Y" when "the research design identifies a correlation or a suggestive pattern." This is **too aggressive** — it would flag Grumbach's "reduces" and Dasgupta's "resulted in," both published in APSR/AJPS with standard quasi-experimental designs.

**Revised guidance:** Flag causal language only when it exceeds what the research design supports. DiD/IV/event study designs support causal verbs.

---

## Finding 4: Limitations Are Brief, Inline, and Scattered

### What top papers actually do

| Paper | Limitation words (approx.) | Standalone section? | Location |
|-------|---------------------------|--------------------|----|
| Grumbach | 200-300 | No | Inline in methods + footnotes |
| Naidu et al. | 200 | No | End of results paragraph |
| Ahmed & Stasavage | 300-400 | No | Inline in analysis sections |
| Abramson & Carter | 200 | No | Inline + Online Appendix reference |
| Grzymala-Busse | 150 | No | Footnotes + inline |
| King et al. | 50-100 | No | Brief inline |
| Claassen | 50-100 | No | Brief inline |
| Dasgupta & Ziblatt | Inline as concerns arise | No | Woven into results |
| Correa et al. | 100 + "proof of concept" framing | No | Upfront "what results do not say" |
| Mayshar et al. | 200 | No | Upfront in intro |

**Zero top papers have a standalone limitations section.** Limitations are always brief (100-300 words total), scattered across methods and results, often in footnotes.

**Contrast:** Non-top papers also lack standalone sections, but their hedging is so pervasive that the entire text reads like a limitation.

---

## Finding 5: Topic Sentences Vary by Section Type

### What top papers actually do

In **results sections**, topic sentences are approximately 50/50:
- **Claim-first:** "The results are starkly different for changes in minoritarian democracy" (Claassen). "These findings suggest that racial politics within states are not central" (Grumbach).
- **Table-reference-first / purpose-first:** "Table 1 presents the main results" (multiple papers). "In this section we test our prediction" (Naidu). "I present the main results in Table 1" (Grumbach).

In **theory/lit review sections**, topic sentences are overwhelmingly claim-first, consistent with current skill guidance.

### What the old skill prescribed

> Open every body paragraph with a topic sentence that states a claim, not a literature summary.

This is correct for theory and lit review paragraphs but **too rigid for results paragraphs**, where "Table X reports..." and "In this section we test..." are standard openers.

**Revised guidance:** Claim-first for theory/lit review. In results, table references and purpose statements are standard openers; the claim follows immediately after.

---

## Finding 6: Introductions State the Finding by Paragraph 2-3

### What top papers actually do

| Paper | Paragraph where main finding stated | Paragraph 1 function |
|-------|-----------------------------------|----|
| Ahmed & Stasavage | 1 (abstract-style opening) | Key finding stated directly |
| Abramson & Carter | 1-2 | Knowledge gap → finding |
| Grzymala-Busse | 1 (abstract embedded) | Field statement → thesis |
| Naidu et al. | 2-3 | Macro stylized fact → theory |
| King et al. | 2-3 | Puzzle → finding |
| Dasgupta & Ziblatt | 2 | Big question → finding |
| Grumbach | 4-5 | Contemporary motivation → gap → finding |
| Claassen | 3-4 | Crisis framing → existing theories → finding |
| Correa et al. | 2-3 | Puzzle → model description |
| Mayshar et al. | 3-4 | Broad question → theory → argument |

**Median: paragraph 2-3.** The finding appears on page 1 in the vast majority of audited papers.

**Paragraph 1 functions (distribution):**
- Knowledge gap / puzzle: 3 papers
- Bold claim / finding: 3 papers
- Contemporary motivation: 2 papers
- Field-level framing: 2 papers

The current skill's intro structure (puzzle → answer → how → contributions) is approximately right, but the skill should emphasize: **the finding must appear by paragraph 2-3, on page 1.**

---

## Finding 7: Conclusions Are Brief and Forward-Looking

### What top papers actually do

| Paper | Conclusion length | Function |
|-------|------------------|------|
| Grumbach | ~400-500 words | Summary + nationalization framing + future research |
| Naidu et al. | ~200-300 words | Brief summary + broader implications |
| King et al. | ~2 paragraphs | Summary + new data implications |
| Claassen | ~1-2 paragraphs | Summary + reframing ("this stands in contrast...") |
| Dasgupta & Ziblatt | ~2 paragraphs | Summary + broader democracy implications |
| Grzymala-Busse | ~400-500 words | Summary + literary/ironic conclusion |
| Abramson & Carter | ~300-400 words | Summary + case illustration + future research |

**Pattern:** 200-500 words. Summary + implications. Occasionally literary (Grzymala-Busse: "In winning battles, the Church lost the war"). Never introduces new analysis. Never extensively caveats.

---

## Finding 8: Main Findings Are Restated 3-5 Times

### What top papers actually do

Every top paper restates its main finding 3-5 times:
1. Abstract (short, punchy)
2. Introduction (with framing/contribution context)
3. Results section (with coefficients/statistics)
4. End of results (summary before robustness)
5. Conclusion (with implications)

Each restatement adds something: precision, quantification, theoretical context, implications.

This is **not redundancy** — it is strategic reinforcement. The proofreading skill should not flag this pattern.

**Contrast:** Non-top papers also restate, but add nothing new in each iteration (Gerschewski restates the erosion/decay distinction 5+ times with identical wording).

---

## Finding 9: Paragraph Length Is Tight in Results

### What top papers actually do

| Section | Typical paragraph length |
|---------|------------------------|
| Introduction | 4-8 sentences |
| Theory / lit review | 5-10 sentences |
| Results | 4-7 sentences |
| Conclusion | 5-8 sentences |

Results paragraphs are the **tightest** in the paper. Long discursive results paragraphs (8-12 sentences) appear only in King et al., which interleaves methodology heavily with results.

**Contrast:** Non-top papers have longer paragraphs throughout (Gerschewski: 8-12, Riley: 6-10).

---

## Finding 10: Voice Is Uniformly First-Person Active

### What top papers actually do

- Single-author: "I show," "I find," "I argue" (Grumbach, Grzymala-Busse, Claassen)
- Multi-author: "We show," "We find," "We demonstrate" (all others)
- Active voice dominant everywhere except table references ("The results are reported in Table 1")
- **No passive hedging constructions** like "It could be argued that" or "It might be suggested that"

---

## Summary: Top-Journal Norms vs. Old Skill Prescriptions

| Dimension | What top papers do | What the old skill prescribed | Gap |
|-----------|-------------------|------------------------------|-----|
| **Main-finding verbs** | show, demonstrate, reveal, reduce, produce, result in | "documents," "provides evidence consistent with" | Skill too timid |
| **Hedging pattern** | Asymmetric: flat on main, hedged on auxiliary | Uniform hedging pressure | Skill over-hedges |
| **Causal verbs** | Used freely for DiD/IV/event study | Flagged as overclaiming | Skill too restrictive |
| **Limitation placement** | 100-300 words, inline, scattered, no section | Not addressed explicitly | Missing guidance |
| **Topic sentences in results** | 50/50 claim-first vs. table-reference | "Always claim-first" | Skill too rigid for results |
| **Intro timing** | Finding by paragraph 2-3 | "Deliver punchline fast" (vague) | Needs quantification |
| **Conclusion** | 200-500 words, brief, forward-looking | Not specified | Missing guidance |
| **Restatement** | 3-5x with progressive precision | Could be flagged as redundancy | Proofreading false positive |
| **Results paragraph length** | 4-7 sentences | Not specified | Missing guidance |
| **Voice** | First person, active, assertive | Correct | No gap |
