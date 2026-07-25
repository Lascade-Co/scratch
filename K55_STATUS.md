# K(5,5) geodesic labeling — investigation status

## Problem
Fill a 5×5 grid (edges of K_{5,5}) with 25 distinct positive integers so that
the 25 entries + 100 rook-adjacent pair sums are exactly {1..125}.

## Master identity (verified numerically on the solvable K(2,2))
With P(q)=Σ_entries q^x, f_i / g_k the row/column generating polynomials,
E(q)=Σ_{v=1}^{125} q^v:

    Σ_i f_i(q)² + Σ_k g_k(q)²  =  2·[ E(q) − P(q) + P(q²) ]

Shadows: q=−1 ⇒ K5 (parity); d²/dq² at q=1 ⇒ K6 (sum of squares);
q=ζ_m ⇒ residue-class count systems (below), which strictly subsume them.

## Residue sieve (exact counting per class mod m)
For each r mod m:  n_r + rowpairs_r + colpairs_r = T_r, with T_r exactly known.
Solved exactly with CP-SAT; encoding validated on K(2,2) (must be & is SAT).

| m  | full sieve (with realizability) | count-level sieve |
|----|--------------------------------|-------------------|
| 2–6 | SAT (≤0.4s)                   | —                 |
| 7   | SAT (9.7s)                     | —                 |
| 8   | SAT (3.5s)                     | —                 |
| 9   | SAT (15.6s)                    | —                 |
| 10  | unknown @240s                  | **SAT (7.4s)**    |
| 12  | unknown @240s                  | **SAT (87.9s)**   |
| 16  | unknown @240s                  | unknown @300s     |
| 20  | unknown @240s                  | unknown @300s     |

## Conclusion of the congruence program (option 3)
No modulus yields an obstruction; witnesses exist at every decided m.
Since the residue systems subsume K5 and every root-of-unity shadow of the
master identity, and K6 (archimedean shadow) also survives (~21,900 parity
configs), **elementary counting/congruence methods cannot decide K(5,5)**.
The instance passes every necessary condition found:
  integrality S=875 · 1,2 entries · entries ≤117 · parity a∈{9..19} ·
  sum-of-squares identity · all residue count systems tested.

## Computational status
- Brute-force tree ≈1.7×10^18 nodes (Knuth estimate) — out of reach anywhere.
- CP-SAT (bare, and with K5 added): UNKNOWN after 9-min in-session windows
  (~400k conflicts, 1.1M branches per window; state not resumable).
- Z3: no verdict in-window.
- This environment kills background processes at turn boundaries; only ~10-min
  synchronous windows are reliable → long solver runs need a persistent machine.

## Remaining avenues
1. Persistent solver run (recommended): cube-and-conquer SAT (march_cu +
   kissat/CaDiCaL in parallel) or CP-SAT unlimited. C&C gives a measurable ETA
   after the first cubes complete — no a-priori 1–2h guarantee is honest.
2. Deeper structure (low odds, high effort): top-segment analysis (labels
   118–125 forced to be pair sums of a constrained top entry set), Sidon-type
   packing arguments per row/column.
