#!/usr/bin/env python3
"""General pruned-DFS solver for the ring C_n geodesic-labeling problem.
Geodesics = all cyclic windows of length 1..m, m = n//2; target = {1..n*m}."""
import sys

def solve(n, want_all=False):
    m = n // 2
    G = n * m
    TARGET = set(range(1, G + 1))
    c = m * (m + 1) // 2
    tot = G * (G + 1) // 2
    if tot % c:
        return None, 0, "fails integrality (S not integer)"
    S = tot // c
    w = [0] * n
    used = set()
    eu = [False] * (G + 1)
    sols = []
    nodes = [0]

    def wins_end(i):
        added = []
        for L in range(1, m + 1):
            st = i - L + 1
            if st < 0:
                break
            s = sum(w[st:i + 1])
            # even n: opposite m-arcs sum to S -> m-window in [S-G, G]? general bound:
            if s > G or s in used:
                for v in added:
                    used.discard(v)
                return None
            used.add(s)
            added.append(s)
        return added

    def dfs(i, cur):
        nodes[0] += 1
        if i == n:
            if cur != S:
                return False
            vals = [sum(w[(s + k) % n] for k in range(L))
                    for L in range(1, m + 1) for s in range(n)]
            if set(vals) == TARGET and len(vals) == G:
                sols.append(w[:])
                return not want_all
            return False
        for v in range(1, G + 1):
            if eu[v] or cur + v > S:
                if cur + v > S:
                    break
                continue
            w[i] = v
            eu[v] = True
            added = wins_end(i)
            if added is not None:
                if dfs(i + 1, cur + v):
                    eu[v] = False
                    for a in added:
                        used.discard(a)
                    w[i] = 0
                    return True
                for a in added:
                    used.discard(a)
            eu[v] = False
            w[i] = 0
        return False

    # fix w[0]=1 (value 1 is min geodesic -> single edge)
    w[0] = 1
    used.add(1)
    eu[1] = True
    dfs(1, 1)
    return sols, nodes[0], f"S={S}"


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [3, 4, 10, 11]
    for n in ns:
        res = solve(n, want_all=False)
        if res[0] is None:
            print(f"n={n:>2}: {res[2]}  -> NO SOLUTION (immediate)")
            continue
        sols, nodes, info = res
        m = n // 2
        if sols:
            w = sols[0]
            vals = sorted(sum(w[(s + k) % n] for k in range(L))
                          for L in range(1, m + 1) for s in range(n))
            ok = vals == list(range(1, n * m + 1))
            print(f"n={n:>2}: {info}, nodes={nodes}  -> SOLUTION {w}  (valid={ok})")
        else:
            print(f"n={n:>2}: {info}, nodes={nodes}  -> no solution exists")
