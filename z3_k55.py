#!/usr/bin/env python3
"""Independent Z3/SMT cross-check for K(5,5) geodesic labeling.
Different solver technology from CP-SAT; corroborates SAT/UNSAT verdicts."""
from z3 import Int, Solver, Distinct, Sum, sat, unsat

N = 5
x = [[Int(f"x_{i}_{k}") for k in range(N)] for i in range(N)]
s = Solver()
s.set("timeout", 2_600_000)   # ~43 min wall cap (ms)

for i in range(N):
    for k in range(N):
        s.add(x[i][k] >= 1, x[i][k] <= 117)

vals = [x[i][k] for i in range(N) for k in range(N)]
for k in range(N):
    for i in range(N):
        for j in range(i+1, N):
            vals.append(x[i][k] + x[j][k])
for i in range(N):
    for k in range(N):
        for l in range(k+1, N):
            vals.append(x[i][k] + x[i][l])
assert len(vals) == 125

for v in vals:
    s.add(v >= 1, v <= 125)
s.add(Distinct(vals))
s.add(Sum([x[i][k] for i in range(N) for k in range(N)]) == 875)

# symmetry breaking (same as CP-SAT)
s.add(x[0][0] == 1)
for k in range(N-1): s.add(x[0][k] < x[0][k+1])
for i in range(N-1): s.add(x[i][0] < x[i+1][0])
s.add(x[0][1] < x[1][0])

print("z3 solving K(5,5)...", flush=True)
res = s.check()
print("Z3 RESULT:", res, flush=True)
if res == sat:
    mdl = s.model()
    print("SOLUTION grid:")
    for i in range(N):
        print("  ", [mdl.evaluate(x[i][k]).as_long() for k in range(N)])
elif res == unsat:
    print(">>> Z3: PROVEN INFEASIBLE — no K(5,5) labeling exists.")
else:
    print("(z3 returned unknown — hit time cap)")
