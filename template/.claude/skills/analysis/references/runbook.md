# R Pipeline Runbook

## Running the pipeline

From the repo root:

```bash
# Full pipeline (runs all numbered scripts in order)
bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh

# Targeted run (preferred when only one script changed)
bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target 30_main_results
```

## Script inventory and dependencies

### Dependency chain

```
00_setup.R  (sourced by all scripts -- libraries, config, helpers)
    |
20_data.R  (data construction -- produces the analysis datasets)
    |
    +-- 30_main_results.R   (main analyses)
    +-- 40_robustness.R     (robustness checks)
    +-- ...                  (add more scripts as needed)
```

### What the dependency chain means

- **If you change `00_setup.R`**: Every script may be affected. Rerun the full pipeline.
- **If you change `20_data.R`**: All downstream scripts (30+) need rerunning because they consume its outputs.
- **If you change a leaf script** (e.g., `40_robustness.R`): Only that script needs rerunning.

### Script naming convention

| Range | Purpose |
|-------|---------|
| `00_*` | Setup (sourced, not run standalone) |
| `20_*` | Data construction |
| `30_*` | Main analyses |
| `40_*` | Robustness checks |
| `50_*` | Extensions / supplementary analyses |

## Integrity checks

After every pipeline run, verify:

1. The target R script exited successfully (exit code 0).
2. Expected output markdown files exist and are non-empty in `analysis/output/results/`.
3. If figure-generating scripts ran, check that PNGs in `analysis/output/figures/` have fresh timestamps.
4. If results changed, compile the paper (`typst compile --root . paper/paper.typ`) and fix any errors.
5. Spot-check that in-text numbers in `paper/paper.typ` match the latest output files.

## Troubleshooting

### Script fails with package error
Install the missing package, then rerun. All packages should be loaded via `00_setup.R`.

### Outputs look stale
If output file timestamps are older than script timestamps, rerun the full pipeline rather than guessing which scripts are stale.
