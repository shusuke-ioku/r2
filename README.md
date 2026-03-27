# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI-powered research environment for academic papers, built on [Claude Code](https://claude.ai/claude-code). You talk to Claude; r2 routes your request to the right specialized agent.

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

When you ask Claude to do something, r2 matches your request to a skill, which dispatches the right agent. 8 agents, 14 skills:

| Skill | Agent | What it does |
|-------|-------|-------------|
| `writing` | `manuscript-writer` | Academic prose, equations, tables, captions |
| `analysis` | `analyst-agent` | R pipeline, debugging, result alignment |
| `debugging` | `analyst-agent` | Autonomous error diagnosis and self-correction |
| `review` | `reviewer` | Stress-testing arguments and claims |
| `deep-research` | `researcher` | Multi-database literature surveys with snowballing |
| `reading` | `researcher` | Critical evaluation of individual papers |
| `source-acquisition` | `source-acquirer` | Download papers, add to Zotero, index into RAG |
| `formal-modeling` | `theorist` | Game-theoretic models, proofs, propositions |
| `slides` | `slides-writer` | Presentation slides synced with manuscript |
| `proofreading` | `proofreader` | First-time reader simulation for flow diagnosis |
| `verification` | *(cross-cutting)* | Prove correctness before reporting "done" |
| `parallel-dispatch` | *(orchestration)* | Run independent tasks concurrently |
| `portfolio-sync` | — | Sync title/abstract to a GitHub Pages site |
| `skill-creation` | — | Create, evaluate, and optimize custom skills |

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

**Local API** (Zotero desktop) — if Zotero is running with the MCP plugin, r2 can search your library, read PDF content, and retrieve your highlights and annotations directly. This gives Claude access to everything in your Zotero library without exporting anything.

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

## Simulated Peer Review

r2 simulates the full editorial review process at a top journal. An editor agent reads your paper, instantiates three independent reviewer subagents tailored to your paper's specific field, method, and case, then collects their reports and renders a consolidated decision.

**Three reviewers, three perspectives:**

| Reviewer | Focus |
|----------|-------|
| Literature Scholar | Novelty, theoretical contribution, literature engagement |
| Methodologist | Identification strategy, inference, data quality, robustness |
| Case/Domain Expert | Empirical accuracy, source quality, contextual validity |

Each reviewer operates independently (no cross-contamination), writes a structured report with severity-graded objections (fatal / serious / minor), and grounds criticisms in published work via RAG. The editor then synthesizes all three into a single report with NVI assessment (Novelty, Validity, Importance), calibrated publication prospects at named venues, and a ranked revision roadmap.

```
> /review-section              # review the full paper or a section
> "stress-test my argument"    # triggers automatically
> "what would reviewers say"   # triggers automatically
```

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
| 2026-03-27 | Drop copier; add `/update-r2` slash command; add humanizer skill; expand review skill with editor-report template and reviewer profiles; update agents and skills |
| 2026-03-22 | Initial release — 8 agents, 14 skills, 10 slash commands, RAG with three external databases, citation snowballing |

## License

MIT
