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
