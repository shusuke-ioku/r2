---
name: deep-research
description: >
  Comprehensive literature survey combining local Zotero RAG with external
  paper databases (Semantic Scholar, OpenAlex, Scopus). Trigger aggressively:
  activate whenever the user asks to survey a topic, explore a literature,
  find papers on a theme, map the field, do a deep dive, review the state
  of the art, search for related work, or comprehensively research any
  scholarly question. Trigger on phrases like "what does the literature say
  about X," "find papers on Y," "survey the field of Z," "deep dive into X,"
  "what's the state of the art on X," "map the literature on X," "research
  X for me," "who's working on X," or "I need to understand the literature
  on X." Even "look into X" about a scholarly topic should trigger this skill.
  If the user wants to read ONE specific paper, use the reading skill instead.
  This skill is for BREADTH -- surveying many sources on a topic.
---

# Deep Researcher

## Why This Skill Exists

The user needs to survey literatures — not read one paper, but map a field.
This means combining what is already in the local Zotero library (full-text
via RAG) with external databases (abstracts via Semantic Scholar, OpenAlex,
Scopus) to build a comprehensive picture. The output is a structured report
that synthesizes findings based on **full-text reading**, not abstracts.

A real literature survey is iterative: you read a paper, discover new
citations in it, chase those, read those, discover more leads, and repeat
until the frontier stops expanding. This skill enforces that iterative
loop — search, acquire, read, discover new leads, repeat — and only writes
the report after the loop converges.

## Workflow

The key principle: **read before you write.** The report must be based on
full-text reading, not abstracts. The core of the workflow is an iterative
loop — search, acquire, read, discover new leads from reading, repeat —
that runs until convergence. The report is written only after the loop
terminates.

```
Phase 0: Decompose
        ↓
   ┌──────────────────────────────┐
   │  Phase 1: DISCOVERY LOOP    │
   │                              │
   │  Search (local + external)   │
   │        ↓                     │
   │  Snowball from key papers    │
   │        ↓                     │
   │  Triage → candidate list     │
   │        ↓                     │
   │  Acquire & index HIGH papers │
   │        ↓                     │
   │  Read acquired papers        │
   │        ↓                     │
   │  New leads found in reading? │
   │    YES → back to Search      │
   │    NO  → exit loop           │
   └──────────────────────────────┘
        ↓
Phase 2: Synthesize & report
```

### Phase 0: Decompose the research question

Before searching, decompose the user's question into its components:

- **Core question**: What exactly are we trying to understand?
- **Sub-questions**: Break into 3-5 atomic sub-questions that together cover
  the topic. Different angles, different keywords, different literatures.
- **Scope**: What disciplines? What time period? Theoretical vs. empirical?
- **Connection to project**: How does this relate to the user's paper?
  Read CLAUDE.md and the paper's abstract for topic context.

State the decomposition explicitly to the user before proceeding.

### Phase 1: Discovery loop (iterate until convergence)

This phase is a **loop**. Each iteration has five steps: search, snowball,
triage, acquire, read. The loop terminates when reading no longer surfaces
new HIGH-priority papers that aren't already in the candidate list.

Maintain a running **candidate list** across iterations (see §1.3 for
format). Papers accumulate across iterations; never discard earlier finds.

#### Iteration 1: Seed search

The first iteration casts a wide net to build the initial candidate pool.

**1.1 Search local RAG**

Start with what we already have. Run multiple searches against the local
Zotero index:

1. **`rag_search`** with 2-3 query variations (different keywords, angles)
2. **`rag_deep_query`** with the sub-questions for systematic retrieval
3. Note which citekeys appear repeatedly — these are the core local sources

Record what the local library covers well and where it has gaps.

**1.2 Search external databases**

Use `lit_search` with multiple strategies:

1. **Broad sweep**: `focus="broad"` with the main query
2. **High-impact**: `focus="top_journals"` or `min_citations` filter
3. **Recent developments**: `focus="recent"` or `year="2020-"`
4. **Classical foundations**: `focus="classical"` for seminal papers
5. **Variant queries**: Rephrase using different terminology

For each sub-question, run at least one targeted `lit_search`.

**1.3 Snowball from ALL HIGH-priority papers**

For **every** HIGH-priority paper in the candidate list, run citation
tracking in both directions:

- **`lit_citations`** (forward): Who cites this paper?
- **`lit_references`** (backward): What does this paper cite?

Do NOT limit snowballing to a subset. Every HIGH-priority paper's citation
network may contain relevant work that keyword searches missed. In
subsequent iterations, snowball from newly added HIGH-priority papers
(skip papers already snowballed in a prior iteration).

**1.4 Triage: update the candidate list**

After searching and snowballing, compile / update the **candidate list**.
For each paper, record:

| Field | Description |
|-------|-------------|
| Title | Full title |
| Authors | First author et al. |
| Year | Publication year |
| DOI | If known (look up via Semantic Scholar if not) |
| Source | How found (local RAG / lit-search / snowball / cited-in:X) |
| Status | `indexed` / `in-zotero` / `external` / `failed` / `read` |
| Priority | `HIGH` / `MEDIUM` / `LOW` based on relevance |
| Notes | Brief note on what the paper contributes |

**1.5 Acquire & index HIGH-priority papers**

Download and index all HIGH-priority papers not yet in RAG. Ask the user
before downloading MEDIUM/LOW papers if the list exceeds 5.

Use the **source-acquisition skill** (or delegate to the **source-acquirer
agent**) which follows a **4-tier fallback chain**:

1. **Sci-Hub** (via `lit-download`) — 3 internal strategies
2. **Web search** for open-access PDF (NBER, SSRN, author pages, repos)
3. **Semantic Scholar** open-access URL
4. **Flag for manual acquisition** (only after tiers 1-3 all fail)

See `source-acquisition/SKILL.md` for full details on each tier.

**Every acquired paper MUST be added to Zotero** so it automatically appears
in `ref.bib` via BBT auto-export. Non-negotiable — regardless of which
tier succeeded.

**Quick reference:**

```bash
# Find DOI
r2 rag lit-search "PAPER TITLE" --focus broad -n 5

# Tier 1: Sci-Hub
r2 rag lit-download "10.xxxx/yyyy" --type doi --title "Paper Title"

# Tier 1 batch (3+ papers):
r2 rag lit-download-batch \
  '[{"id": "10.xxxx/yyyy", "title": "Paper A"}]' --auto-index

# Tier 2 (if Sci-Hub fails): Web search for open-access PDF
# Use WebSearch: "PAPER TITLE" filetype:pdf
# Then curl/WebFetch to download, then add to Zotero + index

# Verify: Check output for OK, Zotero: added, Indexed
```

**Do NOT mark a paper as `failed` until all 4 tiers have been tried.**
Do NOT proceed to reading until all HIGH-priority papers from this
iteration are either acquired or flagged.

**1.6 Read acquired papers**

For every HIGH-priority paper (pre-existing or newly acquired), do a
targeted full-text read:

```bash
r2 rag query "TARGETED QUESTION" --citekey dir__FILENAME
```

Use query variations tailored to what each paper contributes. Record
substantive notes: arguments, evidence, mechanisms, formal structure,
key findings. Mark status as `read` in the candidate list.

**Critically: while reading, note any papers cited or referenced that
are not yet in the candidate list.** These are the new leads that drive
the next iteration.

**1.7 Convergence check**

After reading, ask: **Did reading surface new HIGH-priority papers not
already in the candidate list?**

- **YES** → Add them to the candidate list. Start a new iteration:
  snowball from the newly read papers (§1.3), search for the new leads
  (§1.2 if needed), triage (§1.4), acquire (§1.5), read (§1.6).
- **NO** → The loop has converged. Proceed to Phase 2.

**Convergence criteria:**
- No new HIGH-priority papers discovered in the latest reading pass
- OR the candidate list has been stable for 2 consecutive iterations
- OR the user signals to stop (time/cost constraint)

**Iteration budget:** Expect 2-4 iterations for a typical survey. If the
loop has not converged after 5 iterations, report the current state to the
user and ask whether to continue or proceed to synthesis.

#### Subsequent iterations (2, 3, ...)

Each subsequent iteration is narrower than the first:

- **Search**: Only for specific papers or topics identified during reading
  (not the broad sweep of iteration 1)
- **Snowball**: From ALL newly added HIGH-priority papers not yet snowballed
  (track which papers have been snowballed to avoid redundant calls)
- **Triage**: Add new finds to the existing candidate list
- **Acquire & Read**: Same process as iteration 1
- **Convergence check**: Same criterion

### Phase 2: Synthesize and report (write from full-text knowledge)

This phase runs only after the discovery loop has converged. By now,
every HIGH-priority paper has been acquired, indexed, and read.

#### 2.1 Synthesize with deep research

Use **`lit_deep_research`** with the main query to get a combined local +
external synthesis prompt. This supplements (not replaces) the full-text
reading done during the discovery loop.

If the topic is broad enough to warrant it, run `lit_deep_research` on
2-3 of the sub-questions separately.

#### 2.2 Produce the structured report

Read `references/report-template.md` and follow its structure exactly.
The report must include ALL of the following sections:

1. **Research question & scope**
2. **Key themes** (organized thematically, not by paper)
3. **Synthesis** (what the literature collectively says, where it agrees/
   disagrees, what the mechanisms are)
4. **Gaps & opportunities** (what remains unstudied or underexplored)
5. **Connection to this project** (how findings inform the user's paper)
6. **Acquisition log** (what was downloaded, what failed, what the user
   needs to acquire manually — include iteration count and convergence note)
7. **Full bibliography** (all sources cited in the report)

**Every claim in the report must be grounded in full-text reading or at
minimum an abstract read.** If you have not read a paper, do not cite it
in the synthesis — mention it only in the acquisition log as a candidate
the user may want to pursue.

#### 2.3 Write Obsidian notes

For each HIGH-priority paper that was read during the discovery loop:

1. **Create an atomic paper note** at `notes/papers/<citekey>.md` using the
   template in `notes/templates/paper.md`. Fill in YAML frontmatter and all
   body sections from your reading. Use `[[wiki-links]]` to reference other
   paper notes and concept notes.

2. **Create concept notes** at `notes/concepts/<concept>.md` for any
   theoretical concepts substantially developed across multiple papers.
   Use the template in `notes/templates/concept.md`.

3. **Update relevant thematic MOCs** in `notes/lit/` --- add one-line entries
   linking to the new paper notes.

#### 2.4 Save the synthesis report

Call **`lit_save_report`** to save the synthesis report to
`notes/lit/YYYY-MM-DD_slug.md`. This report should use `[[wiki-links]]`
to reference the atomic paper notes created in §2.3, making it a
navigable MOC rather than a standalone monolith.

## Citation Rules

- **Cite only what you have read:** At minimum read the abstract via RAG or external search before citing. Never cite from title alone.
- **Zotero only:** Use `.claude/scripts/zotero_add.py` or `lit_download` for missing references. Never edit `ref.bib` directly.
- **Never self-cite:** Never use the user's own paper as a source. The lit review surveys external literature only.

## Progress Reporting & Orchestration

### The problem with monolithic agents

Subagents run in a subprocess and only return their final result. If you
delegate the entire survey to one agent, the user sees nothing for 15+
minutes. This is unacceptable.

### Solution: the orchestrator runs the loop

**Never delegate the entire survey to a single agent.** The main
conversation (orchestrator) must run the discovery loop itself, launching
focused subagents for individual steps, and reporting progress to the user
between steps. See `.claude/commands/survey.md` for the exact pattern.

The orchestrator:
1. Does Phase 0 itself (decompose — no agent needed)
2. Launches a researcher agent for **search + snowball + triage**
3. **Reports candidate list to user**
4. Launches a source-acquirer agent for **acquisition**
5. **Reports download results to user**
6. Launches a researcher agent for **reading + lead discovery**
7. **Reports reading summary to user**
8. Checks convergence itself
9. **Reports convergence status to user**
10. Loops back to step 2 if not converged, or proceeds to Phase 2

Progress is naturally visible because the orchestrator lives in the main
conversation and speaks to the user between each subagent call.

### Progress format

Show the user this after each step:

```
📊 Iteration N — STEP_NAME complete
  Candidate list: X papers (H high / M med / L low)
  Acquired: A downloaded, F failed, P pending
  Read: R papers read (full text)
  New leads this iteration: K
```

### Subagent log file (secondary)

Each subagent should ALSO write progress to `notes/lit/_survey_progress.md`
(append-mode, with timestamps) for fine-grained tracking within long steps.
This is a backup — the primary progress channel is the orchestrator
reporting between steps.

Clean up the log file after the final report is saved.

## Principles

**Why iterative?** A linear search → report flow writes from abstracts.
Reading full text reveals citations, nuances, and connections that keyword
searches miss. Each reading pass surfaces new leads that expand the
frontier. The loop terminates naturally when reading stops producing new
HIGH-priority papers — that's convergence.

**Why multiple search passes?** A single query in one database misses papers
that use different terminology, sit in adjacent fields, or are too old/new
for the default search window. Systematic coverage requires varied queries
across multiple sources.

**Why local RAG first?** The local library contains papers the user already
knows are relevant. Full-text search over these (not just abstracts) provides
richer evidence. Starting here also reveals gaps that guide external search.

**Why snowball?** Citation networks capture intellectual lineage that keyword
searches miss. A paper on "economic voting" might be highly relevant to
"trade shocks and extremism" but share zero keywords.

**Why acquire before reporting?** The external search returns abstracts only.
A report based on abstracts is shallow. Acquiring and reading the full text
first produces a report grounded in actual substance, not summaries of
summaries.

**Why thematic organization?** Listing papers one by one is a bibliography,
not a survey. Organizing by theme reveals the structure of the field —
where literatures converge, where they talk past each other, and where this
project fits.

## Common Failure Modes

**Writing the report before reading the papers.** This is the #1 failure.
The report must be the LAST step, written after the discovery loop converges.
If you find yourself writing the report while papers are still unread, stop
and go back to the loop.

**Not iterating.** One pass of search → acquire → read is not enough.
Reading surfaces new leads. If you skip the convergence check and go
straight to reporting, you are leaving papers on the table.

**Stopping after one search.** One `lit_search` call is not a survey. Run
multiple queries with different keywords, focus modes, and sub-questions.
If your report cites fewer than 10 distinct sources, you did not search
enough.

**Listing without synthesizing.** "Paper A says X. Paper B says Y." is not
synthesis. Synthesis means identifying themes, tensions, and mechanisms
across papers. Group by theme, not by paper.

**Ignoring the local library.** External search is easy but shallow
(abstracts only). The local RAG has full text. Always check what's already
indexed before going external.

**Citing papers you haven't read.** If you have not read at least the
abstract via RAG or external search, do not cite it in the synthesis.
Mention it in the acquisition log as a candidate for future acquisition.

**Not reporting progress.** The user should always know which iteration
you are on, how many papers you have found/downloaded/read, and whether
the loop is converging. Write to the progress log file at every major
step — `notes/lit/_survey_progress.md`. A silent 15-minute agent
run with no visibility is a failure mode, not a feature.

**Forgetting to save.** Always call `lit_save_report` at the end.
