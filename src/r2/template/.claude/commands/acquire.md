Trigger the source-acquirer agent. Download papers, add to Zotero, and index into RAG.

Target: $ARGUMENTS (e.g., a DOI like "10.1017/S0003055421000460", a paper title, or a JSON batch)

Use the source-acquirer agent to:
1. Find DOI if only title provided (search Semantic Scholar)
2. Download via Sci-Hub: `r2 rag lit-download "IDENTIFIER" --type TYPE --title "TITLE"`
3. Verify Zotero addition (mandatory -- every paper must be in Zotero)
4. Verify RAG indexing (check chunk count in output)
5. For batch: `r2 rag lit-download-batch 'JSON' --auto-index`
6. Report results: which papers succeeded, which failed, and why
