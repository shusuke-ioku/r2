Trigger the manuscript-writer agent. Write or revise a section of the manuscript.

Target section: $ARGUMENTS (e.g., "introduction", "lit review", "results", "theory")

Before writing:
1. Read `.claude/skills/writing/SKILL.md` and follow it exactly
2. Read surrounding sections in `paper/paper.typ` for context and flow
3. Read the abstract and contribution claims for alignment
4. If the section engages literature, consult `notes/lit/` first

After writing:
1. Run `typst compile --root . paper/paper.typ` and fix all errors
2. Verify the section is consistent with the rest of the paper
3. Trigger the verifier skill before claiming completion
