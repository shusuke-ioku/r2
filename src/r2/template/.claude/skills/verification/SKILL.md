---
name: verification
description: >
  Use when completing any task that changes R scripts, analysis outputs, the Typst
  manuscript, or any multi-step workflow. Use when about to report "done" or "fixed"
  or "updated." Use when the agent has expressed confidence, satisfaction, or
  completion intent without showing fresh evidence. Use when the agent says "should
  work now," "looks correct," or "I believe this is right." If the task touched code,
  data, or the paper, this skill must gate the final response---no exceptions.
---

# Verifier

No claim of completion without proof. Ever.

## The Rule

Before reporting any task as done, you must produce **fresh, timestamped evidence** that the change works. "I edited the file" is not evidence. "The script ran and produced output X" is evidence. "I updated the paper" is not evidence. "`typst compile` exited 0 and the relevant passage now reads Y" is evidence.

If you cannot produce the evidence, you are not done.

## Verification Gates

Every claim requires specific evidence. No substitutes.

| Claim | Required Evidence |
|---|---|
| "R script is fixed" | Show the script ran to completion (exit 0) via `bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target <script>`. Paste key output lines. |
| "Results updated" | Read the updated file(s) in `analysis/output/results/` and report changed values (direction, magnitude, significance). |
| "Paper compiles" | Run `typst compile --root . paper/paper.typ` and show exit 0. |
| "Paper is aligned with results" | Read both the latest output file and the corresponding passage in `paper/paper.typ`. Quote the matching numbers side by side. |
| "Bug is fixed" | Reproduce the original failure condition, show it no longer fails, and show the correct output. |
| "Multi-step task complete" | Each step has its own verification evidence, presented in order. |
| "Table/figure updated" | Read the output file, then read the paper passage. Show they match. |
| "New script works" | Run it. Show exit 0. Read its output. Report key findings. |

## Rationalization Table

These are excuses. Do not use them.

| What You Want to Say | What It Actually Means | What to Do Instead |
|---|---|---|
| "Should work now" | You did not run it | Run it |
| "Looks correct" | You eyeballed it without executing | Execute it |
| "I'm confident this is right" | You are guessing | Verify |
| "The change is straightforward" | You assume no side effects | Run the pipeline and check |
| "I updated the paper to match" | You edited text but did not compile or cross-check | Compile, then read both source and paper |
| "This should fix it" | You wrote a patch but did not test | Test |
| "Based on the previous output" | You are using stale data | Rerun and read fresh output |
| "I believe the numbers match" | You did not compare them | Compare them, side by side, right now |

## Workflow

### After any R script change

1. Run the script: `bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target <script_name>`
2. If it fails: fix and rerun. Do not report the fix until it passes.
3. Read the output files it produces in `analysis/output/results/`.
4. Report key results (coefficients, significance, sample sizes).

### After any paper edit

1. Compile: `typst compile --root . paper/paper.typ`
2. If compilation fails: fix and recompile. Do not report success until exit 0.
3. Read the edited passage back from the file to confirm the edit landed correctly.

### After results change

1. Complete the R script verification above.
2. Read the updated output files.
3. Read the corresponding sections of `paper/paper.typ`.
4. Compare numbers, signs, significance stars, and prose claims. Quote both sources.
5. Fix any mismatches. Recompile. Verify again.

### After a multi-step task

Verify each step independently before moving to the next. Do not batch-verify at the end. A failure in step 2 makes steps 3--5 meaningless.

## Red Flags

If you catch yourself doing any of the following, stop and verify:

- Expressing satisfaction or confidence before running the code
- Using the word "should" in a completion statement
- Reporting success based on what you *edited* rather than what you *observed*
- Skipping compilation because "it was just a small change"
- Skipping the pipeline because "only one line changed"
- Assuming output files are current without reading them after a fresh run
- Saying "done" without quoting specific evidence in the same message

## Enforcement

This skill is not advisory. It is a gate. The final message of any task that touches code, outputs, or the paper must contain:

1. The exact command(s) run for verification
2. Their exit status
3. Key output values or compilation result
4. Side-by-side comparison if results and paper are both involved

If any of these are missing, the task is not complete. Go back and verify.
