#!/usr/bin/env python3
"""K(5,5) geodesic labeling.

Fill a 5x5 grid X with distinct positive ints so that the 25 entries plus
the 100 rook-adjacent (same-row / same-column) pairwise sums are exactly
{1,...,125}.

Necessary conditions used:
  - each entry appears in 1 (single) + 4 (row pairs) + 4 (col pairs) = 9 windows
    => 9*S = sum(1..125) = 7875 => S = sum of entries = 875.
  - value 1 and 2 are entries (min geodesic; 2 = 1+1 impossible).
  - all 125 values distinct and in [1,125]; every rook pair-sum <= 125.

Symmetry broken (group = 5! rows x 5! cols x transpose = 28800):
  - x[0][0] = 1 (global min entry to a corner)
  - row 0 increasing across columns; column 0 increasing down rows
  - transpose fixed by x[0][1] < x[1][0]
"""
import sys

N = 5
S_TARGET = 875
VMAX = 125

g = [0]*25
used = bytearray(VMAX+1)      # used[v]=1 if value v already realized
nodes = 0
PRINT_EVERY = 20_000_000
sols = []
best_depth = 0

def future_bounds(remaining):
    """(min,max) achievable sum of `remaining` distinct unused values in [1,125]."""
    lo = 0; cnt = 0
    v = 1
    while cnt < remaining and v <= VMAX:
        if not used[v]:
            lo += v; cnt += 1
        v += 1
    if cnt < remaining: return (1, -1)   # impossible
    hi = 0; cnt = 0; v = VMAX
    while cnt < remaining and v >= 1:
        if not used[v]:
            hi += v; cnt += 1
        v -= 1
    return (lo, hi)

def recurse(t, esum):
    global nodes, best_depth
    nodes += 1
    if nodes % PRINT_EVERY == 0:
        print(f"  nodes={nodes:,}  depth-reached={best_depth}  grid={g}", flush=True)
    if t > best_depth:
        best_depth = t
    if t == 25:
        if esum == S_TARGET and all(used[1:VMAX+1]):
            sols.append(g[:]); return True
        return False
    i, k = divmod(t, N)
    lo = 1
    if i == 0 and k > 0: lo = g[t-1] + 1          # row 0 increasing
    if k == 0 and i > 0: lo = g[(i-1)*N] + 1       # col 0 increasing
    if t == 5:                                     # cell (1,0): transpose break
        lo = max(lo, g[1] + 1)
    base = i*N
    remaining_after = 24 - t
    for v in range(lo, VMAX+1):
        if used[v]:
            continue
        nesum = esum + v
        if nesum > S_TARGET:
            break                                  # v ascending -> prune rest
        adds = [v]; used[v] = 1; ok = True
        for c in range(k):                         # row neighbors
            s = v + g[base+c]
            if s > VMAX or used[s]: ok = False; break
            used[s] = 1; adds.append(s)
        if ok:
            for r in range(i):                     # col neighbors
                s = v + g[r*N+k]
                if s > VMAX or used[s]: ok = False; break
                used[s] = 1; adds.append(s)
        if ok and remaining_after:
            fmin, fmax = future_bounds(remaining_after)
            need = S_TARGET - nesum
            if fmax < 0 or need < fmin or need > fmax:
                ok = False
        if ok:
            g[t] = v
            if recurse(t+1, nesum):
                for a in adds: used[a] = 0
                return True
            g[t] = 0
        for a in adds: used[a] = 0
    return False

if __name__ == "__main__":
    g[0] = 0
    found = recurse(0, 0)
    print(f"TOTAL nodes={nodes:,}  best_depth={best_depth}")
    if sols:
        print("SOLUTION grid (row-major):")
        for r in range(N):
            print("  ", sols[0][r*N:(r+1)*N])
    else:
        print("no solution found in explored space")
