# Ring C₁₀ geodesic edge-weight labeling — findings

## Problem
Ring of 10 vertices / 10 edges (cycle C₁₀). Assign edge weights so the 50 geodesic
path weights are exactly {1, 2, …, 50}.

The 50 geodesics = all cyclic contiguous windows of length 1..5
(10 starting positions × 5 lengths): lengths 1–4 give the unique shortest path;
length 5 (diametric pairs) has **two** shortest arcs, so all ten length-5 windows count.

## Derived necessary conditions
- **Sum = 85.** Each edge lies in 1+2+3+4+5 = 15 windows, so Σwindows = 15·S = 1275 ⇒ S = 85.
- **1 is an edge** (unique minimum; any 2+ arc ≥ 1+2 = 3). Rotation fixes it at position 0.
- **2 is an edge** (2 = 1+1 only, impossible with distinct weights).
- **Every length-5 window ∈ [35, 50]** (complement rule: two opposite 5-arcs sum to 85,
  both ≤ 50 ⇒ each ≥ 35).
- **Any single edge ≤ 40** (the other 9 distinct positives sum to ≥ 45).

## Algorithm
DFS placing edge weights around the ring; prune the moment a completed window is
> 50, duplicates an earlier geodesic value, or (length-5) falls below 35. Sound and
complete — pruning only rejects on necessary conditions. Not brute force.

## Result: NO SOLUTION EXISTS
Confirmed three independent ways:

| Search | Assumptions | Nodes | Solutions |
|---|---|---|---|
| DFS, w₀=1 fixed, cap 40 | WLOG symmetry + tight bound | 735,496 | 0 |
| Fully unconstrained | none (full range 1–50, no fixing) | 14,373,810 | 0 |
| Strong necessary-condition pruning | edges 1,2; 5-windows∈[35,50] | 384 | 0 |

Under the strong pruning, **no branch even reaches depth 10** — every path dies early
(324 duplicate-value collisions, 37 windows > 50, 12 length-5 windows < 35).

## Files
- `ring_labeling.py`      — main DFS solver (`--all` for every solution up to symmetry)
- `brute_unconstrained.py`— assumption-free exhaustive search
- `verify_z3.py`          — independent Z3/SMT model
- `tree_search.py`        — instrumented DFS, writes `tree.json`
- `make_tree_html.py`     — renders `search_tree.html` (zoomable search-tree diagram)
