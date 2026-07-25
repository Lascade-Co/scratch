#!/usr/bin/env python3
"""Count-level residue sieve (v4) — the pure necessary condition, no
realizability layer, so models are small and decidable.

Variables: row profiles c[i][r] (0..5, each row sums to 5) and column
profiles d[k][r], sharing entry-class counts n_r. Pair counts from profile
products. If this count system is INFEASIBLE for any m, K(5,5) is impossible.
Rows and columns are exchangeable at count level -> sort both by weighted key.
"""
import sys
from ortools.sat.python import cp_model


def T_counts(m, top):
    return [sum(1 for v in range(1, top + 1) if v % m == r) for r in range(m)]


def count_sieve(m, N=5, time_cap=300.0, workers=4):
    top = N ** 3
    emax = top - (2 * N - 2)
    T = T_counts(m, top)
    cap = T_counts(m, emax)
    maxpairs = N * (N - 1) // 2

    md = cp_model.CpModel()

    def make_side(tag):
        prof = [[md.NewIntVar(0, N, f"{tag}_{j}_{r}") for r in range(m)]
                for j in range(N)]
        for j in range(N):
            md.Add(sum(prof[j]) == N)
        # pair-count totals per residue
        U = []
        prods = []
        for j in range(N):
            row = prof[j]
            pr = {}
            for s in range(m):
                for t in range(s, m):
                    p = md.NewIntVar(0, N * N, f"p{tag}_{j}_{s}_{t}")
                    md.AddMultiplicationEquality(p, [row[s], row[t]])
                    pr[(s, t)] = p
            prods.append(pr)
        for r in range(m):
            terms = []
            for j in range(N):
                ordered = []
                for s in range(m):
                    t = (r - s) % m
                    key = (min(s, t), max(s, t))
                    ordered.append(prods[j][key])
                selfs = [prof[j][s] for s in range(m) if (2 * s) % m == r]
                u = md.NewIntVar(0, maxpairs, f"U{tag}_{j}_{r}")
                md.Add(2 * u == sum(ordered) - sum(selfs))
                terms.append(u)
            U.append(sum(terms))
        # sort rows by weighted prefix key (sound symmetry break)
        pref = min(m, 8)
        keys = []
        for j in range(N):
            w = md.NewIntVar(0, 6 ** pref, f"K{tag}_{j}")
            md.Add(w == sum(prof[j][r] * (6 ** (pref - 1 - r))
                            for r in range(pref)))
            keys.append(w)
        for j in range(N - 1):
            md.Add(keys[j] <= keys[j + 1])
        return prof, U

    c, Urow = make_side("r")
    d, Vcol = make_side("c")

    for r in range(m):
        n_r = sum(c[i][r] for i in range(N))
        md.Add(n_r == sum(d[k][r] for k in range(N)))     # shared marginals
        md.Add(n_r + Urow[r] + Vcol[r] == T[r])
        md.Add(n_r <= cap[r])
    md.Add(sum(c[i][1 % m] for i in range(N)) >= 1)
    if (2 % m) != (1 % m):
        md.Add(sum(c[i][2 % m] for i in range(N)) >= 1)

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_cap
    sv.parameters.num_search_workers = workers
    status = sv.Solve(md)
    return sv.StatusName(status), sv.WallTime()


if __name__ == "__main__":
    # validation: K(2,2) must be SAT for all m
    for m in [4, 10]:
        name, t = count_sieve(m, N=2, time_cap=20.0)
        print(f"validate K(2,2) m={m}: {name} ({t:.1f}s)",
              "OK" if name in ("OPTIMAL", "FEASIBLE") else "**BUG**", flush=True)
    mods = [int(a) for a in sys.argv[1:]] or [10, 12, 16, 20]
    print("\nK(5,5) count-level sieve:")
    unsat = []
    for m in mods:
        name, t = count_sieve(m, N=5)
        print(f"  m={m:>2}: {name:<10} ({t:.1f}s)", flush=True)
        if name == "INFEASIBLE":
            unsat.append(m)
    print("\nUNSAT moduli:", unsat if unsat else "none")
