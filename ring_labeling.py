#!/usr/bin/env python3
"""
Edge-weight labeling of a ring C_10 (10 vertices, 10 edges) such that the
50 geodesic-path weights are exactly the integers 1..50.

The 50 geodesics are all cyclic contiguous windows of length 1,2,3,4,5
(10 starting positions x 5 lengths = 50):
  - lengths 1..4: the unique shortest path for pairs at distance 1..4
  - length 5    : diametric pairs have TWO shortest arcs, so all 10
                  length-5 windows are geodesics.

Constraints derived:
  - sum of edge weights S = 1275 / 15 = 85   (each edge is in 15 windows)
  - value 1 must be a single edge (min geodesic) -> fix at position 0
  - every length-5 window lies in [35,50] (complement rule: a+b=85, both<=50)
  - any single edge <= 40 (9 others are distinct positives summing to >=45)

Search: DFS over positions with pruning as soon as a window is completed.
"""

import sys

N = 10
TARGET = set(range(1, 51))
MAXV = 40  # upper bound on any single edge weight


def windows(w):
    """All 50 cyclic windows of length 1..5, as a list of sums."""
    out = []
    for L in range(1, 6):
        for s in range(N):
            out.append(sum(w[(s + k) % N] for k in range(L)))
    return out


def solve(all_solutions=False):
    solutions = []
    w = [0] * N
    used = set()          # geodesic values placed so far (non-wrapping windows)
    edge_used = [False] * 51
    nodes = 0

    # Fix w[0] = 1 to kill rotational symmetry.
    w[0] = 1
    used.add(1)
    edge_used[1] = True

    def check_windows_ending_at(i):
        """Check/record all non-wrapping windows [i-L+1 .. i], L=1..5.
        Returns list of added values on success, or None on conflict."""
        added = []
        for L in range(1, 6):
            start = i - L + 1
            if start < 0:
                break
            s = sum(w[start:i + 1])
            if s > 50 or s in used:
                # rollback
                for v in added:
                    used.discard(v)
                return None
            used.add(s)
            added.append(s)
        return added

    def dfs(i, cur_sum):
        nonlocal nodes
        nodes += 1
        if i == N:
            # place all wrapping windows + final verification
            vals = windows(w)
            if set(vals) == TARGET and len(vals) == 50:
                solutions.append(w[:])
                return not all_solutions  # stop if only one wanted
            return False

        remaining_positions = N - i
        for v in range(2, MAXV + 1):  # positions 1..9 use 2..40
            if edge_used[v]:
                continue
            new_sum = cur_sum + v
            # sum feasibility: remaining positions must be distinct, unused,
            # and total must reach exactly 85.
            rem_after = remaining_positions - 1
            if new_sum + rem_after * 1 > 85:      # even minimal fill overshoots
                # values only grow, but distinctness means we can't easily
                # lower-bound tightly; just cap on new_sum alone:
                if new_sum > 85:
                    break
            # reflection symmetry: enforce w[1] < w[9] by requiring w[1] be
            # the smaller neighbour of the fixed vertex.
            w[i] = v
            edge_used[v] = True
            added = check_windows_ending_at(i)
            if added is not None:
                if dfs(i + 1, new_sum):
                    edge_used[v] = False
                    for a in added:
                        used.discard(a)
                    w[i] = 0
                    return True
                for a in added:
                    used.discard(a)
            edge_used[v] = False
            w[i] = 0
        return False

    dfs(1, 1)
    return solutions, nodes


if __name__ == "__main__":
    all_sols = "--all" in sys.argv
    sols, nodes = solve(all_solutions=all_sols)
    print(f"DFS nodes explored: {nodes}")
    if not sols:
        print("No solution found.")
    else:
        # dedup by dihedral symmetry (rotation + reflection)
        seen = set()
        uniq = []
        for w in sols:
            forms = []
            for r in range(N):
                rot = tuple(w[r:] + w[:r])
                forms.append(rot)
                forms.append(rot[::-1])
            key = min(forms)
            if key not in seen:
                seen.add(key)
                uniq.append(w)
        print(f"Found {len(sols)} raw solution(s), {len(uniq)} unique up to symmetry.\n")
        for w in uniq:
            print("edge weights :", w)
            print("sum          :", sum(w))
            vals = sorted(windows(w))
            print("geodesic set == {1..50}:", vals == list(range(1, 51)))
            # breakdown by length
            for L in range(1, 6):
                ws = sorted(sum(w[(s + k) % N] for k in range(L)) for s in range(N))
                print(f"  len {L}: {ws}")
            print()
