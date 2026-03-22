---
name: parallel-dispatch
description: >
  Use when 2+ independent tasks can run concurrently without shared state
  or sequential dependencies. Trigger whenever the user requests multiple
  things in a single message and the tasks don't depend on each other --
  e.g., "run robustness checks 40 and 47", "search for papers on X and Y",
  "rewrite section 3 and compile the paper", "download these 3 papers and
  run the analysis". Also trigger when you identify parallelizable subtasks
  within a larger request, even if the user didn't explicitly ask for
  concurrency. If two things CAN run at the same time, they SHOULD.
---

# Parallel Dispatch

Run independent tasks concurrently. Faster results, same correctness.

## When to Use

Dispatch in parallel when you have 2+ tasks that satisfy ALL of these:

1. **No data dependency**: Task B does not need Task A's output.
2. **No file conflicts**: Tasks do not write to the same file.
3. **No ordering requirement**: Results are valid regardless of completion order.

### Common project patterns that qualify

- Running multiple R robustness scripts (`40_robustness.R` + `47_income1931_replications.R`)
- Literature search across sources (`rag_search` + `lit_search` on the same topic)
- Downloading multiple papers (`lit_download` for different DOIs)
- Reviewing one paper section while compiling another (`typst compile` + prose review)
- Running analysis while searching literature on a related question
- Multiple `rag_deep_query` calls for different sub-questions in a literature survey
- Forward and backward citation tracking on different seed papers (`lit_citations` + `lit_references`)

## When NOT to Use

Do not parallelize tasks that have dependencies. Sequential execution is correct when:

- **Output feeds input**: Run script, then update paper with results. The paper edit needs the script's output.
- **Shared file writes**: Two tasks both modify `paper/paper.typ`. One will overwrite the other.
- **Conditional logic**: "Run this check; if it fails, try the alternative." Task B depends on Task A's outcome.
- **Cumulative state**: Building a dataset incrementally where each step appends to the last.

When in doubt, run sequentially. Wrong results from a race condition cost more time than the parallelism saves.

## Agent Prompt Structure

Each dispatched agent gets a self-contained prompt with four components:

### 1. Scope
One task, one domain. An agent that runs an R script should not also edit the manuscript. An agent that searches literature should not also rewrite prose.

### 2. Goal
State the concrete deliverable. Not "look into robustness" but "run `Rscript analysis/scripts/40_robustness.R` and report whether it succeeds, plus key coefficient estimates."

### 3. Constraints
Specify what the agent should NOT touch. This prevents conflicts between concurrent agents.

- "Do not modify any files outside `analysis/output/`."
- "Read `paper/paper.typ` but do not edit it."
- "Save results to `analysis/output/results/40_robustness.md` only."

### 4. Output format
Tell the agent what to return so you can integrate results afterward.

- "Report: script exit status, runtime, key coefficients (name, estimate, SE, p-value), any warnings."
- "Return: list of relevant papers with citekey, title, and one-sentence relevance summary."

### Example prompt for a dispatched agent

```
Run the robustness analysis script.

Scope: Execute analysis/scripts/40_robustness.R
Goal: Run the script to completion, self-debug if it fails, and report results.
Constraints:
  - Do not modify paper/paper.typ
  - Do not modify any other R script
  - If the script fails, fix only 40_robustness.R and rerun
Output: Report exit status, key coefficients (estimate, SE, significance),
  and any changes from previous results in analysis/output/results/.
```

## Integration After Completion

After all dispatched agents return, the coordinating agent must:

1. **Collect results**: Read each agent's output.
2. **Check for conflicts**: Did any agent unexpectedly modify a shared resource? If so, resolve manually.
3. **Synthesize**: Combine findings into a coherent response. If agents were searching literature from different angles, merge and deduplicate. If agents ran different scripts, compare results for consistency.
4. **Proceed with dependent work**: Now that parallel tasks are done, execute any sequential follow-ups (e.g., update the paper with the combined results).

## Common Parallel Patterns

### Pattern A: Multi-script robustness check

User asks to run several robustness or replication scripts.

```
Agent 1: Rscript analysis/scripts/40_robustness.R
Agent 2: Rscript analysis/scripts/47_income1931_replications.R
--- wait for both ---
Coordinator: Compare results, check for sign flips or significance changes,
  update paper if needed (sequential).
```

### Pattern B: Parallel literature acquisition

User asks to survey a topic or download multiple papers.

```
Agent 1: rag_search("economic shocks radical mobilization")
Agent 2: lit_search("trade shocks far-right voting", focus="broad")
Agent 3: lit_search("peripheral regions extremism", focus="recent")
--- wait for all ---
Coordinator: Deduplicate, rank by relevance, identify papers to download,
  then batch-download via lit_download_batch (sequential).
```

### Pattern C: Write + compile cycle

User asks to revise a section and also check that the paper compiles.

```
Agent 1: Revise the literature review in paper/paper.typ (writing skill)
Agent 2: typst compile --root . paper/paper.typ to check current build status
--- wait for both ---
Coordinator: Apply the revision, recompile to verify no Typst errors
  (sequential, since Agent 1's edits need a fresh compile).
```

Note: In Pattern C, the compile agent checks the CURRENT state while the writing skill drafts changes. The final compile must happen after the revision is applied -- that step is sequential.

### Pattern D: Analysis + literature in parallel

User asks a question that requires both empirical evidence and literature context.

```
Agent 1: Run analysis/scripts/30_main_results.R, report results
Agent 2: rag_deep_query("measurement strategies for key independent variable")
--- wait for both ---
Coordinator: Synthesize empirical findings with literature context,
  draft or update the relevant paper section (sequential).
```

## Principles

**Maximize concurrency, minimize coordination.** The value of parallel dispatch comes from wall-clock time savings. Every coordination step (merging, conflict resolution) erodes that gain. Design agent scopes to be as independent as possible so integration is trivial.

**Fail independently.** If one agent fails (script error, search returns nothing), the others should still produce useful results. Do not couple agents such that one failure cascades.

**Scope narrowly.** A focused agent with a clear goal produces better results than a broad agent juggling multiple concerns. When in doubt, split into more agents with narrower scope rather than fewer agents with broader scope.
