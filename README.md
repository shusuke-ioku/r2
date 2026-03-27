# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI-powered research environment for academic papers, built on [Claude Code](https://claude.ai/claude-code). Uses multi-agent orchestration, skill-based task routing, RAG retrieval, and autonomous debugging — following the latest agentic AI design patterns and actively maintained as they evolve.

Out of the box you get: literature search, paper downloads, semantic knowledge retrieval, multi-agent writing, formal modeling, and peer-review simulation.

## Install

```bash
pip install "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
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

Full-stack literature engine: index PDFs locally, search three external databases simultaneously, download papers in one command, and combine everything for deep research queries. Retrieval modes include standard semantic search, Self-RAG (LLM-graded relevance filtering), and DeepRAG (automatic query decomposition into sub-questions). Forward and backward citation snowballing lets you iteratively expand from seed papers until convergence.

```bash
# Index your bibliography's PDFs into a local vector store
r2 rag index

# Semantic search over your indexed library
r2 rag search "democratic backsliding civil society"

# Self-RAG: over-retrieve, then LLM grades each chunk for relevance
r2 rag self-query "causes of institutional decay"

# DeepRAG: decompose a complex question into sub-queries automatically
r2 rag deep-query "how do economic shocks affect political mobilization"

# Search 3 external databases at once (Semantic Scholar, OpenAlex, Scopus)
r2 rag lit-search "authoritarian resilience" --focus top_journals

# Download a paper, add to Zotero, and index — one command
r2 rag lit-download "10.1093/example" --type doi

# Forward/backward citation snowballing
r2 rag lit-citations PAPER_ID    # who cited this paper?
r2 rag lit-references PAPER_ID   # what did this paper cite?

# Deep research: local RAG + external databases combined with synthesis
r2 rag lit-deep-research "institutional decay mechanisms"
```

### Skills Engine

Every task is routed through a skill dispatch system. When you ask Claude Code to do something, the framework matches your request against 14 skill definitions using semantic search, then delegates to the right specialized agent with the right tools and instructions. Skills are composable — a literature survey triggers deep-research, which calls source-acquisition to download papers, which calls reading to evaluate them. You can also create, update, and benchmark your own skills.

```bash
# Which skill handles this task? (ranked by confidence)
r2 skills dispatch "write the introduction"

# List all registered skills
r2 skills list

# Create a custom skill
r2 skills create my-skill -d "description" --body-file SKILL.md
```

**Built-in skills:**

| Skill | What it does |
|-------|-------------|
| `writing` | Dense academic prose, equations, tables, captions |
| `analysis` | R pipeline execution, debugging, result alignment |
| `review` | Skeptical stress-testing of arguments and claims |
| `deep-research` | Multi-database literature surveys with snowballing |
| `reading` | Critical evaluation of individual papers |
| `formal-modeling` | Game-theoretic models, proofs, propositions |
| `source-acquisition` | Download, Zotero, and RAG indexing in one step |
| `verification` | Prove correctness before reporting "done" |
| `debugging` | Autonomous error diagnosis and self-correction |
| `proofreading` | First-time reader simulation for flow diagnosis |
| `slides` | Presentation slides synced with manuscript |
| `parallel-dispatch` | Run independent tasks concurrently |
| `portfolio-sync` | Sync title/abstract to a GitHub Pages site |
| `skill-creation` | Create, evaluate, and optimize custom skills |

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

r2 has two components: the **Python package** (CLI + RAG engine) and the **framework files** (agents, skills, commands, rules that live in your project's `.claude/` directory). They update separately.

### Update the Python package

```bash
pip install --upgrade "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

This updates the `r2` CLI, RAG engine, and skills engine. It does not touch your project files.

### Update framework files

Inside Claude Code, run:

```
/update-r2
```

This slash command tells Claude to:

1. Clone the latest r2 template from GitHub
2. Diff each framework file against your local version
3. Auto-apply upstream changes to files you haven't modified
4. For files you *have* customized, show the diff and merge intelligently — preserving your edits while incorporating upstream improvements
5. Never touch user content (`paper.typ`, `ref.bib`, analysis scripts, data)

Because Claude handles the merge (not a script), it understands context: if you renamed a variable in a skill definition and upstream restructured the same skill, Claude merges both changes correctly instead of producing conflict markers.

**First time updating an older project?** If your project doesn't have the `/update-r2` command yet, just tell Claude:

> Update the r2 framework files in this project from https://github.com/shusuke-ioku/r2/tree/main/src/r2/template — diff each file, preserve my local changes, and apply upstream updates.

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
├── .env                   # API keys (created from .env.example)
└── .claude/
    ├── agents/            # 8 agent definitions
    ├── skills/            # 14 skill definitions
    ├── commands/          # 10 slash commands
    ├── rules/             # Project rules
    ├── lessons.md         # Learned patterns (grows over time)
    └── directory-structure.md
```

## Update History

| Date | Change |
|------|--------|
| 2026-03-27 | Drop copier dependency; replace `r2 update` with `/update-r2` slash command (Claude-driven merge); add humanizer skill; expand review skill with editor-report template and reviewer profiles; update agents and skills |
| 2026-03-22 | Initial release v0.1.0 — 8 agents, 14 skills, 10 slash commands, RAG with three external databases, citation snowballing, Skills Engine with Anthropic embeddings |

## License

MIT
