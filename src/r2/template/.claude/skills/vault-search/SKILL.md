---
name: vault-search
description: >
  Searches the Obsidian vault (library/) for relevant paper notes, concept notes,
  and thematic MOCs. Uses the Obsidian Local REST API when available, falls back
  to file-based search. Trigger whenever context from the literature is needed:
  writing prose that engages the literature, checking what we know about a topic,
  finding which papers discuss a concept, tracing backlinks, or any task where
  consulting library/ would improve the output. Trigger on phrases like "what do
  we have on X," "check our notes," "which papers discuss X," "find notes about
  X," "what does the vault say about X." Also trigger proactively when another
  skill (writing, formal-modeling, review) would benefit from vault context
  before proceeding.
---

# Vault Search

## Why This Skill Exists

The vault (`library/`) contains structured knowledge: atomic paper notes with
YAML frontmatter, concept notes linking papers to ideas, and thematic MOCs
providing overviews. Searching this vault effectively means using its structure
— frontmatter properties, wiki-links, tags, and Obsidian's search — not just
grepping for keywords.

## Search Strategies

Use the strategy (or combination) that best fits the query. Always try the
Obsidian REST API first; fall back to file-based search if Obsidian isn't
running.

### 1. Obsidian REST API (primary, when Obsidian is running)

**Health check:**
```bash
curl -sk https://127.0.0.1:27124/ 2>/dev/null | head -1
```
If this returns JSON, the API is live. Read the API key from the plugin's
config if needed:
```bash
cat library/.obsidian/plugins/obsidian-local-rest-api/data.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('apiKey',''))"
```

**Full-text search** (Obsidian's built-in fuzzy search):
```bash
curl -sk -X POST -H "Authorization: Bearer $KEY" \
  "https://127.0.0.1:27124/search/simple/?query=guardianship+dilemma"
```

**Read a specific note:**
```bash
curl -sk -H "Authorization: Bearer $KEY" \
  "https://127.0.0.1:27124/vault/papers/svolik2012.md"
```

**List all tags with counts:**
```bash
curl -sk -H "Authorization: Bearer $KEY" \
  "https://127.0.0.1:27124/tags/"
```

**Dataview query** (if Dataview plugin is installed):
```bash
curl -sk -X POST -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  "https://127.0.0.1:27124/search/" \
  -d 'TABLE authors, year, relevance FROM "papers" WHERE contains(themes, "democratic-backsliding") SORT relevance ASC'
```

### 2. File-based search (fallback, always available)

Use these when Obsidian isn't running or for quick targeted lookups.

**a. Frontmatter property search** — find papers by theme, relevance, year:
```bash
# All high-relevance papers on a theme
grep -rl "theme-keyword" library/papers/ | \
  xargs grep -l "relevance: high"
```

**b. Backlink search** — find all notes linking to a specific paper or concept:
```bash
# Everything that references a citekey
grep -rl "\[\[citekey\]\]" library/
```

**c. Citekey lookup** — jump straight to a paper note:
```bash
cat library/papers/citekey.md
```

**d. Concept traversal** — read a concept note, then follow its linked papers:
```bash
# Read the concept, extract linked papers
cat library/concepts/concept-name.md
grep -oP '\[\[([^\]]+)\]\]' library/concepts/concept-name.md
```

**e. MOC scan** — read a thematic overview for broad context:
```bash
cat library/lit/topic-name.md
```

**f. Multi-property YAML search** — parse frontmatter for structured queries:
```bash
# Find all papers from 2020+ with high relevance
python3 -c "
import glob, yaml, sys
for f in glob.glob('library/papers/*.md'):
    with open(f) as fh:
        txt = fh.read()
    if not txt.startswith('---'): continue
    fm = txt.split('---')[1]
    try:
        d = yaml.safe_load(fm)
        if d.get('year',0) >= 2020 and d.get('relevance') == 'high':
            print(f'{f}: {d.get(\"citekey\")} ({d.get(\"year\")})')
    except: pass
"
```

## When to Use Which Strategy

| Need | Strategy |
|------|----------|
| "What do we know about X?" | Full-text search (API or grep) |
| "Which high-relevance papers on theme Y?" | Frontmatter property search |
| "What cites paper Z?" | Backlink search for `[[Z]]` |
| "Give me context on concept W" | Concept note → follow links |
| "Broad overview of topic T" | MOC scan in `library/lit/` |
| "All papers by Author A" | Frontmatter `authors:` search |
| "Recent work (2020+) on X" | Multi-property YAML search |

## Output Format

Return results as a structured list:

```
### Vault Search Results: [query]

**Papers found:** N
**Concepts found:** M

#### Most relevant
- [[citekey1]] — one-line summary (relevance: high)
- [[citekey2]] — one-line summary (relevance: high)

#### Supporting
- [[citekey3]] — one-line summary (relevance: medium)

#### Concepts
- [[concept-name]] — definition summary

#### MOCs consulted
- library/lit/topic.md — section headings relevant to query
```

When called by another skill (writing, review, etc.), return the **content**
of the most relevant notes directly so the calling agent has the context it
needs without a second lookup.

## Integration with Other Skills

This skill is a **service skill** — other skills should invoke it (or the
vault-searcher agent) before proceeding when literature context would help:

- **writing**: Search vault before writing prose that engages the literature
- **formal-modeling**: Search for related formal models before designing a new one
- **review**: Search for papers a reviewer might cite as challenges
- **deep-research**: Check vault for what's already known before searching externally

## Common Failure Modes

**Searching only by keyword.** The vault's structure (frontmatter, links) is
more precise than full-text search. Use property queries for structured needs.

**Ignoring MOCs.** The thematic MOCs in `library/lit/` are curated overviews —
they're often the fastest path to relevant context.

**Not following links.** A concept note links to papers; a paper note links
to concepts. One hop through the link graph often surfaces what you need.

**Returning file paths instead of content.** The caller needs the actual
information, not just where to find it. Read and return the relevant content.
