# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI-powered research environment for academic papers, built on [Claude Code](https://claude.ai/claude-code). Specialized agents handle writing, analysis, literature review, formal modeling, and peer-review simulation — you just talk to Claude.

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

To add r2 to an **existing project**, run `r2 init .` in the project directory. It only writes framework files — never touches your paper, data, or scripts.

## What You Get

**8 agents** that Claude dispatches automatically based on your request:

| Agent | Does |
|-------|------|
| `manuscript-writer` | Academic prose, equations, tables, captions |
| `analyst-agent` | R pipeline execution, debugging, results |
| `researcher` | Literature surveys, paper reading |
| `source-acquirer` | Download papers, add to Zotero, index into RAG |
| `reviewer` | Stress-testing arguments and claims |
| `theorist` | Game-theoretic models, proofs, propositions |
| `slides-writer` | Presentation slides synced with manuscript |
| `proofreader` | First-time reader simulation |

**RAG literature engine** — search your library and three external databases (Semantic Scholar, OpenAlex, Scopus), download papers, and do citation snowballing:

```bash
r2 rag index                              # index your PDFs
r2 rag search "democratic backsliding"     # search local library
r2 rag lit-search "exit voice" --focus top_journals  # search external DBs
r2 rag lit-download "10.1093/example"      # download + Zotero + index
```

## Updating

```bash
# Update the r2 CLI
pip install --upgrade "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

To update framework files (agents, skills, commands) in your project, run `/update-r2` inside Claude Code. Claude fetches the latest template, diffs each file against your local version, and merges changes — preserving your customizations.

If your project doesn't have `/update-r2` yet, tell Claude:

> Update the r2 framework files from https://github.com/shusuke-ioku/r2/tree/main/src/r2/template — preserve my local changes.

## API Keys

Only `ANTHROPIC_API_KEY` is required. Optional keys unlock external database search (Scopus, Semantic Scholar) and Zotero integration. See `.env.example` for the full list.

## License

MIT
