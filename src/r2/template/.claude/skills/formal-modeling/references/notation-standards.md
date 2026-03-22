# Notation Standards for Formal Theory

Consistent notation across the model, empirical sections, and appendix is essential. Reviewers who spot inconsistency between the theory and empirics sections will question whether the author understands the connection between the two.

## General Rules

1. **One symbol per concept, one concept per symbol.** If $\theta$ means economic distress in one proposition, it means economic distress everywhere.
2. **Roman for labels, italic for variables.** Use $\text{OrgDensity}$ (upright) for empirical variable names in regression equations; use single italic letters ($D$, $\theta$) in the formal model.
3. **Subscripts for indexing, superscripts for types.** Player $i$'s action is $a_i$; a type-$H$ (honest) politician's action is $a^H$.
4. **Bold for vectors.** $\mathbf{X}$ for a covariate vector, $x$ for a scalar.
5. **Blackboard bold for standard sets.** $\mathbb{R}$ for reals, $\mathbb{1}$ for indicator functions.

## Player Labels

| Player | Symbol | Notes |
|---|---|---|
| Incumbent party | $I$ | Can also use $P$ for "party" if context is clear |
| Radical challenger | $C$ | |
| Voters / public | $V$ or mass of voters on $[0,1]$ | |
| Nature | Standard game-theory convention | |

## Key Parameters

| Concept | Symbol | Domain | Notes |
|---|---|---|---|
| Economic distress | $\theta$ | $[0, 1]$ or $\mathbb{R}_+$ | Higher = worse crisis |
| Gatekeeping capacity | $\gamma$ | $[0, 1]$ | Higher = parties better at excluding challengers |
| Corruption level | $c$ | $[0, 1]$ | Chosen by incumbent |
| Cost of extraparliamentary action | $\kappa$ | $\mathbb{R}_+$ | Fixed cost to challenger |
| Public susceptibility to radical ideology | $s(\cdot)$ | $[0, 1]$ | Function of corruption and distress |
| Probability of backsliding | $\pi$ | $[0, 1]$ | Equilibrium outcome |

## Equilibrium Notation

- Equilibrium strategies: starred ($c^*, a^*$) or with superscript $\text{eq}$
- Best-response functions: $BR_i(\cdot)$
- Expected utility: $U_i(\cdot)$ or $\mathbb{E}[u_i(\cdot)]$

## Typst Formatting

### Propositions and Proofs

Use the custom environments defined in `paper/style.typ`:

```typst
#asp[Economic Distress][
  The parameter $theta in [0, 1]$ represents the severity of economic distress.
  Higher $theta$ reduces the electoral return to good policy.
]

#prop[Gatekeeping Paradox][
  For $theta > overline(theta)$, the equilibrium probability of extraparliamentary
  action $pi^*$ is increasing in gatekeeping capacity $gamma$.
]

#proof[
  Consider the challenger's decision...
  ...
  This establishes the result. $qed$
]
```

### Numbered Equations

Use `#nneq()` for numbered display equations:

```typst
#nneq($
  U_I (c) = (1 - c) dot v(theta) + c dot r - (1 - gamma) dot L
$)
```

### Inline Math

Standard Typst `$...$`:

```typst
The incumbent chooses corruption $c in [0, 1]$ to maximize expected utility.
```

## Mapping Model to Empirics

When referencing the model in the empirical section (or vice versa), use explicit mapping:

```typst
The model predicts that organizational density ($D$ in the model,
$"OrgDensity"_(p,t)$ in the regression) increases with economic
distress ($theta$, proxied by the change in per-capita income 1929--1931).
```

## Checklist Before Finalizing

- [ ] Every symbol is defined at first use
- [ ] No symbol is used for two different concepts
- [ ] Subscripts/superscripts are consistent across all sections
- [ ] Parameter domains are stated explicitly in assumptions
- [ ] Equilibrium quantities are distinguished from parameters (stars or labels)
- [ ] Empirical variable names in regressions use upright text
- [ ] Theory section symbols match appendix proof symbols exactly
