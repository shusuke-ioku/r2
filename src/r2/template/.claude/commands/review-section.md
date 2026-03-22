Trigger the reviewer agent. Stress-test a section or argument in the manuscript.

Target: $ARGUMENTS (e.g., "identification strategy", "Section 3", "the mechanism argument")

Follow `.claude/skills/review/SKILL.md` exactly:
1. Literature background via RAG tools first
2. Skeptical attack on each claim (steelman, then object)
3. Constructive repair for each objection
4. Severity rating (fatal / serious / minor)

Output the review using the template in `.claude/skills/review/references/review-template.md`.
