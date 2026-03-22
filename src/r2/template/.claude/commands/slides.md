Trigger the slides-writer agent. Create or update presentation slides and talking notes.

Target: $ARGUMENTS (e.g., "sync with latest paper", "add slide for new results", "update notes")

Use the slides-writer agent to:
1. Read paper/paper.typ for current argument, results, and figures
2. Read existing talk/slides.typ and talk/notes.md
3. Diff what has changed since last sync
4. Update talk/notes.md first (script-first principle)
5. Update talk/slides.typ to match
6. Enforce single-line rule (~55 chars max per bullet)
7. Compile: `typst compile --root . talk/slides.typ`
