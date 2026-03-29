Update the r2 framework files from the latest upstream template.

Source: `https://github.com/shusuke-ioku/r2.git` branch `main`, path `src/r2/template/`

## File categories

**Always update** (framework-owned, no user content):
- `.claude/skills/**`
- `.claude/commands/**`
- `.claude/agents/**`
- `.claude/scripts/**`
- `.claude/rules/**`

**Never touch** (user content):
- `paper/paper.typ`
- `paper/style.typ`
- `ref.bib`
- `talk/slides.typ`
- `talk/notes.md`
- `notes/**`
- `library/**`
- `.env`

**Skip** (template-only, not relevant to projects):
- `*.jinja` files
- `copier.yml`

**Everything else**: update if local file is unchanged from previous framework version; show diff and ask if local file was modified.

## Steps

### 1. Fetch upstream

```bash
rm -rf /tmp/r2-update && git clone --depth 1 https://github.com/shusuke-ioku/r2.git /tmp/r2-update
```

### 2. Scan and categorize

For every file under `/tmp/r2-update/src/r2/template/`, skip `*.jinja` and `copier.yml`, then classify:

- If the file matches a "never touch" path: skip
- If the file matches an "always update" path: mark for update
- Otherwise: compare local vs upstream; if identical, skip; if different, mark for review

### 3. Preview

Print a summary table BEFORE making any changes:

```
r2 update preview:
  Updated:  N files (framework skills, commands, agents, rules, scripts)
  Skipped:  N files (user content, unchanged files)
  New:      N files (upstream added, not present locally)
  Review:   N files (both sides changed — will show diffs)
```

Ask the user: "Proceed with update? (The review files will be shown one at a time for your approval.)"

### 4. Apply

- **Always-update files**: copy from upstream, overwriting local
- **New files**: copy from upstream, creating directories as needed
- **Review files**: show the diff and ask the user whether to accept upstream, keep local, or merge

### 5. Clean up

```bash
rm -rf /tmp/r2-update
```

### 6. Report

Print what was updated, what was skipped, and any review files the user chose to keep local.

## Important

- Never touch user content files listed above
- The `.claude/` directory is framework-owned — updates here are safe
- If a skill was customized locally, the update will overwrite it; the user should track customizations in project-specific files, not by editing shipped skills
- Run `git diff` after the update to review all changes before committing
