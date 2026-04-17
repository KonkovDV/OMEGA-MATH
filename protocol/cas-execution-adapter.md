# OMEGA CAS Execution Adapter (Computer Algebra System)

Defines the contract for symbolic computation from the OMEGA Python runtime.

## Purpose

The CAS adapter wraps SymPy (primary, pip-installable) and optionally SageMath
(subprocess) to provide algebra, calculus, number theory, and combinatorics
capabilities for OMEGA research problems.

## SOTA Grounding (April 2026)

- **SymPy** (sympy/sympy): v1.13+ (Python-native CAS). Covers symbolic algebra,
  calculus, number theory, combinatorics, polynomial manipulation, Diophantine
  equations, group theory, special functions. 13k+ stars, actively maintained.
- **SageMath** (sagemath/sage): Full-featured CAS including PARI/GP, GAP, Singular,
  FLINT backends. More powerful but requires external installation. The adapter
  supports SageMath via subprocess calls.
- **MCP-Solver pattern** (arXiv:2501.00539): The interactive model-edit + solve
  pattern applies here — CAS queries are built incrementally and validated.

## Adapter Contract

### Input: `CASRequest`

```yaml
action: "simplify | solve | series | factor | integrate | differentiate | evaluate | custom"
expression: "<SymPy expression string>"
variable: "x"                # for operations that need a variable
assumptions: {}              # e.g., {positive: true, integer: true}
timeout_seconds: 30
backend: "sympy | sage"      # default: sympy
```

### Output: `CASResult`

```yaml
success: true | false
action: "<echoed action>"
backend: "sympy | sage"
result: "<string representation of result>"
latex: "<LaTeX representation, if available>"
duration_seconds: 0.05
error: null
```

## Supported Actions

### `simplify`
Simplify an expression: `simplify(expr)`.

### `solve`
Solve an equation or system: `solve(expr, var)`.

### `series`
Taylor/Laurent series expansion: `series(expr, var, point, order)`.

### `factor`
Factor a polynomial or integer: `factor(expr)`.

### `integrate`
Symbolic integration: `integrate(expr, var)` or definite `integrate(expr, (var, a, b))`.

### `differentiate`
Symbolic differentiation: `diff(expr, var)`.

### `evaluate`
Numerical evaluation: `N(expr, precision)`.

### `custom`
Execute arbitrary SymPy code in a sandboxed namespace. Same security restrictions
as the solver adapter.

## Security Considerations

For `custom` action, the execution namespace is restricted to SymPy symbols only.
No `import`, `exec`, `eval`, `open`, `os`, or `subprocess` calls are permitted.

## Integration Points

- **Experimentalist agent**: symbolic verification of conjectures, series analysis,
  factorization for number-theory problems.
- **Prover agent**: CAS-assisted proof steps (e.g., verifying algebraic identities
  that feed into formal proofs).
- **Writer agent**: LaTeX rendering of symbolic results for publications.
