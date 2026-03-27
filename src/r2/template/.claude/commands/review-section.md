Trigger the reviewer agent to run a full simulated journal review.

Target: $ARGUMENTS (e.g., "full paper", "identification strategy", "Section 3", "the mechanism argument")

The reviewer agent acts as a journal editor and will:
1. Read the target and identify the discipline, methods, and case domain
2. Dispatch three parallel reviewer subagents:
   - R1: Literature Scholar (theory, contribution, novelty, literature engagement)
   - R2: Methodologist (identification, inference, data quality, robustness)
   - R3: Case/Domain Expert (empirical accuracy, sources, interpretive validity)
3. Collect all three reviews
4. Produce a consolidated Editor Report with:
   - NVI assessment (Novelty, Validity, Importance)
   - Consensus issues, unique concerns, contradictions
   - Revision roadmap ranked by priority
   - Publication assessment with honest venue-tier probabilities

Follow `.claude/skills/review/SKILL.md` exactly.
