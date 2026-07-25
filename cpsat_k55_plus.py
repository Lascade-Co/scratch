#!/usr/bin/env python3
"""K(5,5) geodesic labeling via CP-SAT, WITH derived constraints added as
redundant (exact necessary) conditions to accelerate the solver:

  K1  sum of entries = 875
  K3  entries in [1,117]  (domain)
  K5  parity: #odd entries a in {9,11,13,15,17,19}
             and  sum p_i^2 + sum p'_k^2 = 11a - 63   (p=row/col odd-counts)
  K6  sum-of-squares identity: 7*Q + sum R_i^2 + sum C_k^2 = 658875
      (Q=sum x^2, R=row sums, C=col sums)

None of these removes a valid labeling; they only prune the search."""
from ortools.sat.python import cp_model

N = 5
def main():
    m = cp_model.CpModel()
    x = [[m.NewIntVar(1, 117, f"x_{i}_{k}") for k in range(N)] for i in range(N)]

    allvals = [x[i][k] for i in range(N) for k in range(N)]
    for k in range(N):
        for i in range(N):
            for j in range(i+1, N):
                s = m.NewIntVar(1, 125, f"col_{k}_{i}_{j}")
                m.Add(s == x[i][k] + x[j][k]); allvals.append(s)
    for i in range(N):
        for k in range(N):
            for l in range(k+1, N):
                s = m.NewIntVar(1, 125, f"row_{i}_{k}_{l}")
                m.Add(s == x[i][k] + x[i][l]); allvals.append(s)
    assert len(allvals) == 125
    m.AddAllDifferent(allvals)

    # K1
    m.Add(sum(x[i][k] for i in range(N) for k in range(N)) == 875)

    # symmetry breaking
    m.Add(x[0][0] == 1)
    for k in range(N-1): m.Add(x[0][k] < x[0][k+1])
    for i in range(N-1): m.Add(x[i][0] < x[i+1][0])
    m.Add(x[0][1] < x[1][0])

    # ---- K6: 7*Q + sum R^2 + sum C^2 = 658875 ----
    xsq = [[m.NewIntVar(1, 117*117, f"xsq_{i}_{k}") for k in range(N)] for i in range(N)]
    for i in range(N):
        for k in range(N):
            m.AddMultiplicationEquality(xsq[i][k], [x[i][k], x[i][k]])
    Q = m.NewIntVar(1, 25*117*117, "Q")
    m.Add(Q == sum(xsq[i][k] for i in range(N) for k in range(N)))
    R = [m.NewIntVar(15, 875, f"R_{i}") for i in range(N)]
    C = [m.NewIntVar(15, 875, f"C_{k}") for k in range(N)]
    for i in range(N): m.Add(R[i] == sum(x[i][k] for k in range(N)))
    for k in range(N): m.Add(C[k] == sum(x[i][k] for i in range(N)))
    Rsq = [m.NewIntVar(225, 875*875, f"Rsq_{i}") for i in range(N)]
    Csq = [m.NewIntVar(225, 875*875, f"Csq_{k}") for k in range(N)]
    for i in range(N): m.AddMultiplicationEquality(Rsq[i], [R[i], R[i]])
    for k in range(N): m.AddMultiplicationEquality(Csq[k], [C[k], C[k]])
    m.Add(7*Q + sum(Rsq) + sum(Csq) == 658875)

    # ---- K5: parity ----
    o = [[m.NewBoolVar(f"o_{i}_{k}") for k in range(N)] for i in range(N)]
    for i in range(N):
        for k in range(N):
            m.AddModuloEquality(o[i][k], x[i][k], 2)   # o = x mod 2 (1 if odd)
    a = m.NewIntVar(0, 25, "a")
    m.Add(a == sum(o[i][k] for i in range(N) for k in range(N)))
    m.AddAllowedAssignments([a], [[9],[11],[13],[15],[17],[19]])
    p  = [m.NewIntVar(0, 5, f"p_{i}")  for i in range(N)]
    pp = [m.NewIntVar(0, 5, f"pp_{k}") for k in range(N)]
    for i in range(N): m.Add(p[i]  == sum(o[i][k] for k in range(N)))
    for k in range(N): m.Add(pp[k] == sum(o[i][k] for i in range(N)))
    psq  = [m.NewIntVar(0, 25, f"psq_{i}")  for i in range(N)]
    ppsq = [m.NewIntVar(0, 25, f"ppsq_{k}") for k in range(N)]
    for i in range(N): m.AddMultiplicationEquality(psq[i],  [p[i],  p[i]])
    for k in range(N): m.AddMultiplicationEquality(ppsq[k], [pp[k], pp[k]])
    m.Add(sum(psq) + sum(ppsq) == 11*a - 63)

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = 3000.0
    status = solver.Solve(m)
    print("STATUS:", solver.StatusName(status))
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("SOLUTION grid:")
        for i in range(N):
            print("  ", [solver.Value(x[i][k]) for k in range(N)])
        vals = sorted(solver.Value(v) for v in allvals)
        print("permutation of 1..125:", vals == list(range(1, 126)))
    elif status == cp_model.INFEASIBLE:
        print(">>> PROVEN INFEASIBLE: no K(5,5) geodesic labeling exists.")
    else:
        print("(no verdict within time cap)")

if __name__ == "__main__":
    main()
