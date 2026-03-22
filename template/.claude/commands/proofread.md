Trigger the proofreader agent. Simulate a first-time reader and diagnose flow issues.

Target: $ARGUMENTS (e.g., "the full paper", "introduction through theory", "results section")

Use the proofreader agent (read-only, no edits) to:
1. Read paper/paper.typ sequentially from beginning to end
2. Track the reader's mental state (what they know, expect, wonder)
3. Flag every moment understanding breaks down
4. Classify issues: logical gap, forward reference, expectation violation, undefined term, buried claim, redundancy, pacing, overclaiming
5. Rate severity: Blocks comprehension / Causes confusion / Minor friction
6. Check abstract is under 150 words
7. Output a numbered checklist in reading order, then detailed analysis
