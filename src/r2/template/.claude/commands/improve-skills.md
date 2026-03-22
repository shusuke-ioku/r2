---
description: >
  Review skill triggering performance and propose/apply improvements based on
  real usage data. Run with no args for a dry-run report, "apply" to improve and
  write back, or a skill name to focus on one skill.
---

# Improve Skills

Review and optimize skill descriptions based on accumulated usage data.

## Arguments

- No arguments: dry-run report showing which skills need improvement and why
- `report`: same as no arguments
- `apply`: run improvements and apply the best descriptions to SKILL.md files
- `<skill-name>`: focus on a specific skill (e.g., `analysis`, `writing`)
- `<skill-name> apply`: focus on one skill and apply the result

## Steps

1. Run the auto-improvement orchestrator from `.claude/skills/skill-creation/scripts/auto_improve.py`
2. The orchestrator will:
   - Read usage data from `.claude/skills_engine/.usage.db`
   - Score each skill on: avg confidence, confidence variance, event count, time since last improvement
   - For dry-run: display the priority-ranked report
   - For apply: generate eval sets, run improvement loops, and write improved descriptions
3. After applying, trigger `skill_reindex` via MCP to update the semantic index

## Usage

```bash
# From the skill-creation scripts directory:
cd .claude/skills/skill-creation
PYTHONPATH="$PWD" python3 scripts/auto_improve.py \
  --skills-dir ../../skills \
  --db ../../skills_engine/.usage.db \
  --model sonnet \
  --verbose \
  [--run] [--apply] [--force SKILL_NAME]
```

## Important

- The improvement loop spawns `claude -p` subprocesses for each eval query
- Cost: ~120 API calls per skill (3 iterations * 20 queries * 2 runs)
- Default is dry-run (report only) — use `--run` to actually improve, `--apply` to write back
- Descriptions are backed up to `description_history.json` before modification
- 7-day cooldown between improvements for the same skill
