# K(5,5) geodesic labeling — established results & metrics

Everything below is machine-verified in this branch's git history (all
investigation scripts live in earlier commits; `git log` this branch).

## 1. The problem and where it came from

Origin: label the 10 edges of a graph so all geodesic (shortest-path) weight
sums are exactly 1..#geodesics. For the ring C₁₀ (the original question) we
proved **no solution exists**. The complete bipartite K(5,5) is the natural
next candidate — and the only nontrivial one in its family (see §3).

**Grid form (use this):** fill a 5×5 grid with 25 distinct positive integers
so that the 25 entries + 100 rook-adjacent pair sums (same row or column) are
exactly {1..125}. Rows = one vertex side, columns = the other, cell = edge;
rook pairs = the 2-edge geodesics.

## 2. Cycle family Cₙ (context, all settled)

Required edge sum S = [G(G+1)/2] / [m(m+1)/2], G = n·m, m = ⌊n/2⌋; S must be
an integer ("integrality gate").

| n | verdict | evidence |
|---|---------|----------|
| 3 | solvable: [1,2,3] | exhaustive |
| 4 | solvable: [1,3,2,6] | exhaustive |
| 10 | **no solution** (integrality passes, S=85) | 735,496-node pruned DFS; 14,373,810-node assumption-free DFS; 384-node necessary-condition tree; Z3 `unsat` (16 min) — four independent confirmations |
| 11 | impossible | S = 1540/15 non-integer |
| 12 | impossible | S = 2628/21 non-integer |
| all other n ≤ 20 | impossible | integrality fails |

## 3. Bipartite family K(m,m)

S = m³(m³+1) / (2(2m−1)). Only **m = 2 and m = 5** pass integrality for
m ≤ 15. K(2,2) is solvable — grid [[1,3],[6,2]] (labels {1..8}); it is the
validation instance used by every tool in this package. K(3,3), K(4,4) are
impossible outright. **K(5,5) (S = 875) is the open case being handed off.**

## 4. Proven necessary conditions for K(5,5) (all passed — none decides)

| # | condition | status |
|---|-----------|--------|
| K1 | Σ entries = 875 (each entry lies in 9 of the 125 geodesics; 9S = 7875) | passes |
| K2 | values 1 and 2 are entries; 3 is an entry iff cells of 1,2 not rook-adjacent | structural |
| K3 | every entry ≤ 117 ⇒ labels 118–125 are all pair sums | passes |
| K4 | e₈ + e₂₅ ≤ 125 (8th-smallest + largest entry) | passes |
| K5 | #odd entries a satisfies Σpᵢ² + Σp'ₖ² = 11a − 63 (p = row/col odd counts) ⇒ a ∈ {9,11,13,15,17,19}; realizable configs per a: 300 / 6,300 / 11,500 / 12,040 / 3,700 / 25 (Gale–Ryser-checked) | passes (~21,900 configs survive) |
| K6 | 7Q + ΣRᵢ² + ΣCₖ² = 658,875 (Q = Σx², R/C row/col sums); mod 4: 3a + ρ_R + ρ_C ≡ 3, ρ_R, ρ_C odd | passes |

Master identity (verified numerically on K(2,2)): with P(q)=Σ q^entry,
fᵢ/gₖ row/col generating polynomials, E(q)=Σ_{v≤125} q^v:

    Σᵢ fᵢ(q)² + Σₖ gₖ(q)² = 2·[E(q) − P(q) + P(q²)]

K5 is its q = −1 shadow; K6 its second derivative at q = 1; residue systems
(§5) are its root-of-unity shadows at full strength.

## 5. Residue-class sieve (congruence program — complete, no obstruction)

Exact counting per class r mod m: n_r + rowpairs_r + colpairs_r = T_r with
T_r known exactly. Solved with CP-SAT; encoding validated on K(2,2) (returns
SAT for every modulus there, as it must).

| m | full system (with 5×5 realizability) | count-level system |
|---|---|---|
| 2–6 | SAT ≤ 0.4 s | — |
| 7 | SAT 9.7 s | — |
| 8 | SAT 3.5 s | — |
| 9 | SAT 15.6 s | — |
| 10 | unknown @ 240 s | **SAT 7.4 s** |
| 12 | unknown @ 240 s | **SAT 87.9 s** |
| 16, 20 | unknown @ 240 s | unknown @ 300 s (compute-bound, both directions) |

**Conclusion: no congruence/counting obstruction exists at any decided
modulus. Elementary methods cannot settle K(5,5); it must be searched.**

## 6. Search-space and solver metrics (why this needs a persistent machine)

- Knuth random-probing estimate (300,000 dives) of the pruned DFS tree:
  **1.67×10¹⁸ ± 0.48×10¹⁸ nodes** (3.64×10¹⁷ with the 1-in-corner quotient);
  estimated solution-leaf count in probes: 0. At the measured ~10⁶ nodes/s (C,
  -O3, single core): **~54,000 years** — brute force is out everywhere.
- CP-SAT (this package's model, 4 slow cores, 540 s budget): 401,456
  conflicts, 1,126,604 branches, 1.01×10⁹ propagations, 821 restarts →
  **UNKNOWN**. No solution found; no refutation. The instance reaches real
  search (presolve ~20 s) and is genuinely hard, not degenerate.
- Z3 on the same model: no verdict in ~7-minute windows.
- Randomized restarts (C and Python, various seeds): best partial fill
  22/25 cells; no solution encountered.
- CNF (this package): 42,525 vars, 1,667,878 clauses, 26 MB, generated in
  ~4 s; self-test solves K(2,2) end-to-end and recovers [[1,3],[6,2]].

## 7. Honest runtime expectation

Nobody can promise a 1–2 h verdict for a possibly-UNSAT instance; resolution
time is governed by the shortest proof/solution the solver can find. What the
cube route (README §Path C) gives you is a **measured ETA within ~15 minutes
of starting**: 100 disjoint cubes, embarrassingly parallel; after the first
cubes finish, remaining ≈ median-cube-time × cubes-left / cores. If early
cubes run hours each, stop and reassess rather than burn the machine.
