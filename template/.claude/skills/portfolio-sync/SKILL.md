---
name: portfolio-sync
description: >
  Use at the end of every session, or when the user says "sync portfolio",
  "update portfolio", "push to portfolio", or "end of session". Syncs the
  paper's title and abstract to the user's GitHub Pages portfolio site.
---

# Portfolio Sync

Sync the current title and abstract from `paper/paper.typ` to the portfolio site, then commit and push.

## Workflow

1. Read the current title and abstract from `paper/paper.typ`.
2. Read `../../_portfolio/research.qmd`.
3. Update the title and abstract in `research.qmd` to match the paper.
4. Commit the change in the portfolio repo (`../../_portfolio/`).
5. Push to remote.

## Rules

- Only update title and abstract — do not touch other content in `research.qmd`.
- If nothing changed since last sync, skip silently.
- The portfolio repo is at `../../_portfolio/` (GitHub Pages site).

## Post-sync: Skill Health Check

After syncing, run the lightweight skill improvement check:

```bash
cd .claude/skills/skill-creation && PYTHONPATH="$PWD" python3 scripts/check_improvement_needed.py \
  --skills-dir ../. --db ../../skills_engine/.usage.db
```

If any skills need improvement, mention it briefly to the user (e.g., "2 skills could benefit from improvement — run `/improve-skills` when convenient.").
