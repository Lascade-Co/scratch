#!/usr/bin/env python3
"""Verify a claimed K(N,N) labeling. Input: a text file (or stdin) containing
N*N integers (whitespace/newline separated, row-major; N inferred from count).
Exit 0 and print PASS iff the entries plus all rook pair sums are exactly
{1..N^3}. Trust nothing that hasn't passed this check."""
import sys


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


def main():
    data = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    nums = [int(t) for t in data.split()]
    N = round(len(nums) ** 0.5)
    if N * N != len(nums):
        print(f"FAIL: expected a square count of numbers, got {len(nums)}")
        return 1
    grid = [nums[i * N:(i + 1) * N] for i in range(N)]
    lab = labels_of(grid)
    want = list(range(1, N ** 3 + 1))
    if lab == want:
        print(f"PASS: valid K({N},{N}) labeling — entries + rook pair sums "
              f"= {{1..{N**3}}} exactly.")
        for row in grid:
            print("  ", row)
        return 0
    missing = sorted(set(want) - set(lab))[:10]
    dupes = sorted({v for v in lab if lab.count(v) > 1})[:10]
    print(f"FAIL: labels != {{1..{N**3}}}. missing(first 10)={missing} "
          f"duplicated(first 10)={dupes}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
