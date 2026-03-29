# Prose Standards

Detailed rules for prose in `paper/paper.typ`. Load this file whenever writing or revising manuscript text.

## Argument First (Body Paragraphs)

In body sections (lit review, theory, results, discussion), the argument lives in topic sentences. A reader who reads only the first sentence of every paragraph should be able to reconstruct the full argument.

- Open every body paragraph with a **topic sentence that states a claim**, not a literature summary. Citations are evidence marshaled in support, not the point.
  - Good: "Peripheral status---not poverty---is the critical precondition for radical mobilization."
  - Bad: "Several scholars have studied the relationship between economic conditions and radical mobilization (Smith 2020; Jones 2021)."
- **Results section exception.** In results sections, table-reference openers are standard: "Table 1 reports the main results" or "In this section we test our prediction that..." The claim follows immediately after. In APSR/AJPS, roughly half of results paragraphs open with table references or purpose statements rather than claims. Both patterns are standard.
- One idea per paragraph. If a paragraph serves two purposes, split it. If you cannot state its point in one sentence, restructure.
- Place the most important claim in the first or second sentence, not the last. Burying the point at the end forces readers to hold material in working memory without knowing why it matters.

## Punch First (Introduction and Abstract)

The introduction and abstract play by different rules. Their job is to sell the paper---to make a reviewer, editor, or conference attendee want to keep reading. The topic-sentence requirement is suspended here. Instead:

- **Lead with the most arresting hook**: a vivid historical fact, a striking puzzle, a counterintuitive finding, a bold claim. The first sentence should make the reader lean in.
- **Deliver the punchline fast**: the reader should know what the paper finds by the end of the first paragraph. Do not build up slowly.
- **Write as if the reader will stop after three sentences** unless you give them a reason to continue. Most will.
- **Avoid dutiful throat-clearing** ("Democracy is important." "Scholars have long studied..."). These openings signal a boring paper. Start with something only this paper can say.

## Precision

Precise prose signals that the author knows exactly what matters and what doesn't.

- Use short, declarative sentences for key claims. Save complex syntax for genuinely complex ideas---if the idea is simple, the sentence should be too.
- Cut throat-clearing ("It is worth noting that...", "Importantly,..."). These phrases delay the claim without adding information. Just state it.
- Delete filler adverbs ("very", "quite", "relatively", "somewhat") unless they do real epistemic work. "Relatively" is fine when comparing two specific quantities; it is filler when softening a claim you're not sure about.
- Drop inflated adjectives ("crucial", "fundamental", "groundbreaking"). If the contribution is real, the substance carries it. Adjectives that try to do the work of evidence signal insecurity.
- Limit em-dashes: prefer commas, parentheses, colons, or separate sentences. One em-dash pair per paragraph at most. Overuse creates a breathless, digressive tone.
- Anchor claims in specifics---names, dates, numbers, places---not abstractions. "Union membership grew 340% between 1931 and 1936" beats "labor organizations experienced dramatic growth during this period."

## Calibration

Calibration is the difference between a paper that reviewers trust and one they dismiss. The verb tracks the research design, not generic caution. Evidence base: `calibration-report.md` (audit of published APSR/AJPS papers).

### Design-calibrated verbs

Top APSR/AJPS papers use causal verbs for well-identified designs and descriptive verbs for observational work:

- DiD / event study / RCT → "reduces," "increases," "produces," "resulted in"
- IV / RDD → "the effect of X on Y," "increases," "establishes"
- Panel FE with strong controls → "produces," "is associated with," "contributed to"
- Cross-section with sensitivity tests → "drives," "is associated with," "predicts"
- Descriptive / observational → "shows," "finds," "reveals," "demonstrates"
- Formal model results → "confirms," "implies," "indicates"

### Asymmetric hedging

State main findings flatly. Reserve hedging for secondary tests, mechanism explorations, and results you are genuinely uncertain about.

- Main finding (no hedge): "Republican control reduces democratic performance" (Grumbach 2022, APSR). "The results are unambiguous" (King et al. 2013, APSR).
- Auxiliary test (moderate hedge): "Our analysis suggests" (Correa et al. 2025, AJPS---empirical section of a theory paper, framed as "proof of concept").
- Mechanism (hedge): "provides some evidence that" (Ahmed & Stasavage 2020, APSR).
- Null on competitor: flat assertion: "has no measurable effect" (King et al. 2013, APSR). "is not associated with" (Grzymala-Busse 2023, APSR).

### What not to hedge

- Main findings with clean identification
- Null results on competing theories (these are positive evidence for your argument)
- Formal model results (mathematical entailments)
- Well-established descriptive facts

### What to hedge

- Secondary findings and mechanism tests
- Marginal results (p < 0.10)---report the p-value, let readers judge
- Speculative implications beyond the scope of the data
- Claims outside the case or population studied

### Other calibration rules

- Prefer precise language ("93 percent increase within two years") over vague intensifiers ("dramatic surge"). Quantification anchors the reader and preempts skepticism.
- Never claim "the first to" or "novel contribution" unless verifiably true. Show the gap by describing what prior work does and does not do---the reader will see the novelty.
- State limitations briefly, inline, scattered across methods and results. No standalone limitations section. Top APSR papers scatter 100-300 words of limitations total, often in footnotes. Repeating caveats signals you don't believe your own findings.
- If the contribution is real, state it plainly. "This paper identifies..." not "This paper attempts to shed some light on..." The latter reads as an apology for the paper's existence.

## Assertiveness in Literature Engagement

This section governs how the paper engages with existing literature---distinct from Calibration above, which governs how the paper reports its own findings. Evidence base: 20+ recent APSR papers (2019--2026); see `section-forms.md` for the full audit.

### Stating Conventional Wisdom

In APSR/AJPS papers, conventional wisdom is stated as fact:
- "Dictators confront a guardianship dilemma" (Paine 2022) --- not "Scholars have argued that dictators face..."
- "Rural areas are conservative electoral strongholds" (Dasgupta 2024) --- not "The literature suggests that rural areas tend to..."
- "Public support has long been thought crucial for the vitality and survival of democracy" (Claassen 2019)

The reader is a political scientist. They know the conventional wisdom. State it; do not explain who said it or hedge that it might not be universally accepted. The citations do the attribution work.

### Challenging Conventional Wisdom

Challenge directly:
- "I show instead that political fragmentation was the outcome of deliberate choices" (Grzymala-Busse 2023)
- "We revise the conventional wisdom that Africa's international borders were drawn arbitrarily" (Paine et al. 2024)
- "Yet such perspectives overlook moments when elites align not from opportunity, but from constraint" (Fukumoto 2026)

Do not soften the challenge: never write "While the prevailing view has merit, this paper offers an alternative perspective..." State what the conventional view misses and what your paper shows, directly.

### Synthesizing Multiple Literatures

When combining insights from multiple works into a single claim, present the synthesis as a logical consequence of the literatures, not as your interpretive construction:
- Good: "When parties exclude radicals and the military contains its radical faction, the conventional pathways to breakdown are closed."
- Bad: "Together, these literatures produce what I call a 'two-gates' expectation..."
- Bad: "The expectation is a cumulative implication, not any single work's claim..."

The reader does not need you to disclaim that your synthesis is your synthesis. If the logic is clear, they will follow it.

## Citations

Citations position the paper in a literature. They are strategic, not decorative.

- Cite to **position your claim** relative to the literature, not to demonstrate reading. Every citation must do work: support a claim, mark a contrast, or identify a gap.
- Use parenthetical form for background consensus: "...executives who aggrandize power @bermeo2016 @svolik2019."
- Use prose citations when engaging a specific argument: "Ziblatt et al. (2024) provide the most granular evidence to date, showing that..."
- Cluster related citations rather than sprinkling them sentence by sentence. A paragraph with six separate citation sentences reads like an annotated bibliography, not an argument.
- Never cite a paper you have not read. Use RAG tools to verify content before citing. Mischaracterizing a source is worse than omitting it.

## Introduction Structure

Structure the introduction as a logical chain. Each element answers the question the previous one raises. **The main finding must appear by paragraph 2-3, on page 1.** In our audit of published APSR/AJPS papers, the vast majority state the finding on the first page.

1. **Puzzle / gap**: What does the literature miss or get wrong? (1 paragraph) --- This is the question that justifies the paper's existence. Frame it as a genuine intellectual puzzle, not a gap-in-the-literature complaint.
2. **This paper's answer**: What do you do, and what do you find? (1 paragraph) --- State the answer plainly. The reader should know the main finding by paragraph 2-3.
3. **How you know**: Identification strategy, key evidence, credibility. (1--2 paragraphs) --- Explain why the reader should believe the finding. Name the data, the variation, the key test.
4. **Contributions**: What changes in our understanding? One paragraph per contribution, framed against specific prior work. --- Each contribution paragraph names what was believed before and what this paper changes.

Avoid "This paper proceeds as follows" roadmaps unless the structure is genuinely non-obvious. Roadmaps consume space without advancing the argument.

## Conclusion Structure

Keep conclusions brief: 200-500 words, 2-3 paragraphs. In our audit, no APSR/AJPS paper had a conclusion longer than ~500 words.

1. **Summary** (1 paragraph): Restate the main finding with its implications, not just a recapitulation. Add the "so what."
2. **Broader implications** (1 paragraph): Connect to the larger literature or contemporary relevance. This is where you can be slightly more speculative---but stay grounded.
3. **Optional: future research** (1-2 sentences): Only if genuinely pointing toward a productive next step, not a dutiful "more research is needed."

Do not introduce new analysis, new data, or new caveats in the conclusion. Do not extensively requalify results you already presented. The conclusion should leave the reader with confidence in the contribution, not doubt.
