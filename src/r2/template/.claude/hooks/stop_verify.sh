#!/usr/bin/env bash
# Stop hook: verify paper compiles before allowing session end.
# Exit 2 = force agent re-engagement (Claude Code convention).
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
errors=""

# 1. Compile paper.typ if it exists
if [[ -f "$ROOT_DIR/paper/paper.typ" ]]; then
  typst_out=$(cd "$ROOT_DIR" && typst compile --root . paper/paper.typ 2>&1)
  if [[ $? -ne 0 ]]; then
    errors="TYPST COMPILE FAILED — fix before ending session: $(echo "$typst_out" | tail -5)"
  fi
fi

# 2. If errors found, block the stop
if [[ -n "$errors" ]]; then
  cat <<EOF
{"decision":"block","reason":"$errors"}
EOF
  exit 2
fi

# 3. No compile errors — approve with reminder
cat <<'EOF'
{"decision":"approve","reason":"Paper compiles OK. Verify: (1) all changes have evidence, (2) affected R scripts were run."}
EOF
