Trigger the verifier skill. Verify the current state of the project.

If $ARGUMENTS is provided, verify that specific claim or component.

Otherwise, run a full verification:
1. Run `typst compile --root . paper/paper.typ` -- confirm exit 0
2. Check that `analysis/output/results/` files are up to date
3. Spot-check that key numbers in the paper match the latest output files
4. Report actual state with evidence -- no assumptions
