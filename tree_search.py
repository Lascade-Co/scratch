#!/usr/bin/env python3
"""Instrumented DFS that records the full search tree with pruning reasons,
so the exploration can be visualised and cross-checked.

Necessary conditions applied as pruning (all provably required):
  - w[0] = 1              (value 1 is the unique-min geodesic -> a single edge;
                           rotation fixes it at position 0)
  - every length-5 window in [35,50]   (complement rule: a + (85-a) = 85, both <=50)
  - every completed window <= 50 and distinct
  - edge values distinct
  - total edge sum must be able to reach exactly 85
"""
import json

N = 10
TARGET = set(range(1, 51))
MAXV = 40

nodes = []          # list of node dicts
children = {}       # id -> [child ids]
counter = [0]

w = [0] * N
used = set()
edge_used = [False] * 51
leaf_reasons = {}


def new_node(parent, pos, val, note):
    nid = counter[0]
    counter[0] += 1
    nodes.append({"id": nid, "pos": pos, "val": val, "note": note})
    children.setdefault(parent, []).append(nid) if parent is not None else None
    children.setdefault(nid, [])
    return nid


def windows_ending_at(i):
    """Return (ok, added, reason). Applies <=50, distinct, and [35,50] for L=5."""
    added = []
    for L in range(1, 6):
        st = i - L + 1
        if st < 0:
            break
        s = sum(w[st:i + 1])
        if s > 50:
            for v in added:
                used.discard(v)
            return False, [], f"win L{L}={s}>50"
        if L == 5 and s < 35:
            for v in added:
                used.discard(v)
            return False, [], f"5-win={s}<35"
        if s in used:
            for v in added:
                used.discard(v)
            return False, [], f"dup {s}"
        used.add(s)
        added.append(s)
    return True, added, None


def dfs(i, cur, parent):
    if i == N:
        vals = [sum(w[(s + k) % N] for k in range(L))
                for L in range(1, 6) for s in range(N)]
        ok = set(vals) == TARGET
        nid = new_node(parent, i, None, "SOLUTION" if ok else "full-but-no-match")
        return ok
    solved = False
    for v in range(1, MAXV + 1):
        if edge_used[v]:
            continue
        if cur + v > 85:
            break
        w[i] = v
        edge_used[v] = True
        ok, added, reason = windows_ending_at(i)
        if ok:
            nid = new_node(parent, i, v, "expand")
            if dfs(i + 1, cur + v, nid):
                solved = True
        else:
            new_node(parent, i, v, "prune:" + reason)
        edge_used[v] = False
        w[i] = 0
    return solved


# root: w[0] = 1 fixed
root = new_node(None, 0, 1, "root w0=1")
w[0] = 1
used.add(1)
edge_used[1] = True
found = dfs(1, 1, root)

print("total tree nodes:", counter[0])
print("solution found:", found)

# leaf outcome tally
from collections import Counter
tally = Counter()
for n in nodes:
    if not children.get(n["id"]):
        tally[n["note"].split()[0] if n["note"].startswith("prune") else n["note"]] += 1
print("leaf outcomes:", dict(tally))

with open("tree.json", "w") as f:
    json.dump({"nodes": nodes, "children": children, "root": root,
               "found": found}, f)
print("wrote tree.json")
