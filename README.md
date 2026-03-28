# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI-powered research environment for political science papers, built on [Claude Code](https://claude.ai/claude-code). You talk to Claude; r2 routes your request to the right specialized agent.

## Install

```bash
pip install "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

## Quick Start

```bash
r2 init my-paper/
cd my-paper/
cp .env.example .env   # add your ANTHROPIC_API_KEY
git init && git add -A && git commit -m "Initial scaffold"
claude                  # start Claude Code
```

To add r2 to an **existing project**, run `r2 init .` — it only writes framework files, never touches your paper, data, or scripts.

## Agents and Skills

When you ask Claude to do something, r2 matches your request to a skill, which dispatches the right agent. 11 agents, 17 skills:

| Skill | Agent | What it does |
|-------|-------|-------------|
| `writing` | `manuscript-writer` | Academic prose, equations, tables, captions |
| `analysis` | `analyst-agent` | R pipeline, debugging, result alignment |
| `debugging` | `analyst-agent` | Autonomous error diagnosis and self-correction |
| `review` | `reviewer` | Stress-testing arguments and claims |
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

Skills are not static instructions — they can be created, tested, and iteratively improved. The `skill-creation` skill handles the full lifecycle: draft a SKILL.md, generate realistic test prompts, run them with and without the skill in parallel, compare outputs in a browser-based viewer, grade against assertions, aggregate into benchmarks, and repeat until satisfied. An automated optimization loop rewrites skill descriptions for better dispatch accuracy. The Skills Engine CLI (`r2 skills`) adds semantic search, ranked dispatch recommendations, and usage tracking on top.

```bash
r2 skills dispatch "rewrite the theory section"   # which skill handles this?
r2 skills list                                      # all registered skills
r2 skills search "literature"                       # semantic search
```

## RAG Literature Engine

Search your library and three external databases (Semantic Scholar, OpenAlex, Scopus), download papers, and do citation snowballing:

```bash
r2 rag index                              # index your PDFs
r2 rag search "democratic backsliding"     # search local library
r2 rag lit-search "exit voice" --focus top_journals  # search external DBs
r2 rag lit-download "10.1093/example"      # download + Zotero + index
```

## Zotero Integration

r2 integrates with Zotero at two levels:

**Cloud API** (pyzotero) — when you download a paper with `r2 rag lit-download`, r2 automatically creates a Zotero item with full metadata (resolved via CrossRef) and attaches the PDF if obtainable. This means every paper you acquire through r2 appears in your Zotero library with correct bibliographic data. Set `RAG_ZOTERO_API_KEY` and `RAG_ZOTERO_USER_ID` in `.env` to enable.

**Local API** (Zotero desktop) — if Zotero desktop is running, r2 can search your library, read PDF content, and retrieve your highlights and annotations directly. This gives Claude access to everything in your Zotero library without exporting anything.

```bash
# Download a paper: PDF saved + Zotero item created + indexed into RAG
r2 rag lit-download "10.1093/example"

# Search your Zotero library (requires Zotero desktop running)
python .claude/scripts/zotero_cli.py search "democratic backsliding"

# Read PDF content from a Zotero item
python .claude/scripts/zotero_cli.py pdf-content ITEM_KEY

# Search your highlights and annotations
python .claude/scripts/zotero_cli.py search-annotations "key finding"
```

## Literature Surveys

The `deep-research` skill runs systematic literature surveys built around an iterative discovery loop:

1. **Search** your local Zotero library (full-text via RAG) and three external databases (Semantic Scholar, OpenAlex, Scopus) with varied queries
2. **Snowball** forward and backward citations from every high-priority paper found
3. **Triage** candidates by relevance, download and index the high-priority ones
4. **Read** acquired papers in full text — not abstracts
5. **Check convergence**: did reading surface new leads? If yes, loop back to step 1 with the new leads. If no, the frontier has closed — proceed to synthesis.

The loop typically runs 2-4 iterations before converging. The final report is written only after convergence, organized thematically with synthesis across sources — not paper-by-paper summaries.

Progress is visible throughout: the orchestrator runs the loop in the main conversation, launching focused subagents for each step and reporting the growing candidate list between steps.

```
> /survey "economic shocks and political extremism"
> "survey the literature on democratic backsliding"
> "what does the field say about civil society and authoritarianism"
```

## Obsidian Vault Integration

r2 scaffolds an [Obsidian](https://obsidian.md) vault at `notes/` for structured knowledge management. Three types of notes:

- **Paper notes** (`notes/papers/<citekey>.md`) — one atomic note per source with YAML frontmatter (citekey, authors, year, themes, relevance) and structured sections (arguments, findings, methods, critique). Created automatically when reading papers via the `reading` skill.
- **Concept notes** (`notes/concepts/<concept>.md`) — one note per theoretical idea, linking to the paper notes that develop it.
- **Thematic MOCs** (`notes/lit/`) — Maps of Content that organize paper notes by theme with `[[wiki-links]]`.

The `vault-search` skill (and `vault-searcher` agent) searches this vault using Obsidian's Local REST API when available, falling back to file-based search. Other skills — `writing`, `deep-research`, `review`, `formal-modeling` — consult the vault automatically before proceeding.

To enable API-based search, install the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) community plugin in your vault. File-based search works without it.

## Revision Dashboard

Reviews generate actionable todo items in `revision/todo.md`. The `task-manager` agent tracks progress: adding items from reviews, marking them done with results, evaluating what remains, and enforcing a gatekeeper principle — it pushes back when items are dismissed without addressing the underlying concern.

```
> /review-section                    # review → generates todos
> "what's left on the revision list" # triggers task-management
> "mark item 3 done"                # updates dashboard
```

## Simulated Peer Review

An editor agent dispatches three independent reviewer subagents — a literature scholar, a methodologist, and a case/domain expert — each tailored to the paper's specific field, method, and empirical context. Reviewers operate independently, write severity-graded reports (fatal / serious / minor), and ground criticisms in published work via RAG. The editor synthesizes all three into a consolidated report with NVI assessment (Novelty, Validity, Importance), calibrated publication prospects at named venues, and a ranked revision roadmap.

```
> /review-section              # review the full paper or a section
> "stress-test my argument"    # triggers automatically
> "what would reviewers say"   # triggers automatically
```

## Harness Engineering

r2 treats the Claude Code harness — CLAUDE.md, rules, skills, hooks, and settings — as infrastructure to be engineered, not just configuration to be written. The framework implements several principles:

**Skill dispatch as a mandatory routing layer.** Every user request is matched against the skill table before any work begins. A rationalization-prevention table blocks common excuses for skipping dispatch ("this is just a simple question," "the skill is overkill"). Skills are triggered at even 1% relevance.

**Hooks as automated guardrails.** Shell hooks enforce invariants that the model would otherwise forget under context pressure: auto-compiling Typst after every edit, syntax-checking R scripts, blocking edits to auto-generated files (ref.bib, analysis outputs), verifying the paper compiles before session end, and injecting critical reminders after context compaction.

**Context budget management.** Always-loaded context (CLAUDE.md + rules) is kept lean. Reference-heavy docs (RAG usage, skills engine) are candidates for on-demand loading via skills when context budget tightens. The `PostCompact` hook re-injects critical rules that would otherwise be lost during automatic conversation compression.

**Build to delete.** Every skill and hook encodes an assumption about what the model can't do reliably on its own. As models improve, these assumptions should be periodically stress-tested and retired when they no longer hold.

## Updating

Run `/update-r2` inside Claude Code. Claude fetches the latest template from GitHub, diffs each file, and merges changes — preserving your customizations.

If your project doesn't have `/update-r2` yet, tell Claude:

> Update the r2 framework files from https://github.com/shusuke-ioku/r2/tree/main/src/r2/template — preserve my local changes.

To update the r2 CLI itself:

```bash
pip install --upgrade "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

## API Keys

Only `ANTHROPIC_API_KEY` is required. Optional keys unlock external database search (Scopus, Semantic Scholar) and Zotero integration. See `.env.example` for the full list.

## Update History

| Date | Change |
|------|--------|
| 2026-03-28 | Add Obsidian vault integration (`notes/`), revision dashboard (`revision/`), 3 new agents (reader, vault-searcher, task-manager), 3 new skills (vault-search, task-management, humanizer), hooks (stop verify, R syntax check, session init), settings.local.json template; extract skill-dispatch to standalone rule; migrate all paths from `paper/notes/` to `notes/` |
| 2026-03-27 | Drop copier; add `/update-r2` slash command; add humanizer skill; expand review skill with editor-report template and reviewer profiles; update agents and skills |
| 2026-03-22 | Initial release — 8 agents, 14 skills, 10 slash commands, RAG with three external databases, citation snowballing |

## License

MIT
