#!/usr/bin/env python3
"""Combined parity + mod-4 sum-of-squares feasibility for K(5,5).

A parity configuration is (p, p') = (row odd-counts, col odd-counts), each a
composition of a into 5 parts (0..5). Necessary conditions:

  (P)  sum p_i^2 + sum p'_k^2 = 11a - 63                 [parity of #odd values]
  (R)  rho_R = #odd(p) is odd,  rho_C = #odd(p') is odd  [row/col sums = 875 odd]
  (G)  a 0/1 matrix with margins (p, p') exists          [Gale-Ryser]
  (M4) 3a + rho_R + rho_C = 3  (mod 4)                   [sum-of-squares mod 4]

If NO (a,p,p') survives all four, K(5,5) is impossible. Otherwise the moment
approach is insufficient and the question rests on search.
"""
from itertools import product

def comps(a):
    return [c for c in product(range(6), repeat=5) if sum(c) == a]

def gale_ryser(rows, cols):
    if sum(rows) != sum(cols): return False
    r = sorted(rows, reverse=True)
    for k in range(1, len(r)+1):
        if sum(r[:k]) > sum(min(c, k) for c in cols):
            return False
    return True

odd = lambda c: sum(1 for x in c if x % 2)

survivors = {}
for a in range(1, 26):
    target = 11*a - 63
    if target < 0: continue
    cs = comps(a)
    by_sq = {}
    for c in cs:
        by_sq.setdefault(sum(x*x for x in c), []).append(c)
    found = 0
    example = None
    for q1, group1 in by_sq.items():
        q2 = target - q1
        if q2 not in by_sq: continue
        for p in group1:
            rR = odd(p)
            if rR % 2 == 0: continue                 # (R)
            for pp in by_sq[q2]:
                rC = odd(pp)
                if rC % 2 == 0: continue             # (R)
                if (3*a + rR + rC) % 4 != 3: continue  # (M4)
                if not gale_ryser(p, pp): continue     # (G)
                found += 1
                if example is None:
                    example = (p, pp, rR, rC)
    if found:
        survivors[a] = (found, example)

print("a  : survivors after (P)+(R)+(G)+(M4)")
for a in sorted(survivors):
    n, ex = survivors[a]
    print(f"{a:>2} : {n:>6}   example rows={ex[0]} cols={ex[1]} "
          f"(rho_R={ex[2]}, rho_C={ex[3]})")

if not survivors:
    print("\n*** NO parity configuration survives -> K(5,5) IMPOSSIBLE (proof) ***")
else:
    print(f"\nSurviving a values: {sorted(survivors)}")
    print("=> parity + mod-4 sum-of-squares is NOT sufficient to rule out K(5,5).")
