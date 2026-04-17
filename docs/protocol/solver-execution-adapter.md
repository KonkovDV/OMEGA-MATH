# OMEGA Solver Execution Adapter (SAT/SMT)

Defines the contract for programmatic SAT and SMT solving from the OMEGA Python runtime.

## Purpose

The solver adapter wraps Z3 (primary) and optionally PySAT to provide structured
constraint-solving capabilities for OMEGA problems in number theory, combinatorics,
and graph theory domains.

## SOTA Grounding (April 2026)

- **MCP-Solver** (szeider/mcp-solver, arXiv:2501.00539, SAT 2025): MCP server bridging
  LLMs with MiniZinc, PySAT, MaxSAT, Z3, and Clingo ASP. Key pattern: interactive
  model-edit + solve loop with iterated validation. Published at SAT 2025 (LIPIcs).
  The OMEGA adapter adopts the same structured input/output contract but uses Z3's
  Python bindings directly instead of the MCP process layer.
- **Z3** (z3prover/z3): Production SMT solver supporting integers, reals, bitvectors,
  arrays, quantifiers, and optimization. Python bindings via `z3-solver` pip package.
- **PySAT** (pysathq/pysat): SAT/MaxSAT toolkit with multiple solver backends
  (Glucose, Lingeling, etc.). Cardinality constraints, CNF generation, model enumeration.

## Adapter Contract

### Input: `SolverRequest`

```yaml
backend: "z3 | pysat"
mode: "sat | smt | optimize"
spec: "<solver specification — see below>"
timeout_seconds: 60
```

### Z3 Spec (mode: smt | optimize)

Pass a Python code string that builds Z3 expressions. The adapter executes it in a
sandboxed namespace with `z3` pre-imported:

```yaml
spec: |
  x = Int('x')
  y = Int('y')
  solver.add(x + y == 10)
  solver.add(x > 0, y > 0)
```

### PySAT Spec (mode: sat)

Pass a list of clauses in DIMACS-like format:

```yaml
spec:
  num_vars: 4
  clauses: [[1, 2], [-1, 3], [-2, -3, 4]]
```

### Output: `SolverResult`

```yaml
success: true | false
backend: "z3 | pysat"
mode: "sat | smt | optimize"
satisfiable: true | false | null
model: {}           # variable → value mapping if SAT
objective: null     # optimization result if applicable
duration_seconds: 0.05
error: null         # error message if failed
```

## Security Considerations

The Z3 spec is executed as Python code. The adapter restricts the execution namespace
to Z3 symbols only, preventing arbitrary code execution. No `import`, `exec`, `eval`,
`open`, `os`, or `subprocess` calls are permitted in spec strings.

## Integration Points

- **Experimentalist agent**: uses SAT/SMT solving for bounded verification,
  counterexample search, and constraint enumeration.
- **omega-runner**: `experiment-first` runs invoke the solver adapter and record
  results as experiment artifacts.
- **Triage matrix**: T1-computational and T2-experimental problems can leverage
  SAT/SMT as the primary attack route.
