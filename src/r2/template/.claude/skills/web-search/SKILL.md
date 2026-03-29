---
name: web-search
description: >
  Deep iterative web search using Codex CLI and Claude Code's built-in
  WebSearch/WebFetch. Trigger when any task would benefit from web-based
  information that is NOT in academic databases (Semantic Scholar, OpenAlex,
  Scopus) or the local RAG. Examples: historical background, news coverage,
  government documents, Wikipedia context, organization histories, non-academic
  sources, fact-checking, current events, data sources. Trigger on phrases
  like "search the web for," "find online," "look up," "what does Wikipedia
  say," "is there a news article about," "find background on," or whenever
  the deep-research skill's academic databases are insufficient.
  If the query is purely about academic papers, use deep-research instead.
  This skill is for the OPEN WEB — everything outside academic databases.
---

# Deep Web Search

## Why This Skill Exists

Claude Code's built-in WebSearch returns shallow snippets from a single query.
For real research, you need iterative search: query, read results, identify
gaps, refine, search again, fetch full pages when needed. This skill
orchestrates that loop using two tools:

1. **Codex CLI** (`codex exec`) — dispatched as a subprocess for heavy-lifting
   web research. Codex has its own web search capabilities and can iterate
   autonomously. Use for broad, exploratory queries.
2. **Claude Code's WebSearch/WebFetch** — used directly for quick lookups and
   targeted URL fetching. Use for narrow, specific queries.

## When to Use Which Tool

| Scenario | Tool |
|----------|------|
| Broad exploratory research ("find background on X") | Codex exec |
| Quick fact check ("what year did X happen") | WebSearch |
| Fetch specific URL content | WebFetch |
| Multi-step research with iteration | Codex exec |
| Verify a specific claim | WebSearch + WebFetch |

## Codex Dispatch Pattern

Use `codex exec` via Bash for deep web research:

```bash
codex exec --full-auto --skip-git-repo-check -o /tmp/web_search_result.md \
  "Search the web thoroughly for: QUERY.
   Find at least 5-10 high-quality sources.
   For each source, record: title, URL, key findings.
   Write a structured synthesis with inline citations [1], [2], etc.
   End with a numbered reference list.
   Focus on: SPECIFIC_ASPECTS"
```

**Key flags:**
- `--full-auto` — non-interactive, sandboxed execution
- `--skip-git-repo-check` — allow running outside git repos
- `-o FILE` — write the final response to a file for Claude Code to read
- Uses the default model from `~/.codex/config.toml`

**Read the output** after codex finishes:
```bash
cat /tmp/web_search_result.md
```

## Workflow

### Quick Mode (single query)
1. Use WebSearch with the query
2. If results are sufficient, return them
3. If not, fetch top URLs with WebFetch for more detail
4. Synthesize and return

### Deep Mode (iterative, default)
1. **Initial search**: Dispatch `codex exec` with the research question
2. **Read results**: Read the output file
3. **Gap analysis**: Identify what's missing or needs verification
4. **Follow-up**: Use WebSearch/WebFetch for targeted follow-ups on gaps
5. **Synthesize**: Combine all findings into a structured report

### Output Format

Always return findings in this structure:

```markdown
## Web Search: [QUERY]

### Key Findings
- Finding 1 [1]
- Finding 2 [2]
...

### Synthesis
[Paragraph synthesizing findings thematically]

### Sources
[1] Title — URL
[2] Title — URL
...

### Gaps / Unresolved
- What remains unknown or uncertain
```

## Integration with Other Skills

- **deep-research**: Handles academic databases. Web-search handles everything
  else. When both are needed, dispatch both in parallel.
- **source-acquisition**: If web search finds a relevant academic paper,
  hand off to source-acquisition for proper download + Zotero indexing.
- **reading**: If web search finds a long document worth deep reading,
  consider downloading and reading via the reading skill.

## Failure Modes

**Only searching once.** A single query rarely gives complete coverage.
Iterate: search, read, identify gaps, search again.

**Not fetching full pages.** Search snippets are often insufficient.
When a result looks promising, fetch the full page with WebFetch.

**Mixing academic and web search.** Academic papers should go through
deep-research + source-acquisition. Web search is for the open web.

**Not citing sources.** Every claim must have a URL. No unsourced assertions.
