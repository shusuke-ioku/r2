# r2

*Not the droid you're looking for — but it will get your paper through R&R.*

An AI research environment for political science, built on [Claude Code](https://claude.ai/claude-code). r2 treats writing, reviewing, and literature work as engineering problems: every evaluation norm is extracted from real published papers, every skill is routed before the model acts, and every guardrail is automated.

## What it does

**Write like the journals you're targeting.** The writing and polishing skills are calibrated against an empirical audit of APSR/AJPS papers — not generic style guides. When the skill says "move your finding to paragraph 2," that's because 82% of top-tier intros do exactly that.

**Know what reviewers will say before they say it.** Three simulated reviewers — a literature scholar, a methodologist, and a domain expert — score your paper on Novelty, Validity, and Importance. Their biases have been corrected against a blind training set so they don't under-rate formal theory or compress scores to the middle.

**Read the literature faster than you can download it.** A local RAG index over your PDFs, three external databases, snowballing, automatic PDF acquisition, and Zotero integration. The survey loops until it stops finding new leads. Think Claude's deep research, but for academic papers — with your own library as the starting point.

**Build a knowledge base as you go.** Every paper you read becomes a structured Obsidian note. Future writing and review skills consult it automatically.

## Install

```bash
pip install "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
r2 init my-paper/ && cd my-paper/
cp .env.example .env   # add ANTHROPIC_API_KEY
claude                  # start Claude Code
```

Add r2 to an **existing project**: `r2 init .` — writes framework files only, never touches your paper or data.

## Updating

Run `/update-r2` inside Claude Code. To update the CLI itself:

```bash
pip install --upgrade "r2-research @ git+https://github.com/shusuke-ioku/r2.git"
```

## API Keys

Only `ANTHROPIC_API_KEY` is required. Optional keys unlock Scopus, Semantic Scholar, and Zotero. See `.env.example`.

---

## Manuscript Polish

The problem with LLM writing assistance: it doesn't know what good looks like in your field. r2 solves this by extracting concrete norms from an 80-paper calibration corpus of APSR/AJPS publications — what verbs they use, how they structure intros, where they place findings, how they close conclusions.

Three parallel assessors evaluate your manuscript from distinct angles:

| Assessor | Focus | Example issues |
|----------|-------|----------------|
| **Proofreader** | Reader experience | "Your finding doesn't appear until paragraph 4 — the reader has been passive for 3 paragraphs" |
| **Calibration assessor** | Field norms | "With an IV first-stage F of 28, this hedging damages trust — 75% of APSR papers state the main finding flatly" |
| **Humanizer** | AI tells | "Significance inflation: 3 adjectives in 2 sentences. Published papers let the coefficients speak." |

After assessment, the orchestrator deduplicates issues, ranks by severity, and builds a revision plan with word budgets per section. Revisions proceed section-by-section with Typst compilation after each edit. The loop re-assesses and iterates until convergence.

**Priority ordering is corpus-backed**: intro ownership (+32pp gap between top and non-top) gets fixed before results placement (+9pp gap) gets fixed before sentence-level polish.

```
> /polish                    # full convergence loop
> "polish for APSR"          # triggers automatically
```

## Simulated Peer Review

Manuscript polish makes your writing match what gets published. Peer review asks a different question: **will this paper get in?**

An editor agent dispatches three independent reviewer subagents, each with expertise tailored to your paper's field, method, and case. They write severity-graded reports (fatal / serious / minor) and ground every objection in published work via RAG.

The **NVI scoring system** (Novelty, Validity, Importance) is adapted from real editorial practice. Each dimension is scored 1--5; the composite drives venue-tier classification and R&R probability estimates.

The scoring has been **calibrated against a blind test set** of top-generalist vs. field-journal papers, correcting five biases: formal theory undervaluation, top-field hedging, non-novelty over-application, probability compression, and score compression toward 3--4.

| Polish answers | Review answers |
|----------------|----------------|
| Does this read like APSR? | Would APSR accept it? |
| Is the intro front-loaded? | Is the contribution novel? |
| Are the findings stated at the right confidence level? | Is the identification strategy credible? |
| Are there AI-writing tells? | Does the literature positioning hold up? |

```
> /review                     # full simulated peer review
> "stress-test my argument"   # triggers automatically
```

## Literature Surveys

r2 builds a **local RAG vector store** (ChromaDB + sentence-transformers) over your PDF library and connects to three external databases: Semantic Scholar, OpenAlex, and Scopus.

The `deep-research` skill runs an iterative discovery loop:

1. **Search** local RAG + external databases with multiple query variations
2. **Snowball** forward and backward citations from high-priority papers
3. **Acquire** PDFs automatically: download, create Zotero item with CrossRef metadata, index into RAG
4. **Read** acquired papers in full text, not just abstracts
5. **Check convergence**: new leads found? Loop back. No? Synthesize.

The loop typically runs 2--4 iterations. The final report is thematic, not paper-by-paper.

**Zotero integration** operates at two levels: the cloud API creates items with full metadata and PDF attachments (auto-exported via Better BibTeX), while the local API gives Claude direct access to your library, highlights, and annotations.

```bash
r2 rag index                              # index PDFs into vector store
r2 rag search "democratic backsliding"     # semantic search
r2 rag lit-search "exit voice" --focus top_journals
r2 rag lit-download "10.1093/example"      # download + Zotero + index
```

## Knowledge Vault

r2 scaffolds an [Obsidian](https://obsidian.md) vault at `library/` with three note types:

- **Paper notes** — one per source, with structured sections: key arguments, findings, methods, relevance, critique
- **Concept notes** — one per theoretical idea, linking to papers that develop it
- **Thematic MOCs** — Maps of Content organized by theme with `[[wiki-links]]`

The `vault-search` skill uses Obsidian's Local REST API when available, or file-based search as fallback. Other skills consult the vault automatically before writing or reviewing.

## Skills and Agents

Every request is matched to a skill before Claude acts. 18 skills route to 13 specialized agents:

| Skill | What it does |
|-------|-------------|
| `polishing` | Convergence-loop submission polish with 3 parallel assessors |
| `writing` | Empirically calibrated academic prose |
| `proofreading` | First-time reader simulation for flow diagnosis |
| `review` | Simulated peer review with NVI scoring |
| `deep-research` | Multi-database literature surveys with snowballing |
| `reading` | Critical evaluation of papers + vault notes |
| `source-acquisition` | Download papers, Zotero, RAG indexing |
| `analysis` | R pipeline management and debugging |
| `formal-modeling` | Game-theoretic models, proofs, propositions |
| `slides` | Presentation slides synced with manuscript |
| `vault-search` | Obsidian vault search for literature context |
| `task-management` | Revision dashboard |
| `verification` | Prove correctness before reporting "done" |
| `skill-creation` | Create, evaluate, and optimize custom skills |

```bash
r2 skills dispatch "rewrite the theory section"   # which skill handles this?
r2 skills list                                      # all registered skills
```

## Design Principles

**Norms from data, not intuition.** The calibration layer is built from an 80-paper corpus audit. When the model says "this is how top journals do it," it can cite the count.

**Mandatory skill dispatch.** Every request hits the skill router first. A rationalization-prevention table blocks excuses like "this is too simple for a skill."

**Automated guardrails via hooks.** Typst auto-compilation, R syntax checks, file-edit blocks, compilation verification before session end, rule re-injection after context compaction.

**Build to delete.** Every skill encodes an assumption about what the model can't do reliably. Stress-test those assumptions as models improve.

## License

MIT
