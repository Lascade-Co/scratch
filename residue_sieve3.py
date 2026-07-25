#!/usr/bin/env python3
"""Residue sieve v2 — linear channeling encoding (no quadratic products).

Same exact system as residue_sieve.py, but pair counting is done per rook
pair with a residue-sum intvar + carry, then indicator booleans:

    e[i][k] in [0,m-1]          entry residue of cell (i,k)
    s_p = e_a + e_b             for each of the 100 rook pairs p
    t[p][v] channel bools       s_p == v,  v in [0, 2m-2]
    U_r = sum_p ( t[p][r] + t[p][r+m] )

For each residue r:  n_r + U_r = T_r,  with n_r from channel bools of e.
Extra exact facts: n_r <= #{v<=EMAX: v==r}, and values 1,2 are entries.
"""
import sys
from ortools.sat.python import cp_model


def T_counts(m, top):
    return [sum(1 for v in range(1, top + 1) if v % m == r) for r in range(m)]


def sieve(m, N=5, time_cap=240.0, workers=2, want_witness=False):
    top = N ** 3
    emax = top - (2 * N - 2)
    T = T_counts(m, top)
    cap = T_counts(m, emax)

    md = cp_model.CpModel()
    # cell residue channel bools + intvar
    y = [[[md.NewBoolVar(f"y_{i}_{k}_{r}") for r in range(m)]
          for k in range(N)] for i in range(N)]
    e = [[md.NewIntVar(0, m - 1, f"e_{i}_{k}") for k in range(N)]
         for i in range(N)]
    for i in range(N):
        for k in range(N):
            md.AddExactlyOne(y[i][k])
            md.Add(e[i][k] == sum(r * y[i][k][r] for r in range(m)))

    # rook pairs
    pairs = []
    for i in range(N):
        for k in range(N):
            for l in range(k + 1, N):
                pairs.append((e[i][k], e[i][l]))
    for k in range(N):
        for i in range(N):
            for j in range(i + 1, N):
                pairs.append((e[i][k], e[j][k]))
    assert len(pairs) == 2 * N * (N * (N - 1) // 2)

    tch = []
    for p, (ea, eb) in enumerate(pairs):
        tb = [md.NewBoolVar(f"t_{p}_{v}") for v in range(2 * m - 1)]
        md.AddExactlyOne(tb)
        md.Add(ea + eb == sum(v * tb[v] for v in range(2 * m - 1)))
        tch.append(tb)

    for r in range(m):
        n_r = sum(y[i][k][r] for i in range(N) for k in range(N))
        u_terms = [tb[r] for tb in tch]
        if r + m <= 2 * m - 2:
            u_terms += [tb[r + m] for tb in tch]
        md.Add(n_r + sum(u_terms) == T[r])
        md.Add(n_r <= cap[r])

    # values 1 and 2 are entries
    md.Add(sum(y[i][k][1 % m] for i in range(N) for k in range(N)) >= 1)
    if (2 % m) != (1 % m):
        md.Add(sum(y[i][k][2 % m] for i in range(N) for k in range(N)) >= 1)

    # double-lex symmetry breaking (rows and columns each permutable):
    # encode row/col lex order via weighted keys (sound for matrix symmetry)
    Wr = []
    for i in range(N):
        w = md.NewIntVar(0, m ** N, f"Wr_{i}")
        md.Add(w == sum(e[i][k] * (m ** (N - 1 - k)) for k in range(N)))
        Wr.append(w)
    for i in range(N - 1):
        md.Add(Wr[i] <= Wr[i + 1])
    Wc = []
    for k in range(N):
        w = md.NewIntVar(0, m ** N, f"Wc_{k}")
        md.Add(w == sum(e[i][k] * (m ** (N - 1 - i)) for i in range(N)))
        Wc.append(w)
    for k in range(N - 1):
        md.Add(Wc[k] <= Wc[k + 1])

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_cap
    sv.parameters.num_search_workers = workers
    status = sv.Solve(md)
    name = sv.StatusName(status)
    wit = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) and want_witness:
        wit = [[sv.Value(e[i][k]) for k in range(N)] for i in range(N)]
    return name, wit, sv.WallTime()


if __name__ == "__main__":
    # quick re-validation on K(2,2)
    for m in [4, 8]:
        name, _, t = sieve(m, N=2, time_cap=20.0)
        print(f"validate K(2,2) m={m}: {name} ({t:.1f}s)",
              "OK" if name in ("OPTIMAL", "FEASIBLE") else "**BUG**", flush=True)

    mods = [int(a) for a in sys.argv[1:]] or [10, 12, 16, 20, 24, 25, 40]
    unsat = []
    print("\nK(5,5) residue sieve v2:")
    for m in mods:
        name, wit, t = sieve(m, N=5, want_witness=(m in (20, 25, 40)))
        print(f"  m={m:>2}: {name:<10} ({t:.1f}s)", flush=True)
        if name == "INFEASIBLE":
            unsat.append(m)
        if wit:
            for row in wit:
                print("        ", row)
    print("\nUNSAT moduli:", unsat if unsat else "none")
