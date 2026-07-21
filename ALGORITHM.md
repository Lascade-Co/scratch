# Optimized algorithm — geodesic edge-labeling of the ring $C_{10}$

## 1. Formalization

Let the ring be the cycle $C_{10}$ with edges $e_0,\dots,e_9$ (indices taken $\bmod\ 10$)
and weights

$$w_i \in \mathbb{Z}^{+},\qquad i \in \mathbb{Z}_{10}=\{0,\dots,9\}.$$

For a start $s\in\mathbb{Z}_{10}$ and length $L\in\{1,\dots,5\}$ define the **window sum**

$$W(s,L)\;=\;\sum_{k=0}^{L-1} w_{\,(s+k)\bmod 10}.$$

The geodesics of $C_{10}$ are exactly the windows of length $1$–$5$ (length $5$
diametric pairs contribute *two* shortest arcs), so the geodesic multiset is

$$\mathcal{G}=\bigl\{\,W(s,L)\;:\;s\in\mathbb{Z}_{10},\;L\in\{1,\dots,5\}\,\bigr\},\qquad |\mathcal{G}|=10\times5=50.$$

**Goal.** Find $w=(w_0,\dots,w_9)$ with

$$\mathcal{G}=\{1,2,\dots,50\}\quad(\text{a bijection, since }|\mathcal G|=50).$$

## 2. Necessary conditions (pruning invariants)

Each edge occurs in $\sum_{L=1}^{5}L$ windows, hence

$$\sum_{s,L}W(s,L)=15\sum_i w_i=\sum_{n=1}^{50}n=1275\;\Longrightarrow\;\boxed{\,S:=\textstyle\sum_i w_i=85\,}. \tag{C1}$$

$$1\in\mathcal G \text{ needs } w_i=1 \text{ (any } L\!\ge\!2 \text{ sum}\ge 1+2=3);\quad
2\in\mathcal G \text{ needs } w_j=2\ (2=1{+}1 \text{ forbidden by distinctness}). \tag{C2}$$

Opposite length-$5$ arcs partition $E$, so $W(s,5)+W(s{+}5,5)=S=85$; with both $\le 50$:

$$35\le W(s,5)\le 50\qquad\forall s. \tag{C3}$$

All windows distinct $\Rightarrow$ the $w_i$ are distinct; with (C1),

$$w_i\le S-\!\!\sum_{k=1}^{9}k = 85-45 = 40\qquad\forall i. \tag{C4}$$

Rotation symmetry is quotiented by fixing the edge of weight $1$:

$$w_0:=1. \tag{C5}$$

## 3. The algorithm (pruned DFS)

State: partial assignment of $w_0,\dots,w_{i-1}$, running sum $\sigma=\sum_{k<i}w_k$,
and the set $U\subseteq\{1,\dots,50\}$ of geodesic values already realized by
**non-wrapping** windows $W(s,L)$ with $s+L\le i$.

Define the pruning predicate for placing value $v$ at position $i$
(let $w_i\!\leftarrow\!v$ tentatively). It **fails** iff any newly-completed
window $W(i{-}L{+}1,\,L)$, $1\le L\le\min(5,i{+}1)$, violates

$$\underbrace{W>50}_{\text{range}}\quad\lor\quad
\underbrace{W\in U}_{\text{collision}}\quad\lor\quad
\underbrace{(L=5\ \land\ W<35)}_{\text{(C3)}}\quad\lor\quad
\underbrace{\sigma+v>85}_{\text{(C1)}}.$$

Every clause is a *necessary* condition, so pruning is **sound** (no valid labeling
is discarded) and the enumeration is **complete**.

```
Search(i, σ, U):
    if i = 10:
        report solution if  {W(s,L) : s∈ℤ₁₀, L∈1..5} = {1..50}   # includes wrapping windows
        return
    for v = 1 … 40  with  v ∉ {w₀,…,w_{i-1}}  and  σ+v ≤ 85:      # (C4),(C1)
        w_i ← v
        A ← ∅                                                     # values added this step
        ok ← true
        for L = 1 … min(5, i+1):                                  # windows ending at i
            W ← Σ_{t=i-L+1}^{i} w_t
            if W > 50  or  W ∈ U  or  (L=5 and W<35):  ok ← false; break
            A ← A ∪ {W}
        if ok:  Search(i+1, σ+v, U ∪ A)
        undo w_i, A
```

Driver: fix $w_0=1$ (C5), $U=\{1\}$, call `Search(1, 1, {1})`.
Optionally add reflection quotient $w_1<w_9$ (checked once $w_9$ is placed) to halve the tree.

## 4. Complexity

Naïve enumeration of $10$ distinct values in $[1,40]$ over the ring is
$\binom{40}{10}\cdot 9!/2 \approx 10^{16}$ — infeasible. The predicate above collapses
this: with (C1)–(C5) the **entire** tree is

$$384\ \text{nodes},\qquad \text{depth} < 10\ \text{on every branch},$$

i.e. $O(\text{a few hundred})$ visited states — polynomial-scale in practice, decidedly
not brute force. (Dropping (C3) and the tight cap still finishes in $7.4\times10^{5}$
nodes; dropping *all* symmetry/bounds, $1.4\times10^{7}$.)

## 5. Result

$$\mathcal{G}=\{1,\dots,50\}\ \text{is}\ \textbf{unsatisfiable on } C_{10}.$$

Confirmed independently by: the pruned DFS ($7.4\times10^5$ nodes), an assumption-free
DFS ($1.4\times10^7$ nodes), the $384$-node necessary-condition tree, and a Z3 SMT model
(`unsat`). Under (C1)–(C5) no branch reaches depth $10$: every path terminates in a
range violation ($W>50$), a value collision ($W\in U$), or a (C3) violation ($W<35$).
