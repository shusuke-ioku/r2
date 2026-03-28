# Critique Framework

Work through every lens below. Skip nothing -- even strong papers have
identifiable limitations, and the user needs an honest map of where a source
is reliable and where it is not.

## 1. Question and Contribution

- Is the research question stated explicitly, or must you infer it?
- What is the exact marginal contribution over the closest prior work? Name
  the prior work.
- Does the paper demonstrate both novelty (no one has done this) and relevance
  (someone should)?
- Is the question important for substantive or theoretical reasons, or mainly
  for methodological novelty?
- Could the question be answered more directly with a different design?

## 2. Theory and Mechanism

- Are causal mechanisms clearly specified? Can you draw a DAG from the text?
- Are scope conditions explicit? Under what conditions does the theory predict
  no effect or a reversed effect?
- Does the author name rival mechanisms that could produce the same observable
  pattern? Are they tested or merely acknowledged?
- Is the theory micro-founded (individual-level logic) or purely macro
  (aggregate correlation repackaged as theory)?
- Would the mechanism travel to the user's empirical context, or does it
  depend on context-specific institutions that differ from the project's
  setting?

## 3. Design and Identification

- What is the identification strategy? (Difference-in-differences, IV, RDD,
  matching, panel FE, descriptive, process tracing, etc.)
- What are the core identifying assumptions? Are they stated or must you infer
  them?
- List the top 3 threats to internal validity. Does the author address them?
  How convincingly?
- For DiD: Is the parallel trends assumption tested? Pre-trends shown?
  Staggered treatment handled?
- For IV: Is the exclusion restriction plausible? Is the first stage strong?
- For any design: Could reverse causality, selection, or confounding survive
  the controls?
- What robustness checks are run? What obvious checks are missing?
- Is the sample large enough for the design to have power? Are results
  sensitive to dropping observations?

## 4. Measurement

- Are core constructs (DV, key IVs) measured with face validity? Would an
  informed skeptic accept the operationalization?
- Is there coding ambiguity? Multiple coders? Inter-coder reliability?
- For historical data: What is the original source? How was it digitized? Are
  there known biases in the archive?
- Is the temporal alignment correct? Does the IV precede the DV in the causal
  window claimed?
- Is the geographic unit appropriate? Could aggregation or disaggregation
  change the result (MAUP)?
- Are there floor/ceiling effects, heavy censoring, or measurement error that
  could attenuate or inflate estimates?

## 5. Inference and Interpretation

- Are effect sizes substantively meaningful, not just statistically
  significant? Does the author discuss magnitudes?
- Is uncertainty properly reported? Confidence intervals, not just stars?
- Does the author claim causation when the design supports only association?
- Are null results interpreted honestly, or explained away?
- Does the conclusion stay within what the design actually identifies, or does
  it drift into policy/normative claims unsupported by the evidence?
- Are heterogeneous effects explored? Could the average effect mask important
  variation?

## 6. Relevance for This Project

- Which theoretical ideas strengthen or challenge the framing in
  `paper/paper.typ`?
- Which empirical strategies could be adapted for the project's context?
  What would need to change?
- Which measurement choices offer useful precedent for the project's own
  variables?
- Which pitfalls in this source should the project actively avoid?
- Does this source need an atomic paper note in `notes/papers/`?
  Which thematic MOC in `notes/lit/` should link to it?
- Could a reviewer of the user's paper cite this source as a challenge? If so,
  how should the user preempt it?
