#!/usr/bin/env python3
"""DIMACS CNF generator for the K(N,N) geodesic labeling problem.

Problem (N=5): fill a 5x5 grid with 25 distinct positive integers so that the
25 entries plus the 100 rook-adjacent pair sums (same row or same column) are
exactly {1..125}. SAT = a labeling exists; UNSAT = provably impossible.

Encoding (documented so any model can be decoded independently):
  emax = N^3 - (2N-2)          proven upper bound on any entry (117 for N=5)
  top  = N^3                   number of labels (125 for N=5)
  cells c = N*i + k            row-major, 0-based
  X[c][v] = c*emax + v         cell c holds value v (v in 1..emax)   [1-based]
  Z[p][s] = N^2*emax + p*(top-2) + (s-2)
                               rook pair p has sum s (s in 3..top)
  pairs p: first all same-row pairs (i asc, then k<l), then all same-column
           pairs (k asc, then i<j)
  auxiliary sequential-AMO variables follow after all Z variables.

Clauses:
  - each cell exactly one value (ALO + pairwise AMO)
  - channeling: X[A][a] & X[B][b] -> Z[p][a+b]   (or blocked if a+b > top)
  - each pair at most one sum (sequential AMO; the true sum is forced by
    channeling, so ALO is implied)
  - each label L in 1..top produced exactly once, producers being the entry
    variables (L <= emax) and the pair-sum variables (L >= 3). This single
    family encodes: distinct entries, distinct sums, bijection onto {1..top},
    values 1 and 2 forced to be entries, labels > emax forced to be sums.
  - symmetry breaking: value 1 fixed at cell (0,0); column-0 entries
    increasing down; row-0 entries increasing right; val(0,1) < val(1,0)
    kills the transpose. (Sound: proven that value 1 is always an entry.)

--selftest generates the K(2,2) instance (known solvable, solution
[[1,3],[6,2]]), solves it with a built-in DPLL, decodes and verifies the
labeling end-to-end. Run this once on the target machine before trusting
k55.cnf.
"""
import argparse
import sys


def build(N):
    top = N ** 3
    emax = top - (2 * N - 2)
    ncells = N * N

    def cell(i, k):
        return N * i + k

    def X(c, v):
        return c * emax + v

    pairs = []
    for i in range(N):
        for k in range(N):
            for l in range(k + 1, N):
                pairs.append((cell(i, k), cell(i, l)))
    for k in range(N):
        for i in range(N):
            for j in range(i + 1, N):
                pairs.append((cell(i, k), cell(j, k)))
    npairs = len(pairs)
    zbase = ncells * emax

    def Z(p, s):
        return zbase + p * (top - 2) + (s - 2)

    nv = [zbase + npairs * (top - 2)]      # running variable counter

    def newvar():
        nv[0] += 1
        return nv[0]

    cls = []

    def seq_amo(lits):
        """sequential at-most-one; ~3n clauses, n-1 aux vars"""
        n = len(lits)
        if n <= 1:
            return
        if n <= 4:                          # pairwise cheaper for tiny sets
            for a in range(n):
                for b in range(a + 1, n):
                    cls.append((-lits[a], -lits[b]))
            return
        r = [newvar() for _ in range(n - 1)]
        cls.append((-lits[0], r[0]))
        for idx in range(1, n - 1):
            cls.append((-lits[idx], r[idx]))
            cls.append((-r[idx - 1], r[idx]))
            cls.append((-lits[idx], -r[idx - 1]))
        cls.append((-lits[n - 1], -r[n - 2]))

    # 1) one value per cell
    for c in range(ncells):
        cls.append(tuple(X(c, v) for v in range(1, emax + 1)))
        for v in range(1, emax + 1):
            for w in range(v + 1, emax + 1):
                cls.append((-X(c, v), -X(c, w)))

    # 2) channeling / blocking
    for p, (A, B) in enumerate(pairs):
        for a in range(1, emax + 1):
            for b in range(1, emax + 1):
                s = a + b
                if s > top:
                    cls.append((-X(A, a), -X(B, b)))
                else:
                    cls.append((-X(A, a), -X(B, b), Z(p, s)))

    # 3) at most one sum per pair
    for p in range(npairs):
        seq_amo([Z(p, s) for s in range(3, top + 1)])

    # 4) each label produced exactly once
    for L in range(1, top + 1):
        producers = []
        if L <= emax:
            producers += [X(c, L) for c in range(ncells)]
        if L >= 3:
            producers += [Z(p, L) for p in range(npairs)]
        cls.append(tuple(producers))
        seq_amo(producers)

    # 5) symmetry breaking
    cls.append((X(cell(0, 0), 1),))
    def less_than(cA, cB):                  # val(cA) < val(cB)
        for a in range(1, emax + 1):
            for b in range(1, a):           # forbid a > b
                cls.append((-X(cA, a), -X(cB, b)))
    for i in range(1, N - 1):
        less_than(cell(i, 0), cell(i + 1, 0))
    for k in range(1, N - 1):
        less_than(cell(0, k), cell(0, k + 1))
    if N >= 2:
        less_than(cell(0, 1), cell(1, 0))

    return cls, nv[0], {"N": N, "top": top, "emax": emax,
                        "ncells": ncells, "npairs": npairs, "zbase": zbase}


def write_dimacs(cls, nvars, meta, path):
    with open(path, "w") as f:
        f.write(f"c K({meta['N']},{meta['N']}) geodesic labeling; "
                f"X[c][v]=c*{meta['emax']}+v; "
                f"Z[p][s]={meta['zbase']}+p*{meta['top']-2}+(s-2)\n")
        f.write(f"p cnf {nvars} {len(cls)}\n")
        f.write("".join(" ".join(map(str, cl)) + " 0\n" for cl in cls))


# ---------------- built-in DPLL (for the K(2,2) self-test only) -------------
def dpll(nvars, clauses):
    clauses = [list(c) for c in clauses]
    assign = {}

    def value(lit):
        v = assign.get(abs(lit))
        if v is None:
            return None
        return v if lit > 0 else not v

    def propagate():
        changed = True
        while changed:
            changed = False
            for cl in clauses:
                unassigned, sat = [], False
                for lit in cl:
                    val = value(lit)
                    if val is True:
                        sat = True
                        break
                    if val is None:
                        unassigned.append(lit)
                if sat:
                    continue
                if not unassigned:
                    return False
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    assign[abs(lit)] = lit > 0
                    changed = True
        return True

    def rec():
        if not propagate():
            return False
        for v in range(1, nvars + 1):
            if v not in assign:
                snapshot = dict(assign)
                assign[v] = True
                if rec():
                    return True
                assign.clear()
                assign.update(snapshot)
                assign[v] = False
                if rec():
                    return True
                assign.clear()
                assign.update(snapshot)
                return False
        return True

    return assign if rec() else None


def decode(assign, meta):
    N, emax = meta["N"], meta["emax"]
    grid = [[None] * N for _ in range(N)]
    for i in range(N):
        for k in range(N):
            c = N * i + k
            for v in range(1, emax + 1):
                if assign.get(c * emax + v):
                    grid[i][k] = v
    return grid


def labels_of(grid):
    N = len(grid)
    vals = [grid[i][k] for i in range(N) for k in range(N)]
    for i in range(N):
        for k in range(N):
            for l in range(k + 1, N):
                vals.append(grid[i][k] + grid[i][l])
    for k in range(N):
        for i in range(N):
            for j in range(i + 1, N):
                vals.append(grid[i][k] + grid[j][k])
    return sorted(vals)


def selftest():
    cls, nvars, meta = build(2)
    print(f"K(2,2) CNF: {nvars} vars, {len(cls)} clauses; solving with "
          f"built-in DPLL...")
    assign = dpll(nvars, cls)
    if assign is None:
        print("SELF-TEST FAILED: K(2,2) came back UNSAT but [[1,3],[6,2]] "
              "solves it — the encoding is broken. DO NOT use k55.cnf.")
        return 1
    grid = decode(assign, meta)
    ok = labels_of(grid) == list(range(1, 9))
    print(f"decoded grid: {grid}  labels==1..8: {ok}")
    if not ok:
        print("SELF-TEST FAILED: decoded grid invalid. DO NOT use k55.cnf.")
        return 1
    print("SELF-TEST PASSED: encoding verified end-to-end on K(2,2).")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--cubes", action="store_true",
                    help="also write cubes.txt: one unit literal per line, "
                         "cube c = 'rook pair p produces label top' "
                         "(exhaustive & disjoint given the encoding)")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    out = a.out or f"k{a.n}{a.n}.cnf"
    cls, nvars, meta = build(a.n)
    write_dimacs(cls, nvars, meta, out)
    print(f"wrote {out}: {nvars} vars, {len(cls)} clauses "
          f"(emax={meta['emax']}, pairs={meta['npairs']})")
    if a.cubes:
        top, zbase, npairs = meta["top"], meta["zbase"], meta["npairs"]
        with open("cubes.txt", "w") as f:
            for p in range(npairs):
                f.write(f"{zbase + p * (top - 2) + (top - 2)}\n")
        print(f"wrote cubes.txt: {npairs} unit literals "
              f"(Z[p][{top}] for each rook pair p). Every model has exactly "
              f"one true — the cubes partition the search space.")
