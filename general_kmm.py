#!/usr/bin/env python3
"""General complete bipartite K(m,m) geodesic labeling.

m x m grid; geodesics = entries (m^2) + rook-pair-sums (m^2(m-1)); total M=m^3.
Each entry is in 2m-1 geodesics => (2m-1)*S = M(M+1)/2, M=m^3.
=> S = m^3(m^3+1) / (2(2m-1)).   Integer required.
"""
from fractions import Fraction
from itertools import permutations

def info(m):
    M = m**3
    tot = M*(M+1)//2
    cov = 2*m - 1
    S = Fraction(tot, cov)
    return M, tot, cov, S, (S.denominator == 1)

print("K(m,m): m  M=m^3  sum(1..M)  cover(2m-1)  S=sum/cover  integer?")
for m in range(2, 16):
    M, tot, cov, S, integral = info(m)
    print(f"        {m:>2} {M:>6} {tot:>10} {cov:>6}   "
          f"{(str(int(S)) if integral else format(float(S),'.3f')):>12}  "
          f"{'YES' if integral else 'no'}")

# --- exhaustive solve for tiny integral cases (m=2) ---
def solve_kmm(m):
    M = m**3
    _, _, _, S, integral = info(m)
    if not integral:
        return None, "fails integrality"
    S = int(S)
    cells = m*m
    g = [0]*cells
    used = bytearray(M+1)
    sols = []
    def rec(t, esum):
        if t == cells:
            if esum == S and all(used[1:M+1]):
                sols.append(g[:]); return True
            return False
        i, k = divmod(t, m)
        lo = 1
        if i == 0 and k > 0: lo = g[t-1]+1
        if k == 0 and i > 0: lo = g[(i-1)*m]+1
        if t == m and m >= 2: lo = max(lo, g[1]+1)   # transpose break
        for v in range(lo, M+1):
            if used[v]: continue
            if esum+v > S: break
            adds=[v]; used[v]=1; ok=True
            for c in range(k):
                s=v+g[i*m+c]
                if s>M or used[s]: ok=False;break
                used[s]=1; adds.append(s)
            if ok:
                for r in range(i):
                    s=v+g[r*m+k]
                    if s>M or used[s]: ok=False;break
                    used[s]=1; adds.append(s)
            if ok:
                g[t]=v
                if rec(t+1, esum+v):
                    for a in adds: used[a]=0
                    return True
                g[t]=0
            for a in adds: used[a]=0
        return False
    rec(0,0)
    return sols, f"S={S}"

for m in [2, 3, 4]:
    sols, note = solve_kmm(m) if info(m)[4] else (None, "fails integrality")
    if sols is None:
        print(f"\nK({m},{m}): {note} -> NO SOLUTION")
    elif sols:
        print(f"\nK({m},{m}): {note} -> SOLUTION grid:")
        for r in range(m):
            print("   ", sols[0][r*m:(r+1)*m])
    else:
        print(f"\nK({m},{m}): {note} -> no solution exists")
