#!/usr/bin/env python3
"""Parity / counting feasibility for K(5,5) geodesic labeling.

Let a = number of ODD entries among the 25 cells.  With p_i = #odd in row i,
p'_k = #odd in col k (both partitions of a into 5 parts, each 0..5), a pair-sum
is odd iff its two cells differ in parity, so #odd pair-sums = sum_i p_i(5-p_i)
+ sum_k p'_k(5-p'_k).  {1..125} has 63 odd values, a of which are entries, so:

    #odd pair-sums = 63 - a
    =>  sum_i p_i^2 + sum_k p'_k^2 = 11a - 63.          (P)

We test, for each a, whether (P) is satisfiable by two 5-part square-sums that
are ALSO jointly realizable as a 0/1 (odd-indicator) matrix (Gale-Ryser).
"""
from itertools import product

def compositions(a):
    """all (p0..p4), each 0..5, summing to a."""
    for c in product(range(6), repeat=5):
        if sum(c) == a:
            yield c

def gale_ryser(rows, cols):
    """Does a 0/1 matrix with given row sums and col sums exist?"""
    if sum(rows) != sum(cols):
        return False
    r = sorted(rows, reverse=True)
    n = len(cols)
    for k in range(1, len(r) + 1):
        lhs = sum(r[:k])
        rhs = sum(min(c, k) for c in cols)
        if lhs > rhs:
            return False
    return True

print("a  target(11a-63)  achievable?  #(row,col) parity patterns  sample")
survivors = []
for a in range(1, 26):
    if a % 2 == 0:
        continue                      # (P) forces a odd
    target = 11 * a - 63
    if target < 0:
        continue
    comps = list(compositions(a))
    sq = {}                            # square-sum -> list of comps
    for c in comps:
        s = sum(x * x for x in c)
        sq.setdefault(s, []).append(c)
    # find q1+q2 = target with a realizable 0/1 matrix
    ok_count = 0
    sample = None
    keys = sorted(sq)
    for q1 in keys:
        q2 = target - q1
        if q2 in sq:
            for rp in sq[q1]:
                for cp in sq[q2]:
                    if gale_ryser(rp, cp):
                        ok_count += 1
                        if sample is None:
                            sample = (rp, cp)
    tag = "YES" if ok_count else "no"
    if ok_count:
        survivors.append(a)
    print(f"{a:>2}  {target:>12}   {tag:>10}   {ok_count:>6}   {sample}")

print("\nParity-feasible odd-entry counts a:", survivors)
print("=> parity alone does NOT rule K(5,5) out; it constrains a to", survivors)
