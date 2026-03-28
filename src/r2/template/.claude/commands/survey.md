Orchestrate a literature survey on a topic. You are the orchestrator — do NOT
delegate the entire survey to a single agent. Run the discovery loop yourself,
launching focused subagents for each step, and report progress to the user
between steps.

Topic: $ARGUMENTS

Follow `.claude/skills/deep-research/SKILL.md` exactly, using this
orchestration pattern:

## Phase 0: Decompose (do this yourself, no agent needed)

Decompose the topic into 3-5 sub-questions. Show them to the user.

## Phase 1: Discovery loop (you run this loop)

For each iteration:

### Step 1: Search + Snowball + Triage
Launch a **researcher agent** with instructions to:
- Search local RAG (multiple query variations)
- Search external databases (broad, high-impact, recent, classical)
- Snowball from ALL HIGH-priority papers (forward + backward citations)
- Triage: build/update candidate list with priorities
- Write progress to `notes/lit/_survey_progress.md`
- Return the candidate list as structured output

When the agent returns, **show the user**:
```
📊 Iteration N — Search complete
  Candidate list: X papers (H high / M med / L low)
  Already in RAG: A | Need acquisition: B
```

### Step 2: Acquire
Launch a **source-acquirer agent** with the list of papers to acquire.
Instructions: use the 4-tier fallback chain (Sci-Hub → web search → S2 OA → flag).
Write progress to the log file. Return acquisition results.

When the agent returns, **show the user**:
```
📊 Iteration N — Acquisition complete
  Downloaded: D | Failed: F | Already indexed: I
  [list any failures with reasons]
```

### Step 3: Read
Launch a **researcher agent** with instructions to:
- Read every HIGH-priority paper via RAG (targeted queries)
- Record substantive notes per paper
- Note any NEW papers cited that aren't in the candidate list
- Return: reading notes + list of new leads

When the agent returns, **show the user**:
```
📊 Iteration N — Reading complete
  Papers read: R (full text via RAG)
  New leads found: K
```

### Step 4: Convergence check (you do this yourself)
If new HIGH-priority leads were found → add to candidate list, start next
iteration (back to Step 1, but narrower search focused on new leads).
If no new leads → exit loop, proceed to Phase 2.

Tell the user:
```
📊 Convergence: [CONTINUING — N new leads | CONVERGED — no new leads]
```

## Phase 2: Synthesize + Report
Launch a **researcher agent** with instructions to:
- Run `lit_deep_research` for combined synthesis
- Produce structured report (themes, gaps, connection to project)
- Save via `lit_save_report`
- Return the report

Show the user the final summary and report path.

## Rules
- NEVER launch one agent for the entire survey
- ALWAYS show progress between steps
- Use `model: opus` for all agents
- The candidate list accumulates across iterations — never discard
- Track which papers have been snowballed to avoid redundant API calls
