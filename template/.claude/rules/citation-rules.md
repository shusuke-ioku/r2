# Citation Rules

- **Zotero only:** Use `.claude/scripts/zotero_add.py` for missing/broken citations (Zotero API + BBT auto-export). Never edit `ref.bib` directly.
- **Cite only what you have read:** Read the source (at minimum its abstract) via RAG or PDF before citing. Never cite from title alone.
- **Never self-cite:** Never use the user's own paper as a source for any argument. The lit review surveys external literature only.
- **Literature context:** Always consult `paper/notes/lit/` before writing prose that engages the literature. Start with `00_overview.md`.
- **Background docs:** All background research goes in `paper/notes/`. Do not scatter elsewhere.
- **Abstract length:** The abstract must never exceed 150 words. Count words after any edit to the abstract and cut until under 150.
- **Typst self-fix:** After any edit to `paper/paper.typ` or `ref.bib`, run `typst compile --root . paper/paper.typ` and self-fix all errors.
