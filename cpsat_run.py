#!/usr/bin/env python3
"""K(5,5) geodesic labeling via OR-Tools CP-SAT — persistent-run version.

Complete solver: exhibits a labeling (verified before printing) or proves
INFEASIBLE. Includes every proven-exact reduction:
  entries in [1,117]; sum of entries = 875; values 1,2 forced (via bijection);
  parity system K5 (#odd entries a in {9..19}, sum p_i^2 + p'_k^2 = 11a-63);
  full symmetry quotient (value 1 pinned to corner, sorted row-0/col-0,
  transpose break).

Usage:
  pip install ortools
  python3 cpsat_run.py --workers 12                # M3 Max: 12 perf cores
  python3 cpsat_run.py --workers 12 --time 7200    # optional wall cap (s)
  python3 cpsat_run.py --seed 3 --log run3.log     # vary seed across runs

Progress goes to stderr (tee it). On SAT the grid is printed and written to
solution.txt — always re-check it with verify_solution.py."""
import argparse
import sys
from ortools.sat.python import cp_model

N = 5


def build():
    m = cp_model.CpModel()
    x = [[m.NewIntVar(1, 117, f"x_{i}_{k}") for k in range(N)] for i in range(N)]

    allvals = [x[i][k] for i in range(N) for k in range(N)]
    for k in range(N):
        for i in range(N):
            for j in range(i + 1, N):
                s = m.NewIntVar(1, 125, f"col_{k}_{i}_{j}")
                m.Add(s == x[i][k] + x[j][k])
                allvals.append(s)
    for i in range(N):
        for k in range(N):
            for l in range(k + 1, N):
                s = m.NewIntVar(1, 125, f"row_{i}_{k}_{l}")
                m.Add(s == x[i][k] + x[i][l])
                allvals.append(s)
    m.AddAllDifferent(allvals)                                   # bijection
    m.Add(sum(x[i][k] for i in range(N) for k in range(N)) == 875)

    # symmetry quotient
    m.Add(x[0][0] == 1)
    for k in range(N - 1):
        m.Add(x[0][k] < x[0][k + 1])
    for i in range(N - 1):
        m.Add(x[i][0] < x[i + 1][0])
    m.Add(x[0][1] < x[1][0])

    # K5 parity system (proven exact-necessary; prunes without loss)
    o = [[m.NewBoolVar(f"o_{i}_{k}") for k in range(N)] for i in range(N)]
    for i in range(N):
        for k in range(N):
            m.AddModuloEquality(o[i][k], x[i][k], 2)
    a = m.NewIntVar(0, 25, "a")
    m.Add(a == sum(o[i][k] for i in range(N) for k in range(N)))
    m.AddAllowedAssignments([a], [[9], [11], [13], [15], [17], [19]])
    p = [m.NewIntVar(0, 5, f"p_{i}") for i in range(N)]
    pp = [m.NewIntVar(0, 5, f"pp_{k}") for k in range(N)]
    for i in range(N):
        m.Add(p[i] == sum(o[i][k] for k in range(N)))
    for k in range(N):
        m.Add(pp[k] == sum(o[i][k] for i in range(N)))
    psq = [m.NewIntVar(0, 25, f"psq_{i}") for i in range(N)]
    ppsq = [m.NewIntVar(0, 25, f"ppsq_{k}") for k in range(N)]
    for i in range(N):
        m.AddMultiplicationEquality(psq[i], [p[i], p[i]])
    for k in range(N):
        m.AddMultiplicationEquality(ppsq[k], [pp[k], pp[k]])
    m.Add(sum(psq) + sum(ppsq) == 11 * a - 63)

    return m, x, allvals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--time", type=float, default=0.0,
                    help="wall cap in seconds; 0 = run to a verdict")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", default=None,
                    help="redirect solver progress log to this file")
    args = ap.parse_args()

    m, x, allvals = build()
    sv = cp_model.CpSolver()
    sv.parameters.num_search_workers = args.workers
    sv.parameters.random_seed = args.seed
    sv.parameters.log_search_progress = True
    if args.time > 0:
        sv.parameters.max_time_in_seconds = args.time
    if args.log:
        logf = open(args.log, "w")
        sv.log_callback = lambda s: (logf.write(s + "\n"), logf.flush())

    status = sv.Solve(m)
    name = sv.StatusName(status)
    print("STATUS:", name)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        grid = [[sv.Value(x[i][k]) for k in range(N)] for i in range(N)]
        vals = sorted(sv.Value(v) for v in allvals)
        ok = vals == list(range(1, 126))
        print("SOLUTION grid (verified bijection onto 1..125:", ok, ")")
        for row in grid:
            print("  ", row)
        with open("solution.txt", "w") as f:
            f.write("\n".join(" ".join(map(str, row)) for row in grid) + "\n")
        print("written to solution.txt — re-check with verify_solution.py")
        return 0 if ok else 1
    if status == cp_model.INFEASIBLE:
        print(">>> PROVEN INFEASIBLE: no K(5,5) geodesic labeling exists.")
        print("    Cross-check with the independent SAT route (kissat) "
              "before treating this as final.")
        return 0
    print("no verdict within the time cap; rerun with more time or use the "
          "SAT route")
    return 2


if __name__ == "__main__":
    sys.exit(main())
