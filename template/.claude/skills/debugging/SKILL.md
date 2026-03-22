---
name: debugging
description: >
  Use when an R script throws an error or warning, a Typst compilation fails,
  regression outputs look wrong (sign flips, NA coefficients, implausible
  magnitudes), the pipeline runner exits non-zero, or the user reports that
  "something broke" or "results look off." Also use when you encounter an
  error during any other skill's workflow and need a systematic fix.
---

# Debugger

Systematic root-cause debugging for R and Typst failures in this project. This is a rigid skill -- follow the phases in order, do not skip steps.

## Iron Law

**No fix without diagnosis.** Never change code to "see if this helps." Every edit must follow from a specific hypothesis about what is wrong and why. Shotgun fixes mask root causes, introduce new bugs, and waste cycles.

## Phase 1 -- Read and Reproduce

1. **Read the full error.** Read the complete traceback or compiler output. Do not skim. The root cause is usually in the deepest frame, not the surface message.
2. **Reproduce consistently.** Run the failing script via the pipeline runner:
   ```bash
   bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target SCRIPT_NAME
   ```
   For Typst: `typst compile --root . paper/paper.typ`. Confirm the error recurs. If it does not, the problem is environmental (stale session state, cached objects) -- note this.
3. **Check recent changes.** Run `git diff` and `git log --oneline -5` to see what changed since the last known-good state. Most bugs are caused by the most recent edit.

## Phase 2 -- Known Gotchas Checklist

Before deeper investigation, check these project-specific traps. They account for the majority of failures:

| Symptom | Likely cause | Fix |
|---|---|---|
| Silent wrong coefficients after `conleyreg` call | conleyreg v0.1.8 corrupts fixest internal state when same formula is reused with different data in a loop | Deep-copy data: `as.data.frame(data)[,,drop=FALSE]`. Rebuild data from scratch in loops -- never subset a shared parent tibble. |
| `could not find function "X"` | Missing library load | Ensure script sources `00_setup.R` at the top. Check that the needed package is loaded there. |
| Merge produces NAs or drops rows | Key variable normalization mismatch | Apply `stringr::str_squish()` and consistent normalization to both sides of the join before merging. |
| Date column is character, not Date | `as_date()` not applied or format string wrong | Wrap with `lubridate::as_date()` using the correct format. |
| Model uses stale variable or wrong N | Data object is outdated | Re-source `20_data.R` (or run the pipeline from data step). Verify object dimensions after load. |
| Typst compile error: "expected X, found Y" | Malformed Typst syntax | Read the error line number. Common culprits: unmatched `$` in math mode, missing `#` before function calls, unclosed brackets, raw `%` or `&` outside math mode. |
| Typst compile error in table | Mismatched column count or bad `table.cell` span | Count columns in the `table()` call. Every row must fill exactly the declared column count (accounting for `colspan`). |

If the symptom matches a row in this table, apply the fix directly and go to Phase 4. Do not over-investigate known problems.

## Phase 3 -- Hypothesize and Minimally Fix

1. **Form one hypothesis.** State it explicitly: "The error occurs because X, which means Y." Write it down (in your reasoning) before touching code.
2. **Make the smallest possible change** that would confirm or refute the hypothesis. One edit, one rerun. Do not bundle multiple fixes -- you will not know which one worked.
3. **If the hypothesis is wrong**, discard the change, form a new hypothesis, and repeat.

## Phase 4 -- Verify

1. **Rerun the affected script** via the pipeline runner. Confirm zero exit code and correct output.
2. **Check downstream effects.** If the fixed script produces outputs consumed by other scripts or by `paper/paper.typ`, rerun those too. Consult `.claude/skills/analysis/references/runbook.md` for the dependency chain.
3. **Compile the paper** if any result files in `analysis/output/results/` changed: `typst compile --root . paper/paper.typ`.
4. **Report** to the user: what broke, why, what you changed, and confirmation that the fix holds.

## 3-Fix Rule

If three consecutive fix attempts fail (three hypotheses tested and rejected), **stop.** Do not keep guessing. Report to the user:

- The exact error (full traceback).
- The three hypotheses you tested and why each was wrong.
- Your best remaining guess.

The user has domain knowledge you lack. Escalation is not failure -- it is efficiency.

## Red Flags

Stop and reassess if you observe any of these:

- **You are editing a file you have not read.** Read first, always.
- **You are changing more than 10 lines to fix a single bug.** Large fixes usually mean you are treating symptoms, not the cause. Step back.
- **The "fix" requires disabling a test or check.** That is not a fix; it is hiding the problem.
- **You are modifying raw data files.** Never. Create derived datasets via scripts.
- **Results changed but you did not update the paper.** Every result change must propagate to `paper/paper.typ`.

## Rationalization Table

Recognize and reject these common rationalizations for skipping the process:

| Tempting thought | Why it is wrong | What to do instead |
|---|---|---|
| "I'll just try this quick change" | Untested hypotheses compound. Three quick tries waste more time than one careful diagnosis. | Write the hypothesis first, then edit. |
| "It's probably just a typo" | Maybe. But confirm by reading the error, not by guessing which typo. | Phase 1 -- read the full traceback. |
| "This worked before, so the bug must be elsewhere" | Code that "worked before" can break when upstream data or packages change. | Check `git diff` and package versions. |
| "I'll fix the warning later" | Warnings become errors. Especially R warnings about coercion, factor levels, or dropped rows. | Fix warnings now. They are diagnostic information. |
| "The error message is misleading" | Occasionally true, but assume the message is accurate until proven otherwise. | Take the message literally first. Reinterpret only after literal reading fails. |
