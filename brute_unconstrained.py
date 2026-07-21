#!/usr/bin/env python3
"""Independent, assumption-free confirmation.

No WLOG fixing of position, no upper-bound cap beyond the trivial <=50.
Edges are distinct positive ints (forced: single edges are geodesics).
Searches ALL arrangements; prunes only on necessary conditions.
"""
N = 10
TARGET = set(range(1, 51))

w = [0] * N
used = set()
edge_used = [False] * 51
nodes = 0
found = []


def windows_ending_at(i):
    added = []
    for L in range(1, 6):
        st = i - L + 1
        if st < 0:
            break
        s = sum(w[st:i + 1])
        if s > 50 or s in used:
            for v in added:
                used.discard(v)
            return None
        used.add(s)
        added.append(s)
    return added


def dfs(i, cur):
    global nodes
    nodes += 1
    if cur > 85:
        return
    if i == N:
        if cur != 85:
            return
        vals = [sum(w[(s + k) % N] for k in range(L))
                for L in range(1, 6) for s in range(N)]
        if set(vals) == TARGET:
            found.append(w[:])
        return
    for v in range(1, 51):          # full range, no cap, no fixing
        if edge_used[v]:
            continue
        w[i] = v
        edge_used[v] = True
        added = windows_ending_at(i)
        if added is not None:
            dfs(i + 1, cur + v)
            for a in added:
                used.discard(a)
        edge_used[v] = False
        w[i] = 0


dfs(0, 0)
print("nodes:", nodes)
print("solutions found:", len(found))
for f in found[:5]:
    print("  ", f)
