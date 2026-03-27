---
name: source-acquisition
description: >
  Downloads academic papers via Sci-Hub, adds them to Zotero with full metadata,
  indexes them into the local RAG vector store, and optionally reads them via the
  reading skill. TRIGGER this skill whenever the user asks to: download a paper,
  get a PDF, acquire a source, add a paper to the library, "get me this paper",
  "download this DOI", "add this to Zotero", "I need the full text of X",
  "can you find the PDF for X", or any request that involves obtaining a paper
  that is not yet in the local library. Also trigger when the deep-research skill
  identifies papers to acquire, when a citation is needed but the paper is not
  indexed, or when the user provides a DOI, title, or paper ID and wants it
  in the system. If in doubt, trigger -- a failed download is cheap, a missing
  source is expensive.
---

# Source Acquisition

Acquire papers, add to Zotero, index for RAG, and read. Every acquired paper
MUST be added to Zotero -- no exceptions.

## Why This Skill Exists

The deep-research skill identifies papers worth reading. The reading skill
evaluates them. But between discovery and reading there is a gap: the paper
must be downloaded, added to Zotero (so it appears in `ref.bib` via BBT
auto-export), and indexed into the RAG vector store (so it becomes searchable).
This skill owns that entire pipeline.

## Pipeline: Download → Zotero → Index → (Read)

Every acquisition follows this exact sequence:

### Step 1: Download via Sci-Hub

Use the RAG CLI to download the paper:

```bash
r2 rag lit-download "IDENTIFIER" \
  --type TYPE --title "PAPER TITLE"
```

- **IDENTIFIER**: DOI (preferred), PMID, or paper title
- **TYPE**: `doi`, `pmid`, or `title` (auto-detected if omitted)
- **TITLE**: Always provide when available -- used as Zotero metadata fallback

DOI is always preferred. If you only have a title, search Semantic Scholar first
to find the DOI:

```bash
r2 rag lit-search "TITLE" --focus broad -n 5
```

Then use the DOI from the search results.

### Step 2: Verify Zotero Addition

The `lit-download` command automatically:
1. Downloads the PDF via Sci-Hub (scidownl + direct scraping fallback)
2. Resolves metadata from CrossRef (for DOIs)
3. Creates a Zotero library item with full metadata
4. Attaches the PDF to the Zotero item

Check the output for:
- `Zotero: added (ITEM_KEY)` = success
- `Zotero: ...error...` = partial failure -- item may exist without PDF

If Zotero fails, use the standalone script as fallback:
```bash
python .claude/scripts/zotero_add.py CITEKEY
```

**Zotero addition is mandatory.** Every downloaded paper must appear in Zotero
so that BBT auto-exports it to `ref.bib`. Without this, the paper cannot be
cited in the manuscript.

### Step 3: Verify RAG Indexing

The `lit-download` command auto-indexes into RAG after download. Check the
output for:
- `Indexed dir__FILENAME (N chunks)` = success
- `Skipped (exists)` = already indexed (OK)
- `Total entries: 0` = indexing failed (see Troubleshooting)

Verify the paper is searchable:
```bash
r2 rag search "KEY TERM FROM PAPER" -n 3
```

### Step 4: Read (Optional but Recommended)

After indexing, the paper is available for full-text RAG queries. If the paper
was acquired for a specific purpose (e.g., to support a claim in the manuscript),
read it immediately using the reading skill:

```bash
r2 rag query "SPECIFIC QUESTION" --citekey dir__FILENAME
```

Or trigger the reading skill for a comprehensive evaluation.

## Batch Acquisition

For multiple papers (e.g., from a deep-research "Papers to Index" table):

```bash
r2 rag lit-download-batch \
  '[{"id": "10.xxxx/yyyy", "title": "Paper Title"}, {"id": "10.xxxx/zzzz", "title": "Another Paper"}]' \
  --auto-index
```

Each paper in the batch is automatically added to Zotero. The `--auto-index`
flag indexes all downloaded PDFs at once.

**Priority order:** Download HIGH-priority papers first. Ask the user before
downloading MEDIUM/LOW papers if the list is long (>5 papers).

## DOI Discovery

When you have a paper title but no DOI, find it before downloading:

1. **Semantic Scholar**: `lit-search "TITLE" --focus broad -n 5`
2. **OpenAlex**: `lit-search "TITLE" --source oa -n 5`
3. **CrossRef** (via curl): `curl -s "https://api.crossref.org/works?query=TITLE&rows=3"`

Always prefer DOI over title for downloads -- DOI-based downloads have higher
success rates and better Zotero metadata.

## Download Chain (4-tier fallback)

Acquisition tries four strategies in order. If one tier fails, the next
tier activates automatically. **Do not flag a paper as failed until all
four tiers have been exhausted.**

### Tier 1: Sci-Hub (via `lit-download`)

The `lit-download` command tries three Sci-Hub strategies internally:

1. **scidownl** (primary) — Python Sci-Hub client
2. **Direct httpx scraping** — Parses HTML for PDF URLs, downloads with httpx
3. **Lightpanda browser** — Renders Sci-Hub pages with JavaScript via
   Lightpanda headless browser, rewrites PDF URLs to the source mirror domain.

The Lightpanda fallback requires the binary at `.venv/bin/lightpanda` (already
installed). It uses `fetch --dump html --with_frames` mode to render pages with
full JavaScript execution, then extracts the PDF URL from the rendered DOM.

### Tier 2: Web search for open-access PDF

If Sci-Hub fails (all mirrors exhausted), search the web for an open-access
version. Many papers are freely available on author pages, working paper
series, or institutional repositories.

**Search strategy** (use WebSearch tool):

```
"PAPER TITLE" filetype:pdf
```

If that fails, try broader queries:
```
"FIRST AUTHOR LAST NAME" "SHORT TITLE" pdf
"PAPER TITLE" site:nber.org OR site:ssrn.com OR site:repec.org
```

**Common open-access sources** (prioritize in this order):
1. **NBER** (nber.org) — working papers freely available
2. **SSRN** (ssrn.com, papers.ssrn.com) — preprints and working papers
3. **Author personal/institutional pages** — often host final or near-final PDFs
4. **ResearchGate** — author-uploaded versions
5. **University repositories** — institutional open-access mandates
6. **arXiv / EconPapers / IDEAS/RePEc** — preprint servers
7. **Journal open access** — some papers are gold/green OA

**Download the PDF** (use WebFetch or curl):
```bash
curl -L -o ".claude/rag/pdfs/FILENAME.pdf" "PDF_URL"
```

**Verify the PDF** is valid (not an HTML error page or login wall):
```bash
file ".claude/rag/pdfs/FILENAME.pdf"  # should say "PDF document"
head -c 5 ".claude/rag/pdfs/FILENAME.pdf"  # should start with %PDF-
```

**After successful web download**, continue to Step 2 (Zotero) and Step 3
(RAG indexing) as normal. The paper still needs Zotero metadata and RAG
indexing regardless of how it was obtained.

To add the downloaded PDF to Zotero and index into RAG:
```bash
# Add to Zotero with metadata
python .claude/scripts/zotero_add.py --doi "DOI" --pdf ".claude/rag/pdfs/FILENAME.pdf"
# Index into RAG
r2 rag index --source dir --pdf-dir .claude/rag/pdfs
```

### Tier 3: Semantic Scholar open-access URL

Some papers have publisher-provided open-access links in Semantic Scholar:

```bash
r2 rag lit-paper "S2_PAPER_ID"
```

Check the output for an `openAccessPdf` URL. If present, download directly.

### Tier 4: Flag for manual acquisition

Only after Tiers 1-3 all fail, flag the paper for the user with:
- Title, authors, DOI
- What was tried and why it failed
- Suggested manual routes (university library proxy, interlibrary loan,
  email the author)

## Troubleshooting

### Download fails (all tiers exhausted)
- Paper may be behind a strict paywall with no OA version
- Flag to user for manual acquisition (university library, author request)

### Zotero addition fails
- Check Zotero desktop is running (needed for BBT auto-export)
- Check API credentials: `RAG_ZOTERO_API_KEY` and `RAG_ZOTERO_LIBRARY_ID` in `.env`
- Use fallback: `python .claude/scripts/zotero_add.py CITEKEY`

### Auto-indexing shows 0 entries
- This was a known bug (now fixed): `pdf_dir` was empty
- If it recurs, manually index: `r2 rag index --source dir --pdf-dir .claude/rag/pdfs`

### Paper indexed but not searchable
- Embedding model may not handle the paper's language well
- Try: `r2 rag remove dir__FILENAME && r2 rag index --force --source dir --pdf-dir .claude/rag/pdfs`

## Rules

- **Zotero is mandatory**: Every downloaded paper must be added to Zotero. No exceptions.
- **DOI first**: Always find the DOI before downloading. Title-based downloads are a last resort.
- **Verify every step**: Check download success, Zotero status, and indexing status in the output.
- **Report failures**: If a paper cannot be downloaded, tell the user immediately with the reason.
- **Never edit ref.bib**: Zotero + BBT handles bibliography. Use `zotero_add.py` for missing entries.
- **Clean filenames**: The `--filename` flag accepts citekey-style names (e.g., `reny2021_apsr`).
