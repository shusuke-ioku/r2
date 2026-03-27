Update the r2 framework files from the latest upstream template.

Source: https://github.com/shusuke-ioku/r2/tree/main/src/r2/template

## Procedure

1. Fetch the latest template file listing from the repo:
   ```
   git ls-tree -r --name-only HEAD:src/r2/template https://github.com/shusuke-ioku/r2.git
   ```
   Or clone to a temp dir:
   ```
   git clone --depth 1 https://github.com/shusuke-ioku/r2.git /tmp/r2-update
   ```

2. Compare each file under `/tmp/r2-update/src/r2/template/` with the corresponding local file. Ignore `.jinja` files and `copier.yml`.

3. For each file:
   - **New upstream file** (doesn't exist locally): Create it.
   - **Upstream changed, local unchanged**: Overwrite with upstream.
   - **Local changed, upstream unchanged**: Keep local version.
   - **Both changed**: Show the user the diff and merge intelligently, preserving local customizations while incorporating upstream improvements.
   - **Files in `_skip_if_exists`** (`paper/paper.typ`, `ref.bib`, `talk/slides.typ`): Never overwrite — these are user content.

4. Report what was updated, what was preserved, and any merges that need the user's attention.

5. Clean up: `rm -rf /tmp/r2-update`

## Important
- Never overwrite user content files (paper.typ, ref.bib, etc.)
- When merging, prefer preserving user customizations over upstream defaults
- Show diffs before making changes to files the user has modified
