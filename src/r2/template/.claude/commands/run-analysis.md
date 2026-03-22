Trigger the analyst-agent. Run the analysis pipeline and report results.

If an argument is provided ($ARGUMENTS), run only that target script:
`bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh --target $ARGUMENTS`

If no argument, run the full pipeline:
`bash .claude/skills/analysis/scripts/run_analysis_pipeline.sh`

After running:
1. Read updated outputs in `analysis/output/results/`
2. Report key findings: coefficient direction, magnitude, significance, red flags
3. Check paper alignment: verify `paper/paper.typ` tables/figures/prose match latest outputs
4. Trigger the verifier skill before claiming completion
