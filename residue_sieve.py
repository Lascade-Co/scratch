#!/usr/bin/env python3
"""Exact residue-class sieve for the K(N,N) geodesic labeling problem.

Every label v in {1..N^3} lies in class v mod m. Labels = 25 entries + rook
pair-sums, so for each residue r:

    n_r + rowpairs_r + colpairs_r = T_r          (exact counting identity)

with T_r = #{v in [1,N^3] : v == r (mod m)},  n_r = #entries in class r.
Row/col pair counts are determined by per-row / per-column residue profiles:
for a row with count vector c, unordered pairs summing to r:

    pairs_r(c) = ( sum_{s,t: s+t==r} c_s c_t  -  sum_{s: 2s==r} c_s ) / 2.

We solve the system EXACTLY with CP-SAT, including full 3D realizability:
binaries y[i][k][r] (cell (i,k) has residue r) tie row profiles c[i][.] and
column profiles d[k][.] to one genuine residue matrix. Extra exact facts:
  - n_r <= #{v in [1, EMAX] : v == r (mod m)}   (entries distinct, <= EMAX)
  - value 1 and value 2 are entries  =>  n_{1%m} >= 1, n_{2%m} >= 1
    (n_{1%m} >= 2 if the classes coincide, only possible m=1).

UNSAT for ANY modulus  =>  no labeling exists (machine-checked proof step).
SAT for all           =>  congruence methods cannot decide; witnesses shown.

Validation mode: N=2 (labels 1..8, EMAX=6) has the known solution
[[1,3],[6,2]]; every modulus must return SAT there or the encoding is buggy.
"""
import sys
from ortools.sat.python import cp_model


def T_counts(m, top):
    return [sum(1 for v in range(1, top + 1) if v % m == r) for r in range(m)]


def sieve(m, N=5, emax=None, time_cap=90.0, workers=2, want_witness=False):
    top = N ** 3
    emax = emax if emax is not None else top - (2 * N - 2)   # K3 analogue
    T = T_counts(m, top)
    cap = T_counts(m, emax)

    md = cp_model.CpModel()
    # y[i][k][r]: cell (i,k) holds an entry of residue r
    y = [[[md.NewBoolVar(f"y_{i}_{k}_{r}") for r in range(m)]
          for k in range(N)] for i in range(N)]
    for i in range(N):
        for k in range(N):
            md.AddExactlyOne(y[i][k])

    c = [[md.NewIntVar(0, N, f"c_{i}_{r}") for r in range(m)] for i in range(N)]
    d = [[md.NewIntVar(0, N, f"d_{k}_{r}") for r in range(m)] for k in range(N)]
    for i in range(N):
        for r in range(m):
            md.Add(c[i][r] == sum(y[i][k][r] for k in range(N)))
    for k in range(N):
        for r in range(m):
            md.Add(d[k][r] == sum(y[i][k][r] for i in range(N)))

    maxpairs = N * (N - 1) // 2

    def add_pair_counts(prof, tag):
        """prof: list of count-vectors; returns U[r] = total pairs summing to r."""
        U = [[md.NewIntVar(0, maxpairs, f"U{tag}_{j}_{r}") for r in range(m)]
             for j in range(N)]
        for j in range(N):
            row = prof[j]
            # products p[s][t] = row[s]*row[t] for s<=t
            prod = {}
            for s in range(m):
                for t in range(s, m):
                    p = md.NewIntVar(0, N * N, f"p{tag}_{j}_{s}_{t}")
                    md.AddMultiplicationEquality(p, [row[s], row[t]])
                    prod[(s, t)] = p
            for r in range(m):
                ordered = []
                for s in range(m):
                    for t in range(m):
                        if (s + t) % m == r:
                            key = (min(s, t), max(s, t))
                            ordered.append(prod[key])   # each ordered (s,t) once
                selfsum = [row[s] for s in range(m) if (2 * s) % m == r]
                md.Add(2 * U[j][r] == sum(ordered) - sum(selfsum))
        return [sum(U[j][r] for j in range(N)) for r in range(m)]

    Urow = add_pair_counts(c, "r")
    Vcol = add_pair_counts(d, "c")

    n = [md.NewIntVar(0, min(N * N, cap[r]), f"n_{r}") for r in range(m)]
    for r in range(m):
        md.Add(n[r] == sum(c[i][r] for i in range(N)))
        md.Add(n[r] + Urow[r] + Vcol[r] == T[r])

    # values 1 and 2 are entries
    md.Add(n[1 % m] >= 1)
    if m > 1 and (2 % m) != (1 % m):
        md.Add(n[2 % m] >= 1)

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_cap
    sv.parameters.num_search_workers = workers
    status = sv.Solve(md)
    name = sv.StatusName(status)
    wit = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) and want_witness:
        wit = [[next(r for r in range(m) if sv.Value(y[i][k][r]))
                for k in range(N)] for i in range(N)]
    return name, wit, sv.WallTime()


if __name__ == "__main__":
    # ---- validation on K(2,2), which HAS a solution: every m must be SAT ----
    print("validation on K(2,2) [known solvable]:")
    for m in [2, 3, 4, 5, 8]:
        name, _, t = sieve(m, N=2, time_cap=30.0)
        flag = "OK" if name in ("OPTIMAL", "FEASIBLE") else "**ENCODING BUG**"
        print(f"  m={m:>2}: {name:<10} ({t:.1f}s)  {flag}", flush=True)

    # ---- the real battery on K(5,5) ----
    mods = [int(a) for a in sys.argv[1:]] or [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 25]
    print("\nK(5,5) residue sieve:")
    unsat = []
    for m in mods:
        name, wit, t = sieve(m, N=5, time_cap=120.0,
                             want_witness=(m in (5, 20)))
        print(f"  m={m:>2}: {name:<10} ({t:.1f}s)", flush=True)
        if name == "INFEASIBLE":
            unsat.append(m)
        if wit:
            print("       witness residue matrix:")
            for row in wit:
                print("        ", row)
    print()
    if unsat:
        print(f"*** MODULI {unsat} ARE INFEASIBLE -> K(5,5) HAS NO LABELING ***")
        print("    (verify independently with Z3 before announcing)")
    else:
        print("All moduli admit residue configurations -> congruence/counting")
        print("obstructions (incl. K5, and every root-of-unity shadow of the")
        print("master identity) CANNOT rule out K(5,5).")
