#!/usr/bin/env python3
"""Decode a SAT solver model into the K(N,N) grid and verify it.

Usage: python3 decode_model.py <solver-output-file> [--n 5]

Accepts kissat/cadical output: lines starting with 'v ' listing literals
(also tolerates a bare list of literals). Uses the variable numbering
documented in generate_cnf.py: X[c][v] = c*emax + v, cells row-major,
emax = N^3 - (2N-2). Prints the grid and runs the full verification."""
import sys


def main():
    path = sys.argv[1]
    N = 5
    if "--n" in sys.argv:
        N = int(sys.argv[sys.argv.index("--n") + 1])
    emax = N ** 3 - (2 * N - 2)
    pos = set()
    for line in open(path):
        line = line.strip()
        if line.startswith("v ") or line.startswith("V "):
            line = line[2:]
        elif not (line and (line[0].isdigit() or line[0] == "-")):
            continue
        for tok in line.split():
            try:
                lit = int(tok)
            except ValueError:
                break
            if lit > 0:
                pos.add(lit)
    grid = [[None] * N for _ in range(N)]
    for c in range(N * N):
        for v in range(1, emax + 1):
            if c * emax + v in pos:
                if grid[c // N][c % N] is not None:
                    print(f"FAIL: cell {c} has two values in the model")
                    return 1
                grid[c // N][c % N] = v
    if any(x is None for row in grid for x in row):
        print("FAIL: some cell has no value — is this a complete model "
              "('v' lines) from a SATISFIABLE run?")
        return 1

    vals = [grid[i][k] for i in range(N) for k in range(N)]
    for i in range(N):
        for k in range(N):
            for l in range(k + 1, N):
                vals.append(grid[i][k] + grid[i][l])
    for k in range(N):
        for i in range(N):
            for j in range(i + 1, N):
                vals.append(grid[i][k] + grid[j][k])
    ok = sorted(vals) == list(range(1, N ** 3 + 1))
    print("decoded grid:")
    for row in grid:
        print("  ", row)
    print(f"verification (entries + rook sums == 1..{N**3}):",
          "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
