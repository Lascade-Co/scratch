#!/usr/bin/env python3
"""Independent confirmation with Z3: does a valid C_10 labeling exist?

Model: w[0..9] >= 1 integers. The 50 cyclic windows of length 1..5 must be
50 distinct integers each in [1,50] -> exactly a permutation of {1..50}.
"""
from z3 import Int, Solver, Distinct, And, sat

N = 10
w = [Int(f"w{i}") for i in range(N)]
s = Solver()

for i in range(N):
    s.add(w[i] >= 1)

sums = []
for L in range(1, 6):
    for start in range(N):
        expr = sum(w[(start + k) % N] for k in range(L))
        sums.append(expr)

# 50 sums, each in [1,50], all distinct  <=>  permutation of 1..50
for e in sums:
    s.add(And(e >= 1, e <= 50))
s.add(Distinct(*sums))
s.add(sum(w) == 85)  # implied, speeds things up

# fix rotational symmetry: value 1 is a single edge, put it at position 0
s.add(w[0] == 1)

print("solving...")
res = s.check()
print("result:", res)
if res == sat:
    m = s.model()
    weights = [m[w[i]].as_long() for i in range(N)]
    print("edge weights:", weights)
    vals = sorted(sum(weights[(st + k) % N] for k in range(L))
                  for L in range(1, 6) for st in range(N))
    print("geodesic set == {1..50}:", vals == list(range(1, 51)))
else:
    print("UNSAT: no labeling exists for C_10 under these requirements.")
