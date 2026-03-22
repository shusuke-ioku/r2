# Proof-Checking Protocol

A systematic protocol for verifying propositions and proofs. Run this checklist every time a proof is written or revised.

## Step 1: Structure Check

Before examining any algebra, verify the proof's logical skeleton.

1. **Is the proof strategy stated?** (direct proof, contradiction, induction, construction)
2. **Are all assumptions referenced by number?** Every "by Assumption X" should point to a numbered assumption that exists.
3. **Does the conclusion match the proposition?** Read the proposition statement and the proof's final line side by side. They must say the same thing.
4. **Is the proof complete?** Does it cover all cases? If the proposition says "for all $\theta > \bar{\theta}$", does the proof handle the boundary $\theta = \bar{\theta}$?

## Step 2: Algebraic Verification

Redo every derivation from scratch. Do not read the existing algebra and nod along---re-derive it independently and compare.

### Common algebraic errors

**Sign errors in derivatives:**
- When taking $\partial / \partial \theta$ of a product $f(\theta) \cdot g(\theta)$, apply the product rule fully
- When differentiating through a max or argmax, use the envelope theorem (Milgrom-Segal) or verify directly

**Division by zero:**
- Check every denominator. If it can be zero for some parameter value, the proof must either exclude that value or handle it separately

**Monotonicity claims:**
- "Clearly increasing" is not a proof. Show the derivative is positive, or show the function is a composition of increasing functions
- For implicit functions, use the implicit function theorem and check the sign of $-F_\theta / F_x$

**Inequality chains:**
- Every $\geq$ vs $>$ matters. If the proposition claims strict inequality, the proof must produce strict inequality at every step
- Watch for "weak link" steps where $>$ degrades to $\geq$

**Optimization:**
- First-order conditions are necessary but not sufficient (unless the objective is globally concave)
- Check second-order conditions: $\partial^2 U / \partial c^2 < 0$ at the optimum
- Check boundary solutions: is the interior optimum actually in the feasible set?

## Step 3: Logical Verification

### Necessary vs. sufficient conditions

The most common logical error in political science theory papers. If you prove "A implies B", you have NOT proven "B implies A." Check:
- Does the proposition claim necessity, sufficiency, or both?
- Does the proof deliver what was claimed?

### Existence vs. uniqueness

Proving an equilibrium exists is different from proving it is unique. If the proposition claims uniqueness, the proof must rule out all other equilibria, not just exhibit one.

### Vacuous truth

A proposition "If A then B" is vacuously true when A is impossible. Check that the conditions under which the proposition applies are non-empty. For example, "For $\theta > \bar{\theta}$ and $\theta < \underline{\theta}$..." is vacuously true if $\bar{\theta} > \underline{\theta}$.

## Step 4: Economic Plausibility

After verifying the math, check whether the result makes economic sense.

1. **Extreme cases:** What happens as $\theta \to 0$ (no distress) and $\theta \to 1$ (maximal distress)? Do the equilibrium predictions make intuitive sense at the boundaries?
2. **Comparative statics signs:** Does each comparative static match the verbal intuition in the introduction? If the math says one thing and the intuition says another, one of them is wrong---find out which.
3. **Parameter restrictions:** Are the conditions for the main result empirically plausible? If the proposition requires $\gamma > 0.99$, it may be mathematically correct but empirically irrelevant.
4. **Degenerate cases:** What happens when two players have the same payoff? When a probability is exactly 0 or 1? These edge cases often reveal hidden assumptions.

## Step 5: Presentation Check

1. **Can a non-theorist follow the proof?** Read it as if you are a comparativist who last took a game theory course in graduate school. Flag any step that requires knowledge beyond Nash equilibrium, subgame perfection, and basic calculus.
2. **Is anything relegated to the appendix that should be in the main text?** Key intuition-building steps belong in the body. Tedious algebra belongs in the appendix. If the only way to understand why the result holds is to read the appendix, the main-text proof is too terse.
3. **Are there verbal guideposts?** Between algebraic blocks, include sentences like "The key step is..." or "Rearranging and using Assumption 2..." to help the reader follow the logic without re-deriving everything.

## Red Flags

If you encounter any of these, stop and investigate:

- A comparative static that flips sign for "reasonable" parameter values
- An equilibrium that requires a player to use a weakly dominated strategy
- A proof that works only for a knife-edge parameter value (measure zero)
- An assumption that is never used in any proof (either drop it or explain why it is there for interpretation)
- Two propositions that appear to contradict each other under overlapping parameter ranges
- A result that holds "generically" without specifying what genericity means
