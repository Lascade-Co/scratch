# K(5,5) geodesic labeling — solver handoff

**Task:** decide whether a 5×5 grid of 25 distinct positive integers exists
whose 25 entries plus 100 rook-adjacent pair sums (same row or same column)
are exactly {1..125}. This is equivalent to labeling the edges of K₅,₅ so its
125 geodesic path weights are exactly 1..125.

**State of knowledge:** every provable necessary condition passes and the
entire congruence/counting program yields no obstruction — see `RESULTS.md`
for all established results and metrics. The question is now purely
computational: **SAT (a grid exists) or UNSAT (provably impossible)**. Both
outcomes are mathematically interesting.

## Package contents

| file | purpose |
|---|---|
| `RESULTS.md` | everything proven so far + all metrics (read first) |
| `generate_cnf.py` | writes `k55.cnf` (42,525 vars / 1.67M clauses); `--selftest` proves the encoding end-to-end on the solvable K(2,2); `--cubes` writes 100 disjoint cube literals |
| `cpsat_run.py` | complete CP-SAT solver with all exact reductions built in |
| `decode_model.py` | SAT model → grid, with automatic verification |
| `verify_solution.py` | independent checker for any claimed grid |
| `Makefile` | one-command entry points for everything below |

## Setup (macOS / M3 Max)

```bash
brew install kissat cadical          # SAT solvers (either suffices)
pip3 install ortools                 # CP-SAT route
make test                            # MUST print SELF-TEST PASSED
```

Run `make test` before anything else: it generates the K(2,2) instance,
solves it with a built-in DPLL, decodes and verifies the known solution
[[1,3],[6,2]]. If it fails, do not trust any output of this package.

## Path A — CP-SAT (simplest; good first run)

```bash
python3 cpsat_run.py --workers 12 2> >(tee cpsat.log >&2)
```

Runs to a verdict (no time cap by default). On SAT it prints the grid,
verifies the bijection, and writes `solution.txt`. On INFEASIBLE it says so.
Progress streams to stderr. Different `--seed` values give independent
searches — running 2–3 seeds over a weekend is reasonable.

## Path B — SAT solver, single instance

```bash
python3 generate_cnf.py --n 5 -o k55.cnf
kissat k55.cnf | tee kissat.log            # or: cadical k55.cnf
```

- Exit "s SATISFIABLE": save the `v` lines to `model.txt`, then
  `python3 decode_model.py model.txt` (decodes + verifies), then
  `python3 verify_solution.py solution-grid.txt` as the final word.
- Exit "s UNSATISFIABLE": rerun with proof logging and check it:
  `kissat k55.cnf k55.drat && drat-trim k55.cnf k55.drat` (drat-trim:
  github.com/marijnheule/drat-trim). A checked DRAT proof is a real
  mathematical certificate of impossibility. Warning: the proof file can be
  tens of GB; ensure disk.

## Path C — cube & conquer (parallel + measurable ETA; recommended)

The encoding forces exactly one rook pair to produce label 125, giving 100
disjoint cubes that partition the search space:

```bash
make cubes            # k55.cnf + cubes.txt (100 unit literals)
make run-cubes J=12   # solves all 100 cubes, 12 in parallel
```

`run-cubes` appends each cube's unit clause to a copy of the CNF and runs
kissat per cube (logs in `cubes-out/`). Interpretation:
- **any cube SAT** → decode that cube's model; done (grid exists).
- **all 100 cubes UNSAT** → K(5,5) is impossible (each cube UNSAT-certifiable
  with DRAT as in Path B).
- **ETA:** after the first batch, remaining ≈ median cube time × cubes left /
  12. If early cubes take hours each, stop and reassess — that is the signal
  this needs either the pro tooling below or a bigger machine.

Pro option: `march_cu` (github.com/marijnheule/CnC) generates thousands of
dynamically-chosen cubes for better balance; use it if the fixed 100 cubes
are lopsided.

## Trust rules

1. Never accept a grid that has not passed `verify_solution.py`.
2. Never accept UNSAT from a single solver alone: either check a DRAT proof
   (Path B) or reproduce with the other engine (CP-SAT vs kissat/cadical).
3. The two engines here are fully independent implementations of the same
   documented model — agreement between them is strong evidence.

## Reporting back

Whichever outcome: report the verdict, the wall time, the solver + version,
and (SAT) the verified grid or (UNSAT) the proof-check log. The full
investigation that led here — C₁₀ impossibility, the K(m,m) family analysis,
parity/moment/residue programs — is in this branch's git history.
