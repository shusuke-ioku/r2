#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
ANALYSIS_DIR="$ROOT_DIR/analysis"
TARGET="${1:-all}"

if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-all}"
fi

run_script() {
  local script_name="$1"
  echo "[run] analysis/scripts/${script_name}.R"
  (cd "$ANALYSIS_DIR" && Rscript "scripts/${script_name}.R")
}

# Auto-discover valid targets from analysis/scripts/ directory
# Scripts must follow naming convention: NN_descriptive_name.R
VALID_TARGETS=()
if [[ -d "$ANALYSIS_DIR/scripts" ]]; then
  while IFS= read -r f; do
    basename="${f##*/}"
    name="${basename%.R}"
    # Skip setup scripts (00_*) since they are sourced, not run standalone
    if [[ "$name" != 00_* ]]; then
      VALID_TARGETS+=("$name")
    fi
  done < <(find "$ANALYSIS_DIR/scripts" -maxdepth 1 -name '[0-9][0-9]_*.R' | sort)
fi

case "$TARGET" in
  all)
    # Run data construction first, then all analysis scripts in order
    for t in "${VALID_TARGETS[@]}"; do
      run_script "$t"
    done
    ;;
  *)
    matched=false
    for valid in "${VALID_TARGETS[@]}"; do
      if [[ "$TARGET" == "$valid" ]]; then
        run_script "$TARGET"
        matched=true
        break
      fi
    done
    if [[ "$matched" == false ]]; then
      echo "Unsupported target: $TARGET" >&2
      echo "Valid targets: all ${VALID_TARGETS[*]}" >&2
      exit 2
    fi
    ;;
esac

echo "[ok] Pipeline run finished."
