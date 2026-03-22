# Threat Taxonomy

Use these categories to classify objections. Each claim-level objection should be tagged with exactly one threat type. If an objection spans multiple types, pick the primary one and note the secondary in the "Notes" field.

---

## 1. Logical Gap

The argument's internal logic does not hold. The conclusion does not follow from the premises, even granting all empirical claims.

**What to look for**: Non sequiturs, unstated assumptions that do real work, leaps from correlation language to causal language without justification, contradictions between sections.

**Example**: "The paper argues that organizational density caused electoral gains, but the theoretical framework in Section 2 describes a mechanism that operates through elite signaling, not mass mobilization. The empirical test (organizational density) does not map onto the stated theory (elite signaling). Either the theory or the test needs to change."

---

## 2. Empirical Weakness

The data or evidence presented does not adequately support the claim. The evidence exists but is too thin, too noisy, or from a problematic source.

**What to look for**: Small samples, large standard errors, selective presentation of results, reliance on a single data source when multiple exist, outdated data when newer data is available.

**Example**: "The protest count variable comes from newspaper reports, which systematically undercount rural protests (as documented in [Author Year]). If rural areas had more unreported protests, the urban-rural gradient in Table 3 could be an artifact of reporting bias."

---

## 3. Identification Failure

The causal identification strategy has a specific, articulable flaw. This is distinct from empirical weakness---the data might be fine, but the research design does not isolate the causal channel claimed.

**What to look for**: Violation of exclusion restrictions, failure of parallel trends, bad-control problems, collider bias, weak instruments, SUTVA violations, contamination across treatment and control units.

**Example**: "The difference-in-differences design assumes parallel trends between treated and control units. But Figure 2 shows diverging trends starting two years before treatment. The authors should either (a) present a formal pre-trend test, (b) use a method robust to pre-trend violations (e.g., Rambachan and Roth 2023), or (c) restrict the sample to units with demonstrably parallel pre-trends."

---

## 4. Alternative Explanation

A different mechanism or cause could produce the same observed pattern. The paper's preferred explanation is not the only one consistent with the evidence.

**What to look for**: Omitted variables that correlate with both treatment and outcome, confounders the author did not discuss, competing theories in the published literature that predict the same empirical patterns.

**Example**: "The paper attributes the rise of radical organizations to economic distress. But [Author Year] documents that a parallel state-building program expanded into rural areas in exactly this period. The organizational infrastructure, not economic distress alone, may explain the pattern. A test using variation in this alternative infrastructure would help distinguish these explanations."

Always ground alternative explanations in published work. A speculative "maybe X caused Y" without a citation is easy to dismiss. A "Smith (2019) documents that X caused Y in a similar context" is not.

---

## 5. Scope Overreach

The evidence supports a narrower claim than the one made. The author generalizes beyond what the data, sample, or context permits.

**What to look for**: Claims about "democracies" based on one country, claims about "economic shocks" based on one shock, extrapolation from a specific historical context to general theory without qualification, abstract language that disguises narrow evidence.

**Example**: "The abstract states that 'economic crises create opportunities for anti-democratic mobilization.' The evidence comes from one country during one crisis in one institutional context. The claim should be qualified to match the actual scope of the evidence. The broader generalization is a hypothesis the paper motivates, not a finding it establishes."

---

## 6. Measurement Concern

A key variable is measured in a way that may not capture what it claims to capture. The construct validity is questionable.

**What to look for**: Proxies that are distant from the concept of interest, coding decisions that embed assumptions, variables that conflate distinct phenomena, measurement error that correlates with other variables in the model.

**Example**: "The paper uses 'number of organizations' as a proxy for movement strength. But a region with ten small groups of five members each is coded the same as a region with ten large groups of five hundred members each. If organizational size correlates with the treatment variable, this introduces systematic measurement error. Weighting by membership (if available) or using an alternative measure like event counts would address this."

---

## 7. Missing Evidence

A claim is asserted without supporting evidence, or the evidence that would be most convincing is absent. Different from empirical weakness---here the evidence is simply not presented.

**What to look for**: Unsupported assertions in the text, claims that "it is well known that..." without citation, theoretical mechanisms described but never tested, obvious tests that the reader expects but the paper does not include.

**Example**: "Section 3 argues that the ideology appealed specifically to a vulnerable population because of its reform rhetoric. But no evidence is presented linking that population's status to organizational membership. At minimum, the paper should show a correlation between the population share and organizational density at the subnational level."

---

## 8. Non-Novelty

The paper's claimed contribution has already been established in prior work. The paper does not sufficiently differentiate itself from existing literature.

**What to look for**: Published papers that make the same argument with the same or better evidence, papers in adjacent fields that the author may not know about, recent working papers that scoop the contribution.

**Example**: "[Author Year] already demonstrates a similar finding using similar data and a similar design. The authors need to articulate clearly what their paper adds---is it a different mechanism, a different outcome, better data, or a different identification strategy? Without this, a reviewer will ask 'what's new here?'"

When flagging non-novelty, be precise about what overlaps and what does not. Partial overlap is common and usually manageable with better positioning. Full overlap is rare but fatal.
