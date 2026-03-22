# r2

AI-driven research environment for academic papers — powered by [Claude Code](https://claude.ai/claude-code).

r2 gives you a complete research workflow out of the box: literature search, paper downloads, RAG-powered knowledge retrieval, multi-agent writing, formal modeling, and review — all orchestrated through Claude Code's skill and agent system.

## Install

```bash
pip install r2-research

# With all optional extras (Sci-Hub downloads, Cognee skills engine):
pip install r2-research[all]
```

## Quick Start

```bash
# Scaffold a new research project
r2 init my-paper/
cd my-paper/

# Configure API keys
cp .env.example .env
# Edit .env — only ANTHROPIC_API_KEY is required

# Initialize git (needed for r2 update to work later)
git init && git add -A && git commit -m "Initial scaffold"

# Start Claude Code in the project
claude
```

Your project now has the full r2 framework: 8 agents, 14 skills, 10 slash commands, and RAG infrastructure.

## What You Get

### Agents

| Agent | Does |
|-------|------|
| `manuscript-writer` | Dense academic prose, equations, tables, captions |
| `analyst-agent` | R pipeline execution, debugging, result verification |
| `researcher` | Literature surveys, paper reading, source acquisition |
| `source-acquirer` | Download papers via Sci-Hub, add to Zotero, index into RAG |
| `reviewer` | Skeptical stress-testing of arguments and claims |
| `theorist` | Formal game-theoretic models, proofs, propositions |
| `slides-writer` | Presentation slides synced with manuscript |
| `proofreader` | First-time reader simulation for flow diagnosis |

### RAG System

```bash
# Index your bibliography's PDFs
r2 rag index

# Semantic search over your literature
r2 rag search "democratic backsliding civil society"

# Search external databases (Semantic Scholar, OpenAlex, Scopus)
r2 rag lit-search "authoritarian resilience" --focus top_journals

# Download a paper, add to Zotero, and index in one command
r2 rag lit-download "10.1093/example" --type doi

# Deep research: local RAG + external search combined
r2 rag lit-deep-research "institutional decay mechanisms"
```

### Skills Engine

```bash
# See which skill matches a task
r2 skills dispatch "write the introduction"

# List all available skills
r2 skills list
```

## API Keys

| Key | Required | What it enables |
|-----|----------|-----------------|
| `ANTHROPIC_API_KEY` | Yes | Claude generation in RAG queries |
| `RAG_OPENALEX_EMAIL` | No | OpenAlex polite pool (higher rate limits) |
| `RAG_SCOPUS_API_KEY` | No | Scopus literature search |
| `RAG_S2_API_KEY` | No | Semantic Scholar higher rate limits |
| `RAG_SCIHUB_URL` | No | Paper downloads via Sci-Hub |
| `RAG_ZOTERO_API_KEY` | No | Zotero bibliography integration |
| `RAG_ZOTERO_USER_ID` | No | Zotero bibliography integration |
| `OPENAI_API_KEY` | No | Skills engine semantic dispatch (Cognee) |

r2 works with zero optional keys — you get local PDF indexing and embedding search. Features unlock as you add keys.

## Updating

```bash
# Update the Python package
pip install --upgrade r2-research

# Update framework files (skills, agents, commands, rules) in your project
r2 update
```

`r2 update` uses [Copier](https://copier.readthedocs.io/) to merge upstream changes with your local edits. It will never touch your content (analysis, paper, notes).

## Project Structure After `r2 init`

```
my-paper/
├── CLAUDE.md              # Project rules and skill dispatch
├── .env.example           # API key template
├── .here                  # Project root marker
├── .copier-answers.yml    # Template config (for r2 update)
└── .claude/
    ├── agents/            # 8 agent definitions
    ├── skills/            # 14 skill definitions
    ├── commands/          # 10 slash commands
    ├── rules/             # Project rules
    ├── lessons.md         # Learned patterns (grows over time)
    └── directory-structure.md
```

## License

MIT
