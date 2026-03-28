# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

A harness-engineered research environment for political science papers, built on [Claude Code](https://claude.ai/claude-code). 11 specialized agents, 17 skills, automated guardrails via hooks, and a mandatory skill-dispatch layer that routes every request before the model touches anything.

Literature surveys that actually iterate: search four databases, snowball citations, download via Sci-Hub, read full text, discover new leads, loop until convergence. Simulated peer review calibrated against real APSR/AJPS acceptance patterns. A revision dashboard that pushes back when you try to dismiss valid reviewer concerns. An Obsidian vault that builds itself as you read.

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

## How It Works

### Agents and Skills

When you ask Claude to do something, r2 matches your request to a skill, which dispatches the right agent. 11 agents, 17 skills:

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

### RAG Literature Engine

Search your library and three external databases (Semantic Scholar, OpenAlex, Scopus), download papers, and do citation snowballing:

```bash
r2 rag index                              # index your PDFs
r2 rag search "democratic backsliding"     # search local library
r2 rag lit-search "exit voice" --focus top_journals  # search external DBs
r2 rag lit-download "10.1093/example"      # download + Zotero + index
```

### Zotero Integration

r2 integrates with Zotero at two levels:

**Cloud API** (pyzotero) — when you download a paper with `r2 rag lit-download`, r2 automatically creates a Zotero item with full metadata (resolved via CrossRef) and attaches the PDF. Every paper you acquire appears in your Zotero library with correct bibliographic data. Set `RAG_ZOTERO_API_KEY` and `RAG_ZOTERO_USER_ID` in `.env`.

**Local API** (Zotero desktop) — if Zotero desktop is running, r2 can search your library, read PDF content, and retrieve your highlights and annotations directly.

```bash
r2 rag lit-download "10.1093/example"                          # download + Zotero + index
python .claude/scripts/zotero_cli.py search "backsliding"      # search Zotero
python .claude/scripts/zotero_cli.py pdf-content ITEM_KEY      # read PDF text
python .claude/scripts/zotero_cli.py search-annotations "key"  # search highlights
```

### Obsidian Vault

r2 scaffolds an [Obsidian](https://obsidian.md) vault at `notes/` for structured knowledge management:

- **Paper notes** (`notes/papers/<citekey>.md`) — one per source, with YAML frontmatter and structured sections. Created automatically when reading papers.
- **Concept notes** (`notes/concepts/<concept>.md`) — one per theoretical idea, linking to paper notes.
- **Thematic MOCs** (`notes/lit/`) — Maps of Content organizing paper notes by theme with `[[wiki-links]]`.

Skills consult the vault automatically before writing prose, reviewing, or building theory. To enable API-based search, install the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin. File-based search works without it.

### Harness Engineering

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
