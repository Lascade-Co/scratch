#!/usr/bin/env python3
"""K(5,5) geodesic labeling via OR-Tools CP-SAT.

25 entry vars x[i][k] in [1,117]; the 25 entries + 100 rook-pair-sums must be a
permutation of {1..125} (enforced by AllDifferent over 125 vars each in [1,125]).
CP-SAT can either exhibit a solution or PROVE infeasibility."""
from ortools.sat.python import cp_model

def main():
    m = cp_model.CpModel()
    N = 5
    x = [[m.NewIntVar(1, 117, f"x_{i}_{k}") for k in range(N)] for i in range(N)]

    allvals = []
    for i in range(N):
        for k in range(N):
            allvals.append(x[i][k])
    # column pair-sums (A-side 2-paths)
    for k in range(N):
        for i in range(N):
            for j in range(i+1, N):
                s = m.NewIntVar(1, 125, f"col_{k}_{i}_{j}")
                m.Add(s == x[i][k] + x[j][k])
                allvals.append(s)
    # row pair-sums (B-side 2-paths)
    for i in range(N):
        for k in range(N):
            for l in range(k+1, N):
                s = m.NewIntVar(1, 125, f"row_{i}_{k}_{l}")
                m.Add(s == x[i][k] + x[i][l])
                allvals.append(s)

    assert len(allvals) == 125
    m.AddAllDifferent(allvals)                       # => bijection onto {1..125}
    m.Add(sum(x[i][k] for i in range(N) for k in range(N)) == 875)  # K1

    # symmetry breaking
    m.Add(x[0][0] == 1)                              # value 1 to the corner
    for k in range(N-1): m.Add(x[0][k] < x[0][k+1]) # row 0 increasing
    for i in range(N-1): m.Add(x[i][0] < x[i+1][0]) # col 0 increasing
    m.Add(x[0][1] < x[1][0])                         # transpose break

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 8
    # no time limit: let it run to a definitive answer
    status = solver.Solve(m)
    print("STATUS:", solver.StatusName(status))
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("SOLUTION grid:")
        for i in range(N):
            print("  ", [solver.Value(x[i][k]) for k in range(N)])
        vals = sorted(solver.Value(v) for v in allvals)
        print("is permutation of 1..125:", vals == list(range(1, 126)))
    elif status == cp_model.INFEASIBLE:
        print(">>> PROVEN INFEASIBLE: no K(5,5) geodesic labeling exists.")

if __name__ == "__main__":
    main()
