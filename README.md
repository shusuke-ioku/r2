# r2 v0.2.0

*Not the droid you're looking for — but it will get your paper through R&R.*

A **harness-engineered** research environment for political science papers, built on [Claude Code](https://claude.ai/claude-code). **11 agents**, **17 skills**, **automated guardrails** via hooks, and a **mandatory skill-dispatch layer** that routes every request before the model touches anything.

- **Iterative literature surveys with RAG and Zotero** — a local **RAG vector store** over your PDF library, combined with three external databases (Semantic Scholar, OpenAlex, Scopus) and **two-level Zotero integration** (cloud API for metadata + local API for annotations). Surveys **snowball citations**, acquire PDFs automatically, read full text, discover new leads, and loop until convergence.
- **Empirically calibrated peer review** — three independent reviewer agents scored against a blind training set of top-generalist vs. field-journal publications to correct systematic biases
- **Gatekeeper revision management** — reviews auto-generate todo items; the task manager **pushes back** when you dismiss concerns that a real reviewer would raise again
- **Self-building Obsidian vault** — every paper you read becomes a structured, wiki-linked note that future writing and review skills consult automatically

## Install

```bash
pip install "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
r2 init my-paper/ && cd my-paper/
cp .env.example .env   # add ANTHROPIC_API_KEY
claude                  # start Claude Code
```

Add r2 to an **existing project**: `r2 init .` — writes framework files only, never touches your paper or data.

## Updating

Run `/update-r2` inside Claude Code. Claude fetches the latest template, diffs each file, and merges changes — preserving your customizations.

To update the CLI itself:

```bash
pip install --upgrade "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

## API Keys

Only `ANTHROPIC_API_KEY` is required. Optional keys unlock external database search (Scopus, Semantic Scholar) and Zotero integration. See `.env.example` for the full list.

---

## Iterative Literature Surveys with RAG and Zotero

r2 builds a **local RAG vector store** (ChromaDB + sentence-transformers) over your PDF library. Every paper you download or already have in Zotero gets chunked, embedded, and indexed for full-text semantic search.

On top of the local index, three external databases — **Semantic Scholar**, **OpenAlex**, and **Scopus** — provide abstract-level search across the full academic literature. The `deep-research` skill combines both into an iterative discovery loop:

1. **Search** local RAG (multiple query variations) + external databases (broad, high-impact, recent, classical)
2. **Snowball** forward and backward citations from every high-priority paper
3. **Triage** candidates by relevance into a running candidate list
4. **Acquire** high-priority papers: download PDF, create Zotero item with full CrossRef metadata, index into RAG — in one call
5. **Read** acquired papers in full text via RAG, not just abstracts
6. **Check convergence**: did reading surface new leads? If yes, loop back to step 1. If no, proceed to synthesis.

The loop typically runs 2–4 iterations. The final report is written only after convergence, organized thematically — not paper-by-paper.

**Zotero integration** operates at two levels. The **cloud API** (pyzotero) creates Zotero items with full metadata and PDF attachments whenever you download a paper — every acquisition flows into your bibliography automatically via Better BibTeX auto-export. The **local API** (Zotero desktop) gives Claude direct access to your library, PDF content, highlights, and annotations without exporting anything.

```bash
r2 rag index                              # index your PDFs into vector store
r2 rag search "democratic backsliding"     # semantic search over local library
r2 rag lit-search "exit voice" --focus top_journals  # search external DBs
r2 rag lit-download "10.1093/example"      # download + Zotero + index in one call
r2 rag lit-citations PAPER_ID             # forward citation snowballing
r2 rag lit-references PAPER_ID            # backward citation snowballing
```

## Empirically Calibrated Peer Review

An editor agent dispatches three independent reviewer subagents — a **literature scholar**, a **methodologist**, and a **case/domain expert** — each instantiated with expertise tailored to the paper's specific field, method, and empirical context. Reviewers operate independently, write severity-graded reports (fatal / serious / minor), and ground every objection in published work via RAG.

The review framework uses the **NVI scoring system** (Novelty, Validity, Importance) adapted from real editorial practice. Each dimension is scored 1–5; the composite informs venue-tier classification and R&R probability estimates.

The scoring has been **empirically calibrated** against a blind training set of published papers from top-generalist journals (APSR, AJPS) and field journals. This calibration corrects five systematic biases that the uncalibrated model exhibits: formal theory undervaluation, top-field hedging (defaulting to "good field journal" when uncertain), non-novelty over-application, probability compression in the 0.15–0.35 range, and NVI scale compression toward 3–4.

```
> /review-section              # full paper or a specific section
> "stress-test my argument"    # triggers automatically
> "what would reviewers say"   # triggers automatically
```

## Gatekeeper Revision Management

Every review automatically generates actionable todo items in `revision/todo.md`, prioritized by severity (CRITICAL / IMPORTANT / MINOR) and tagged with effort estimates. The `task-manager` agent enforces a **gatekeeper principle**: before marking any item "done" or "not needed," it re-reads the original reviewer concern and verifies the resolution actually addresses it.

If you dismiss an item but the reviewer's point has genuine merit, the task manager says so directly — "The reviewer's point stands because X. Dismissing it risks Y at review." It only marks "not needed" when it can articulate why the concern does not apply. This protects the paper from a real reviewer who will raise the same objection.

The dashboard tracks progress with a visual progress bar, lane counts by priority, and category groupings (Identification, Robustness, Measurement, Framing, Citation). Completed items are archived in `revision/done.md` with full result records.

```
> "what's left on the revision list"   # evaluate progress
> "mark item 3 done"                  # moves to done.md with result
> "add a robustness task"             # manual additions
```

## Self-Building Obsidian Vault

r2 scaffolds an [Obsidian](https://obsidian.md) vault at `notes/` with three types of structured notes:

- **Paper notes** (`notes/papers/<citekey>.md`) — one atomic note per source with YAML frontmatter (citekey, authors, year, themes, relevance) and structured sections (key arguments, findings, methods, relevance to this project, borrowable elements, critique). Created automatically by the `reading` skill.
- **Concept notes** (`notes/concepts/<concept>.md`) — one per theoretical idea, linking to the paper notes that develop it. Created when a source introduces a concept not yet in the vault.
- **Thematic MOCs** (`notes/lit/`) — Maps of Content that organize paper notes by theme using `[[wiki-links]]`. Updated automatically as new papers are read.

The `vault-search` skill searches this vault using **Obsidian's Local REST API** when available (full-text search, Dataview queries, tag lookups) or **file-based search** as fallback (frontmatter property queries, backlink traversal, YAML parsing). Other skills — `writing`, `deep-research`, `review`, `formal-modeling` — consult the vault automatically before proceeding.

To enable API-based search, install the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) community plugin. File-based search works without it.

## Agents and Skills

When you ask Claude to do something, r2 matches your request to a skill, which dispatches the right agent:

| Skill | Agent | What it does |
|-------|-------|-------------|
| `writing` | `manuscript-writer` | Academic prose, equations, tables, captions |
| `analysis` | `analyst-agent` | R pipeline, debugging, result alignment |
| `debugging` | `analyst-agent` | Autonomous error diagnosis and self-correction |
| `review` | `reviewer` | Simulated peer review with three independent reviewers |
| `deep-research` | `researcher` | Multi-database literature surveys with snowballing |
| `reading` | `reader` | Critical evaluation of individual papers + vault notes |
| `source-acquisition` | `source-acquirer` | Download papers, add to Zotero, index into RAG |
| `formal-modeling` | `theorist` | Game-theoretic models, proofs, propositions |
| `slides` | `slides-writer` | Presentation slides synced with manuscript |
| `proofreading` | `proofreader` | First-time reader simulation for flow diagnosis |
| `vault-search` | `vault-searcher` | Search Obsidian vault for literature context |
| `task-management` | `task-manager` | Revision dashboard: add/done/evaluate tasks |
| `verification` | *(cross-cutting)* | Prove correctness before reporting "done" |
| `parallel-dispatch` | *(orchestration)* | Run independent tasks concurrently |
| `portfolio-sync` | — | Sync title/abstract to a GitHub Pages site |
| `skill-creation` | — | Create, evaluate, and optimize custom skills |
| `humanizer` | — | Remove AI-writing tells from prose |

Skills can be created, tested, and iteratively improved. The `skill-creation` skill handles the full lifecycle: draft a SKILL.md, generate test prompts, run them with and without the skill, compare outputs, grade against assertions, and repeat. The Skills Engine CLI (`r2 skills`) adds semantic search, ranked dispatch, and usage tracking.

```bash
r2 skills dispatch "rewrite the theory section"   # which skill handles this?
r2 skills list                                      # all registered skills
r2 skills search "literature"                       # semantic search
```

## Harness Engineering

r2 treats the Claude Code harness — CLAUDE.md, rules, skills, hooks, and settings — as infrastructure to be engineered, not just configuration to be written.

**Skill dispatch as mandatory routing.** Every request is matched against the skill table before any work begins. A rationalization-prevention table blocks common excuses for skipping dispatch. Skills trigger at even 1% relevance.

**Hooks as automated guardrails.** Shell hooks enforce invariants the model forgets under context pressure: auto-compiling Typst after edits, syntax-checking R scripts, blocking edits to auto-generated files, verifying compilation before session end, and re-injecting critical rules after context compaction.

**Context budget management.** Always-loaded context is kept lean. Reference-heavy docs are candidates for on-demand loading via skills. The `PostCompact` hook re-injects critical rules lost during conversation compression.

**Build to delete.** Every skill and hook encodes an assumption about what the model can't do reliably. As models improve, stress-test those assumptions and retire what no longer holds.

## Update History

| Date | Change |
|------|--------|
| 2026-03-28 | v0.2.0 — Obsidian vault, revision dashboard, 3 new agents, hooks, harness engineering; migrate `paper/notes/` → `notes/` |
| 2026-03-27 | v0.1.0 — Drop copier; `/update-r2`; humanizer; expanded review with editor reports |
| 2026-03-22 | Initial release — 8 agents, 14 skills, RAG with three external databases |

## License

MIT
