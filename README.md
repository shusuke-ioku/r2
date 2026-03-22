# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI-powered research environment for academic papers, built on [Claude Code](https://claude.ai/claude-code). Implements current best practices in agent engineering — multi-agent orchestration, skill-based dispatch, RAG-augmented retrieval, and autonomous debugging — and is actively maintained as the field advances.

Out of the box you get: literature search, paper downloads, semantic knowledge retrieval, multi-agent writing, formal modeling, and peer-review simulation.

## Install

```bash
pip install r2-research

# With all optional extras:
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
| `source-acquirer` | Download papers, add to Zotero, index into RAG |
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
| `RAG_ZOTERO_API_KEY` | No | Zotero bibliography integration |
| `RAG_ZOTERO_USER_ID` | No | Zotero bibliography integration |

r2 works with zero optional keys — you get local PDF indexing and embedding search. Features unlock as you add keys.

## Updating

```bash
# Update the Python package
pip install --upgrade r2-research

# Update framework files (skills, agents, commands, rules) in your project
r2 update
```

`r2 update` uses [Copier](https://copier.readthedocs.io/) to merge upstream changes with your local edits. It will never touch your content (analysis, paper, notes).

## Adding r2 to an Existing Project

If you already have a research project with paper, data, and analysis scripts, you can add r2 on top.

**Important:** Before proceeding, make a backup copy of your project folder (e.g., `cp -r my-project/ my-project-backup/`). The restructuring only renames and moves files — it never deletes — but a backup ensures you can always recover if anything goes wrong.

Open Claude Code in your project and paste this prompt:

> Prepare this project for r2. The r2 framework expects this layout:
>
> ```
> project-root/
> ├── paper/paper.typ (or paper.tex)   # manuscript
> ├── ref.bib                          # bibliography (project root)
> ├── analysis/scripts/                # R scripts (00_setup.R, 20_data.R, 30_*.R, etc.)
> ├── analysis/data/                   # datasets
> ├── analysis/output/results/         # generated result summaries
> ├── analysis/output/figures/         # generated plots
> ├── paper/notes/lit/                 # literature review notes
> └── .here                            # project root marker
> ```
>
> Audit the current project structure and make it r2-compatible:
>
> 1. **Manuscript**: If the main .typ/.tex file isn't named `paper.typ`/`paper.tex`, rename it to `paper.typ` (or `paper.tex`) so r2 agents can find it. Update any internal references (e.g., `#import` or `\input` paths). Do NOT delete the old file — rename it.
> 2. **Bibliography**: If `ref.bib` is inside `paper/`, move it to the project root. Update the bibliography path in the manuscript.
> 3. **Analysis**: If R scripts or data aren't under `analysis/`, move them. Create `analysis/output/results/` and `analysis/output/figures/` if they don't exist.
> 4. **Literature notes**: Create `paper/notes/lit/` if it doesn't exist.
> 5. **Root marker**: Create `.here` if it doesn't exist.
> 6. **Never delete** any data files, scripts, source documents, PDFs, or analysis outputs. Only rename and move.
>
> After restructuring, report what you changed. Then I'll run `r2 init . --defaults`.

After Claude restructures the project, run:

```bash
r2 init . --defaults
cp .env.example .env  # add your API keys
```

`r2 init` only writes framework files (`.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/rules/`, `CLAUDE.md`, `.env.example`). It never touches your paper, data, or scripts.

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
