#!/usr/bin/env bash
# PostToolUse hook: R script back-pressure
# Runs syntax check on edited R scripts, reminds agent to run pipeline.
set -euo pipefail

file_path=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0
echo "$file_path" | grep -qE 'analysis/scripts/.*\.R$' || exit 0

script_name=$(basename "$file_path" .R)

# Syntax check (fast — no execution)
parse_out=$(Rscript -e "parse(file='$file_path')" 2>&1) || {
  echo "R SYNTAX ERROR in ${script_name}.R:"
  echo "$parse_out" | tail -10
  exit 1
}

# Inject reminder to run the pipeline
cat <<EOF
{"hookSpecificOutput":{"additionalContext":"R script ${script_name}.R modified and parses OK. Run the analysis pipeline to verify results: bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target ${script_name}"}}
EOF
